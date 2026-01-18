"""
Database Connection Test
Tests Supabase connection and verifies all tables exist
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import db
from app.config import settings


def test_connection():
    """Test basic Supabase connection"""
    print("=" * 60)
    print("[TEST] SUPABASE CONNECTION")
    print("=" * 60)
    
    try:
        # Initialize connection
        db.connect()
        print("[OK] Supabase client initialized")
        
        # Get client
        client = db.get_client()
        print(f"[OK] Connected to: {settings.SUPABASE_URL}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {str(e)}")
        return False


def test_tables():
    """Test that all 19 tables exist"""
    print("\n" + "=" * 60)
    print("[TEST] DATABASE TABLES")
    print("=" * 60)
    
    expected_tables = [
        "tech_teams",
        "users",
        "tech_team_members",
        "projects",
        "project_members",
        "tasks",
        "leaves",
        "incidents",
        "project_invitations",
        "software_requests",
        "esp_packages",
        "esp_l7_recommendations",
        "esp_simulations",
        "esp_l6_reviews",
        "esp_pm_decisions",
        "notice_periods",
        "events",
        "event_participants",
        "business_trips",
    ]
    
    client = db.get_client()
    passed = 0
    failed = 0
    
    for table in expected_tables:
        try:
            # Try to select from table (will fail if table doesn't exist)
            response = client.table(table).select("*").limit(1).execute()
            print(f"[OK] Table '{table}' exists")
            passed += 1
        except Exception as e:
            print(f"[ERROR] Table '{table}' missing or error: {str(e)}")
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"Results: {passed}/{len(expected_tables)} tables verified")
    print("-" * 60)
    
    return failed == 0


def test_insert_and_delete():
    """Test insert and delete operations"""
    print("\n" + "=" * 60)
    print("[TEST] INSERT/DELETE OPERATIONS")
    print("=" * 60)
    
    client = db.get_service_client()  # Use service client for admin operations
    
    try:
        # Test insert into tech_teams
        print("\n[ACTION] Testing INSERT...")
        test_team = {
            "name": "Test Team",
            "description": "This is a test team",
            "department": "Testing"
        }
        
        response = client.table("tech_teams").insert(test_team).execute()
        
        if response.data and len(response.data) > 0:
            team_id = response.data[0]["id"]
            print(f"[OK] INSERT successful - Created team with ID: {team_id}")
            
            # Test delete
            print("\n[ACTION] Testing DELETE...")
            delete_response = client.table("tech_teams").delete().eq("id", team_id).execute()
            print(f"[OK] DELETE successful - Removed test team")
            
            return True
        else:
            print("[ERROR] INSERT failed - No data returned")
            return False
            
    except Exception as e:
        print(f"[ERROR] Operation failed: {str(e)}")
        return False


def test_service_client():
    """Test service role client (admin access)"""
    print("\n" + "=" * 60)
    print("[TEST] SERVICE ROLE CLIENT")
    print("=" * 60)
    
    try:
        service_client = db.get_service_client()
        print("[OK] Service role client initialized")
        
        # Try to access users table with service client
        response = service_client.table("users").select("*").limit(1).execute()
        print("[OK] Service role client can access database")
        
        return True
    except Exception as e:
        print(f"[ERROR] Service client test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("QKREW BACKEND - DATABASE CONNECTION TEST")
    print("=" * 60 + "\n")
    
    results = {
        "Connection": test_connection(),
        "Tables": test_tables(),
        "Service Client": test_service_client(),
        "Insert/Delete": test_insert_and_delete(),
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name:20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("SUCCESS! ALL TESTS PASSED! Database is ready!")
    else:
        print("WARNING! SOME TESTS FAILED! Check errors above.")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
