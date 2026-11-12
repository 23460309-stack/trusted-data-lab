
# Integración de fuentes heterogéneas (E1)

## Discrepancias de esquema y su resolución

| Aspecto         | INEGI (INPC)                  | Banxico (INPC)             | Banxico (tipo de cambio)   | Resolución                                                                                   |
| --------------- | ----------------------------- | -------------------------- | -------------------------- | --------------------------------------------------------------------------------------------- |
| Estructura JSON | `Series[0].OBSERVATIONS`    | `bmx.series[0].datos`    | `bmx.series[0].datos`    | Un lector por fuente que entrega la misma tabla larga                                         |
| Campo de fecha  | `TIME_PERIOD` (`2026/09`) | `fecha` (`01/09/2026`) | `fecha` (`02/01/2020`) | Se convierte a fecha real; mensual al primer día del mes                                     |
| Campo de valor  | `OBS_VALUE` (texto)         | `dato` (texto)           | `dato` (texto)           | Conversión a número; lo que no convierte queda como nulo y lo detecta la puerta de calidad  |
| Frecuencia      | Mensual                       | Mensual                    | Diaria (días hábiles)    | Tipo de cambio resumido por mes: promedio, cierre y número de días                          |
| Cobertura       | 1969 a la fecha               | 2020 a la fecha            | 2020 a la fecha            | Tabla sobre los meses del INEGI; vacíos previos a 2020 son ausencia estructural de la fuente |

## Conflicto entre fuentes: INPC

El INPC existe en dos fuentes. Se comparan mes a mes en los meses comunes (`docs/E1/conciliacion_inpc.csv`).

- **Regla:** el INEGI es la fuente primaria (origen del índice). Banxico solo se usa para verificar.
- **Tolerancia:** 0.01 puntos de índice. Una diferencia mayor se registra y prevalece el valor del INEGI.
