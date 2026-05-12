import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio

from ..models import Event
from .utils import geocode_location

DINAMALAR_CHENNAI_URL = "https://www.dinamalar.com/news_main.asp?cat=2"

async def scrape_dinamalar() -> List[Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    events = []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(DINAMALAR_CHENNAI_URL, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Simple keyword matching for demo/MVP
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic"]
            articles = soup.find_all("div", class_="news_main_txt") or []
            
            for art in articles:
                text = art.get_text()
                link = art.find("a")["href"] if art.find("a") else DINAMALAR_CHENNAI_URL
                
                if any(k in text for k in keywords):
                    # In a real app, we'd use NLP or LLM to extract details
                    # For MVP, we'll create a semi-simulated event from the news headline
                    location = "Chennai" # Default
                    # Look for common Chennai areas in text (simplified)
                    areas = ["T. Nagar", "Anna Nagar", "Adyar", "Central", "Egmore", "Guindy", "Purasawalkam"]
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    party_keywords = {"திமுக": "DMK", "அதிமுக": "AIADMK", "பாஜக": "BJP", "தவெக": "TVK", "விசிக": "VCK"}
                    found_party = next((v for k, v in party_keywords.items() if k in text), "Other")
                    
                    event = {
                        "party_name": found_party,
                        "party_color": "#808080", # Default gray
                        "event_type": "meeting" if "கூட்டம்" in text else "rally",
                        "title": text[:100],
                        "title_tamil": text[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=4),
                        "end_time": datetime.utcnow() + timedelta(hours=6),
                        "status": "unverified",
                        "source_url": link,
                        "source_name": "Dinamalar"
                    }
                    
                    # Geocode the area
                    coords = await geocode_location(found_area)
                    if coords:
                        event["latitude"], event["longitude"] = coords
                        events.append(event)
                        
    except Exception as e:
        print(f"Dinamalar scraping error: {e}")
        
    return events

# Small test block
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scrape_dinamalar())
    print(f"Scraped {len(results)} potential events from Dinamalar.")
