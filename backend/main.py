from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List

from .database import create_db_and_tables, get_session
from .models import Party, Event

from .routes import events, parties

import asyncio
from .scrapers.scheduler import scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
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
