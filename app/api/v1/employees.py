"""
Employees API Endpoints
Enhanced employee management with dashboard statistics and detailed information
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.core.dependencies import get_current_active_user
from app.database import get_db

employees_router = APIRouter()


# ============================================================================
# GET EMPLOYEE DASHBOARD DATA
# ============================================================================

@employees_router.get("/{employee_id}/dashboard")
async def get_employee_dashboard(
    employee_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive employee dashboard data
    
    Returns:
    - Employee profile
    - Workload statistics
    - Active projects
    - Active tasks
    - Leave balance
    - Recent incidents
    - Performance metrics
    """
    try:
        # Get employee details
        employee_response = db.table("users").select("*").eq("id", employee_id).execute()
        
        if not employee_response.data or len(employee_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found"
            )
        
        employee = employee_response.data[0]
        
        # Get active projects count
        project_members = db.table("project_members").select("project_id").eq("user_id", employee_id).execute()
        project_ids = [pm["project_id"] for pm in (project_members.data or [])]
        
        active_projects = []
        if project_ids:
            projects_response = db.table("projects").select("*").in_("id", project_ids).eq("status", "active").execute()
            active_projects = projects_response.data or []
        
        # Get tasks statistics
        tasks_response = db.table("tasks").select("*").eq("assignee_id", employee_id).execute()
        all_tasks = tasks_response.data or []
        
        active_tasks = [t for t in all_tasks if t.get("status") in ["not_started", "in_progress"]]
        completed_tasks = [t for t in all_tasks if t.get("status") == "completed"]
        blocked_tasks = [t for t in all_tasks if t.get("status") == "blocked"]
        
        # Get leave balance
        leaves_response = db.table("leaves").select("*").eq("employee_id", employee_id).execute()
        all_leaves = leaves_response.data or []
        
        approved_leaves = [l for l in all_leaves if l.get("status") == "approved"]
        pending_leaves = [l for l in all_leaves if "pending" in l.get("status", "")]
        
        total_leave_days_used = sum(l.get("days", 0) for l in approved_leaves)
        pending_leave_days = sum(l.get("days", 0) for l in pending_leaves)
        
        # Get incidents
        incidents_response = db.table("incidents").select("*").eq("owner_id", employee_id).execute()
        all_incidents = incidents_response.data or []
        
        open_incidents = [i for i in all_incidents if i.get("status") != "resolved"]
        critical_incidents = [i for i in open_incidents if i.get("severity") in ["high", "critical"]]
        
        # Calculate workload
        workload_percent = employee.get("current_workload_percent", 0)
        weekly_capacity = employee.get("weekly_capacity", 40)
        
        # Get manager info
        manager = None
        if employee.get("manager_id"):
            manager_response = db.table("users").select("id, name, email, role").eq("id", employee["manager_id"]).execute()
            if manager_response.data:
                manager = manager_response.data[0]
        
        return {
            "employee": {
                "id": employee["id"],
                "name": employee["name"],
                "email": employee["email"],
                "phone": employee.get("phone"),
                "role": employee.get("role"),
                "hierarchy_level": employee.get("hierarchy_level"),
                "department": employee.get("department"),
                "status": employee.get("status", "active"),
                "skills": employee.get("skills", []),
                "experience_years": employee.get("experience_years", 0),
                "weekly_capacity": weekly_capacity,
                "is_active": employee.get("is_active", True),
                "created_at": employee.get("created_at"),
                "manager": manager
            },
            "workload": {
                "current_workload_percent": workload_percent,
                "weekly_capacity": weekly_capacity,
                "assignment_status": employee.get("assignment_status", "available"),
                "active_project_count": len(active_projects),
                "active_task_count": len(active_tasks)
            },
            "projects": {
                "total": len(active_projects),
                "active": active_projects[:5]  # Top 5 active projects
            },
            "tasks": {
                "total": len(all_tasks),
                "active": len(active_tasks),
                "completed": len(completed_tasks),
                "blocked": len(blocked_tasks),
                "recent_tasks": active_tasks[:10]  # Top 10 active tasks
            },
            "leaves": {
                "annual_quota": 20,  # Standard quota
                "used": total_leave_days_used,
                "pending": pending_leave_days,
                "remaining": 20 - total_leave_days_used,
                "total_requests": len(all_leaves),
                "recent_leaves": all_leaves[:5]  # Recent 5 leaves
            },
            "incidents": {
                "total": len(all_incidents),
                "open": len(open_incidents),
                "critical": len(critical_incidents),
                "recent_incidents": open_incidents[:5]  # Recent 5 open incidents
            },
            "performance": {
                "task_completion_rate": (len(completed_tasks) / len(all_tasks) * 100) if all_tasks else 0,
                "on_time_delivery": 85,  # Placeholder - calculate from task deadlines
                "quality_score": 90  # Placeholder - calculate from feedback
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch employee dashboard: {str(e)}\n{traceback.format_exc()}"
        )


# ============================================================================
# GET EMPLOYEE SKILLS
# ============================================================================

@employees_router.get("/{employee_id}/skills")
async def get_employee_skills(
    employee_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get employee skills and expertise"""
    try:
        employee_response = db.table("users").select("id, name, skills, experience_years").eq("id", employee_id).execute()
        
        if not employee_response.data:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee = employee_response.data[0]
        skills = employee.get("skills", [])
        
        # Get tasks that used these skills
        tasks_response = db.table("tasks").select("*").eq("assignee_id", employee_id).execute()
        tasks = tasks_response.data or []
        
        # Calculate skill proficiency based on task completion
        skill_stats = {}
        for skill in skills:
            skill_tasks = [t for t in tasks if skill.lower() in str(t.get("required_skills", [])).lower()]
            completed = [t for t in skill_tasks if t.get("status") == "completed"]
            
            skill_stats[skill] = {
                "name": skill,
                "proficiency": min(100, 60 + (employee.get("experience_years", 0) * 5)),  # Base proficiency
                "tasks_completed": len(completed),
                "total_tasks": len(skill_tasks)
            }
        
        return {
            "employee_id": employee_id,
            "name": employee["name"],
            "skills": list(skill_stats.values()),
            "total_skills": len(skills),
            "experience_years": employee.get("experience_years", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch skills: {str(e)}"
        )


# ============================================================================
# GET EMPLOYEE INCIDENTS
# ============================================================================

@employees_router.get("/{employee_id}/incidents")
async def get_employee_incidents(
    employee_id: str,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get incidents owned by or assigned to employee"""
    try:
        # Get incidents owned by employee
        query = db.table("incidents").select("*").eq("owner_id", employee_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.execute()
        incidents = response.data or []
        
        # Categorize incidents
        open_incidents = [i for i in incidents if i.get("status") != "resolved"]
        critical_incidents = [i for i in incidents if i.get("severity") in ["high", "critical"]]
        
        return {
            "incidents": incidents,
            "total": len(incidents),
            "open": len(open_incidents),
            "critical": len(critical_incidents),
            "by_severity": {
                "critical": len([i for i in incidents if i.get("severity") == "critical"]),
                "high": len([i for i in incidents if i.get("severity") == "high"]),
                "medium": len([i for i in incidents if i.get("severity") == "medium"]),
                "low": len([i for i in incidents if i.get("severity") == "low"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch incidents: {str(e)}"
        )


# ============================================================================
# GET EMPLOYEE LEAVES
# ============================================================================

@employees_router.get("/{employee_id}/leaves")
async def get_employee_leaves(
    employee_id: str,
    status_filter: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get leave requests for employee"""
    try:
        query = db.table("leaves").select("*").eq("employee_id", employee_id)
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.order("created_at", desc=True).execute()
        leaves = response.data or []
        
        # Calculate leave balance
        approved_leaves = [l for l in leaves if l.get("status") == "approved"]
        pending_leaves = [l for l in leaves if "pending" in l.get("status", "")]
        
        total_used = sum(l.get("days", 0) for l in approved_leaves)
        total_pending = sum(l.get("days", 0) for l in pending_leaves)
        
        return {
            "leaves": leaves,
            "total": len(leaves),
            "balance": {
                "annual_quota": 20,
                "used": total_used,
                "pending": total_pending,
                "remaining": 20 - total_used
            },
            "by_status": {
                "approved": len(approved_leaves),
                "pending": len(pending_leaves),
                "rejected": len([l for l in leaves if l.get("status") == "rejected"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch leaves: {str(e)}"
        )


# ============================================================================
# GET EMPLOYEE PERFORMANCE METRICS
# ============================================================================

@employees_router.get("/{employee_id}/performance")
async def get_employee_performance(
    employee_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get employee performance metrics"""
    try:
        # Get all tasks
        tasks_response = db.table("tasks").select("*").eq("assignee_id", employee_id).execute()
        tasks = tasks_response.data or []
        
        # Get all projects
        project_members = db.table("project_members").select("*").eq("user_id", employee_id).execute()
        
        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t.get("status") == "completed"])
        on_time_tasks = len([t for t in tasks if t.get("status") == "completed" and t.get("completed_on_time", True)])
        
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        on_time_rate = (on_time_tasks / completed_tasks * 100) if completed_tasks > 0 else 0
        
        return {
            "employee_id": employee_id,
            "metrics": {
                "task_completion_rate": round(completion_rate, 2),
                "on_time_delivery_rate": round(on_time_rate, 2),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "active_projects": len(project_members.data or []),
                "quality_score": 90,  # Placeholder
                "productivity_score": 85  # Placeholder
            },
            "trends": {
                "last_30_days": {
                    "tasks_completed": completed_tasks,  # Should filter by date
                    "avg_completion_time": "3.5 days"  # Placeholder
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch performance metrics: {str(e)}"
        )
