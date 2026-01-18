"""
Dashboard API
Provides comprehensive dashboard data from database
"""

from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.core.rbac import is_admin, Roles

dashboard_router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_team_utilization(db: Client) -> List[Dict]:
    """Calculate utilization for each tech team"""
    try:
        # Get all tech teams
        teams_response = db.table("tech_teams").select("id, name").execute()
        teams = teams_response.data or []
        
        utilization_data = []
        
        for team in teams:
            # Get team members
            members_response = db.table("tech_team_members").select(
                "user_id"
            ).eq("team_id", team["id"]).execute()
            
            member_ids = [m["user_id"] for m in (members_response.data or [])]
            
            if not member_ids:
                continue
            
            # Get workload for team members
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
        # Build query based on role
        query = db.table("tasks").select(
            "id, title, status, priority, due_date, blocked_reason, "
            "project_id, assignee_id, "
            "projects(name), "
            "users!assignee_id(name, avatar_url)"
        )
        
        # Filter based on role
        if user_role == Roles.TECHNICAL_LEAD:
            # TL sees tasks from their team members
            team_response = db.table("tech_teams").select("id").eq("team_lead_id", user_id).execute()
            if team_response.data:
                team_ids = [t["id"] for t in team_response.data]
                member_response = db.table("tech_team_members").select("user_id").in_("team_id", team_ids).execute()
                member_ids = [m["user_id"] for m in (member_response.data or [])]
                query = query.in_("assignee_id", member_ids)
        
        elif user_role == Roles.PROJECT_MANAGER:
            # PM sees tasks from their projects
            project_response = db.table("projects").select("id").eq("project_manager_id", user_id).execute()
            project_ids = [p["id"] for p in (project_response.data or [])]
            query = query.in_("project_id", project_ids)
        
        # Get blocked or high priority tasks
        tasks_response = query.in_("status", ["blocked", "in_progress"]).in_(
            "priority", ["high", "critical"]
        ).limit(5).execute()
        
        tasks = []
        for task in (tasks_response.data or []):
            assignee = task.get("users", {})
            project = task.get("projects", {})
            
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
        # Calculate date 30 days from now
        thirty_days = (datetime.now() + timedelta(days=30)).date().isoformat()
        
        # Build query based on role
        query = db.table("projects").select(
            "id, name, priority, progress, deadline, status"
        )
        
        # Filter based on role
        if user_role == Roles.PROJECT_MANAGER:
            query = query.eq("project_manager_id", user_id)
        elif user_role == Roles.TECHNICAL_LEAD:
            query = query.eq("team_lead_id", user_id)
        
        # Get projects with deadlines in next 30 days
        projects_response = query.eq("status", "active").lte(
            "deadline", thirty_days
        ).order("deadline").limit(5).execute()
        
        projects = []
        for project in (projects_response.data or []):
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
            
            # Get tasks completed on this day
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
        # Return dummy data if error
        return [
            {"day": "Mon", "tasks": 0},
            {"day": "Tue", "tasks": 0},
            {"day": "Wed", "tasks": 0},
            {"day": "Thu", "tasks": 0},
            {"day": "Fri", "tasks": 0},
            {"day": "Sat", "tasks": 0},
            {"day": "Sun", "tasks": 0}
        ]


# ============================================================================
# MAIN DASHBOARD ENDPOINT
# ============================================================================

@dashboard_router.get("/")
async def get_dashboard(
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive dashboard data
    Access: Admin, HR, PM, TL only
    """
    try:
        user_role = current_user.get("role")
        user_id = current_user["id"]
        
        # Check access
        if user_role not in [Roles.ADMIN, Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            raise HTTPException(status_code=403, detail="Access denied. Dashboard is for Admin, HR, PM, and TL only.")
        
        # ========================================================================
        # 1. KPIs
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
        # 2. Organization Health
        # ========================================================================
        
        # Project Health (% of projects on track)
        all_projects_response = db.table("projects").select("risk_level").eq("status", "active").execute()
        low_risk_projects = len([p for p in (all_projects_response.data or []) if p.get("risk_level") == "low"])
        project_health = (low_risk_projects / max(len(all_projects_response.data or []), 1)) * 100
        
        # Task Completion Rate
        all_tasks_response = db.table("tasks").select("status").execute()
        completed_tasks_all = len([t for t in (all_tasks_response.data or []) if t.get("status") == "completed"])
        task_completion_rate = (completed_tasks_all / max(len(all_tasks_response.data or []), 1)) * 100
        
        # Capacity Utilization
        all_users_workload = db.table("users").select("current_workload_percent").eq("status", "active").execute()
        avg_workload = sum([u.get("current_workload_percent", 0) for u in (all_users_workload.data or [])]) / max(len(all_users_workload.data or []), 1)
        
        # Incident SLA (% resolved within 24h)
        incident_sla = 85  # Placeholder - would need resolution time tracking
        
        # ========================================================================
        # 3. Charts Data
        # ========================================================================
        
        project_distribution = get_project_distribution(db)
        weekly_productivity = get_weekly_productivity(db)
        team_utilization = calculate_team_utilization(db)
        
        # ========================================================================
        # 4. Tasks & Deadlines
        # ========================================================================
        
        tasks_at_risk = get_tasks_at_risk(db, user_id, user_role)
        upcoming_deadlines = get_upcoming_deadlines(db, user_id, user_role)
        
        # ========================================================================
        # 5. Recent Activity (placeholder - would need activity log table)
        # ========================================================================
        
        recent_activity = []
        
        # ========================================================================
        # 6. Alerts
        # ========================================================================
        
        alerts = []
        
        # Check for overutilized teams
        for team in team_utilization:
            if team["utilization"] > 85:
                alerts.append({
                    "type": "warning",
                    "title": f"{team['team']} Overutilized",
                    "message": f"Team utilization at {team['utilization']}%",
                    "action": "Review workload distribution"
                })
        
        # Check for blocked tasks
        if len(tasks_at_risk) > 0:
            blocked_count = len([t for t in tasks_at_risk if t["status"] == "blocked"])
            if blocked_count > 0:
                alerts.append({
                    "type": "danger",
                    "title": f"{blocked_count} Blocked Tasks",
                    "message": "Tasks are blocked and need attention",
                    "action": "Review blocked tasks"
                })
        
        # ========================================================================
        # 7. Quick Actions
        # ========================================================================
        
        quick_actions = [
            {"label": "Create Project", "icon": "FolderPlus", "route": "/app/projects/new"},
            {"label": "Assign Task", "icon": "UserPlus", "route": "/app/tasks/new"},
            {"label": "View Reports", "icon": "BarChart", "route": "/app/analytics"},
        ]
        
        # ========================================================================
        # BUILD RESPONSE
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
            "recentActivity": recent_activity,
            "alerts": alerts,
            "quickActions": quick_actions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Dashboard error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error loading dashboard: {str(e)}")
