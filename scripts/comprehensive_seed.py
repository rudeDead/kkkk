"""
Comprehensive Seed Data Script
Populates all database tables with realistic test data
- 20+ employees across L2-L12
- 5 projects with full team assignments
- Tasks, incidents, leaves, and more
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import db
from app.core.security import hash_password


# ============================================================================
# EMPLOYEE DATA (25 employees across L2-L12)
# ============================================================================
EMPLOYEES = [
    # L2 - VP Engineering (Admin)
    {"email": "vp@qkrew.com", "name": "Victoria VP", "role": "admin", "level": "L2", "dept": "Engineering", "skills": ["Leadership", "Strategy", "Architecture"], "exp": 18},
    
    # L3 - Directors (Project Managers)
    {"email": "john.director@qkrew.com", "name": "John Director", "role": "project_manager", "level": "L3", "dept": "Engineering", "skills": ["Project Management", "Agile", "Scrum"], "exp": 12},
    {"email": "lisa.director@qkrew.com", "name": "Lisa Director", "role": "project_manager", "level": "L3", "dept": "Product", "skills": ["Product Strategy", "Roadmapping", "Analytics"], "exp": 11},
    
    # L4 - Engineering Managers (Project Managers)
    {"email": "sarah.manager@qkrew.com", "name": "Sarah Manager", "role": "project_manager", "level": "L4", "dept": "Engineering", "skills": ["Team Leadership", "Delivery", "Agile"], "exp": 9},
    {"email": "mark.manager@qkrew.com", "name": "Mark Manager", "role": "project_manager", "level": "L4", "dept": "Engineering", "skills": ["Project Planning", "Risk Management", "Stakeholder Management"], "exp": 8},
    
    # L5 - Senior Managers (Project Managers)
    {"email": "mike.senior@qkrew.com", "name": "Mike Senior", "role": "project_manager", "level": "L5", "dept": "Engineering", "skills": ["Cross-functional Coordination", "Strategy", "Planning"], "exp": 10},
    
    # L6 - Principal Architects (Technical Leads)
    {"email": "david.architect@qkrew.com", "name": "David Architect", "role": "technical_lead", "level": "L6", "dept": "Engineering", "skills": ["System Architecture", "Python", "FastAPI", "PostgreSQL", "AWS", "Microservices"], "exp": 14},
    {"email": "sophia.architect@qkrew.com", "name": "Sophia Architect", "role": "technical_lead", "level": "L6", "dept": "Engineering", "skills": ["Cloud Architecture", "Kubernetes", "DevOps", "Security"], "exp": 13},
    
    # L7 - Team Leads (Technical Leads)
    {"email": "emily.lead@qkrew.com", "name": "Emily Lead", "role": "technical_lead", "level": "L7", "dept": "Engineering", "skills": ["Python", "FastAPI", "React", "Leadership", "Mentoring"], "exp": 8},
    {"email": "james.lead@qkrew.com", "name": "James Lead", "role": "technical_lead", "level": "L7", "dept": "Engineering", "skills": ["Full Stack", "Node.js", "React", "Team Management"], "exp": 7},
    {"email": "olivia.lead@qkrew.com", "name": "Olivia Lead", "role": "technical_lead", "level": "L7", "dept": "Engineering", "skills": ["Backend", "Python", "Django", "Code Review"], "exp": 7},
    
    # L8 - Senior Engineers (Employees)
    {"email": "robert.senior@qkrew.com", "name": "Robert Senior", "role": "employee", "level": "L8", "dept": "Engineering", "skills": ["Python", "React", "Mentoring", "Code Review", "Testing"], "exp": 6},
    {"email": "emma.senior@qkrew.com", "name": "Emma Senior", "role": "employee", "level": "L8", "dept": "Engineering", "skills": ["Full Stack", "TypeScript", "Node.js", "PostgreSQL"], "exp": 6},
    
    # L9 - Software Engineers (Employees)
    {"email": "alice.engineer@qkrew.com", "name": "Alice Engineer", "role": "employee", "level": "L9", "dept": "Engineering", "skills": ["Python", "JavaScript", "React", "SQL"], "exp": 4},
    {"email": "bob.engineer@qkrew.com", "name": "Bob Engineer", "role": "employee", "level": "L9", "dept": "Engineering", "skills": ["Backend", "FastAPI", "PostgreSQL", "Redis"], "exp": 4},
    {"email": "carol.engineer@qkrew.com", "name": "Carol Engineer", "role": "employee", "level": "L9", "dept": "Engineering", "skills": ["Frontend", "React", "TypeScript", "CSS"], "exp": 3},
    
    # L10 - Associate Engineers (Employees)
    {"email": "daniel.associate@qkrew.com", "name": "Daniel Associate", "role": "employee", "level": "L10", "dept": "Engineering", "skills": ["Python", "JavaScript", "Git"], "exp": 2},
    {"email": "fiona.associate@qkrew.com", "name": "Fiona Associate", "role": "employee", "level": "L10", "dept": "Engineering", "skills": ["React", "HTML", "CSS", "JavaScript"], "exp": 2},
    
    # L11 - Junior Engineers (Employees)
    {"email": "george.junior@qkrew.com", "name": "George Junior", "role": "employee", "level": "L11", "dept": "Engineering", "skills": ["Python", "SQL", "Git"], "exp": 1},
    {"email": "hannah.junior@qkrew.com", "name": "Hannah Junior", "role": "employee", "level": "L11", "dept": "Engineering", "skills": ["JavaScript", "React", "HTML"], "exp": 1},
    
    # L12 - Trainees (Employees)
    {"email": "ian.trainee@qkrew.com", "name": "Ian Trainee", "role": "employee", "level": "L12", "dept": "Engineering", "skills": ["Python Basics", "Web Development"], "exp": 0},
    {"email": "julia.trainee@qkrew.com", "name": "Julia Trainee", "role": "employee", "level": "L12", "dept": "Engineering", "skills": ["JavaScript Basics", "React Basics"], "exp": 0},
    
    # HR Team
    {"email": "hr.manager@qkrew.com", "name": "Helen HR", "role": "hr", "level": "L4", "dept": "Human Resources", "skills": ["HR Management", "Recruitment", "Employee Relations", "Compliance"], "exp": 8},
    {"email": "hr.specialist@qkrew.com", "name": "Henry HR", "role": "hr", "level": "L6", "dept": "Human Resources", "skills": ["Talent Acquisition", "Onboarding", "Training"], "exp": 5},
]

# ============================================================================
# PROJECT DATA (5 projects)
# ============================================================================
PROJECTS = [
    {
        "name": "E-Commerce Platform Redesign",
        "description": "Complete overhaul of the e-commerce platform with modern UI/UX and microservices architecture",
        "type": "delivery",
        "priority": "high",
        "status": "active",
        "risk_level": "medium",
        "total_hours": 2000,
        "done_hours": 800,
        "skills": ["React", "Node.js", "PostgreSQL", "AWS", "Microservices"],
        "tech_stack": ["React", "Node.js", "FastAPI", "PostgreSQL", "Redis", "AWS"],
        "start_date": "2026-01-01",
        "deadline": "2026-06-30"
    },
    {
        "name": "Mobile App Development",
        "description": "Native mobile applications for iOS and Android with real-time features",
        "type": "delivery",
        "priority": "critical",
        "status": "active",
        "risk_level": "high",
        "total_hours": 1500,
        "done_hours": 300,
        "skills": ["React Native", "TypeScript", "Firebase", "Mobile Development"],
        "tech_stack": ["React Native", "TypeScript", "Firebase", "Redux"],
        "start_date": "2026-01-15",
        "deadline": "2026-05-31"
    },
    {
        "name": "Internal Analytics Dashboard",
        "description": "Real-time analytics and reporting dashboard for business intelligence",
        "type": "internal",
        "priority": "medium",
        "status": "active",
        "risk_level": "low",
        "total_hours": 800,
        "done_hours": 600,
        "skills": ["Python", "React", "Data Visualization", "SQL"],
        "tech_stack": ["Python", "FastAPI", "React", "Recharts", "PostgreSQL"],
        "start_date": "2025-11-01",
        "deadline": "2026-02-28"
    },
    {
        "name": "AI Chatbot Integration",
        "description": "Intelligent chatbot for customer support with NLP capabilities",
        "type": "research",
        "priority": "medium",
        "status": "planning",
        "risk_level": "high",
        "total_hours": 1200,
        "done_hours": 0,
        "skills": ["Python", "Machine Learning", "NLP", "API Integration"],
        "tech_stack": ["Python", "TensorFlow", "FastAPI", "OpenAI API"],
        "start_date": "2026-02-01",
        "deadline": "2026-07-31"
    },
    {
        "name": "Legacy System Migration",
        "description": "Migration of legacy monolith to modern microservices architecture",
        "type": "maintenance",
        "priority": "high",
        "status": "active",
        "risk_level": "high",
        "total_hours": 3000,
        "done_hours": 1200,
        "skills": ["Python", "Django", "FastAPI", "Docker", "Kubernetes"],
        "tech_stack": ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"],
        "start_date": "2025-10-01",
        "deadline": "2026-08-31"
    }
]


def create_employees():
    """Create all employees"""
    print("\n" + "=" * 60)
    print("CREATING EMPLOYEES")
    print("=" * 60)
    
    client = db.get_service_client()
    created_users = {}
    password = "qkrew123"  # Same password for all
    
    for emp in EMPLOYEES:
        try:
            # Check if exists
            response = client.table("users").select("*").eq("email", emp["email"]).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[INFO] {emp['email']} already exists")
                created_users[emp["email"]] = response.data[0]
                continue
            
            # Create user
            user_data = {
                "email": emp["email"],
                "password_hash": hash_password(password[:72]),
                "name": emp["name"],
                "role": emp["role"],
                "hierarchy_level": emp["level"],
                "department": emp["dept"],
                "status": "active",
                "skills": emp["skills"],
                "experience_years": emp["exp"],
                "weekly_capacity": 40
            }
            
            response = client.table("users").insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                created_users[emp["email"]] = user
                print(f"[OK] Created: {emp['name']} ({emp['level']} - {emp['role']})")
                
        except Exception as e:
            print(f"[ERROR] Failed to create {emp['email']}: {str(e)}")
    
    return created_users


def create_projects(users):
    """Create projects with proper team assignments"""
    print("\n" + "=" * 60)
    print("CREATING PROJECTS")
    print("=" * 60)
    
    client = db.get_service_client()
    created_projects = []
    
    # Get user IDs by role
    pms = [u for u in users.values() if u['hierarchy_level'] in ['L3', 'L4', 'L5']]
    architects = [u for u in users.values() if u['hierarchy_level'] == 'L6' and u['role'] == 'technical_lead']
    team_leads = [u for u in users.values() if u['hierarchy_level'] == 'L7']
    
    for idx, proj in enumerate(PROJECTS):
        try:
            # Check if exists
            response = client.table("projects").select("*").eq("name", proj["name"]).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[INFO] Project '{proj['name']}' already exists")
                created_projects.append(response.data[0])
                continue
            
            # Assign leadership
            pm = pms[idx % len(pms)]
            architect = architects[idx % len(architects)] if architects else None
            tl = team_leads[idx % len(team_leads)]
            
            project_data = {
                "name": proj["name"],
                "description": proj["description"],
                "project_manager_id": pm["id"],
                "principal_architect_id": architect["id"] if architect else None,
                "team_lead_id": tl["id"],
                "required_skills": proj["skills"],
                "tech_stack": proj["tech_stack"],
                "project_type": proj["type"],
                "priority": proj["priority"],
                "status": proj["status"],
                "risk_level": proj["risk_level"],
                "total_hours": proj["total_hours"],
                "done_hours": proj["done_hours"],
                "progress": round((proj["done_hours"] / proj["total_hours"]) * 100, 2),
                "start_date": proj["start_date"],
                "deadline": proj["deadline"]
            }
            
            response = client.table("projects").insert(project_data).execute()
            
            if response.data and len(response.data) > 0:
                project = response.data[0]
                created_projects.append(project)
                print(f"[OK] Created: {proj['name']}")
                print(f"     PM: {pm['name']}, Architect: {architect['name'] if architect else 'None'}, TL: {tl['name']}")
                
        except Exception as e:
            print(f"[ERROR] Failed to create project '{proj['name']}': {str(e)}")
    
    return created_projects


def assign_project_members(projects, users):
    """Assign team members to projects"""
    print("\n" + "=" * 60)
    print("ASSIGNING PROJECT MEMBERS")
    print("=" * 60)
    
    client = db.get_service_client()
    
    # Get engineers (L8-L12)
    engineers = [u for u in users.values() if u['hierarchy_level'] in ['L8', 'L9', 'L10', 'L11', 'L12']]
    
    for idx, project in enumerate(projects):
        # Assign 3-5 engineers per project
        num_members = min(5, len(engineers))
        start_idx = (idx * 3) % len(engineers)
        project_engineers = engineers[start_idx:start_idx + num_members]
        
        for eng in project_engineers:
            try:
                # Check if already assigned
                response = client.table("project_members").select("*").eq("project_id", project["id"]).eq("user_id", eng["id"]).execute()
                
                if response.data and len(response.data) > 0:
                    continue
                
                member_data = {
                    "project_id": project["id"],
                    "user_id": eng["id"],
                    "role": "Developer",
                    "allocation_percent": 100 if idx == 0 else 50  # First project gets 100%
                }
                
                client.table("project_members").insert(member_data).execute()
                print(f"[OK] Assigned {eng['name']} to {project['name']}")
                
            except Exception as e:
                print(f"[ERROR] Failed to assign member: {str(e)}")


def create_tasks(projects, users):
    """Create tasks for projects"""
    print("\n" + "=" * 60)
    print("CREATING TASKS")
    print("=" * 60)
    
    client = db.get_service_client()
    
    task_templates = [
        {"title": "Setup project infrastructure", "priority": "high", "status": "completed", "hours": 40, "progress": 100},
        {"title": "Design database schema", "priority": "high", "status": "completed", "hours": 24, "progress": 100},
        {"title": "Implement authentication module", "priority": "critical", "status": "in_progress", "hours": 60, "progress": 70},
        {"title": "Build user dashboard", "priority": "high", "status": "in_progress", "hours": 80, "progress": 45},
        {"title": "Create API endpoints", "priority": "medium", "status": "in_progress", "hours": 100, "progress": 30},
        {"title": "Write unit tests", "priority": "medium", "status": "not_started", "hours": 40, "progress": 0},
        {"title": "Setup CI/CD pipeline", "priority": "high", "status": "not_started", "hours": 32, "progress": 0},
        {"title": "Performance optimization", "priority": "low", "status": "not_started", "hours": 50, "progress": 0},
    ]
    
    engineers = [u for u in users.values() if u['hierarchy_level'] in ['L8', 'L9', 'L10', 'L11']]
    
    for project in projects:
        # Create 5-8 tasks per project
        num_tasks = min(8, len(task_templates))
        
        for i in range(num_tasks):
            task = task_templates[i]
            assignee = engineers[i % len(engineers)]
            
            try:
                task_data = {
                    "title": f"{task['title']} - {project['name'][:30]}",
                    "description": f"Task for {project['name']}",
                    "project_id": project["id"],
                    "assignee_id": assignee["id"],
                    "priority": task["priority"],
                    "status": task["status"],
                    "progress": task["progress"],
                    "estimated_hours": task["hours"],
                    "actual_hours": int(task["hours"] * task["progress"] / 100),
                    "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                }
                
                response = client.table("tasks").insert(task_data).execute()
                if response.data:
                    print(f"[OK] Created task: {task['title'][:40]}...")
                    
            except Exception as e:
                print(f"[ERROR] Failed to create task: {str(e)}")


def create_incidents(projects, users):
    """Create incidents"""
    print("\n" + "=" * 60)
    print("CREATING INCIDENTS")
    print("=" * 60)
    
    client = db.get_service_client()
    
    incidents = [
        {"title": "Production server downtime", "severity": "critical", "status": "resolved"},
        {"title": "Database connection timeout", "severity": "high", "status": "in_progress"},
        {"title": "UI rendering issue on mobile", "severity": "medium", "status": "open"},
        {"title": "API rate limiting error", "severity": "high", "status": "in_progress"},
        {"title": "Memory leak in background job", "severity": "medium", "status": "open"},
    ]
    
    engineers = [u for u in users.values() if u['hierarchy_level'] in ['L8', 'L9', 'L10']]
    
    for idx, inc in enumerate(incidents):
        project = projects[idx % len(projects)]
        reporter = engineers[idx % len(engineers)]
        assignee = engineers[(idx + 1) % len(engineers)]
        
        try:
            incident_data = {
                "title": inc["title"],
                "description": f"Incident reported in {project['name']}",
                "project_id": project["id"],
                "severity": inc["severity"],
                "status": inc["status"],
                "reported_by_id": reporter["id"],
                "assigned_to_id": assignee["id"]
            }
            
            response = client.table("incidents").insert(incident_data).execute()
            if response.data:
                print(f"[OK] Created incident: {inc['title']}")
                
        except Exception as e:
            print(f"[ERROR] Failed to create incident: {str(e)}")


def create_leaves(users):
    """Create leave requests"""
    print("\n" + "=" * 60)
    print("CREATING LEAVE REQUESTS")
    print("=" * 60)
    
    client = db.get_service_client()
    
    employees = [u for u in users.values() if u['role'] == 'employee']
    
    leave_types = ['casual', 'sick', 'earned']
    statuses = ['approved', 'pending_hr_review', 'forwarded_to_team_lead']
    
    for i in range(10):  # Create 10 leave requests
        emp = employees[i % len(employees)]
        
        start_date = datetime.now() + timedelta(days=(i * 7))
        end_date = start_date + timedelta(days=3)
        
        try:
            leave_data = {
                "employee_id": emp["id"],
                "leave_type": leave_types[i % len(leave_types)],
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": 3,
                "reason": f"Personal leave request {i+1}",
                "status": statuses[i % len(statuses)]
            }
            
            response = client.table("leaves").insert(leave_data).execute()
            if response.data:
                print(f"[OK] Created leave for {emp['name']}")
                
        except Exception as e:
            print(f"[ERROR] Failed to create leave: {str(e)}")


def save_credentials():
    """Save all credentials to a text file"""
    print("\n" + "=" * 60)
    print("SAVING CREDENTIALS")
    print("=" * 60)
    
    credentials_file = os.path.join(os.path.dirname(__file__), "employee_credentials.txt")
    
    with open(credentials_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("QKREW - EMPLOYEE CREDENTIALS\n")
        f.write("=" * 70 + "\n\n")
        f.write("DEFAULT PASSWORD FOR ALL EMPLOYEES: qkrew123\n\n")
        f.write("=" * 70 + "\n\n")
        
        for emp in EMPLOYEES:
            f.write(f"{emp['name']:30} | {emp['email']:35} | {emp['level']} - {emp['role']}\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write("ADMIN CREDENTIALS:\n")
        f.write("Email: admin@qkrew.com | Password: admin123\n")
        f.write("=" * 70 + "\n")
    
    print(f"[OK] Credentials saved to: {credentials_file}")


def main():
    """Run comprehensive seed script"""
    print("\n" + "=" * 80)
    print("QKREW - COMPREHENSIVE SEED DATA SCRIPT")
    print("=" * 80)
    
    # Connect to database
    db.connect()
    
    # Create all data
    users = create_employees()
    projects = create_projects(users)
    assign_project_members(projects, users)
    create_tasks(projects, users)
    create_incidents(projects, users)
    create_leaves(users)
    save_credentials()
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE SEED DATA COMPLETE!")
    print("=" * 80)
    print(f"\nCreated:")
    print(f"  - {len(users)} employees (L2-L12)")
    print(f"  - {len(projects)} projects")
    print(f"  - ~40 tasks")
    print(f"  - ~5 incidents")
    print(f"  - ~10 leave requests")
    print("\nCredentials saved to: employee_credentials.txt")
    print("Default password for all: qkrew123")
    print("=" * 80 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
