"""
Projects API Endpoints
Handles project CRUD, team management, and analytics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import date, datetime
from app.models.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    ProjectMemberAdd, ProjectMemberUpdate, ProjectMemberResponse, ProjectAnalytics
)
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.rbac import require_role, Roles, is_admin
from app.database import get_db, get_service_db


router = APIRouter()


# ============================================================================
# GET ALL PROJECTS
# ============================================================================

@router.get("/", response_model=ProjectListResponse)
async def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    project_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get all projects with filters and pagination
    
    **Filters:**
    - status: planning, active, on_hold, completed, cancelled
    - priority: low, medium, high, critical
    - project_type: delivery, internal, research, maintenance, client_support
    - search: Search by name or description
    """
    try:
        query = db.table("projects").select("*", count="exact")
        
        # Role-based filtering
        user_role = current_user.get("role")
        
        # Admin, HR, PM see all projects
        if is_admin(current_user) or user_role in [Roles.HR, Roles.PROJECT_MANAGER]:
            pass  # No filtering - see all projects
        
        # Technical Lead sees projects where they are team_lead OR member
        elif user_role == Roles.TECHNICAL_LEAD:
            # Get projects where user is team lead
            team_lead_query = db.table("projects").select("id").eq("team_lead_id", current_user["id"]).execute()
            team_lead_project_ids = [p["id"] for p in (team_lead_query.data or [])]
            
            # Get projects where user is a member
            member_response = db.table("project_members").select("project_id").eq("user_id", current_user["id"]).execute()
            member_project_ids = [m["project_id"] for m in (member_response.data or [])]
            
            # Combine both lists
            all_project_ids = list(set(team_lead_project_ids + member_project_ids))
            
            if all_project_ids:
                query = query.in_("id", all_project_ids)
            else:
                # No projects - return empty
                return {
                    "projects": [],
                    "total": 0,
                    "page": page,
                    "limit": limit
                }
        
        # Employees see only projects they are members of
        else:
            # Get projects where user is a member
            member_response = db.table("project_members").select("project_id").eq("user_id", current_user["id"]).execute()
            project_ids = [m["project_id"] for m in (member_response.data or [])]
            
            if project_ids:
                query = query.in_("id", project_ids)
            else:
                # No projects - return empty
                return {
                    "projects": [],
                    "total": 0,
                    "page": page,
                    "limit": limit
                }
        
        # Apply filters
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
        if project_type:
            query = query.eq("project_type", project_type)
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        # Pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        # Execute
        response = query.execute()
        
        return {
            "projects": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )


# ============================================================================
# GET PROJECT BY ID
# ============================================================================

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get project by ID"""
    try:
        response = db.table("projects").select("*").eq("id", project_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )


# ============================================================================
# CREATE PROJECT
# ============================================================================

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Create new project
    
    **Permissions:**
    - Admin: Can create any project
    - Project Manager: Can create projects
    """
    # Check permissions
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin, PM, or Tech Lead can create projects"
        )
    
    try:
        # Prepare project data
        new_project = {
            "name": project_data.name,
            "description": project_data.description,
            "project_manager_id": project_data.project_manager_id,
            "principal_architect_id": project_data.principal_architect_id,
            "team_lead_id": project_data.team_lead_id,
            "required_skills": project_data.required_skills,
            "tech_stack": project_data.tech_stack,
            "project_type": project_data.project_type,
            "priority": project_data.priority,
            "status": project_data.status,
            "start_date": project_data.start_date.isoformat(),
            "deadline": project_data.deadline.isoformat() if project_data.deadline else None,
            "risk_level": project_data.risk_level,
            "created_by_id": current_user["id"],
            "progress": 0,
            "total_hours": 0,
            "done_hours": 0,
            "team_size": 0,
            "active_members": 0,
            "active_tasks": 0,
            "blocked_tasks": 0,
            "completed_tasks": 0
        }
        
        # Insert project
        response = db.table("projects").insert(new_project).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


