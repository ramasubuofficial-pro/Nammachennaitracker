import httpx
import json
import os
from typing import Optional, Tuple

CACHE_FILE = "data/chennai_locations.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=4)

async def geocode_location(location_name: str) -> Optional[Tuple[float, float]]:
    cache = load_cache()
    
    # Check cache first
    if location_name in cache:
        return cache[location_name]["lat"], cache[location_name]["lng"]
    
    # Query Nominatim (with Chennai context)
    query = f"{location_name}, Chennai, Tamil Nadu, India"
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    
    headers = {"User-Agent": "NammaChennaiTracker/1.0"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()
            
            if data:
                lat = float(data[0]["lat"])
                lng = float(data[0]["lon"])
                
                # Update cache
                cache[location_name] = {"lat": lat, "lng": lng}
                save_cache(cache)
                
                return lat, lng
    except Exception as e:
        print(f"Geocoding error for {location_name}: {e}")
    
    return None
