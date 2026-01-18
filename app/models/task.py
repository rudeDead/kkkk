"""
Task Pydantic Models
"""

from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TaskBase(BaseModel):
    """Base task model"""
    title: str
    description: Optional[str] = None
    project_id: str
    assignee_id: Optional[str] = None
    priority: str = "medium"  # low, medium, high, critical
    status: str = "not_started"  # not_started, in_progress, blocked, completed
    estimated_hours: Optional[int] = None
    due_date: Optional[date] = None
    is_learning_task: bool = False
    mentor_id: Optional[str] = None


class TaskCreate(TaskBase):
    """Task creation"""
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implement authentication API",
                "description": "Build JWT-based auth with FastAPI",
                "project_id": "uuid",
                "assignee_id": "uuid",
                "priority": "high",
                "status": "not_started",
                "estimated_hours": 16,
                "due_date": "2026-01-15",
                "is_learning_task": False
            }
        }


class TaskUpdate(BaseModel):
    """Task update"""
    title: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    blocked_reason: Optional[str] = None
    due_date: Optional[date] = None
    is_learning_task: Optional[bool] = None
    mentor_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response"""
    id: str
    title: str
    description: Optional[str]
    project_id: str
    assignee_id: Optional[str]
    priority: str
    status: str
    progress: Optional[int]
    estimated_hours: Optional[int]
    actual_hours: Optional[int]
    blocked_reason: Optional[str]
    is_learning_task: bool
    mentor_id: Optional[str]
    due_date: Optional[date]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
