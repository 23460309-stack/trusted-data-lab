
# Objetivos de calidad (E0)

**Autor:** Kevin Gilberto Borjas Avalos

| # | Objetivo                                 | Métrica                                                                | Meta                                                               | Cómo se verifica                                                                                                                 |
| - | ---------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Completitud histórica de la capa Bronce | Observaciones por serie en `datos/bronce/manifiesto.csv`              | Cada serie tiene al menos 36 periodos                              | Columna `observaciones` del manifiesto                                                                                          |
| 2 | Confiabilidad de la captura automática  | Porcentaje de series con estado `ok` por ejecución de GitHub Actions | 95% o más                                                         | Filas `ok` entre filas totales del manifiesto desde la entrega e0                                                               |
| 3 | Seguridad y trazabilidad                 | Credenciales en el repositorio y datos con fuente y fecha de captura    | 0 credenciales en el repo; 100% de las capturas con fuente y fecha | Revisión del repo (los tokens solo existen como secretos de GitHub) y columnas `fuente` y `fecha_captura_utc` del manifiesto |
