from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine

class Party(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    name_tamil: str
    color: str
    logo_url: Optional[str] = None
    official_url: Optional[str] = None
    social_urls: Optional[str] = None # JSON string or comma-separated

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    party_name: str
    party_color: str
    event_type: str        # rally / meeting / strike
    title: str
    title_tamil: str
    location_name: str
    location_tamil: str
    latitude: float
    longitude: float
    start_time: datetime
    end_time: datetime
    status: str            # confirmed / unverified
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
