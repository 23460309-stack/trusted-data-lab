"""Linaje de datos de la capa Oro: cada registro se rastrea hasta su archivo de Bronce y su fecha de ingesta.

Entradas: datos/plata/series_validas.csv, datos/bronce/manifiesto.csv y las tablas de datos/oro/
Salidas:  datos/oro/linaje_mensual.csv, columnas fuentes_bronce y fecha_ingesta_utc en las tablas de Oro
          de E1, y docs/E2/linaje.md
Se puede ejecutar varias veces: reemplaza las columnas de linaje en lugar de duplicarlas.
"""
from pathlib import Path

import pandas as pd

from config import BRONCE, ORO, PLATA, RAIZ

FENCE = "`" * 3
S_INEGI, S_BANXICO, S_FIX = "inpc_nacional_inegi", "inpc_nacional", "tipo_cambio_fix"
COLS_LINAJE = ["fuentes_bronce", "fecha_ingesta_utc"]
PARAM_SERIE = {"inpc_inegi": S_INEGI, "tc_fix_prom": S_FIX, "var_inpc_pct_w": S_INEGI, "var_tc_pct_w": S_FIX}


def unir(s):
    return ";".join(sorted(set(";".join(s).split(";"))))


def cargar_origenes():
    sv = pd.read_csv(PLATA / "series_validas.csv", parse_dates=["fecha"])
    man = pd.read_csv(BRONCE / "manifiesto.csv")
    man = man[(man["estado"] == "ok") & man["archivo"].notna()].copy()
    man["nombre"] = man["archivo"].map(lambda p: Path(p).name)
    ing = man.groupby("nombre").agg(archivo=("archivo", "last"), fecha_ingesta_utc=("fecha_captura_utc", "max"))

    orig = {}
    for serie, nombres in sv.groupby("serie")["archivo_origen"].agg(lambda s: sorted(set(s))).items():
        if len(nombres) != 1:
            raise ValueError(f"La serie {serie} proviene de varios archivos: {nombres}")
        nombre = nombres[0]
        if nombre not in ing.index:
            raise ValueError(f"El archivo {nombre} no tiene registro de ingesta en el manifiesto")
        archivo = ing.loc[nombre, "archivo"]
        if not (RAIZ / archivo).exists():
            raise FileNotFoundError(f"No existe el archivo de Bronce {archivo}")
        orig[serie] = {"archivo": archivo, "fecha_ingesta_utc": ing.loc[nombre, "fecha_ingesta_utc"]}
    return sv, orig


def linaje_mensual(sv, orig, meses):
    sv = sv.copy()
    sv["mes"] = sv["fecha"].dt.to_period("M").dt.to_timestamp()
    g = (
        sv.groupby(["serie", "fuente", "mes"])
        .agg(registros_origen=("valor", "size"), fecha_origen_min=("fecha", "min"), fecha_origen_max=("fecha", "max"))
        .reset_index()
    )
    g["archivo_origen_bronce"] = g["serie"].map(lambda s: orig[s]["archivo"])
    g["fecha_ingesta_utc"] = g["serie"].map(lambda s: orig[s]["fecha_ingesta_utc"])
    ln = g[g["mes"].isin(meses)].sort_values(["mes", "serie"]).reset_index(drop=True)
    return ln, len(sv) - int(ln["registros_origen"].sum())


def por_mes(ln, series):
    sub = ln[ln["serie"].isin(series)]
    return sub.groupby("mes").agg(
        fuentes_bronce=("archivo_origen_bronce", lambda s: ";".join(sorted(set(s)))),
        fecha_ingesta_utc=("fecha_ingesta_utc", "max"),
    )


def por_periodo(gm, claves):
    tmp = gm.copy()
    tmp["clave"] = claves
    return tmp.groupby("clave").agg(fuentes_bronce=("fuentes_bronce", unir), fecha_ingesta_utc=("fecha_ingesta_utc", "max"))


