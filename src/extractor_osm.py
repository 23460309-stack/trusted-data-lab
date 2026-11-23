"""Extractor de OpenStreetMap (Overpass API): tiendas y límites municipales de Colima -> capa Bronce.

Minimización de datos: de cada tienda solo se conservan campos no personales
(identificador, tipo, marca y coordenadas). No se guardan nombres, sitios web ni direcciones.
Los límites municipales son datos administrativos públicos y se guardan completos.
"""
import json
import sys
import time
from datetime import datetime, timezone

import requests

from config import BRONCE, RAIZ
from extractor import registrar

SERVIDORES = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HEADERS = {"User-Agent": "TrustedDataLab-ITColima/1.0 (proyecto academico; github.com/23460309-stack/trusted-data-lab)"}
TIENDAS = "convenience|supermarket|general"
LICENCIA = "ODbL 1.0. Atribución: © OpenStreetMap contributors (https://www.openstreetmap.org/copyright)"

CONSULTA_TIENDAS = f"""
[out:json][timeout:90];
area["name"="Colima"]["admin_level"="4"]->.est;
(
  node["shop"~"^({TIENDAS})$"](area.est);
  way["shop"~"^({TIENDAS})$"](area.est);
);
out center tags;
"""

CONSULTA_LIMITES = """
[out:json][timeout:180];
area["name"="Colima"]["admin_level"="4"]->.est;
relation["boundary"="administrative"]["admin_level"="6"](area.est);
out geom;
"""

CAMPOS_CONSERVADOS = ["osm_type", "osm_id", "shop", "brand", "lat", "lon"]
CAMPOS_DESCARTADOS = ["name", "website", "phone", "email", "addr:*", "opening_hours", "operator", "otros tags"]


def consultar(texto, intentos_por_servidor=2, pausa=10):
    for servidor in SERVIDORES:
        host = servidor.split("/")[2]
        for n in range(1, intentos_por_servidor + 1):
            try:
                r = requests.post(servidor, data={"data": texto}, headers=HEADERS, timeout=200)
                print(f"    {host}: HTTP {r.status_code} (intento {n}/{intentos_por_servidor})")
                if r.status_code == 200:
                    return r.json()
            except (requests.RequestException, ValueError) as e:
                print(f"    {host}: error {type(e).__name__} (intento {n}/{intentos_por_servidor})")
            time.sleep(pausa)
    return None


def proyectar_tienda(e):
    tags = e.get("tags", {})
    centro = e.get("center", {})
    return {
        "osm_type": e["type"],
        "osm_id": e["id"],
        "shop": tags.get("shop"),
        "brand": tags.get("brand"),
        "lat": e.get("lat", centro.get("lat")),
        "lon": e.get("lon", centro.get("lon")),
    }


def guardar(carpeta, nombre, ahora, cuerpo):
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / f"{nombre}_{ahora:%Y%m%d}.json"
    archivo.write_text(json.dumps(cuerpo, ensure_ascii=False), encoding="utf-8")
    return archivo


def main():
    ahora = datetime.now(timezone.utc)
    carpeta = BRONCE / "osm"
    fallos = 0

    # 1) Tiendas
    print("[osm] tiendas_colima")
    crudo = consultar(CONSULTA_TIENDAS)
    registros = [proyectar_tienda(e) for e in (crudo or {}).get("elements", [])]
    if not registros:
        print("    No se obtuvieron tiendas")
        registrar([ahora.isoformat(), "osm", "tiendas_colima", "overpass", 0, "", "error"])
        fallos += 1
    else:
        archivo = guardar(carpeta, "tiendas_colima", ahora, {
            "fuente": "OpenStreetMap (Overpass API)",
            "fecha_ingesta_utc": ahora.isoformat(),
            "osm_base_timestamp": crudo.get("osm3s", {}).get("timestamp_osm_base"),
            "licencia": LICENCIA,
            "consulta": CONSULTA_TIENDAS.strip(),
            "campos_conservados": CAMPOS_CONSERVADOS,
            "campos_descartados_por_privacidad": CAMPOS_DESCARTADOS,
            "registros": registros,
        })
        ruta = archivo.relative_to(RAIZ).as_posix()
        registrar([ahora.isoformat(), "osm", "tiendas_colima", "overpass", len(registros), ruta, "ok"])
        print(f"    OK: {len(registros)} tiendas -> {ruta}")

    time.sleep(5)

    # 2) Límites municipales
    print("[osm] limites_municipales_colima")
    crudo = consultar(CONSULTA_LIMITES)
    relaciones = [e for e in (crudo or {}).get("elements", []) if e.get("type") == "relation"]
    if not relaciones:
        print("    No se obtuvieron límites")
        registrar([ahora.isoformat(), "osm", "limites_municipales_colima", "overpass", 0, "", "error"])
        fallos += 1
    else:
        archivo = guardar(carpeta, "limites_municipales_colima", ahora, {
            "fuente": "OpenStreetMap (Overpass API)",
            "fecha_ingesta_utc": ahora.isoformat(),
            "osm_base_timestamp": crudo.get("osm3s", {}).get("timestamp_osm_base"),
            "licencia": LICENCIA,
            "consulta": CONSULTA_LIMITES.strip(),
            "relaciones": relaciones,
        })
        ruta = archivo.relative_to(RAIZ).as_posix()
        registrar([ahora.isoformat(), "osm", "limites_municipales_colima", "overpass", len(relaciones), ruta, "ok"])
        print(f"    OK: {len(relaciones)} municipios -> {ruta}")

    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()