# ============================================================================
# UPDATE PROJECT
# ============================================================================

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Update project
    
    **Permissions:**
    - Admin: Can update any project
    - Project Manager: Can update own projects
    """
    try:
        # Check if project exists
        project_response = db.table("projects").select("*").eq("id", project_id).execute()
        
        if not project_response.data or len(project_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project = project_response.data[0]
        
        # Check permissions
        # Admin, PM (owner), or TL (of this project) can update
        if not is_admin(current_user):
            is_pm_owner = current_user["id"] == project.get("project_manager_id")
            is_tl_of_project = current_user["id"] == project.get("team_lead_id")
            
            if not (is_pm_owner or is_tl_of_project):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to update this project"
                )
        
        # Prepare update data
        update_data = {}
        
        if project_data.name is not None:
            update_data["name"] = project_data.name
        if project_data.description is not None:
            update_data["description"] = project_data.description
        if project_data.project_manager_id is not None:
            update_data["project_manager_id"] = project_data.project_manager_id
        if project_data.principal_architect_id is not None:
            update_data["principal_architect_id"] = project_data.principal_architect_id
        if project_data.team_lead_id is not None:
            update_data["team_lead_id"] = project_data.team_lead_id
        if project_data.required_skills is not None:
            update_data["required_skills"] = project_data.required_skills
        if project_data.tech_stack is not None:
            update_data["tech_stack"] = project_data.tech_stack
        if project_data.project_type is not None:
            update_data["project_type"] = project_data.project_type
        if project_data.priority is not None:
            update_data["priority"] = project_data.priority
        if project_data.status is not None:
            update_data["status"] = project_data.status
        if project_data.progress is not None:
            update_data["progress"] = project_data.progress
        if project_data.start_date is not None:
            update_data["start_date"] = project_data.start_date.isoformat()
        if project_data.deadline is not None:
            update_data["deadline"] = project_data.deadline.isoformat()
        if project_data.risk_level is not None:
            update_data["risk_level"] = project_data.risk_level
        
        # Update project
        response = db.table("projects").update(update_data).eq("id", project_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


# ============================================================================
# DELETE PROJECT
# ============================================================================

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Delete project (soft delete - set status to cancelled)
    
    **Permissions:**
    - Admin only
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can delete projects"
        )
    
    try:
        # Check if exists
        check = db.table("projects").select("id").eq("id", project_id).execute()
        
        if not check.data or len(check.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Soft delete
        db.table("projects").update({"status": "cancelled"}).eq("id", project_id).execute()
        
        return {
            "message": "Project deleted successfully",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


# ============================================================================
# PROJECT TEAM MANAGEMENT
# ============================================================================

@router.get("/{project_id}/members")
async def get_project_members(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all project members"""
    try:
        response = db.table("project_members").select("*").eq("project_id", project_id).execute()
        
        members = response.data or []
        
        # Get user details for each member
        if members:
            user_ids = [m["user_id"] for m in members]
            users_response = db.table("users").select("id, name, email, role, hierarchy_level").in_("id", user_ids).execute()
            users_map = {u["id"]: u for u in (users_response.data or [])}
            
            # Enrich members with user data
            for member in members:
                member["user"] = users_map.get(member["user_id"])
        
        return {
            "members": members,
            "total": len(members)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch members: {str(e)}"
        )


@router.post("/{project_id}/members", status_code=status.HTTP_201_CREATED)
async def add_project_member(
    project_id: str,
    member_data: ProjectMemberAdd,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Add member to project
    
    **Permissions:**
    - Admin, PM, or Tech Lead
    """
    # Admin, PM, or TL can add members
    # But TL can only add to their own projects
    if not is_admin(current_user):
        user_role = current_user.get("role")
        
        if user_role == Roles.TECHNICAL_LEAD:
            # Check if TL of this project
            project_check = db.table("projects").select("team_lead_id").eq("id", project_id).execute()
            if not project_check.data or project_check.data[0].get("team_lead_id") != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only add members to projects you lead"
                )
        elif user_role != Roles.PROJECT_MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, PM, or Tech Lead can add members"
            )
    
    try:
        # Check if already member
        existing = db.table("project_members").select("id").eq("project_id", project_id).eq("user_id", member_data.user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a project member"
            )
        
        # Add member
        new_member = {
            "project_id": project_id,
            "user_id": member_data.user_id,
            "role": member_data.role,
            "allocation_percent": member_data.allocation_percent
        }
        
        response = db.table("project_members").insert(new_member).execute()
        
        # Update project team_size
        members_count = db.table("project_members").select("id", count="exact").eq("project_id", project_id).execute()
        db.table("projects").update({"team_size": members_count.count}).eq("id", project_id).execute()
        
        return response.data[0] if response.data else {}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add member: {str(e)}"
        )


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Remove member from project"""
    # Admin, PM, or TL can remove members
    # But TL can only remove from their own projects
    if not is_admin(current_user):
        user_role = current_user.get("role")
        
        if user_role == Roles.TECHNICAL_LEAD:
            # Check if TL of this project
            project_check = db.table("projects").select("team_lead_id").eq("id", project_id).execute()
            if not project_check.data or project_check.data[0].get("team_lead_id") != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only remove members from projects you lead"
                )
        elif user_role != Roles.PROJECT_MANAGER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Admin, PM, or Tech Lead can remove members"
            )
    
    try:
        db.table("project_members").delete().eq("project_id", project_id).eq("user_id", user_id).execute()
        
        # Update project team_size
        members_count = db.table("project_members").select("id", count="exact").eq("project_id", project_id).execute()
        db.table("projects").update({"team_size": members_count.count}).eq("id", project_id).execute()
        
        return {"message": "Member removed successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove member: {str(e)}"
        )


# ============================================================================
# PROJECT ANALYTICS
# ============================================================================

