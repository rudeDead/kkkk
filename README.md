# 🚀 QKREW V4 Backend

Enterprise Workforce Management Platform - FastAPI + Supabase

## 📋 Overview

QKREW V4 is a comprehensive enterprise-grade backend system for managing workforce operations across 13 organizational hierarchy levels. Features include employee management, project tracking, AI-powered staffing simulation (ESP), intelligent leave conflict detection, incident management, and complete RBAC with 72+ granular permissions.

## 🛠️ Tech Stack

- **Framework:** FastAPI 0.109.0
- **Database:** Supabase (PostgreSQL 14+)
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt (passlib)
- **AI Features:** OpenRouter API (HR Chatbot)
- **HTTP Client:** httpx (async)
- **Python:** 3.11+

## 🎯 Key Features

### **18 Integrated API Modules**
1. **Authentication** - JWT-based login, token refresh, permissions
2. **User Management** - CRUD, workload tracking, filtering
3. **Employee Hub** - Dashboard, skills, performance metrics
4. **Project Management** - Full lifecycle, team assignments, analytics
5. **Task Management** - Priority-based tracking, status workflows
6. **Team Management** - Technical teams, member management
7. **Leave Management** - Sequential approval (HR → TL → PM)
8. **Leave Conflicts** - AI-powered conflict detection
9. **Leave Manager** - Risk-based routing and approvals
10. **Incident Management** - Severity-based tracking, resolution
11. **Operations** - Software requests, notice periods, business trips
12. **Events** - Company events, participant registration
13. **Notes** - Project documentation, categorization
14. **ESP Manager** - Extra Staffing Projection (L7 → L6 → PM workflow)
15. **ESP Simulator** - Staffing impact simulation
16. **Dashboard** - Comprehensive KPIs and analytics
17. **Features** - Analytics, profile management
18. **Chatbot** - OpenRouter-powered HR assistant

### **AI-Powered Intelligence**
- ✅ **Leave Conflict Detection** - Rule-based engine analyzing critical tasks, incidents, and resource availability
- ✅ **ESP Simulation** - Skill-matching algorithm with capacity analysis and internal candidate discovery
- ✅ **HR Chatbot** - Natural language processing for HR queries
- ✅ **Risk Assessment** - Multi-factor analysis for leaves and projects

### **13-Level Organizational Hierarchy**
- **L1-L2:** CTO & VP Engineering (Strategic leadership)
- **L3-L5:** Directors & Senior Managers (Department oversight)
- **L6-L7:** Principal Architects & Team Leads (Technical leadership)
- **L8-L13:** Engineers & Specialists (Execution)

### **5 Primary Roles with 72+ Permissions**
- **Admin** - Full system access, policy creation, supreme control
- **HR** - Leave validation, employee management, event coordination
- **Project Manager** - Project oversight, final approvals, ESP decisions
- **Technical Lead** - Team management, ESP creation, leave approvals
- **Employee** - Task management, self-service operations

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/              # Core functionality
│   │   ├── security.py    # JWT, password hashing
│   │   ├── rbac.py        # Role-based access control
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/            # Pydantic schemas
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── ...
│   ├── api/v1/            # API routes (18 modules)
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── employees.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── teams.py
│   │   ├── leaves.py
│   │   ├── leave_manager.py
│   │   ├── leave_conflicts.py
│   │   ├── incidents.py
│   │   ├── operations.py
│   │   ├── events.py
│   │   ├── notes.py
│   │   ├── esp_manager.py
│   │   ├── esp_simulator.py
│   │   ├── dashboard.py
│   │   ├── features.py
│   │   └── chatbot.py
│   ├── config.py          # Configuration
│   ├── database.py        # Supabase client
│   └── main.py            # FastAPI app
├── scripts/
│   └── create_tables.sql  # Database schema
├── .env.example           # Environment template
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Supabase account
- OpenRouter API key (for chatbot)

### 2. Setup Supabase

1. Create project at https://supabase.com
2. Get credentials from Settings → API:
   - Project URL
   - Anon/Public Key
   - Service Role Key

### 3. Create Database Schema

1. Open Supabase SQL Editor
2. Copy `scripts/create_tables.sql`
3. Execute to create all tables

### 4. Install Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 5. Configure Environment

Create `.env` file:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SECRET_KEY=your-secret-key-minimum-32-characters
OPENROUTER_API_KEY=your-openrouter-key
```

### 6. Run Server

```bash
# Development mode
uvicorn app.main:app --reload --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7. Access API

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🔐 Authentication

### Login

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@qkrew.com",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "name": "Admin User",
    "email": "admin@qkrew.com",
    "role": "admin",
    "hierarchy_level": "L1"
  }
}
```

### Use Token

```bash
Authorization: Bearer <access_token>
```

## 📊 Database Schema

### Core Tables (19 Total)
1. **users** - Employee profiles, hierarchy, skills
2. **tech_teams** - Technical team structure
3. **tech_team_members** - Team membership
4. **projects** - Project lifecycle management
5. **project_members** - Project team assignments
6. **tasks** - Task tracking and workflows
7. **leaves** - Leave requests and approvals
8. **incidents** - Incident reporting and resolution
9. **software_requests** - Software procurement
10. **notice_periods** - Employee exit management
11. **business_trips** - Travel management
12. **events** - Company events
13. **event_participants** - Event registration
14. **notes** - Project documentation
15. **esp_packages** - Staffing projection packages
16. **esp_l7_recommendations** - L7 staffing recommendations
17. **esp_simulations** - AI simulation results
18. **esp_l6_reviews** - L6 technical reviews
19. **esp_pm_decisions** - PM final decisions

**Total Columns:** 250+

## 🎯 API Endpoints Overview

### Authentication & Users
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/employees/{id}/dashboard` - Employee dashboard

