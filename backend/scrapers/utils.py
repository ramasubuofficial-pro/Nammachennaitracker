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

import re
from datetime import datetime

TAMIL_MONTHS = {
    "ஜனவரி": 1, "ஜன": 1, "january": 1, "jan": 1,
    "பிப்ரவரி": 2, "பிப்": 2, "february": 2, "feb": 2,
    "மார்ச்": 3, "march": 3, "mar": 3,
    "ஏப்ரல்": 4, "ஏப்": 4, "april": 4, "apr": 4,
    "மே": 5, "may": 5,
    "ஜூன்": 6, "ஜூன": 6, "june": 6, "jun": 6,
    "ஜூலை": 7, "ஜூல": 7, "july": 7, "jul": 7,
    "ஆகஸ்ட்": 8, "ஆக": 8, "august": 8, "aug": 8,
    "செப்டம்பர்": 9, "செப்": 9, "september": 9, "sep": 9,
    "அக்டோபர்": 10, "அக்": 10, "october": 10, "oct": 10,
    "நவம்பர்": 11, "நவ": 11, "november": 11, "nov": 11,
    "டிசம்பர்": 12, "டிச": 12, "december": 12, "dec": 12
}

def parse_date_from_text(text: str) -> Optional[datetime]:
    if not text:
        return None
        
    # Try pattern: DD-MM-YYYY or DD/MM/YYYY or DD.MM.YYYY
    match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})', text)
    if match:
        day, month, year = map(int, match.groups())
        try:
            return datetime(year, month, day, 9, 0)
        except ValueError:
            pass
            
    # Try pattern: DD-MM-YY or DD/MM/YY
    match = re.search(r'(\d{1,2})[-/.](\d{1,2})[-/.](\d{2})\b', text)
    if match:
        day, month, year_short = map(int, match.groups())
        year = 2000 + year_short
        try:
            return datetime(year, month, day, 9, 0)
        except ValueError:
            pass

    # Try matching Tamil or English month names: e.g. "ஜூன் 06" or "06 ஜூன்" or "June 6"
    for month_name, month_num in TAMIL_MONTHS.items():
        # Pattern 1: month_name followed by 1 or 2 digits date
        p1 = re.compile(rf'{month_name}\s*,?\s*(\d{{1,2}})', re.IGNORECASE)
        m1 = p1.search(text)
        if m1:
            day = int(m1.group(1))
            year = datetime.now().year
            year_match = re.search(r'\b(202\d)\b', text)
            if year_match:
                year = int(year_match.group(1))
            try:
                return datetime(year, month_num, day, 9, 0)
            except ValueError:
                pass
                
        # Pattern 2: 1 or 2 digits date followed by month_name
        p2 = re.compile(rf'(\d{{1,2}})\s*,?\s*{month_name}', re.IGNORECASE)
        m2 = p2.search(text)
        if m2:
            day = int(m2.group(1))
            year = datetime.now().year
            year_match = re.search(r'\b(202\d)\b', text)
            if year_match:
                year = int(year_match.group(1))
            try:
                return datetime(year, month_num, day, 9, 0)
            except ValueError:
                pass
                
    return None

