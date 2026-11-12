# Atípicos y ruido (E1)

## 1. Método

Se analizan las **variaciones mensuales (%)**, no los niveles, porque el INPC crece con el tiempo y en niveles marcaría todo lo reciente como atípico.

- **IQR:** atípico si queda fuera de [Q1 - 1.5*IQR, Q3 + 1.5*IQR].
- **Z-Score robusto:** 0.6745*(x - mediana)/MAD; atípico si |Z| > 3.5.
- **Regla:** un mes es atípico solo si lo marcan **ambos** métodos.

## 2. Resultados

```text
    variable  observaciones  limite_inf_iqr  limite_sup_iqr  atipicos_iqr  atipicos_zrobusto  atipicos_ambos
var_inpc_pct            693          -1.323           3.217            86                 94              86
  var_tc_pct             81          -5.515           4.058             6                  3               3
```

Atípicos del INPC por década:

```text
mes
1970     6
1980    72
1990     8
```

Meses con mayor |Z|:

### Variación mensual del INPC (%)

```text
            var_inpc_pct  var_inpc_pct_z
mes                                     
1988-01-01     15.462379       23.000652
1987-12-01     14.769817       21.921936
1982-08-01     11.221803       16.395637
1983-01-01     10.881015       15.864835
1982-12-01     10.678709       15.549728
1986-01-01      8.840996       12.687352
1987-04-01      8.749507       12.544851
1988-02-01      8.340750       11.908181
```

### Variación mensual del tipo de cambio FIX (%)

```text
            var_tc_pct  var_tc_pct_z
mes                                 
2020-03-01   18.754079      8.627232
2024-06-01    8.478286      3.992913
2020-04-01    8.434204      3.973032
```

## 3. Tratamiento

- Los registros ya pasaron la Puerta de Calidad y son datos oficiales válidos, así que los atípicos se interpretan como **eventos económicos reales**, no como errores de captura. No se eliminan.
- Se agrega, por cada variable, `_atipico` (bandera), `_z` (Z-Score robusto) y `_w` (valor winsorizado, acotado a los límites del IQR). El valor original se conserva.
- Para el modelado se podrá elegir entre la versión original y la winsorizada.

## 4. Ruido

Se agrega `tc_fix_prom_suav`, media móvil de 3 meses del tipo de cambio mensual, para reducir fluctuación de corto plazo. La serie original se conserva.

## 5. Evidencia

Gráfica con los atípicos marcados: `docs/E1/atipicos.png`.
