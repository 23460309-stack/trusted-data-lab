
# Puerta de Calidad automática (E1)

Herramienta: Pandera (`src/puerta_calidad.py`). Se valida cada registro de la tabla larga de Bronce, antes de entrar a la capa Plata.

## Reglas

| Regla    | Detalle                                                              | Si falla                                   |
| -------- | -------------------------------------------------------------------- | ------------------------------------------ |
| Esquema  | Existen las 7 columnas esperadas y no hay columnas de más           | Se detiene el pipeline (fallo estructural) |
| Fuente   | Solo `inegi` o `banxico`                                         | Cuarentena                                 |
| Fecha    | Tipo fecha, no nula, entre 1969-01-01 y hoy                          | Cuarentena                                 |
| Valor    | Numérico, no nulo, mayor que 0 y dentro del rango de su serie       | Cuarentena                                 |
| Unicidad | Una sola fila por fecha dentro de cada serie; se conserva la primera | Cuarentena (las repetidas)                 |

## Rangos plausibles por serie

| Serie               | Rango     |
| ------------------- | --------- |
| inpc_nacional_inegi | (0, 1000] |
| inpc_nacional       | (0, 1000] |
| tipo_cambio_fix     | (5, 50]   |

## Cuarentena

- Los registros inválidos se guardan en `datos/cuarentena/cuarentena_<fecha>.csv` con la columna `motivo`; nunca se borran.
- Cada ejecución queda en `datos/cuarentena/bitacora_puerta.csv` (entrada, válidos y cuarentena).
- Invariante: registros válidos + registros en cuarentena = registros de entrada. Si no se cumple, el pipeline falla.

## Pruebas

`src/probar_puerta.py` valida 8 registros sintéticos (2 buenos y 6 con defectos: valor negativo, fuera de rango, no numérico, fecha inválida, fecha futura y fecha duplicada).
