"""
Users API Endpoints
Handles user CRUD operations, workload tracking, and user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional, List
from app.models.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.security import hash_password
from app.core.dependencies import get_current_user, get_current_active_user
from app.core.rbac import require_role, require_admin, Roles, can_manage_user, is_admin
from app.database import get_db, get_service_db


router = APIRouter()


# ============================================================================
# GET ALL USERS (with filters and pagination)
# ============================================================================

@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    hierarchy_level: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get all users with filters and pagination
    
    **Filters:**
    - role: Filter by role (admin, project_manager, technical_lead, hr, employee)
    - hierarchy_level: Filter by level (L1-L13)
    - department: Filter by department
    - status: Filter by status (active, on_leave, notice_period, exited)
    - search: Search by name or email
    
    **Permissions:**
    - Admin: Can see all users
    - Others: Can see all users (read-only)
    """
    try:
        # Build query
        query = db.table("users").select("*", count="exact")
        
        # Apply filters
        if role:
            query = query.eq("role", role)
        if hierarchy_level:
            query = query.eq("hierarchy_level", hierarchy_level)
        if department:
            query = query.eq("department", department)
        if status:
            query = query.eq("status", status)
        if search:
            query = query.or_(f"name.ilike.%{search}%,email.ilike.%{search}%")
        
        # Pagination
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        # Execute query
        response = query.execute()
        
        users = response.data or []
        total = response.count or 0
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


# ============================================================================
# GET USER BY ID
# ============================================================================

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get user by ID
    
    **Permissions:**
    - Anyone can view user details
    """
    try:
        response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user: {str(e)}"
        )


# ============================================================================
# CREATE USER (Admin or HR only)
# ============================================================================

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Create new user
    
    **Permissions:**
    - Admin: Can create any user
    - HR: Can create employees
    """
    # Check permissions
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin or HR can create users"
        )
    
    try:
        # Check if email already exists
        existing = db.table("users").select("id").eq("email", user_data.email).execute()
        if existing.data and len(existing.data) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Prepare user data
        new_user = {
            "email": user_data.email,
            "password_hash": password_hash,
            "name": user_data.name,
            "role": user_data.role,
            "hierarchy_level": user_data.hierarchy_level,
            "department": user_data.department,
            "skills": user_data.skills,
            "experience_years": user_data.experience_years,
            "weekly_capacity": user_data.weekly_capacity,
            "manager_id": user_data.manager_id,
            "tech_team_id": user_data.tech_team_id,
            "status": user_data.status,
            "created_by_id": current_user["id"]
        }
        
        # Insert user
        response = db.table("users").insert(new_user).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


# ============================================================================
# UPDATE USER
# ============================================================================

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Update user
    
    **Permissions:**
    - Admin: Can update any user
    - HR: Can update employee profiles
    - Manager: Can update their direct reports
    - User: Can update own profile (limited fields)
    """
    try:
        # Fetch target user
        target_response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not target_response.data or len(target_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        target_user = target_response.data[0]
        
        # Check permissions
        if not can_manage_user(current_user, target_user) and current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this user"
            )
        
        # Prepare update data (only include provided fields)
        update_data = {}
        
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.name is not None:
            update_data["name"] = user_data.name
        if user_data.role is not None:
            # Only admin can change roles
            if not is_admin(current_user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only Admin can change user roles"
                )
            update_data["role"] = user_data.role
        if user_data.hierarchy_level is not None:
            update_data["hierarchy_level"] = user_data.hierarchy_level
        if user_data.department is not None:
            update_data["department"] = user_data.department
        if user_data.skills is not None:
            update_data["skills"] = user_data.skills
        if user_data.experience_years is not None:
            update_data["experience_years"] = user_data.experience_years
        if user_data.weekly_capacity is not None:
            update_data["weekly_capacity"] = user_data.weekly_capacity
        if user_data.manager_id is not None:
            update_data["manager_id"] = user_data.manager_id
        if user_data.tech_team_id is not None:
            update_data["tech_team_id"] = user_data.tech_team_id
        if user_data.status is not None:
            update_data["status"] = user_data.status
        if user_data.password is not None:
            update_data["password_hash"] = hash_password(user_data.password)
        
        update_data["updated_by_id"] = current_user["id"]
        
        # Update user
        response = db.table("users").update(update_data).eq("id", user_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


# ============================================================================
# DELETE USER (Admin only)
# ============================================================================

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """
    Delete user (soft delete - set status to 'exited')
    
    **Permissions:**
    - Admin only
    """
    # Only admin can delete users
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin can delete users"
        )
    
    try:
        # Check if user exists
        check_response = db.table("users").select("id").eq("id", user_id).execute()
        
        if not check_response.data or len(check_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete (set status to exited)
        response = db.table("users").update({
            "status": "exited",
            "updated_by_id": current_user["id"]
        }).eq("id", user_id).execute()
        
        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


# ============================================================================
# GET USER WORKLOAD
# ============================================================================

@router.get("/{user_id}/workload")
async def get_user_workload(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get user workload details
    
    Returns:
    - Active projects
    - Active tasks
    - Current workload percentage
    - Blocking incidents
    """
    try:
        # Get user
        user_response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user = user_response.data[0]
        
        # Get active projects
        projects_response = db.table("project_members").select("project_id").eq("user_id", user_id).execute()
        project_ids = [p["project_id"] for p in (projects_response.data or [])]
        
        # Get active tasks
        tasks_response = db.table("tasks").select("*").eq("assignee_id", user_id).in_("status", ["not_started", "in_progress"]).execute()
        active_tasks = tasks_response.data or []
        
        # Get blocking incidents
        incidents_response = db.table("incidents").select("*").eq("assigned_to_id", user_id).eq("status", "open").execute()
        blocking_incidents = incidents_response.data or []
        
        return {
            "user_id": user_id,
            "name": user["name"],
            "email": user["email"],
            "workload": {
                "current_workload_percent": user.get("current_workload_percent", 0),
                "weekly_capacity": user.get("weekly_capacity", 40),
                "assignment_status": user.get("assignment_status", "unassigned")
            },
            "projects": {
                "active_count": len(project_ids),
                "project_ids": project_ids
            },
            "tasks": {
                "active_count": len(active_tasks),
                "tasks": active_tasks
            },
            "incidents": {
                "blocking_count": len(blocking_incidents),
                "incidents": blocking_incidents
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workload: {str(e)}"
        )


# ============================================================================
# GET USER PROJECTS
# ============================================================================

@router.get("/{user_id}/projects")
async def get_user_projects(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all projects assigned to user"""
    try:
        # Get project memberships
        memberships = db.table("project_members").select("*").eq("user_id", user_id).execute()
        
        if not memberships.data or len(memberships.data) == 0:
            return {"projects": [], "total": 0}
        
        # Get project IDs
        project_ids = [m["project_id"] for m in memberships.data]
        
        # Get projects
        projects = db.table("projects").select("*").in_("id", project_ids).execute()
        
        return {
            "projects": projects.data or [],
            "total": len(projects.data or [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects: {str(e)}"
        )


# ============================================================================
# GET USER TASKS
# ============================================================================

@router.get("/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all tasks assigned to user"""
    try:
        query = db.table("tasks").select("*").eq("assignee_id", user_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.execute()
        
        return {
            "tasks": response.data or [],
            "total": len(response.data or [])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )
