import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import re
from .utils import geocode_location, parse_date_from_text
from datetime import timezone

# Suppress HTML parser warning when parsing XML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Party YouTube channels mapped to channel IDs
YOUTUBE_CHANNELS = {
    "TVK": {
        "channel_id": "UCGZHc6wDJFjeNAAJhatSDXg",
        "color": "#ffd700"
    },
    "DMK": {
        "channel_id": "UCU3vZv9cZGF0DC_oO_mJ6-Q",
        "color": "#ff0000"
    },
    "NTK": {
        "channel_id": "UCaHtAkjUh6995E5N2A0-vZQ",
        "color": "#ffa500"
    }
}

async def scrape_channel_videos(party_name: str, channel_id: str, color: str) -> List[Dict]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    events = []
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                print(f"YouTube RSS for {party_name} failed: status {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            entries = soup.find_all("entry")
            
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "ஆர்ப்பாட்டம்", "பரப்புரை", "நேரலை"]
            areas = ["Velachery", "Adyar", "Mylapore", "Saidapet", "Chepauk", "Triplicane", "T. Nagar", "Anna Nagar", "Central", "Egmore", "Guindy", "Purasawalkam", "Tambaram", "Chromepet", "Nungambakkam", "Royapettah"]
            chennai_indicators = ["chennai", "சென்ன", "velachery", "adyar", "mylapore", "saidapet", "chepauk", "triplicane", "t. nagar", "anna nagar", "central", "egmore", "guindy", "purasawalkam", "tambaram", "chromepet", "nungambakkam", "royapettah"]
            
            for entry in entries:
                title = entry.find("title").get_text() if entry.find("title") else ""
                link_el = entry.find("link")
                link = link_el["href"] if link_el and link_el.has_attr("href") else ""
                
                desc_el = entry.find(re.compile(".*description"))
                desc = desc_el.get_text() if desc_el else ""
                
                text = f"{title} {desc}"
                
                # Check for keywords and Chennai indicator
                if any(k in text for k in keywords) and any(ind in text.lower() for ind in chennai_indicators):
                    # Parse publication time
                    pub_el = entry.find("published")
                    pub_time = datetime.utcnow()
                    if pub_el:
                        try:
                            pub_str = pub_el.get_text().strip()
                            if pub_str.endswith('Z'):
                                pub_str = pub_str[:-1] + '+00:00'
                            pub_time = datetime.fromisoformat(pub_str).astimezone(timezone.utc).replace(tzinfo=None)
                        except Exception as parse_err:
                            print(f"Error parsing pub date: {parse_err}")
                    
                    # Try to parse explicit event date from title or description
                    event_date = parse_date_from_text(text)
                    
                    # Filter out old events: if no explicit date and published > 24 hours ago, skip
                    if not event_date and (datetime.utcnow() - pub_time) > timedelta(hours=24):
                        continue
                        
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    # Set start/end time
                    if event_date:
                        start_time = event_date
                        end_time = event_date + timedelta(hours=3)
                    else:
                        start_time = pub_time
                        end_time = pub_time + timedelta(hours=2)
                        
                    event = {
                        "party_name": party_name,
                        "party_color": color,
                        "event_type": "rally" if "பேரணி" in text or "rally" in text.lower() or "பரப்புரை" in text else "meeting",
                        "title": title[:100],
                        "title_tamil": title[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": start_time,
                        "end_time": end_time,
                        "status": "confirmed",
                        "source_url": link or url,
                        "source_name": f"{party_name} YouTube"
                    }
                    
                    coords = await geocode_location(found_area)
                    if coords:
                        event["latitude"], event["longitude"] = coords
                        events.append(event)

    except Exception as e:
        print(f"YouTube RSS error for {party_name}: {e}")
        
    return events

async def scrape_youtube_rss() -> List[Dict]:
    print("Running YouTube RSS Scrapers...")
    tasks = []
    for party, info in YOUTUBE_CHANNELS.items():
        tasks.append(scrape_channel_videos(party, info["channel_id"], info["color"]))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_events = []
    for r in results:
        if isinstance(r, list):
            all_events.extend(r)
        elif isinstance(r, Exception):
            print(f"YouTube sub-scraper failed: {r}")
            
    return all_events

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    events = loop.run_until_complete(scrape_youtube_rss())
    print(f"Scraped {len(events)} events from YouTube RSS.")
