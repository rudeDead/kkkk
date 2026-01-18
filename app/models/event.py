"""
Event Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class EventBase(BaseModel):
    """Base event model"""
    name: str
    description: Optional[str] = None
    event_type: str  # team_building, training, conference, celebration, meeting
    event_date: date
    location: Optional[str] = None
    max_participants: Optional[int] = None


class EventCreate(EventBase):
    """Event creation"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Annual Team Building",
                "description": "Company-wide team building event",
                "event_type": "team_building",
                "event_date": "2026-02-15",
                "location": "Conference Hall A",
                "max_participants": 100
            }
        }


class EventUpdate(BaseModel):
    """Event update"""
    name: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    event_date: Optional[date] = None
    location: Optional[str] = None
    max_participants: Optional[int] = None


class EventResponse(BaseModel):
    """Event response"""
    id: str
    name: str
    description: Optional[str]
    event_type: str
    start_datetime: datetime
    end_datetime: datetime
    location: Optional[str]
    max_participants: Optional[int]
    current_participants: Optional[int] = 0
    organized_by_id: str
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True
