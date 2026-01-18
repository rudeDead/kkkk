"""
Events API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from app.models.event import EventCreate, EventUpdate, EventResponse
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


router = APIRouter()


@router.get("/")
async def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    event_type: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all events"""
    try:
        query = db.table("events").select("*", count="exact")
        
        if event_type:
            query = query.eq("event_type", event_type)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "events": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get event by ID"""
    try:
        response = db.table("events").select("*").eq("id", event_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=EventResponse, status_code=201)
async def create_event(
    event_data: EventCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create event (Admin/HR only)"""
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(status_code=403, detail="Only Admin or HR can create events")
    
    try:
        new_event = {
            "name": event_data.name,
            "description": event_data.description,
            "event_type": event_data.event_type,
            "start_datetime": event_data.event_date.isoformat() + "T00:00:00",  # Convert date to datetime
            "end_datetime": event_data.event_date.isoformat() + "T23:59:59",  # End of day
            "location": event_data.location,
            "max_participants": event_data.max_participants,
            "organized_by_id": current_user["id"]
        }
        
        response = db.table("events").insert(new_event).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create event")
        
        # Add current_participants count (0 for new event)
        event_result = response.data[0]
        event_result["current_participants"] = 0
        
        return event_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update event (Admin/HR only)"""
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(status_code=403, detail="Only Admin or HR can update events")
    
    try:
        check = db.table("events").select("id").eq("id", event_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        update_data = {}
        if event_data.name is not None:
            update_data["name"] = event_data.name
        if event_data.description is not None:
            update_data["description"] = event_data.description
        if event_data.event_type is not None:
            update_data["event_type"] = event_data.event_type
        if event_data.event_date is not None:
            update_data["event_date"] = event_data.event_date.isoformat()
        if event_data.location is not None:
            update_data["location"] = event_data.location
        if event_data.max_participants is not None:
            update_data["max_participants"] = event_data.max_participants
        
        response = db.table("events").update(update_data).eq("id", event_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update event")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete event (Admin only)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        check = db.table("events").select("id").eq("id", event_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        db.table("events").delete().eq("id", event_id).execute()
        
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{event_id}/register")
async def register_for_event(
    event_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Register for event"""
    try:
        # Check if event exists and has capacity
        event = db.table("events").select("*").eq("id", event_id).execute()
        if not event.data:
            raise HTTPException(status_code=404, detail="Event not found")
        
        event_data = event.data[0]
        if event_data.get("max_participants") and event_data.get("current_participants", 0) >= event_data["max_participants"]:
            raise HTTPException(status_code=400, detail="Event is full")
        
        # Check if already registered
        existing = db.table("event_participants").select("id").eq("event_id", event_id).eq("user_id", current_user["id"]).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Already registered")
        
        # Register
        db.table("event_participants").insert({"event_id": event_id, "user_id": current_user["id"]}).execute()
        
        # Update participant count
        new_count = event_data.get("current_participants", 0) + 1
        db.table("events").update({"current_participants": new_count}).eq("id", event_id).execute()
        
        return {"message": "Successfully registered for event"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{event_id}/unregister")
async def unregister_from_event(
    event_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Unregister from event"""
    try:
        db.table("event_participants").delete().eq("event_id", event_id).eq("user_id", current_user["id"]).execute()
        
        # Update participant count
        event = db.table("events").select("current_participants").eq("id", event_id).execute()
        if event.data:
            new_count = max(0, event.data[0].get("current_participants", 1) - 1)
            db.table("events").update({"current_participants": new_count}).eq("id", event_id).execute()
        
        return {"message": "Successfully unregistered from event"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}/participants")
async def get_event_participants(
    event_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get event participants"""
    try:
        participants = db.table("event_participants").select("*").eq("event_id", event_id).execute()
        
        if participants.data:
            user_ids = [p["user_id"] for p in participants.data]
            users = db.table("users").select("id, name, email, role").in_("id", user_ids).execute()
            users_map = {u["id"]: u for u in (users.data or [])}
            
            for p in participants.data:
                p["user"] = users_map.get(p["user_id"])
        
        return {"participants": participants.data or [], "total": len(participants.data or [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
