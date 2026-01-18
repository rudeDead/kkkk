"""
Software Requests, Notice Period, Business Trips APIs
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import datetime
from app.models.operations import (
    SoftwareRequestCreate, SoftwareRequestResponse,
    NoticePeriodCreate, NoticePeriodResponse,
    BusinessTripCreate, BusinessTripResponse
)
from app.core.dependencies import get_current_active_user
from app.core.rbac import is_admin, Roles
from app.database import get_db, get_service_db


# SOFTWARE REQUESTS ROUTER
software_requests_router = APIRouter()

@software_requests_router.get("/")
async def get_software_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get software requests - Admin/HR see all, others see own"""
    try:
        query = db.table("software_requests").select("*, requested_by:users!requested_by_id(name, email)", count="exact")
        
        if status:
            query = query.eq("status", status)
        
        # Admin and HR see ALL requests (for approval)
        # Others see only their own requests
        if not is_admin(current_user) and current_user.get("role") != Roles.HR:
            query = query.eq("requested_by_id", current_user["id"])
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "requests": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@software_requests_router.post("/", status_code=201)
async def create_software_request(
    request_data: SoftwareRequestCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create software request"""
    try:
        new_request = {
            "software_name": request_data.software_name,
            "purpose": request_data.purpose,
            "estimated_cost": request_data.estimated_cost,
            "urgency": request_data.urgency,
            "requested_by_id": current_user["id"],
            "status": "pending"
        }
        
        response = db.table("software_requests").insert(new_request).execute()
        
        return response.data[0] if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@software_requests_router.post("/{request_id}/approve")
async def approve_software_request(
    request_id: str,
    decision_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Approve software request (Admin/HR only)"""
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(status_code=403, detail="Admin/HR only")
    
    try:
        update_data = {
            "status": "approved",
            "decided_by_id": current_user["id"],
            "decision_notes": decision_notes
        }
        
        response = db.table("software_requests").update(update_data).eq("id", request_id).execute()
        
        return {"message": "Request approved", "request": response.data[0] if response.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@software_requests_router.post("/{request_id}/reject")
async def reject_software_request(
    request_id: str,
    decision_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Reject software request (Admin/HR only)"""
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(status_code=403, detail="Admin/HR only")
    
    try:
        update_data = {
            "status": "rejected",
            "decided_by_id": current_user["id"],
            "decision_notes": decision_notes
        }
        
        response = db.table("software_requests").update(update_data).eq("id", request_id).execute()
        
        return {"message": "Request rejected", "request": response.data[0] if response.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# NOTICE PERIOD ROUTER
notice_period_router = APIRouter()

@notice_period_router.get("/")
async def get_notice_periods(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get notice periods - PERSONAL MODULE (own only, except Admin)"""
    try:
        query = db.table("notice_periods").select("*, employee:users!employee_id(name, email)", count="exact")
        
        # PERSONAL MODULE: Everyone sees only their own notice period (except Admin)
        if not is_admin(current_user):
            # Everyone (including HR, PM, TL) sees only their own notice period
            query = query.eq("employee_id", current_user["id"])
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "notice_periods": response.data or [],
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@notice_period_router.post("/", status_code=201)
async def create_notice_period(
    notice_data: NoticePeriodCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create notice period (Admin/HR only)"""
    if not is_admin(current_user) and current_user.get("role") != Roles.HR:
        raise HTTPException(status_code=403, detail="Admin/HR only")
    
    try:
        new_notice = {
            "employee_id": notice_data.employee_id,
            "last_working_day": notice_data.last_working_day.isoformat(),
            "reason": notice_data.reason,
            "handover_notes": notice_data.handover_notes,
            "status": "active"
        }
        
        response = db.table("notice_periods").insert(new_notice).execute()
        
        # Update user status
        db.table("users").update({"status": "notice_period"}).eq("id", notice_data.employee_id).execute()
        
        return response.data[0] if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# BUSINESS TRIPS ROUTER
business_trips_router = APIRouter()

@business_trips_router.get("/")
async def get_business_trips(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get all business trips with employee names"""
    try:
        query = db.table("business_trips").select("*, users!employee_id(name)", count="exact")
        
        if status:
            query = query.eq("status", status)
        
        # Non-admin users see only their own trips
        if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            query = query.eq("employee_id", current_user["id"])
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # Format response with employee names
        trips = []
        for trip in (response.data or []):
            trip_data = {**trip}
            if trip.get("users"):
                trip_data["employee_name"] = trip["users"].get("name", "Unknown")
                del trip_data["users"]
            trips.append(trip_data)
        
        return {
            "trips": trips,
            "total": response.count or 0,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_trips_router.get("/{trip_id}")
async def get_business_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """Get single business trip with full details"""
    try:
        response = db.table("business_trips").select("*, users!employee_id(name, role, hierarchy_level)").eq("id", trip_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        trip = response.data[0]
        if trip.get("users"):
            trip["employee_name"] = trip["users"].get("name", "Unknown")
            trip["employee_role"] = trip["users"].get("role", "Unknown")
            trip["employee_level"] = trip["users"].get("hierarchy_level", "Unknown")
            del trip["users"]
        
        return trip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_trips_router.post("/", status_code=201)
async def create_business_trip(
    trip_data: BusinessTripCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Create business trip"""
    try:
        new_trip = {
            "employee_id": current_user["id"],
            "destination": trip_data.destination,
            "purpose": trip_data.purpose,
            "start_date": trip_data.start_date.isoformat(),
            "end_date": trip_data.end_date.isoformat(),
            "estimated_cost": trip_data.estimated_cost,
            "status": "pending"
        }
        
        response = db.table("business_trips").insert(new_trip).execute()
        
        return response.data[0] if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_trips_router.get("/{trip_id}/impact-analysis")
async def analyze_trip_impact(
    trip_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_db)
):
    """
    Analyze business trip impact on projects and calculate profit/loss
    
    Returns:
    - Affected projects
    - Project impact score (how much each project will be affected)
    - Expected benefits from the trip
    - Net profit calculation
    """
    try:
        # Get trip details
        trip_response = db.table("business_trips").select("*").eq("id", trip_id).execute()
        if not trip_response.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        trip = trip_response.data[0]
        employee_id = trip["employee_id"]
        start_date = trip["start_date"]
        end_date = trip["end_date"]
        
        # Calculate trip duration in days
        from datetime import datetime
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        trip_duration = (end - start).days + 1
        
        # Get employee's active projects
        projects_response = db.table("project_members").select(
            "*, projects!project_id(id, name, priority, status, deadline)"
        ).eq("user_id", employee_id).execute()
        
        affected_projects = []
        total_impact_score = 0
        
        for pm in (projects_response.data or []):
            if not pm.get("projects"):
                continue
                
            project = pm["projects"]
            
            # Skip completed/cancelled projects
            if project.get("status") in ["completed", "cancelled"]:
                continue
            
            # Calculate impact score (0-100)
            # Factors: priority, role in project, trip duration
            impact_score = 0
            
            # Priority impact (0-40 points)
            priority_scores = {"critical": 40, "high": 30, "medium": 20, "low": 10}
            impact_score += priority_scores.get(project.get("priority", "medium"), 20)
            
            # Role impact (0-30 points)
            role = pm.get("role", "member")
            role_scores = {"owner": 30, "lead": 25, "member": 15}
            impact_score += role_scores.get(role, 15)
            
            # Duration impact (0-30 points)
            duration_impact = min(trip_duration * 3, 30)
            impact_score += duration_impact
            
            total_impact_score += impact_score
            
            affected_projects.append({
                "project_id": project["id"],
                "project_name": project["name"],
                "priority": project.get("priority", "medium"),
                "role_in_project": role,
                "impact_score": impact_score,
                "impact_level": "critical" if impact_score > 70 else "high" if impact_score > 50 else "medium" if impact_score > 30 else "low",
                "deadline": project.get("deadline"),
                "mitigation": "Assign backup resource" if impact_score > 50 else "Monitor progress"
            })
        
        # Calculate expected benefits
        # Rule-based benefit calculation
        purpose = trip.get("purpose", "").lower()
        
        expected_benefits = {
            "client_relationship": 0,
            "new_business": 0,
            "knowledge_transfer": 0,
            "team_building": 0
        }
        
        # Benefit scoring based on purpose
        if "client" in purpose or "meeting" in purpose:
            expected_benefits["client_relationship"] = 70
            expected_benefits["new_business"] = 50
        if "training" in purpose or "conference" in purpose:
            expected_benefits["knowledge_transfer"] = 80
        if "team" in purpose:
            expected_benefits["team_building"] = 60
        
        total_benefit_score = sum(expected_benefits.values())
        
        # Calculate profit/loss
        estimated_cost = float(trip.get("estimated_cost", 0))
        
        # Estimated revenue impact (simplified)
        # Assume each benefit point translates to $100 in value
        estimated_revenue = total_benefit_score * 100
        
        # Project delay cost (simplified)
        # Assume each impact point costs $50 in delays
        delay_cost = total_impact_score * 50
        
        net_profit = estimated_revenue - estimated_cost - delay_cost
        
        # Recommendation
        recommendation = {
            "approve": net_profit > 0,
            "confidence": "high" if abs(net_profit) > 1000 else "medium" if abs(net_profit) > 500 else "low",
            "reason": ""
        }
        
        if net_profit > 0:
            recommendation["reason"] = f"Expected net profit of ${net_profit:.2f}. Benefits outweigh costs and project impact."
        else:
            recommendation["reason"] = f"Expected net loss of ${abs(net_profit):.2f}. Consider rescheduling or remote alternatives."
        
        return {
            "trip_id": trip_id,
            "employee_id": employee_id,
            "trip_duration_days": trip_duration,
            "affected_projects": affected_projects,
            "total_projects_affected": len(affected_projects),
            "total_impact_score": total_impact_score,
            "average_impact": total_impact_score / max(len(affected_projects), 1),
            "expected_benefits": expected_benefits,
            "total_benefit_score": total_benefit_score,
            "financial_analysis": {
                "estimated_cost": estimated_cost,
                "estimated_revenue": estimated_revenue,
                "delay_cost": delay_cost,
                "net_profit": net_profit,
                "roi_percentage": (net_profit / max(estimated_cost, 1)) * 100 if estimated_cost > 0 else 0
            },
            "recommendation": recommendation
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_trips_router.post("/{trip_id}/approve")
async def approve_business_trip(
    trip_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Approve business trip (PM/L7 only)"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        update_data = {
            "status": "approved",
            "approved_by_id": current_user["id"]
        }
        
        response = db.table("business_trips").update(update_data).eq("id", trip_id).execute()
        
        return {"message": "Trip approved", "trip": response.data[0] if response.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@business_trips_router.post("/{trip_id}/reject")
async def reject_business_trip(
    trip_id: str,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_active_user),
    db: Client = Depends(get_service_db)
):
    """Reject business trip (PM/L7 only)"""
    if not is_admin(current_user) and current_user.get("role") not in [Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        update_data = {
            "status": "rejected",
            "approved_by_id": current_user["id"],
            "rejection_reason": reason
        }
        
        response = db.table("business_trips").update(update_data).eq("id", trip_id).execute()
        
        return {"message": "Trip rejected", "trip": response.data[0] if response.data else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

