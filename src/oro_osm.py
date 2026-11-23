"""Capa Oro geoespacial: tiendas por municipio, tabla con linaje y mapa.

Entradas: datos/plata/tiendas_colima.csv y datos/plata/municipios_colima.geojson
Salidas:  datos/oro/tiendas_oro.csv, datos/oro/tiendas_por_municipio.csv y docs/E2/mapa_tiendas_colima.png
Cada registro de Oro conserva su linaje: archivo de Bronce, identificador original y fecha de ingesta.
"""
import geopandas as gpd
import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import ORO, PLATA, RAIZ

CRS_AREAS = "EPSG:6372"
COLORES = {"convenience": "#1b9e77", "supermarket": "#d95f02", "general": "#7570b3"}
ETIQUETAS = {"convenience": "Conveniencia", "supermarket": "Supermercado", "general": "Tienda general"}
COLUMNAS_TIENDAS = [
    "id_origen", "osm_type", "osm_id", "shop", "brand", "lat", "lon", "municipio",
    "archivo_origen", "fecha_ingesta_utc", "osm_base_timestamp",
]


def agregar(tiendas, munis):
    munis = munis.copy()
    munis["area_km2"] = (munis.to_crs(CRS_AREAS).area / 1e6).round(1)

    agg = tiendas.groupby("municipio").agg(
        tiendas=("id_origen", "size"),
        conveniencia=("shop", lambda s: int((s == "convenience").sum())),
        supermercados=("shop", lambda s: int((s == "supermarket").sum())),
        generales=("shop", lambda s: int((s == "general").sum())),
        con_marca=("brand", lambda s: int(s.notna().sum())),
    )
    oro = pd.DataFrame(munis.drop(columns="geometry"))[
        ["municipio", "osm_relation_id", "area_km2", "archivo_origen", "fecha_ingesta_utc", "osm_base_timestamp"]
    ].rename(columns={
        "archivo_origen": "archivo_origen_limites",
        "fecha_ingesta_utc": "fecha_ingesta_limites_utc",
        "osm_base_timestamp": "osm_base_timestamp_limites",
    })
    oro = oro.merge(agg, on="municipio", how="left")
    for c in ["tiendas", "conveniencia", "supermercados", "generales", "con_marca"]:
        oro[c] = oro[c].fillna(0).astype(int)

    oro["tiendas_por_100km2"] = (oro["tiendas"] / oro["area_km2"] * 100).round(2)
    oro["pct_del_total"] = (oro["tiendas"] / oro["tiendas"].sum() * 100).round(1)
    oro["pct_con_marca"] = (oro["con_marca"] / oro["tiendas"].where(oro["tiendas"] > 0) * 100).round(1)

    # Linaje de las tiendas (el mismo archivo de Bronce para todas)
    oro["archivo_origen_tiendas"] = tiendas["archivo_origen"].iloc[0]
    oro["fecha_ingesta_tiendas_utc"] = tiendas["fecha_ingesta_utc"].iloc[0]
    oro["osm_base_timestamp_tiendas"] = tiendas["osm_base_timestamp"].iloc[0]
    return munis, oro.sort_values("tiendas", ascending=False).reset_index(drop=True)


def verificar_linaje(tiendas_oro, oro):
    """Cada cifra agregada debe poder rastrearse hasta sus registros y hasta Bronce."""
    por_muni = tiendas_oro.groupby("municipio").size()
    for _, fila in oro.iterrows():
        assert por_muni.get(fila["municipio"], 0) == fila["tiendas"], f"Conteo no coincide en {fila['municipio']}"
    assert oro["tiendas"].sum() == len(tiendas_oro), "El total agregado no coincide con las tiendas"
    for col in ["id_origen", "archivo_origen", "fecha_ingesta_utc"]:
        assert tiendas_oro[col].notna().all(), f"Hay tiendas sin {col}"
    assert tiendas_oro["id_origen"].is_unique, "Hay identificadores de origen repetidos"


def graficar(munis, oro, tiendas, ruta):
    gm = munis.merge(oro[["municipio", "tiendas"]], on="municipio")
    fig, ejes = plt.subplots(1, 2, figsize=(15, 7))

    munis.plot(ax=ejes[0], color="#f2f2f2", edgecolor="black", linewidth=0.6)
    for shop, g in tiendas.groupby("shop"):
        ejes[0].scatter(g["lon"], g["lat"], s=16, color=COLORES[shop], label=ETIQUETAS[shop], alpha=0.8)
    ejes[0].legend(title="Tipo de tienda", loc="lower left")
    ejes[0].set_title("Tiendas registradas en OpenStreetMap")

    gm.plot(
        column="tiendas", cmap="YlOrBr", edgecolor="black", linewidth=0.6, ax=ejes[1],
        legend=True, legend_kwds={"label": "Tiendas por municipio", "shrink": 0.7},
    )
    for _, r in gm.iterrows():
        p = r.geometry.representative_point()
        ejes[1].annotate(f"{r['municipio']}\n{r['tiendas']}", (p.x, p.y), ha="center", fontsize=7)
    ejes[1].set_title("Tiendas por municipio")

    for ax in ejes:
        ax.set_axis_off()
    fecha = tiendas["fecha_ingesta_utc"].iloc[0][:10]
    fig.text(
        0.5, 0.02,
        f"Datos: © OpenStreetMap contributors (ODbL). Extraídos el {fecha}. "
        "La cobertura de OpenStreetMap es desigual: los conteos subestiman el total real de tiendas.",
        ha="center", fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(ruta, dpi=130)
    plt.close(fig)


def main():
    tiendas = pd.read_csv(PLATA / "tiendas_colima.csv")
    munis = gpd.read_file(PLATA / "municipios_colima.geojson")

    munis, oro = agregar(tiendas, munis)
    tiendas_oro = tiendas[COLUMNAS_TIENDAS].copy()
    verificar_linaje(tiendas_oro, oro)

    ORO.mkdir(parents=True, exist_ok=True)
    tiendas_oro.to_csv(ORO / "tiendas_oro.csv", index=False)
    oro.to_csv(ORO / "tiendas_por_municipio.csv", index=False)
    graficar(munis, oro, tiendas, RAIZ / "docs" / "E2" / "mapa_tiendas_colima.png")

    pd.set_option("display.width", 200)
    print("--- Tiendas por municipio ---")
    print(oro[["municipio", "tiendas", "area_km2", "tiendas_por_100km2", "pct_del_total", "pct_con_marca"]]
          .to_string(index=False))
    print(f"\nTotal de tiendas: {oro['tiendas'].sum()} | municipios sin tiendas: {int((oro['tiendas'] == 0).sum())}")
    print("Verificación de linaje superada: cada cifra agregada coincide con sus registros de origen.")
    print("\nGuardado: datos/oro/tiendas_oro.csv, datos/oro/tiendas_por_municipio.csv "
          "y docs/E2/mapa_tiendas_colima.png")


if __name__ == "__main__":
    main()