@router.get("/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get project analytics and health metrics"""
    try:
        # Get project
        project_response = db.table("projects").select("*").eq("id", project_id).execute()
        
        if not project_response.data or len(project_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project = project_response.data[0]
        
        # Get tasks
        tasks_response = db.table("tasks").select("*").eq("project_id", project_id).execute()
        tasks = tasks_response.data or []
        
        tasks_total = len(tasks)
        tasks_completed = len([t for t in tasks if t["status"] == "completed"])
        tasks_blocked = len([t for t in tasks if t["status"] == "blocked"])
        
        # Calculate time metrics
        start_date = datetime.fromisoformat(project["start_date"]) if isinstance(project["start_date"], str) else project["start_date"]
        deadline = datetime.fromisoformat(project["deadline"]) if project.get("deadline") and isinstance(project["deadline"], str) else project.get("deadline")
        
        today = datetime.now()
        days_elapsed = (today - start_date).days if start_date else 0
        days_remaining = (deadline - today).days if deadline else 0
        days_total = (deadline - start_date).days if (start_date and deadline) else 0
        
        # Calculate health score
        progress = project.get("progress", 0)
        health_score = min(100, (progress + (tasks_completed / max(tasks_total, 1) * 100)) / 2)
        
        if health_score >= 70:
            health_status = "healthy"
        elif health_score >= 40:
            health_status = "warning"
        else:
            health_status = "critical"
        
        # Risk factors
        risk_factors = []
        if tasks_blocked > 0:
            risk_factors.append(f"{tasks_blocked} blocked tasks")
        if days_remaining < 7 and progress < 80:
            risk_factors.append("Approaching deadline with low progress")
        if project.get("risk_level") in ["high", "critical"]:
            risk_factors.append(f"High risk level: {project.get('risk_level')}")
        
        return {
            "project_id": project_id,
            "project_name": project["name"],
            "overall_progress": progress,
            "tasks_completed": tasks_completed,
            "tasks_total": tasks_total,
            "tasks_blocked": tasks_blocked,
            "days_elapsed": max(0, days_elapsed),
            "days_remaining": max(0, days_remaining),
            "days_total": max(0, days_total),
            "team_size": project.get("team_size", 0),
            "team_utilization": 75.0,  # Placeholder
            "risk_level": project.get("risk_level", "low"),
            "risk_factors": risk_factors,
            "health_score": health_score,
            "health_status": health_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(e)}"
        )


# ============================================================================
# PROJECT RACI MATRIX
# ============================================================================

@router.get("/{project_id}/raci")
async def get_project_raci(
    project_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get RACI matrix with actual team member names
    Returns team members grouped by hierarchy level
    """
    try:
        # Get project details
        project_response = db.table("projects").select(
            "id, name, project_manager_id, principal_architect_id, team_lead_id"
        ).eq("id", project_id).execute()
        
        if not project_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        project = project_response.data[0]
        
        # Get all project members with user details
        members_response = db.table("project_members").select(
            "*, users(id, name, email, role, hierarchy_level)"
        ).eq("project_id", project_id).execute()
        
        members = members_response.data or []
        
        # Get project leadership details
        leadership_ids = []
        if project.get("project_manager_id"):
            leadership_ids.append(project["project_manager_id"])
        if project.get("principal_architect_id"):
            leadership_ids.append(project["principal_architect_id"])
        if project.get("team_lead_id"):
            leadership_ids.append(project["team_lead_id"])
        
        leadership = {}
        if leadership_ids:
            leadership_response = db.table("users").select(
                "id, name, email, role, hierarchy_level"
            ).in_("id", leadership_ids).execute()
            
            for user in (leadership_response.data or []):
                if user["id"] == project.get("project_manager_id"):
                    leadership["project_manager"] = user
                if user["id"] == project.get("principal_architect_id"):
                    leadership["principal_architect"] = user
                if user["id"] == project.get("team_lead_id"):
                    leadership["team_lead"] = user
        
        # Group members by hierarchy level
        members_by_level = {
            "L1_L2": [],  # Admin
            "L3_L5": [],  # PM
            "L6_L7": [],  # Tech Lead
            "L8_L13": []  # Employees
        }
        
        for member in members:
            user = member.get("users") if isinstance(member.get("users"), dict) else {}
            level = user.get("hierarchy_level", "")
            
            if level in ["L1", "L2"]:
                members_by_level["L1_L2"].append(user)
            elif level in ["L3", "L4", "L5"]:
                members_by_level["L3_L5"].append(user)
            elif level in ["L6", "L7"]:
                members_by_level["L6_L7"].append(user)
            elif level in ["L8", "L9", "L10", "L11", "L12", "L13"]:
                members_by_level["L8_L13"].append(user)
        
        return {
            "project_id": project_id,
            "project_name": project["name"],
            "leadership": leadership,
            "members_by_level": members_by_level,
            "total_members": len(members)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch RACI data: {str(e)}"
        )

