# Propuesta del Observatorio: Precios de Alimentos en Colima

**Autor:** Kevin Gilberto Borjas Avalos
**Materia:** Ingeniería de Datos, Proyecto Integrador Trusted Data Lab (E0)

## 1. Ficha del observatorio

| Campo               | Descripción                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Sector              | Comercio y precios al consumidor (alimentos, bebidas y tabaco)                                                                                         |
| Región             | Colima, México                                                                                                                                        |
| Pregunta detonadora | ¿Cuánto cambiarán los precios al consumidor en los próximos meses y qué factores los explican, para que un comercio de Colima planee sus compras? |
| Cliente potencial   | Pequeños comercios locales (tiendas de abarrotes, fondas, restaurantes) que necesitan anticipar costos para fijar precios y planear compras           |

## 2. Entrevista de campo

**Entrevistado:** José Manuel Ramírez Torres, dueño de Abarrotes "Santa Anita"
**Ubicación:** Villa de Álvarez, Colima, México (negocio con 12 años de antigüedad)
**Fecha y duración:**  fecha 6/11/2026 y duración 15 min

| # | Pregunta                                                                     | Respuesta                                                                                                                                                                                                                                                                                                       |
| - | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | ¿Cada cuánto cambian los precios de sus proveedores y cómo se entera?     | Depende del proveedor: algunos cambian sus precios cada mes y otros cada semana. Se entera cuando el vendedor viene a surtir, cuando le mandan listas de precios por WhatsApp o al comprar directamente en las bodegas.                                                                                         |
| 2 | ¿Qué productos son los que más suben o más le afectan?                   | Aceite, huevo, azúcar, leche, arroz y frijol. Son de mucha venta, y cuando suben tiene que invertir más dinero para comprar la misma cantidad. El huevo y el aceite son los que más cambian.                                                                                                                 |
| 3 | ¿Cómo decide cuándo subir sus precios a los clientes?                     | Revisa cuánto le costó el producto nuevo y cuánto está ganando. Si el aumento del proveedor es pequeño, mantiene el precio para no afectar a sus clientes; si es considerable, sube un poco para no perder dinero. También compara con los precios de otras tiendas cercanas para mantenerse competitivo. |
| 4 | ¿Qué información le ayudaría a planear sus compras con anticipación?    | Saber qué productos subirán de precio próximamente, cuánto podrían aumentar y en qué fechas. También saber cuáles tienen mayor probabilidad de escasear para comprar más antes de que suban de costo.                                                                                                  |
| 5 | ¿Usaría un tablero con el pronóstico de precios? ¿Qué le gustaría ver? | Sí, siempre que sea fácil de entender y rápido de consultar. Le gustaría ver los productos que maneja con su precio actual, cómo han cambiado en los últimos meses y cuánto podrían costar en las siguientes semanas, además de alertas cuando un producto esté por subir.                            |

**Aprendizajes:**

- Los precios cambian con frecuencias distintas (semanal o mensual según el proveedor), y el comerciante se entera de forma informal (visitas de vendedores y WhatsApp), sin una fuente de información sistemática.
- Seis productos concentran su preocupación: aceite, huevo, azúcar, leche, arroz y frijol. Son los candidatos naturales para dar seguimiento en el observatorio.
- Su decisión de precios combina el costo del proveedor, su margen y la competencia local; evita trasladar aumentos pequeños para no perder clientes.
- Su necesidad principal es anticiparse: saber qué subirá, cuánto y cuándo, para comprar antes del aumento.
- Quiere un tablero simple, con histórico reciente, pronóstico de pocas semanas y alertas. Esto valida el problema y orienta el diseño de la capa Oro.

## 3. Las 3 preguntas analíticas

