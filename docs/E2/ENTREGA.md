
# Ficha de entrega técnica: E2

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos (equipo de 1 integrante)
**Repositorio:** https://github.com/23460309-stack/trusted-data-lab
**Tag:** `e2`

## 1. Resumen de lo entregado

| # | Entregable de E2                                                                                          | Implementación                                                    | Documentación                                          |
| - | --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------- |
| 1 | Fuente especializada integrada: geoespacial (OpenStreetMap, con GeoPandas y visualización cartográfica) | `src/extractor_osm.py`, `src/plata_osm.py`, `src/oro_osm.py` | `docs/E2/mapa_tiendas_colima.png`                     |
| 2 | Declaración de ética y legalidad                                                                        | Este repositorio                                                   | `docs/etica-datos.md`                                 |
| 3 | Linaje y trazabilidad de datos                                                                            | `src/linaje.py`                                                  | `docs/E2/linaje.md`, `datos/oro/linaje_mensual.csv` |
| 4 | Ficha de entrega y relatoría                                                                             | Este documento                                                     | `docs/relatoria-E2.md`                                |

## 2. Fuente integrada

- **Fuente:** OpenStreetMap, consultada con la API pública Overpass. No requiere token. Licencia ODbL con atribución "© OpenStreetMap contributors".
- **Datos:** tiendas (`shop` = convenience, supermarket o general) y límites de los 10 municipios de Colima.
- **Minimización de datos:** de cada tienda solo se conservan identificador de OpenStreetMap, tipo de tienda, marca y coordenadas. Nombre, sitio web, teléfono, correo, dirección y horario se descartan desde la ingesta. No hay datos personales.
- **Fuente evaluada y descartada:** la API del DENUE del INEGI, que no devolvió resultados ni para el ejemplo de su documentación (ver `docs/etica-datos.md`, sección 6). Los scripts de diagnóstico están en `src/sondeos/`.

## 3. Flujo de datos

- **Bronce:** `datos/bronce/osm/` guarda las respuestas ya reducidas (tiendas) y las geometrías municipales, con fecha de ingesta, licencia y campos conservados y descartados. Cada captura se registra en `datos/bronce/manifiesto.csv`.
- **Plata:** `src/plata_osm.py` valida cada tienda con Pandera (tipo, categoría, coordenadas en un rango razonable y sin duplicados), arma los polígonos municipales y asigna cada tienda a su municipio con un cruce espacial. Lo inválido va a `datos/cuarentena/` con su motivo.
- **Oro:** `src/oro_osm.py` genera `tiendas_oro.csv` (209 tiendas con linaje), `tiendas_por_municipio.csv` y el mapa.
- **Orquestación:** `src/pipeline.py` ejecuta 10 etapas (7 de E1 y 3 de E2). El flujo `.github/workflows/captura.yml` descarga las fuentes cada lunes y corre el pipeline. El paso de OpenStreetMap usa `continue-on-error`: si Overpass está saturado, el pipeline continúa con los últimos datos de OpenStreetMap guardados en el repositorio.

## 4. Resultados principales

| Elemento                    | Resultado                                                                                                                                                                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Tiendas extraídas          | 209 (133 de conveniencia, 38 supermercados y 38 tiendas generales)                                                                                                                   |
| Puerta de Calidad (tiendas) | 209 de entrada: 209 válidas y 0 en cuarentena                                                                                                                                       |
| Municipios                  | 10 de 10, con 5,752.5 km² en total                                                                                                                                                  |
| Distribución               | Manzanillo 93 (44.5%), Colima 41, Villa de Álvarez 33, Comala 17, Tecomán 14, Armería 7, Coquimatlán 2, Minatitlán 1, Cuauhtémoc 1 e Ixtlahuacán 0                            |
| Mayor densidad              | Villa de Álvarez, con 11.52 tiendas por cada 100 km²                                                                                                                               |
| Tiendas con marca           | 35.4%                                                                                                                                                                                |
| Linaje                      | Todas las filas de las tablas de Oro tienen archivo de Bronce y fecha de ingesta; 858 filas en `linaje_mensual.csv`; los conteos por municipio coinciden con las tiendas de origen |

## 5. Cómo verificar

- **Mapa:** `docs/E2/mapa_tiendas_colima.png`.
- **Linaje:** `docs/E2/linaje.md` explica el modelo y trae un ejemplo de trazado.
- **Pipeline completo:** `python src/pipeline.py`; debe terminar con `Pipeline completado.`
- **Flujo automático:** pestaña Actions, flujo Pipeline Bronce, Plata y Oro (la ejecución #5 terminó con éxito).

## 6. Decisiones y limitaciones

- OpenStreetMap lo editan voluntarios: la cobertura es muy desigual y probablemente subestima las tiendas de barrio. Los conteos son de tiendas registradas, no de la oferta real, y no sirven para comparar municipios ni para decisiones de política.
- El porcentaje de tiendas con marca (35.4%) sugiere sesgo hacia cadenas comerciales.
- No se calculan tiendas por habitante porque no se cargaron datos de población.
- Si el DENUE vuelve a responder, su método de conteo oficial servirá para medir qué tan completa es la cobertura de OpenStreetMap.
- Si el extractor corre dos veces el mismo día, el archivo de Bronce de ese día se reemplaza.

## 7. Lista de verificación de entrega

- [ ] Declaración de ética sin campos pendientes
- [ ] Tag `e2` creado y subido a GitHub
- [ ] Enlace registrado en el formulario oficial del proyecto integrador
