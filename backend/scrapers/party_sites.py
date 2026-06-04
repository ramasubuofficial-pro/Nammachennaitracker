import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import re
from .utils import geocode_location

# Suppress HTML parser warning when parsing XML
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

async def scrape_ntk_website() -> List[Dict]:
    url = "https://www.naamtamilar.org/feed/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    events = []
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                print(f"NTK RSS failed: status {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("item")
            
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "ஆர்ப்பாட்டம்", "அறிவிப்பு"]
            areas = ["Velachery", "Adyar", "Mylapore", "Saidapet", "Chepauk", "Triplicane", "T. Nagar", "Anna Nagar", "Central", "Egmore", "Guindy", "Purasawalkam", "Tambaram", "Chromepet", "Nungambakkam", "Royapettah"]
            chennai_indicators = ["chennai", "சென்ன", "velachery", "adyar", "mylapore", "saidapet", "chepauk", "triplicane", "t. nagar", "anna nagar", "central", "egmore", "guindy", "purasawalkam", "tambaram", "chromepet", "nungambakkam", "royapettah"]
            
            for item in items:
                title = item.find("title").get_text() if item.find("title") else ""
                
                # Retrieve link cleanly
                link_el = item.find("link")
                link = ""
                if link_el:
                    # sometimes link element in HTML parser wraps next sibling
                    link = link_el.get_text() or link_el.next_sibling
                    if link:
                        link = str(link).strip()
                
                desc_el = item.find(re.compile(".*description"))
                desc = desc_el.get_text() if desc_el else ""
                text = f"{title} {desc}"
                
                # Check for keywords and Chennai context
                if any(k in text for k in keywords) and any(ind in text.lower() for ind in chennai_indicators):
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    event = {
                        "party_name": "NTK",
                        "party_color": "#ffa500",
                        "event_type": "rally" if "பேரணி" in text or "rally" in text.lower() else "meeting",
                        "title": title[:100],
                        "title_tamil": title[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=24), # upcoming
                        "end_time": datetime.utcnow() + timedelta(hours=26),
                        "status": "confirmed",
                        "source_url": link or url,
                        "source_name": "NTK Official Site"
                    }
                    
                    coords = await geocode_location(found_area)
                    if coords:
                        event["latitude"], event["longitude"] = coords
                        events.append(event)
    except Exception as e:
        print(f"NTK website scraping error: {e}")
        
    return events

async def scrape_aiadmk_website() -> List[Dict]:
    url = "https://aiadmk.org.in/feed/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    events = []
    
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                print(f"AIADMK RSS failed: status {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.find_all("item")
            
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "ஆர்ப்பாட்டம்", "அறிவிப்பு"]
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
                        
                desc_el = item.find(re.compile(".*description"))
                desc = desc_el.get_text() if desc_el else ""
                text = f"{title} {desc}"
                
                if any(k in text for k in keywords) and any(ind in text.lower() for ind in chennai_indicators):
                    found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                    
                    event = {
                        "party_name": "AIADMK",
                        "party_color": "#008000",
                        "event_type": "rally" if "பேரணி" in text or "rally" in text.lower() else "meeting",
                        "title": title[:100],
                        "title_tamil": title[:100],
                        "location_name": found_area,
                        "location_tamil": found_area, 
                        "start_time": datetime.utcnow() + timedelta(hours=24),
                        "end_time": datetime.utcnow() + timedelta(hours=26),
                        "status": "confirmed",
                        "source_url": link or url,
                        "source_name": "AIADMK Official Site"
                    }
                    
                    coords = await geocode_location(found_area)
                    if coords:
                        event["latitude"], event["longitude"] = coords
                        events.append(event)
    except Exception as e:
        print(f"AIADMK website scraping error: {e}")
        
    return events

async def scrape_tvk_website() -> List[Dict]:
    url = "https://tvkvijay.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    events = []
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                print(f"TVK Site failed: status {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            keywords = ["கூட்டம்", "பேரணி", "meeting", "rally", "தடை", "traffic", "campaign", "strike", "மறியல்", "ஆர்ப்பாட்டம்", "அறிவிப்பு"]
            areas = ["Velachery", "Adyar", "Mylapore", "Saidapet", "Chepauk", "Triplicane", "T. Nagar", "Anna Nagar", "Central", "Egmore", "Guindy", "Purasawalkam", "Tambaram", "Chromepet", "Nungambakkam", "Royapettah"]
            chennai_indicators = ["chennai", "சென்ன", "velachery", "adyar", "mylapore", "saidapet", "chepauk", "triplicane", "t. nagar", "anna nagar", "central", "egmore", "guindy", "purasawalkam", "tambaram", "chromepet", "nungambakkam", "royapettah"]
            
            for l in links:
                text = l.get_text(strip=True)
                href = l["href"]
                
                # Check if it has a title length that looks like an event/announcement link
                if len(text) > 15 and (any(k in text for k in keywords) or "events" in href or "announcements" in href):
                    is_chennai = any(ind in text.lower() for ind in chennai_indicators) or "chennai" in href.lower()
                    if is_chennai:
                        found_area = next((a for a in areas if a.lower() in text.lower()), "Chennai")
                        
                        # Build absolute link
                        link = href
                        if href.startswith("/"):
                            link = f"https://tvkvijay.com{href}"
                            
                        event = {
                            "party_name": "TVK",
                            "party_color": "#ffd700",
                            "event_type": "rally" if "பேரணி" in text or "rally" in text.lower() or "campaign" in text.lower() else "meeting",
                            "title": text[:100],
                            "title_tamil": text[:100],
                            "location_name": found_area,
                            "location_tamil": found_area, 
                            "start_time": datetime.utcnow() + timedelta(hours=24),
                            "end_time": datetime.utcnow() + timedelta(hours=26),
                            "status": "unverified",
                            "source_url": link,
                            "source_name": "TVK Official Site"
                        }
                        
                        coords = await geocode_location(found_area)
                        if coords:
                            event["latitude"], event["longitude"] = coords
                            events.append(event)
    except Exception as e:
        print(f"TVK website scraping error: {e}")
        
    return events

async def scrape_all_party_sites() -> List[Dict]:
    print("Running Party Websites Scrapers...")
    results = await asyncio.gather(
        scrape_ntk_website(),
        scrape_aiadmk_website(),
        scrape_tvk_website(),
        return_exceptions=True
    )
    
    all_events = []
    for r in results:
        if isinstance(r, list):
            all_events.extend(r)
        elif isinstance(r, Exception):
            print(f"Sub-scraper failed with exception: {r}")
            
    return all_events

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    events = loop.run_until_complete(scrape_all_party_sites())
    print(f"Scraped {len(events)} events from Party Websites.")
