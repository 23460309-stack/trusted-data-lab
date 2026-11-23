
# Relatoría de etapa: E2

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos

## 1. Contexto

La etapa E2 consiste en integrar una fuente de datos avanzada al observatorio, garantizar la trazabilidad de los registros e incorporar una declaración de ética y legalidad. Se eligió la opción geoespacial, con el objetivo de mapear las tiendas de Colima, que son el cliente potencial del observatorio.

## 2. Actividades realizadas

1. **Evaluación del DENUE del INEGI** como fuente: se obtuvo el token, se escribió un sondeo y un diagnóstico con seis consultas, entre ellas el ejemplo oficial de la documentación.
2. **Cambio a OpenStreetMap** (Overpass API): sondeo de tiendas y municipios, y un extractor que guarda los datos en la capa Bronce con minimización de datos.
3. **Plata geoespacial:** validación con Pandera, polígonos municipales y cruce espacial para asignar cada tienda a su municipio.
4. **Oro geoespacial:** tabla por municipio, tabla de tiendas con linaje y mapa.
5. **Linaje:** columnas de origen en todas las tablas de Oro y tabla de linaje mensual.
6. **Declaración de ética y legalidad** con el análisis de términos, robots.txt, licencias, privacidad y sesgos.
7. **Automatización:** pipeline de 10 etapas y flujo de GitHub Actions actualizado.

## 3. Decisiones de diseño

- Se descartó el DENUE porque su API no devolvió resultados ni para el ejemplo de su documentación, ni desde Python ni desde el navegador. Se conserva el diagnóstico en `src/sondeos/`.
- Se eligió OpenStreetMap porque la consulta no necesita token, entrega tiendas y límites municipales en una misma fuente, y está entre las opciones geoespaciales aceptadas.
- Minimización de datos: se descartan nombre, sitio web, teléfono, correo, dirección y horario desde la ingesta, para no almacenar datos que puedan identificar a personas.
- Los límites municipales se piden municipio por municipio, con varios servidores y reintento que retoma los faltantes.
- La capa Plata usa siempre el archivo de límites más reciente que tenga los 10 municipios, para no asignar tiendas con un archivo incompleto.
- El paso de OpenStreetMap del flujo automático no detiene el pipeline si falla.

## 4. Hallazgos

- OpenStreetMap registra 209 tiendas en Colima, todas con coordenadas y todas válidas en la Puerta de Calidad.
- La distribución es muy desigual: Manzanillo concentra el 44.5% y Ixtlahuacán no tiene ninguna. Es improbable que refleje la realidad, y es un sesgo de cobertura medible.
- El 35.4% de las tiendas tiene marca: las cadenas están sobrerrepresentadas frente a las tiendas de abarrotes independientes, que son el cliente del observatorio.
- La mayor densidad es la de Villa de Álvarez (11.52 tiendas por cada 100 km²), por ser el municipio más pequeño y urbano.
- Los 10 polígonos municipales suman 5,752.5 km².
- El flujo automático puede fallar en el paso de OpenStreetMap por saturación de los servidores públicos, y el pipeline continúa con los últimos datos guardados.

## 5. Dificultades y cómo se resolvieron

| Dificultad                                                                                                   | Solución                                                                          |
| ------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| La API del DENUE respondió "No hay resultados" incluso para el ejemplo oficial, en Python y en el navegador | Se descartó y se cambió a OpenStreetMap                                          |
| `ModuleNotFoundError: requests` al ejecutar el sondeo (la terminal usaba otro intérprete de Python)       | `python -m pip install -r requirements.txt`                                      |
| Overpass devolvió 502, 504 y tiempo agotado con la consulta de los límites de todos los municipios         | Una consulta por municipio, varios servidores y reintento que retoma los faltantes |
| Solo se descargaron 9 de los 10 municipios en la primera corrida                                             | Se repitió la ejecución con la opción `--solo-limites` hasta completar los 10 |
| El flujo de GitHub no tenía las librerías geoespaciales en `requirements.txt`                            | Se agregaron geopandas, pyogrio, pyproj y shapely con sus versiones                |

## 6. Evidencias

- Mapa: `docs/E2/mapa_tiendas_colima.png`.
- Linaje: `docs/E2/linaje.md` y `datos/oro/linaje_mensual.csv`.
- Declaración de ética: `docs/etica-datos.md`.
- Bitácoras de la Puerta de Calidad: `datos/cuarentena/bitacora_puerta.csv` y `datos/cuarentena/bitacora_puerta_osm.csv`.
- Flujo en GitHub Actions: ejecución #5 (éxito).

## 7. Siguientes pasos

- Comparar la cobertura de OpenStreetMap con el conteo oficial del DENUE cuando su API funcione.
- Agregar datos de población para calcular tiendas por habitante.
- E3: series de componentes del INPC para el análisis multivariado.
