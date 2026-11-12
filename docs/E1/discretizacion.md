# Discretización y jerarquías conceptuales (E1)

## 1. Discretización

| Variable origen | Método | Categorías |
|---|---|---|
| `var_inpc_pct` (variación mensual del INPC, %) | Criterio del analista | deflacion (<= 0), baja (0 a 0.5], moderada (0.5 a 1], alta (1 a 3], muy_alta (> 3) |
| `tc_fix_prom` (nivel del tipo de cambio) | Ancho igual, 3 rangos | bajo, medio, alto |
| `tc_fix_prom` | Frecuencia igual, 3 grupos | bajo, medio, alto |
| `var_tc_pct_w` (variación mensual del tipo de cambio, winsorizada) | Frecuencia igual, 4 cuartiles | q1_menor, q2, q3, q4_mayor |

Los cortes de la inflación se definieron por criterio del analista (conocimiento del dominio) y son un parámetro que se puede ajustar en `src/discretizar.py`. Los valores originales se conservan; las categorías son columnas nuevas.

### Comparación de métodos: nivel del tipo de cambio (meses por categoría)

```text
       ancho_igual  frecuencia_igual
bajo            39                28
medio           37                27
alto             6                27
```

El ancho igual produce grupos desiguales cuando los datos se concentran en una zona del rango. La frecuencia igual reparte los meses de forma pareja, pero sus fronteras dependen de los datos.

## 2. Jerarquías conceptuales

**Temporal:** mes -> trimestre -> semestre -> año -> década (columnas `trimestre`, `semestre`, `anio`, `decada`). La columna `trimestre_num` (1 a 4) permite estudiar la temporada del año (pregunta E2).

**Inflación:** deflacion y baja -> estable; moderada -> moderada; alta y muy_alta -> alta (columna `inflacion_grupo`).

## 3. Resumen por nivel jerárquico

Meses por categoría de inflación en cada década:

```text
inflacion_cat  deflacion  baja  moderada  alta  muy_alta
decada                                                  
1960s                  1     7         2     1         0
1970s                  2    23        39    49         7
1980s                  0     0         5    40        75
1990s                  0     7        46    56        11
2000s                 12    59        45     4         0
2010s                 24    57        35     4         0
2020s                  7    42        31     2         0
```

Inflación mensual promedio (%) por década:

```text
decada
1960s    0.393
1970s    1.175
1980s    4.309
1990s    1.507
2000s    0.403
2010s    0.326
2020s    0.401
```

Inflación mensual promedio (%) por trimestre del año, desde 2010:

```text
trimestre_num
1    0.480
2   -0.008
3    0.366
4    0.597
```
