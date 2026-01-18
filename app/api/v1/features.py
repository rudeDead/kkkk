"""
Dashboard, Analytics, Chatbot, Profile APIs
Enhanced with comprehensive real data analytics from database
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.core.dependencies import get_current_active_user
from app.database import get_db
from pydantic import BaseModel, EmailStr


# ============================================================================
# DASHBOARD ROUTER
# ============================================================================
dashboard_router = APIRouter()

# ============================================================================
# COMPREHENSIVE HELPER FUNCTIONS
# ============================================================================

def calculate_team_utilization(db: Client) -> List[Dict]:
    """Calculate utilization for each tech team"""
    try:
        teams_response = db.table("tech_teams").select("id, name").execute()
        teams = teams_response.data or []
        
        utilization_data = []
        
        for team in teams:
            members_response = db.table("tech_team_members").select(
                "user_id"
            ).eq("team_id", team["id"]).execute()
            
            member_ids = [m["user_id"] for m in (members_response.data or [])]
            
            if not member_ids:
                continue
            
            users_response = db.table("users").select(
                "current_workload_percent"
            ).in_("id", member_ids).execute()
            
            workloads = [u.get("current_workload_percent", 0) for u in (users_response.data or [])]
            
            if workloads:
                avg_utilization = sum(workloads) / len(workloads)
                utilization_data.append({
                    "team": team["name"],
                    "utilization": round(avg_utilization, 1),
                    "members": len(workloads)
                })
        
        return sorted(utilization_data, key=lambda x: x["utilization"], reverse=True)
    
    except Exception as e:
        print(f"Error calculating team utilization: {e}")
        return []


def get_tasks_at_risk(db: Client, user_id: str, user_role: str) -> List[Dict]:
    """Get tasks that are blocked or at risk"""
    try:
        tasks_response = db.table("tasks").select(
            "id, title, status, priority, due_date, blocked_reason, "
            "project_id, assignee_id, "
            "projects(name), "
            "users!tasks_assignee_id_fkey(name, avatar_url)"
        ).in_("status", ["blocked", "in_progress"]).in_(
            "priority", ["high", "critical"]
        ).limit(5).execute()
        
        tasks = []
        for task in (tasks_response.data or []):
            assignee = task.get("users", {}) if task.get("users") else {}
            project = task.get("projects", {}) if task.get("projects") else {}
            
            tasks.append({
                "id": task["id"],
                "name": task["title"],
                "status": task["status"],
                "priority": task["priority"],
                "project": project.get("name", "Unknown"),
                "assignee": assignee.get("name", "Unassigned"),
                "avatar": assignee.get("avatar_url", ""),
                "dueDate": task.get("due_date", "No deadline")
            })
        
        return tasks
    
    except Exception as e:
        print(f"Error getting tasks at risk: {e}")
        return []


def get_upcoming_deadlines(db: Client, user_id: str, user_role: str) -> List[Dict]:
    """Get projects with upcoming deadlines"""
    try:
        thirty_days = (datetime.now() + timedelta(days=30)).date().isoformat()
        today = datetime.now().date().isoformat()
        
        projects_response = db.table("projects").select(
            "id, name, priority, progress, deadline, status"
        ).eq("status", "active").gte(
            "deadline", today
        ).lte(
            "deadline", thirty_days
        ).order("deadline").limit(5).execute()
        
        projects = []
        for project in (projects_response.data or []):
            if project.get("deadline"):
                deadline = datetime.fromisoformat(project["deadline"]).date()
                days_left = (deadline - datetime.now().date()).days
                
                projects.append({
                    "id": project["id"],
                    "name": project["name"],
                    "priority": project["priority"],
                    "progress": project.get("progress", 0),
                    "daysLeft": max(0, days_left)
                })
        
        return projects
    
    except Exception as e:
        print(f"Error getting upcoming deadlines: {e}")
        return []


def get_project_distribution(db: Client) -> List[Dict]:
    """Get project distribution by status"""
    try:
        projects_response = db.table("projects").select("status").execute()
        
        status_counts = {}
        for project in (projects_response.data or []):
            status = project.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        colors = {
            "planning": "#3b82f6",
            "active": "#10b981",
            "on_hold": "#f59e0b",
            "completed": "#6366f1",
            "cancelled": "#ef4444"
        }
        
        return [
            {
                "name": status.replace("_", " ").title(),
                "value": count,
                "color": colors.get(status, "#6b7280")
            }
            for status, count in status_counts.items()
        ]
    
    except Exception as e:
        print(f"Error getting project distribution: {e}")
        return []


def get_weekly_productivity(db: Client) -> List[Dict]:
    """Get task completion trend for last 7 days"""
    try:
        productivity = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).date()
            
            tasks_response = db.table("tasks").select("id").gte(
                "completed_at", date.isoformat()
            ).lt(
                "completed_at", (date + timedelta(days=1)).isoformat()
            ).execute()
            
            productivity.append({
                "day": days[date.weekday()],
                "tasks": len(tasks_response.data or [])
            })
        
        return productivity
    
    except Exception as e:
        print(f"Error getting weekly productivity: {e}")
        return [{"day": day, "tasks": 0} for day in days]


def get_leave_analytics(db: Client) -> Dict:
    """Get comprehensive leave analytics"""
    try:
        # Pending leaves by status
        pending_response = db.table("leaves").select("status").in_(
            "status", ["pending_hr_review", "forwarded_to_team_lead", "pending_l7_decision"]
        ).execute()
        
        # Approved leaves this month
        month_start = datetime.now().replace(day=1).date().isoformat()
        approved_response = db.table("leaves").select("id").eq(
            "status", "approved"
        ).gte("approved_at", month_start).execute()
        
        # Leaves by type
        all_leaves = db.table("leaves").select("leave_type").execute()
        leave_types = {}
        for leave in (all_leaves.data or []):
            ltype = leave.get("leave_type", "unknown")
            leave_types[ltype] = leave_types.get(ltype, 0) + 1
        
        return {
            "pending": len(pending_response.data or []),
            "approved_this_month": len(approved_response.data or []),
            "by_type": leave_types
        }
    except Exception as e:
        print(f"Error getting leave analytics: {e}")
        return {"pending": 0, "approved_this_month": 0, "by_type": {}}


def get_incident_analytics(db: Client) -> Dict:
    """Get comprehensive incident analytics"""
    try:
        # Open incidents by severity
        open_response = db.table("incidents").select("severity, status").in_(
            "status", ["open", "in_progress"]
        ).execute()
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for incident in (open_response.data or []):
            severity = incident.get("severity", "low")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Resolved this week
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        resolved_response = db.table("incidents").select("id").eq(
            "status", "resolved"
        ).gte("resolved_at", week_ago).execute()
        
        return {
            "open_total": len(open_response.data or []),
            "by_severity": severity_counts,
            "resolved_this_week": len(resolved_response.data or [])
        }
    except Exception as e:
        print(f"Error getting incident analytics: {e}")
        return {"open_total": 0, "by_severity": {}, "resolved_this_week": 0}


def get_employee_analytics(db: Client) -> Dict:
    """Get employee distribution and workload analytics"""
    try:
        users_response = db.table("users").select(
            "status, role, hierarchy_level, current_workload_percent"
        ).execute()
        
        users = users_response.data or []
        
        # Status distribution
        status_counts = {}
        for user in users:
            status = user.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Role distribution
        role_counts = {}
        for user in users:
            role = user.get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        # Workload distribution
        active_users = [u for u in users if u.get("status") == "active"]
        overloaded = len([u for u in active_users if u.get("current_workload_percent", 0) > 85])
        underutilized = len([u for u in active_users if u.get("current_workload_percent", 0) < 50])
        
        return {
            "total": len(users),
            "by_status": status_counts,
            "by_role": role_counts,
            "overloaded": overloaded,
            "underutilized": underutilized
        }
    except Exception as e:
        print(f"Error getting employee analytics: {e}")
        return {"total": 0, "by_status": {}, "by_role": {}, "overloaded": 0, "underutilized": 0}


def get_esp_analytics(db: Client) -> Dict:
    """Get ESP package analytics"""
    try:
        esp_response = db.table("esp_packages").select("status").execute()
        
        status_counts = {}
        for esp in (esp_response.data or []):
            status = esp.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(esp_response.data or []),
            "by_status": status_counts
        }
    except Exception as e:
        print(f"Error getting ESP analytics: {e}")
        return {"total": 0, "by_status": {}}


def get_upcoming_events(db: Client) -> List[Dict]:
    """Get upcoming events in next 7 days"""
    try:
        today = datetime.now().isoformat()
        week_later = (datetime.now() + timedelta(days=7)).isoformat()
        
        events_response = db.table("events").select(
            "id, name, event_type, start_datetime, location, is_virtual"
        ).gte("start_datetime", today).lte(
            "start_datetime", week_later
        ).order("start_datetime").limit(5).execute()
        
        events = []
        for event in (events_response.data or []):
            events.append({
                "id": event["id"],
                "name": event["name"],
                "type": event.get("event_type", "meeting"),
                "date": event.get("start_datetime", ""),
                "location": event.get("location", "Virtual") if not event.get("is_virtual") else "Virtual"
            })
        
        return events
    except Exception as e:
        print(f"Error getting upcoming events: {e}")
        return []


def get_software_requests_analytics(db: Client) -> Dict:
    """Get software request analytics"""
    try:
        requests_response = db.table("software_requests").select("status, urgency").execute()
        
        status_counts = {}
        urgency_counts = {}
        
        for req in (requests_response.data or []):
            status = req.get("status", "unknown")
            urgency = req.get("urgency", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
        
        return {
            "total": len(requests_response.data or []),
            "by_status": status_counts,
            "by_urgency": urgency_counts
        }
    except Exception as e:
        print(f"Error getting software requests analytics: {e}")
        return {"total": 0, "by_status": {}, "by_urgency": {}}


@dashboard_router.get("/")
async def get_dashboard(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get comprehensive dashboard data with rich analytics"""
    try:
        user_role = current_user.get("role")
        user_id = current_user["id"]
        
        # ========================================================================
        # 1. CORE KPIs
        # ========================================================================
        
        # Active Projects
        active_projects_response = db.table("projects").select("id").eq("status", "active").execute()
        active_projects_count = len(active_projects_response.data or [])
        
        # Completed Tasks (this week)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        completed_tasks_response = db.table("tasks").select("id").eq(
            "status", "completed"
        ).gte("completed_at", week_ago).execute()
        completed_tasks_count = len(completed_tasks_response.data or [])
        
        # Total Team Members
        active_users_response = db.table("users").select("id").eq("status", "active").execute()
        total_members = len(active_users_response.data or [])
        
        # Pending Leaves
        pending_leaves_response = db.table("leaves").select("id").in_(
            "status", ["pending_hr_review", "forwarded_to_team_lead", "pending_l7_decision"]
        ).execute()
        pending_leaves_count = len(pending_leaves_response.data or [])
        
        # Open Incidents
        open_incidents_response = db.table("incidents").select("id, severity").in_(
            "status", ["open", "in_progress"]
        ).execute()
        open_incidents_count = len(open_incidents_response.data or [])
        critical_incidents = len([i for i in (open_incidents_response.data or []) if i.get("severity") == "critical"])
        
        # ========================================================================
        # 2. ORGANIZATION HEALTH
        # ========================================================================
        
        all_projects_response = db.table("projects").select("risk_level").eq("status", "active").execute()
        low_risk_projects = len([p for p in (all_projects_response.data or []) if p.get("risk_level") == "low"])
        project_health = (low_risk_projects / max(len(all_projects_response.data or []), 1)) * 100
        
        all_tasks_response = db.table("tasks").select("status").execute()
        completed_tasks_all = len([t for t in (all_tasks_response.data or []) if t.get("status") == "completed"])
        task_completion_rate = (completed_tasks_all / max(len(all_tasks_response.data or []), 1)) * 100
        
        all_users_workload = db.table("users").select("current_workload_percent").eq("status", "active").execute()
        avg_workload = sum([u.get("current_workload_percent", 0) for u in (all_users_workload.data or [])]) / max(len(all_users_workload.data or []), 1)
        
        incident_sla = 85  # Placeholder
        
        # ========================================================================
        # 3. CHARTS DATA
        # ========================================================================
        
        project_distribution = get_project_distribution(db)
        weekly_productivity = get_weekly_productivity(db)
        team_utilization = calculate_team_utilization(db)
        
        # ========================================================================
        # 4. TASKS & DEADLINES
        # ========================================================================
        
        tasks_at_risk = get_tasks_at_risk(db, user_id, user_role)
        upcoming_deadlines = get_upcoming_deadlines(db, user_id, user_role)
        
        # ========================================================================
        # 5. COMPREHENSIVE ANALYTICS
        # ========================================================================
        
        leave_analytics = get_leave_analytics(db)
        incident_analytics = get_incident_analytics(db)
        employee_analytics = get_employee_analytics(db)
        esp_analytics = get_esp_analytics(db)
        software_analytics = get_software_requests_analytics(db)
        upcoming_events = get_upcoming_events(db)
        
        # ========================================================================
        # 6. ALERTS
        # ========================================================================
        
        alerts = []
        
        # Overutilized teams
        for team in team_utilization:
            if team["utilization"] > 85:
                alerts.append({
                    "type": "warning",
                    "title": f"{team['team']} Overutilized",
                    "message": f"Team utilization at {team['utilization']}%",
                    "action": "Review workload distribution"
                })
        
        # Blocked tasks
        if len(tasks_at_risk) > 0:
            blocked_count = len([t for t in tasks_at_risk if t["status"] == "blocked"])
            if blocked_count > 0:
                alerts.append({
                    "type": "danger",
                    "title": f"{blocked_count} Blocked Tasks",
                    "message": "Tasks are blocked and need attention",
                    "action": "Review blocked tasks"
                })
        
        # Critical incidents
        if critical_incidents > 0:
            alerts.append({
                "type": "danger",
                "title": f"{critical_incidents} Critical Incidents",
                "message": "Critical incidents require immediate attention",
                "action": "View Incidents"
            })
        
        # Pending leaves
        if pending_leaves_count > 10:
            alerts.append({
                "type": "warning",
                "title": f"{pending_leaves_count} Pending Leaves",
                "message": "Many leave requests awaiting approval",
                "action": "Review Leaves"
            })
        
        # ========================================================================
        # BUILD COMPREHENSIVE RESPONSE
        # ========================================================================
        
        return {
            "kpis": {
                "activeProjects": {
                    "value": active_projects_count,
                    "trend": 5,
                    "trendDirection": "up"
                },
                "completedTasks": {
                    "value": completed_tasks_count,
                    "trend": 12,
                    "trendDirection": "up",
                    "period": "this week"
                },
                "totalTeamMembers": {
                    "value": total_members,
                    "trend": 2,
                    "trendDirection": "up"
                },
                "pendingLeaves": {
                    "value": pending_leaves_count,
                    "trend": 3,
                    "trendDirection": "down"
                },
                "openIncidents": {
                    "value": open_incidents_count,
                    "critical": critical_incidents
                }
            },
            "health": {
                "projectHealth": round(project_health, 1),
                "taskCompletionRate": round(task_completion_rate, 1),
                "capacityUtilization": round(avg_workload, 1),
                "incidentSLA": incident_sla
            },
            "projectDistribution": project_distribution,
            "productivity": weekly_productivity,
            "teamUtilization": team_utilization,
            "tasksAtRisk": tasks_at_risk,
            "upcomingDeadlines": upcoming_deadlines,
            "recentActivity": [],
            "alerts": alerts,
            "quickActions": [
                {"label": "Create Project", "icon": "FolderPlus", "route": "/app/projects/new"},
                {"label": "Assign Task", "icon": "UserPlus", "route": "/app/tasks/new"},
                {"label": "View Reports", "icon": "BarChart", "route": "/app/analytics"},
            ],
            # Extended Analytics
            "analytics": {
                "leaves": leave_analytics,
                "incidents": incident_analytics,
                "employees": employee_analytics,
                "esp": esp_analytics,
                "softwareRequests": software_analytics
            },
            "upcomingEvents": upcoming_events
        }
    
    except Exception as e:
        import traceback
        print(f"Dashboard error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")


