import re

# Read the file
with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and update PM permissions (around line 539-540)
for i, line in enumerate(lines):
    if 'if is_project_manager(user):' in line and i < 600:
        # Insert sidebar config after the return { line
        if lines[i+1].strip() == 'return {':
            sidebar_config = '''            "sidebar": {
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
'''
            lines.insert(i+2, sidebar_config)
            print(f"Added PM sidebar config at line {i+2}")
            break

# Write back
with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("PM sidebar configuration added successfully!")
