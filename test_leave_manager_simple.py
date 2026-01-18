"""
Leave Manager API - Simple Test Guide
Update the credentials below with your actual user emails/passwords
"""

import requests
import json

# ============================================================================
# CONFIGURATION - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
# ============================================================================

BASE_URL = "http://localhost:8000/api/v1"

# TODO: Update these with actual user credentials from your database
TEST_USERS = {
    "hr": {
        "email": "YOUR_HR_EMAIL@example.com",  # Update this
        "password": "YOUR_PASSWORD"             # Update this
    },
    "tl": {
        "email": "YOUR_TL_EMAIL@example.com",  # Update this
        "password": "YOUR_PASSWORD"             # Update this
    },
    "pm": {
        "email": "YOUR_PM_EMAIL@example.com",  # Update this
        "password": "YOUR_PASSWORD"             # Update this
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def login(email, password):
    """Login and return token"""
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"✓ Logged in as {email}")
        return token
    else:
        print(f"✗ Login failed for {email}: {response.text}")
        return None


def test_get_pending_leaves(token, role_name):
    """Test GET /leave-manager/pending"""
    print(f"\n--- Testing GET pending leaves as {role_name} ---")
    
    response = requests.get(
        f"{BASE_URL}/leave-manager/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Success! Found {data.get('total', 0)} pending leaves")
        print(f"  Role: {data.get('role')}")
        print(f"  Status Filter: {data.get('status_filter')}")
        
        leaves = data.get('leaves', [])
        if leaves:
            print(f"\n  First leave:")
            leave = leaves[0]
            print(f"    ID: {leave.get('id')}")
            print(f"    Employee: {leave.get('users', {}).get('name', 'Unknown')}")
            print(f"    Days: {leave.get('days')}")
            print(f"    Risk Level: {leave.get('risk_level')}")
            print(f"    Status: {leave.get('status')}")
            return leave.get('id')
    else:
        print(f"✗ Failed: {response.text}")
    
    return None


def test_risk_analysis(token, leave_id):
    """Test GET /leave-manager/{id}/risk-analysis"""
    print(f"\n--- Testing Risk Analysis for leave {leave_id} ---")
    
    response = requests.get(
        f"{BASE_URL}/leave-manager/{leave_id}/risk-analysis",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Risk Analysis Retrieved:")
        print(f"  Risk Level: {data.get('risk_level')}")
        print(f"  Leave Days: {data.get('leave_days')}")
        print(f"  TL Can Approve: {data.get('recommendation', {}).get('tl_can_approve')}")
        
        risk_factors = data.get('risk_factors', [])
        if risk_factors:
            print(f"  Risk Factors:")
            for factor in risk_factors:
                print(f"    - {factor.get('description')}")
    else:
        print(f"✗ Failed: {response.text}")


def test_hr_approve(token, leave_id):
    """Test POST /leave-manager/{id}/hr-approve"""
    print(f"\n--- Testing HR Approval for leave {leave_id} ---")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/hr-approve",
        json={"notes": "Test HR approval"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ HR Approved Successfully")
        print(f"  Message: {response.json().get('message')}")
    else:
        print(f"✗ Failed: {response.text}")


def test_tl_decision(token, leave_id, action="approve"):
    """Test POST /leave-manager/{id}/tl-decision"""
    print(f"\n--- Testing TL Decision ({action}) for leave {leave_id} ---")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/tl-decision",
        json={"action": action, "notes": f"Test TL {action}"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ TL Decision Successful")
        print(f"  Message: {response.json().get('message')}")
    else:
        print(f"✗ Failed: {response.text}")


def test_pm_decision(token, leave_id, action="approve"):
    """Test POST /leave-manager/{id}/pm-decision"""
    print(f"\n--- Testing PM Decision ({action}) for leave {leave_id} ---")
    
    response = requests.post(
        f"{BASE_URL}/leave-manager/{leave_id}/pm-decision",
        json={"action": action, "notes": f"Test PM {action}"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✓ PM Decision Successful")
        print(f"  Message: {response.json().get('message')}")
    else:
        print(f"✗ Failed: {response.text}")


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    print("="*60)
    print("LEAVE MANAGER API - MANUAL TEST")
    print("="*60)
    print("\nIMPORTANT: Update TEST_USERS with your actual credentials first!")
    print()
    
    # Step 1: Login as HR
    print("\n" + "="*60)
    print("STEP 1: Login as HR")
    print("="*60)
    hr_token = login(TEST_USERS["hr"]["email"], TEST_USERS["hr"]["password"])
    
    if not hr_token:
        print("\n⚠ Please update HR credentials in the script and try again")
        return
    
    # Step 2: Get pending leaves for HR
    print("\n" + "="*60)
    print("STEP 2: Get Pending Leaves (HR View)")
    print("="*60)
    leave_id = test_get_pending_leaves(hr_token, "HR")
    
    if not leave_id:
        print("\n⚠ No pending leaves found. Create a leave request first.")
        print("  You can create one via the frontend or Swagger UI")
        return
    
    # Step 3: Get risk analysis
    print("\n" + "="*60)
    print("STEP 3: Get Risk Analysis")
    print("="*60)
    test_risk_analysis(hr_token, leave_id)
    
    # Step 4: HR approves
    print("\n" + "="*60)
    print("STEP 4: HR Approves & Forwards to TL")
    print("="*60)
    test_hr_approve(hr_token, leave_id)
    
    # Step 5: Login as TL
    print("\n" + "="*60)
    print("STEP 5: Login as TL")
    print("="*60)
    tl_token = login(TEST_USERS["tl"]["email"], TEST_USERS["tl"]["password"])
    
    if not tl_token:
        print("\n⚠ Please update TL credentials in the script")
        return
    
    # Step 6: Get pending leaves for TL
    print("\n" + "="*60)
    print("STEP 6: Get Pending Leaves (TL View)")
    print("="*60)
    test_get_pending_leaves(tl_token, "TL")
    
    # Step 7: TL makes decision
    print("\n" + "="*60)
    print("STEP 7: TL Decision")
    print("="*60)
    print("Choose action: 'approve' for low risk OR 'forward_to_pm' for high risk")
    
    # For testing, let's forward to PM
    test_tl_decision(tl_token, leave_id, "forward_to_pm")
    
    # Step 8: Login as PM
    print("\n" + "="*60)
    print("STEP 8: Login as PM")
    print("="*60)
    pm_token = login(TEST_USERS["pm"]["email"], TEST_USERS["pm"]["password"])
    
    if not pm_token:
        print("\n⚠ Please update PM credentials in the script")
        return
    
    # Step 9: Get pending leaves for PM
    print("\n" + "="*60)
    print("STEP 9: Get Pending Leaves (PM View)")
    print("="*60)
    test_get_pending_leaves(pm_token, "PM")
    
    # Step 10: PM makes final decision
    print("\n" + "="*60)
    print("STEP 10: PM Final Decision")
    print("="*60)
    test_pm_decision(pm_token, leave_id, "approve")
    
    print("\n" + "="*60)
    print("✓ WORKFLOW TEST COMPLETED!")
    print("="*60)
    print("\nWorkflow: HR → TL → PM → Approved")


if __name__ == "__main__":
    main()
