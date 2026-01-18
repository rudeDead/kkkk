"""
Incidents API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import datetime
from app.models.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


router = APIRouter()


@router.get("/")
async def get_incidents(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to_id: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all incidents"""
    try:
        query = db.table("incidents").select("*", count="exact")
        
        user_role = current_user.get("role")
        
        # Admin, HR, PM see all incidents
        if is_admin(current_user) or user_role in [Roles.HR, Roles.PROJECT_MANAGER]:
            pass  # No filtering - see all incidents
        
        # Technical Lead sees incidents from their assigned projects
        elif user_role == Roles.TECHNICAL_LEAD:
            # Get TL's assigned projects
            team_lead_query = db.table("projects").select("id").eq("team_lead_id", current_user["id"]).execute()
            team_lead_project_ids = [p["id"] for p in (team_lead_query.data or [])]
            
            member_response = db.table("project_members").select("project_id").eq("user_id", current_user["id"]).execute()
            member_project_ids = [m["project_id"] for m in (member_response.data or [])]
            
            all_project_ids = list(set(team_lead_project_ids + member_project_ids))
            
            if all_project_ids:
                query = query.in_("project_id", all_project_ids)
            else:
                # No projects - return empty
                return {
                    "incidents": [],
                    "total": 0,
                    "page": page,
                    "limit": limit
                }
        
        # Employees see incidents from their assigned projects OR incidents assigned to them
        else:
            # Get employee's assigned projects
            member_response = db.table("project_members").select("project_id").eq("user_id", current_user["id"]).execute()
            project_ids = [m["project_id"] for m in (member_response.data or [])]
            
            if project_ids:
                # Incidents from assigned projects OR assigned to user OR reported by user
                project_ids_str = ','.join([f'"{pid}"' for pid in project_ids])
                query = query.or_(f"project_id.in.({project_ids_str}),assigned_to_id.eq.{current_user['id']},reported_by_id.eq.{current_user['id']}")
            else:
                # No projects - only show incidents assigned to or reported by user
                query = query.or_(f"assigned_to_id.eq.{current_user['id']},reported_by_id.eq.{current_user['id']}")
        
        if project_id:
            query = query.eq("project_id", project_id)
        if severity:
            query = query.eq("severity", severity)
        if status:
            query = query.eq("status", status)
        if assigned_to_id:
            query = query.eq("assigned_to_id", assigned_to_id)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "incidents": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get incident by ID"""
    try:
        response = db.table("incidents").select("*").eq("id", incident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=IncidentResponse, status_code=201)
async def create_incident(
    incident_data: IncidentCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create new incident"""
    try:
        new_incident = {
            "title": incident_data.title,
            "description": incident_data.description,
            "project_id": incident_data.project_id,
            "severity": incident_data.severity,
            "assigned_to_id": incident_data.assigned_to_id,
            "reported_by_id": current_user["id"],
            "status": "open"
        }
        
        response = db.table("incidents").insert(new_incident).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create incident")
        
        # Update user's has_blocking_incident if high/critical
        if incident_data.severity in ["high", "critical"] and incident_data.assigned_to_id:
            db.table("users").update({"has_blocking_incident": True}).eq("id", incident_data.assigned_to_id).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    incident_data: IncidentUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update incident"""
    try:
        existing = db.table("incidents").select("*").eq("id", incident_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = existing.data[0]
        
        # Check permissions
        if not is_admin(current_user):
            if current_user["id"] != incident["assigned_to_id"] and current_user.get("role") not in [Roles.TECHNICAL_LEAD, Roles.PROJECT_MANAGER]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        update_data = {}
        if incident_data.title is not None:
            update_data["title"] = incident_data.title
        if incident_data.description is not None:
            update_data["description"] = incident_data.description
        if incident_data.severity is not None:
            update_data["severity"] = incident_data.severity
        if incident_data.status is not None:
            update_data["status"] = incident_data.status
            if incident_data.status == "resolved":
                update_data["resolved_at"] = datetime.now().isoformat()
            elif incident_data.status == "closed":
                update_data["closed_at"] = datetime.now().isoformat()
        if incident_data.assigned_to_id is not None:
            update_data["assigned_to_id"] = incident_data.assigned_to_id
            update_data["assigned_by_id"] = current_user["id"]
        if incident_data.resolution_notes is not None:
            update_data["resolution_notes"] = incident_data.resolution_notes
        
        response = db.table("incidents").update(update_data).eq("id", incident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update incident")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete incident (Admin only)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        check = db.table("incidents").select("id").eq("id", incident_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        db.table("incidents").delete().eq("id", incident_id).execute()
        
        return {"message": "Incident deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{incident_id}/resolve")
async def resolve_incident(
    incident_id: str,
    resolution_notes: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Resolve incident"""
    try:
        update_data = {
            "status": "resolved",
            "resolved_at": datetime.now().isoformat(),
            "resolution_notes": resolution_notes
        }
        
        response = db.table("incidents").update(update_data).eq("id", incident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = response.data[0]
        
        # Clear user's blocking incident flag if this was their last high/critical incident
        if incident.get("assigned_to_id"):
            remaining = db.table("incidents").select("id").eq("assigned_to_id", incident["assigned_to_id"]).in_("severity", ["high", "critical"]).eq("status", "open").execute()
            if not remaining.data:
                db.table("users").update({"has_blocking_incident": False}).eq("id", incident["assigned_to_id"]).execute()
        
        return {"message": "Incident resolved", "incident": incident}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: str,
    status: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Quick status update for assigned employees
    Employees can update status of incidents assigned to them
    """
    try:
        # Validate status
        valid_statuses = ["open", "in_progress", "resolved", "closed"]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        # Get incident
        existing = db.table("incidents").select("*").eq("id", incident_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident = existing.data[0]
        
        # Check permissions - only assigned user, TL, PM, or Admin can update
        if not is_admin(current_user):
            if current_user["id"] != incident["assigned_to_id"] and current_user.get("role") not in [Roles.TECHNICAL_LEAD, Roles.PROJECT_MANAGER]:
                raise HTTPException(status_code=403, detail="You can only update incidents assigned to you")
        
        # Prepare update
        update_data = {"status": status}
        
        if status == "resolved":
            update_data["resolved_at"] = datetime.now().isoformat()
        
        # Update incident
        response = db.table("incidents").update(update_data).eq("id", incident_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update status")
        
        updated_incident = response.data[0]
        
        # Clear blocking incident flag if resolved
        if status == "resolved" and incident.get("assigned_to_id"):
            remaining = db.table("incidents").select("id").eq("assigned_to_id", incident["assigned_to_id"]).in_("severity", ["high", "critical"]).neq("status", "resolved").execute()
            if not remaining.data:
                db.table("users").update({"has_blocking_incident": False}).eq("id", incident["assigned_to_id"]).execute()
        
        return {
            "message": f"Incident status updated to {status}",
            "incident": updated_incident
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

