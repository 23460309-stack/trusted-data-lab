# Propuesta del Observatorio: Precios de Alimentos en Colima

**Autor:** Kevin Gilberto Borjas Avalos
**Materia:** Ingeniería de Datos, Proyecto Integrador Trusted Data Lab (E0)

## 1. Ficha del observatorio

| Campo               | Descripción                                                                                                                                 |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Sector              | Comercio y precios al consumidor (alimentos, bebidas y tabaco)                                                                               |
| Región             | Colima, México                                                                                                                              |
| Pregunta detonadora | ¿Cuánto cambiarán los precios de los alimentos en Colima en los próximos meses y qué factores los explican?                             |
| Cliente potencial   | Pequeños comercios locales (tiendas de abarrotes, fondas, restaurantes) que necesitan anticipar costos para fijar precios y planear compras |


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

1. **Variable a pronosticar (E1):** ¿Cuál será el índice de precios (INPC) de alimentos, bebidas y tabaco en Colima en los próximos 6 meses?
2. **Factores a experimentar (E2):** ¿Afectan la temporada del año (trimestre) y la categoría de producto (por ejemplo frutas y verduras frente a carnes) a la variación mensual de precios?
3. **Grupos multivariados a comparar (E3):** ¿Se comportan distinto las ciudades del occidente (Colima, Guadalajara, Tepic) considerando varias categorías de precios a la vez?

## 4. Plan de recopilación de datos

[COMPLETAR en el Paso 2: al menos 2 fuentes con análisis ético y legal (robots.txt y términos de uso)]
