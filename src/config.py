"""Rutas del proyecto."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SERIES_JSON = RAIZ / "src" / "series.json"
BRONCE = RAIZ / "datos" / "bronce"
PLATA = RAIZ / "datos" / "plata"
ORO = RAIZ / "datos" / "oro"
CUARENTENA = RAIZ / "datos" / "cuarentena"