"""Discretización de variables continuas y jerarquías conceptuales.

Entrada: datos/oro/tabla_oro.csv (se ejecuta después de normalizar.py)
Salidas: datos/oro/tabla_oro.csv (con columnas nuevas) y docs/E1/discretizacion.md
Los valores numéricos originales se conservan.
"""
import pandas as pd

from config import ORO, RAIZ

FENCE = "`" * 3

# Discretización por criterio del analista: variación mensual del INPC (%)
CORTES_INFLACION = [-float("inf"), 0, 0.5, 1.0, 3.0, float("inf")]
ETIQ_INFLACION = ["deflacion", "baja", "moderada", "alta", "muy_alta"]
GRUPO_INFLACION = {
    "deflacion": "estable",
    "baja": "estable",
    "moderada": "moderada",
    "alta": "alta",
    "muy_alta": "alta",
}
ETIQ_NIVEL = ["bajo", "medio", "alto"]
ETIQ_CUARTIL = ["q1_menor", "q2", "q3", "q4_mayor"]


def discretizar(t):
    t = t.copy()
    t["inflacion_cat"] = pd.cut(
        t["var_inpc_pct"], bins=CORTES_INFLACION, labels=ETIQ_INFLACION
    ).astype(object)
    t["tc_nivel_ancho"] = pd.cut(t["tc_fix_prom"], bins=3, labels=ETIQ_NIVEL).astype(object)
    t["tc_nivel_frec"] = pd.qcut(t["tc_fix_prom"], q=3, labels=ETIQ_NIVEL).astype(object)
    t["tc_var_cuartil"] = pd.qcut(t["var_tc_pct_w"], q=4, labels=ETIQ_CUARTIL).astype(object)
    return t


def jerarquias(t):
    t = t.copy()
    t["anio"] = [d.year for d in t.index]
    t["decada"] = [f"{d.year // 10 * 10}s" for d in t.index]
    t["semestre"] = [f"{d.year}-S{1 if d.month <= 6 else 2}" for d in t.index]
    t["trimestre"] = [f"{d.year}-T{d.quarter}" for d in t.index]
    t["trimestre_num"] = [d.quarter for d in t.index]
    t["inflacion_grupo"] = t["inflacion_cat"].map(GRUPO_INFLACION)
    return t


def verificar(t):
    assert t["inflacion_cat"].notna().sum() == t["var_inpc_pct"].notna().sum()
    assert t["inflacion_grupo"].notna().sum() == t["inflacion_cat"].notna().sum()
    assert t["tc_nivel_ancho"].notna().sum() == t["tc_fix_prom"].notna().sum()
    assert t["tc_nivel_frec"].notna().sum() == t["tc_fix_prom"].notna().sum()
    assert t["tc_var_cuartil"].notna().sum() == t["var_tc_pct_w"].notna().sum()


def tablas(t):
    comp = pd.DataFrame({
        "ancho_igual": t["tc_nivel_ancho"].value_counts(),
        "frecuencia_igual": t["tc_nivel_frec"].value_counts(),
    }).reindex(ETIQ_NIVEL).fillna(0).astype(int)
    dist = pd.crosstab(t["decada"], t["inflacion_cat"]).reindex(columns=ETIQ_INFLACION, fill_value=0)
    infl_decada = t.groupby("decada")["var_inpc_pct"].mean().round(3).rename("inflacion_mensual_prom_pct")
    estac = (
        t.loc["2010-01-01":].groupby("trimestre_num")["var_inpc_pct"].mean().round(3)
        .rename("inflacion_mensual_prom_pct")
    )
    return comp, dist, infl_decada, estac


def informe(comp, dist, infl_decada, estac, ruta):
    texto = f"""# Discretización y jerarquías conceptuales (E1)

## 1. Discretización

| Variable origen | Método | Categorías |
|---|---|---|
| `var_inpc_pct` (variación mensual del INPC, %) | Criterio del analista | deflacion (<= 0), baja (0 a 0.5], moderada (0.5 a 1], alta (1 a 3], muy_alta (> 3) |
| `tc_fix_prom` (nivel del tipo de cambio) | Ancho igual, 3 rangos | bajo, medio, alto |
| `tc_fix_prom` | Frecuencia igual, 3 grupos | bajo, medio, alto |
| `var_tc_pct_w` (variación mensual del tipo de cambio, winsorizada) | Frecuencia igual, 4 cuartiles | q1_menor, q2, q3, q4_mayor |

Los cortes de la inflación se definieron por criterio del analista (conocimiento del dominio) y son un parámetro que se puede ajustar en `src/discretizar.py`. Los valores originales se conservan; las categorías son columnas nuevas.

### Comparación de métodos: nivel del tipo de cambio (meses por categoría)

{FENCE}text
{comp.to_string()}
{FENCE}

El ancho igual produce grupos desiguales cuando los datos se concentran en una zona del rango. La frecuencia igual reparte los meses de forma pareja, pero sus fronteras dependen de los datos.

## 2. Jerarquías conceptuales

**Temporal:** mes -> trimestre -> semestre -> año -> década (columnas `trimestre`, `semestre`, `anio`, `decada`). La columna `trimestre_num` (1 a 4) permite estudiar la temporada del año (pregunta E2).

**Inflación:** deflacion y baja -> estable; moderada -> moderada; alta y muy_alta -> alta (columna `inflacion_grupo`).

## 3. Resumen por nivel jerárquico

Meses por categoría de inflación en cada década:

{FENCE}text
{dist.to_string()}
{FENCE}

Inflación mensual promedio (%) por década:

{FENCE}text
{infl_decada.to_string()}
{FENCE}

Inflación mensual promedio (%) por trimestre del año, desde 2010:

{FENCE}text
{estac.to_string()}
{FENCE}
"""
    ruta.write_text(texto, encoding="utf-8")


if __name__ == "__main__":
    pd.set_option("display.width", 220)
    t = pd.read_csv(ORO / "tabla_oro.csv", index_col="mes", parse_dates=["mes"])
    t = jerarquias(discretizar(t))
    verificar(t)
    t.to_csv(ORO / "tabla_oro.csv")

    comp, dist, infl_decada, estac = tablas(t)
    print("--- Nivel del tipo de cambio: ancho igual vs frecuencia igual ---")
    print(comp.to_string())
    print("\n--- Meses por categoría de inflación y década ---")
    print(dist.to_string())
    print("\n--- Inflación mensual promedio (%) por década ---")
    print(infl_decada.to_string())
    print("\n--- Inflación mensual promedio (%) por trimestre, desde 2010 ---")
    print(estac.to_string())

    informe(comp, dist, infl_decada, estac, RAIZ / "docs" / "E1" / "discretizacion.md")
    print("\nGuardado: datos/oro/tabla_oro.csv y docs/E1/discretizacion.md")