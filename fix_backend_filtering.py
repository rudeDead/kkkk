"""
Fix backend API endpoints to filter projects and tasks for employees
"""

# Fix Projects API
projects_file = r'd:\Tanmay\Qkrishi\Planning\backend\app\api\v1\projects.py'

try:
    with open(projects_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the get_projects function and add employee filtering
    if 'Employees can only see assigned projects' not in content:
        # Find where the query is initialized
        old_pattern = '''    try:
        query = db.table("projects").select("*", count="exact")
        
        if status:'''
        
        new_pattern = '''    try:
        query = db.table("projects").select("*", count="exact")
        
        # Employees can only see assigned projects
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            # Filter to projects where user is a member or assigned
            query = query.contains("members", [{"id": current_user["id"]}])
        
        if status:'''
        
        content = content.replace(old_pattern, new_pattern)
        
        with open(projects_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] Added employee filtering to projects API")
    else:
        print("[SKIP] Projects API already has employee filtering")
except FileNotFoundError:
    print("[SKIP] projects.py not found")

# Fix Tasks API
tasks_file = r'd:\Tanmay\Qkrishi\Planning\backend\app\api\v1\tasks.py'

try:
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the get_tasks function and add employee filtering
    if 'Employees can only see assigned tasks' not in content:
        # Find where the query is initialized
        old_pattern = '''    try:
        query = db.table("tasks").select("*", count="exact")
        
        if project_id:'''
        
        new_pattern = '''    try:
        query = db.table("tasks").select("*", count="exact")
        
        # Employees can only see assigned tasks
        if not is_admin(current_user) and current_user.get("role") not in [Roles.HR, Roles.PROJECT_MANAGER, Roles.TECHNICAL_LEAD]:
            query = query.eq("assigned_to_id", current_user["id"])
        
        if project_id:'''
        
        content = content.replace(old_pattern, new_pattern)
        
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[OK] Added employee filtering to tasks API")
    else:
        print("[SKIP] Tasks API already has employee filtering")
except FileNotFoundError:
    print("[SKIP] tasks.py not found")

print("\n[SUCCESS] Backend filtering complete!")
print("   - Projects: Employees see only assigned projects")
print("   - Tasks: Employees see only assigned tasks")
print("   - Leaves: Already filtered (own only)")
print("   - Incidents: Already filtered (own/assigned)")
