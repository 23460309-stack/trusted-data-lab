"""Normalización (Min-Max) y estandarización (Z-Score) de variables continuas.

Entrada: datos/plata/tabla_limpia.csv
Salidas: datos/oro/tabla_oro.csv, datos/oro/parametros_escalado.csv y docs/E1/normalizacion.md
Los valores originales se conservan; las versiones escaladas se agregan como columnas nuevas.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from config import ORO, PLATA, RAIZ

COLUMNAS = ["inpc_inegi", "tc_fix_prom", "var_inpc_pct_w", "var_tc_pct_w"]
FENCE = "`" * 3


def parametros(t):
    p = pd.DataFrame({
        "min": t[COLUMNAS].min(),
        "max": t[COLUMNAS].max(),
        "media": t[COLUMNAS].mean(),
        "desv_std": t[COLUMNAS].std(ddof=0),
        "observaciones": t[COLUMNAS].notna().sum(),
    })
    p.index.name = "columna"
    return p


def escalar(t, p):
    o = t.copy()
    for c in COLUMNAS:
        o[f"{c}_minmax"] = (t[c] - p.loc[c, "min"]) / (p.loc[c, "max"] - p.loc[c, "min"])
        o[f"{c}_zscore"] = (t[c] - p.loc[c, "media"]) / p.loc[c, "desv_std"]
    return o


def verificar(o):
    """Compara contra scikit-learn; los nulos se conservan como nulos."""
    for c in COLUMNAS:
        mm = MinMaxScaler().fit_transform(o[[c]])[:, 0]
        zs = StandardScaler().fit_transform(o[[c]])[:, 0]
        assert np.allclose(o[f"{c}_minmax"], mm, equal_nan=True), f"Min-Max no coincide en {c}"
        assert np.allclose(o[f"{c}_zscore"], zs, equal_nan=True), f"Z-Score no coincide en {c}"


def chequeo(o):
    filas = []
    for c in COLUMNAS:
        mm, zs = o[f"{c}_minmax"], o[f"{c}_zscore"]
        filas.append({
            "columna": c,
            "minmax_min": mm.min(),
            "minmax_max": mm.max(),
            "z_media": zs.mean(),
            "z_desv": zs.std(ddof=0),
        })
    return pd.DataFrame(filas).round(4)


def informe(p, ch, ruta):
    texto = f"""# Normalización y estandarización (E1)

## 1. Método

- **Min-Max:** x' = (x - min) / (max - min). Lleva la variable al rango [0, 1].
- **Z-Score:** z = (x - media) / desviación estándar (poblacional). Centra en 0 con desviación 1.
- Se aplican a `inpc_inegi`, `tc_fix_prom` y a las variaciones mensuales winsorizadas (`var_inpc_pct_w`, `var_tc_pct_w`), que tienen unidades y escalas distintas.
- Los valores originales se conservan; las versiones escaladas se agregan con los sufijos `_minmax` y `_zscore`.
- Los nulos permanecen como nulos (no se imputan al escalar).

## 2. Parámetros

{FENCE}text
{p.round(4).to_string()}
{FENCE}

Se guardan en `datos/oro/parametros_escalado.csv` para poder revertir la transformación (por ejemplo, al devolver pronósticos a la escala original).

## 3. Verificación

{FENCE}text
{ch.to_string(index=False)}
{FENCE}

- Min-Max: mínimo 0 y máximo 1 en cada columna.
- Z-Score: media cercana a 0 y desviación cercana a 1.
- Los resultados se compararon con `MinMaxScaler` y `StandardScaler` de scikit-learn.

## 4. Limitación

Los parámetros se calcularon con toda la muestra, lo cual es adecuado para describir los datos. Para el modelo de pronóstico se calcularán únicamente con el periodo de entrenamiento, para evitar filtrar información del futuro.
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    t = pd.read_csv(PLATA / "tabla_limpia.csv", index_col="mes", parse_dates=["mes"])
    p = parametros(t)
    o = escalar(t, p)
    verificar(o)

    ORO.mkdir(parents=True, exist_ok=True)
    o.to_csv(ORO / "tabla_oro.csv")
    p.to_csv(ORO / "parametros_escalado.csv")
    ch = chequeo(o)
    informe(p, ch, RAIZ / "docs" / "E1" / "normalizacion.md")

    print("--- Parámetros ---")
    print(p.round(4).to_string())
    print("\n--- Verificación de la escala ---")
    print(ch.to_string(index=False))
    print("\nVerificación contra scikit-learn superada.")
    print("Guardado: datos/oro/tabla_oro.csv, datos/oro/parametros_escalado.csv y docs/E1/normalizacion.md")