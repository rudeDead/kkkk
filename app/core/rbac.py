"""
QKREW Backend - Role-Based Access Control (RBAC)
Implements permission system with ADMIN SUPREME CONTROL
"""

from functools import wraps
from fastapi import HTTPException, status
from typing import List, Callable, Dict, Any


# ============================================================================
# ROLE DEFINITIONS
# ============================================================================

class Roles:
    """System roles"""
    ADMIN = "admin"  # SUPREME CONTROLLER - Can override EVERYTHING
    PROJECT_MANAGER = "project_manager"  # L3-L5
    TECHNICAL_LEAD = "technical_lead"  # L6-L7
    HR = "hr"
    EMPLOYEE = "employee"  # L8-L13


class HierarchyLevels:
    """Hierarchy levels L1-L13"""
    L1 = "L1"  # CTO (ADMIN)
    L2 = "L2"  # VP Engineering (ADMIN)
    L3 = "L3"  # Director (PM)
    L4 = "L4"  # Engineering Manager (PM)
    L5 = "L5"  # Senior Manager (PM)
    L6 = "L6"  # Principal Architect (Technical Lead)
    L7 = "L7"  # Team Lead (Technical Lead)
    L8 = "L8"  # Senior Engineer (Employee)
    L9 = "L9"  # Engineer (Employee)
    L10 = "L10"  # Junior Engineer (Employee)
    L11 = "L11"  # Associate Engineer (Employee)
    L12 = "L12"  # Trainee (Employee)
    L13 = "L13"  # Intern (Employee)


# ============================================================================
# PERMISSION DECORATORS
# ============================================================================

def require_role(allowed_roles: List[str]):
    """
    Decorator to check if user has required role
    
    ADMIN can ALWAYS override - has access to EVERYTHING
    
    Args:
        allowed_roles: List of roles that can access this endpoint
    
    Usage:
        @require_role([Roles.ADMIN, Roles.PROJECT_MANAGER])
        async def create_project(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            # ADMIN SUPREME CONTROL - Can access EVERYTHING
            if current_user and current_user.get("role") == Roles.ADMIN:
                return await func(*args, current_user=current_user, **kwargs)
            
            # Check if user has required role
            if not current_user or current_user.get("role") not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_hierarchy_level(min_level: str):
    """
    Decorator to check if user has minimum hierarchy level
    
    ADMIN can ALWAYS override
    
    Args:
        min_level: Minimum hierarchy level required (e.g., "L7")
    
    Usage:
        @require_hierarchy_level("L7")
        async def create_esp_package(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            # ADMIN SUPREME CONTROL
            if current_user and current_user.get("role") == Roles.ADMIN:
                return await func(*args, current_user=current_user, **kwargs)
            
            # Extract level number (e.g., "L7" -> 7)
            user_level = int(current_user.get("hierarchy_level", "L13")[1:])
            required_level = int(min_level[1:])
            
            # Lower number = higher level (L1 > L13)
            if user_level > required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Minimum hierarchy level required: {min_level}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_admin():
    """
    Decorator to require ADMIN role (SUPREME CONTROL)
    
    Usage:
        @require_admin()
        async def delete_user(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user or current_user.get("role") != Roles.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied. Admin privileges required."
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# PERMISSION CHECK FUNCTIONS
# ============================================================================

def is_admin(user: dict) -> bool:
    """Check if user is admin (SUPREME CONTROL)"""
    return user.get("role") == Roles.ADMIN or user.get("hierarchy_level") in ["L1", "L2"]


def is_hr(user: dict) -> bool:
    """Check if user is HR"""
    return user.get("role") == Roles.HR


def is_project_manager(user: dict) -> bool:
    """Check if user is Project Manager (L3-L5)"""
    return user.get("role") == Roles.PROJECT_MANAGER or user.get("hierarchy_level") in ["L3", "L4", "L5"]


def is_technical_lead(user: dict) -> bool:
    """Check if user is Technical Lead (L6-L7)"""
    return user.get("role") == Roles.TECHNICAL_LEAD or user.get("hierarchy_level") in ["L6", "L7"]


def is_owner_or_admin(user: dict, resource_user_id: str) -> bool:
    """Check if user is the owner of resource or admin"""
    return is_admin(user) or user.get("id") == resource_user_id


def can_manage_user(current_user: dict, target_user: dict) -> bool:
    """
    Check if current user can manage target user
    
    Rules:
    - ADMIN can manage EVERYONE
    - Manager can manage their direct reports
    - HR can manage employee profiles
    """
    if is_admin(current_user):
        return True
    
    if is_hr(current_user):
        return True
    
    if target_user.get("manager_id") == current_user.get("id"):
        return True
    
    return False


def can_view_project(user: dict, project: dict) -> bool:
    """Check if user can view project"""
    if is_admin(user):
        return True
    
    # PM, TL can view all projects
    if is_project_manager(user) or is_technical_lead(user):
        return True
    
    # HR can view (read-only)
    if is_hr(user):
        return True
    
    # Employees can only view assigned projects
    # Check if user is in project members
    return False  # Implement project membership check


def can_create_project(user: dict) -> bool:
    """Check if user can create projects"""
    return is_admin(user)


def can_update_project(user: dict, project: dict) -> bool:
    """Check if user can update project"""
    if is_admin(user):
        return True
    
    # PM can update own projects
    if is_project_manager(user) and project.get("manager_id") == user.get("id"):
        return True
    
    # L6 can update if assigned as architect
    if is_technical_lead(user) and user.get("hierarchy_level") == "L6":
        # Check if assigned as architect
        return False  # Implement architect check
    
    return False


def can_delete_project(user: dict) -> bool:
    """Check if user can delete projects"""
    return is_admin(user)


def can_create_task(user: dict) -> bool:
    """Check if user can create tasks"""
    if is_admin(user):
        return True
    
    return is_project_manager(user) or is_technical_lead(user)


def can_delete_task(user: dict) -> bool:
    """Check if user can delete tasks"""
    if is_admin(user):
        return True
    
    return is_project_manager(user)


def can_create_employee(user: dict) -> bool:
    """Check if user can create employees"""
    return is_admin(user) or is_hr(user)


def can_delete_employee(user: dict) -> bool:
    """Check if user can delete employees"""
    return is_admin(user)


def can_view_all_leaves(user: dict) -> bool:
    """Check if user can view all leave requests"""
    return is_admin(user) or is_hr(user)


def can_approve_leave(user: dict) -> bool:
    """Check if user can approve leaves"""
    if is_admin(user) or is_hr(user):
        return True
    
    # L7 can approve
    if user.get("hierarchy_level") == "L7":
        return True
    
    # L6 can approve escalations
    if user.get("hierarchy_level") == "L6":
        return True
    
    return False


# ============================================================================
# GET USER PERMISSIONS
# ============================================================================

def get_user_permissions(user: dict) -> Dict[str, Any]:
    """
    Get all permissions for a user
    Returns a dictionary of module permissions for frontend
    ✅ MATCHES ALL FRONTEND PERMISSION FILES
    """
    role = user.get("role")
    hierarchy_level = user.get("hierarchy_level")
    
    # ============================================================================
    # ADMIN - SUPREME CONTROL (L1-L2)
    # ============================================================================
    if is_admin(user):
        return {
            "sidebar": {
                "dashboard": True,
                "projects": True,
                "tasks": True,
                "employees": True,
                "teams": True,
                "leaves": True,
                "incidents": True,
                "software_requests": True,
                "notice_period": True,
                "events": True,
                "analytics": True,
                "esp": True,
                "business_trips": True,
                "leave_conflicts": True,
                "chatbot": True
            },
            "projects": {
                "create": True,
                "view_all": True,
                "update": True,
                "delete": True,
                "manage_members": True,
                "view_budget": True,
                "view_health": True,
                "update_progress": True
            },
            "tasks": {
                "create": True,
                "view_all": True,
                "update": True,
                "delete": True,
                "assign": True,
                "update_status": True,
                "update_progress": True,
                "mark_blocked": True
            },
            "employees": {
                "create": True,
                "view_all": True,
                "view_details": True,
                "update": True,
                "delete": True,
                "view_salary": True,
                "update_salary": True,
                "view_performance": True,
                "update_skills": True,
                "view_balance": True
            },
            "teams": {
                "create": True,
                "view_all": True,
                "update": True,
                "delete": True,
                "manage_members": True,
                "view_capacity": True
            },
            "leaves": {
                "create": True,
                "view_own": True,
                "view": True,
                "update": True,
                "cancel": True,
                "view_balance": True
            },
            "leave_conflicts": {
                "view_all": True,
                "view": True,
                "approve": True,
                "reject": True,
                "escalate": True,
                "escalation_decision": True,
                "override": True,
                "run_analysis": True,
                "view_alternatives": True,
                "hr_review": True,
                "force_decision": True
            },
            "incidents": {
                "create": True,
                "view_all": True,
                "view": True,
                "update_status": True,
                "assign": True,
                "resolve": True,
                "delete": True,
                "view_sla": True
            },
            "esp": {
                "run_simulation": True,
                "create_recommendation": True,
                "view_recommendations": True,
                "review_forward": True,
                "view_results": True,
                "final_decision": True,
                "view_all": True,
                "view_alternatives": True,
                "override": True
            },
            "software_requests": {
                "create": True,
                "view_all": True,
                "view": True,
                "approve": True,
                "reject": True,
                "update": True,
                "delete": True
            },
            "business_trips": {
                "create": True,
                "view_all": True,
                "view": True,
                "approve_manager": True,
                "approve_finance": True,
                "approve_hr": True,
                "run_analysis": True,
                "update_status": True,
                "add_expenses": True,
                "view_budget": True
            },
            "notice_period": {
                "create": True,
                "view_all": True,
                "view": True,
                "update": True,
                "delete": True
            },
            "events": {
                "create": True,
                "view_all": True,
                "view_details": True,
                "update": True,
                "delete": True,
                "register": True,
                "view_participants": True,
                "mark_attendance": True
            },
            "analytics": {
                "view_all": True,
                "view_project": True,
                "view_task": True,
                "view_employee": True,
                "view_team": True,
                "view_leave": True,
                "view_hr": True,
                "view_incident": True,
                "view_esp": True,
                "view_budget": True,
                "view_utilization": True,
                "view_performance": True,
                "export": True
            },
            "is_admin": True,
            "is_hr": False,
            "is_pm": False,
            "is_tl": False
        }
    
    # ============================================================================
    # HR PERMISSIONS
    # ============================================================================
    if is_hr(user):
        return {
            "sidebar": {
                "dashboard": True,
                "projects": True,
                "tasks": False,
                "employees": True,
                "teams": True,
                "leaves": True,
                "incidents": False,
                "software_requests": True,
                "notice_period": True,
                "events": True,
                "analytics": True,
                "esp": True,
                "business_trips": True,
                "leave_conflicts": True,
                "chatbot": True
            },
            "projects": {"view_all": True},
            "tasks": {"view_all": False},
            "employees": {
                "create": True,
                "view_all": True,
                "view_details": True,
                "update": True,
                "view_salary": True,
                "update_salary": True,
                "view_performance": True,
                "update_skills": True,
                "view_balance": True
            },
            "teams": {"view_all": True},
            "leaves": {
                "create": True,
                "view_own": True,
                "view_balance": True
            },
            "leave_conflicts": {
                "view_all": True,
                "view": True,
                "escalate": True,
                "view_alternatives": True,
                "hr_review": True
            },
            "incidents": {"view_all": False},
            "esp": {"view_all": False},
            "software_requests": {"view_all": True},
            "business_trips": {
                "create": True,
                "view_all": True,
                "approve_hr": True,
                "view_budget": True
            },
            "notice_period": {
                "create": True,
                "view_all": True,
                "update": True
            },
            "events": {
                "create": True,
                "view_all": True,
                "update": True,
                "delete": True,
                "mark_attendance": True
            },
            "analytics": {
                "view_leave": True,
                "view_hr": True,
                "export": True
            },
            "is_admin": False,
            "is_hr": True,
            "is_pm": False,
            "is_tl": False
        }
    
    # ============================================================================
    # PROJECT MANAGER PERMISSIONS (L3-L5)
    # ============================================================================
    if is_project_manager(user):
        return {
            "sidebar": {
                "dashboard": True,
                "projects": True,
                "tasks": True,
                "employees": True,
                "teams": True,
                "leaves": True,
                "incidents": True,
                "software_requests": True,
                "notice_period": True,
                "events": True,
                "analytics": False,  # PM cannot see Analytics
                "esp": True,
                "business_trips": True,
                "leave_conflicts": True,
                "chatbot": True
            },
            "projects": {
                "view_all": True,
                "view": True,
                "update": True,  # own projects
                "manage_members": True,  # own projects
                "view_budget": True,
                "view_health": True,
                "update_progress": True
            },
            "tasks": {
                "create": True,
                "view_all": True,
                "update": True,
                "delete": True,
                "assign": True,
                "update_status": True,
                "update_progress": True
            },
            "employees": {"view_all": True, "view_details": True},
            "teams": {"view_all": True},
            "leaves": {
                "create": True,
                "view_own": True,
                "view_balance": True
            },
            "leave_conflicts": {
                "view": True  # project impacts only
            },
            "incidents": {
                "create": True,
                "view_all": True,
                "assign": True,
                "resolve": True,
                "view_sla": True
            },
            "esp": {
                "run_simulation": True,
                "view_all": True,
                "final_decision": True,
                "view_alternatives": True
            },
            "software_requests": {"view_all": True},
            "business_trips": {
                "create": True,
                "view_all": True,
                "approve_manager": True,
                "run_analysis": True
            },
            "notice_period": {"view": True},  # impact only
            "events": {"view_all": True, "register": True},
            "analytics": {
                "view_project": True,
                "view_task": True,
                "view_employee": True,
                "view_budget": True,
                "export": True
            },
            "is_admin": False,
            "is_hr": False,
            "is_pm": True,
            "is_tl": False
        }
    
    # ============================================================================
    # TECHNICAL LEAD PERMISSIONS (L6-L7)
    # ============================================================================
    if is_technical_lead(user):
        is_l6 = hierarchy_level == "L6"
        is_l7 = hierarchy_level == "L7"
        
        return {
            "sidebar": {
                "dashboard": False,  # TL cannot see Dashboard
                "projects": True,
                "tasks": True,
                "employees": True,
                "teams": True,
                "leaves": True,
                "incidents": True,
                "software_requests": True,
                "notice_period": True,
                "events": True,
                "analytics": False,  # TL cannot see Analytics
                "esp": True,
                "business_trips": True,
                "leave_conflicts": True,
                "chatbot": True
            },
            "projects": {
                "view_all": True,
                "view": True,
                "view_health": True
            },
            "tasks": {
                "create": True,
                "view_all": True,
                "update": True,
                "assign": True,
                "update_status": True,
                "update_progress": True,
                "mark_blocked": True
            },
            "employees": {"view_all": True, "view_details": True},
            "teams": {
                "create": is_l7,
                "view_all": True,
                "update": True,  # own team
                "manage_members": is_l7,
                "view_capacity": True
            },
            "leaves": {
                "create": True,
                "view_own": True,
                "view_balance": True
            },
            "leave_conflicts": {
                "view_all": is_l6 or is_l7,
                "view": True,
                "approve": is_l7,
                "reject": is_l7,
                "escalate": is_l7,
                "escalation_decision": is_l6,
                "override": is_l6,
                "run_analysis": True,
                "view_alternatives": True
            },
            "incidents": {
                "create": True,
                "view_all": True,
                "view": True,
                "update_status": True,
                "assign": True,
                "resolve": True,
                "view_sla": True
            },
            "esp": {
                "run_simulation": True,
                "create_recommendation": is_l7,
                "view_recommendations": True,
                "review_forward": is_l6,
                "view_results": True,
                "view_all": True,
                "view_alternatives": True
            },
            "software_requests": {
                "create": True,
                "view_all": True,
                "approve": True,
                "reject": True
            },
            "business_trips": {
                "create": True,
                "view_all": True,
                "approve_manager": True,
                "run_analysis": True
            },
            "notice_period": {"view": True},  # impact only
            "events": {"view_all": True, "register": True},
            "analytics": {
                "view_project": True,
                "view_task": True,
                "view_employee": True,
                "view_team": True,
                "view_incident": True,
                "view_esp": True,
                "view_utilization": True,
                "view_performance": True
            },
            "is_admin": False,
            "is_hr": False,
            "is_pm": False,
            "is_tl": True,
            "is_l6": is_l6,
            "is_l7": is_l7
        }
    
    # ============================================================================
    # EMPLOYEE PERMISSIONS (L8-L13)
    # ============================================================================
    return {
            "sidebar": {
                "dashboard": False,  # Employee cannot see Dashboard
                "projects": True,
                "tasks": True,
                "employees": False,  # Employee cannot see Employees list
                "teams": False,  # Employee cannot see Teams
                "leaves": True,
                "incidents": True,
                "software_requests": True,
                "notice_period": True,
                "events": True,
                "analytics": False,  # Employee cannot see Analytics
                "esp": False,  # Employee cannot see ESP
                "business_trips": True,
                "leave_conflicts": False,  # Employee cannot see Leave Conflicts
                "chatbot": True
            },
        "projects": {"view": True},  # assigned only
        "tasks": {
            "view": True,  # assigned only
            "update_status": True,  # assigned only
            "update_progress": True,  # assigned only
            "mark_blocked": True  # assigned only
        },
        "employees": {"view_all": True},  # basic info only
        "teams": {"view_all": True},
        "leaves": {
            "create": True,
            "view_own": True,
            "view": True,  # own only
            "update": True,  # own pending only
            "cancel": True,  # own only
            "view_balance": True
        },
        "leave_conflicts": {},  # NO ACCESS
        "incidents": {
            "create": True,
            "view": True,  # own/assigned only
            "update_status": True,  # assigned only
            "resolve": True  # assigned only
        },
        "esp": {},  # NO ACCESS
        "software_requests": {
            "create": True,
            "view": True,  # own only
            "update": True,  # own pending only
            "delete": True  # own pending only
        },
        "business_trips": {
            "create": True,
            "view": True,  # own only
            "update_status": True,  # own only
            "add_expenses": True  # own only
        },
        "notice_period": {},  # NO ACCESS
        "events": {
            "view_all": True,
            "view_details": True,
            "register": True,
            "view_participants": True
        },
        "analytics": {},  # NO ACCESS
        "is_admin": False,
        "is_hr": False,
        "is_pm": False,
        "is_tl": False
    }


# ============================================================================
# PERMISSION MATRIX (for reference)
# ============================================================================

PERMISSION_MATRIX = {
    "users": {
        Roles.ADMIN: ["create", "read", "update", "delete"],  # FULL CONTROL
        Roles.PROJECT_MANAGER: ["read"],
        Roles.TECHNICAL_LEAD: ["read"],
        Roles.HR: ["create", "read", "update"],
        Roles.EMPLOYEE: ["read_own"],
    },
    "projects": {
        Roles.ADMIN: ["create", "read", "update", "delete"],  # FULL CONTROL
        Roles.PROJECT_MANAGER: ["create", "read", "update", "delete_own"],
        Roles.TECHNICAL_LEAD: ["create", "read", "update_own"],
        Roles.HR: ["read"],
        Roles.EMPLOYEE: ["read_assigned"],
    },
    "tasks": {
        Roles.ADMIN: ["create", "read", "update", "delete"],  # FULL CONTROL
        Roles.PROJECT_MANAGER: ["create", "read", "update", "delete"],
        Roles.TECHNICAL_LEAD: ["create", "read", "update", "delete"],
        Roles.HR: ["read"],
        Roles.EMPLOYEE: ["read", "update_assigned"],
    },
    "leaves": {
        Roles.ADMIN: ["create", "read", "update", "delete", "approve", "reject"],  # FULL CONTROL
        Roles.PROJECT_MANAGER: ["read"],
        Roles.TECHNICAL_LEAD: ["read", "approve", "reject"],
        Roles.HR: ["read", "approve", "reject"],
        Roles.EMPLOYEE: ["create_own", "read_own", "update_own"],
    },
    "esp": {
        Roles.ADMIN: ["create", "read", "update", "delete", "approve", "reject"],  # FULL CONTROL
        Roles.PROJECT_MANAGER: ["read", "approve", "reject"],
        Roles.TECHNICAL_LEAD: ["create", "read", "update", "review", "simulate"],
        Roles.HR: ["read"],
        Roles.EMPLOYEE: ["read"],
    },
}
