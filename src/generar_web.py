"""Genera web/data/datos.js con las tablas del proyecto y (opcional) sirve la página.

Uso:
    python src/generar_web.py            # solo genera los datos
    python src/generar_web.py --servir   # genera, abre http://localhost:8000
"""
import argparse
import csv
import json
import threading
import webbrowser
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web"

CSVS = {
    "oro": "datos/oro/tabla_oro.csv",
    "trimestral": "datos/oro/tabla_trimestral.csv",
    "anual": "datos/oro/tabla_anual.csv",
    "tiendas": "datos/oro/tiendas_oro.csv",
    "tiendas_municipio": "datos/oro/tiendas_por_municipio.csv",
    "linaje": "datos/oro/linaje_mensual.csv",
    "puerta": "datos/cuarentena/bitacora_puerta.csv",
    "puerta_osm": "datos/cuarentena/bitacora_puerta_osm.csv",
    "manifiesto": "datos/bronce/manifiesto.csv",
}


def leer_csv(ruta: Path):
    if not ruta.exists():
        print(f"  [aviso] no existe {ruta.relative_to(RAIZ)} (se omite)")
        return []
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        filas = list(csv.DictReader(f))
    # Convierte a número lo que lo sea; el resto queda como texto.
    for fila in filas:
        for k, v in fila.items():
            if v is None or v == "":
                fila[k] = None
                continue
            try:
                fila[k] = float(v) if any(c in v for c in ".eE") else int(v)
            except ValueError:
                pass
    print(f"  [ok] {ruta.relative_to(RAIZ)}: {len(filas)} filas")
    return filas


def generar():
    print("Generando datos para la página web...")
    datos = {k: leer_csv(RAIZ / r) for k, r in CSVS.items()}
    geo = RAIZ / "datos/plata/municipios_colima.geojson"
    datos["municipios_geo"] = json.loads(geo.read_text(encoding="utf-8")) if geo.exists() else None
    datos["generado_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    destino = WEB / "data" / "datos.js"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False, allow_nan=False, default=str) + ";\n",
                       encoding="utf-8")
    print(f"Listo: {destino.relative_to(RAIZ)}")


def servir(puerto: int):
    manejador = partial(SimpleHTTPRequestHandler, directory=str(WEB))
    srv = ThreadingHTTPServer(("127.0.0.1", puerto), manejador)
    url = f"http://localhost:{puerto}"
    print(f"\nPágina disponible en {url}   (Ctrl+C para detener)")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--servir", action="store_true", help="levanta el servidor local y abre el navegador")
    ap.add_argument("--puerto", type=int, default=8000)
    a = ap.parse_args()
    generar()
    if a.servir:
        servir(a.puerto)