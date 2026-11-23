"""Capa Plata geoespacial: valida las tiendas de OpenStreetMap, arma los polígonos municipales
y asigna cada tienda a su municipio. Los registros inválidos van a cuarentena con su motivo.

Entradas: datos/bronce/osm/tiendas_colima_*.json y limites_municipales_colima_*.json (los más recientes)
Salidas:  datos/plata/tiendas_colima.csv, datos/plata/municipios_colima.geojson,
          datos/cuarentena/cuarentena_osm_<fecha>.csv y datos/cuarentena/bitacora_puerta_osm.csv
Cada registro conserva su linaje: archivo de Bronce, identificador original y fecha de ingesta.
"""
import json
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd
from pandera.errors import SchemaErrors
from shapely import make_valid
from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union

try:
    import pandera.pandas as pa
except ImportError:  # versiones anteriores de pandera
    import pandera as pa

from config import BRONCE, CUARENTENA, PLATA, RAIZ

CRS_GEO = "EPSG:4326"
CRS_AREAS = "EPSG:6372"  # ITRF2008 / LCC, proyección oficial de México (áreas en metros)
LAT = (18.5, 19.7)
LON = (-104.8, -103.4)


def ultimo(patron):
    archivos = sorted((BRONCE / "osm").glob(patron))
    if not archivos:
        raise FileNotFoundError(f"No hay archivos Bronce que coincidan con {patron}")
    return archivos[-1]


def cargar_tiendas():
    archivo = ultimo("tiendas_colima_*.json")
    j = json.loads(archivo.read_text(encoding="utf-8"))
    meta = {
        "archivo_origen": archivo.relative_to(RAIZ).as_posix(),
        "fecha_ingesta_utc": j["fecha_ingesta_utc"],
        "osm_base_timestamp": j.get("osm_base_timestamp"),
    }
    return pd.DataFrame(j["registros"]), meta


def _poligonos(lineas):
    if not lineas:
        return None
    noded = unary_union(lineas)
    partes = list(noded.geoms) if hasattr(noded, "geoms") else [noded]
    pols = list(polygonize(partes))
    return unary_union(pols) if pols else None


def poligono_municipio(rel):
    def lineas(rol):
        return [
            LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
            for m in rel.get("members", [])
            if m.get("type") == "way" and m.get("role") == rol
            and m.get("geometry") and len(m["geometry"]) > 1
        ]

    geom = _poligonos(lineas("outer"))
    if geom is None or geom.is_empty:
        raise ValueError(f"No se pudo armar el polígono de {rel.get('tags', {}).get('name')}")
    huecos = _poligonos(lineas("inner"))
    if huecos is not None and not huecos.is_empty:
        geom = geom.difference(huecos)
    return make_valid(geom)


def cargar_municipios():
    """Usa el archivo de límites más reciente que tenga los 10 municipios (nunca uno incompleto)."""
    esperados = 10
    candidatos = sorted((BRONCE / "osm").glob("limites_municipales_colima_*.json"), reverse=True)
    for archivo in candidatos:
        j = json.loads(archivo.read_text(encoding="utf-8"))
        if len(j.get("relaciones", [])) >= esperados:
            break
    else:
        raise FileNotFoundError(
            f"No hay un archivo de límites municipales completo ({esperados} municipios) en datos/bronce/osm"
        )
    filas = []
    for rel in j["relaciones"]:
        filas.append({
            "municipio": rel["tags"]["name"].replace("Municipio de ", ""),
            "osm_relation_id": rel["id"],
            "geometry": poligono_municipio(rel),
        })
    gdf = gpd.GeoDataFrame(filas, crs=CRS_GEO)
    gdf["archivo_origen"] = archivo.relative_to(RAIZ).as_posix()
    gdf["fecha_ingesta_utc"] = j["fecha_ingesta_utc"]
    gdf["osm_base_timestamp"] = j.get("osm_base_timestamp")
    return gdf


def esquema():
    return pa.DataFrameSchema(
        {
            "osm_type": pa.Column(checks=pa.Check.isin(["node", "way"])),
            "osm_id": pa.Column(checks=pa.Check.gt(0)),
            "shop": pa.Column(checks=pa.Check.isin(["convenience", "supermarket", "general"])),
            "brand": pa.Column(nullable=True),
            "lat": pa.Column(float, checks=pa.Check.in_range(*LAT)),
            "lon": pa.Column(float, checks=pa.Check.in_range(*LON)),
        },
        unique=["osm_type", "osm_id"],
        report_duplicates="exclude_first",
        strict=True,
    )


