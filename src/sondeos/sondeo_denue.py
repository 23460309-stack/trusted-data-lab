"""Sondeo de la API del DENUE: muestra los campos disponibles sin imprimir datos de contacto.

El token se toma de la variable de entorno DENUE_TOKEN o, si no existe, se pide por teclado.
Nunca se escribe en el código.
"""
import os
import sys
from getpass import getpass

import requests

BASE = "https://www.inegi.org.mx/app/api/denue/v1/consulta"
HEADERS = {"User-Agent": "TrustedDataLab-ITColima/1.0 (proyecto academico)"}
CAMPOS_SEGUROS = ("Id", "CLEE", "Clase_actividad", "Estrato", "Ubicacion", "Latitud", "Longitud")


def obtener_token():
    token = os.environ.get("DENUE_TOKEN") or getpass("Pega tu token del DENUE (no se mostrará) y presiona Enter: ")
    token = token.strip()
    if not token:
        sys.exit("No se proporcionó ningún token")
    return token


def main():
    token = obtener_token()

    # Búsqueda por entidad: condición "abarrotes", entidad 06 (Colima), registros 1 al 5
    try:
        r = requests.get(f"{BASE}/BuscarEntidad/abarrotes/06/1/5/{token}", headers=HEADERS, timeout=60)
    except requests.RequestException as e:
        sys.exit(f"Error de red: {type(e).__name__}")
    print("HTTP", r.status_code)

    try:
        datos = r.json()
    except ValueError:
        print("La respuesta no es JSON:", r.text[:300])
        sys.exit(1)

    if not isinstance(datos, list) or not datos:
        print("Respuesta inesperada:", str(datos)[:300])
        sys.exit(1)

    print("Registros recibidos:", len(datos))
    print("Campos disponibles:", list(datos[0].keys()))
    print("\nMuestra (solo campos no sensibles):")
    for d in datos[:3]:
        print({k: d[k] for k in CAMPOS_SEGUROS if k in d})


if __name__ == "__main__":
    main()