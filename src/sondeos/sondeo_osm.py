"""Sondeo de OpenStreetMap (Overpass API): tiendas y municipios del estado de Colima.

No requiere token. No imprime nombres ni datos de contacto de las tiendas, solo conteos.
"""
import sys
import time
from collections import Counter

import requests

URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "TrustedDataLab-ITColima/1.0 (proyecto academico)"}
TIENDAS = "convenience|supermarket|general|grocery"

CONSULTA_TIENDAS = f"""
[out:json][timeout:90];
area["name"="Colima"]["admin_level"="4"]->.est;
(
  node["shop"~"^({TIENDAS})$"](area.est);
  way["shop"~"^({TIENDAS})$"](area.est);
);
out center tags;
"""

CONSULTA_MUNICIPIOS = """
[out:json][timeout:90];
area["name"="Colima"]["admin_level"="4"]->.est;
relation["boundary"="administrative"]["admin_level"="6"](area.est);
out tags;
"""


def consultar(texto, intentos=3):
    for n in range(1, intentos + 1):
        try:
            r = requests.post(URL, data={"data": texto}, headers=HEADERS, timeout=120)
            print(f"  HTTP {r.status_code}")
            if r.status_code == 200:
                return r.json()
        except (requests.RequestException, ValueError) as e:
            print(f"  Error {type(e).__name__}")
        time.sleep(15 * n)
    return None


def main():
    print("Consultando tiendas...")
    datos = consultar(CONSULTA_TIENDAS)
    if not datos:
        sys.exit("No se pudo obtener respuesta de Overpass")
    elementos = datos.get("elements", [])
    print(f"Elementos recibidos: {len(elementos)}")
    print("Por tipo de elemento:", dict(Counter(e["type"] for e in elementos)))
    print("Por tipo de tienda:", dict(Counter(e.get("tags", {}).get("shop") for e in elementos)))

    etiquetas = Counter(k for e in elementos for k in e.get("tags", {}))
    print("\nEtiquetas más frecuentes (conteo de elementos que las tienen):")
    for k, n in etiquetas.most_common(15):
        print(f"  {k}: {n}")

    sin_coord = sum(1 for e in elementos if "lat" not in e and "center" not in e)
    print(f"\nElementos sin coordenadas: {sin_coord}")

    time.sleep(5)
    print("\nConsultando municipios...")
    mun = consultar(CONSULTA_MUNICIPIOS)
    if not mun:
        sys.exit("No se pudieron obtener los municipios")
    nombres = sorted(e.get("tags", {}).get("name", "?") for e in mun.get("elements", []))
    print(f"Municipios encontrados: {len(nombres)}")
    print(nombres)


if __name__ == "__main__":
    main()