import requests, os, certifi, asyncio, aiohttp
from typing import Generator, AsyncGenerator
import logging
import html

from .settings import settings

logger = logging.getLogger(__name__)

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
    """Synchronous version for backward compatibility."""
    url = f"{settings.snipeit_api_url}/users"
    all_users = []
    params = {"limit": 100, "offset": 0, "expand": "department"}
    
    while True:
        resp = requests.get(url, headers=HEADERS, params=params, verify=CA_BUNDLE, timeout=30)
        resp.raise_for_status()
        data = resp.json()["rows"]
        
        if not data:
            break
            
        all_users.extend(data)
        
        if len(data) < params["limit"]:
            break
            
        params["offset"] += params["limit"]
    
    return all_users

async def fetch_all_users_async() -> list[dict]:
    """Async version with smaller batch sizes."""
    url = f"{settings.snipeit_api_url}/users"
    all_users = []
    
    connector = aiohttp.TCPConnector(ssl=False)  # Use CA_BUNDLE if needed
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        offset = 0
        limit = 100  # Smaller batches
        
        while True:
            params = {"limit": limit, "offset": offset, "expand": "department"}
            
            try:
                async with session.get(url, headers=HEADERS, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    users = data.get("rows", [])
                    
                    if not users:
                        break
                        
                    all_users.extend(users)
                    logger.info(f"Fetched {len(users)} users (offset: {offset})")
                    
                    if len(users) < limit:
                        break
                        
                    offset += limit
                    
            except Exception as e:
                logger.error(f"Error fetching users at offset {offset}: {e}")
                break
    
    return all_users

def user_department_map() -> dict[int, str | None]:
    # cache once per run
    if not hasattr(user_department_map, "_cache"):
        user_department_map._cache = {
            u["id"]: html.unescape(str((u.get("department") or {}).get("name"))) 
            if (u.get("department") or {}).get("name") else None
            for u in fetch_all_users()
        }
    return user_department_map._cache

def fetch_all_hardware() -> Generator[dict, None, None]:
    """Synchronous version for backward compatibility."""
    url = f"{settings.snipeit_api_url}/hardware"
    params = {"limit": 100, "offset": 0, "expand": "company,assigned_to"}
    while True:
        resp = requests.get(url, headers=HEADERS, params=params, verify=CA_BUNDLE, timeout=30)
        resp.raise_for_status()
        data = resp.json()["rows"]
        for item in data:
            yield item
        if not data or len(data) < params["limit"]:
            break
        params["offset"] += params["limit"]

async def fetch_all_hardware_async() -> AsyncGenerator[list[dict], None]:
    """Async version that yields batches of hardware."""
    url = f"{settings.snipeit_api_url}/hardware"
    
    connector = aiohttp.TCPConnector(ssl=False)  # Use CA_BUNDLE if needed
    timeout = aiohttp.ClientTimeout(total=30)
    
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        offset = 0
        limit = 50  # Smaller batches for better memory management
        
        while True:
            params = {"limit": limit, "offset": offset, "expand": "company,assigned_to"}
            
            try:
                async with session.get(url, headers=HEADERS, params=params) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    hardware_batch = data.get("rows", [])
                    
                    if not hardware_batch:
                        break
                        
                    logger.info(f"Fetched {len(hardware_batch)} hardware items (offset: {offset})")
                    yield hardware_batch
                    
                    if len(hardware_batch) < limit:
                        break
                        
                    offset += limit
                    
            except Exception as e:
                logger.error(f"Error fetching hardware at offset {offset}: {e}")
                break

        