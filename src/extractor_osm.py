"""Extractor de OpenStreetMap (Overpass API): tiendas y límites municipales de Colima -> capa Bronce.

Minimización de datos: de cada tienda solo se conservan campos no personales
(identificador, tipo, marca y coordenadas). No se guardan nombres, sitios web ni direcciones.
Los límites municipales son datos administrativos públicos y se guardan completos.

Uso:
    python src/extractor_osm.py                  # tiendas y límites
    python src/extractor_osm.py --solo-limites   # solo límites (retoma los municipios que falten)
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
MUNICIPIOS = [
    "Armería", "Comala", "Coquimatlán", "Cuauhtémoc", "Ixtlahuacán",
    "Manzanillo", "Minatitlán", "Municipio de Colima", "Tecomán", "Villa de Álvarez",
]

CONSULTA_TIENDAS = f"""
[out:json][timeout:90];
area["name"="Colima"]["admin_level"="4"]->.est;
(
  node["shop"~"^({TIENDAS})$"](area.est);
  way["shop"~"^({TIENDAS})$"](area.est);
);
out center tags;
"""

CAMPOS_CONSERVADOS = ["osm_type", "osm_id", "shop", "brand", "lat", "lon"]
CAMPOS_DESCARTADOS = ["name", "website", "phone", "email", "addr:*", "opening_hours", "operator", "otros tags"]


def consulta_limite(nombre):
    return f"""
[out:json][timeout:120];
area["name"="Colima"]["admin_level"="4"]->.est;
relation["boundary"="administrative"]["admin_level"="6"]["name"="{nombre}"](area.est);
out geom;
"""


def consultar(texto, intentos_por_servidor=2, pausa=8):
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


def extraer_tiendas(ahora):
    carpeta = BRONCE / "osm"
    carpeta.mkdir(parents=True, exist_ok=True)
    print("[osm] tiendas_colima")
    crudo = consultar(CONSULTA_TIENDAS)
    registros = [proyectar_tienda(e) for e in (crudo or {}).get("elements", [])]
    if not registros:
        print("    No se obtuvieron tiendas")
        registrar([ahora.isoformat(), "osm", "tiendas_colima", "overpass", 0, "", "error"])
        return False
    archivo = carpeta / f"tiendas_colima_{ahora:%Y%m%d}.json"
    archivo.write_text(json.dumps({
        "fuente": "OpenStreetMap (Overpass API)",
        "fecha_ingesta_utc": ahora.isoformat(),
        "osm_base_timestamp": crudo.get("osm3s", {}).get("timestamp_osm_base"),
        "licencia": LICENCIA,
        "consulta": CONSULTA_TIENDAS.strip(),
        "campos_conservados": CAMPOS_CONSERVADOS,
        "campos_descartados_por_privacidad": CAMPOS_DESCARTADOS,
        "registros": registros,
    }, ensure_ascii=False), encoding="utf-8")
    ruta = archivo.relative_to(RAIZ).as_posix()
    registrar([ahora.isoformat(), "osm", "tiendas_colima", "overpass", len(registros), ruta, "ok"])
    print(f"    OK: {len(registros)} tiendas -> {ruta}")
    return True


def guardar_limites(archivo, ahora, base_ts, relaciones):
    archivo.write_text(json.dumps({
        "fuente": "OpenStreetMap (Overpass API)",
        "fecha_ingesta_utc": ahora.isoformat(),
        "osm_base_timestamp": base_ts,
        "licencia": LICENCIA,
        "nota": "Una consulta por municipio (out geom)",
        "relaciones": list(relaciones.values()),
    }, ensure_ascii=False), encoding="utf-8")


def extraer_limites(ahora):
    carpeta = BRONCE / "osm"
    carpeta.mkdir(parents=True, exist_ok=True)
    archivo = carpeta / f"limites_municipales_colima_{ahora:%Y%m%d}.json"
    relaciones, base_ts = {}, None
    if archivo.exists():  # retoma lo ya descargado hoy
        previo = json.loads(archivo.read_text(encoding="utf-8"))
        base_ts = previo.get("osm_base_timestamp")
        relaciones = {r["tags"]["name"]: r for r in previo.get("relaciones", [])}

    print(f"[osm] limites_municipales_colima (ya descargados: {len(relaciones)} de {len(MUNICIPIOS)})")
    for nombre in MUNICIPIOS:
        if nombre in relaciones:
            print(f"  {nombre}: ya estaba")
            continue
        print(f"  {nombre}:")
        crudo = consultar(consulta_limite(nombre))
        rels = [e for e in (crudo or {}).get("elements", []) if e.get("type") == "relation"]
        if rels:
            relaciones[nombre] = rels[0]
            base_ts = crudo.get("osm3s", {}).get("timestamp_osm_base", base_ts)
            guardar_limites(archivo, ahora, base_ts, relaciones)
            print("    OK")
        else:
            print("    no se pudo obtener; se reintentará en la siguiente ejecución")
        time.sleep(5)

    completo = len(relaciones) == len(MUNICIPIOS)
    ruta = archivo.relative_to(RAIZ).as_posix() if relaciones else ""
    registrar([ahora.isoformat(), "osm", "limites_municipales_colima", "overpass",
               len(relaciones), ruta, "ok" if completo else "parcial"])
    print(f"    Municipios disponibles: {len(relaciones)} de {len(MUNICIPIOS)}")
    return completo


def main():
    ahora = datetime.now(timezone.utc)
    solo_limites = "--solo-limites" in sys.argv
    ok = True
    if not solo_limites:
        ok = extraer_tiendas(ahora) and ok
        time.sleep(5)
    ok = extraer_limites(ahora) and ok
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()