"""
Leave Manager API
Sequential Approval Workflow: HR → TL → PM
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime
from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.core.rbac import is_admin, Roles
from pydantic import BaseModel

leave_manager_router = APIRouter()


# ============================================================================
# REQUEST MODELS
# ============================================================================

class HRApprovalRequest(BaseModel):
    notes: Optional[str] = None


class TLDecisionRequest(BaseModel):
    action: str  # 'approve' or 'forward_to_pm'
    notes: Optional[str] = None


class PMDecisionRequest(BaseModel):
    action: str  # 'approve' or 'reject'
    notes: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_risk_level(leave_days: int, employee_id: str, db: Client) -> tuple:
    """
    Calculate risk level based on:
    1. Leave duration (>3 days = risk)
    2. Critical tasks assigned
    3. Blocking incidents
    
    Returns: (risk_level, risk_factors)
    """
    risk_factors = []
    
    # Factor 1: Leave Duration
    if leave_days > 3:
        risk_factors.append({
            "type": "extended_absence",
            "description": f"Leave duration exceeds 3 days ({leave_days} days)"
        })
    
    # Factor 2: Critical Tasks
    try:
        critical_tasks = db.table("tasks").select("id, title").eq("assignee_id", str(employee_id)).eq("priority", "critical").neq("status", "completed").execute()
        critical_count = len(critical_tasks.data or [])
        
        if critical_count > 0:
            risk_factors.append({
                "type": "critical_tasks",
                "description": f"{critical_count} critical task(s) assigned",
                "count": critical_count,
                "tasks": [{"id": t["id"], "title": t.get("title", "Untitled")} for t in (critical_tasks.data or [])]
            })
    except Exception:
        critical_count = 0
    
    # Factor 3: Blocking Incidents
    try:
        incidents = db.table("incidents").select("id, title, severity").eq("assigned_to_id", str(employee_id)).neq("status", "resolved").in_("severity", ["high", "critical"]).execute()
        incident_count = len(incidents.data or [])
        
        if incident_count > 0:
            risk_factors.append({
                "type": "blocking_incidents",
                "description": f"{incident_count} high/critical incident(s)",
                "count": incident_count,
                "incidents": [{"id": i["id"], "title": i.get("title", "Untitled"), "severity": i.get("severity")} for i in (incidents.data or [])]
            })
    except Exception:
        incident_count = 0
    
    # Determine Risk Level
    if incident_count > 0:
        risk_level = "high"
    elif critical_count > 0 or leave_days > 3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return risk_level, risk_factors


def get_team_member_ids(user_id: str, role: str, db: Client) -> set:
    """Get team member IDs for TL or PM"""
    team_member_ids = set()
    
    if role == Roles.TECHNICAL_LEAD:
        # Get tech team members
        teams = db.table("tech_teams").select("id").eq("team_lead_id", user_id).execute()
        if teams.data:
            for team in teams.data:
                members = db.table("tech_team_members").select("user_id").eq("team_id", team["id"]).execute()
                if members.data:
                    team_member_ids.update([m["user_id"] for m in members.data])
    
    elif role == Roles.PROJECT_MANAGER:
        # Get project members
        projects = db.table("projects").select("id").eq("project_manager_id", user_id).execute()
        if projects.data:
            for project in projects.data:
                members = db.table("project_members").select("user_id").eq("project_id", project["id"]).execute()
                if members.data:
                    team_member_ids.update([m["user_id"] for m in members.data])
    
    return team_member_ids


# ============================================================================
# ENDPOINTS
# ============================================================================

@leave_manager_router.get("/pending")
async def get_pending_leaves(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get pending leaves based on user role:
    - HR: pending_hr_review
    - TL: forwarded_to_team_lead (their team only)
    - PM: pending_l7_decision (their projects only)
    """
    try:
        user_role = current_user.get("role")
        user_id = current_user["id"]
        
        print(f"📊 Total Modules:  14")
        print(f"🔐 Total Perms:    72")
        print(f"🎯 Admin:          {is_admin(current_user)}")
        print(f"🎯 HR:             {user_role == Roles.HR}")
        print(f"🎯 PM:             {user_role == Roles.PROJECT_MANAGER}")
        print(f"🎯 TL:             {user_role == Roles.TECHNICAL_LEAD}")
        
        # Determine status filter based on role
        if is_admin(current_user) or user_role == Roles.HR:
            # HR sees all pending HR reviews
            status_filter = "pending_hr_review"
            query = db.table("leaves").select("*, users!employee_id(name, email, hierarchy_level)").eq("status", status_filter)
            leaves_response = query.execute()
            all_leaves = leaves_response.data or []
        
        elif user_role == Roles.TECHNICAL_LEAD:
            # TL sees forwarded_to_team_lead for:
            # 1. Members of their tech team
            # 2. Members of ANY project where they are the team_lead
            status_filter = "forwarded_to_team_lead"
            
            team_member_ids = set()
            
            # Method 1: Get members from tech teams where user is team lead
            teams_response = db.table("tech_teams").select("id").eq("team_lead_id", user_id).execute()
            team_ids = [t["id"] for t in (teams_response.data or [])]
            
            print(f"TL Tech Teams: {team_ids}")
            
            if team_ids:
                for team_id in team_ids:
                    members_response = db.table("tech_team_members").select("user_id").eq("team_id", team_id).execute()
                    if members_response.data:
                        team_member_ids.update([m["user_id"] for m in members_response.data])
            
            # Method 2: Get members from projects where user is team_lead
            projects_response = db.table("projects").select("id").eq("team_lead_id", user_id).execute()
            project_ids = [p["id"] for p in (projects_response.data or [])]
            
            print(f"TL Projects: {project_ids}")
            
            if project_ids:
                for project_id in project_ids:
                    members_response = db.table("project_members").select("user_id").eq("project_id", project_id).execute()
                    if members_response.data:
                        team_member_ids.update([m["user_id"] for m in members_response.data])
            
            print(f"TL All Team Members (Tech Team + Projects): {team_member_ids}")
            
            # Get all leaves with this status
            query = db.table("leaves").select("*, users!employee_id(name, email, hierarchy_level)").eq("status", status_filter)
            leaves_response = query.execute()
            
            # Filter to only team members
            all_leaves = [leave for leave in (leaves_response.data or []) if leave.get("employee_id") in team_member_ids]
            
            print(f"TL Filtered Leaves: {len(all_leaves)}")

        
        elif user_role == Roles.PROJECT_MANAGER:
            # PM sees pending_l7_decision for their project members
            status_filter = "pending_l7_decision"
            
            # Get projects where user is PM
            projects_response = db.table("projects").select("id").eq("project_manager_id", user_id).execute()
            project_ids = [p["id"] for p in (projects_response.data or [])]
            
            print(f"PM Projects: {project_ids}")
            
            project_member_ids = set()
            if project_ids:
                # Get all members of these projects
                for project_id in project_ids:
                    members_response = db.table("project_members").select("user_id").eq("project_id", project_id).execute()
                    if members_response.data:
                        project_member_ids.update([m["user_id"] for m in members_response.data])
            
            print(f"PM Project Members: {project_member_ids}")
            
            # Get all leaves with this status
            query = db.table("leaves").select("*, users!employee_id(name, email, hierarchy_level)").eq("status", status_filter)
            leaves_response = query.execute()
            
            # Filter to only project members
            all_leaves = [leave for leave in (leaves_response.data or []) if leave.get("employee_id") in project_member_ids]
            
            print(f"PM Filtered Leaves: {len(all_leaves)}")
        
        else:
            # Other roles see nothing
            all_leaves = []
        
        # Enrich with risk analysis
        enriched_leaves = []
        for leave in all_leaves:
            leave_days = leave.get("days", 1)
            employee_id = leave.get("employee_id")
            
            risk_level, risk_factors = calculate_risk_level(leave_days, employee_id, db)
            
            enriched_leaves.append({
                **leave,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "can_tl_approve": risk_level == "low" and user_role == Roles.TECHNICAL_LEAD
            })
        
        return {
            "leaves": enriched_leaves,
            "total": len(enriched_leaves),
            "role": user_role,
            "status_filter": status_filter if 'status_filter' in locals() else None
        }
    
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Error fetching pending leaves: {str(e)}\n{traceback.format_exc()}")


