# Valores faltantes: diagnóstico e imputación (E1)

## 1. Diagnóstico

```text
      columna  faltantes  pct primer_dato  faltantes_antes_del_primer_dato  huecos_internos p_mannwhitney_inpc
 inpc_banxico        612 88.2     2020-01                              612                0           5.00e-49
  tc_fix_prom        612 88.2     2020-01                              612                0           5.00e-49
tc_fix_cierre        612 88.2     2020-01                              612                0           5.00e-49
```

- `p_mannwhitney_inpc`: prueba de Mann-Whitney sobre el INPC (variable observada) entre meses con y sin dato. Un p-valor muy pequeño indica que la ausencia se relaciona con una variable observada, lo que descarta MCAR.
- Limitación: la prueba de Little para MCAR no está disponible en las librerías usadas, por lo que el argumento combina la prueba anterior con la causa documentada.

## 2. Mecanismo

Todos los faltantes son anteriores al primer dato de cada serie (no hay huecos internos): son faltantes por diseño. Su causa es la ventana de descarga (`inicio` en `src/series.json`), decidida sin mirar los valores. Dependen solo del tiempo, que es una variable observada, así que no son MCAR en sentido estricto y se clasifican como MAR (estructural). MNAR no se puede descartar con los datos, pero no hay evidencia a favor: la causa documentada es independiente de los valores faltantes.

## 3. Justificación del método de imputación

Se ocultó al azar el 10% de los meses de `tc_fix_prom` (200 repeticiones, semilla 42) y se reconstruyeron con tres métodos.

```text
interpolacion_lineal    0.349426
ultimo_valor            0.552999
media_global            1.593583
```

Método elegido: **interpolacion_lineal** (menor RMSE medio).

## 4. Decisión aplicada

- Huecos internos de hasta 2 meses consecutivos: se imputan con interpolacion_lineal y se marcan en las columnas `<columna>_imputado`. Valores imputados en esta corrida: **0**.
- Meses anteriores al primer dato: **no se imputan**. Rellenar décadas de tipo de cambio con valores estimados sería inventar información; se mantienen como nulos y se documentan como ausencia estructural.
- Alternativa pendiente: ampliar la ventana de descarga de Banxico hacia atrás para reducir estos faltantes.
