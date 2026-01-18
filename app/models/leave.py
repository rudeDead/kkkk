"""
Leave Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class LeaveBase(BaseModel):
    """Base leave model"""
    leave_type: str  # casual, sick, earned, maternity, paternity, unpaid
    start_date: date
    end_date: date
    days: int
    reason: Optional[str] = None


class LeaveCreate(LeaveBase):
    """Leave creation"""
    class Config:
        json_schema_extra = {
            "example": {
                "leave_type": "casual",
                "start_date": "2026-01-15",
                "end_date": "2026-01-17",
                "days": 3,
                "reason": "Personal work"
            }
        }


class LeaveUpdate(BaseModel):
    """Leave update"""
    status: Optional[str] = None  # pending_hr_review, forwarded_to_team_lead, approved, rejected, cancelled
    decision_notes: Optional[str] = None
    alternate_assigned_id: Optional[str] = None


class LeaveResponse(BaseModel):
    """Leave response"""
    id: str
    employee_id: str
    leave_type: str
    start_date: date
    end_date: date
    days: int
    reason: Optional[str]
    status: str
    conflict_severity: Optional[str]
    conflict_details: Optional[dict]
    alternate_assigned_id: Optional[str]
    hr_reviewed_by: Optional[str]
    hr_reviewed_at: Optional[datetime]
    decided_by_id: Optional[str]
    decision_notes: Optional[str]
    created_at: Optional[datetime]
    approved_at: Optional[datetime]