def validar(df):
    """Devuelve (validos, cuarentena). Un fallo estructural detiene el proceso."""
    try:
        esquema().validate(df, lazy=True)
        return df, df.iloc[0:0].assign(motivo="")
    except SchemaErrors as e:
        fc = e.failure_cases
        if fc["index"].isna().any():
            raise ValueError(f"Fallo estructural en las tiendas:\n{fc}") from e
        motivos = {}
        for _, f in fc.iterrows():
            motivos.setdefault(int(f["index"]), []).append(
                f"{f['column']}: {f['check']} (valor={f['failure_case']})"
            )
        malos = df.loc[list(motivos)].copy()
        malos["motivo"] = malos.index.map(lambda i: " | ".join(motivos[i]))
        return df.drop(index=list(motivos)), malos


def main():
    ahora = datetime.now(timezone.utc)
    tiendas, meta = cargar_tiendas()
    munis = cargar_municipios()
    entrada = len(tiendas)

    validas, malas = validar(tiendas)

    puntos = gpd.GeoDataFrame(
        validas.copy(),
        geometry=gpd.points_from_xy(validas["lon"], validas["lat"]),
        crs=CRS_GEO,
    )
    unidos = gpd.sjoin(puntos, munis[["municipio", "geometry"]], how="left", predicate="within")
    unidos = unidos[~unidos.index.duplicated(keep="first")]
    fuera = unidos["municipio"].isna()

    columnas = list(tiendas.columns)
    fuera_df = pd.DataFrame(unidos.loc[fuera, columnas]).assign(
        motivo="geometria: fuera de los límites municipales de Colima"
    )
    cuarentena = pd.concat([malas, fuera_df], ignore_index=True)

    ok = pd.DataFrame(unidos.loc[~fuera, columnas + ["municipio"]]).copy()
    ok["id_origen"] = ok["osm_type"] + "/" + ok["osm_id"].astype(str)
    ok["archivo_origen"] = meta["archivo_origen"]
    ok["fecha_ingesta_utc"] = meta["fecha_ingesta_utc"]
    ok["osm_base_timestamp"] = meta["osm_base_timestamp"]

    if len(ok) + len(cuarentena) != entrada:
        raise ValueError("La puerta perdió registros: válidos + cuarentena no igualan la entrada")

    PLATA.mkdir(parents=True, exist_ok=True)
    CUARENTENA.mkdir(parents=True, exist_ok=True)
    ok.to_csv(PLATA / "tiendas_colima.csv", index=False)
    munis.to_file(PLATA / "municipios_colima.geojson", driver="GeoJSON")

    if len(cuarentena):
        cuarentena.assign(
            etapa="E2_plata_osm",
            fecha_cuarentena_utc=ahora.isoformat(),
            archivo_origen=meta["archivo_origen"],
        ).to_csv(CUARENTENA / f"cuarentena_osm_{ahora:%Y%m%d_%H%M%S}.csv", index=False)

    bitacora = CUARENTENA / "bitacora_puerta_osm.csv"
    pd.DataFrame([{
        "fecha_ejecucion_utc": ahora.isoformat(),
        "registros_entrada": entrada,
        "registros_validos": len(ok),
        "registros_cuarentena": len(cuarentena),
    }]).to_csv(bitacora, mode="a", header=not bitacora.exists(), index=False)

    print(f"Tiendas: entrada {entrada} | válidas (a Plata) {len(ok)} | en cuarentena {len(cuarentena)}")
    if len(cuarentena):
        print(cuarentena[["osm_type", "osm_id", "motivo"]].head(10).to_string(index=False))

    areas = (munis.to_crs(CRS_AREAS).set_index("municipio").area / 1e6).round(1)
    print("\n--- Área de cada municipio (km²) ---")
    print(areas.sort_values(ascending=False).to_string())
    print(f"Total: {areas.sum():.1f} km²")

    print("\n--- Tiendas por municipio ---")
    print(ok["municipio"].value_counts().to_string())
    print("\n--- Tiendas por tipo ---")
    print(ok["shop"].value_counts().to_string())
    print(f"\nTiendas con marca (cadenas): {ok['brand'].notna().mean() * 100:.1f}%")
    print("\nGuardado: datos/plata/tiendas_colima.csv y datos/plata/municipios_colima.geojson")


if __name__ == "__main__":
    main()