def verificar(nombre, t):
    vacios = int(t["fuentes_bronce"].isna().sum() + t["fecha_ingesta_utc"].isna().sum())
    if vacios:
        raise ValueError(f"{nombre}: hay filas sin linaje")
    archivos = set(";".join(t["fuentes_bronce"]).split(";"))
    for f in archivos:
        if not (RAIZ / f).exists():
            raise FileNotFoundError(f"{nombre}: no existe el archivo de Bronce {f}")
    return archivos


def main():
    sv, orig = cargar_origenes()
    oro = pd.read_csv(ORO / "tabla_oro.csv", index_col="mes", parse_dates=["mes"])
    ln, sin_oro = linaje_mensual(sv, orig, set(oro.index))
    ln.to_csv(ORO / "linaje_mensual.csv", index=False)

    gm_oro = por_mes(ln, [S_INEGI, S_BANXICO, S_FIX])
    gm_mod = por_mes(ln, [S_INEGI, S_FIX])

    resultados = {}
    oro = oro.drop(columns=COLS_LINAJE, errors="ignore").join(gm_oro)
    oro.to_csv(ORO / "tabla_oro.csv")
    resultados["tabla_oro (mensual)"] = oro

    mod = pd.read_csv(ORO / "tabla_modelado.csv", index_col="mes", parse_dates=["mes"])
    mod = mod.drop(columns=COLS_LINAJE, errors="ignore").join(gm_mod)
    mod.to_csv(ORO / "tabla_modelado.csv")
    resultados["tabla_modelado (mensual)"] = mod

    tri = pd.read_csv(ORO / "tabla_trimestral.csv", index_col="trimestre")
    gq = por_periodo(gm_mod, [f"{d.year}-T{d.quarter}" for d in gm_mod.index])
    tri = tri.drop(columns=COLS_LINAJE, errors="ignore").join(gq)
    tri.to_csv(ORO / "tabla_trimestral.csv")
    resultados["tabla_trimestral"] = tri

    anu = pd.read_csv(ORO / "tabla_anual.csv", index_col="anio")
    ga = por_periodo(gm_mod, [d.year for d in gm_mod.index])
    anu = anu.drop(columns=COLS_LINAJE, errors="ignore").join(ga)
    anu.to_csv(ORO / "tabla_anual.csv")
    resultados["tabla_anual"] = anu

    par = pd.read_csv(ORO / "parametros_escalado.csv", index_col="columna")
    par = par.drop(columns=COLS_LINAJE, errors="ignore")
    par["fuentes_bronce"] = [orig[PARAM_SERIE[c]]["archivo"] for c in par.index]
    par["fecha_ingesta_utc"] = [orig[PARAM_SERIE[c]]["fecha_ingesta_utc"] for c in par.index]
    par.to_csv(ORO / "parametros_escalado.csv")
    resultados["parametros_escalado"] = par

    tiendas = pd.read_csv(ORO / "tiendas_oro.csv")
    for col in ["id_origen", "archivo_origen", "fecha_ingesta_utc"]:
        if tiendas[col].isna().any():
            raise ValueError(f"tiendas_oro: hay filas sin {col}")
    for f in set(tiendas["archivo_origen"]):
        if not (RAIZ / f).exists():
            raise FileNotFoundError(f"tiendas_oro: no existe el archivo de Bronce {f}")

    print("--- Linaje por tabla de Oro ---")
    todos = set()
    for nombre, t in resultados.items():
        archivos = verificar(nombre, t)
        todos |= archivos
        print(f"{nombre}: {len(t)} filas, todas con linaje | archivos de Bronce distintos: {len(archivos)}")
    print(f"tiendas_oro: {len(tiendas)} filas, todas con id_origen, archivo y fecha de ingesta")

    n_arch = oro["fuentes_bronce"].map(lambda s: len(s.split(";")))
    print("\nArchivos de Bronce por mes en tabla_oro:", n_arch.value_counts().sort_index().to_dict())
    print(f"Tabla de linaje: {len(ln)} filas (mes x serie)")
    print(f"Registros de Plata que aún no llegan a Oro (meses sin INPC publicado): {sin_oro}")

    print("\n--- Archivos de Bronce y fechas de ingesta ---")
    for serie, o in orig.items():
        print(f"{serie}: {o['archivo']} | ingesta {o['fecha_ingesta_utc']}")
    print(f"tiendas_colima: {tiendas['archivo_origen'].iloc[0]} | ingesta {tiendas['fecha_ingesta_utc'].iloc[0]}")

    ultimo = oro.index.max()
    print(f"\n--- Ejemplo de trazado: mes {ultimo:%Y-%m} ---")
    print(ln[ln["mes"] == ultimo][["serie", "archivo_origen_bronce", "fecha_ingesta_utc",
                                    "registros_origen", "fecha_origen_min", "fecha_origen_max"]].to_string(index=False))

    informe(orig, tiendas, oro, ln, sin_oro, ultimo, RAIZ / "docs" / "E2" / "linaje.md")
    print("\nGuardado: datos/oro/linaje_mensual.csv, columnas de linaje en las tablas de Oro y docs/E2/linaje.md")


