"""
Team Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TeamBase(BaseModel):
    """Base team model"""
    name: str
    description: Optional[str] = None
    department: Optional[str] = None
    team_lead_id: Optional[str] = None


class TeamCreate(TeamBase):
    """Team creation"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Backend Team",
                "description": "Backend development team",
                "department": "Engineering",
                "team_lead_id": "uuid"
            }
        }


class TeamUpdate(BaseModel):
    """Team update"""
    name: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    team_lead_id: Optional[str] = None


class TeamResponse(BaseModel):
    """Team response"""
    id: str
    name: str
    description: Optional[str]
    department: Optional[str]
    team_lead_id: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class TeamMemberAdd(BaseModel):
    """Add member to team"""
    user_id: str
