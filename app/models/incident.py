"""
Incident Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class IncidentBase(BaseModel):
    """Base incident model"""
    title: str
    description: Optional[str] = None
    project_id: str
    severity: str  # low, medium, high, critical
    assigned_to_id: Optional[str] = None


class IncidentCreate(IncidentBase):
    """Incident creation"""
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Production API Down",
                "description": "Users cannot access the API",
                "project_id": "uuid",
                "severity": "critical",
                "assigned_to_id": "uuid"
            }
        }


class IncidentUpdate(BaseModel):
    """Incident update"""
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_to_id: Optional[str] = None
    resolution_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    """Incident response"""
    id: str
    title: str
    description: Optional[str]
    project_id: str
    severity: str
    status: str  # open, in_progress, resolved, closed
    assigned_to_id: Optional[str]
    reported_by_id: str
    assigned_by_id: Optional[str]
    resolution_notes: Optional[str]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]

