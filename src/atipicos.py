"""Detección y tratamiento de atípicos y ruido (IQR + Z-Score robusto).

Entrada: datos/plata/tabla_mensual.csv
Salidas: datos/plata/tabla_limpia.csv, docs/E1/atipicos.png y docs/E1/atipicos.md
Los valores originales nunca se modifican: se agregan columnas de bandera y versión winsorizada.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import PLATA, RAIZ

K_IQR = 1.5
UMBRAL_Z = 3.5
VENTANA_SUAV = 3
FENCE = "`" * 3
VARIABLES = {
    "var_inpc_pct": "Variación mensual del INPC (%)",
    "var_tc_pct": "Variación mensual del tipo de cambio FIX (%)",
}


def cargar():
    return pd.read_csv(PLATA / "tabla_mensual.csv", index_col="mes", parse_dates=["mes"])


def variaciones(t):
    v = pd.DataFrame(index=t.index)
    v["var_inpc_pct"] = (t["inpc_inegi"] / t["inpc_inegi"].shift(1) - 1) * 100
    v["var_tc_pct"] = (t["tc_fix_prom"] / t["tc_fix_prom"].shift(1) - 1) * 100
    return v


def limites_iqr(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - K_IQR * iqr, q3 + K_IQR * iqr


def z_robusto(s):
    med = s.median()
    mad = (s - med).abs().median()
    return 0.6745 * (s - med) / mad


def tratar(v):
    resumen = []
    for col in VARIABLES:
        s = v[col]
        lo, hi = limites_iqr(s)
        v[f"{col}_z"] = z_robusto(s)
        f_iqr = (s < lo) | (s > hi)
        f_z = v[f"{col}_z"].abs() > UMBRAL_Z
        v[f"{col}_atipico"] = f_iqr & f_z
        v[f"{col}_w"] = s.where(~v[f"{col}_atipico"], s.clip(lo, hi))
        resumen.append({
            "variable": col,
            "observaciones": int(s.notna().sum()),
            "limite_inf_iqr": round(lo, 3),
            "limite_sup_iqr": round(hi, 3),
            "atipicos_iqr": int(f_iqr.sum()),
            "atipicos_zrobusto": int(f_z.sum()),
            "atipicos_ambos": int(v[f"{col}_atipico"].sum()),
        })
    return v, pd.DataFrame(resumen)


def top_atipicos(v, col, n=8):
    d = v.loc[v[f"{col}_atipico"], [col, f"{col}_z"]].copy()
    d["abs_z"] = d[f"{col}_z"].abs()
    return d.sort_values("abs_z", ascending=False).head(n).drop(columns="abs_z")


def graficar(v, ruta):
    fig, ejes = plt.subplots(2, 1, figsize=(11, 7))
    for eje, (col, titulo) in zip(ejes, VARIABLES.items()):
        s = v[col]
        marca = v[f"{col}_atipico"]
        eje.plot(s.index, s, linewidth=0.8)
        eje.scatter(s.index[marca], s[marca], color="red", s=14, label="atípico (IQR y Z robusto)")
        eje.set_title(titulo)
        eje.legend()
    fig.tight_layout()
    fig.savefig(ruta, dpi=120)
    plt.close(fig)


def informe(resumen, por_decada, tops, ruta):
    bloques = "\n".join(
        f"### {VARIABLES[c]}\n\n{FENCE}text\n{tops[c].to_string()}\n{FENCE}\n" for c in VARIABLES
    )
    texto = f"""# Atípicos y ruido (E1)

## 1. Método

Se analizan las **variaciones mensuales (%)**, no los niveles, porque el INPC crece con el tiempo y en niveles marcaría todo lo reciente como atípico.

- **IQR:** atípico si queda fuera de [Q1 - {K_IQR}*IQR, Q3 + {K_IQR}*IQR].
- **Z-Score robusto:** 0.6745*(x - mediana)/MAD; atípico si |Z| > {UMBRAL_Z}.
- **Regla:** un mes es atípico solo si lo marcan **ambos** métodos.

## 2. Resultados

{FENCE}text
{resumen.to_string(index=False)}
{FENCE}

Atípicos del INPC por década:

{FENCE}text
{por_decada.to_string()}
{FENCE}

Meses con mayor |Z|:

{bloques}
## 3. Tratamiento

- Los registros ya pasaron la Puerta de Calidad y son datos oficiales válidos, así que los atípicos se interpretan como **eventos económicos reales**, no como errores de captura. No se eliminan.
- Se agrega, por cada variable, `_atipico` (bandera), `_z` (Z-Score robusto) y `_w` (valor winsorizado, acotado a los límites del IQR). El valor original se conserva.
- Para el modelado se podrá elegir entre la versión original y la winsorizada.

## 4. Ruido

Se agrega `tc_fix_prom_suav`, media móvil de {VENTANA_SUAV} meses del tipo de cambio mensual, para reducir fluctuación de corto plazo. La serie original se conserva.

## 5. Evidencia

Gráfica con los atípicos marcados: `docs/E1/atipicos.png`.
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    t = cargar()
    v, resumen = tratar(variaciones(t))
    t["tc_fix_prom_suav"] = t["tc_fix_prom"].rolling(VENTANA_SUAV, min_periods=VENTANA_SUAV).mean()

    limpia = t.join(v)
    limpia.to_csv(PLATA / "tabla_limpia.csv")

    atip = v.loc[v["var_inpc_pct_atipico"]]
    por_decada = atip.groupby((atip.index.year // 10) * 10).size().rename("atipicos_inpc")
    tops = {c: top_atipicos(v, c) for c in VARIABLES}

    print("--- Resumen de detección ---")
    print(resumen.to_string(index=False))
    print("\n--- Atípicos del INPC por década ---")
    print(por_decada.to_string())
    for c in VARIABLES:
        print(f"\n--- Meses con mayor |Z|: {VARIABLES[c]} ---")
        print(tops[c].to_string())

    graficar(v, RAIZ / "docs" / "E1" / "atipicos.png")
    informe(resumen, por_decada, tops, RAIZ / "docs" / "E1" / "atipicos.md")
    print("\nGuardado: datos/plata/tabla_limpia.csv, docs/E1/atipicos.png y docs/E1/atipicos.md")