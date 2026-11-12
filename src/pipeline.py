"""Pipeline completo Bronce -> Plata -> Oro en un solo comando.

Uso:  python src/pipeline.py
Requiere la capa Bronce ya descargada (python src/extractor.py).
Se detiene en el primer paso que falle y verifica las salidas esperadas.
"""
import os
import subprocess
import sys
import time

import pandas as pd

from config import CUARENTENA, ORO, PLATA, RAIZ

PASOS = [
    ("Integración y conciliación de fuentes", "integrar.py"),
    ("Puerta de Calidad (Plata y cuarentena)", "puerta_calidad.py"),
    ("Valores faltantes", "faltantes.py"),
    ("Atípicos y ruido", "atipicos.py"),
    ("Normalización (inicio de Oro)", "normalizar.py"),
    ("Discretización y jerarquías", "discretizar.py"),
    ("Reducción de datos", "reducir.py"),
]

SALIDAS = [
    PLATA / "series_validas.csv",
    PLATA / "tabla_mensual.csv",
    PLATA / "tabla_limpia.csv",
    ORO / "tabla_oro.csv",
    ORO / "parametros_escalado.csv",
    ORO / "tabla_modelado.csv",
    ORO / "tabla_trimestral.csv",
    ORO / "tabla_anual.csv",
]


def ejecutar(nombre, script):
    inicio = time.time()
    entorno = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(
        [sys.executable, str(RAIZ / "src" / script)],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace", env=entorno,
    )
    if r.returncode != 0:
        print(f"[FALLO] {nombre} ({script})")
        print(r.stdout[-2000:])
        print(r.stderr[-3000:])
        sys.exit(1)
    print(f"[OK] {nombre} ({time.time() - inicio:.1f} s)")


def main():
    print("=== Pipeline Bronce -> Plata -> Oro ===")
    for nombre, script in PASOS:
        ejecutar(nombre, script)

    faltan = [s.relative_to(RAIZ).as_posix() for s in SALIDAS if not s.exists() or s.stat().st_size == 0]
    if faltan:
        print(f"[FALLO] Salidas faltantes o vacías: {faltan}")
        sys.exit(1)

    bitacora = pd.read_csv(CUARENTENA / "bitacora_puerta.csv").iloc[-1]
    oro = pd.read_csv(ORO / "tabla_oro.csv")
    print("\n=== Resumen ===")
    print(
        f"Puerta de Calidad: entrada {bitacora['registros_entrada']} | "
        f"válidos {bitacora['registros_validos']} | cuarentena {bitacora['registros_cuarentena']}"
    )
    print(f"Capa Oro: tabla_oro {oro.shape[0]} filas x {oro.shape[1]} columnas")
    print(f"Último mes con dato: {oro['mes'].iloc[-1]}")
    print("Pipeline completado.")


if __name__ == "__main__":
    main()