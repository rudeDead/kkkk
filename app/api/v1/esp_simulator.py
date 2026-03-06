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
    matching_project_skills: List[str] = []
    missing_project_skills: List[str] = []

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
    
    # ── Skill normalization helper ─────────────────────────────────────────
    def norm(s: str) -> str:
        """Lowercase + strip so 'Team Leadership' == 'team leadership'."""
        return s.lower().strip().replace("-", " ").replace("_", " ")

    required_skills: list = project.get("required_skills") or []
    req_norm = [norm(s) for s in required_skills]   # normalized required list

    # ── 2. Current team ────────────────────────────────────────────────────
    current_members = project.get("project_members", [])
    current_team_size = len(current_members)

    current_skills_raw: list = []
    current_total_experience = 0
    current_total_workload = 0

    for member in current_members:
        user = member.get("users", {})
        if user:
            current_skills_raw.extend(user.get("skills") or [])
            current_total_experience += user.get("experience_years") or 0
            current_total_workload  += user.get("current_workload_percent") or 0

    current_skills_raw = list(set(current_skills_raw))
    cur_norm = [norm(s) for s in current_skills_raw]

    current_avg_experience = current_total_experience / max(current_team_size, 1)
    current_avg_workload   = current_total_workload   / max(current_team_size, 1)

    # Skill coverage (normalised comparison)
    if req_norm:
        cur_matched = [s for s in req_norm if s in cur_norm]
        current_skill_coverage = (len(cur_matched) / len(req_norm)) * 100
    else:
        current_skill_coverage = 100.0

    # ── 3. Proposed employees ──────────────────────────────────────────────
    employee_response = db.table("users").select("*").in_(
        "id", request.employee_ids
    ).execute()

    if not employee_response.data:
        raise HTTPException(status_code=404, detail="Employees not found")

    proposed_employees = employee_response.data

    # ── 4. Per-employee impact + skill gap ────────────────────────────────
    employee_contributions = []
    new_skills_raw: list = list(current_skills_raw)
    new_total_experience = current_total_experience

    for emp in proposed_employees:
        emp_skills_raw  = emp.get("skills") or []
        emp_experience  = emp.get("experience_years") or 0
        emp_workload    = emp.get("current_workload_percent") or 0
        available_capacity = max(0, 100 - emp_workload)
        emp_norm = [norm(s) for s in emp_skills_raw]

        # Skill match vs project requirements (normalised)
        if req_norm:
            matched_req = [required_skills[i] for i, s in enumerate(req_norm) if s in emp_norm]
            missing_req = [required_skills[i] for i, s in enumerate(req_norm) if s not in emp_norm]
            skill_match_score = (len(matched_req) / len(req_norm)) * 100
        else:
            matched_req = []
            missing_req = []
            skill_match_score = 50.0

        # Productivity: experience (50%) + availability (50%)
        exp_factor  = min(emp_experience / 10.0, 1.0)
        avail_factor = available_capacity / 100.0
        productivity_score = (exp_factor * 0.5 + avail_factor * 0.5) * 100

        employee_contributions.append(EmployeeImpact(
            id=emp["id"],
            name=emp["name"],
            experience_years=emp_experience,
            skills=emp_skills_raw,
            current_workload_percent=emp_workload,
            available_capacity=available_capacity,
            skill_match_score=round(skill_match_score, 1),
            productivity_score=round(productivity_score, 1),
            matching_project_skills=matched_req,
            missing_project_skills=missing_req,
        ))

        new_skills_raw.extend(emp_skills_raw)
        new_total_experience += emp_experience

    # ── 5. Projected state ─────────────────────────────────────────────────
    new_team_size  = current_team_size + len(proposed_employees)
    new_skills_raw = list(set(new_skills_raw))
    new_norm       = [norm(s) for s in new_skills_raw]
    new_avg_experience = new_total_experience / new_team_size

    if req_norm:
        new_matched = [s for s in req_norm if s in new_norm]
        new_skill_coverage = (len(new_matched) / len(req_norm)) * 100
    else:
        new_skill_coverage = 100.0

    # Remaining skill gaps after adding new team
    skill_gaps_remaining = [required_skills[i] for i, s in enumerate(req_norm) if s not in new_norm]

    avg_productivity    = sum(e.productivity_score for e in employee_contributions) / len(employee_contributions)
    skill_coverage_boost = new_skill_coverage - current_skill_coverage

    # ── 6. Velocity model (floors prevent collapse to zero) ────────────────
    # Velocity = team_size × skill_factor × experience_factor
    # SKILL_FLOOR: even a fully-mismatched team still executes at 20% efficiency
    # EXP_FLOOR:   even juniors contribute at 30% of a 10-yr senior
    SKILL_FLOOR = 0.20
    EXP_FLOOR   = 0.30

    cur_skill_f = max(current_skill_coverage / 100.0, SKILL_FLOOR)
    cur_exp_f   = max(current_avg_experience  / 10.0,  EXP_FLOOR)
    cur_velocity = max(current_team_size, 1) * cur_skill_f * cur_exp_f

    new_skill_f = max(new_skill_coverage / 100.0, SKILL_FLOOR)
    new_exp_f   = max(new_avg_experience  / 10.0,  EXP_FLOOR)
    new_velocity = new_team_size * new_skill_f * new_exp_f

    # Guarantee new_velocity > cur_velocity (more people → always faster)
    new_velocity = max(new_velocity, cur_velocity * 1.05)

    velocity_increase = round(((new_velocity - cur_velocity) / cur_velocity) * 100, 1)

    # ── 7. Timeline ────────────────────────────────────────────────────────
    current_progress = project.get("progress") or 0
    remaining_work   = max(0, 100 - current_progress)
    MAX_MONTHS = 24
    BASE = 12.0   # a single-unit velocity completes 100% work in 12 months

    if remaining_work > 0:
        raw_cur = (remaining_work / 100.0) * BASE / cur_velocity
        raw_new = (remaining_work / 100.0) * BASE / new_velocity
        current_months = min(round(raw_cur, 1), MAX_MONTHS)
        # new_months must always be strictly less than current_months
        new_months = min(round(raw_new, 1), current_months - 0.5)
        new_months = max(new_months, 0.5)          # at least 2 weeks
        months_saved = round(current_months - new_months, 1)
    else:
        current_months, new_months, months_saved = 0.0, 0.0, 0.0

    # ── 8. Progress boost ──────────────────────────────────────────────────
    team_size_factor  = (new_team_size - current_team_size) / max(current_team_size, 1)
    skill_factor      = skill_coverage_boost / 100.0
    productivity_factor = avg_productivity / 100.0
    progress_boost = min(40.0, (team_size_factor * 15) + (skill_factor * 20) + (productivity_factor * 10))
    new_progress   = min(100, current_progress + progress_boost)

    # ── 9. Workload ────────────────────────────────────────────────────────
    new_avg_workload = (
        current_total_workload +
        sum(e.current_workload_percent for e in employee_contributions)
    ) / new_team_size

    # ── 10. Build response ─────────────────────────────────────────────────
    return SimulationResult(
        current_state={
            "team_size":        current_team_size,
            "progress":         current_progress,
            "skill_coverage":   round(current_skill_coverage, 1),
            "avg_experience":   round(current_avg_experience, 1),
            "avg_workload":     round(current_avg_workload, 1),
            "skills":           current_skills_raw,
            "estimated_months": current_months,
        },
        projected_state={
            "team_size":        new_team_size,
            "progress":         round(new_progress, 1),
            "skill_coverage":   round(new_skill_coverage, 1),
            "avg_experience":   round(new_avg_experience, 1),
            "avg_workload":     round(new_avg_workload, 1),
            "skills":           new_skills_raw,
            "estimated_months": new_months,
        },
        impact={
            "progress_boost":       round(progress_boost, 1),
            "skill_coverage_boost": round(skill_coverage_boost, 1),
            "velocity_increase":    velocity_increase,
            "months_saved":         months_saved,
            "new_skills_added":     [s for s in new_skills_raw if norm(s) not in cur_norm],
            "avg_productivity":     round(avg_productivity, 1),
            "workload_reduction":   round(current_avg_workload - new_avg_workload, 1),
            "skill_gaps_remaining": skill_gaps_remaining,
            "required_skills":      required_skills,
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
