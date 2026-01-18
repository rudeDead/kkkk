"""
ESP Manager API - Extra Staffing Projection
Simplified skill-matching based system using QKREW database schema
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime
from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.core.rbac import is_admin, Roles
from pydantic import BaseModel

esp_manager_router = APIRouter()


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class L7RecommendationCreate(BaseModel):
    skill: str
    positions_needed: int
    suggested_level: str  # e.g., "L9-L10"
    justification: str
    priority: str = "medium"  # low, medium, high, critical


class ESPPackageCreate(BaseModel):
    project_id: str
    team_id: str
    required_headcount: int
    duration_months: int
    justification: str
    recommendations: List[L7RecommendationCreate]


class L6ReviewRequest(BaseModel):
    decision: str  # approved, rejected, needs_modification
    technical_notes: Optional[str] = None
    capacity_notes: Optional[str] = None
    risk_notes: Optional[str] = None
    additional_positions: Optional[List[Dict]] = None


class PMDecisionRequest(BaseModel):
    final_decision: str  # approved, rejected, modified, deferred
    approved_positions: Optional[List[Dict]] = None
    rejected_positions: Optional[List[Dict]] = None
    selected_alternatives: Optional[List[Dict]] = None
    business_justification: Optional[str] = None
    decision_notes: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS - SKILL MATCHING ENGINE
# ============================================================================

def calculate_skill_coverage(project_id: str, db: Client) -> Dict:
    """
    Calculate skill coverage for a project
    Returns: {skill: {required: bool, coverage_percent: float, team_members: []}}
    """
    # Get project required skills
    project = db.table("projects").select("required_skills, name").eq("id", project_id).single().execute()
    
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    required_skills = project.data.get("required_skills", [])
    
    # Get project members with their skills
    members_response = db.table("project_members").select(
        "user_id, users!inner(id, name, skills, hierarchy_level, current_workload_percent)"
    ).eq("project_id", project_id).execute()
    
    members = members_response.data or []
    
    # Calculate coverage for each required skill
    skill_coverage = {}
    
    for skill in required_skills:
        # Find team members with this skill
        skilled_members = []
        for member in members:
            user = member.get("users", {})
            user_skills = user.get("skills", [])
            
            if skill in user_skills:
                skilled_members.append({
                    "id": user.get("id"),
                    "name": user.get("name"),
                    "level": user.get("hierarchy_level"),
                    "workload": user.get("current_workload_percent", 0)
                })
        
        # Calculate coverage percentage
        # If 0 members: 0%, if 1 member: 50%, if 2+: 100%
        if len(skilled_members) == 0:
            coverage = 0
        elif len(skilled_members) == 1:
            # Check if they're overloaded
            if skilled_members[0]["workload"] > 85:
                coverage = 25  # Critically low
            else:
                coverage = 50  # Single point of failure
        else:
            coverage = 100
        
        skill_coverage[skill] = {
            "required": True,
            "coverage_percent": coverage,
            "team_members": skilled_members,
            "gap": len(skilled_members) == 0 or (len(skilled_members) == 1 and skilled_members[0]["workload"] > 85)
        }
    
    return {
        "project_name": project.data.get("name"),
        "skill_coverage": skill_coverage,
        "overall_coverage": sum(s["coverage_percent"] for s in skill_coverage.values()) / len(skill_coverage) if skill_coverage else 100
    }


def find_internal_candidates(skill: str, level_range: str, exclude_project_id: str, db: Client) -> List[Dict]:
    """
    Find internal employees who have the skill and are not on the project
    """
    # Parse level range (e.g., "L9-L10" -> ["L9", "L10"])
    if "-" in level_range:
        levels = level_range.split("-")
        level_filter = levels  # Will check if user level is in this range
    else:
        level_filter = [level_range]
    
    # Get all users with the skill
    users_response = db.table("users").select(
        "id, name, skills, hierarchy_level, current_workload_percent, department"
    ).contains("skills", [skill]).eq("status", "active").execute()
    
    candidates = []
    
    for user in users_response.data or []:
        # Check if user is in the right level range
        user_level = user.get("hierarchy_level")
        if user_level not in level_filter:
            continue
        
        # Check if user is already on this project
        membership = db.table("project_members").select("id").eq(
            "user_id", user["id"]
        ).eq("project_id", exclude_project_id).execute()
        
        if membership.data:
            continue  # Already on project
        
        # Calculate availability
        workload = user.get("current_workload_percent", 0)
        availability = 100 - workload
        
        if availability > 20:  # At least 20% available
            candidates.append({
                "id": user["id"],
                "name": user["name"],
                "level": user_level,
                "current_workload": workload,
                "availability_percent": availability,
                "department": user.get("department"),
                "match_score": availability  # Simple score based on availability
            })
    
    # Sort by availability (highest first)
    candidates.sort(key=lambda x: x["availability_percent"], reverse=True)
    
    return candidates


def generate_esp_simulation(project_id: str, team_id: str, db: Client) -> Dict:
    """
    Generate ESP simulation with skill gap analysis and recommendations
    """
    # Get skill coverage
    coverage_data = calculate_skill_coverage(project_id, db)
    skill_coverage = coverage_data["skill_coverage"]
    
    # Identify skill gaps
    skill_gaps = {}
    system_recommendations = []
    
    for skill, data in skill_coverage.items():
        if data["gap"]:
            # Determine recommended level based on project complexity
            project = db.table("projects").select("priority").eq("id", project_id).single().execute()
            priority = project.data.get("priority", "medium") if project.data else "medium"
            
            if priority in ["critical", "high"]:
                recommended_level = "L8-L9"
            else:
                recommended_level = "L9-L10"
            
            # Calculate positions needed
            if data["coverage_percent"] == 0:
                positions = 2  # No coverage - need 2 people
            else:
                positions = 1  # Single point of failure - need 1 more
            
            skill_gaps[skill] = {
                "current_coverage": data["coverage_percent"],
                "team_members": len(data["team_members"]),
                "positions_needed": positions,
                "recommended_level": recommended_level
            }
            
            # Find internal candidates
            internal_candidates = find_internal_candidates(skill, recommended_level, project_id, db)
            
            system_recommendations.append({
                "skill": skill,
                "positions_needed": positions,
                "recommended_level": recommended_level,
                "reason": f"Coverage: {data['coverage_percent']}% - {'No team members' if data['coverage_percent'] == 0 else 'Single point of failure'}",
                "internal_candidates": internal_candidates[:5],  # Top 5
                "estimated_cost_monthly": positions * 9000  # Rough estimate
            })
    
    # Calculate capacity metrics
    members = db.table("project_members").select(
        "users!inner(current_workload_percent)"
    ).eq("project_id", project_id).execute()
    
    workloads = [m["users"]["current_workload_percent"] for m in (members.data or []) if m.get("users")]
    current_utilization = sum(workloads) / len(workloads) if workloads else 0
    
    # Project utilization with new hires
    total_positions = sum(r["positions_needed"] for r in system_recommendations)
    projected_utilization = current_utilization * len(workloads) / (len(workloads) + total_positions) if total_positions > 0 else current_utilization
    
    # Assess risk
    if current_utilization > 90:
        risk_level = "critical"
    elif current_utilization > 80:
        risk_level = "high"
    elif current_utilization > 70:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Generate alternatives
    alternatives = []
    
    # Alternative 1: Internal reallocation
    total_internal = sum(len(r["internal_candidates"]) for r in system_recommendations)
    if total_internal > 0:
        alternatives.append({
            "option": "Internal Reallocation",
            "description": f"{total_internal} internal candidates available with matching skills",
            "savings": total_positions * 9000 * 0.3,  # 30% savings vs new hire
            "feasibility": "high",
            "pros": ["No recruitment delay", "Team knows codebase", "Lower cost"],
            "cons": ["May impact other projects"]
        })
    
    # Alternative 2: Contract workers
    alternatives.append({
        "option": "Contract Workers (3-month)",
        "description": "Hire contractors for immediate needs",
        "savings": total_positions * 9000 * 0.2,
        "feasibility": "high",
        "pros": ["Fast onboarding", "Flexible duration"],
        "cons": ["Higher hourly rate", "Less commitment"]
    })
    
    return {
        "skill_gaps": skill_gaps,
        "capacity_analysis": {
            "current_utilization": round(current_utilization, 2),
            "projected_utilization": round(projected_utilization, 2),
            "team_size": len(workloads),
            "risk_level": risk_level
        },
        "system_recommendations": system_recommendations,
        "alternative_options": alternatives,
        "confidence_score": 0.85 if len(workloads) >= 3 else 0.6,
        "overall_coverage": coverage_data["overall_coverage"]
    }


# ============================================================================
# L7 ENDPOINTS - Team Lead
# ============================================================================

@esp_manager_router.post("/packages")
async def create_esp_package(
    package: ESPPackageCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    L7 creates an ESP package with recommendations
    """
    # Check permissions (L7 or Admin)
    if not is_admin(current_user) and current_user.get("role") != Roles.TECHNICAL_LEAD:
        raise HTTPException(status_code=403, detail="Only Technical Leads can create ESP packages")
    
    try:
        # Create ESP package
        esp_data = {
            "project_id": package.project_id,
            "team_id": package.team_id,
            "created_by_id": current_user["id"],
            "status": "submitted_to_l6",
            "required_headcount": package.required_headcount,
            "duration_months": package.duration_months,
            "justification": package.justification,
            "submitted_at": datetime.now().isoformat(),
            "workflow_history": [{
                "timestamp": datetime.now().isoformat(),
                "action": "L7 submitted package",
                "actor": current_user["name"],
                "level": current_user.get("hierarchy_level"),
                "notes": package.justification
            }]
        }
        
        esp_response = db.table("esp_packages").insert(esp_data).execute()
        esp_package = esp_response.data[0]
        
        # Create L7 recommendations
        for rec in package.recommendations:
            rec_data = {
                "esp_package_id": esp_package["id"],
                "skill": rec.skill,
                "positions_needed": rec.positions_needed,
                "suggested_level": rec.suggested_level,
                "justification": rec.justification,
                "priority": rec.priority
            }
            db.table("esp_l7_recommendations").insert(rec_data).execute()
        
        return {
            "message": "ESP package created successfully",
            "package": esp_package
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@esp_manager_router.get("/packages")
async def get_esp_packages(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get ESP packages based on user role
    """
    try:
        query = db.table("esp_packages").select(
            "*, projects(name), tech_teams(name), users!created_by_id(name, hierarchy_level)"
        )
        
        # Filter by status if provided
        if status:
            query = query.eq("status", status)
        
        # Role-based filtering
        user_role = current_user.get("role")
        
        if user_role == Roles.TECHNICAL_LEAD:
            # L7 sees their own packages
            query = query.eq("created_by_id", current_user["id"])
        elif user_role == Roles.TECHNICAL_LEAD:
            # L6 sees packages pending their review
            query = query.in_("status", ["submitted_to_l6", "l6_reviewing"])
        elif user_role == Roles.PROJECT_MANAGER:
            # PM sees packages pending their decision
            query = query.in_("status", ["pm_reviewing", "l6_approved"])
        
        packages = query.order("created_at", desc=True).execute()
        
        return {
            "packages": packages.data or [],
            "total": len(packages.data or []),
            "role": user_role
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# L6 ENDPOINTS - Principal Architect
# ============================================================================

@esp_manager_router.post("/{package_id}/simulate")
async def run_esp_simulation(
    package_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    L6 runs ESP simulation for a package
    """
    # Check permissions
    if not is_admin(current_user) and current_user.get("hierarchy_level") != "L6":
        raise HTTPException(status_code=403, detail="Only L6 can run simulations")
    
    try:
        # Get package
        package = db.table("esp_packages").select("*").eq("id", package_id).single().execute()
        
        if not package.data:
            raise HTTPException(status_code=404, detail="Package not found")
        
        # Run simulation
        simulation_results = generate_esp_simulation(
            package.data["project_id"],
            package.data["team_id"],
            db
        )
        
        # Save simulation
        sim_data = {
            "esp_package_id": package_id,
            "skill_gaps": simulation_results["skill_gaps"],
            "capacity_analysis": simulation_results["capacity_analysis"],
            "system_recommendations": simulation_results["system_recommendations"],
            "alternative_options": simulation_results["alternative_options"],
            "current_utilization": simulation_results["capacity_analysis"]["current_utilization"],
            "projected_utilization": simulation_results["capacity_analysis"]["projected_utilization"],
            "confidence_score": simulation_results["confidence_score"],
            "risk_factors": {"overall_coverage": simulation_results["overall_coverage"]},
            "created_by_id": current_user["id"]
        }
        
        db.table("esp_simulations").insert(sim_data).execute()
        
        # Update package status
        db.table("esp_packages").update({"status": "l6_reviewing"}).eq("id", package_id).execute()
        
        return {
            "message": "Simulation completed",
            "simulation": simulation_results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@esp_manager_router.post("/{package_id}/l6-review")
async def l6_review_package(
    package_id: str,
    review: L6ReviewRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    L6 reviews and forwards package to PM
    """
    if not is_admin(current_user) and current_user.get("hierarchy_level") != "L6":
        raise HTTPException(status_code=403, detail="Only L6 can review packages")
    
    try:
        # Create review
        review_data = {
            "esp_package_id": package_id,
            "reviewed_by_id": current_user["id"],
            "decision": review.decision,
            "technical_notes": review.technical_notes,
            "capacity_notes": review.capacity_notes,
            "risk_notes": review.risk_notes,
            "additional_positions": review.additional_positions or [],
            "forwarded_to_pm_at": datetime.now().isoformat()
        }
        
        db.table("esp_l6_reviews").insert(review_data).execute()
        
        # Update package status
        new_status = "l6_approved" if review.decision == "approved" else "submitted_to_l6"
        db.table("esp_packages").update({"status": new_status}).eq("id", package_id).execute()
        
        return {
            "message": f"Package {review.decision}",
            "status": new_status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PM ENDPOINTS - Project Manager
# ============================================================================

@esp_manager_router.post("/{package_id}/pm-decision")
async def pm_make_decision(
    package_id: str,
    decision: PMDecisionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    PM makes final decision on ESP package
    """
    if not is_admin(current_user) and current_user.get("role") != Roles.PROJECT_MANAGER:
        raise HTTPException(status_code=403, detail="Only Project Managers can make final decisions")
    
    try:
        # Create decision
        decision_data = {
            "esp_package_id": package_id,
            "decided_by_id": current_user["id"],
            "final_decision": decision.final_decision,
            "approved_positions": decision.approved_positions or [],
            "rejected_positions": decision.rejected_positions or [],
            "selected_alternatives": decision.selected_alternatives or [],
            "business_justification": decision.business_justification,
            "decision_notes": decision.decision_notes
        }
        
        db.table("esp_pm_decisions").insert(decision_data).execute()
        
        # Update package status
        status_map = {
            "approved": "pm_approved",
            "rejected": "pm_rejected",
            "modified": "pm_modified",
            "deferred": "pm_modified"
        }
        
        new_status = status_map.get(decision.final_decision, "pm_modified")
        
        db.table("esp_packages").update({
            "status": new_status,
            "final_decision_at": datetime.now().isoformat()
        }).eq("id", package_id).execute()
        
        return {
            "message": f"Decision: {decision.final_decision}",
            "status": new_status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@esp_manager_router.get("/{package_id}/details")
async def get_package_details(
    package_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get complete package details with all related data
    """
    try:
        # Get package
        package = db.table("esp_packages").select(
            "*, projects(name, required_skills), tech_teams(name), users!created_by_id(name, hierarchy_level)"
        ).eq("id", package_id).single().execute()
        
        if not package.data:
            raise HTTPException(status_code=404, detail="Package not found")
        
        # Get L7 recommendations
        l7_recs = db.table("esp_l7_recommendations").select("*").eq("esp_package_id", package_id).execute()
        
        # Get simulation
        simulation = db.table("esp_simulations").select("*").eq("esp_package_id", package_id).order("created_at", desc=True).limit(1).execute()
        
        # Get L6 review
        l6_review = db.table("esp_l6_reviews").select("*, users(name)").eq("esp_package_id", package_id).execute()
        
        # Get PM decision
        pm_decision = db.table("esp_pm_decisions").select("*, users(name)").eq("esp_package_id", package_id).execute()
        
        return {
            "package": package.data,
            "l7_recommendations": l7_recs.data or [],
            "simulation": simulation.data[0] if simulation.data else None,
            "l6_review": l6_review.data[0] if l6_review.data else None,
            "pm_decision": pm_decision.data[0] if pm_decision.data else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@esp_manager_router.get("/projects/{project_id}/skill-coverage")
async def get_project_skill_coverage(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get skill coverage analysis for a project
    """
    try:
        coverage = calculate_skill_coverage(project_id, db)
        return coverage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
