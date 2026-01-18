from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from supabase import Client
from app.core.dependencies import get_current_active_user
from app.database import get_db

router = APIRouter()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SimulateStaffingRequest(BaseModel):
    project_id: str
    employee_ids: List[str]

class EmployeeImpact(BaseModel):
    id: str
    name: str
    experience_years: int
    skills: List[str]
    current_workload_percent: float
    available_capacity: float
    skill_match_score: float
    productivity_score: float

class SimulationResult(BaseModel):
    current_state: dict
    projected_state: dict
    impact: dict
    employee_contributions: List[EmployeeImpact]

# ============================================================================
# ESP SIMULATION ENDPOINT
# ============================================================================

@router.post("/simulate", response_model=SimulationResult)
async def simulate_staffing(
    request: SimulateStaffingRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Simulate the impact of adding employees to a project.
    Calculates based on:
    - Employee experience
    - Skill matching
    - Current workload
    - Work capacity
    """
    
    # 1. Get project details
    project_response = db.table("projects").select(
        "*, project_members(*, users(*))"
    ).eq("id", request.project_id).single().execute()
    
    if not project_response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = project_response.data
    
    # 2. Get current team members
    current_members = project.get("project_members", [])
    current_team_size = len(current_members)
    
    # 3. Calculate current state
    current_skills = []
    current_total_experience = 0
    current_total_workload = 0
    
    for member in current_members:
        user = member.get("users", {})
        if user:
            current_skills.extend(user.get("skills", []))
            current_total_experience += user.get("experience_years", 0)
            current_total_workload += user.get("current_workload_percent", 0)
    
    current_skills = list(set(current_skills))  # Unique skills
    current_avg_experience = current_total_experience / max(current_team_size, 1)
    current_avg_workload = current_total_workload / max(current_team_size, 1)
    
    # Calculate current skill coverage
    required_skills = project.get("required_skills", [])
    current_skill_coverage = 0
    if required_skills:
        matched_skills = [s for s in required_skills if s in current_skills]
        current_skill_coverage = (len(matched_skills) / len(required_skills)) * 100
    else:
        current_skill_coverage = 100
    
    # 4. Get proposed employees
    employee_response = db.table("users").select("*").in_(
        "id", request.employee_ids
    ).execute()
    
    if not employee_response.data:
        raise HTTPException(status_code=404, detail="Employees not found")
    
    proposed_employees = employee_response.data
    
    # 5. Calculate impact for each employee
    employee_contributions = []
    new_skills = []
    new_total_experience = current_total_experience
    new_total_capacity = 0
    
    
    for emp in proposed_employees:
        emp_skills = emp.get("skills") or []  # Handle None case
        emp_experience = emp.get("experience_years") or 0
        emp_workload = emp.get("current_workload_percent") or 0
        emp_capacity = emp.get("weekly_capacity") or 40
        
        # Calculate available capacity
        available_capacity = 100 - emp_workload
        
        # Calculate skill match score
        if required_skills and len(required_skills) > 0:
            matched = [s for s in required_skills if s in emp_skills]
            skill_match_score = (len(matched) / len(required_skills)) * 100
        else:
            skill_match_score = 50  # Default if no required skills
        
        # Calculate productivity score (based on experience and availability)
        experience_factor = min(emp_experience / 10, 1.0)  # Max at 10 years
        availability_factor = available_capacity / 100
        productivity_score = (experience_factor * 0.5 + availability_factor * 0.5) * 100

        
        employee_contributions.append(EmployeeImpact(
            id=emp["id"],
            name=emp["name"],
            experience_years=emp_experience,
            skills=emp_skills,
            current_workload_percent=emp_workload,
            available_capacity=available_capacity,
            skill_match_score=skill_match_score,
            productivity_score=productivity_score
        ))
        
        # Accumulate new skills
        new_skills.extend(emp_skills)
        new_total_experience += emp_experience
        new_total_capacity += available_capacity
    
    # 6. Calculate projected state
    new_team_size = current_team_size + len(proposed_employees)
    new_skills = list(set(current_skills + new_skills))
    new_avg_experience = new_total_experience / new_team_size
    
    # Calculate new skill coverage
    if required_skills:
        matched_skills = [s for s in required_skills if s in new_skills]
        new_skill_coverage = (len(matched_skills) / len(required_skills)) * 100
    else:
        new_skill_coverage = 100
    
    # Calculate productivity boost
    avg_productivity = sum(e.productivity_score for e in employee_contributions) / len(employee_contributions)
    skill_coverage_boost = new_skill_coverage - current_skill_coverage
    
    # Estimate progress boost (based on team size, skills, and productivity)
    team_size_factor = (new_team_size - current_team_size) / max(current_team_size, 1)
    skill_factor = skill_coverage_boost / 100
    productivity_factor = avg_productivity / 100
    
    progress_boost = min(40, (team_size_factor * 15) + (skill_factor * 20) + (productivity_factor * 10))
    
    current_progress = project.get("progress", 0)
    new_progress = min(100, current_progress + progress_boost)
    
    # Calculate timeline impact
    current_velocity = current_team_size * (current_skill_coverage / 100) * (current_avg_experience / 10)
    new_velocity = new_team_size * (new_skill_coverage / 100) * (new_avg_experience / 10)
    
    if current_velocity > 0:
        velocity_increase = ((new_velocity - current_velocity) / current_velocity) * 100
    else:
        velocity_increase = 100
    
    # Estimate months saved (rough calculation)
    remaining_work = 100 - current_progress
    if remaining_work > 0 and current_velocity > 0:
        current_months = (remaining_work / current_velocity) * 2  # Rough estimate
        new_months = (remaining_work / new_velocity) * 2
        months_saved = max(0, current_months - new_months)
    else:
        current_months = 6
        new_months = 4
        months_saved = 2
    
    # Calculate workload distribution
    new_avg_workload = (current_total_workload + sum(e.current_workload_percent for e in employee_contributions)) / new_team_size
    
    # 7. Build response
    return SimulationResult(
        current_state={
            "team_size": current_team_size,
            "progress": current_progress,
            "skill_coverage": current_skill_coverage,
            "avg_experience": current_avg_experience,
            "avg_workload": current_avg_workload,
            "skills": current_skills,
            "estimated_months": round(current_months, 1)
        },
        projected_state={
            "team_size": new_team_size,
            "progress": new_progress,
            "skill_coverage": new_skill_coverage,
            "avg_experience": new_avg_experience,
            "avg_workload": new_avg_workload,
            "skills": new_skills,
            "estimated_months": round(new_months, 1)
        },
        impact={
            "progress_boost": round(progress_boost, 1),
            "skill_coverage_boost": round(skill_coverage_boost, 1),
            "velocity_increase": round(velocity_increase, 1),
            "months_saved": round(months_saved, 1),
            "new_skills_added": [s for s in new_skills if s not in current_skills],
            "avg_productivity": round(avg_productivity, 1),
            "workload_reduction": round(current_avg_workload - new_avg_workload, 1)
        },
        employee_contributions=employee_contributions
    )


# ============================================================================
# GET AVAILABLE EMPLOYEES FOR PROJECT
# ============================================================================

@router.get("/projects/{project_id}/available-employees")
async def get_available_employees(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get employees available to add to a project.
    Filters out employees already on the project.
    Returns with workload and skill information.
    """
    
    # Get current project members
    project_response = db.table("project_members").select(
        "user_id"
    ).eq("project_id", project_id).execute()
    
    current_member_ids = [m["user_id"] for m in project_response.data]
    
    # Get all active users not on the project
    users_response = db.table("users").select(
        "id, name, email, hierarchy_level, skills, experience_years, "
        "current_workload_percent, weekly_capacity, department"
    ).eq("status", "active").execute()
    
    available_employees = [
        {
            **user,
            "available_capacity": 100 - user.get("current_workload_percent", 0)
        }
        for user in users_response.data
        if user["id"] not in current_member_ids
    ]
    
    return {
        "employees": available_employees,
        "total": len(available_employees)
    }
