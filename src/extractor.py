"""Extractor de la capa Bronce: descarga series del INEGI y Banxico sin transformarlas."""
import csv
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "src" / "series.json"
SALIDA = RAIZ / "datos" / "bronce"
MANIFIESTO = SALIDA / "manifiesto.csv"

INEGI_BASE = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR"
BANXICO_BASE = "https://www.banxico.org.mx/SieAPIRest/service/v1/series"
HEADERS = {
    "User-Agent": "TrustedDataLab-ITColima/1.0 (proyecto academico; github.com/23460309-stack/trusted-data-lab)"
}


def pedir(url, headers=None, intentos=3):
    """GET con reintentos. No imprime la URL porque la del INEGI lleva el token."""
    for n in range(1, intentos + 1):
        try:
            r = requests.get(url, headers={**HEADERS, **(headers or {})}, timeout=60)
            if r.status_code == 200:
                return r.json()
            print(f"    HTTP {r.status_code} (intento {n}/{intentos})")
        except (requests.RequestException, ValueError) as e:
            print(f"    Error {type(e).__name__} (intento {n}/{intentos})")
        time.sleep(5 * n)
    return None


def extraer_inegi(serie, token):
    url = (
        f"{INEGI_BASE}/{serie['id']}/es/{serie.get('area', '00')}/false/"
        f"{serie.get('banco', 'BIE')}/2.0/{token}?type=json"
    )
    return pedir(url)


def extraer_banxico(serie, token):
    """Pide la serie por años para no exceder los límites de la API y las une."""
    hoy = date.today()
    anio_ini = int(serie["inicio"][:4])
    datos, titulo = [], None
    for anio in range(anio_ini, hoy.year + 1):
        ini = serie["inicio"] if anio == anio_ini else f"{anio}-01-01"
        fin = hoy.isoformat() if anio == hoy.year else f"{anio}-12-31"
        crudo = pedir(f"{BANXICO_BASE}/{serie['id']}/datos/{ini}/{fin}", {"Bmx-Token": token})
        if crudo is None:
            return None
        s = crudo["bmx"]["series"][0]
        titulo = s.get("titulo", titulo)
        datos.extend(s.get("datos", []))
        time.sleep(1)
    return {"bmx": {"series": [{"idSerie": serie["id"], "titulo": titulo, "datos": datos}]}}


def contar(fuente, crudo):
    try:
        if fuente == "inegi":
            return len(crudo["Series"][0]["OBSERVATIONS"])
        return len(crudo["bmx"]["series"][0]["datos"])
    except (KeyError, IndexError, TypeError):
        return 0


def registrar(fila):
    SALIDA.mkdir(parents=True, exist_ok=True)
    nuevo = not MANIFIESTO.exists()
    with open(MANIFIESTO, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha_captura_utc", "fuente", "serie", "id", "observaciones", "archivo", "estado"])
        w.writerow(fila)


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    tokens = {"inegi": os.environ.get("INEGI_TOKEN"), "banxico": os.environ.get("BANXICO_TOKEN")}
    ahora = datetime.now(timezone.utc)
    fallos = 0

    for serie in config["series"]:
        fuente, nombre = serie["fuente"], serie["nombre"]
        print(f"[{fuente}] {nombre}")

        if serie["id"].startswith("COMPLETAR"):
            print("    Falta el ID de la serie en src/series.json")
            registrar([ahora.isoformat(), fuente, nombre, serie["id"], 0, "", "sin_id"])
            fallos += 1
            continue
        if not tokens.get(fuente):
            print(f"    Falta la variable de entorno del token de {fuente}")
            registrar([ahora.isoformat(), fuente, nombre, serie["id"], 0, "", "sin_token"])
            fallos += 1
            continue

        crudo = (extraer_inegi if fuente == "inegi" else extraer_banxico)(serie, tokens[fuente])
        n = contar(fuente, crudo) if crudo else 0
        if n == 0:
            print("    No se obtuvieron observaciones")
            registrar([ahora.isoformat(), fuente, nombre, serie["id"], 0, "", "error"])
            fallos += 1
            continue

        carpeta = SALIDA / fuente
        carpeta.mkdir(parents=True, exist_ok=True)
        archivo = carpeta / f"{nombre}_{ahora:%Y%m%d}.json"
        archivo.write_text(json.dumps(crudo, ensure_ascii=False, indent=1), encoding="utf-8")
        registrar([ahora.isoformat(), fuente, nombre, serie["id"], n, archivo.relative_to(RAIZ).as_posix(), "ok"])
        print(f"    OK: {n} observaciones -> {archivo.relative_to(RAIZ).as_posix()}")
        time.sleep(2)

    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()