def informe(orig, tiendas, oro, ln, sin_oro, ultimo, ruta):
    filas = "\n".join(f"| {s} | `{o['archivo']}` | {o['fecha_ingesta_utc']} |" for s, o in orig.items())
    dist = oro["fuentes_bronce"].map(lambda s: len(s.split(";"))).value_counts().sort_index().to_dict()
    texto = f"""# Linaje y trazabilidad de datos (E2)

Cada registro de la capa Oro puede rastrearse hasta su archivo de la capa Bronce y su fecha de ingesta.

## 1. Cómo funciona

- **Ingesta:** cada captura se registra en `datos/bronce/manifiesto.csv` (fuente, serie, observaciones, archivo, estado y fecha de captura en UTC).
- **Plata:** cada registro validado conserva `archivo_origen`, `fecha_raw` y `valor_raw` de su origen.
- **Oro de E1 (series de tiempo):** las tablas llevan las columnas `fuentes_bronce` (archivos de Bronce usados por esa fila) y `fecha_ingesta_utc` (la más reciente de esas fuentes). La tabla `datos/oro/linaje_mensual.csv` detalla cada mes y serie: archivo, fecha de ingesta, número de registros de origen y rango de fechas de origen.
- **Oro de E2 (OpenStreetMap):** cada tienda lleva `id_origen` (tipo e id de OpenStreetMap), `archivo_origen`, `fecha_ingesta_utc` y `osm_base_timestamp` (fecha de los datos de OpenStreetMap). La tabla por municipio conserva el archivo y la fecha de ingesta de las tiendas y de los límites.

## 2. Archivos de Bronce vigentes

| Serie | Archivo de Bronce | Fecha de ingesta (UTC) |
|---|---|---|
{filas}
| tiendas_colima | `{tiendas['archivo_origen'].iloc[0]}` | {tiendas['fecha_ingesta_utc'].iloc[0]} |

## 3. Verificaciones automáticas

- Ninguna fila de Oro queda sin `fuentes_bronce` ni `fecha_ingesta_utc`.
- Todos los archivos de Bronce citados existen en el repositorio.
- Las cifras agregadas por municipio coinciden con las tiendas de origen (`src/oro_osm.py`).
- Archivos de Bronce por mes en `tabla_oro`: {dist} (los meses anteriores a 2020 solo vienen del INEGI).
- Filas en la tabla de linaje: {len(ln)}. Registros de Plata que aún no llegan a Oro por corresponder a meses sin INPC publicado: {sin_oro}.

## 4. Ejemplo: rastrear el mes {ultimo:%Y-%m}

{FENCE}python
import pandas as pd
ln = pd.read_csv("datos/oro/linaje_mensual.csv", parse_dates=["mes"])
print(ln[ln["mes"] == "{ultimo:%Y-%m-%d}"])
{FENCE}

Cada fila indica el archivo de Bronce de origen, su fecha de ingesta y los registros que contribuyeron.

## 5. Limitaciones

- Si el extractor corre dos veces el mismo día, el archivo de Bronce de ese día se reemplaza; la fecha de ingesta registrada es la de la última captura.
- Los parámetros de escalado (`parametros_escalado.csv`) se calculan con toda la muestra, así que su linaje apunta a las series completas.
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    main()