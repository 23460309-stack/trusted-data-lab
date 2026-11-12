
# Relatoría de etapa: E1

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos

## 1. Contexto

La etapa E1 consiste en automatizar el flujo de datos hacia las capas Plata y Oro mediante pipelines de limpieza estadística y una Puerta de Calidad con cuarentena de registros inválidos. Se parte de la capa Bronce construida en E0: el INPC general nacional del INEGI (694 meses desde 1969), el INPC nacional de Banxico (82 meses desde 2020) y el tipo de cambio FIX de Banxico (1725 registros diarios desde 2020).

## 2. Actividades realizadas

1. **Lectura e integración de las fuentes heterogéneas.** Se unificaron formatos de fecha (`2026/09` frente a `01/09/2026`), tipos de dato (valores en texto a numéricos) y frecuencias (el tipo de cambio diario se resumió por mes). Se conciliaron los dos INPC.
2. **Puerta de Calidad con Pandera.** Cada registro se valida contra un esquema y reglas de rango, fecha y unicidad. Los inválidos van a cuarentena con su motivo y nunca se borran.
3. **Valores faltantes.** Diagnóstico del mecanismo, comparación de tres métodos de imputación y decisión justificada.
4. **Atípicos y ruido.** Detección con IQR y Z-Score robusto sobre las variaciones mensuales, tratamiento por winsorización y suavizado del tipo de cambio.
5. **Normalización y estandarización** con Min-Max y Z-Score, verificadas contra scikit-learn.
6. **Discretización y jerarquías conceptuales** (temporal y de inflación).
7. **Reducción de datos** por selección de variables y agregación trimestral y anual.
8. **Automatización:** un orquestador (`src/pipeline.py`) y el flujo de GitHub Actions que regenera Bronce, Plata y Oro cada semana.

## 3. Decisiones de diseño

- Los atípicos se buscan en las variaciones mensuales y no en los niveles, porque el INPC crece con el tiempo y en niveles marcaría todo lo reciente como atípico.
- Un mes es atípico solo si lo marcan los dos métodos (IQR y Z-Score robusto), para reducir falsos positivos.
- Los atípicos se tratan como eventos económicos reales: se acotan solo para el modelado y el valor original se conserva.
- No se imputan los faltantes anteriores a 2020: rellenar décadas de tipo de cambio con valores estimados sería inventar información.
- Se descartó el muestreo por tratarse de una serie de tiempo.
- En la Puerta de Calidad, que haya registros en cuarentena no detiene el pipeline; sí lo detiene un fallo estructural o que válidos más cuarentena no igualen la entrada.

## 4. Hallazgos

- Las series oficiales llegaron limpias: de 2501 registros reales, los 2501 pasaron la Puerta de Calidad. Para comprobar que la puerta funciona se usó una prueba con 8 registros sintéticos defectuosos: 2 pasaron y 6 fueron a cuarentena con su motivo.
- El INPC de Banxico y el del INEGI son idénticos en los 82 meses comparados (diferencia máxima 0.000000).
- Los 612 faltantes son anteriores a 2020 y los causó la ventana de descarga. La prueba de Mann-Whitney (p = 5e-49) indica que la ausencia se relaciona con el INPC, por lo que no es MCAR: se clasificó como MAR estructural.
- La interpolación lineal fue el mejor método de imputación (RMSE 0.349).
- Los 86 atípicos del INPC se concentran en la inflación alta de los años 80 (72 meses; los mayores, enero de 1988 y diciembre de 1987). Los del tipo de cambio son marzo de 2020 (+18.75%), abril de 2020 y junio de 2024.
- La inflación mensual promedio fue de 4.31% en los años 80 y de 0.33% a 0.40% desde el año 2000.
- Desde 2010, el trimestre 4 tiene el mayor promedio de inflación mensual (0.597%) y el trimestre 2 el menor (-0.008%). Es una pista de estacionalidad que se pondrá a prueba en E2.
- La correlación de -0.69 entre el INPC y el tipo de cambio es probablemente espuria (niveles con tendencia en un periodo corto) y no se interpreta como relación causal.

## 5. Dificultades y cómo se resolvieron

| Dificultad                                                                                                                               | Solución                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Error en `src/atipicos.py` al contar atípicos por década: se agrupaba con el índice de la tabla completa tras filtrar los atípicos | Se filtró primero y se agrupó con el índice de la tabla filtrada |
| `git push` rechazado porque el flujo automático había subido datos nuevos al repositorio                                             | `git pull --no-rebase --no-edit` y luego `git push`             |

## 6. Evidencias

- Informes por etapa en `docs/E1/`.
- Gráfica de atípicos: `docs/E1/atipicos.png`.
- Bitácora de la Puerta de Calidad: `datos/cuarentena/bitacora_puerta.csv`.
- Ejecución del flujo en GitHub Actions: Pipeline Bronce, Plata y Oro, ejecución #3 (éxito).

## 7. Siguientes pasos

- E1 (continuación): modelo de pronóstico del INPC con parámetros de escalado calculados solo con el periodo de entrenamiento.
- E2: experimentar con el efecto del tipo de cambio y de la temporada del año sobre la variación mensual del INPC.
- E3: agregar series de componentes del INPC para la comparación multivariada, y ampliar la ventana de descarga de Banxico hacia atrás.
