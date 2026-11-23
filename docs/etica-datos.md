
# Declaración de ética y legalidad de los datos

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos
**Última revisión:** fecha, 23 de noviembre de 2026

## 1. Fuentes y su base legal

| Fuente                       | Qué se usa                                                                              | Acceso                         | Licencia o términos             | Obligación principal                                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| INEGI, API de Indicadores    | INPC general nacional (mensual)                                                          | API oficial con token gratuito | Términos de Libre Uso del INEGI | Citar la fuente, no alterar los metadatos y no presentar el proyecto como oficial del INEGI                  |
| Banxico, API del SIE         | Tipo de cambio FIX e INPC nacional                                                       | API oficial con token gratuito | Términos de uso del SIE         | Citar a Banco de México como fuente con su dirección web y respetar los límites de consulta               |
| OpenStreetMap (Overpass API) | Tiendas (`shop` = convenience, supermarket o general) y límites municipales de Colima | API pública, sin token        | ODbL 1.0                         | Atribución "© OpenStreetMap contributors" y compartir bajo la misma licencia lo derivado que se distribuya |
| DENUE del INEGI (API)        | Evaluado, no integrado                                                                   | API oficial con token          | Términos de Libre Uso del INEGI | Ver sección 6                                                                                               |

## 2. Análisis de robots.txt

| Sitio           | Resultado                                                                                                                                                                                                                  |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| inegi.org.mx    | La ruta `/app` (donde se aloja la API) aparece con `Allow`. Las restricciones (`Disallow`) son del catálogo de microdatos (`/catalog/`) y del registro de usuarios (`/auth/register/`), que el proyecto no usa. |
| banxico.org.mx  | No se encontraron reglas que restrinjan la ruta de la API (`/SieAPIRest/`) ni un bloqueo total del sitio.                                                                                                                |
| overpass-api.de |  https://overpass-api.de/robots.txt, indicando si restringe `/api/`                                                                                                                                                     |

Los tres servicios usados son APIs diseñadas para consulta automatizada, no páginas que se raspen.

## 3. Uso responsable de las APIs

- **Overpass:** el servidor público pide no exceder unas 10,000 consultas y 1 GB diarios, y dividir esas cifras entre 100 si el uso es regular. El extractor hace una ejecución semanal de unas 12 consultas (una de tiendas y una por cada uno de los 10 municipios), con pausas entre consultas y reintentos espaciados. Se identifica con un User-Agent que nombra el proyecto académico.
- **INEGI y Banxico:** una ejecución semanal, pidiendo solo las series necesarias, con pausas y reintentos espaciados.
- **Tokens:** se guardan como secretos del repositorio en GitHub Actions y nunca se escriben en el código ni en los registros. Los scripts de sondeo piden el token por teclado.

## 4. Licencias y atribución

- **INEGI y Banxico:** se cita la fuente en la documentación y no se altera el contenido original. La capa Bronce conserva las respuestas crudas con sus metadatos.
- **OpenStreetMap:** los datos están bajo ODbL. El mapa del proyecto (`docs/E2/mapa_tiendas_colima.png`) lleva la atribución "© OpenStreetMap contributors". Las tablas derivadas (`tiendas_oro.csv`, `tiendas_por_municipio.csv` y `municipios_colima.geojson`) son bases de datos derivadas; si el repositorio se hace público o se distribuyen, deben publicarse bajo ODbL con atribución y un enlace a https://www.openstreetmap.org/copyright. Mientras el repositorio sea privado, el uso es interno.
- **Código del proyecto:** autoría propia, con fines académicos.

## 5. Privacidad y minimización de datos

