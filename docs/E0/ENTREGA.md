
# Ficha de entrega técnica: E0

**Proyecto:** Trusted Data Lab, Observatorio de precios al consumidor
**Autor:** Kevin Gilberto Borjas Avalos (equipo de 1 integrante)
**Repositorio:** https://github.com/23460309-stack/trusted-data-lab
**Tag:** `e0`

## 1. Resumen de lo entregado

| # | Entregable                        | Ubicación                                                                                      | Estado         |
| - | --------------------------------- | ----------------------------------------------------------------------------------------------- | -------------- |
| 1 | Propuesta del Observatorio        | `docs/E0/propuesta.md`                                                                        | Completo       |
| 2 | Máquina de captura (capa Bronce) | `src/extractor.py`, `src/series.json`, `.github/workflows/captura.yml`, `datos/bronce/` | Completo       |
| 3 | Sistema de Calidad inicial (PSP)  | `calidad/tiempo-kevin.csv`, `calidad/defectos-kevin.csv`, `calidad/objetivos-calidad.md`  | Completo       |
| 4 | Ficha de entrega técnica         | `docs/E0/ENTREGA.md`                                                                          | Este documento |

## 2. Fuentes de datos

| Fuente                          | Serie                                     | Frecuencia | Observaciones en la captura inicial |
| ------------------------------- | ----------------------------------------- | ---------- | ----------------------------------- |
| INEGI, API de Indicadores (BIE) | INPC índice general nacional (ID 910392) | Mensual    | 693                                 |
| Banxico, API del SIE            | Tipo de cambio FIX (SF43718)              | Diaria     | 1724                                |
| Banxico, API del SIE            | INPC nacional (SP1)                       | Mensual    | 81                                  |

Todas superan el mínimo de 36 periodos.

## 3. Cómo verificar cada entregable

**Captura automática**

- Workflow: pestaña **Actions → Captura Bronce**. Se ejecuta cada lunes a las 14:00 UTC y también de forma manual. La ejecución #1 terminó en éxito.
- Datos crudos en `datos/bronce/inegi/` y `datos/bronce/banxico/`.
- Registro de cada captura en `datos/bronce/manifiesto.csv` (fuente, serie, observaciones, archivo y estado).

**Calidad**

- Registro de tiempo por fase: `calidad/tiempo-kevin.csv`.
- Registro de defectos con tiempo de corrección: `calidad/defectos-kevin.csv`.
- Tres objetivos medibles con su forma de verificación: `calidad/objetivos-calidad.md`.

**Ejecución local (opcional)**

```powershell
pip install -r requirements.txt
$env:INEGI_TOKEN="<token>"
$env:BANXICO_TOKEN="<token>"
python src/extractor.py
```

Los tokens se guardan como secretos del repositorio (`INEGI_TOKEN` y `BANXICO_TOKEN`) y no aparecen en el código.

## 4. Decisiones y limitaciones

- No se encontró en el BIE una serie de INPC específica de Colima, por lo que los datos de precios son nacionales. Colima se mantiene como región de estudio y de validación con el cliente.
- El INPC de Banxico replica el índice calculado por el INEGI; el tipo de cambio aporta la variable explicativa distinta. En las siguientes etapas se agregarán series de componentes del INPC para la comparación multivariada (E3).
- El análisis ético y legal de las fuentes (robots.txt y términos de uso) está en la sección 4.2 de la propuesta.

## 5. Lista de verificación de entrega

- [ ] Los 3 docentes agregados como colaboradores del repositorio
- [X] Tag `e0` creado y subido a GitHub
- [X] Enlace registrado en el formulario oficial del proyecto integrador
- [X] Enlace pegado en la tarea
