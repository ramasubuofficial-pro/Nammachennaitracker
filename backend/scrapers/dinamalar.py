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
    # Updated URL for latest news
    URL = "https://www.dinamalar.com/news/latest-tamil-news"
    
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
            
            # Navigate to the news list in the JSON structure
            # Based on subagent findings: props.pageProps.responseListingMain.newlist.data
            try:
                articles = data["props"]["pageProps"]["responseListingMain"]["newlist"]["data"]
            except KeyError:
                print("Dinamalar: Could not find news list in JSON.")
                return []
            
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "தவெக", "TVK", "விஜய்", "Vijay"]
            
            for art in articles:
                title = art.get("newstitle", "")
                desc = art.get("newsdescription", "")
                slug = art.get("slug", "")
                text = f"{title} {desc}"
                
                if any(k in text for k in keywords):
                    # Extract details
                    areas = ["T. Nagar", "Anna Nagar", "Adyar", "Central", "Egmore", "Guindy", "Purasawalkam"]
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    party_keywords = {"திமுக": "DMK", "அதிமுக": "AIADMK", "பாஜக": "BJP", "தவெக": "TVK", "விசிக": "VCK"}
                    found_party = next((v for k, v in party_keywords.items() if k in text), "Other")
                    
                    event = {
                        "party_name": found_party,
                        "party_color": "#808080",
                        "event_type": "meeting" if "கூட்டம்" in text else "rally",
                        "title": title[:100],
                        "title_tamil": title[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=4),
                        "end_time": datetime.utcnow() + timedelta(hours=6),
                        "status": "unverified",
                        "source_url": f"https://www.dinamalar.com/news/{slug}" if slug else URL,
                        "source_name": "Dinamalar"
                    }
                    
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
