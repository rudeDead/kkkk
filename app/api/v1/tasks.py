"""
Tasks API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import datetime
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


router = APIRouter()


@router.get("/")
async def get_tasks(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all tasks with filters"""
    try:
        query = db.table("tasks").select("*", count="exact")
        
        user_role = current_user.get("role")
        
        # Admin, HR, PM see all tasks (or filtered by params)
        if is_admin(current_user) or user_role in [Roles.HR, Roles.PROJECT_MANAGER]:
            pass  # No role-based filtering
        
        # Technical Lead sees tasks from assigned projects
        elif user_role == Roles.TECHNICAL_LEAD:
            if not project_id:  # If no specific project, filter by assigned projects
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
                    return {"tasks": [], "total": 0, "page": page, "limit": limit}
        
        # Employees see tasks from their assigned projects
        else:
            if not project_id:  # If no specific project, filter by assigned projects
                # Get employee's assigned projects
                member_response = db.table("project_members").select("project_id").eq("user_id", current_user["id"]).execute()
                project_ids = [m["project_id"] for m in (member_response.data or [])]
                
                if project_ids:
                    query = query.in_("project_id", project_ids)
                else:
                    # No projects - only show tasks assigned to user
                    query = query.eq("assignee_id", current_user["id"])
        
        # Apply additional filters
        if assignee_id:
            if assignee_id == "me":
                query = query.eq("assignee_id", current_user["id"])
            else:
                query = query.eq("assignee_id", assignee_id)
        
        if project_id:
            query = query.eq("project_id", project_id)
        if status:
            query = query.eq("status", status)
        if priority:
            query = query.eq("priority", priority)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "tasks": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get task by ID"""
    try:
        response = db.table("tasks").select("*").eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create new task"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        new_task = {
            "title": task_data.title,
            "description": task_data.description,
            "project_id": task_data.project_id,
            "assignee_id": task_data.assignee_id,
            "priority": task_data.priority,
            "status": task_data.status,
            "estimated_hours": task_data.estimated_hours,
            "due_date": task_data.due_date.isoformat() if task_data.due_date else None,
            "is_learning_task": task_data.is_learning_task,
            "mentor_id": task_data.mentor_id,
            "progress": 0,
            "actual_hours": 0,
            "created_by_id": current_user["id"]
        }
        
        response = db.table("tasks").insert(new_task).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create task")
        
        # Update project task counts
        project_id = task_data.project_id
        tasks_count = db.table("tasks").select("id", count="exact").eq("project_id", project_id).execute()
        active_count = db.table("tasks").select("id", count="exact").eq("project_id", project_id).in_("status", ["not_started", "in_progress"]).execute()
        
        db.table("projects").update({
            "active_tasks": active_count.count
        }).eq("id", project_id).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Update task"""
    try:
        # Get existing task
        existing = db.table("tasks").select("*").eq("id", task_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = existing.data[0]
        
        # Check permissions
        if not is_admin(current_user):
            if current_user["id"] != task["assignee_id"] and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Build update data
        update_data = {}
        if task_data.title is not None:
            update_data["title"] = task_data.title
        if task_data.description is not None:
            update_data["description"] = task_data.description
        if task_data.assignee_id is not None:
            update_data["assignee_id"] = task_data.assignee_id
        if task_data.priority is not None:
            update_data["priority"] = task_data.priority
        if task_data.status is not None:
            update_data["status"] = task_data.status
            if task_data.status == "completed":
                update_data["completed_at"] = datetime.now().isoformat()
                update_data["progress"] = 100
        if task_data.progress is not None:
            update_data["progress"] = task_data.progress
        if task_data.estimated_hours is not None:
            update_data["estimated_hours"] = task_data.estimated_hours
        if task_data.actual_hours is not None:
            update_data["actual_hours"] = task_data.actual_hours
        if task_data.blocked_reason is not None:
            update_data["blocked_reason"] = task_data.blocked_reason
        if task_data.due_date is not None:
            update_data["due_date"] = task_data.due_date.isoformat()
        if task_data.is_learning_task is not None:
            update_data["is_learning_task"] = task_data.is_learning_task
        if task_data.mentor_id is not None:
            update_data["mentor_id"] = task_data.mentor_id
        
        response = db.table("tasks").update(update_data).eq("id", task_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update task")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Delete task (Admin only)"""
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    
    try:
        check = db.table("tasks").select("id").eq("id", task_id).execute()
        if not check.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        db.table("tasks").delete().eq("id", task_id).execute()
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
