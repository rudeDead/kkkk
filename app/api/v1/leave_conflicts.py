"""
Leave Conflicts Detection API
Rule-based conflict detection following the enterprise logic
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional, List, Dict
from datetime import datetime, date, timedelta
from app.core.dependencies import get_current_active_user
from app.database import get_db
from app.core.rbac import is_admin, Roles

leave_conflicts_router = APIRouter()


def calculate_skill_match(required_skills: dict, employee_skills: dict) -> float:
    """Calculate skill match percentage"""
    if not required_skills:
        return 100.0
    
    total_weight = sum(required_skills.values())
    matched_weight = 0
    
    for skill, weight in required_skills.items():
        if employee_skills.get(skill, 0) >= 60:
            matched_weight += weight
    
    return (matched_weight / total_weight) * 100 if total_weight > 0 else 0


def calculate_workload(employee_id: str, db: Client) -> int:
    """Calculate employee workload (0-100)"""
    weight_map = {"critical": 40, "high": 30, "medium": 20, "low": 10}
    
    tasks = db.table("tasks").select("priority").eq("assignee_id", employee_id).neq("status", "completed").execute()
    
    workload = sum(weight_map.get(t.get("priority", "medium"), 20) for t in (tasks.data or []))
    return min(workload, 100)


def has_blocking_incident(employee_id: str, db: Client) -> bool:
    """Check if employee has blocking incidents"""
    incidents = db.table("incidents").select("id").eq("owner_id", employee_id).neq("status", "resolved").in_("severity", ["high", "critical"]).execute()
    return len(incidents.data or []) > 0


def find_valid_alternate(employee_id: str, critical_task: dict, db: Client) -> Optional[Dict]:
    """Find valid alternate for critical task"""
    # Get all potential alternates (same team or similar skills)
    users = db.table("users").select("id, name, skills").eq("status", "active").execute()
    
    for user in (users.data or []):
        if user["id"] == employee_id:
            continue
        
        alt_id = user["id"]
        alt_skills = user.get("skills", [])
        
        # Convert skills list to dict for matching
        skills_dict = {skill: 80 for skill in alt_skills} if isinstance(alt_skills, list) else {}
        
        skill_match = calculate_skill_match(critical_task.get("required_skills", {}), skills_dict)
        workload = calculate_workload(alt_id, db)
        availability = 100 - workload
        has_incident = has_blocking_incident(alt_id, db)
        
        if skill_match >= 80 and availability >= 30 and not has_incident:
            return {
                "id": alt_id,
                "name": user["name"],
                "skill_match": skill_match,
                "availability": availability
            }
    
    return None


@leave_conflicts_router.get("/analyze/{leave_id}")
async def analyze_leave_conflict(
    leave_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Analyze leave request for conflicts using enterprise rule-based logic
    
    Returns:
    - HR validation status
    - Resource hold check
    - Pending tasks check
    - Incident hard block check
    - Alternate validation
    - Final decision (APPROVED_BY_L7, PENDING_L6, REJECTED)
    """
    try:
        # Get leave request - use proper UUID format
        try:
            leave_response = db.table("leaves").select("*").eq("id", str(leave_id)).execute()
        except Exception as query_error:
            raise HTTPException(status_code=400, detail=f"Invalid leave ID format: {str(query_error)}")
        
        if not leave_response.data or len(leave_response.data) == 0:
            raise HTTPException(status_code=404, detail=f"Leave request not found with ID: {leave_id}")
        
        leave = leave_response.data[0]
        employee_id = leave.get("employee_id")
        
        if not employee_id:
            raise HTTPException(status_code=400, detail="Leave request missing employee_id")
        
        start_date = leave.get("start_date")
        end_date = leave.get("end_date")
        
        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="Leave request missing start_date or end_date")
        
        # Calculate leave duration
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00') if 'Z' in start_date else start_date)
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00') if 'Z' in end_date else end_date)
            leave_days = (end - start).days + 1
        except Exception as date_error:
            # Fallback to simple calculation
            leave_days = 1
        
        # Get employee details
        try:
            employee = db.table("users").select("name, hierarchy_level").eq("id", str(employee_id)).execute()
        except Exception as emp_error:
            raise HTTPException(status_code=500, detail=f"Error fetching employee: {str(emp_error)}")
        
        if not employee.data or len(employee.data) == 0:
            raise HTTPException(status_code=404, detail=f"Employee not found with ID: {employee_id}")
        
        emp_data = employee.data[0]
        
        # ============================================================
        # HR VALIDATION - Leave Balance Check
        # ============================================================
        hr_approved = True  # Simplified - implement actual balance check
        
        if not hr_approved:
            return {
                "leave_id": leave_id,
                "employee_name": emp_data.get("name", "Unknown"),
                "hierarchy_level": emp_data.get("hierarchy_level", "Unknown"),
                "leave_days": leave_days,
                "start_date": start_date,
                "end_date": end_date,
                "hr_validation": {
                    "approved": False,
                    "reason": "Insufficient leave balance"
                },
                "final_decision": "REJECTED_BY_HR",
                "can_l7_approve": False
            }
        
        # ============================================================
        # L7 CONFLICT ANALYSIS
        # ============================================================
        
        # 1. Resource Hold - Critical Task Check
        try:
            critical_tasks = db.table("tasks").select("*").eq("assignee_id", str(employee_id)).eq("priority", "critical").neq("status", "completed").execute()
            has_critical_task = len(critical_tasks.data or []) > 0
        except Exception:
            critical_tasks = type('obj', (object,), {'data': []})()
            has_critical_task = False
        
        # 2. Pending Tasks Check
        try:
            pending_tasks = db.table("tasks").select("id, title, priority, status").eq("assignee_id", str(employee_id)).in_("status", ["open", "blocked"]).execute()
            has_pending = len(pending_tasks.data or []) > 0
        except Exception:
            pending_tasks = type('obj', (object,), {'data': []})()
            has_pending = False
        
        # 3. Incident Hard Block
        try:
            has_incident = has_blocking_incident(str(employee_id), db)
        except Exception:
            has_incident = False
        
        # 4. Valid Alternate Check (Required for L7 approval)
        valid_alternate = None
        if has_critical_task and critical_tasks.data:
            try:
                valid_alternate = find_valid_alternate(str(employee_id), critical_tasks.data[0], db)
            except Exception:
                valid_alternate = None
        
        # ============================================================
        # DECISION LOGIC
        # ============================================================
        flags = {
            "resource_hold": has_critical_task,
            "pending_tasks": has_pending,
            "incident_hard_block": has_incident,
            "has_valid_alternate": valid_alternate is not None if has_critical_task else True
        }
        
        # Determine final decision
        if has_incident or (has_critical_task and not valid_alternate):
            final_decision = "PENDING_L6"
            can_l7_approve = False
            reason = "Incident hard block" if has_incident else "No valid alternate found for critical task"
        elif has_critical_task or has_pending:
            final_decision = "PENDING_L6"
            can_l7_approve = False
            reason = "Operational risk - requires L6 approval"
        else:
            final_decision = "APPROVED_BY_L7"
            can_l7_approve = True
            reason = "All conditions satisfied"
        
        return {
            "leave_id": leave_id,
            "employee_id": employee_id,
            "employee_name": emp_data.get("name", "Unknown"),
            "hierarchy_level": emp_data.get("hierarchy_level", "Unknown"),
            "leave_days": leave_days,
            "start_date": start_date,
            "end_date": end_date,
            "leave_details": {
                "leave_type": leave.get("leave_type", "casual"),
                "reason": leave.get("reason", ""),
                "days_requested": leave.get("days", leave_days),
                "status": leave.get("status", "pending")
            },
            "leave_quota": {
                "total_annual_leave": 20,  # Standard quota - can be customized per employee
                "used_leave": emp_data.get("used_leave_days", 0),
                "remaining_leave": 20 - emp_data.get("used_leave_days", 0),
                "pending_leave": leave_days,
                "balance_after_approval": 20 - emp_data.get("used_leave_days", 0) - leave_days
            },
            "hr_validation": {
                "approved": True,
                "leave_balance_sufficient": True
            },
            "conflict_analysis": {
                "resource_hold": has_critical_task,
                "pending_tasks_count": len(pending_tasks.data or []),
                "pending_tasks": [
                    {
                        "id": t.get("id"),
                        "title": t.get("title", "Untitled"),
                        "priority": t.get("priority", "medium"),
                        "status": t.get("status", "unknown")
                    } for t in (pending_tasks.data or [])
                ],
                "incident_hard_block": has_incident,
                "critical_tasks_count": len(critical_tasks.data or []),
                "valid_alternate": valid_alternate
            },
            "flags": flags,
            "final_decision": final_decision,
            "can_l7_approve": can_l7_approve,
            "decision_reason": reason,
            "recommendation": {
                "action": "approve" if can_l7_approve else "escalate_to_l6",
                "confidence": "high" if can_l7_approve else "medium",
                "notes": reason
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Error analyzing leave conflict: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)



@leave_conflicts_router.get("/")
async def get_leave_conflicts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get leave requests with conflict analysis - PM/TL see only their project members"""
    try:
        # Get all leave requests (or filter by status)
        query = db.table("leaves").select("*, users!employee_id(name, hierarchy_level)")
        
        if status:
            query = query.eq("status", status)
        
        leaves = query.execute()
        all_leaves = leaves.data or []
        
        # Filter leaves based on role - PM/TL see only their project members
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR]:
            user_id = current_user["id"]
            
            # Get projects where user is PM or TL
            if current_user.get("role") == Roles.PROJECT_MANAGER:
                projects = db.table("projects").select("id").eq("project_manager_id", user_id).execute()
            elif current_user.get("role") == Roles.TECHNICAL_LEAD:
                projects = db.table("projects").select("id").eq("team_lead_id", user_id).execute()
            else:
                projects = None
            
            if projects and projects.data:
                # Get all team members from these projects
                project_ids = [p["id"] for p in projects.data]
                team_member_ids = set()
                
                for project_id in project_ids:
                    members = db.table("project_members").select("user_id").eq("project_id", project_id).execute()
                    if members.data:
                        team_member_ids.update([m["user_id"] for m in members.data])
                
                # Filter leaves to only team members
                all_leaves = [leave for leave in all_leaves if leave.get("employee_id") in team_member_ids]
            else:
                all_leaves = []
        
        conflicts = []
        for leave in all_leaves:
            # Quick conflict check
            employee_id = leave.get("employee_id")
            if not employee_id:
                continue
            
            # Check for critical tasks
            try:
                critical_tasks = db.table("tasks").select("id").eq("assignee_id", str(employee_id)).eq("priority", "critical").neq("status", "completed").execute()
                critical_count = len(critical_tasks.data or [])
            except Exception:
                critical_count = 0
            
            # Check for incidents
            try:
                incidents = db.table("incidents").select("id").eq("owner_id", str(employee_id)).neq("status", "resolved").in_("severity", ["high", "critical"]).execute()
                incident_count = len(incidents.data or [])
            except Exception:
                incident_count = 0
            
            has_conflict = critical_count > 0 or incident_count > 0
            
            # Determine severity
            if incident_count > 0:
                severity_level = "high"
            elif critical_count > 0:
                severity_level = "medium"
            else:
                severity_level = "low"
            
            # Apply severity filter if provided
            if severity and severity_level != severity:
                continue
            
            # Extract employee name
            employee_name = "Unknown"
            if isinstance(leave.get("users"), dict):
                employee_name = leave["users"].get("name", "Unknown")
            
            conflicts.append({
                "id": leave["id"],
                "leave_id": leave["id"],
                "employee_id": employee_id,
                "employee_name": employee_name,
                "start_date": leave.get("start_date"),
                "end_date": leave.get("end_date"),
                "leave_type": leave.get("leave_type", "casual"),
                "reason": leave.get("reason", ""),
                "status": leave.get("status", "pending"),
                "severity": severity_level,
                "has_critical_tasks": critical_count > 0,
                "has_incidents": incident_count > 0,
                "conflict_count": critical_count + incident_count
            })
        
        return {
            "conflicts": conflicts,
            "total": len(conflicts)
        }
        
    except Exception as e:
        import traceback
        error_detail = f"Error fetching leave conflicts: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

