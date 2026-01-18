"""
Script to add "Own Quota" filtering to backend API endpoints
Ensures employees only see their own data
"""

import re

# ============================================================================
# INCIDENTS.PY - Add employee filtering
# ============================================================================
incidents_file = r'd:\Tanmay\Qkrishi\Planning\backend\app\api\v1\incidents.py'

with open(incidents_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_incidents function and add filtering after the query initialization
old_pattern = r'(query = db\.table\("incidents"\)\.select\("\*", count="exact"\)\s+)(if project_id:)'
new_code = r'''\1
        # Employees can only see their own incidents (reported by or assigned to)
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            # Filter to incidents where user is reporter or assignee
            query = query.or_(f"reported_by_id.eq.{current_user['id']},assigned_to_id.eq.{current_user['id']}")
        
        \2'''

content = re.sub(old_pattern, new_code, content)

with open(incidents_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Added 'Own Quota' filtering to incidents.py")

# ============================================================================
# SOFTWARE REQUESTS - Check if exists and add filtering
# ============================================================================
try:
    sw_requests_file = r'd:\Tanmay\Qkrishi\Planning\backend\app\api\v1\software_requests.py'
    
    with open(sw_requests_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add filtering for software requests
    old_pattern = r'(query = db\.table\("software_requests"\)\.select\("\*", count="exact"\)\s+)(if status:)'
    new_code = r'''\1
        # Employees can only see their own software requests
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            query = query.eq("requested_by_id", current_user["id"])
        
        \2'''
    
    content = re.sub(old_pattern, new_code, content)
    
    with open(sw_requests_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Added 'Own Quota' filtering to software_requests.py")
except FileNotFoundError:
    print("[SKIP] software_requests.py not found")

# ============================================================================
# BUSINESS TRIPS - Check if exists and add filtering
# ============================================================================
try:
    trips_file = r'd:\Tanmay\Qkrishi\Planning\backend\app\api\v1\business_trips.py'
    
    with open(trips_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add filtering for business trips
    old_pattern = r'(query = db\.table\("business_trips"\)\.select\("\*", count="exact"\)\s+)(if status:)'
    new_code = r'''\1
        # Employees can only see their own business trips
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            query = query.eq("employee_id", current_user["id"])
        
        \2'''
    
    content = re.sub(old_pattern, new_code, content)
    
    with open(trips_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Added 'Own Quota' filtering to business_trips.py")
except FileNotFoundError:
    print("[SKIP] business_trips.py not found")

print("\n[SUCCESS] Backend 'Own Quota' filtering complete!")
print("   - Leaves: Already has filtering")
print("   - Incidents: Now filters by reporter/assignee")
print("   - Software Requests: Now filters by requester")
print("   - Business Trips: Now filters by employee")
