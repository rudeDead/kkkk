"""
Teams API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from app.models.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberAdd
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


router = APIRouter()


@router.get("/")
async def get_teams(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    department: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all teams"""
    try:
        query = db.table("tech_teams").select("*", count="exact")
        
        if department:
            query = query.eq("department", department)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "teams": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get team by ID"""
    try:
        response = db.table("tech_teams").select("*").eq("id", team_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Team not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=TeamResponse, status_code=201)
async def create_team(
    team_data: TeamCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create new team (Admin or PM only)"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.HR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        new_team = {
            "name": team_data.name,
            "description": team_data.description,
            "department": team_data.department,
            "team_lead_id": team_data.team_lead_id
        }
        
        response = db.table("tech_teams").insert(new_team).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create team")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: str,
    team_data: TeamUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update team"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.HR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        check = db.table("tech_teams").select("id").eq("id", team_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Team not found")
        
        update_data = {}
        if team_data.name is not None:
            update_data["name"] = team_data.name
        if team_data.description is not None:
            update_data["description"] = team_data.description
        if team_data.department is not None:
            update_data["department"] = team_data.department
        if team_data.team_lead_id is not None:
            update_data["team_lead_id"] = team_data.team_lead_id
        
        response = db.table("tech_teams").update(update_data).eq("id", team_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update team")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete team (Admin only)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        check = db.table("tech_teams").select("id").eq("id", team_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Team not found")
        
        db.table("tech_teams").delete().eq("id", team_id).execute()
        
        return {"message": "Team deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get team members"""
    try:
        response = db.table("tech_team_members").select("*").eq("team_id", team_id).execute()
        
        members = response.data or []
        
        # Get user details
        if members:
            user_ids = [m["user_id"] for m in members]
            users = db.table("users").select("id, name, email, role, hierarchy_level").in_("id", user_ids).execute()
            users_map = {u["id"]: u for u in (users.data or [])}
            
            for member in members:
                member["user"] = users_map.get(member["user_id"])
        
        return {"members": members, "total": len(members)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/members", status_code=201)
async def add_team_member(
    team_id: str,
    member_data: TeamMemberAdd,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Add member to team"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.HR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Check if already member
        existing = db.table("tech_team_members").select("id").eq("team_id", team_id).eq("user_id", member_data.user_id).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="User is already a team member")
        
        new_member = {
            "team_id": team_id,
            "user_id": member_data.user_id
        }
        
        response = db.table("tech_team_members").insert(new_member).execute()
        
        # Update user's tech_team_id
        db.table("users").update({"tech_team_id": team_id}).eq("id", member_data.user_id).execute()
        
        return response.data[0] if response.data else {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: str,
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Remove member from team"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.HR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        db.table("tech_team_members").delete().eq("team_id", team_id).eq("user_id", user_id).execute()
        
        # Clear user's tech_team_id
        db.table("users").update({"tech_team_id": None}).eq("id", user_id).execute()
        
        return {"message": "Member removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
