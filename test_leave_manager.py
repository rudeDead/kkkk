"""
Leave Manager API Test Script
Tests the complete workflow: HR → TL → PM
"""

import requests
import json
from datetime import datetime, timedelta

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test credentials (update these based on your database)
CREDENTIALS = {
    "hr": {
        "email": "hr@qkrew.com",
        "password": "password123"
    },
    "tl": {
        "email": "tl@qkrew.com",
        "password": "password123"
    },
    "pm": {
        "email": "pm@qkrew.com",
        "password": "password123"
    },
    "employee": {
        "email": "employee@qkrew.com",
        "password": "password123"
    }
}

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def login(role):
    """Login and get JWT token"""
    print_info(f"Logging in as {role.upper()}...")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=CREDENTIALS[role]
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print_success(f"Logged in as {role.upper()}")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        return None


def create_leave_request(token, employee_id, days=2):
    """Create a test leave request"""
    print_info(f"Creating leave request for {days} days...")
    
    start_date = datetime.now() + timedelta(days=7)
    end_date = start_date + timedelta(days=days-1)
    
    leave_data = {
        "employee_id": employee_id,
        "leave_type": "casual",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "days": days,
        "reason": "Test leave request for workflow testing"
    }
    
    response = requests.post(
        f"{BASE_URL}/leaves",
        json=leave_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code in [200, 201]:
        leave_id = response.json().get("id")
        print_success(f"Leave created with ID: {leave_id}")
        return leave_id
    else:
        print_error(f"Failed to create leave: {response.text}")
        return None


def get_pending_leaves(token, role):
    """Get pending leaves for the current role"""
    print_info(f"Fetching pending leaves for {role.upper()}...")
    
    response = requests.get(
        f"{BASE_URL}/leave-manager/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        leaves = data.get("leaves", [])
        print_success(f"Found {len(leaves)} pending leave(s)")
        
        if leaves:
            print_info("Leave details:")
            for leave in leaves[:3]:  # Show first 3
                print(f"  - ID: {leave.get('id')}")
                print(f"    Employee: {leave.get('users', {}).get('name', 'Unknown')}")
                print(f"    Days: {leave.get('days')}")
                print(f"    Risk: {leave.get('risk_level', 'N/A')}")
                print(f"    Status: {leave.get('status')}")
        
        return leaves
    else:
        print_error(f"Failed to fetch leaves: {response.text}")
        return []


def get_risk_analysis(token, leave_id):
    """Get risk analysis for a leave"""
    print_info(f"Fetching risk analysis for leave {leave_id}...")
    
    response = requests.get(
        f"{BASE_URL}/leave-manager/{leave_id}/risk-analysis",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success("Risk analysis retrieved")
        print(f"  Risk Level: {data.get('risk_level')}")
        print(f"  Leave Days: {data.get('leave_days')}")
        
        risk_factors = data.get('risk_factors', [])
        if risk_factors:
            print("  Risk Factors:")
            for factor in risk_factors:
                print(f"    - {factor.get('description')}")
        
        recommendation = data.get('recommendation', {})
        print(f"  TL Can Approve: {recommendation.get('tl_can_approve')}")
        print(f"  Requires PM: {recommendation.get('requires_pm_approval')}")
        
        return data
    else:
        print_error(f"Failed to get risk analysis: {response.text}")
        return None


def hr_approve(token, leave_id):
    """HR approves and forwards to TL"""
    print_info("HR validating and forwarding to TL...")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/hr-approve",
        json={"notes": "Leave balance verified. Forwarding to Team Lead."},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print_success("HR approved - Forwarded to Team Lead")
        return True
    else:
        print_error(f"HR approval failed: {response.text}")
        return False


def tl_decision(token, leave_id, action="approve"):
    """TL makes decision (approve or forward_to_pm)"""
    print_info(f"TL making decision: {action}...")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/tl-decision",
        json={
            "action": action,
            "notes": f"TL decision: {action}"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        if action == "approve":
            print_success("TL approved the leave")
        else:
            print_success("TL forwarded to PM (high risk)")
        return True
    else:
        print_error(f"TL decision failed: {response.text}")
        return False


def pm_decision(token, leave_id, action="approve"):
    """PM makes final decision"""
    print_info(f"PM making final decision: {action}...")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/pm-decision",
        json={
            "action": action,
            "notes": f"PM final decision: {action}"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print_success(f"PM {action}d the leave")
        return True
    else:
        print_error(f"PM decision failed: {response.text}")
        return False


def test_low_risk_workflow():
    """Test workflow for low-risk leave (≤3 days, no critical tasks)"""
    print_header("TEST 1: Low Risk Workflow (HR → TL → Approved)")
    
    # Step 1: Login as employee and create leave
    employee_token = login("employee")
    if not employee_token:
        return False
    
    # Get employee ID (you may need to adjust this)
    response = requests.get(
        f"{BASE_URL}/profile",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    employee_id = response.json().get("id") if response.status_code == 200 else None
    
    if not employee_id:
        print_error("Could not get employee ID")
        return False
    
    # Create 2-day leave (low risk)
    leave_id = create_leave_request(employee_token, employee_id, days=2)
    if not leave_id:
        return False
    
    # Step 2: HR approves
    hr_token = login("hr")
    if not hr_token:
        return False
    
    hr_leaves = get_pending_leaves(hr_token, "hr")
    if not hr_approve(hr_token, leave_id):
        return False
    
    # Step 3: TL reviews and approves (low risk)
    tl_token = login("tl")
    if not tl_token:
        return False
    
    tl_leaves = get_pending_leaves(tl_token, "tl")
    risk = get_risk_analysis(tl_token, leave_id)
    
    if risk and risk.get('risk_level') == 'low':
        if not tl_decision(tl_token, leave_id, "approve"):
            return False
    else:
        print_error("Expected low risk but got different risk level")
        return False
    
    print_success("✓ Low Risk Workflow Completed Successfully!")
    return True


def test_high_risk_workflow():
    """Test workflow for high-risk leave (>3 days or critical tasks)"""
    print_header("TEST 2: High Risk Workflow (HR → TL → PM → Approved)")
    
    # Step 1: Login as employee and create leave
    employee_token = login("employee")
    if not employee_token:
        return False
    
    response = requests.get(
        f"{BASE_URL}/profile",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    employee_id = response.json().get("id") if response.status_code == 200 else None
    
    if not employee_id:
        print_error("Could not get employee ID")
        return False
    
    # Create 5-day leave (high risk due to duration)
    leave_id = create_leave_request(employee_token, employee_id, days=5)
    if not leave_id:
        return False
    
    # Step 2: HR approves
    hr_token = login("hr")
    if not hr_token:
        return False
    
    if not hr_approve(hr_token, leave_id):
        return False
    
    # Step 3: TL forwards to PM (high risk)
    tl_token = login("tl")
    if not tl_token:
        return False
    
    risk = get_risk_analysis(tl_token, leave_id)
    
    if risk and risk.get('risk_level') in ['medium', 'high']:
        if not tl_decision(tl_token, leave_id, "forward_to_pm"):
            return False
    else:
        print_error("Expected medium/high risk but got low risk")
        return False
    
    # Step 4: PM makes final decision
    pm_token = login("pm")
    if not pm_token:
        return False
    
    pm_leaves = get_pending_leaves(pm_token, "pm")
    if not pm_decision(pm_token, leave_id, "approve"):
        return False
    
    print_success("✓ High Risk Workflow Completed Successfully!")
    return True


def main():
    """Run all tests"""
    print_header("LEAVE MANAGER API - WORKFLOW TESTING")
    print_info("Testing Sequential Approval: HR → TL → PM")
    print_info("Base URL: " + BASE_URL)
    
    results = []
    
    # Test 1: Low Risk Workflow
    try:
        results.append(("Low Risk Workflow", test_low_risk_workflow()))
    except Exception as e:
        print_error(f"Test 1 failed with exception: {str(e)}")
        results.append(("Low Risk Workflow", False))
    
    # Test 2: High Risk Workflow
    try:
        results.append(("High Risk Workflow", test_high_risk_workflow()))
    except Exception as e:
        print_error(f"Test 2 failed with exception: {str(e)}")
        results.append(("High Risk Workflow", False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}\n")
    
    if passed == total:
        print_success("All tests passed! 🎉")
    else:
        print_error(f"{total - passed} test(s) failed")


if __name__ == "__main__":
    main()
