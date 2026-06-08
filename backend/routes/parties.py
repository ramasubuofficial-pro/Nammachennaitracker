from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Party

router = APIRouter(prefix="/api/parties", tags=["Parties"])

from ..models import Party, Event

from datetime import datetime

@router.get("/")
def read_parties(session: Session = Depends(get_session)):
    now = datetime.utcnow()
    parties = session.exec(select(Party)).all()
    events = session.exec(select(Event).where(Event.end_time >= now)).all()
    
    party_list = []
    for p in parties:
        # Simple count for active/upcoming events mapped to the party
        count = len([e for e in events if e.party_name == p.name])
        p_data = p.dict()
        p_data["event_count"] = count
        party_list.append(p_data)
        
    return party_list

@router.get("/{id}", response_model=Party)
def read_party(id: int, session: Session = Depends(get_session)):
    party = session.get(Party, id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party