### Projects & Tasks
- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/tasks` - List tasks
- `POST /api/v1/tasks` - Create task

### Leave Management
- `GET /api/v1/leave-manager/pending` - Pending leaves
- `POST /api/v1/leave-manager/{id}/hr-approve` - HR approval
- `POST /api/v1/leave-manager/{id}/tl-decision` - TL decision
- `POST /api/v1/leave-manager/{id}/pm-decision` - PM decision
- `GET /api/v1/leave-conflicts/analyze/{id}` - Conflict analysis

### ESP (Extra Staffing Projection)
- `POST /api/v1/esp/packages` - Create ESP package (L7)
- `POST /api/v1/esp/{id}/simulate` - Run simulation (L6)
- `POST /api/v1/esp/{id}/l6-review` - L6 review
- `POST /api/v1/esp/{id}/pm-decision` - PM decision
- `GET /api/v1/esp/projects/{id}/skill-coverage` - Skill analysis

### Dashboard & Analytics
- `GET /api/v1/dashboard` - Main dashboard
- `GET /api/v1/analytics/projects` - Project analytics
- `GET /api/v1/analytics/tasks` - Task analytics

### Chatbot
- `POST /api/v1/chatbot/chat` - HR chatbot interaction

## 🔧 Workflow Systems

### 1. Leave Approval Workflow
```
Employee Request → HR Validation → Team Lead Review → PM Decision
                                    ↓ (Low Risk)
                                  Approved
                                    ↓ (Medium/High Risk)
                                  PM Review
```

### 2. ESP Workflow
```
L7 Creates Package → L6 Simulates & Reviews → PM Makes Final Decision
```

### 3. Incident Resolution
```
Report → Assign → Track → Resolve
```

## 🛡️ RBAC Implementation

### Role-Based Decorators

```python
from app.core.rbac import require_role, require_admin, Roles

# Require specific roles
@require_role([Roles.ADMIN, Roles.PROJECT_MANAGER])
async def create_project(...):
    pass

# Admin only
@require_admin()
async def delete_user(...):
    pass
```

### Permission Checks

```python
from app.core.rbac import is_admin, has_permission

if is_admin(current_user):
    # Admin can do anything
    pass

if has_permission(current_user, "projects.create"):
    # User has specific permission
    pass
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py
```

## 🚀 Deployment

### Free Deployment Options

1. **Render.com** (Recommended)
   - 750 hours/month free
   - Auto-deploy from GitHub
   - PostgreSQL included

2. **Railway.app**
   - $5 free credit/month
   - No sleep
   - Great DX

3. **Fly.io**
   - 3 free VMs
   - PostgreSQL included
   - Global deployment

### Deployment Configuration

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_KEY`
- `SECRET_KEY`
- `OPENROUTER_API_KEY`

## 📚 API Documentation

Full interactive documentation available at:
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`

## 🔍 Key Algorithms

### 1. Skill Coverage Calculation
```python
def calculate_skill_coverage(project_id: str, db: Client) -> Dict:
    """
    Returns: {skill: {coverage_percent, team_members, gap}}
    - 0 members = 0% coverage
    - 1 member = 50% coverage (single point of failure)
    - 2+ members = 100% coverage
    """
```

### 2. Leave Conflict Detection
```python
def analyze_leave_conflict(leave_id: str, db: Client) -> Dict:
    """
    Checks:
    - Critical task assignments
    - Blocking incidents
    - Leave balance
    - Valid alternates
    Returns: APPROVED_BY_L7, PENDING_L6, or REJECTED
    """
```

### 3. ESP Simulation
```python
def generate_esp_simulation(project_id: str, team_id: str, db: Client) -> Dict:
    """
    Analyzes:
    - Skill gaps
    - Capacity utilization
    - Internal candidates
    - Cost estimation
    Returns: Recommendations and alternatives
    """
```

## 📝 Development Guidelines

### Adding New Features

1. **Create Pydantic Models** (`app/models/`)
2. **Implement Business Logic** (`app/services/` if needed)
3. **Create API Routes** (`app/api/v1/`)
4. **Add RBAC Checks**
5. **Update Documentation**
6. **Write Tests**

### Code Style

- Follow PEP 8
- Use type hints
- Document complex functions
- Keep functions focused and small
- Use meaningful variable names

## 🤝 Contributing

This is a proprietary project. Contact the admin for access.

## 📄 License

Proprietary - All rights reserved © 2026 QKREW

---

**Version:** 4.0.0  
**Last Updated:** 2026-01-18  
**Status:** Production Ready  
**Modules:** 18 API Modules  
**Database Tables:** 19  
**Total Columns:** 250+  
**Permissions:** 72+  
**Hierarchy Levels:** 13
