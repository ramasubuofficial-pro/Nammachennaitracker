import asyncio
from sqlmodel import Session, select
from datetime import datetime
from ..database import engine
from ..models import Event, Party
from .dinamalar import scrape_dinamalar
from .thehindu import scrape_thehindu_tamil
from .party_sites import scrape_all_party_sites
from .youtube_rss import scrape_youtube_rss
from .twitter_x import scrape_twitter_x

async def run_scrapers():
    print(f"[{datetime.now()}] Starting scraping tasks...")
    
    # Run scrapers
    results_dinamalar = await scrape_dinamalar()
    results_thehindu = await scrape_thehindu_tamil()
    results_party_sites = await scrape_all_party_sites()
    results_youtube = await scrape_youtube_rss()
    results_twitter = await scrape_twitter_x()
    
    all_results = results_dinamalar + results_thehindu + results_party_sites + results_youtube + results_twitter
    
    with Session(engine) as session:
        for data in all_results:
            # Check if event with title already exists to avoid duplicates
            existing = session.exec(select(Event).where(Event.title == data["title"])).first()
            if not existing:
                # Assign actual party color from Party table (simplified)
                party = session.exec(select(Party).where(Party.name == data["party_name"])).first()
                if party:
                    data["party_color"] = party.color
                
                event = Event(**data)
                session.add(event)
        
        session.commit()
    
    print(f"[{datetime.now()}] Finished scraping. Added {len(all_results)} potential new events.")

async def scheduler():
    while True:
        try:
            await run_scrapers()
        except Exception as e:
            print(f"Scheduler error: {e}")
        
        # Run every 60 minutes
        await asyncio.sleep(3600)
