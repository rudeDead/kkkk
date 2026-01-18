import re

# Read the file
with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the orphaned duplicate section (lines 456-552)
# The pattern is: after the first closing brace of admin permissions,
# there's a duplicate set of permissions that shouldn't be there

# Split at the problematic section
parts = content.split('        }\n    \n                "view": True,')

if len(parts) == 2:
    # Remove everything until the HR PERMISSIONS comment
    before = parts[0] + '        }\n    \n    # ============================================================================\n    # HR PERMISSIONS\n    # ============================================================================\n    if is_hr(user):\n        return {\n            "sidebar": {\n                "dashboard": True,\n                "projects": True,\n                "tasks": False,\n                "employees": True,\n                "teams": True,\n                "leaves": True,\n                "incidents": False,\n                "software_requests": True,\n                "notice_period": True,\n                "events": True,\n                "analytics": True,\n                "esp": True,\n                "business_trips": True,\n                "leave_conflicts": True,\n                "chatbot": True\n            },'
    
    # Find where the original HR permissions start
    after_idx = parts[1].find('            "projects": {"view_all": True},')
    if after_idx != -1:
        after = parts[1][after_idx:]
        fixed_content = before + '\n' + after
        
        # Write back
        with open(r'd:\Tanmay\Qkrishi\Planning\backend\app\core\rbac.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print("File fixed successfully!")
    else:
        print("Could not find HR permissions start")
else:
    print("Pattern not found in file")
