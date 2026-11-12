"""Lee la capa Bronce (JSON crudos) y la convierte a una tabla larga común.

Se conservan los valores originales (fecha_raw, valor_raw) para poder
rastrear cualquier registro que luego no pase la validación.
"""
import json

import pandas as pd

from config import BRONCE, SERIES_JSON


def _ultimo_archivo(fuente, nombre):
    archivos = sorted((BRONCE / fuente).glob(f"{nombre}_*.json"))
    if not archivos:
        raise FileNotFoundError(f"No hay archivos Bronce de {fuente}/{nombre}")
    return archivos[-1]


def _leer_json(archivo):
    return json.loads(archivo.read_text(encoding="utf-8"))


def cargar_inegi(nombre):
    archivo = _ultimo_archivo("inegi", nombre)
    df = pd.DataFrame(_leer_json(archivo)["Series"][0]["OBSERVATIONS"])
    return pd.DataFrame({
        "fuente": "inegi",
        "serie": nombre,
        "fecha_raw": df["TIME_PERIOD"],
        "valor_raw": df["OBS_VALUE"],
        "fecha": pd.to_datetime(df["TIME_PERIOD"] + "/01", format="%Y/%m/%d", errors="coerce"),
        "valor": pd.to_numeric(df["OBS_VALUE"], errors="coerce"),
        "archivo_origen": archivo.name,
    })


def cargar_banxico(nombre):
    archivo = _ultimo_archivo("banxico", nombre)
    df = pd.DataFrame(_leer_json(archivo)["bmx"]["series"][0]["datos"])
    return pd.DataFrame({
        "fuente": "banxico",
        "serie": nombre,
        "fecha_raw": df["fecha"],
        "valor_raw": df["dato"],
        "fecha": pd.to_datetime(df["fecha"], format="%d/%m/%Y", errors="coerce"),
        "valor": pd.to_numeric(df["dato"], errors="coerce"),
        "archivo_origen": archivo.name,
    })


def cargar_todo():
    series = json.loads(SERIES_JSON.read_text(encoding="utf-8"))["series"]
    tablas = []
    for s in series:
        cargador = cargar_inegi if s["fuente"] == "inegi" else cargar_banxico
        tablas.append(cargador(s["nombre"]))
    return pd.concat(tablas, ignore_index=True)


def resumen(df):
    return df.groupby(["fuente", "serie"]).agg(
        filas=("valor_raw", "size"),
        desde=("fecha", "min"),
        hasta=("fecha", "max"),
        valores_nulos=("valor", lambda s: int(s.isna().sum())),
        fechas_invalidas=("fecha", lambda s: int(s.isna().sum())),
    )


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    print(resumen(cargar_todo()))