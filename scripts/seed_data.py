"""
Seed Data Script
Creates initial admin user and sample data for testing
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import db
from app.core.security import hash_password
from app.config import settings


def create_admin_user():
    """Create initial admin user"""
    print("\n" + "=" * 60)
    print("CREATING ADMIN USER")
    print("=" * 60)
    
    client = db.get_service_client()
    
    try:
        # Check if admin already exists
        response = client.table("users").select("*").eq("email", "admin@qkrew.com").execute()
        
        if response.data and len(response.data) > 0:
            print("[INFO] Admin user already exists")
            print(f"[INFO] Email: admin@qkrew.com")
            return response.data[0]
        
        # Create admin user
        # Note: bcrypt has 72 byte limit, truncate password if needed
        password = "admin123"[:72]
        
        admin_data = {
            "email": "admin@qkrew.com",
            "password_hash": hash_password(password),
            "name": "Admin User",
            "role": "admin",
            "hierarchy_level": "L1",
            "department": "Management",
            "status": "active",
            "skills": ["Leadership", "Management", "Strategy"],
            "experience_years": 15,
            "weekly_capacity": 40,
            "assignment_status": "assigned",
            "current_workload_percent": 100,
            "active_project_count": 0,
            "active_task_count": 0,
            "has_blocking_incident": False
        }
        
        response = client.table("users").insert(admin_data).execute()
        
        if response.data and len(response.data) > 0:
            admin = response.data[0]
            print("[OK] Admin user created successfully!")
            print(f"[OK] ID: {admin['id']}")
            print(f"[OK] Email: {admin['email']}")
            print(f"[OK] Role: {admin['role']}")
            print(f"[OK] Hierarchy: {admin['hierarchy_level']}")
            print("\n" + "-" * 60)
            print("LOGIN CREDENTIALS:")
            print("Email: admin@qkrew.com")
            print("Password: admin123")
            print("-" * 60)
            return admin
        else:
            print("[ERROR] Failed to create admin user")
            return None
            
    except Exception as e:
        print(f"[ERROR] Failed to create admin: {str(e)}")
        return None


def create_sample_users():
    """Create sample users for testing"""
    print("\n" + "=" * 60)
    print("CREATING SAMPLE USERS")
    print("=" * 60)
    
    client = db.get_service_client()
    
    sample_users = [
        # L3 - Director (Project Manager)
        {
            "email": "pm@qkrew.com",
            "password_hash": hash_password("pm123"[:72]),
            "name": "John Director",
            "role": "project_manager",
            "hierarchy_level": "L3",
            "department": "Engineering",
            "status": "active",
            "skills": ["Project Management", "Agile", "Scrum"],
            "experience_years": 10,
            "weekly_capacity": 40
        },
        # L4 - Engineering Manager (Project Manager)
        {
            "email": "em@qkrew.com",
            "password_hash": hash_password("em123"[:72]),
            "name": "Sarah Manager",
            "role": "project_manager",
            "hierarchy_level": "L4",
            "department": "Engineering",
            "status": "active",
            "skills": ["Project Management", "Team Leadership", "Delivery"],
            "experience_years": 8,
            "weekly_capacity": 40
        },
        # L5 - Senior Manager (Project Manager)
        {
            "email": "sm@qkrew.com",
            "password_hash": hash_password("sm123"[:72]),
            "name": "Mike Senior",
            "role": "project_manager",
            "hierarchy_level": "L5",
            "department": "Engineering",
            "status": "active",
            "skills": ["Cross-functional Coordination", "Strategy", "Planning"],
            "experience_years": 12,
            "weekly_capacity": 40
        },
        # L6 - Principal Architect (Technical Lead)
        {
            "email": "architect@qkrew.com",
            "password_hash": hash_password("arch123"[:72]),
            "name": "David Architect",
            "role": "technical_lead",
            "hierarchy_level": "L6",
            "department": "Engineering",
            "status": "active",
            "skills": ["System Architecture", "Python", "FastAPI", "PostgreSQL", "AWS"],
            "experience_years": 12,
            "weekly_capacity": 40
        },
        # L7 - Team Lead (Technical Lead)
        {
            "email": "lead@qkrew.com",
            "password_hash": hash_password("lead123"[:72]),
            "name": "Emily Lead",
            "role": "technical_lead",
            "hierarchy_level": "L7",
            "department": "Engineering",
            "status": "active",
            "skills": ["Python", "FastAPI", "React", "Leadership", "Mentoring"],
            "experience_years": 8,
            "weekly_capacity": 40
        },
        # HR Manager
        {
            "email": "hr@qkrew.com",
            "password_hash": hash_password("hr123"[:72]),
            "name": "HR Manager",
            "role": "hr",
            "hierarchy_level": "L4",
            "department": "Human Resources",
            "status": "active",
            "skills": ["HR Management", "Recruitment", "Employee Relations"],
            "experience_years": 7,
            "weekly_capacity": 40
        },
        # L8 - Senior Engineer (Employee)
        {
            "email": "senior@qkrew.com",
            "password_hash": hash_password("sen123"[:72]),
            "name": "Robert Senior",
            "role": "employee",
            "hierarchy_level": "L8",
            "department": "Engineering",
            "status": "active",
            "skills": ["Python", "React", "Mentoring", "Code Review"],
            "experience_years": 6,
            "weekly_capacity": 40
        },
        # L9 - Software Engineer (Employee)
        {
            "email": "employee@qkrew.com",
            "password_hash": hash_password("emp123"[:72]),
            "name": "Alice Engineer",
            "role": "employee",
            "hierarchy_level": "L9",
            "department": "Engineering",
            "status": "active",
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "experience_years": 3,
            "weekly_capacity": 40
        }
    ]
    
    created_count = 0
    
    for user_data in sample_users:
        try:
            # Check if user exists
            response = client.table("users").select("*").eq("email", user_data["email"]).execute()
            
            if response.data and len(response.data) > 0:
                print(f"[INFO] User {user_data['email']} already exists")
                continue
            
            # Create user
            response = client.table("users").insert(user_data).execute()
            
            if response.data and len(response.data) > 0:
                user = response.data[0]
                print(f"[OK] Created: {user['email']} ({user['role']} - {user['hierarchy_level']})")
                created_count += 1
                
        except Exception as e:
            print(f"[ERROR] Failed to create {user_data['email']}: {str(e)}")
    
    print(f"\n[OK] Created {created_count} sample users")
    
    if created_count > 0:
        print("\n" + "-" * 60)
        print("SAMPLE USER CREDENTIALS:")
        print("-" * 60)
        print("L3 Director (PM): pm@qkrew.com / pm123")
        print("L4 Eng Manager (PM): em@qkrew.com / em123")
        print("L5 Senior Manager (PM): sm@qkrew.com / sm123")
        print("L6 Principal Architect: architect@qkrew.com / arch123")
        print("L7 Team Lead: lead@qkrew.com / lead123")
        print("L8 Senior Engineer: senior@qkrew.com / sen123")
        print("L9 Software Engineer: employee@qkrew.com / emp123")
        print("HR Manager: hr@qkrew.com / hr123")
        print("-" * 60)


def main():
    """Run seed data script"""
    print("\n" + "=" * 60)
    print("QKREW BACKEND - SEED DATA SCRIPT")
    print("=" * 60)
    
    # Connect to database
    db.connect()
    
    # Create admin user
    admin = create_admin_user()
    
    if not admin:
        print("\n[ERROR] Failed to create admin user. Exiting.")
        return 1
    
    # Create sample users
    create_sample_users()
    
    print("\n" + "=" * 60)
    print("SEED DATA COMPLETE!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Visit API docs: http://localhost:8000/docs")
    print("3. Login with admin credentials")
    print("=" * 60 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
