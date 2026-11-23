# Linaje y trazabilidad de datos (E2)

Cada registro de la capa Oro puede rastrearse hasta su archivo de la capa Bronce y su fecha de ingesta.

## 1. Cómo funciona

- **Ingesta:** cada captura se registra en `datos/bronce/manifiesto.csv` (fuente, serie, observaciones, archivo, estado y fecha de captura en UTC).
- **Plata:** cada registro validado conserva `archivo_origen`, `fecha_raw` y `valor_raw` de su origen.
- **Oro de E1 (series de tiempo):** las tablas llevan las columnas `fuentes_bronce` (archivos de Bronce usados por esa fila) y `fecha_ingesta_utc` (la más reciente de esas fuentes). La tabla `datos/oro/linaje_mensual.csv` detalla cada mes y serie: archivo, fecha de ingesta, número de registros de origen y rango de fechas de origen.
- **Oro de E2 (OpenStreetMap):** cada tienda lleva `id_origen` (tipo e id de OpenStreetMap), `archivo_origen`, `fecha_ingesta_utc` y `osm_base_timestamp` (fecha de los datos de OpenStreetMap). La tabla por municipio conserva el archivo y la fecha de ingesta de las tiendas y de los límites.

## 2. Archivos de Bronce vigentes

| Serie | Archivo de Bronce | Fecha de ingesta (UTC) |
|---|---|---|
| inpc_nacional | `datos/bronce/banxico/inpc_nacional_20261116.json` | 2026-11-16T23:04:44.459142+00:00 |
| inpc_nacional_inegi | `datos/bronce/inegi/inpc_nacional_inegi_20261116.json` | 2026-11-16T23:04:44.459142+00:00 |
| tipo_cambio_fix | `datos/bronce/banxico/tipo_cambio_fix_20261116.json` | 2026-11-16T23:04:44.459142+00:00 |
| tiendas_colima | `datos/bronce/osm/tiendas_colima_20261123.json` | 2026-11-23T06:34:45.673809+00:00 |

## 3. Verificaciones automáticas

- Ninguna fila de Oro queda sin `fuentes_bronce` ni `fecha_ingesta_utc`.
- Todos los archivos de Bronce citados existen en el repositorio.
- Las cifras agregadas por municipio coinciden con las tiendas de origen (`src/oro_osm.py`).
- Archivos de Bronce por mes en `tabla_oro`: {1: 612, 3: 82} (los meses anteriores a 2020 solo vienen del INEGI).
- Filas en la tabla de linaje: 858. Registros de Plata que aún no llegan a Oro por corresponder a meses sin INPC publicado: 9.

## 4. Ejemplo: rastrear el mes 2026-10

```python
import pandas as pd
ln = pd.read_csv("datos/oro/linaje_mensual.csv", parse_dates=["mes"])
print(ln[ln["mes"] == "2026-10-01"])
```

Cada fila indica el archivo de Bronce de origen, su fecha de ingesta y los registros que contribuyeron.

## 5. Limitaciones

- Si el extractor corre dos veces el mismo día, el archivo de Bronce de ese día se reemplaza; la fecha de ingesta registrada es la de la última captura.
- Los parámetros de escalado (`parametros_escalado.csv`) se calculan con toda la muestra, así que su linaje apunta a las series completas.
