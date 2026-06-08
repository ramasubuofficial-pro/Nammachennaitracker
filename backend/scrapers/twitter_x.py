import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from datetime import datetime, timedelta, timezone
import email.utils
from typing import List, Dict
import asyncio
import re
from .utils import geocode_location, parse_date_from_text

# Suppress HTML parser warning when parsing XML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# List of public Nitter instances for rotation/fallback
NITTER_INSTANCES = [
    "nitter.privacydev.net",
    "nitter.net-freaks.com",
    "nitter.poast.org",
    "nitter.cz",
    "nitter.unixfox.eu"
]

# Party handles mapped to handles and database names
TWITTER_ACCOUNTS = {
    "TVK": {
        "handles": ["tvkvijayhq", "TVKPartyHQ"],
        "color": "#ffd700"
    },
    "DMK": {
        "handles": ["arivalayam"],
        "color": "#ff0000"
    },
    "AIADMK": {
        "handles": ["AIADMKOfficial"],
        "color": "#008000"
    },
    "NTK": {
        "handles": ["NaamTamilarOrg"],
        "color": "#ffa500"
    }
}

async def fetch_nitter_rss(handle: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Try nitter instances sequentially until one succeeds
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/{handle}/rss"
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            # Silently fail and try next instance
            continue
            
    print(f"All Nitter instances failed for @{handle}.")
    return ""

async def scrape_twitter_account(party_name: str, handle: str, color: str) -> List[Dict]:
    events = []
    xml_content = await fetch_nitter_rss(handle)
    if not xml_content:
        return []
        
    try:
        soup = BeautifulSoup(xml_content, "html.parser")
        items = soup.find_all("item")
        
        keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "ஆர்ப்பாட்டம்", "பரப்புரை", "அறிவிப்பு"]
        areas = ["Velachery", "Adyar", "Mylapore", "Saidapet", "Chepauk", "Triplicane", "T. Nagar", "Anna Nagar", "Central", "Egmore", "Guindy", "Purasawalkam", "Tambaram", "Chromepet", "Nungambakkam", "Royapettah"]
        chennai_indicators = ["chennai", "சென்ன", "velachery", "adyar", "mylapore", "saidapet", "chepauk", "triplicane", "t. nagar", "anna nagar", "central", "egmore", "guindy", "purasawalkam", "tambaram", "chromepet", "nungambakkam", "royapettah"]
        
        for item in items:
            title = item.find("title").get_text() if item.find("title") else ""
            
            link_el = item.find("link")
            link = ""
            if link_el:
                link = link_el.get_text() or link_el.next_sibling
                if link:
                    link = str(link).strip()
            
            # Clean up the Nitter link to direct to original X.com link
            if link:
                for instance in NITTER_INSTANCES:
                    link = link.replace(instance, "x.com")
            
            text = title
            
            if any(k in text for k in keywords) and any(ind in text.lower() for ind in chennai_indicators):
                # Parse publication date
                pub_el = item.find("pubdate")
                pub_time = datetime.utcnow()
                if pub_el:
                    try:
                        pub_time = email.utils.parsedate_to_datetime(pub_el.get_text()).astimezone(timezone.utc).replace(tzinfo=None)
                    except Exception as parse_err:
                        print(f"Error parsing pubDate: {parse_err}")
                
                # Search for explicit event date
                event_date = parse_date_from_text(text)
                
                # If no explicit event date and tweet published > 24 hours ago, skip
                if not event_date and (datetime.utcnow() - pub_time) > timedelta(hours=24):
                    continue
                    
                found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                
                # Set start/end times
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
                    "status": "unverified",
                    "source_url": link or f"https://x.com/{handle}",
                    "source_name": f"@{handle} Twitter"
                }
                
                coords = await geocode_location(found_area)
                if coords:
                    event["latitude"], event["longitude"] = coords
                    events.append(event)
    except Exception as e:
        print(f"Twitter parsing error for @{handle}: {e}")
        
    return events

async def scrape_twitter_x() -> List[Dict]:
    print("Running Twitter/X Scrapers...")
    tasks = []
    for party, info in TWITTER_ACCOUNTS.items():
        for handle in info["handles"]:
            tasks.append(scrape_twitter_account(party, handle, info["color"]))
            
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_events = []
    for r in results:
        if isinstance(r, list):
            all_events.extend(r)
        elif isinstance(r, Exception):
            print(f"Twitter sub-scraper failed: {r}")
            
    return all_events

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    events = loop.run_until_complete(scrape_twitter_x())
    print(f"Scraped {len(events)} events from Twitter/X.")
