import requests, os, certifi
from typing import Generator

from .settings import settings

# Use custom CA bundle if provided, otherwise use default certifi bundle
CA_BUNDLE = settings.requests_ca_bundle if settings.requests_ca_bundle else certifi.where()

# Set environment variables for SSL
os.environ['SSL_CERT_FILE'] = CA_BUNDLE
os.environ['REQUESTS_CA_BUNDLE'] = CA_BUNDLE

HEADERS = {
    "Authorization": f"Bearer {settings.snipeit_token}",
    "Accept": "application/json",
}

def fetch_all_users() -> list[dict]:
    url = f"{settings.snipeit_api_url}/users"
    params = {"limit": 1000, "expand": "department"}
    resp = requests.get(url, headers=HEADERS, params=params, verify=CA_BUNDLE, timeout=30)
    resp.raise_for_status()
    return resp.json()["rows"]

def user_department_map() -> dict[int, str | None]:
    # cache once per run
    if not hasattr(user_department_map, "_cache"):
        user_department_map._cache = {
            u["id"]: (u.get("department") or {}).get("name")
            for u in fetch_all_users()
        }
    return user_department_map._cache

def fetch_all_hardware() -> Generator[dict, None, None]:
    url = f"{settings.snipeit_api_url}/hardware"
    params = {"limit": 100, "offset": 0, "expand": "company,assigned_to"}
    while True:
        resp = requests.get(url, headers=HEADERS, params=params)
        resp.raise_for_status()
        data = resp.json()["rows"]
        for item in data:
            yield item
        if not data or len(data) < params["limit"]:
            break
        params["offset"] += params["limit"]

        