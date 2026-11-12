"""Prueba de la Puerta de Calidad con registros defectuosos SINTÉTICOS (solo en memoria)."""
import pandas as pd

from puerta_calidad import aplicar_puerta

casos = [
    # (fecha, valor, fecha_raw, valor_raw, defecto esperado)
    ("2026-01-02", 17.5, "02/01/2026", "17.5", "válido"),
    ("2026-01-05", 17.6, "05/01/2026", "17.6", "válido"),
    ("2026-01-06", -3.0, "06/01/2026", "-3", "valor negativo"),
    ("2026-01-07", 900.0, "07/01/2026", "900", "valor fuera de rango"),
    ("2026-01-08", None, "08/01/2026", "N/E", "valor no numérico"),
    (None, 17.8, "31/02/2026", "17.8", "fecha inválida"),
    ("2099-01-01", 17.9, "01/01/2099", "17.9", "fecha futura"),
    ("2026-01-05", 17.7, "05/01/2026", "17.7", "fecha duplicada"),
]

df = pd.DataFrame({
    "fuente": "banxico",
    "serie": "tipo_cambio_fix",
    "fecha_raw": [c[2] for c in casos],
    "valor_raw": [c[3] for c in casos],
    "fecha": pd.to_datetime([c[0] for c in casos]),
    "valor": pd.Series([c[1] for c in casos], dtype=float),
    "archivo_origen": "prueba_sintetica.json",
})

ok, mal = aplicar_puerta(df)

pd.set_option("display.width", 220)
pd.set_option("display.max_colwidth", 90)
print(f"Entrada: {len(df)} | Válidos: {len(ok)} | Cuarentena: {len(mal)}\n")
print(mal[["fecha_raw", "valor_raw", "motivo"]].to_string())
assert len(ok) == 2 and len(mal) == 6 and len(ok) + len(mal) == len(df)
print("\nPrueba superada: cada registro defectuoso fue a cuarentena con su motivo.")