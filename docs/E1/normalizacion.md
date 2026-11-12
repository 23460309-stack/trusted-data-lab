# Normalización y estandarización (E1)

## 1. Método

- **Min-Max:** x' = (x - min) / (max - min). Lleva la variable al rango [0, 1].
- **Z-Score:** z = (x - media) / desviación estándar (poblacional). Centra en 0 con desviación 1.
- Se aplican a `inpc_inegi`, `tc_fix_prom` y a las variaciones mensuales winsorizadas (`var_inpc_pct_w`, `var_tc_pct_w`), que tienen unidades y escalas distintas.
- Los valores originales se conservan; las versiones escaladas se agregan con los sufijos `_minmax` y `_zscore`.
- Los nulos permanecen como nulos (no se imputan al escalar).

## 2. Parámetros

```text
                    min       max    media  desv_std  observaciones
columna                                                            
inpc_inegi       0.0116  147.0260  44.2010   44.8420            694
tc_fix_prom     16.7918   24.2658  19.2819    1.6486             82
var_inpc_pct_w  -1.0137    3.2173   1.0835    1.0435            693
var_tc_pct_w    -4.7990    6.7768  -0.2649    2.2260             81
```

Se guardan en `datos/oro/parametros_escalado.csv` para poder revertir la transformación (por ejemplo, al devolver pronósticos a la escala original).

## 3. Verificación

```text
       columna  minmax_min  minmax_max  z_media  z_desv
    inpc_inegi         0.0         1.0     -0.0     1.0
   tc_fix_prom         0.0         1.0     -0.0     1.0
var_inpc_pct_w         0.0         1.0      0.0     1.0
  var_tc_pct_w         0.0         1.0      0.0     1.0
```

- Min-Max: mínimo 0 y máximo 1 en cada columna.
- Z-Score: media cercana a 0 y desviación cercana a 1.
- Los resultados se compararon con `MinMaxScaler` y `StandardScaler` de scikit-learn.

## 4. Limitación

Los parámetros se calcularon con toda la muestra, lo cual es adecuado para describir los datos. Para el modelo de pronóstico se calcularán únicamente con el periodo de entrenamiento, para evitar filtrar información del futuro.