# ============================================================================
# ANALYTICS ROUTER
# ============================================================================
analytics_router = APIRouter()

@analytics_router.get("/projects")
async def get_project_analytics(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get project analytics"""
    try:
        projects = db.table("projects").select("*").execute()
        
        total = len(projects.data or [])
        by_status = {}
        by_priority = {}
        by_type = {}
        
        for project in (projects.data or []):
            status = project.get("status", "unknown")
            priority = project.get("priority", "unknown")
            ptype = project.get("project_type", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
            by_type[ptype] = by_type.get(ptype, 0) + 1
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_type": by_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/tasks")
async def get_task_analytics(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get task analytics"""
    try:
        tasks = db.table("tasks").select("*").execute()
        
        by_status = {}
        by_priority = {}
        
        for task in (tasks.data or []):
            status = task.get("status", "unknown")
            priority = task.get("priority", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return {
            "total": len(tasks.data or []),
            "by_status": by_status,
            "by_priority": by_priority,
            "tasks": tasks.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get("/teams")
async def get_team_analytics(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get team analytics"""
    try:
        teams = db.table("tech_teams").select("*").execute()
        
        return {
            "total": len(teams.data or []),
            "teams": teams.data or []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PROFILE ROUTER
# ============================================================================
profile_router = APIRouter()

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    skills: Optional[list] = None
    experience_years: Optional[int] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@profile_router.get("/")
async def get_profile(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get current user profile with stats"""
    try:
        user = db.table("users").select("*").eq("id", current_user["id"]).execute()
        
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = user.data[0]
        
        projects_count = db.table("project_members").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        tasks_count = db.table("tasks").select("id", count="exact").eq("assignee_id", current_user["id"]).execute()
        teams_count = db.table("tech_team_members").select("id", count="exact").eq("user_id", current_user["id"]).execute()
        
        profile["stats"] = {
            "projects": projects_count.count or 0,
            "tasks": tasks_count.count or 0,
            "teams": teams_count.count or 0
        }
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@profile_router.put("/")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Update current user profile"""
    try:
        update_data = {}
        
        if profile_data.name is not None:
            update_data["name"] = profile_data.name
        if profile_data.email is not None:
            update_data["email"] = profile_data.email
        if profile_data.skills is not None:
            update_data["skills"] = profile_data.skills
        if profile_data.experience_years is not None:
            update_data["experience_years"] = profile_data.experience_years
        if profile_data.department is not None:
            update_data["department"] = profile_data.department
        if profile_data.avatar_url is not None:
            update_data["avatar_url"] = profile_data.avatar_url
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        update_data["updated_at"] = datetime.now().isoformat()
        
        response = db.table("users").update(update_data).eq("id", current_user["id"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update profile")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@profile_router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Change user password"""
    try:
        from app.core.security import verify_password, get_password_hash
        
        user = db.table("users").select("password_hash").eq("id", current_user["id"]).execute()
        
        if not user.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not verify_password(password_data.current_password, user.data[0]["password_hash"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        new_password_hash = get_password_hash(password_data.new_password)
        db.table("users").update({"password_hash": new_password_hash}).eq("id", current_user["id"]).execute()
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
