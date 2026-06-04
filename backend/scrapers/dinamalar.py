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
    # Targeted URL for Chennai local news
    URL = "https://www.dinamalar.com/news/tamil-nadu-district-news-chennai"
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(URL, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find the Next.js data script
            next_data_script = soup.find("script", id="__NEXT_DATA__")
            if not next_data_script:
                print("Dinamalar: __NEXT_DATA__ script not found.")
                return []
            
            import json
            data = json.loads(next_data_script.string)
            
            # Navigate to the Chennai news list in the Next.js JSON structure
            try:
                articles = data["props"]["pageProps"]["responseapidata"]["districtlisting"]["data"]
            except KeyError:
                print("Dinamalar: Could not find news list in JSON.")
                return []
            
            # Keywords matching the traffic, rally, meeting and strike logic to avoid traffic
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "மறியல்", "முடக்கம்", "strike"]
            
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
            
            # Sort party keys by length descending to prevent substring mismatch (e.g. "அதிமுக" matching "திமுக")
            sorted_party_keys = sorted(party_keywords.keys(), key=len, reverse=True)
            
            for art in articles:
                title = art.get("newstitle", "")
                desc = art.get("newsdescription", "")
                slug = art.get("slug", "")
                text = f"{title} {desc}"
                
                if any(k in text for k in keywords):
                    # Search for area name
                    found_area = "Chennai"
                    for area_eng, patterns in area_mapping.items():
                        if any(p in text.lower() for p in patterns):
                            found_area = area_eng
                            break
                    
                    found_party = next((party_keywords[k] for k in sorted_party_keys if k in text), "Other")
                    if found_party == "Other":
                        continue
                    
                    # Normalize slug to build absolute URL
                    source_url = URL
                    if slug:
                        source_url = f"https://www.dinamalar.com{slug}" if slug.startswith("/") else f"https://www.dinamalar.com/{slug}"
                    
                    event = {
                        "party_name": found_party,
                        "party_color": "#808080",
                        "event_type": "meeting" if "கூட்டம்" in text or "meeting" in text.lower() else "rally",
                        "title": title[:100],
                        "title_tamil": title[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=4),
                        "end_time": datetime.utcnow() + timedelta(hours=6),
                        "status": "unverified",
                        "source_url": source_url,
                        "source_name": "Dinamalar"
                    }
                    
                    # Geocode the area to fetch coordinates
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
