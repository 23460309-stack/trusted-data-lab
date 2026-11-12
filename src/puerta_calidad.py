"""Puerta de Calidad automática (Pandera) con cuarentena.

Valida cada registro de la tabla larga de Bronce:
- válidos      -> datos/plata/series_validas.csv
- inválidos    -> datos/cuarentena/cuarentena_<fecha>.csv, con el motivo (nunca se borran)
Se registra cada ejecución en datos/cuarentena/bitacora_puerta.csv.
"""
from datetime import datetime, timezone

import pandas as pd
from pandera.errors import SchemaErrors

try:
    import pandera.pandas as pa
except ImportError:  # versiones anteriores de pandera
    import pandera as pa

from cargar_bronce import cargar_todo
from config import CUARENTENA, PLATA

COLUMNAS = ["fuente", "serie", "fecha_raw", "valor_raw", "fecha", "valor", "archivo_origen"]

# Rango plausible por serie (límite inferior excluido)
RANGOS = {
    "inpc_nacional_inegi": (0, 1000),
    "inpc_nacional": (0, 1000),
    "tipo_cambio_fix": (5, 50),
}
FECHA_MIN = pd.Timestamp("1969-01-01")


def _es_fecha(serie):
    return pd.api.types.is_datetime64_any_dtype(serie)


def construir_esquema(rango):
    hoy = pd.Timestamp.today().normalize()
    return pa.DataFrameSchema(
        {
            "fuente": pa.Column(checks=pa.Check.isin(["inegi", "banxico"])),
            "serie": pa.Column(),
            "fecha_raw": pa.Column(),
            "valor_raw": pa.Column(nullable=True),
            "fecha": pa.Column(
                checks=[
                    pa.Check(_es_fecha, error="fecha debe ser de tipo datetime"),
                    pa.Check.in_range(FECHA_MIN, hoy),
                ]
            ),
            "valor": pa.Column(float, checks=pa.Check.in_range(rango[0], rango[1], include_min=False)),
            "archivo_origen": pa.Column(),
        },
        unique=["fecha"],                    # sin fechas repetidas dentro de la serie
        report_duplicates="exclude_first",   # se conserva la primera, el resto va a cuarentena
        strict=True,                         # no se permiten columnas de más
    )


def aplicar_puerta(df):
    """Devuelve (validos, cuarentena). Lanza error si falla la estructura completa."""
    faltan = set(COLUMNAS) - set(df.columns)
    if faltan:
        raise ValueError(f"Faltan columnas en la tabla de entrada: {sorted(faltan)}")
    sin_rango = set(df["serie"]) - set(RANGOS)
    if sin_rango:
        raise ValueError(f"Series sin rango definido en la puerta: {sorted(sin_rango)}")

    validos, rechazados = [], []
    for serie, grupo in df.groupby("serie", sort=False):
        try:
            construir_esquema(RANGOS[serie]).validate(grupo, lazy=True)
            validos.append(grupo)
        except SchemaErrors as e:
            fc = e.failure_cases
            if fc["index"].isna().any():
                raise ValueError(f"Fallo estructural en la serie {serie}:\n{fc}") from e
            motivos = {}
            for _, f in fc.iterrows():
                motivos.setdefault(int(f["index"]), []).append(
                    f"{f['column']}: {f['check']} (valor={f['failure_case']})"
                )
            malos = grupo.loc[list(motivos)].copy()
            malos["motivo"] = malos.index.map(lambda i: " | ".join(motivos[i]))
            rechazados.append(malos)
            validos.append(grupo.drop(index=list(motivos)))

    ok = pd.concat(validos).sort_index() if validos else df.iloc[0:0]
    mal = pd.concat(rechazados).sort_index() if rechazados else df.iloc[0:0].assign(motivo="")
    if len(ok) + len(mal) != len(df):
        raise ValueError("La puerta perdió registros: válidos + cuarentena no igualan la entrada")
    return ok, mal


def main():
    df = cargar_todo()
    ok, mal = aplicar_puerta(df)
    ahora = datetime.now(timezone.utc)

    PLATA.mkdir(parents=True, exist_ok=True)
    CUARENTENA.mkdir(parents=True, exist_ok=True)
    ok.to_csv(PLATA / "series_validas.csv", index=False)

    if len(mal):
        mal = mal.assign(etapa="E1_puerta_calidad", fecha_cuarentena_utc=ahora.isoformat())
        mal.to_csv(CUARENTENA / f"cuarentena_{ahora:%Y%m%d_%H%M%S}.csv", index=False)

    bitacora = CUARENTENA / "bitacora_puerta.csv"
    pd.DataFrame([{
        "fecha_ejecucion_utc": ahora.isoformat(),
        "registros_entrada": len(df),
        "registros_validos": len(ok),
        "registros_cuarentena": len(mal),
    }]).to_csv(bitacora, mode="a", header=not bitacora.exists(), index=False)

    print(f"Entrada: {len(df)} | Válidos (a Plata): {len(ok)} | En cuarentena: {len(mal)}")
    if len(mal):
        print(mal[["serie", "fecha_raw", "valor_raw", "motivo"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()