- **Datos personales:** el observatorio no recolecta datos de personas físicas ni de clientes. Las fuentes son estadísticas agregadas (INPC y tipo de cambio) y ubicaciones de comercios.
- **Minimización en OpenStreetMap:** de cada tienda solo se conservan identificador de OpenStreetMap, tipo de tienda, marca y coordenadas. Se descartan desde la ingesta (antes de escribir en Bronce) el nombre, el sitio web, el teléfono, el correo, la dirección, el horario y el resto de las etiquetas. La razón: en una tienda pequeña el nombre puede ser el de una persona, y la dirección puede coincidir con un domicilio. El archivo de Bronce documenta qué campos se conservaron y cuáles se descartaron.
- **Coordenadas:** corresponden a establecimientos comerciales. Si el repositorio se hiciera público, se publicarían los resultados agregados por municipio y se reduciría la precisión de las coordenadas individuales.
- **Entrevista:** Aceptó que su nombre aparezca en el repositorio.
- **Seguridad:** ninguna credencial está en el repositorio. Los tokens que se pegaron durante el desarrollo se regeneran al terminar la etapa.

## 6. Fuente evaluada y descartada: DENUE (API)

Se intentó integrar la API del DENUE del INEGI, que es la fuente oficial de establecimientos. La API respondió "No hay resultados" incluso para el ejemplo de su propia documentación, tanto desde Python como desde el navegador, y devolvió errores internos en otras consultas. Los scripts de diagnóstico están en `src/sondeos/`. Se sustituyó por OpenStreetMap, otra fuente geoespacial aceptada. Si la API se restablece, su método `Cuantificar` (conteos oficiales por municipio, sin datos de contacto) servirá para medir qué tan completa es la cobertura de OpenStreetMap.

## 7. Sesgos identificados y mitigación

| Sesgo                                | Evidencia en los datos                                                                                                                                                                                                                                             | Mitigación                                                                                                                                                                                                           |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cobertura desigual en OpenStreetMap  | De 209 tiendas, Manzanillo concentra 93 (44.5%); Colima tiene 41, Villa de Álvarez 33, Comala 17, Tecomán 14, Armería 7, Coquimatlán 2, Minatitlán 1 y Cuauhtémoc 1; Ixtlahuacán tiene 0. Es muy improbable que refleje la distribución real de comercios. | Los conteos se presentan como "tiendas registradas en OpenStreetMap", no como oferta real; el mapa lleva una nota de subestimación; no se usan para comparar municipios ni para decisiones de política o inversión |
| Sesgo hacia cadenas comerciales      | 35.4% de las tiendas tiene marca. Las tiendas de abarrotes independientes, que son el cliente del observatorio, están probablemente subrepresentadas                                                                                                              | Se reporta el porcentaje con marca por municipio; se declara la limitación en el mapa y en la relatoría                                                                                                             |
| Sesgo urbano y de mapeo voluntario   | La cobertura depende de quién edita OpenStreetMap y dónde; los municipios rurales casi no tienen registros                                                                                                                                                       | Se documenta; la comparación con el conteo oficial del DENUE queda pendiente de que la API funcione                                                                                                                  |
| Cobertura geográfica de los precios | El INPC usado es nacional: no se encontró una serie de INPC de Colima en el BIE                                                                                                                                                                                   | Colima se mantiene como región de estudio y de validación con el cliente; la limitación se declara en la propuesta                                                                                                 |
| Ventana temporal de Banxico          | Las series de Banxico inician en 2020 por configuración propia de la descarga, no por falta de datos en la fuente                                                                                                                                                 | Los 612 meses anteriores no se imputan y se documenta como ausencia estructural (ver `docs/E1/diagnostico_faltantes.md`)                                                                                            |
| Tratamiento de atípicos             | El INPC tiene 86 meses atípicos (72 en los años 80) y el tipo de cambio 3                                                                                                                                                                                        | Se interpretan como eventos económicos reales; se acotan solo para el modelado y el valor original se conserva                                                                                                       |

## 8. Limitaciones del uso de los datos

- Las conclusiones sobre la distribución de tiendas no deben generalizarse más allá de lo registrado en OpenStreetMap.
- El proyecto es académico: no es una fuente oficial ni reemplaza las cifras publicadas por el INEGI o Banxico.
- Los pronósticos de precios son orientativos y no constituyen asesoría financiera.
