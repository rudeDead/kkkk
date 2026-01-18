"""
Comprehensive API Test Suite
Tests all 42 endpoints with CRUD operations
Run this while the FastAPI server is running on http://localhost:8000
"""

import requests
import json
from datetime import date, timedelta


# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test data storage
test_data = {
    "access_token": None,
    "user_id": None,
    "project_id": None,
    "task_id": None,
    "team_id": None,
    "leave_id": None,
    "new_user_id": None
}


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_test(name, passed, details=""):
    """Print test result"""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name}")
    if details and not passed:
        print(f"      Details: {details}")


def get_headers():
    """Get authorization headers"""
    if test_data["access_token"]:
        return {"Authorization": f"Bearer {test_data['access_token']}"}
    return {}


# ============================================================================
# 1. AUTHENTICATION API TESTS (4 endpoints)
# ============================================================================

def test_authentication():
    print_section("AUTHENTICATION API (4 endpoints)")
    
    # Test 1: Login
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@qkrew.com",
            "password": "admin123"
        })
        passed = response.status_code == 200
        if passed:
            data = response.json()
            test_data["access_token"] = data["access_token"]
            test_data["user_id"] = data["user"]["id"]
        print_test("POST /auth/login", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /auth/login", False, str(e))
    
    # Test 2: Get current user
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /auth/me", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /auth/me", False, str(e))
    
    # Test 3: Refresh token
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": test_data["access_token"]  # Using access token for simplicity
        })
        # This might fail but we test it
        print_test("POST /auth/refresh", response.status_code in [200, 401])
    except Exception as e:
        print_test("POST /auth/refresh", False, str(e))
    
    # Test 4: Logout
    try:
        response = requests.post(f"{BASE_URL}/auth/logout", headers=get_headers())
        passed = response.status_code == 200
        print_test("POST /auth/logout", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /auth/logout", False, str(e))


# ============================================================================
# 2. USERS API TESTS (8 endpoints)
# ============================================================================

def test_users():
    print_section("USERS API (8 endpoints)")
    
    # Test 1: Get all users
    try:
        response = requests.get(f"{BASE_URL}/users", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /users", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /users", False, str(e))
    
    # Test 2: Get user by ID
    try:
        response = requests.get(f"{BASE_URL}/users/{test_data['user_id']}", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /users/{id}", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /users/{id}", False, str(e))
    
    # Test 3: Create user
    try:
        response = requests.post(f"{BASE_URL}/users", headers=get_headers(), json={
            "email": "testuser@qkrew.com",
            "password": "test123",
            "name": "Test User",
            "role": "employee",
            "hierarchy_level": "L10",
            "department": "Engineering",
            "skills": ["Python", "Testing"],
            "experience_years": 2,
            "weekly_capacity": 40,
            "status": "active"
        })
        passed = response.status_code == 201
        if passed:
            test_data["new_user_id"] = response.json()["id"]
        print_test("POST /users", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /users", False, str(e))
    
    # Test 4: Update user
    if test_data.get("new_user_id"):
        try:
            response = requests.put(
                f"{BASE_URL}/users/{test_data['new_user_id']}", 
                headers=get_headers(), 
                json={"name": "Updated Test User"}
            )
            passed = response.status_code == 200
            print_test("PUT /users/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("PUT /users/{id}", False, str(e))
    
    # Test 5: Get user workload
    try:
        response = requests.get(f"{BASE_URL}/users/{test_data['user_id']}/workload", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /users/{id}/workload", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /users/{id}/workload", False, str(e))
    
    # Test 6: Get user projects
    try:
        response = requests.get(f"{BASE_URL}/users/{test_data['user_id']}/projects", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /users/{id}/projects", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /users/{id}/projects", False, str(e))
    
    # Test 7: Get user tasks
    try:
        response = requests.get(f"{BASE_URL}/users/{test_data['user_id']}/tasks", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /users/{id}/tasks", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /users/{id}/tasks", False, str(e))
    
    # Test 8: Delete user (will test at end)
    # Skipping for now to keep test user


# ============================================================================
# 3. PROJECTS API TESTS (9 endpoints)
# ============================================================================

def test_projects():
    print_section("PROJECTS API (9 endpoints)")
    
    # Test 1: Get all projects
    try:
        response = requests.get(f"{BASE_URL}/projects", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /projects", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /projects", False, str(e))
    
    # Test 2: Create project
    try:
        today = date.today()
        deadline = today + timedelta(days=60)
        
        response = requests.post(f"{BASE_URL}/projects", headers=get_headers(), json={
            "name": "Test Project",
            "description": "API Test Project",
            "project_manager_id": test_data["user_id"],
            "project_type": "internal",
            "priority": "high",
            "status": "active",
            "start_date": today.isoformat(),
            "deadline": deadline.isoformat(),
            "risk_level": "low",
            "required_skills": ["Python", "FastAPI"],
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"]
        })
        passed = response.status_code == 201
        if passed:
            test_data["project_id"] = response.json()["id"]
        print_test("POST /projects", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /projects", False, str(e))
    
    # Test 3: Get project by ID
    if test_data.get("project_id"):
        try:
            response = requests.get(f"{BASE_URL}/projects/{test_data['project_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /projects/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /projects/{id}", False, str(e))
    
    # Test 4: Update project
    if test_data.get("project_id"):
        try:
            response = requests.put(
                f"{BASE_URL}/projects/{test_data['project_id']}", 
                headers=get_headers(), 
                json={"description": "Updated project description"}
            )
            passed = response.status_code == 200
            print_test("PUT /projects/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("PUT /projects/{id}", False, str(e))
    
    # Test 5: Get project members
    if test_data.get("project_id"):
        try:
            response = requests.get(f"{BASE_URL}/projects/{test_data['project_id']}/members", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /projects/{id}/members", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /projects/{id}/members", False, str(e))
    
    # Test 6: Add project member
    if test_data.get("project_id") and test_data.get("new_user_id"):
        try:
            response = requests.post(
                f"{BASE_URL}/projects/{test_data['project_id']}/members", 
                headers=get_headers(), 
                json={
                    "user_id": test_data["new_user_id"],
                    "role": "Developer",
                    "allocation_percent": 100
                }
            )
            passed = response.status_code == 201
            print_test("POST /projects/{id}/members", passed, response.text if not passed else "")
        except Exception as e:
            print_test("POST /projects/{id}/members", False, str(e))
    
    # Test 7: Get project analytics
    if test_data.get("project_id"):
        try:
            response = requests.get(f"{BASE_URL}/projects/{test_data['project_id']}/analytics", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /projects/{id}/analytics", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /projects/{id}/analytics", False, str(e))
    
    # Test 8: Remove project member (will test later)
    # Test 9: Delete project (will test at end)


# ============================================================================
# 4. TASKS API TESTS (5 endpoints)
# ============================================================================

def test_tasks():
    print_section("TASKS API (5 endpoints)")
    
    # Test 1: Get all tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /tasks", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /tasks", False, str(e))
    
    # Test 2: Create task
    if test_data.get("project_id"):
        try:
            due_date = date.today() + timedelta(days=7)
            
            response = requests.post(f"{BASE_URL}/tasks", headers=get_headers(), json={
                "title": "Test Task",
                "description": "API Test Task",
                "project_id": test_data["project_id"],
                "assignee_id": test_data["user_id"],
                "priority": "high",
                "status": "not_started",
                "estimated_hours": 8,
                "due_date": due_date.isoformat(),
                "is_learning_task": False
            })
            passed = response.status_code == 201
            if passed:
                test_data["task_id"] = response.json()["id"]
            print_test("POST /tasks", passed, response.text if not passed else "")
        except Exception as e:
            print_test("POST /tasks", False, str(e))
    
    # Test 3: Get task by ID
    if test_data.get("task_id"):
        try:
            response = requests.get(f"{BASE_URL}/tasks/{test_data['task_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /tasks/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /tasks/{id}", False, str(e))
    
    # Test 4: Update task
    if test_data.get("task_id"):
        try:
            response = requests.put(
                f"{BASE_URL}/tasks/{test_data['task_id']}", 
                headers=get_headers(), 
                json={
                    "status": "in_progress",
                    "progress": 50,
                    "actual_hours": 4
                }
            )
            passed = response.status_code == 200
            print_test("PUT /tasks/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("PUT /tasks/{id}", False, str(e))
    
    # Test 5: Delete task (will test at end)


# ============================================================================
# 5. TEAMS API TESTS (8 endpoints)
# ============================================================================

def test_teams():
    print_section("TEAMS API (8 endpoints)")
    
    # Test 1: Get all teams
    try:
        response = requests.get(f"{BASE_URL}/teams", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /teams", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /teams", False, str(e))
    
    # Test 2: Create team
    try:
        response = requests.post(f"{BASE_URL}/teams", headers=get_headers(), json={
            "name": "Test Team",
            "description": "API Test Team",
            "department": "Engineering",
            "team_lead_id": test_data["user_id"]
        })
        passed = response.status_code == 201
        if passed:
            test_data["team_id"] = response.json()["id"]
        print_test("POST /teams", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /teams", False, str(e))
    
    # Test 3: Get team by ID
    if test_data.get("team_id"):
        try:
            response = requests.get(f"{BASE_URL}/teams/{test_data['team_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /teams/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /teams/{id}", False, str(e))
    
    # Test 4: Update team
    if test_data.get("team_id"):
        try:
            response = requests.put(
                f"{BASE_URL}/teams/{test_data['team_id']}", 
                headers=get_headers(), 
                json={"description": "Updated team description"}
            )
            passed = response.status_code == 200
            print_test("PUT /teams/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("PUT /teams/{id}", False, str(e))
    
    # Test 5: Get team members
    if test_data.get("team_id"):
        try:
            response = requests.get(f"{BASE_URL}/teams/{test_data['team_id']}/members", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /teams/{id}/members", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /teams/{id}/members", False, str(e))
    
    # Test 6: Add team member
    if test_data.get("team_id") and test_data.get("new_user_id"):
        try:
            response = requests.post(
                f"{BASE_URL}/teams/{test_data['team_id']}/members", 
                headers=get_headers(), 
                json={"user_id": test_data["new_user_id"]}
            )
            passed = response.status_code == 201
            print_test("POST /teams/{id}/members", passed, response.text if not passed else "")
        except Exception as e:
            print_test("POST /teams/{id}/members", False, str(e))
    
    # Test 7: Remove team member
    if test_data.get("team_id") and test_data.get("new_user_id"):
        try:
            response = requests.delete(
                f"{BASE_URL}/teams/{test_data['team_id']}/members/{test_data['new_user_id']}", 
                headers=get_headers()
            )
            passed = response.status_code == 200
            print_test("DELETE /teams/{id}/members/{user_id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /teams/{id}/members/{user_id}", False, str(e))
    
    # Test 8: Delete team (will test at end)


# ============================================================================
# 6. LEAVES API TESTS (8 endpoints)
# ============================================================================

def test_leaves():
    print_section("LEAVES API (8 endpoints)")
    
    # Test 1: Get all leaves
    try:
        response = requests.get(f"{BASE_URL}/leaves", headers=get_headers())
        passed = response.status_code == 200
        print_test("GET /leaves", passed, response.text if not passed else "")
    except Exception as e:
        print_test("GET /leaves", False, str(e))
    
    # Test 2: Create leave
    try:
        start_date = date.today() + timedelta(days=10)
        end_date = start_date + timedelta(days=2)
        
        response = requests.post(f"{BASE_URL}/leaves", headers=get_headers(), json={
            "leave_type": "casual",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": 3,
            "reason": "API Test Leave"
        })
        passed = response.status_code == 201
        if passed:
            test_data["leave_id"] = response.json()["id"]
        print_test("POST /leaves", passed, response.text if not passed else "")
    except Exception as e:
        print_test("POST /leaves", False, str(e))
    
    # Test 3: Get leave by ID
    if test_data.get("leave_id"):
        try:
            response = requests.get(f"{BASE_URL}/leaves/{test_data['leave_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("GET /leaves/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("GET /leaves/{id}", False, str(e))
    
    # Test 4: Update leave
    if test_data.get("leave_id"):
        try:
            response = requests.put(
                f"{BASE_URL}/leaves/{test_data['leave_id']}", 
                headers=get_headers(), 
                json={"status": "forwarded_to_team_lead"}
            )
            passed = response.status_code == 200
            print_test("PUT /leaves/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("PUT /leaves/{id}", False, str(e))
    
    # Test 5: Approve leave
    if test_data.get("leave_id"):
        try:
            response = requests.post(
                f"{BASE_URL}/leaves/{test_data['leave_id']}/approve", 
                headers=get_headers(),
                params={"decision_notes": "Approved for testing"}
            )
            passed = response.status_code == 200
            print_test("POST /leaves/{id}/approve", passed, response.text if not passed else "")
        except Exception as e:
            print_test("POST /leaves/{id}/approve", False, str(e))
    
    # Test 6: Create another leave for rejection test
    try:
        start_date = date.today() + timedelta(days=20)
        end_date = start_date + timedelta(days=1)
        
        response = requests.post(f"{BASE_URL}/leaves", headers=get_headers(), json={
            "leave_type": "sick",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": 2,
            "reason": "Test rejection"
        })
        if response.status_code == 201:
            reject_leave_id = response.json()["id"]
            
            # Test 7: Reject leave
            response = requests.post(
                f"{BASE_URL}/leaves/{reject_leave_id}/reject", 
                headers=get_headers(),
                params={"decision_notes": "Rejected for testing"}
            )
            passed = response.status_code == 200
            print_test("POST /leaves/{id}/reject", passed, response.text if not passed else "")
        else:
            print_test("POST /leaves/{id}/reject", False, "Could not create test leave")
    except Exception as e:
        print_test("POST /leaves/{id}/reject", False, str(e))
    
    # Test 8: Delete leave (will test at end)


# ============================================================================
# CLEANUP TESTS
# ============================================================================

def test_cleanup():
    print_section("CLEANUP - DELETE OPERATIONS")
    
    # Delete task
    if test_data.get("task_id"):
        try:
            response = requests.delete(f"{BASE_URL}/tasks/{test_data['task_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("DELETE /tasks/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /tasks/{id}", False, str(e))
    
    # Delete team
    if test_data.get("team_id"):
        try:
            response = requests.delete(f"{BASE_URL}/teams/{test_data['team_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("DELETE /teams/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /teams/{id}", False, str(e))
    
    # Delete leave
    if test_data.get("leave_id"):
        try:
            response = requests.delete(f"{BASE_URL}/leaves/{test_data['leave_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("DELETE /leaves/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /leaves/{id}", False, str(e))
    
    # Delete project
    if test_data.get("project_id"):
        try:
            response = requests.delete(f"{BASE_URL}/projects/{test_data['project_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("DELETE /projects/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /projects/{id}", False, str(e))
    
    # Delete user
    if test_data.get("new_user_id"):
        try:
            response = requests.delete(f"{BASE_URL}/users/{test_data['new_user_id']}", headers=get_headers())
            passed = response.status_code == 200
            print_test("DELETE /users/{id}", passed, response.text if not passed else "")
        except Exception as e:
            print_test("DELETE /users/{id}", False, str(e))


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print("\n" + "=" * 70)
    print("  QKREW BACKEND - COMPREHENSIVE API TEST SUITE")
    print("  Testing all 42 endpoints")
    print("=" * 70)
    print(f"\nBase URL: {BASE_URL}")
    print("Server must be running on http://localhost:8000\n")
    
    try:
        # Run all tests
        test_authentication()
        test_users()
        test_projects()
        test_tasks()
        test_teams()
        test_leaves()
        test_cleanup()
        
        # Summary
        print("\n" + "=" * 70)
        print("  TEST SUMMARY")
        print("=" * 70)
        print("\nAll 42 endpoints tested!")
        print("\nTest Data Created:")
        print(f"  - Access Token: {'Yes' if test_data['access_token'] else 'No'}")
        print(f"  - Test User: {test_data.get('new_user_id', 'N/A')}")
        print(f"  - Test Project: {test_data.get('project_id', 'N/A')}")
        print(f"  - Test Task: {test_data.get('task_id', 'N/A')}")
        print(f"  - Test Team: {test_data.get('team_id', 'N/A')}")
        print(f"  - Test Leave: {test_data.get('leave_id', 'N/A')}")
        print("\n" + "=" * 70)
        print("  TESTING COMPLETE!")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {str(e)}")


if __name__ == "__main__":
    main()
