"""Diagnóstico de valores faltantes (MCAR/MAR/MNAR) e imputación justificada.

Entrada: datos/plata/series_validas.csv (registros que pasaron la Puerta de Calidad).
Salidas: datos/plata/tabla_mensual.csv y docs/E1/diagnostico_faltantes.md
"""
import numpy as np
import pandas as pd
from scipy import stats

from config import PLATA, RAIZ
from integrar import integrar

COLUMNAS = ["inpc_banxico", "tc_fix_prom", "tc_fix_cierre"]
COL_EXPERIMENTO = "tc_fix_prom"
FRACCION = 0.10
REPETICIONES = 200
SEMILLA = 42
LIMITE_IMPUTACION = 2
FENCE = "`" * 3


def cargar_plata():
    return pd.read_csv(PLATA / "series_validas.csv", parse_dates=["fecha"])


def diagnostico(tabla):
    filas = []
    for col in COLUMNAS:
        falta = tabla[col].isna()
        primero = tabla[col].first_valid_index()
        antes = int((falta & (tabla.index < primero)).sum())
        internos = int((falta & (tabla.index >= primero)).sum())
        _, p = stats.mannwhitneyu(
            tabla.loc[falta, "inpc_inegi"], tabla.loc[~falta, "inpc_inegi"]
        )
        filas.append({
            "columna": col,
            "faltantes": int(falta.sum()),
            "pct": round(100 * falta.mean(), 1),
            "primer_dato": primero.strftime("%Y-%m"),
            "faltantes_antes_del_primer_dato": antes,
            "huecos_internos": internos,
            "p_mannwhitney_inpc": f"{p:.2e}",
        })
    return pd.DataFrame(filas)


def comparar_metodos(serie):
    s = serie.dropna()
    rng = np.random.default_rng(SEMILLA)
    errores = {"media_global": [], "ultimo_valor": [], "interpolacion_lineal": []}
    n = max(1, int(len(s) * FRACCION))
    for _ in range(REPETICIONES):
        pos = rng.choice(np.arange(1, len(s) - 1), size=n, replace=False)
        real = s.iloc[pos].to_numpy()
        oculta = s.copy()
        oculta.iloc[pos] = np.nan
        estimaciones = {
            "media_global": np.full(n, oculta.mean()),
            "ultimo_valor": oculta.ffill().iloc[pos].to_numpy(),
            "interpolacion_lineal": oculta.interpolate(method="linear").iloc[pos].to_numpy(),
        }
        for nombre, est in estimaciones.items():
            errores[nombre].append(float(np.sqrt(np.mean((est - real) ** 2))))
    rmse = pd.Series({k: float(np.mean(v)) for k, v in errores.items()}, name="RMSE_medio")
    return rmse.sort_values()


def imputar(tabla, metodo):
    salida = tabla.copy()
    total = 0
    for col in COLUMNAS:
        original = salida[col]
        if metodo == "interpolacion_lineal":
            nuevo = original.interpolate(method="linear", limit=LIMITE_IMPUTACION, limit_area="inside")
        elif metodo == "ultimo_valor":
            nuevo = original.ffill(limit=LIMITE_IMPUTACION)
        else:
            nuevo = original.fillna(original.mean())
        marca = original.isna() & nuevo.notna()
        salida[col] = nuevo
        salida[f"{col}_imputado"] = marca
        total += int(marca.sum())
    return salida, total


def escribir_informe(diag, rmse, mejor, total_imputados, estructural, ruta):
    mecanismo = (
        "Todos los faltantes son anteriores al primer dato de cada serie (no hay huecos internos): "
        "son faltantes por diseño. Su causa es la ventana de descarga (`inicio` en `src/series.json`), "
        "decidida sin mirar los valores. Dependen solo del tiempo, que es una variable observada, "
        "así que no son MCAR en sentido estricto y se clasifican como MAR (estructural). "
        "MNAR no se puede descartar con los datos, pero no hay evidencia a favor: la causa documentada "
        "es independiente de los valores faltantes."
        if estructural else
        "Hay huecos internos además de los anteriores al primer dato; revisar caso por caso."
    )
    texto = f"""# Valores faltantes: diagnóstico e imputación (E1)

## 1. Diagnóstico

{FENCE}text
{diag.to_string(index=False)}
{FENCE}

- `p_mannwhitney_inpc`: prueba de Mann-Whitney sobre el INPC (variable observada) entre meses con y sin dato. Un p-valor muy pequeño indica que la ausencia se relaciona con una variable observada, lo que descarta MCAR.
- Limitación: la prueba de Little para MCAR no está disponible en las librerías usadas, por lo que el argumento combina la prueba anterior con la causa documentada.

## 2. Mecanismo

{mecanismo}

## 3. Justificación del método de imputación

Se ocultó al azar el {int(FRACCION * 100)}% de los meses de `{COL_EXPERIMENTO}` ({REPETICIONES} repeticiones, semilla {SEMILLA}) y se reconstruyeron con tres métodos.

{FENCE}text
{rmse.to_string()}
{FENCE}

Método elegido: **{mejor}** (menor RMSE medio).

## 4. Decisión aplicada

- Huecos internos de hasta {LIMITE_IMPUTACION} meses consecutivos: se imputan con {mejor} y se marcan en las columnas `<columna>_imputado`. Valores imputados en esta corrida: **{total_imputados}**.
- Meses anteriores al primer dato: **no se imputan**. Rellenar décadas de tipo de cambio con valores estimados sería inventar información; se mantienen como nulos y se documentan como ausencia estructural.
- Alternativa pendiente: ampliar la ventana de descarga de Banxico hacia atrás para reducir estos faltantes.
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    tabla = integrar(cargar_plata())

    diag = diagnostico(tabla)
    print("--- Diagnóstico ---")
    print(diag.to_string(index=False))

    rmse = comparar_metodos(tabla[COL_EXPERIMENTO])
    print("\n--- Error de reconstrucción (RMSE medio) ---")
    print(rmse.to_string())
    mejor = rmse.index[0]

    final, total = imputar(tabla, mejor)
    estructural = bool((diag["huecos_internos"] == 0).all())
    print(f"\nMétodo elegido: {mejor} | Valores imputados: {total}")

    destino = PLATA / "tabla_mensual.csv"
    final.to_csv(destino)
    informe = RAIZ / "docs" / "E1" / "diagnostico_faltantes.md"
    escribir_informe(diag, rmse, mejor, total, estructural, informe)
    print(f"Guardado: {destino.relative_to(RAIZ).as_posix()} y {informe.relative_to(RAIZ).as_posix()}")