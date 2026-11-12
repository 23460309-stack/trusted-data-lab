"""Reducción de datos: selección de variables y agregación temporal.

Entrada: datos/oro/tabla_oro.csv (se ejecuta después de discretizar.py)
Salidas: datos/oro/tabla_modelado.csv, tabla_trimestral.csv, tabla_anual.csv,
         docs/E1/correlaciones.csv y docs/E1/reduccion.md
"""
import pandas as pd

from config import ORO, RAIZ

UMBRAL_CORR = 0.95
FENCE = "`" * 3
# En orden de prioridad: ante dos variables redundantes se conserva la primera
CANDIDATAS = [
    "inpc_inegi", "inpc_banxico", "tc_fix_prom", "tc_fix_cierre",
    "tc_fix_prom_suav", "var_inpc_pct_w", "var_tc_pct_w",
]
CONTEXTO = ["anio", "trimestre_num", "inflacion_cat"]


def seleccionar(t):
    corr = t[CANDIDATAS].corr()  # correlación con los meses disponibles en cada par
    conservadas, descartadas = [], []
    for c in CANDIDATAS:
        redundantes = [k for k in conservadas if abs(corr.loc[c, k]) >= UMBRAL_CORR]
        if redundantes:
            descartadas.append({
                "variable": c,
                "redundante_con": redundantes[0],
                "correlacion": round(corr.loc[c, redundantes[0]], 4),
            })
        else:
            conservadas.append(c)
    return corr, conservadas, pd.DataFrame(descartadas)


def agregar_trimestral(t):
    g = t.groupby("trimestre", sort=True)
    q = pd.DataFrame({
        "meses": g.size(),
        "inpc_cierre": g["inpc_inegi"].last(),
        "inpc_prom": g["inpc_inegi"].mean(),
        "tc_fix_prom": g["tc_fix_prom"].mean(),
    })
    q["var_inpc_trim_pct"] = q["inpc_cierre"].pct_change(fill_method=None) * 100
    q["trimestre_completo"] = q["meses"] == 3
    return q


def agregar_anual(t):
    g = t.groupby("anio")
    a = pd.DataFrame({
        "meses": g.size(),
        "inpc_cierre": g["inpc_inegi"].last(),
        "tc_fix_prom": g["tc_fix_prom"].mean(),
    })
    a["inflacion_anual_pct"] = a["inpc_cierre"].pct_change(fill_method=None) * 100
    a["anio_completo"] = a["meses"] == 12
    return a


def informe(corr, conservadas, descartadas, resumen, ruta):
    desc = descartadas.to_string(index=False) if len(descartadas) else "ninguna"
    texto = f"""# Reducción de datos (E1)

## 1. Técnicas aplicadas

- **Selección de variables** por redundancia (correlación absoluta >= {UMBRAL_CORR}).
- **Agregación temporal:** mensual -> trimestral y anual.
- **Muestreo: no aplicado.** La serie tiene 694 observaciones mensuales y su orden temporal es esencial para el pronóstico; una muestra aleatoria destruiría la dependencia temporal.

## 2. Selección de variables

Matriz de correlación entre las variables candidatas (con los meses disponibles en cada par):

{FENCE}text
{corr.round(3).to_string()}
{FENCE}

Prioridad de conservación: fuente primaria (INEGI) sobre la secundaria (Banxico), y la variable original sobre sus derivadas.

- Variables conservadas: {", ".join(conservadas)}
- Variables descartadas por redundancia:

{FENCE}text
{desc}
{FENCE}

Limitación: la correlación entre niveles de series con tendencia puede ser espuria; aquí solo se usa para detectar redundancia, no para explicar relaciones.

## 3. Agregación

- `datos/oro/tabla_trimestral.csv`: cierre y promedio del INPC, variación trimestral y promedio del tipo de cambio. Se marcan los trimestres incompletos.
- `datos/oro/tabla_anual.csv`: cierre del INPC, inflación anual y promedio del tipo de cambio. Se marcan los años incompletos (2026 llega solo a octubre).

## 4. Magnitud de la reducción

{FENCE}text
{resumen.to_string(index=False)}
{FENCE}
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    t = pd.read_csv(ORO / "tabla_oro.csv", index_col="mes", parse_dates=["mes"])

    corr, conservadas, descartadas = seleccionar(t)
    modelado = t[conservadas + CONTEXTO]
    trimestral = agregar_trimestral(t)
    anual = agregar_anual(t)

    modelado.to_csv(ORO / "tabla_modelado.csv")
    trimestral.to_csv(ORO / "tabla_trimestral.csv")
    anual.to_csv(ORO / "tabla_anual.csv")
    corr.to_csv(RAIZ / "docs" / "E1" / "correlaciones.csv")

    resumen = pd.DataFrame([
        {"tabla": "tabla_oro (mensual, completa)", "filas": len(t), "columnas": t.shape[1]},
        {"tabla": "tabla_modelado (mensual, reducida)", "filas": len(modelado), "columnas": modelado.shape[1]},
        {"tabla": "tabla_trimestral", "filas": len(trimestral), "columnas": trimestral.shape[1]},
        {"tabla": "tabla_anual", "filas": len(anual), "columnas": anual.shape[1]},
    ])
    informe(corr, conservadas, descartadas, resumen, RAIZ / "docs" / "E1" / "reduccion.md")

    print("--- Matriz de correlación ---")
    print(corr.round(3).to_string())
    print(f"\nConservadas: {conservadas}")
    print("Descartadas:")
    print(descartadas.to_string(index=False) if len(descartadas) else "  ninguna")
    print("\n--- Magnitud de la reducción ---")
    print(resumen.to_string(index=False))
    print("\n--- Últimos trimestres ---")
    print(trimestral.tail(4).round(3).to_string())
    print("\n--- Últimos años ---")
    print(anual.tail(4).round(3).to_string())
    print("\nGuardado en datos/oro/ y docs/E1/ (correlaciones.csv y reduccion.md)")