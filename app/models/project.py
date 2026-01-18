"""
Project Pydantic Models
Request/Response schemas for project management
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


# ============================================================================
# PROJECT BASE MODELS
# ============================================================================

class ProjectBase(BaseModel):
    """Base project model"""
    name: str
    description: Optional[str] = None
    project_manager_id: str
    principal_architect_id: Optional[str] = None
    team_lead_id: Optional[str] = None
    required_skills: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    project_type: str  # delivery, internal, research, maintenance, client_support
    priority: str = "medium"  # low, medium, high, critical
    status: str = "planning"  # planning, active, on_hold, completed, cancelled
    start_date: date
    deadline: Optional[date] = None
    risk_level: str = "low"  # low, medium, high


class ProjectCreate(ProjectBase):
    """Project creation request"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "QKREW Backend API",
                "description": "FastAPI backend for QKREW platform",
                "project_manager_id": "uuid",
                "principal_architect_id": "uuid",
                "team_lead_id": "uuid",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "tech_stack": ["Python", "FastAPI", "Supabase", "Docker"],
                "project_type": "delivery",
                "priority": "high",
                "status": "active",
                "start_date": "2026-01-10",
                "deadline": "2026-03-10",
                "risk_level": "medium"
            }
        }


class ProjectUpdate(BaseModel):
    """Project update request (all fields optional)"""
    name: Optional[str] = None
    description: Optional[str] = None
    project_manager_id: Optional[str] = None
    principal_architect_id: Optional[str] = None
    team_lead_id: Optional[str] = None
    required_skills: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    project_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[float] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    risk_level: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response"""
    id: str
    name: str
    description: Optional[str]
    project_manager_id: str
    principal_architect_id: Optional[str]
    team_lead_id: Optional[str]
    required_skills: Optional[List[str]]
    tech_stack: Optional[List[str]]
    project_type: str
    priority: str
    status: str
    progress: Optional[float]
    
    # Hours tracking
    total_hours: Optional[int]
    done_hours: Optional[int]
    
    # Team & tasks
    team_size: Optional[int]
    active_members: Optional[int]
    active_tasks: Optional[int]
    blocked_tasks: Optional[int]
    completed_tasks: Optional[int]
    
    # Risk & health
    risk_level: str
    health_indicators: Optional[dict]
    
    # Timeline
    start_date: date
    deadline: Optional[date]
    
    # Budget
    budget: Optional[dict]
    
    # Audit
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_id: Optional[str]


class ProjectListResponse(BaseModel):
    """Paginated project list"""
    projects: List[ProjectResponse]
    total: int
    page: int
    limit: int


# ============================================================================
# PROJECT MEMBER MODELS
# ============================================================================

class ProjectMemberAdd(BaseModel):
    """Add member to project"""
    user_id: str
    role: Optional[str] = None
    allocation_percent: int = 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "uuid",
                "role": "Backend Developer",
                "allocation_percent": 100
            }
        }


class ProjectMemberUpdate(BaseModel):
    """Update project member"""
    role: Optional[str] = None
    allocation_percent: Optional[int] = None


class ProjectMemberResponse(BaseModel):
    """Project member response"""
    id: str
    project_id: str
    user_id: str
    role: Optional[str]
    allocation_percent: int
    joined_at: datetime


# ============================================================================
# PROJECT ANALYTICS MODELS
# ============================================================================

class ProjectAnalytics(BaseModel):
    """Project analytics response"""
    project_id: str
    project_name: str
    
    # Progress metrics
    overall_progress: float
    tasks_completed: int
    tasks_total: int
    tasks_blocked: int
    
    # Time metrics
    days_elapsed: int
    days_remaining: int
    days_total: int
    
    # Team metrics
    team_size: int
    team_utilization: float
    
    # Risk assessment
    risk_level: str
    risk_factors: List[str]
    
    # Health indicators
    health_score: float
    health_status: str  # healthy, warning, critical
