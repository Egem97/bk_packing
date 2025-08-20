import os
import sys
import json
import requests


BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")


def login(username: str = "admin", password: str = "admin123") -> str:
    """Obtain JWT token from the API."""
    resp = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"username": username, "password": password},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_calidad_by_filters(empresa: str, limit: int = 200, offset: int = 0):
    """
    POST /api/v1/data/calidad-producto-terminado
    Enviar empresa usando el campo 'filters' del request body.
    """
    token = login()
    payload = {
        "limit": limit,
        "offset": offset,
        "filters": {"EMPRESA": empresa},
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/data/calidad-producto-terminado",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    print("[filters] status:", resp.status_code)
    if resp.ok:
        data = resp.json()
        print(f"[filters] registros: {len(data)}")
        print(f"[filters] tamaño JSON: {len(json.dumps(data, ensure_ascii=False))} caracteres")
    else:
        print("[filters] error:", resp.text)


def test_calidad_by_empresa_endpoint(empresa: str, limit: int = 10, offset: int = 0):
    """
    POST /api/v1/data/calidad-producto-terminado/
    Enviar empresa usando el esquema dedicado del endpoint.
    """
    token = login()
    payload = {
        "empresa": empresa,
        "limit": limit,
        "offset": offset,
    }
    resp = requests.post(
        f"{BASE_URL}/api/v1/data/calidad-producto-terminado/",
        headers=_auth_headers(token),
        json=payload,
        timeout=60,
    )
    print("[/empresa] status:", resp.status_code)
    if resp.ok:
        data = resp.json()
        print(f"[/empresa] registros: {len(data)}")
        print(f"[/empresa] tamaño JSON: {len(json.dumps(data, ensure_ascii=False))} caracteres")
    else:
        print("[/empresa] error:", resp.text)


if __name__ == "__main__":
    empresa = os.getenv("EMPRESA", "AGRICOLA BLUE GOLD S.A.C.")
    print("BASE_URL:", BASE_URL)
    print("EMPRESA:", empresa)
    test_calidad_by_filters(empresa)
    test_calidad_by_empresa_endpoint(empresa)


