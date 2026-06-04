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
            
            # Keywords focusing on traffic, rallies, meetings, and campaigns to avoid traffic
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "தேரோட்டம்", "ஊர்வலம்"]
            
            # Chennai indicators to filter out non-Chennai articles from the general Tamilnadu page
            chennai_indicators = ["chennai", "சென்ன", "velachery", "adyar", "mylapore", "saidapet", "chepauk", "triplicane", "t. nagar", "anna nagar", "central", "egmore", "guindy", "purasawalkam", "tambaram", "chromepet", "nungambakkam", "royapettah"]
            
            # Chennai areas mapping for bilingual detection
            area_mapping = {
                "T. Nagar": ["t. nagar", "t nagar", "தி. நகர்", "டி. நகர்"],
                "Anna Nagar": ["anna nagar", "அண்ணா நகர்"],
                "Adyar": ["adyar", "அடையாறு"],
                "Central": ["central", "சென்ட்ரல்"],
                "Egmore": ["egmore", "எழும்பூர்"],
                "Guindy": ["guindy", "கிண்டி"],
                "Purasawalkam": ["purasawalkam", "புரசைவாக்கம்"],
                "Mylapore": ["mylapore", "மயிலாப்பூர்"],
                "Velachery": ["velachery", "வேளச்சேரி"],
                "Saidapet": ["saidapet", "சைதாப்பேட்டை"],
                "Triplicane": ["triplicane", "திருவல்லிக்கேணி"],
                "Chepauk": ["chepauk", "சேப்பாக்கம்"],
                "Tambaram": ["tambaram", "தாம்பரம்"],
                "Chromepet": ["chromepet", "குரோம்பேட்டை"],
                "Nungambakkam": ["nungambakkam", "நுங்கம்பாக்கம்"],
                "Royapettah": ["royapettah", "இராயப்பேட்டை"]
            }
            
            party_keywords = {
                "அதிமுக": "AIADMK",
                "திமுக": "DMK",
                "பாஜக": "BJP",
                "தவெக": "TVK",
                "விசிக": "VCK",
                "நாதக": "NTK",
                "காங்கிரஸ்": "Congress"
            }
            
            # Sort party keys by length descending to prevent substring mismatch
            sorted_party_keys = sorted(party_keywords.keys(), key=len, reverse=True)
            
            for art in articles:
                title_el = art.find("h3")
                if not title_el: continue
                text = title_el.get_text()
                link = art["href"]
                if not link.startswith("http"):
                    link = f"https://www.hindutamil.in{link}"
                
                # Check if it contains keywords AND refers to Chennai
                if any(k in text for k in keywords) and any(ind in text.lower() for ind in chennai_indicators):
                    # Search for area name
                    found_area = "Chennai"
                    for area_eng, patterns in area_mapping.items():
                        if any(p in text.lower() for p in patterns):
                            found_area = area_eng
                            break
                    
                    found_party = next((party_keywords[k] for k in sorted_party_keys if k in text), "Other")
                    
                    event = {
                        "party_name": found_party,
                        "party_color": "#ff0000" if found_party == "DMK" else "#ff9933",
                        "event_type": "rally" if "campaign" in text.lower() or "பேரணி" in text or "rally" in text.lower() else "meeting",
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

# Small test block
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(scrape_thehindu_tamil())
    print(f"Scraped {len(results)} potential events from The Hindu Tamil.")
