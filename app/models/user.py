"""
User Pydantic Models
Request/Response schemas for user management
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============================================================================
# USER BASE MODELS
# ============================================================================

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    name: str
    role: str  # admin, project_manager, technical_lead, hr, employee
    hierarchy_level: str  # L1-L13
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    weekly_capacity: int = 40
    manager_id: Optional[str] = None
    tech_team_id: Optional[str] = None
    status: str = "active"  # active, on_leave, notice_period, exited


class UserCreate(UserBase):
    """User creation request"""
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@qkrew.com",
                "password": "password123",
                "name": "John Doe",
                "role": "employee",
                "hierarchy_level": "L9",
                "department": "Engineering",
                "skills": ["Python", "React", "SQL"],
                "experience_years": 3,
                "weekly_capacity": 40,
                "manager_id": None,
                "tech_team_id": None,
                "status": "active"
            }
        }


class UserUpdate(BaseModel):
    """User update request (all fields optional)"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    hierarchy_level: Optional[str] = None
    department: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    weekly_capacity: Optional[int] = None
    manager_id: Optional[str] = None
    tech_team_id: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None  # Optional password change


class UserResponse(BaseModel):
    """User response (without password)"""
    id: str
    email: str
    name: str
    role: str
    hierarchy_level: str
    department: Optional[str]
    skills: Optional[List[str]]
    experience_years: Optional[int]
    weekly_capacity: int
    manager_id: Optional[str]
    tech_team_id: Optional[str]
    status: str
    avatar_url: Optional[str]
    
    # Workload tracking
    assignment_status: Optional[str]
    current_workload_percent: Optional[int]
    active_project_count: Optional[int]
    active_task_count: Optional[int]
    has_blocking_incident: Optional[bool]
    
    # Audit
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "uuid",
                "email": "user@qkrew.com",
                "name": "John Doe",
                "role": "employee",
                "hierarchy_level": "L9",
                "department": "Engineering",
                "skills": ["Python", "React", "SQL"],
                "experience_years": 3,
                "weekly_capacity": 40,
                "manager_id": None,
                "tech_team_id": None,
                "status": "active",
                "avatar_url": None,
                "assignment_status": "assigned",
                "current_workload_percent": 75,
                "active_project_count": 2,
                "active_task_count": 5,
                "has_blocking_incident": False,
                "created_at": "2026-01-10T00:00:00",
                "updated_at": "2026-01-10T00:00:00"
            }
        }


class UserListResponse(BaseModel):
    """Paginated user list response"""
    users: List[UserResponse]
    total: int
    page: int
    limit: int
