import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio

from ..models import Event
from .utils import geocode_location

THEHINDU_TAMIL_URL = "https://www.hindutamil.in/news/tamilnadu"

async def scrape_thehindu_tamil() -> List[Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    events = []
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(THEHINDU_TAMIL_URL, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Updated selectors based on site redesign
            articles = soup.find_all("a", attrs={"aria-label": "headline"}) or []
            
            keywords = ["தேர்தல்", "கூட்டம்", "meeting", "rally", "campaign", "தவெக", "TVK", "விஜய்", "Vijay"]
            
            for art in articles:
                title_el = art.find("h3")
                if not title_el: continue
                text = title_el.get_text()
                link = art["href"]
                if not link.startswith("http"):
                    link = f"https://www.hindutamil.in{link}"
                
                if any(k in text for k in keywords):
                    # Guess some details for the MVP
                    area = "Chennai"
                    areas = ["Velachery", "Adyar", "Mylapore", "Saidapet", "Chepauk", "Triplicane"]
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    party_keywords = {"திமுக": "DMK", "அதிமுக": "AIADMK", "பாஜக": "BJP", "தவெக": "TVK", "விசிக": "VCK"}
                    found_party = next((v for k, v in party_keywords.items() if k in text), "Other")
                    
                    event = {
                        "party_name": found_party,
                        "party_color": "#ff0000" if found_party == "DMK" else "#ff9933",
                        "event_type": "rally" if "campaign" in text.lower() else "meeting",
                        "title": text[:80],
                        "title_tamil": text[:80],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=3),
                        "end_time": datetime.utcnow() + timedelta(hours=5),
                        "status": "confirmed",
                        "source_url": link,
                        "source_name": "The Hindu Tamil"
                    }
                    
                    coords = await geocode_location(found_area)
                    if coords:
                        event["latitude"], event["longitude"] = coords
                        events.append(event)
                        
    except Exception as e:
        print(f"The Hindu Tamil scraping error: {e}")
        
    return events
