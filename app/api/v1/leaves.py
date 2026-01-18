"""
Leaves API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import datetime
from app.models.leave import LeaveCreate, LeaveUpdate, LeaveResponse
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


router = APIRouter()


@router.get("/")
async def get_leaves(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    employee_id: Optional[str] = None,
    status: Optional[str] = None,
    leave_type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all leaves"""
    try:
        query = db.table("leaves").select("*, employee:users!employee_id(name, email)", count="exact")
        
        # PERSONAL MODULE: Everyone sees only their own leaves (except Admin)
        # Admin can see all leaves
        # HR, PM, TL also see only their own leaves in this module
        if not is_admin(current_user):
            # Everyone (including HR, PM, TL) sees only their own leaves
            query = query.eq("employee_id", current_user["id"])
        elif employee_id:
            # Admin can filter by specific employee
            query = query.eq("employee_id", employee_id)
        
        if status:
            query = query.eq("status", status)
        if leave_type:
            query = query.eq("leave_type", leave_type)
            query = query.eq("leave_type", leave_type)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "leaves": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{leave_id}", response_model=LeaveResponse)
async def get_leave(
    leave_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get leave by ID"""
    try:
        response = db.table("leaves").select("*").eq("id", leave_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        leave = response.data[0]
        
        # Check permissions
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            if leave["employee_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="Access denied")
        
        return leave
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=LeaveResponse, status_code=201)
async def create_leave(
    leave_data: LeaveCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create leave request"""
    try:
        new_leave = {
            "employee_id": current_user["id"],
            "leave_type": leave_data.leave_type,
            "start_date": leave_data.start_date.isoformat(),
            "end_date": leave_data.end_date.isoformat(),
            "days": leave_data.days,
            "reason": leave_data.reason,
            "status": "pending_hr_review",
            "conflict_severity": "none"
        }
        
        response = db.table("leaves").insert(new_leave).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create leave")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{leave_id}", response_model=LeaveResponse)
async def update_leave(
    leave_id: str,
    leave_data: LeaveUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update leave (for approval/rejection)"""
    try:
        # Get existing leave
        existing = db.table("leaves").select("*").eq("id", leave_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        leave = existing.data[0]
        
        # Check permissions
        can_update = False
        if is_admin(current_user):
            can_update = True
        elif current_user.get("role") == Roles.HR:
            can_update = True
        elif current_user.get("role") in [Roles.TECHNICAL_LEAD, Roles.PROJECT_MANAGER]:
            can_update = True
        elif leave["employee_id"] == current_user["id"] and leave["status"] == "pending_hr_review":
            can_update = True  # Can cancel own pending leave
        
        if not can_update:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build update data
        update_data = {}
        
        if leave_data.status is not None:
            update_data["status"] = leave_data.status
            
            if leave_data.status == "approved":
                update_data["approved_at"] = datetime.now().isoformat()
                update_data["decided_by_id"] = current_user["id"]
            elif leave_data.status == "rejected":
                update_data["decided_by_id"] = current_user["id"]
            elif leave_data.status == "forwarded_to_team_lead":
                update_data["hr_reviewed_by"] = current_user["id"]
                update_data["hr_reviewed_at"] = datetime.now().isoformat()
        
        if leave_data.decision_notes is not None:
            update_data["decision_notes"] = leave_data.decision_notes
        
        if leave_data.alternate_assigned_id is not None:
            update_data["alternate_assigned_id"] = leave_data.alternate_assigned_id
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update leave")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{leave_id}")
async def delete_leave(
    leave_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete/cancel leave"""
    try:
        # Get leave
        existing = db.table("leaves").select("*").eq("id", leave_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        leave = existing.data[0]
        
        # Check permissions
        if not is_admin(current_user):
            if leave["employee_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="Can only cancel own leaves")
            if leave["status"] not in ["pending_hr_review", "forwarded_to_team_lead"]:
                raise HTTPException(status_code=400, detail="Cannot cancel approved/rejected leaves")
        
        # Soft delete - set status to cancelled
        db.table("leaves").update({"status": "cancelled"}).eq("id", leave_id).execute()
        
        return {"message": "Leave cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{leave_id}/approve")
async def approve_leave(
    leave_id: str,
    decision_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Approve leave (HR/Admin/Lead)"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.TECHNICAL_LEAD, Roles.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        update_data = {
            "status": "approved",
            "approved_at": datetime.now().isoformat(),
            "decided_by_id": current_user["id"],
            "decision_notes": decision_notes
        }
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        return {"message": "Leave approved", "leave": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{leave_id}/reject")
async def reject_leave(
    leave_id: str,
    decision_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Reject leave (HR/Admin/Lead)"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.TECHNICAL_LEAD, Roles.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        update_data = {
            "status": "rejected",
            "decided_by_id": current_user["id"],
            "decision_notes": decision_notes
        }
        
        response = db.table("leaves").update(update_data).eq("id", leave_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Leave not found")
        
        return {"message": "Leave rejected", "leave": response.data[0]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
