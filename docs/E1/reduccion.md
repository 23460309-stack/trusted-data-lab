# Reducción de datos (E1)

## 1. Técnicas aplicadas

- **Selección de variables** por redundancia (correlación absoluta >= 0.95).
- **Agregación temporal:** mensual -> trimestral y anual.
- **Muestreo: no aplicado.** La serie tiene 694 observaciones mensuales y su orden temporal es esencial para el pronóstico; una muestra aleatoria destruiría la dependencia temporal.

## 2. Selección de variables

Matriz de correlación entre las variables candidatas (con los meses disponibles en cada par):

```text
                  inpc_inegi  inpc_banxico  tc_fix_prom  tc_fix_cierre  tc_fix_prom_suav  var_inpc_pct_w  var_tc_pct_w
inpc_inegi             1.000         1.000       -0.691         -0.686            -0.733          -0.582         0.082
inpc_banxico           1.000         1.000       -0.691         -0.686            -0.733          -0.142         0.082
tc_fix_prom           -0.691        -0.691        1.000          0.979             0.952           0.047         0.082
tc_fix_cierre         -0.686        -0.686        0.979          1.000             0.918           0.061         0.133
tc_fix_prom_suav      -0.733        -0.733        0.952          0.918             1.000           0.130        -0.165
var_inpc_pct_w        -0.582        -0.142        0.047          0.061             0.130           1.000        -0.027
var_tc_pct_w           0.082         0.082        0.082          0.133            -0.165          -0.027         1.000
```

Prioridad de conservación: fuente primaria (INEGI) sobre la secundaria (Banxico), y la variable original sobre sus derivadas.

- Variables conservadas: inpc_inegi, tc_fix_prom, var_inpc_pct_w, var_tc_pct_w
- Variables descartadas por redundancia:

```text
        variable redundante_con  correlacion
    inpc_banxico     inpc_inegi       1.0000
   tc_fix_cierre    tc_fix_prom       0.9787
tc_fix_prom_suav    tc_fix_prom       0.9515
```

Limitación: la correlación entre niveles de series con tendencia puede ser espuria; aquí solo se usa para detectar redundancia, no para explicar relaciones.

## 3. Agregación

- `datos/oro/tabla_trimestral.csv`: cierre y promedio del INPC, variación trimestral y promedio del tipo de cambio. Se marcan los trimestres incompletos.
- `datos/oro/tabla_anual.csv`: cierre del INPC, inflación anual y promedio del tipo de cambio. Se marcan los años incompletos (2026 llega solo a octubre).

## 4. Magnitud de la reducción

```text
                             tabla  filas  columnas
     tabla_oro (mensual, completa)    694        36
tabla_modelado (mensual, reducida)    694         7
                  tabla_trimestral    232         6
                       tabla_anual     58         5
```
