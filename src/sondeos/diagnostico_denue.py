"""Diagnóstico de la API del DENUE: prueba varias consultas y muestra qué responde cada una.

El token se toma de la variable de entorno DENUE_TOKEN o se pide por teclado. No se imprime.
"""
import os
import sys
from getpass import getpass
from urllib.parse import quote

import requests

BASE = "https://www.inegi.org.mx/app/api/denue/v1/consulta"
HEADERS = {"User-Agent": "TrustedDataLab-ITColima/1.0 (proyecto academico)"}

PRUEBAS = [
    ("Ejemplo de la documentación: restaurantes en Jalisco", "BuscarEntidad/restaurantes/14/1/5"),
    ("'abarrotes' en Colima", "BuscarEntidad/abarrotes/06/1/5"),
    ("'tiendas de abarrotes' en Colima", "BuscarEntidad/" + quote("tiendas de abarrotes") + "/06/1/5"),
    ("'todos' en Colima", "BuscarEntidad/todos/06/1/5"),
    ("'abarrotes' a 3 km del centro de Colima", "Buscar/abarrotes/19.2433,-103.7249/3000"),
    ("Conteo de la clase 461110 (tiendas de abarrotes) en Colima", "Cuantificar/461110/06/0"),
]


def obtener_token():
    token = os.environ.get("DENUE_TOKEN") or getpass("Pega tu token del DENUE (no se mostrará) y presiona Enter: ")
    token = token.strip()
    if not token:
        sys.exit("No se proporcionó ningún token")
    return token


def main():
    token = obtener_token()
    campos_mostrados = False
    for etiqueta, ruta in PRUEBAS:
        try:
            r = requests.get(f"{BASE}/{ruta}/{token}", headers=HEADERS, timeout=60)
        except requests.RequestException as e:
            print(f"[error de red: {type(e).__name__}] {etiqueta}")
            continue
        try:
            datos = r.json()
            detalle = f"JSON con {len(datos)} elementos" if isinstance(datos, list) else f"JSON: {str(datos)[:100]}"
        except ValueError:
            datos = None
            detalle = f"texto: {r.text.strip()[:100]}"
        print(f"[HTTP {r.status_code}] {etiqueta} -> {detalle}")
        if isinstance(datos, list) and datos and isinstance(datos[0], dict) and not campos_mostrados:
            print("    Campos disponibles:", list(datos[0].keys()))
            campos_mostrados = True


if __name__ == "__main__":
    main()