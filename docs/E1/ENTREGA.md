
# Ficha de entrega técnica: E1

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos (equipo de 1 integrante)
**Repositorio:** https://github.com/23460309-stack/trusted-data-lab
**Tag:** `e1`

## 1. Resumen de lo entregado

| #  | Entregable de E1                                            | Implementación                                     | Documentación                                                          |
| -- | ----------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------------------- |
| 1a | Valores faltantes: mecanismo e imputación justificada      | `src/faltantes.py`                                | `docs/E1/diagnostico_faltantes.md`                                    |
| 1b | Atípicos y ruido (IQR y Z-Score robusto)                   | `src/atipicos.py`                                 | `docs/E1/atipicos.md`, `docs/E1/atipicos.png`                       |
| 1c | Normalización y estandarización (Min-Max y Z-Score)       | `src/normalizar.py`                               | `docs/E1/normalizacion.md`                                            |
| 1d | Discretización y jerarquías conceptuales                  | `src/discretizar.py`                              | `docs/E1/discretizacion.md`                                           |
| 1e | Reducción de datos (selección de variables y agregación) | `src/reducir.py`                                  | `docs/E1/reduccion.md`, `docs/E1/correlaciones.csv`                 |
| 2  | Integración de fuentes heterogéneas                       | `src/cargar_bronce.py`, `src/integrar.py`       | `docs/E1/integracion.md`, `docs/E1/conciliacion_inpc.csv`           |
| 3  | Puerta de Calidad automática (Pandera) con cuarentena      | `src/puerta_calidad.py`, `src/probar_puerta.py` | `docs/E1/puerta_calidad.md`, `datos/cuarentena/bitacora_puerta.csv` |
| 4  | Ficha técnica y relatoría                                 | Este documento                                      | `docs/relatoria-E1.md`                                                |

## 2. Flujo de datos

- **Bronce:** `src/extractor.py` descarga las series crudas del INEGI y de Banxico (`datos/bronce/`).
- **Plata:** la Puerta de Calidad valida cada registro. Los válidos pasan a `datos/plata/series_validas.csv` y los inválidos van a `datos/cuarentena/` con su motivo. Después se aplican faltantes y atípicos (`datos/plata/tabla_mensual.csv` y `tabla_limpia.csv`).
- **Oro:** normalización, discretización y reducción (`datos/oro/`: `tabla_oro.csv`, `tabla_modelado.csv`, `tabla_trimestral.csv` y `tabla_anual.csv`).
- **Orquestador:** `src/pipeline.py` ejecuta las siete etapas de Plata y Oro en orden, se detiene si alguna falla y verifica las salidas.

## 3. Resultados principales

| Etapa                                                | Resultado                                                                                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Puerta de Calidad (datos reales)                     | 2501 registros de entrada: 2501 válidos y 0 en cuarentena                                                                                       |
| Puerta de Calidad (prueba con registros sintéticos) | 8 de entrada: 2 válidos y 6 en cuarentena, cada uno con su motivo                                                                               |
| Conciliación del INPC (INEGI vs Banxico)            | 82 meses comparados, diferencia máxima 0.000000                                                                                                 |
| Faltantes                                            | 612 meses (88.2%) sin dato en las series de Banxico, todos anteriores a 2020: mecanismo MAR estructural; 0 huecos internos y 0 valores imputados |
| Método de imputación elegido                       | Interpolación lineal (RMSE 0.349, frente a 0.553 del último valor y 1.594 de la media global)                                                  |
| Atípicos                                            | INPC: 86 meses (72 en los años 80); tipo de cambio: 3 meses (marzo y abril de 2020 y junio de 2024)                                             |
| Normalización                                       | Verificada contra scikit-learn                                                                                                                   |
| Reducción                                           | 36 columnas a 7 en la tabla de modelado; 232 trimestres y 58 años                                                                               |

## 4. Automatización

El flujo `.github/workflows/captura.yml` (Pipeline Bronce, Plata y Oro) se ejecuta cada lunes a las 14:00 UTC y también de forma manual. Descarga las series, ejecuta el pipeline y sube a `datos/` los resultados. La ejecución #3 terminó con éxito.

## 5. Cómo verificar

- Pestaña **Actions → Pipeline Bronce, Plata y Oro** del repositorio.
- Ejecución local, con los tokens como variables de entorno: `python src/extractor.py` y luego `python src/pipeline.py`.
- Prueba de la Puerta de Calidad: `python src/probar_puerta.py`.

## 6. Decisiones y limitaciones

- Los datos de precios son nacionales (no existe una serie de INPC de Colima en el BIE); Colima se mantiene como región de estudio y de validación con el cliente.
- El INPC de Banxico es idéntico al del INEGI, por lo que se descarta en la reducción y se conserva solo para conciliar.
- Los faltantes anteriores a 2020 se deben a la ventana de descarga configurada en `src/series.json`; no se imputan y se documentan como ausencia estructural.
- Los atípicos se interpretan como eventos económicos reales y se acotan (winsorización) solo para el modelado; el valor original se conserva.
- Muestreo no aplicado: es una serie de tiempo de 694 observaciones y el orden temporal es esencial para el pronóstico.
- Los parámetros de escalado se calcularon con toda la muestra; para el modelo de pronóstico se recalcularán solo con el periodo de entrenamiento.

## 7. Lista de verificación de entrega

- [ ] Tag `e1` creado y subido a GitHub
- [ ] Enlace registrado en el formulario oficial del proyecto integrador