@leave_manager_router.post("/{leave_id}/hr-approve")
async def hr_approve_leave(
    leave_id: str,
    request: HRApprovalRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """HR validates quota and forwards to TL"""
    try:
        # Check permissions
        if not is_admin(current_user) and current_user.get("role") != Roles.HR:
            raise HTTPException(status_code=403, detail="Only HR can perform this action")
        
        # Update leave status
        update_data = {
            "status": "forwarded_to_team_lead",
            "hr_reviewed_by": current_user["id"],
            "hr_reviewed_at": datetime.now().isoformat()
        }
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        return {
            "message": "Leave forwarded to Team Lead",
            "leave": response.data[0] if response.data else {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@leave_manager_router.post("/{leave_id}/tl-decision")
async def tl_make_decision(
    leave_id: str,
    request: TLDecisionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    TL makes decision:
    - Low risk: Approve
    - Medium/High risk: Forward to PM
    """
    try:
        # Check permissions
        if not is_admin(current_user) and current_user.get("role") != Roles.TECHNICAL_LEAD:
            raise HTTPException(status_code=403, detail="Only Technical Lead can perform this action")
        
        # Determine new status
        if request.action == "approve":
            new_status = "approved"
            update_data = {
                "status": new_status,
                "decided_by_id": current_user["id"],
                "decision_notes": request.notes,
                "approved_at": datetime.now().isoformat()
            }
        elif request.action == "forward_to_pm":
            new_status = "pending_l7_decision"
            update_data = {
                "status": new_status,
                "decision_notes": request.notes
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'forward_to_pm'")
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        return {
            "message": f"Leave {request.action.replace('_', ' ')}d",
            "leave": response.data[0] if response.data else {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@leave_manager_router.post("/{leave_id}/pm-decision")
async def pm_make_decision(
    leave_id: str,
    request: PMDecisionRequest,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """PM makes final decision: approve or reject"""
    try:
        # Check permissions
        if not is_admin(current_user) and current_user.get("role") != Roles.PROJECT_MANAGER:
            raise HTTPException(status_code=403, detail="Only Project Manager can perform this action")
        
        # Determine new status
        if request.action == "approve":
            new_status = "approved"
            approved_at = datetime.now().isoformat()
        elif request.action == "reject":
            new_status = "rejected"
            approved_at = None
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'")
        
        update_data = {
            "status": new_status,
            "decided_by_id": current_user["id"],
            "decision_notes": request.notes
        }
        
        if approved_at:
            update_data["approved_at"] = approved_at
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        return {
            "message": f"Leave {request.action}d",
            "leave": response.data[0] if response.data else {}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@leave_manager_router.get("/{leave_id}/risk-analysis")
async def get_risk_analysis(
    leave_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get detailed risk analysis for a leave request"""
    try:
        # Get leave details
        leave_response = db.table("leaves").select("*, users!employee_id(name, email, hierarchy_level)").eq("id", leave_id).execute()
        
        if not leave_response.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        leave = leave_response.data[0]
        leave_days = leave.get("days", 1)
        employee_id = leave.get("employee_id")
        
        # Calculate risk
        risk_level, risk_factors = calculate_risk_level(leave_days, employee_id, db)
        
        return {
            "leave_id": leave_id,
            "employee_name": leave.get("users", {}).get("name", "Unknown"),
            "leave_days": leave_days,
            "start_date": leave.get("start_date"),
            "end_date": leave.get("end_date"),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": {
                "tl_can_approve": risk_level == "low",
                "requires_pm_approval": risk_level in ["medium", "high"],
                "reason": "Low risk - TL can approve" if risk_level == "low" else "Medium/High risk - Requires PM approval"
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
