from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List

from .database import create_db_and_tables, get_session, engine
from .models import Party, Event

from .routes import events, parties

import asyncio
from .scrapers.scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Auto-seed parties if database is empty (important for Render)
    with Session(engine) as session:
        existing_parties = session.exec(select(Party)).first()
        if not existing_parties:
            parties_data = [
                {"name": "DMK", "name_tamil": "திமுக", "color": "#ff0000", "official_url": "https://dmk.in"},
                {"name": "AIADMK", "name_tamil": "அதிமுக", "color": "#008000", "official_url": "https://aiadmk.org.in"},
                {"name": "BJP", "name_tamil": "பாஜக", "color": "#ff9933", "official_url": "https://www.bjp.org"},
                {"name": "Congress", "name_tamil": "காங்கிரஸ்", "color": "#0000ff", "official_url": "https://www.inc.in"},
                {"name": "TVK", "name_tamil": "தவெக", "color": "#ffd700", "official_url": "https://twitter.com/tvkvijayhq"},
                {"name": "NTK", "name_tamil": "நாதக", "color": "#ffa500", "official_url": "https://www.naamtamilar.org"},
                {"name": "MDMK", "name_tamil": "மதிமுக", "color": "#ff0000", "official_url": "https://mdmk.org.in"},
                {"name": "VCK", "name_tamil": "விசிக", "color": "#0000ff", "official_url": "https://vck.in"}
            ]
            for p_data in parties_data:
                session.add(Party(**p_data))
            session.commit()
            print("Auto-seeded parties on startup.")

    # Start scheduler in background
    asyncio.create_task(scheduler())
    yield

app = FastAPI(title="Namma Chennai Tracker API", lifespan=lifespan)

app.include_router(events.router)
app.include_router(parties.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ticker")
async def get_ticker(session: Session = Depends(get_session)):
    # Placeholder for ticker logic
    return {"message": "Safe travels! No major disruptions reported right now."}

@app.get("/")
async def root():
    return {"message": "Welcome to Namma Chennai Tracker API"}
