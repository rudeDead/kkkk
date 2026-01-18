import re

# Read the file
with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and update TL permissions
tl_added = False
employee_added = False

for i, line in enumerate(lines):
    # Add TL sidebar config
    if 'if is_technical_lead(user):' in line and not tl_added:
        # Find the return { line
        for j in range(i, min(i+10, len(lines))):
            if 'return {' in lines[j]:
                sidebar_config = '''            "sidebar": {
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
'''
                lines.insert(j+1, sidebar_config)
                print(f"Added TL sidebar config at line {j+1}")
                tl_added = True
                break
    
    # Add Employee sidebar config
    if 'return {' in line and i > 650 and not employee_added:  # Employee section is near the end
        # Check if this is the employee permissions section
        prev_lines = ''.join(lines[max(0, i-10):i])
        if 'EMPLOYEE PERMISSIONS' in prev_lines or (i > 700 and not employee_added):
            sidebar_config = '''            "sidebar": {
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
'''
            lines.insert(i+1, sidebar_config)
            print(f"Added Employee sidebar config at line {i+1}")
            employee_added = True
            break

# Write back
with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nSidebar configurations added:")
print(f"  - TL: {tl_added}")
print(f"  - Employee: {employee_added}")
