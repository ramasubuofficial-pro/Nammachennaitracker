from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Event

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.get("/", response_model=List[Event])
def read_events(session: Session = Depends(get_session)):
    events = session.exec(select(Event)).all()
    return events

@router.get("/today", response_model=List[Event])
def read_today_events(session: Session = Depends(get_session)):
    # In a real app, query by start_time
    events = session.exec(select(Event)).all()
    return events

@router.get("/{id}", response_model=Event)
def read_event(id: int, session: Session = Depends(get_session)):
    event = session.get(Event, id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