1. **Variable a pronosticar (E1):** ¿Cuál será el índice general de precios al consumidor (INPC) de México en los próximos 6 meses?
3. **Factores a experimentar (E2):** ¿Afectan el tipo de cambio y la temporada del año (trimestre) a la variación mensual del INPC?
4. **Grupos multivariados a comparar (E3):** ¿Se comportan de forma distinta los componentes del INPC (subyacente, no subyacente y rubros de alimentos) considerando varios indicadores a la vez? Las series de componentes se agregarán a la capa Bronce en la siguiente etapa.

## 4. Plan de recopilación de datos

### 4.1 Fuentes seleccionadas

|                    | Fuente 1                                                          | Fuente 2                                                   |
| ------------------ | ----------------------------------------------------------------- | ---------------------------------------------------------- |
| Institución       | INEGI                                                             | Banco de México (Banxico)                                 |
| Producto           | API de Indicadores (BIE/BISE)                                     | API del Sistema de Información Económica (SIE)           |
| Tipo de acceso     | API REST con token gratuito, respuesta en JSON                    | API REST con token gratuito, respuesta en JSON             |
| Datos              | INPC indice general nacional, mensual (ID 910392, banco BIE-BISE) | Variables explicativas: tipo de cambio FIX e INPC nacional |
| Frecuencia         | Mensual                                                           | Diaria (tipo de cambio) y mensual (INPC)                   |
| Historial          | Más de 36 meses disponibles                                      | Más de 36 meses disponibles                               |
| Rol en el proyecto | Variable a pronosticar (E1)                                       | Factores a experimentar (E2)                               |

**Nota sobre la cobertura geográfica:** no se encontró en el BIE una serie de INPC específica de Colima, por lo que los datos de precios son nacionales. Colima se mantiene como región de estudio y de validación con el cliente (entrevista a un comercio de Villa de Álvarez); el pronóstico nacional sirve como referencia para sus decisiones de compra.

### 4.2 Análisis ético y legal

**INEGI**

- **robots.txt:** no hay restricciones.
- **Términos de uso:** los Términos de Libre Uso del INEGI permiten copiar, distribuir, difundir y adaptar la información sin alterar ni suprimir sus metadatos. Condiciones: citar la fuente ("Fuente: INEGI, nombre del producto") con la fecha de actualización cuando sea posible, no aparentar que el proyecto es avalado u oficial del INEGI y no usar los datos para engañar o cambiar su sentido original.
- **Cumplimiento:** el observatorio mostrará la fuente en cada gráfica y tabla; la capa Bronce conserva los datos crudos con sus metadatos sin modificar.

**Banxico**

- **robots.txt:** no hay restricciones.
- **Términos de uso:** el SIE exige un token de consulta y pide citar claramente a Banco de México como fuente, con la dirección web de origen para que terceros verifiquen la información. La API establece límites de consultas.
- **Cumplimiento:** se citará "Fuente: Banco de México, Sistema de Información Económica (SIE)" con su URL, y se respetarán los límites de consultas.

**Buenas prácticas del extractor (aplican a ambas fuentes)**

- Solo se consumen las APIs oficiales; no se hace scraping de páginas.
- Frecuencia baja: una ejecución programada por semana, pidiendo solo las series necesarias, con reintentos espaciados.
- Los tokens se guardan como secretos de GitHub Actions (INEGI_TOKEN y BANXICO_TOKEN) y nunca se escriben en el código ni en los registros.
- Se envía un User-Agent que identifica el proyecto académico.
- No se recopilan datos personales; los datos son estadísticas agregadas.
- Revisión de términos y robots.txt realizada el: 06/11/2026

### 4.3 Estrategia de captura (capa Bronce)

- Un script en `src/` descargará las series completas de cada fuente y guardará la respuesta cruda (JSON) en `datos/bronce/`, con la fecha de captura en el nombre del archivo.
- GitHub Actions ejecutará el script de forma programada y hará commit de los datos nuevos.
- Meta de E0: serie histórica inicial con al menos 36 periodos mensuales por fuente.
