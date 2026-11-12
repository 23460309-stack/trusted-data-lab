"""Integra las fuentes heterogéneas en una tabla mensual.

Reglas:
- Fechas a primer día del mes (frecuencia mensual).
- Tipo de cambio diario -> promedio, cierre y número de días por mes.
- El INPC del INEGI es la fuente primaria; el de Banxico se usa para conciliar.
- La tabla se arma sobre los meses del INPC del INEGI.
"""
import pandas as pd

from cargar_bronce import cargar_todo
from config import RAIZ

TOLERANCIA_INPC = 0.01   # puntos de índice
DIAS_MIN_MES = 15        # meses con menos días hábiles se marcan como parciales


def _serie_mensual(df_largo, nombre, columna):
    s = df_largo[df_largo["serie"] == nombre].set_index("fecha")["valor"].rename(columna)
    if s.index.duplicated().any():
        raise ValueError(f"Fechas duplicadas en la serie {nombre}")
    return s


def mensualizar_tipo_cambio(tc):
    tc = tc.sort_values("fecha").copy()
    tc["mes"] = tc["fecha"].dt.to_period("M").dt.to_timestamp()
    g = tc.groupby("mes")["valor"]
    return pd.DataFrame({
        "tc_fix_prom": g.mean(),
        "tc_fix_cierre": g.last(),
        "tc_dias": g.count(),
    })


def integrar(df_largo):
    inpc_inegi = _serie_mensual(df_largo, "inpc_nacional_inegi", "inpc_inegi")
    inpc_banxico = _serie_mensual(df_largo, "inpc_nacional", "inpc_banxico")
    tc = mensualizar_tipo_cambio(df_largo[df_largo["serie"] == "tipo_cambio_fix"])

    tabla = pd.concat([inpc_inegi, inpc_banxico, tc], axis=1).reindex(inpc_inegi.index)
    tabla.index.name = "mes"
    tabla["tc_mes_parcial"] = (tabla["tc_dias"] < DIAS_MIN_MES).astype("boolean").where(
        tabla["tc_dias"].notna()
    )
    return tabla.sort_index()


def conciliar_inpc(tabla):
    comun = tabla.dropna(subset=["inpc_inegi", "inpc_banxico"])[["inpc_inegi", "inpc_banxico"]].copy()
    comun["dif"] = comun["inpc_inegi"] - comun["inpc_banxico"]
    comun["dif_abs"] = comun["dif"].abs()
    return comun


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    tabla = integrar(cargar_todo())

    print("--- Últimas filas ---")
    print(tabla.tail(4))
    print("\n--- Nulos por columna ---")
    print(tabla.isna().sum())

    comun = conciliar_inpc(tabla)
    destino = RAIZ / "docs" / "E1" / "conciliacion_inpc.csv"
    comun.to_csv(destino)
    fuera = int((comun["dif_abs"] > TOLERANCIA_INPC).sum())
    print("\n--- Conciliación INPC INEGI vs Banxico ---")
    print(f"Meses comparados: {len(comun)}")
    print(f"Diferencia absoluta máxima: {comun['dif_abs'].max():.6f}")
    print(f"Meses fuera de tolerancia ({TOLERANCIA_INPC}): {fuera}")
    print(f"Detalle guardado en {destino.relative_to(RAIZ).as_posix()}")