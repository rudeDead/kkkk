"""
Software Request, Notice Period, Business Trip Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# SOFTWARE REQUEST MODELS
class SoftwareRequestCreate(BaseModel):
    """Software request creation"""
    software_name: str
    purpose: str
    estimated_cost: Optional[float] = None
    urgency: str = "medium"  # low, medium, high
    
    class Config:
        json_schema_extra = {
            "example": {
                "software_name": "JetBrains IntelliJ IDEA",
                "purpose": "Java development",
                "estimated_cost": 499.00,
                "urgency": "medium"
            }
        }


class SoftwareRequestResponse(BaseModel):
    """Software request response"""
    id: str
    software_name: str
    purpose: str
    estimated_cost: Optional[float]
    urgency: str
    status: str  # pending, approved, rejected
    requested_by_id: str
    decided_by_id: Optional[str]
    decision_notes: Optional[str]
    created_at: Optional[datetime]


# NOTICE PERIOD MODELS
class NoticePeriodCreate(BaseModel):
    """Notice period creation"""
    employee_id: str
    last_working_day: date
    reason: Optional[str] = None
    handover_notes: Optional[str] = None


class NoticePeriodResponse(BaseModel):
    """Notice period response"""
    id: str
    employee_id: str
    last_working_day: date
    reason: Optional[str]
    handover_notes: Optional[str]
    status: str  # active, completed
    created_at: Optional[datetime]


# BUSINESS TRIP MODELS
class BusinessTripCreate(BaseModel):
    """Business trip creation"""
    destination: str
    purpose: str
    start_date: date
    end_date: date
    estimated_cost: Optional[float] = None


class BusinessTripResponse(BaseModel):
    """Business trip response"""
    id: str
    employee_id: str
    destination: str
    purpose: str
    start_date: date
    end_date: date
    estimated_cost: Optional[float]
    status: str  # pending, approved, rejected, completed
    approved_by_id: Optional[str]
    created_at: Optional[datetime]
