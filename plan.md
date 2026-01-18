# 🚀 QKREW - Complete Backend Architecture Plan
## FastAPI + Supabase Implementation

---

## 📋 **Document Overview**

**Project:** QKREW - Employee Management & Project Tracking System  
**Backend Stack:** FastAPI (Python 3.11+) + Supabase (PostgreSQL 14+)  
**Frontend Stack:** React + Vite + Redux Toolkit + Tailwind CSS  
**Database:** PostgreSQL 14+ (Supabase)  
**Authentication:** JWT + Supabase Auth  
**API Style:** RESTful with OpenAPI/Swagger Documentation  

**Total Features:** 21 modules  
**Total Database Tables:** 19 tables (as per database.md)  
**Total API Endpoints:** ~120+ endpoints  

---

## 🎯 **Project Understanding**

### **What is QKREW?**

QKREW is a comprehensive **Employee Resource Management (ERM)** and **Project Tracking Platform** designed for hierarchical organizations (L1-L13 levels). It provides:

1. **Project Management** - Full lifecycle project tracking with RACI matrix
2. **Task Management** - Task assignment, tracking, and progress monitoring
3. **Team Management** - Permanent technical teams with skill matrices
4. **Employee Management** - Complete employee profiles with workload tracking
5. **Leave Management** - AI-powered conflict detection and approval workflow
6. **Incident Tracking** - Critical incident management with SLA tracking
7. **ESP (Extra Staffing Projection)** - AI-driven staffing recommendations
8. **Analytics Dashboard** - Real-time KPIs and productivity metrics
9. **Business Trips** - Trip management and approval workflow
10. **Events Management** - Company events and participation tracking
11. **Software Requests** - Tool/software purchase requests
12. **Notice Period Tracking** - Employee exit management
13. **HR Chatbot** - AI-powered HR assistant
14. **Leave Conflicts** - AI conflict detection and resolution
15. **Notifications** - Frontend-only session-based notifications

### **Organizational Hierarchy**

```
L1-L2:  CTO, VP Engineering (Admin)
L3-L5:  Director, Engineering Manager, Senior Manager (Project Manager)
L6:     Principal Architect (Technical Architect)
L7:     Team Lead (Technical Lead)
L8-L11: Senior Engineers, Engineers, Junior Engineers (Employee)
L12-L13: Trainees, Interns (Learning Employees)
```

### **Key Business Logic**

1. **RBAC (Role-Based Access Control)** - Strict hierarchy-based permissions
2. **Leave Approval Workflow** - HR → L7 → L6 (with AI conflict detection)
3. **ESP Workflow** - L7 creates → L6 reviews + simulates → PM approves
4. **Task Assignment** - L6/L7 assign to L8-L11, L8 assigns learning tasks to L12-L13
5. **Project Lifecycle** - Planning → Active → On Hold → Completed/Cancelled
6. **Incident Management** - Critical/High incidents block leave approvals

---

## 📁 **Backend Folder Structure (Comprehensive & Modular)**

```
backend/
├── app/
│   ├── __init__.py                          # Package initializer
│   ├── main.py                              # FastAPI app entry point, CORS, middleware
│   ├── config.py                            # Environment variables, settings (Pydantic Settings)
│   ├── database.py                          # Supabase client initialization
│   │
│   ├── core/                                # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py                      # JWT token creation/validation, password hashing (bcrypt)
│   │   ├── dependencies.py                  # FastAPI dependencies (get_current_user, get_db)
│   │   ├── rbac.py                          # Role-based access control decorators & utilities
│   │   ├── exceptions.py                    # Custom HTTP exceptions
│   │   └── middleware.py                    # Custom middleware (logging, error handling)
│   │
│   ├── models/                              # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── common.py                        # Common schemas (Pagination, Filters, Response)
│   │   │
│   │   ├── auth.py                          # LoginRequest, TokenResponse, RefreshTokenRequest
│   │   │
│   │   ├── user.py                          # UserBase, UserCreate, UserUpdate, UserResponse
│   │   │
│   │   ├── project/                         # Project schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # ProjectBase, ProjectCreate, ProjectUpdate
│   │   │   ├── response.py                  # ProjectResponse, ProjectListResponse
│   │   │   ├── team.py                      # ProjectTeamMember, AddTeamMemberRequest
│   │   │   ├── analytics.py                 # ProjectAnalytics, ProjectHealth
│   │   │   ├── raci.py                      # RACIMatrix, RACIEntry
│   │   │   └── notes.py                     # ProjectNote, NoteCreate
│   │   │
│   │   ├── task/                            # Task schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # TaskBase, TaskCreate, TaskUpdate
│   │   │   ├── response.py                  # TaskResponse, TaskListResponse
│   │   │   ├── activity.py                  # TaskActivity, ActivityLog
│   │   │   ├── dependencies.py              # TaskDependency, DependencyCreate
│   │   │   └── history.py                   # TaskHistory, HistoryEntry
│   │   │
│   │   ├── team/                            # Team schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # TeamBase, TeamCreate, TeamUpdate
│   │   │   ├── response.py                  # TeamResponse, TeamListResponse
│   │   │   ├── members.py                   # TeamMember, MemberRole
│   │   │   ├── capacity.py                  # TeamCapacity, CapacityAnalysis
│   │   │   ├── skills.py                    # TeamSkills, SkillMatrix
│   │   │   └── projects.py                  # TeamProjects, ProjectAssignment
│   │   │
│   │   ├── employee/                        # Employee schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # EmployeeBase, EmployeeCreate, EmployeeUpdate
│   │   │   ├── response.py                  # EmployeeResponse, EmployeeListResponse
│   │   │   ├── profile.py                   # EmployeeProfile, ProfileUpdate
│   │   │   ├── workload.py                  # EmployeeWorkload, WorkloadAnalysis
│   │   │   ├── skills.py                    # EmployeeSkills, SkillLevel
│   │   │   ├── projects.py                  # EmployeeProjects, ProjectAllocation
│   │   │   ├── tasks.py                     # EmployeeTasks, TaskSummary
│   │   │   ├── leaves.py                    # EmployeeLeaves, LeaveSummary
│   │   │   └── incidents.py                 # EmployeeIncidents, IncidentSummary
│   │   │
│   │   ├── leave/                           # Leave schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # LeaveBase, LeaveCreate, LeaveUpdate
│   │   │   ├── response.py                  # LeaveResponse, LeaveListResponse
│   │   │   ├── workflow.py                  # LeaveWorkflow, WorkflowStatus
│   │   │   ├── conflict.py                  # LeaveConflict, ConflictAnalysis, AlternateMatch
│   │   │   ├── approval.py                  # HRReviewRequest, L7DecisionRequest, L6DecisionRequest
│   │   │   └── calendar.py                  # LeaveCalendar, CalendarEntry
│   │   │
│   │   ├── leave_conflict/                  # Leave Conflict schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # ConflictBase, ConflictResponse
│   │   │   ├── analysis.py                  # AIConflictAnalysis, ConflictSeverity
│   │   │   ├── resolution.py                # ConflictResolution, ResolutionStrategy
│   │   │   └── history.py                   # ConflictHistory, HistoryEntry
│   │   │
│   │   ├── incident/                        # Incident schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # IncidentBase, IncidentCreate, IncidentUpdate
│   │   │   ├── response.py                  # IncidentResponse, IncidentListResponse
│   │   │   ├── activity.py                  # IncidentActivity, ActivityLog
│   │   │   ├── resolution.py                # IncidentResolution, ResolutionNotes
│   │   │   └── timeline.py                  # IncidentTimeline, TimelineEvent
│   │   │
│   │   ├── esp/                             # ESP schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── package.py                   # ESPPackageCreate, ESPPackageResponse
│   │   │   ├── l7_recommendations.py        # L7RecommendationCreate, L7RecommendationResponse
│   │   │   ├── simulation.py                # ESPSimulationRequest, ESPSimulationResponse
│   │   │   ├── l6_review.py                 # L6ReviewCreate, L6ReviewResponse
│   │   │   ├── pm_decision.py               # PMDecisionCreate, PMDecisionResponse
│   │   │   ├── skill_gap.py                 # SkillGapAnalysis, GapCalculation
│   │   │   ├── capacity.py                  # CapacityAnalysis, UtilizationMetrics
│   │   │   ├── alternatives.py              # AlternativeOptions, AlternativeStrategy
│   │   │   └── workflow.py                  # ESPWorkflow, WorkflowHistory
│   │   │
│   │   ├── event/                           # Event schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # EventBase, EventCreate, EventUpdate
│   │   │   ├── response.py                  # EventResponse, EventListResponse
│   │   │   ├── participants.py              # EventParticipant, ParticipantRegistration
│   │   │   └── calendar.py                  # EventCalendar, CalendarView
│   │   │
│   │   ├── business_trip/                   # Business Trip schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── base.py                      # BusinessTripBase, BusinessTripCreate, BusinessTripUpdate
│   │   │   ├── response.py                  # BusinessTripResponse, BusinessTripListResponse
│   │   │   ├── itinerary.py                 # TripItinerary, ItineraryItem
│   │   │   ├── expenses.py                  # TripExpense, ExpenseItem
│   │   │   └── documents.py                 # TripDocument, DocumentUpload
│   │   │
│   │   ├── software_request.py              # SoftwareRequestCreate, SoftwareRequestResponse
│   │   │
│   │   ├── notice_period.py                 # NoticePeriodCreate, NoticePeriodResponse
│   │   │
│   │   ├── dashboard/                       # Dashboard schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── kpis.py                      # KPIResponse, KPIMetrics
│   │   │   ├── health.py                    # HealthIndicators, HealthMetrics
│   │   │   ├── productivity.py              # ProductivityTrends, ProductivityMetrics
│   │   │   ├── alerts.py                    # AlertsResponse, Alert
│   │   │   └── response.py                  # DashboardResponse (aggregates all)
│   │   │
│   │   ├── analytics/                       # Analytics schemas (modular)
│   │   │   ├── __init__.py
│   │   │   ├── project.py                   # ProjectAnalytics, ProjectMetrics
│   │   │   ├── team.py                      # TeamAnalytics, TeamMetrics
│   │   │   ├── employee.py                  # EmployeeAnalytics, EmployeeMetrics
│   │   │   └── task.py                      # TaskAnalytics, TaskMetrics
│   │   │
│   │   ├── chatbot.py                       # ChatMessage, ChatResponse, ChatHistory
│   │   │
│   │   └── profile.py                       # ProfileUpdate, PasswordChange, AvatarUpload
│   │
│   ├── api/                                 # API routes
│   │   ├── __init__.py
│   │   └── v1/                              # API version 1
│   │       ├── __init__.py                  # Router aggregation
│   │       │
│   │       ├── auth.py                      # Authentication endpoints
│   │       │                                # POST /login, /logout, /refresh
│   │       │                                # GET /me
│   │       │
│   │       ├── users.py                     # User management endpoints
│   │       │                                # GET /users, /users/{id}
│   │       │                                # POST /users
│   │       │                                # PUT /users/{id}
│   │       │                                # DELETE /users/{id}
│   │       │                                # GET /users/{id}/workload, /users/{id}/projects, /users/{id}/tasks
│   │       │
│   │       ├── projects/                    # Project endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /projects, POST /projects, GET /projects/{id}, PUT /projects/{id}, DELETE /projects/{id}
│   │       │   ├── team.py                  # GET /projects/{id}/team, POST /projects/{id}/team, DELETE /projects/{id}/team/{user_id}
│   │       │   ├── tasks.py                 # GET /projects/{id}/tasks
│   │       │   ├── analytics.py             # GET /projects/{id}/analytics
│   │       │   ├── health.py                # GET /projects/{id}/health
│   │       │   ├── raci.py                  # GET /projects/{id}/raci, PUT /projects/{id}/raci
│   │       │   ├── notes.py                 # GET /projects/{id}/notes, POST /projects/{id}/notes
│   │       │   └── incidents.py             # GET /projects/{id}/incidents
│   │       │
│   │       ├── tasks/                       # Task endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /tasks, POST /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}
│   │       │   ├── status.py                # PATCH /tasks/{id}/status
│   │       │   ├── progress.py              # PATCH /tasks/{id}/progress
│   │       │   ├── activity.py              # GET /tasks/{id}/activity
│   │       │   ├── dependencies.py          # GET /tasks/{id}/dependencies, POST /tasks/{id}/dependencies
│   │       │   └── history.py               # GET /tasks/{id}/history
│   │       │
│   │       ├── teams/                       # Team endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /teams, POST /teams, GET /teams/{id}, PUT /teams/{id}, DELETE /teams/{id}
│   │       │   ├── members.py               # GET /teams/{id}/members, POST /teams/{id}/members, DELETE /teams/{id}/members/{user_id}
│   │       │   ├── capacity.py              # GET /teams/{id}/capacity
│   │       │   ├── skills.py                # GET /teams/{id}/skills
│   │       │   └── projects.py              # GET /teams/{id}/projects
│   │       │
│   │       ├── employees/                   # Employee endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /employees, POST /employees, GET /employees/{id}, PUT /employees/{id}, DELETE /employees/{id}
│   │       │   ├── profile.py               # GET /employees/{id}/profile, PUT /employees/{id}/profile
│   │       │   ├── workload.py              # GET /employees/{id}/workload
│   │       │   ├── skills.py                # GET /employees/{id}/skills, PUT /employees/{id}/skills
│   │       │   ├── projects.py              # GET /employees/{id}/projects
│   │       │   ├── tasks.py                 # GET /employees/{id}/tasks
│   │       │   ├── leaves.py                # GET /employees/{id}/leaves
│   │       │   └── incidents.py             # GET /employees/{id}/incidents
│   │       │
│   │       ├── leaves/                      # Leave endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /leaves, POST /leaves, GET /leaves/{id}, PUT /leaves/{id}, DELETE /leaves/{id}
│   │       │   ├── workflow.py              # POST /leaves/{id}/hr-review, POST /leaves/{id}/l7-decision, POST /leaves/{id}/l6-decision
│   │       │   ├── conflicts.py             # GET /leaves/{id}/conflicts
│   │       │   ├── alternate.py             # POST /leaves/{id}/assign-alternate
│   │       │   └── calendar.py              # GET /leaves/calendar
│   │       │
│   │       ├── leave_conflicts/             # Leave Conflict endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /leave-conflicts, GET /leave-conflicts/{id}
│   │       │   ├── analysis.py              # GET /leave-conflicts/{id}/analysis
│   │       │   ├── resolution.py            # POST /leave-conflicts/{id}/resolve
│   │       │   └── history.py               # GET /leave-conflicts/{id}/history
│   │       │
│   │       ├── incidents/                   # Incident endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /incidents, POST /incidents, GET /incidents/{id}, PUT /incidents/{id}, DELETE /incidents/{id}
│   │       │   ├── status.py                # PATCH /incidents/{id}/status
│   │       │   ├── assign.py                # PATCH /incidents/{id}/assign
│   │       │   ├── resolve.py               # POST /incidents/{id}/resolve
│   │       │   ├── activity.py              # GET /incidents/{id}/activity
│   │       │   ├── resolution.py            # GET /incidents/{id}/resolution
│   │       │   └── timeline.py              # GET /incidents/{id}/timeline
│   │       │
│   │       ├── esp/                         # ESP endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── packages.py              # GET /esp/packages, POST /esp/packages, GET /esp/packages/{id}, PUT /esp/packages/{id}
│   │       │   ├── simulate.py              # POST /esp/packages/{id}/simulate
│   │       │   ├── l7_recommendations.py    # GET /esp/packages/{id}/l7-recommendations, POST /esp/packages/{id}/l7-recommendations
│   │       │   ├── l6_review.py             # POST /esp/packages/{id}/l6-review, GET /esp/packages/{id}/l6-review
│   │       │   ├── pm_decision.py           # POST /esp/packages/{id}/pm-decision, GET /esp/packages/{id}/pm-decision
│   │       │   ├── simulation_results.py    # GET /esp/packages/{id}/simulation
│   │       │   ├── skill_gap.py             # GET /esp/packages/{id}/skill-gaps
│   │       │   ├── capacity.py              # GET /esp/packages/{id}/capacity-analysis
│   │       │   ├── alternatives.py          # GET /esp/packages/{id}/alternatives
│   │       │   └── workflow.py              # GET /esp/packages/{id}/workflow-history
│   │       │
│   │       ├── events/                      # Event endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /events, POST /events, GET /events/{id}, PUT /events/{id}, DELETE /events/{id}
│   │       │   ├── participants.py          # GET /events/{id}/participants, POST /events/{id}/register, DELETE /events/{id}/unregister
│   │       │   └── calendar.py              # GET /events/calendar
│   │       │
│   │       ├── business_trips/              # Business Trip endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /business-trips, POST /business-trips, GET /business-trips/{id}, PUT /business-trips/{id}, DELETE /business-trips/{id}
│   │       │   ├── approval.py              # POST /business-trips/{id}/approve, POST /business-trips/{id}/reject
│   │       │   ├── itinerary.py             # GET /business-trips/{id}/itinerary, PUT /business-trips/{id}/itinerary
│   │       │   ├── expenses.py              # GET /business-trips/{id}/expenses, POST /business-trips/{id}/expenses
│   │       │   └── documents.py             # GET /business-trips/{id}/documents, POST /business-trips/{id}/documents
│   │       │
│   │       ├── software_requests.py         # Software Request endpoints
│   │       │                                # GET /software-requests, POST /software-requests, GET /software-requests/{id}
│   │       │                                # PUT /software-requests/{id}, DELETE /software-requests/{id}
│   │       │                                # POST /software-requests/{id}/approve, POST /software-requests/{id}/reject
│   │       │
│   │       ├── notice_period.py             # Notice Period endpoints
│   │       │                                # GET /notice-period, POST /notice-period, GET /notice-period/{id}
│   │       │                                # PUT /notice-period/{id}, DELETE /notice-period/{id}
│   │       │
│   │       ├── dashboard/                   # Dashboard endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── main.py                  # GET /dashboard (aggregated data)
│   │       │   ├── kpis.py                  # GET /dashboard/kpis
│   │       │   ├── health.py                # GET /dashboard/health
│   │       │   ├── productivity.py          # GET /dashboard/productivity
│   │       │   └── alerts.py                # GET /dashboard/alerts
│   │       │
│   │       ├── analytics/                   # Analytics endpoints (modular)
│   │       │   ├── __init__.py
│   │       │   ├── projects.py              # GET /analytics/projects
│   │       │   ├── teams.py                 # GET /analytics/teams
│   │       │   ├── employees.py             # GET /analytics/employees
│   │       │   └── tasks.py                 # GET /analytics/tasks
│   │       │
│   │       ├── chatbot.py                   # Chatbot endpoints
│   │       │                                # POST /chatbot/message
│   │       │                                # GET /chatbot/history
│   │       │
│   │       └── profile.py                   # Profile endpoints
│   │                                        # GET /profile, PUT /profile
│   │                                        # PUT /profile/password, PUT /profile/avatar
│   │
│   ├── services/                            # Business logic layer
│   │   ├── __init__.py
│   │   │
│   │   ├── auth/                            # Auth services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── login.py                     # Login logic, token generation
│   │   │   ├── token.py                     # Token validation, refresh
│   │   │   └── password.py                  # Password hashing, validation
│   │   │
│   │   ├── user_service.py                  # User CRUD, workload calculation
│   │   │
│   │   ├── project/                         # Project services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Project CRUD operations
│   │   │   ├── team.py                      # Team management
│   │   │   ├── analytics.py                 # Analytics calculation
│   │   │   ├── health.py                    # Health indicators calculation
│   │   │   ├── raci.py                      # RACI matrix management
│   │   │   └── notes.py                     # Notes management
│   │   │
│   │   ├── task/                            # Task services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Task CRUD operations
│   │   │   ├── status.py                    # Status updates, progress tracking
│   │   │   ├── activity.py                  # Activity logging
│   │   │   ├── dependencies.py              # Dependency management
│   │   │   └── history.py                   # History tracking
│   │   │
│   │   ├── team/                            # Team services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Team CRUD operations
│   │   │   ├── members.py                   # Member management
│   │   │   ├── capacity.py                  # Capacity calculation
│   │   │   ├── skills.py                    # Skill matrix management
│   │   │   └── projects.py                  # Project assignments
│   │   │
│   │   ├── employee/                        # Employee services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Employee CRUD operations
│   │   │   ├── profile.py                   # Profile management
│   │   │   ├── workload.py                  # Workload calculation
│   │   │   ├── skills.py                    # Skills management
│   │   │   ├── projects.py                  # Project assignments
│   │   │   ├── tasks.py                     # Task assignments
│   │   │   ├── leaves.py                    # Leave history
│   │   │   └── incidents.py                 # Incident history
│   │   │
│   │   ├── leave/                           # Leave services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Leave CRUD operations
│   │   │   ├── workflow.py                  # Approval workflow (HR, L7, L6)
│   │   │   ├── conflict_detection.py        # AI conflict detection engine
│   │   │   ├── alternate_finder.py          # Find valid alternates (skill matching)
│   │   │   └── calendar.py                  # Calendar management
│   │   │
│   │   ├── leave_conflict/                  # Leave Conflict services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── analysis.py                  # AI conflict analysis
│   │   │   ├── resolution.py                # Conflict resolution strategies
│   │   │   └── history.py                   # Conflict history tracking
│   │   │
│   │   ├── incident/                        # Incident services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Incident CRUD operations
│   │   │   ├── status.py                    # Status management
│   │   │   ├── assignment.py                # Assignment logic
│   │   │   ├── resolution.py                # Resolution tracking
│   │   │   ├── activity.py                  # Activity logging
│   │   │   └── timeline.py                  # Timeline generation
│   │   │
│   │   ├── esp/                             # ESP services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── package.py                   # Package CRUD operations
│   │   │   ├── simulation_engine.py         # AI simulation engine (core logic)
│   │   │   ├── skill_gap.py                 # Skill gap calculation
│   │   │   ├── capacity.py                  # Capacity analysis
│   │   │   ├── recommendations.py           # System recommendations generation
│   │   │   ├── alternatives.py              # Alternative options generation
│   │   │   ├── confidence.py                # Confidence score calculation
│   │   │   ├── l7_recommendations.py        # L7 recommendation management
│   │   │   ├── l6_review.py                 # L6 review management
│   │   │   ├── pm_decision.py               # PM decision management
│   │   │   └── workflow.py                  # Workflow history tracking
│   │   │
│   │   ├── event/                           # Event services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Event CRUD operations
│   │   │   ├── participants.py              # Participant management
│   │   │   └── calendar.py                  # Calendar view generation
│   │   │
│   │   ├── business_trip/                   # Business Trip services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── crud.py                      # Trip CRUD operations
│   │   │   ├── approval.py                  # Approval workflow
│   │   │   ├── itinerary.py                 # Itinerary management
│   │   │   ├── expenses.py                  # Expense tracking
│   │   │   └── documents.py                 # Document management
│   │   │
│   │   ├── software_request_service.py      # Software request CRUD, approval workflow
│   │   │
│   │   ├── notice_period_service.py         # Notice period CRUD, handover tracking
│   │   │
│   │   ├── dashboard/                       # Dashboard services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── kpis.py                      # KPI calculation
│   │   │   ├── health.py                    # Health indicators calculation
│   │   │   ├── productivity.py              # Productivity trends calculation
│   │   │   ├── alerts.py                    # Alerts generation
│   │   │   └── aggregator.py                # Data aggregation
│   │   │
│   │   ├── analytics/                       # Analytics services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── project.py                   # Project analytics calculation
│   │   │   ├── team.py                      # Team analytics calculation
│   │   │   ├── employee.py                  # Employee analytics calculation
│   │   │   └── task.py                      # Task analytics calculation
│   │   │
│   │   ├── chatbot/                         # Chatbot services (modular)
│   │   │   ├── __init__.py
│   │   │   ├── message_handler.py           # Message processing
│   │   │   ├── context_manager.py           # Context management
│   │   │   ├── ai_engine.py                 # OpenAI/LLM integration
│   │   │   └── history.py                   # Chat history management
│   │   │
│   │   └── profile_service.py               # Profile management, password change, avatar upload
│   │
│   ├── utils/                               # Utility functions
│   │   ├── __init__.py
│   │   ├── email.py                         # Email notifications (SMTP)
│   │   ├── validators.py                    # Custom validators (email, phone, date ranges)
│   │   ├── helpers.py                       # Helper functions (date calculations, formatting)
│   │   ├── constants.py                     # Constants (roles, statuses, enums)
│   │   ├── formatters.py                    # Data formatters (currency, dates, numbers)
│   │   └── logger.py                        # Logging configuration
│   │
│   └── tests/                               # Unit & integration tests
│       ├── __init__.py
│       ├── conftest.py                      # Pytest fixtures
│       │
│       ├── unit/                            # Unit tests
│       │   ├── __init__.py
│       │   ├── test_auth.py
│       │   ├── test_rbac.py
│       │   ├── test_leave_conflict.py
│       │   └── test_esp_simulation.py
│       │
│       ├── integration/                     # Integration tests
│       │   ├── __init__.py
│       │   ├── test_auth_flow.py
│       │   ├── test_leave_workflow.py
│       │   ├── test_esp_workflow.py
│       │   ├── test_project_crud.py
│       │   └── test_dashboard.py
│       │
│       └── e2e/                             # End-to-end tests
│           ├── __init__.py
│           └── test_complete_workflows.py
│
├── alembic/                                 # Database migrations (optional, for non-Supabase)
│   ├── versions/                            # Migration scripts
│   ├── env.py                               # Alembic environment
│   └── alembic.ini                          # Alembic configuration
│
├── scripts/                                 # Utility scripts
│   ├── seed_data.py                         # Seed initial data (users, teams, projects)
│   ├── create_tables.sql                    # Supabase table creation SQL (from database.md)
│   ├── backup_db.py                         # Database backup script
│   └── generate_test_data.py                # Generate test data for development
│
├── docs/                                    # Additional documentation
│   ├── API.md                               # API documentation
│   ├── DEPLOYMENT.md                        # Deployment guide
│   ├── TESTING.md                           # Testing guide
│   └── WORKFLOWS.md                         # Business logic workflows
│
├── .env.example                             # Environment variables template
├── .env                                     # Environment variables (gitignored)
├── .gitignore                               # Git ignore file
├── requirements.txt                         # Python dependencies
├── pyproject.toml                           # Poetry config (optional)
├── pytest.ini                               # Pytest configuration
├── README.md                                # Backend documentation
└── Dockerfile                               # Docker configuration (optional)
```

### **📊 File Count Summary**

| Category | Files | Description |
|----------|-------|-------------|
| **Models (Schemas)** | 85+ | Pydantic request/response schemas (modular by feature) |
| **API Routes** | 60+ | FastAPI endpoint handlers (modular by feature) |
| **Services** | 70+ | Business logic layer (modular by feature) |
| **Core** | 5 | Security, RBAC, dependencies, exceptions, middleware |
| **Utils** | 7 | Helpers, validators, formatters, constants, email, logger |
| **Tests** | 15+ | Unit, integration, and E2E tests |
| **Scripts** | 4 | Seed data, table creation, backup, test data |
| **Config** | 8 | Main, database, env, requirements, pytest, docker |
| **Total** | **250+** | **Complete backend files** |

### **🎯 Key Modular Features**

**Features with Sub-Sidebars (Modular Structure):**

1. **Projects** → `models/project/`, `api/v1/projects/`, `services/project/`
   - Sub-modules: base, team, analytics, health, raci, notes, incidents

2. **Tasks** → `models/task/`, `api/v1/tasks/`, `services/task/`
   - Sub-modules: base, activity, dependencies, history

3. **Teams** → `models/team/`, `api/v1/teams/`, `services/team/`
   - Sub-modules: base, members, capacity, skills, projects

4. **Employees** → `models/employee/`, `api/v1/employees/`, `services/employee/`
   - Sub-modules: base, profile, workload, skills, projects, tasks, leaves, incidents

5. **Leaves** → `models/leave/`, `api/v1/leaves/`, `services/leave/`
   - Sub-modules: base, workflow, conflict, approval, calendar

6. **Leave Conflicts** → `models/leave_conflict/`, `api/v1/leave_conflicts/`, `services/leave_conflict/`
   - Sub-modules: base, analysis, resolution, history

7. **Incidents** → `models/incident/`, `api/v1/incidents/`, `services/incident/`
   - Sub-modules: base, activity, resolution, timeline

8. **ESP** → `models/esp/`, `api/v1/esp/`, `services/esp/`
   - Sub-modules: package, l7_recommendations, simulation, l6_review, pm_decision, skill_gap, capacity, alternatives, workflow

9. **Business Trips** → `models/business_trip/`, `api/v1/business_trips/`, `services/business_trip/`
   - Sub-modules: base, itinerary, expenses, documents

10. **Events** → `models/event/`, `api/v1/events/`, `services/event/`
    - Sub-modules: base, participants, calendar

11. **Dashboard** → `models/dashboard/`, `api/v1/dashboard/`, `services/dashboard/`
    - Sub-modules: kpis, health, productivity, alerts

12. **Analytics** → `models/analytics/`, `api/v1/analytics/`, `services/analytics/`
    - Sub-modules: project, team, employee, task

13. **Chatbot** → `services/chatbot/`
    - Sub-modules: message_handler, context_manager, ai_engine, history

---

## 🗄️ **Database Tables Summary**

Based on `database.md`, we have **19 tables**:

### **Core Tables (1-6)**
1. **users** (23 columns) - User accounts with workload tracking
2. **tech_teams** (7 columns) - Permanent technical teams
3. **tech_team_members** (4 columns) - Team membership junction
4. **projects** (23 columns) - Project management
5. **project_members** (6 columns) - Project assignments junction
6. **tasks** (18 columns) - Task management

### **Operations Tables (7-10)**
7. **leaves** (15 columns) - Leave requests with AI conflict detection
8. **incidents** (12 columns) - Incident tracking
9. **project_invitations** (12 columns) - Project invitations
10. **software_requests** (10 columns) - Software purchase requests

### **ESP Tables (11-16)**
11. **esp_packages** (14 columns) - ESP package management
12. **esp_l7_recommendations** (14 columns) - L7 staffing recommendations
13. **esp_simulations** (11 columns) - ESP simulation results
14. **esp_l6_reviews** (11 columns) - L6 reviews
15. **esp_pm_decisions** (11 columns) - PM final decisions

### **Additional Tables (17-19)**
16. **notice_periods** (10 columns) - Notice period tracking
17. **events** (12 columns) - Company events
18. **event_participants** (5 columns) - Event participation junction

**Note:** Notifications are **frontend-only** (React state arrays), no database table needed.

---

## 🔐 **Authentication & Authorization**

### **Authentication Flow**

```
1. User submits email + password → POST /api/v1/auth/login
2. Backend validates credentials (bcrypt password check)
3. Backend generates JWT token (access + refresh)
4. Frontend stores token in localStorage
5. Frontend sends token in Authorization header: "Bearer <token>"
6. Backend validates token on protected routes
```

### **JWT Token Structure**

```json
{
  "sub": "user_id (UUID)",
  "email": "user@example.com",
  "role": "admin | project_manager | technical_lead | hr | employee",
  "hierarchy_level": "L1-L13",
  "exp": 1234567890
}
```

### **RBAC Implementation**

**Permission Matrix:**

| Feature | Admin (L1-L2) | PM (L3-L5) | L6 | L7 | HR | Employee (L8-L13) |
|---------|---------------|------------|----|----|----|--------------------|
| **Users** | CRUD | R | R | R | R | R (own) |
| **Projects** | CRUD | CRUD (own) | R | CRUD (assigned) | R | R (assigned) |
| **Tasks** | CRUD | CRUD (own projects) | CRUD | CRUD | R | RU (assigned) |
| **Teams** | CRUD | R | R | CRUD (own team) | R | R |
| **Employees** | CRUD | R | R | R | CRUD | R (own) |
| **Leaves** | CRUD | R | R | Approve/Reject | Approve/Reject | CR (own) |
| **Incidents** | CRUD | CRUD | CRUD | CRUD | R | CR (assigned) |
| **ESP** | CRUD | Approve/Reject | Review/Simulate | Create | R | R |
| **Events** | CRUD | R | R | R | CRUD | R |
| **Software Requests** | Approve/Reject | R | R | Approve/Reject | R | CR |
| **Notice Period** | CRUD | R | R | R | CRUD | R |
| **Analytics** | R | R | R | R | R | R (limited) |
| **Dashboard** | R | R | R | R | R | R |

**RBAC Decorator Example:**

```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(allowed_roles: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user, **kwargs):
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.post("/projects")
@require_role(["admin", "project_manager", "technical_lead"])
async def create_project(project: ProjectCreate, current_user: User = Depends(get_current_user)):
    ...
```

---

## 📡 **API Endpoints Specification**

### **1. Authentication (`/api/v1/auth`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/login` | User login | Public |
| POST | `/logout` | User logout | Authenticated |
| POST | `/refresh` | Refresh access token | Authenticated |
| GET | `/me` | Get current user | Authenticated |

**Request/Response Examples:**

```python
# POST /api/v1/auth/login
Request:
{
  "email": "admin@qkrew.com",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@qkrew.com",
    "name": "Admin User",
    "role": "admin",
    "hierarchy_level": "L1",
    "avatar_url": "https://..."
  }
}
```

---

### **2. Users (`/api/v1/users`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/users` | List all users (with filters) | Admin, PM, L6, L7, HR |
| GET | `/users/{id}` | Get user by ID | All (own + authorized) |
| POST | `/users` | Create new user | Admin, HR |
| PUT | `/users/{id}` | Update user | Admin, HR, Self |
| DELETE | `/users/{id}` | Delete user | Admin |
| GET | `/users/{id}/workload` | Get user workload | All |
| GET | `/users/{id}/projects` | Get user projects | All |
| GET | `/users/{id}/tasks` | Get user tasks | All |

**Query Parameters for GET /users:**
- `role` (admin, project_manager, technical_lead, hr, employee)
- `hierarchy_level` (L1-L13)
- `department` (Engineering, QA, Design, etc.)
- `status` (active, on_leave, exited)
- `assignment_status` (unassigned, assigned, critical_owner)
- `page`, `limit` (pagination)

---

### **3. Projects (`/api/v1/projects`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/projects` | List all projects (with filters) | All |
| GET | `/projects/{id}` | Get project by ID | All |
| POST | `/projects` | Create new project | Admin, PM, L7 |
| PUT | `/projects/{id}` | Update project | Admin, PM, L7 |
| DELETE | `/projects/{id}` | Delete project | Admin, PM |
| GET | `/projects/{id}/team` | Get project team members | All |
| POST | `/projects/{id}/team` | Add team member | PM, L7 |
| DELETE | `/projects/{id}/team/{user_id}` | Remove team member | PM, L7 |
| GET | `/projects/{id}/tasks` | Get project tasks | All |
| GET | `/projects/{id}/analytics` | Get project analytics | All |
| GET | `/projects/{id}/health` | Get project health indicators | All |

**Project Schema:**

```python
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    project_manager_id: UUID
    principal_architect_id: Optional[UUID]
    team_lead_id: Optional[UUID]
    required_skills: List[str]
    tech_stack: List[str]
    project_type: str  # delivery, internal, research, maintenance, client_support
    priority: str  # low, medium, high, critical
    start_date: date
    deadline: Optional[date]
    budget: Optional[dict]  # {allocated, spent, remaining}

class ProjectResponse(ProjectCreate):
    id: UUID
    status: str  # planning, active, on_hold, completed, cancelled
    progress: float
    total_hours: int
    done_hours: int
    team_size: int
    active_members: int
    active_tasks: int
    blocked_tasks: int
    completed_tasks: int
    risk_level: str  # low, medium, high
    health_indicators: dict  # {schedule, capacity, incidents, quality}
    created_at: datetime
    updated_at: datetime
```

---

### **4. Tasks (`/api/v1/tasks`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/tasks` | List all tasks (with filters) | All |
| GET | `/tasks/{id}` | Get task by ID | All |
| POST | `/tasks` | Create new task | L6, L7, L8 (learning tasks) |
| PUT | `/tasks/{id}` | Update task | Assignee, L6, L7 |
| DELETE | `/tasks/{id}` | Delete task | L6, L7 |
| PATCH | `/tasks/{id}/status` | Update task status | Assignee |
| PATCH | `/tasks/{id}/progress` | Update task progress | Assignee |

**Task Schema:**

```python
class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    project_id: UUID
    assignee_id: Optional[UUID]
    priority: str  # low, medium, high, critical
    estimated_hours: Optional[int]
    due_date: Optional[date]
    is_learning_task: bool = False
    mentor_id: Optional[UUID]  # Required if is_learning_task=True

class TaskResponse(TaskCreate):
    id: UUID
    status: str  # not_started, in_progress, blocked, completed
    progress: int  # 0-100
    actual_hours: int
    blocked_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
```

---

### **5. Teams (`/api/v1/teams`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/teams` | List all teams | All |
| GET | `/teams/{id}` | Get team by ID | All |
| POST | `/teams` | Create new team | Admin |
| PUT | `/teams/{id}` | Update team | Admin, L7 (own team) |
| DELETE | `/teams/{id}` | Delete team | Admin |
| GET | `/teams/{id}/members` | Get team members | All |
| POST | `/teams/{id}/members` | Add team member | Admin, L7 |
| DELETE | `/teams/{id}/members/{user_id}` | Remove team member | Admin, L7 |
| GET | `/teams/{id}/capacity` | Get team capacity | All |
| GET | `/teams/{id}/skills` | Get team skills matrix | All |

---

### **6. Employees (`/api/v1/employees`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/employees` | List all employees | All |
| GET | `/employees/{id}` | Get employee by ID | All |
| POST | `/employees` | Create new employee | Admin, HR |
| PUT | `/employees/{id}` | Update employee | Admin, HR, Self |
| DELETE | `/employees/{id}` | Delete employee | Admin |
| GET | `/employees/{id}/profile` | Get employee profile | All |
| GET | `/employees/{id}/workload` | Get employee workload | All |
| GET | `/employees/{id}/skills` | Get employee skills | All |
| GET | `/employees/{id}/projects` | Get employee projects | All |
| GET | `/employees/{id}/tasks` | Get employee tasks | All |
| GET | `/employees/{id}/leaves` | Get employee leaves | All |
| GET | `/employees/{id}/incidents` | Get employee incidents | All |

---

### **7. Leaves (`/api/v1/leaves`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/leaves` | List all leaves | All |
| GET | `/leaves/{id}` | Get leave by ID | All |
| POST | `/leaves` | Create leave request | All (own) |
| PUT | `/leaves/{id}` | Update leave | Employee (own), HR |
| DELETE | `/leaves/{id}` | Delete leave | Employee (own), Admin |
| POST | `/leaves/{id}/hr-review` | HR review | HR |
| POST | `/leaves/{id}/l7-decision` | L7 decision | L7 |
| POST | `/leaves/{id}/l6-decision` | L6 decision (escalated) | L6 |
| GET | `/leaves/{id}/conflicts` | Get leave conflicts | HR, L7, L6 |
| POST | `/leaves/{id}/assign-alternate` | Assign alternate | L7, L6 |

**Leave Workflow:**

```
1. Employee creates leave → status: pending_hr_review
2. HR reviews quota → status: forwarded_to_team_lead
3. L7 runs AI conflict detection:
   - Check critical tasks
   - Check pending tasks
   - Check incidents (HARD BLOCK if high/critical)
   - Find valid alternate (skill match ≥80%, availability ≥30%, incident-free)
4. L7 Decision:
   - If incident_hard_block OR no valid_alternate → status: escalated_to_l6
   - If resource_hold OR pending_tasks → status: escalated_to_l6
   - Else → status: approved (with alternate assigned)
5. L6 Decision (if escalated):
   - status: approved OR rejected
```

**Leave Schema:**

```python
class LeaveCreate(BaseModel):
    leave_type: str  # casual, sick, earned, maternity, paternity, unpaid
    start_date: date
    end_date: date
    reason: Optional[str]

class LeaveResponse(LeaveCreate):
    id: UUID
    employee_id: UUID
    days: int
    status: str  # pending_hr_review, forwarded_to_team_lead, pending_l7_decision, approved, rejected, escalated_to_l6
    conflict_severity: Optional[str]  # none, high, critical
    alternate_assigned_id: Optional[UUID]
    hr_reviewed_by: Optional[UUID]
    hr_reviewed_at: Optional[datetime]
    decided_by_id: Optional[UUID]
    decision_notes: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]
```

---

### **8. Incidents (`/api/v1/incidents`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/incidents` | List all incidents | All |
| GET | `/incidents/{id}` | Get incident by ID | All |
| POST | `/incidents` | Create incident | All |
| PUT | `/incidents/{id}` | Update incident | Assignee, L6, L7 |
| DELETE | `/incidents/{id}` | Delete incident | Admin |
| PATCH | `/incidents/{id}/status` | Update status | Assignee |
| PATCH | `/incidents/{id}/assign` | Assign incident | L7, PM |
| POST | `/incidents/{id}/resolve` | Resolve incident | Assignee |

**Incident Schema:**

```python
class IncidentCreate(BaseModel):
    title: str
    description: Optional[str]
    project_id: UUID
    severity: str  # low, medium, high, critical
    assigned_to_id: Optional[UUID]

class IncidentResponse(IncidentCreate):
    id: UUID
    status: str  # open, in_progress, resolved, closed
    reported_by_id: UUID
    assigned_by_id: Optional[UUID]
    resolution_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
```

---

### **9. ESP (Extra Staffing Projection) (`/api/v1/esp`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/esp/packages` | List all ESP packages | All |
| GET | `/esp/packages/{id}` | Get ESP package by ID | All |
| POST | `/esp/packages` | Create ESP package (L7) | L7 |
| PUT | `/esp/packages/{id}` | Update ESP package | L7 (own) |
| POST | `/esp/packages/{id}/simulate` | Run ESP simulation (L6) | L6 |
| POST | `/esp/packages/{id}/l6-review` | L6 review | L6 |
| POST | `/esp/packages/{id}/pm-decision` | PM decision | PM (L3-L5) |
| GET | `/esp/packages/{id}/recommendations` | Get recommendations | All |
| GET | `/esp/packages/{id}/simulation` | Get simulation results | All |

**ESP Workflow:**

```
1. L7 creates ESP package → status: draft
2. L7 submits → status: submitted_to_l6
3. L6 runs simulation:
   - Calculate skill gaps
   - Generate system recommendations
   - Analyze capacity
   - Provide alternatives
4. L6 reviews:
   - Approve/modify L7 recommendations
   - Add ESP simulation recommendations
   - status: l6_approved
5. L6 forwards to PM → status: pm_reviewing
6. PM makes final decision:
   - Approve positions
   - Reject positions
   - Defer positions
   - Select alternatives
   - status: pm_approved / pm_rejected / pm_modified
```

**ESP Simulation Logic:**

```python
def run_esp_simulation(project_id: UUID, team_id: UUID):
    # 1. Get project required skills
    # 2. Get team members with skills
    # 3. Calculate skill gaps:
    #    gap = hours_needed - available_capacity
    # 4. Calculate positions needed:
    #    positions = gap / 28 (productive hours/week)
    # 5. Suggest level based on skill complexity
    # 6. Calculate risk level:
    #    - critical: utilization > 95% OR skill_gaps >= 5
    #    - high: utilization > 85% OR skill_gaps >= 3
    #    - medium: utilization > 70% OR skill_gaps >= 1
    # 7. Generate alternatives:
    #    - Internal reallocation (find underutilized employees)
    #    - Contract workers
    #    - Defer non-critical features
    # 8. Calculate confidence score (0-1)
    return simulation_result
```

---

### **10. Events (`/api/v1/events`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/events` | List all events | All |
| GET | `/events/{id}` | Get event by ID | All |
| POST | `/events` | Create event | Admin, HR |
| PUT | `/events/{id}` | Update event | Admin, HR |
| DELETE | `/events/{id}` | Delete event | Admin |
| POST | `/events/{id}/register` | Register for event | All |
| DELETE | `/events/{id}/unregister` | Unregister from event | All |
| GET | `/events/{id}/participants` | Get event participants | All |

---

### **11. Business Trips (`/api/v1/business-trips`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/business-trips` | List all trips | All |
| GET | `/business-trips/{id}` | Get trip by ID | All |
| POST | `/business-trips` | Create trip | All |
| PUT | `/business-trips/{id}` | Update trip | Employee (own), Admin |
| DELETE | `/business-trips/{id}` | Delete trip | Employee (own), Admin |
| POST | `/business-trips/{id}/approve` | Approve trip | L7, PM |
| POST | `/business-trips/{id}/reject` | Reject trip | L7, PM |

---

### **12. Software Requests (`/api/v1/software-requests`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/software-requests` | List all requests | All |
| GET | `/software-requests/{id}` | Get request by ID | All |
| POST | `/software-requests` | Create request | All |
| PUT | `/software-requests/{id}` | Update request | Employee (own), Admin |
| DELETE | `/software-requests/{id}` | Delete request | Employee (own), Admin |
| POST | `/software-requests/{id}/approve` | Approve request | Admin, L7 |
| POST | `/software-requests/{id}/reject` | Reject request | Admin, L7 |

---

### **13. Notice Period (`/api/v1/notice-period`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/notice-period` | List all notice periods | Admin, HR |
| GET | `/notice-period/{id}` | Get notice period by ID | Admin, HR |
| POST | `/notice-period` | Create notice period | Admin, HR |
| PUT | `/notice-period/{id}` | Update notice period | Admin, HR |
| DELETE | `/notice-period/{id}` | Delete notice period | Admin |

---

### **14. Dashboard (`/api/v1/dashboard`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/dashboard` | Get dashboard data | All |
| GET | `/dashboard/kpis` | Get KPIs | All |
| GET | `/dashboard/health` | Get organization health | All |
| GET | `/dashboard/productivity` | Get productivity trends | All |
| GET | `/dashboard/alerts` | Get alerts & warnings | All |

**Dashboard Response:**

```python
{
  "kpis": {
    "activeProjects": {"value": 28, "trend": 12, "trendDirection": "up"},
    "completedTasks": {"value": 156, "trend": 8, "trendDirection": "up"},
    "totalTeamMembers": {"value": 82, "trend": 3, "trendDirection": "up"},
    "pendingLeaves": {"value": 5, "trend": 2, "trendDirection": "down"},
    "openIncidents": {"value": 8, "critical": 2, "high": 3}
  },
  "health": {
    "projectHealth": 87,
    "taskCompletionRate": 92,
    "capacityUtilization": 78,
    "incidentSLA": 94
  },
  "productivity": [...],  # 7-day trend
  "teamUtilization": [...],
  "tasksAtRisk": [...],
  "upcomingDeadlines": [...],
  "recentActivity": [...],
  "alerts": [...]
}
```

---

### **15. Analytics (`/api/v1/analytics`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/analytics/projects` | Project analytics | All |
| GET | `/analytics/teams` | Team analytics | All |
| GET | `/analytics/employees` | Employee analytics | All |
| GET | `/analytics/tasks` | Task analytics | All |

---

### **16. Chatbot (`/api/v1/chatbot`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/chatbot/message` | Send message to chatbot | All |
| GET | `/chatbot/history` | Get chat history | All |

**Chatbot Logic:**

```python
# Use OpenAI API or local LLM
# Context: User profile, projects, tasks, leaves, etc.
# Capabilities:
# - Answer HR policy questions
# - Check leave balance
# - Show project status
# - Find available team members
# - Suggest skill matches
```

---

### **17. Profile (`/api/v1/profile`)**

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/profile` | Get current user profile | Authenticated |
| PUT | `/profile` | Update current user profile | Authenticated |
| PUT | `/profile/password` | Change password | Authenticated |
| PUT | `/profile/avatar` | Update avatar | Authenticated |

---

## 🛠️ **Technology Stack Details**

### **Backend Dependencies (requirements.txt)**

```txt
# FastAPI Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Supabase
supabase==2.3.0
postgrest-py==0.13.0

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Database
asyncpg==0.29.0
sqlalchemy==2.0.25

# Utilities
python-dotenv==1.0.0
email-validator==2.1.0

# AI/ML (for ESP simulation & chatbot)
openai==1.10.0
numpy==1.26.3
pandas==2.1.4

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0

# CORS
fastapi-cors==0.0.6
```

### **Environment Variables (.env)**

```env
# Application
APP_NAME=QKREW
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# OpenAI (for chatbot)
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-password
```

---

## 📊 **Supabase Table Creation SQL**

**File: `scripts/create_tables.sql`**

This file will contain the complete SQL schema from `database.md`. You will paste this into Supabase SQL Editor.

**Key Tables to Create:**

```sql
-- 1. users table
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  name VARCHAR(255) NOT NULL,
  role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'project_manager', 'technical_lead', 'hr', 'employee')),
  hierarchy_level VARCHAR(5) NOT NULL CHECK (hierarchy_level IN ('L1','L2','L3','L4','L5','L6','L7','L8','L9','L10','L11','L12','L13')),
  skills TEXT[],
  experience_years INTEGER,
  weekly_capacity INTEGER DEFAULT 40,
  department VARCHAR(100),
  manager_id UUID REFERENCES users(id),
  tech_team_id UUID REFERENCES tech_teams(id),
  status VARCHAR(50) DEFAULT 'active',
  avatar_url TEXT,
  assignment_status VARCHAR(50) DEFAULT 'unassigned',
  current_workload_percent INTEGER DEFAULT 0,
  active_project_count INTEGER DEFAULT 0,
  active_task_count INTEGER DEFAULT 0,
  has_blocking_incident BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by_id UUID REFERENCES users(id),
  updated_by_id UUID REFERENCES users(id)
);

-- 2. tech_teams table
CREATE TABLE tech_teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  department VARCHAR(100),
  team_lead_id UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ... (Continue with all 19 tables from database.md)
```

**Note:** The complete SQL will be extracted from `database.md` and provided separately.

---

## 🧪 **Testing Strategy**

### **Unit Tests**

```python
# tests/test_auth.py
def test_login_success():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@qkrew.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@qkrew.com",
        "password": "wrong"
    })
    assert response.status_code == 401
```

### **Integration Tests**

```python
# tests/test_leaves.py
def test_leave_approval_workflow():
    # 1. Employee creates leave
    # 2. HR reviews
    # 3. L7 runs conflict detection
    # 4. L7 approves with alternate
    # 5. Verify status changes
    pass
```

---

## 🚀 **Deployment Plan**

### **Local Development**

```bash
# 1. Clone repository
git clone <repo-url>
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# 5. Run migrations (create tables in Supabase)
# Copy scripts/create_tables.sql to Supabase SQL Editor and execute

# 6. Seed data
python scripts/seed_data.py

# 7. Run development server
uvicorn app.main:app --reload --port 8000

# 8. Access Swagger docs
# http://localhost:8000/docs
```

### **Production Deployment**

**Options:**
1. **Railway** - Easy deployment with PostgreSQL
2. **Render** - Free tier available
3. **AWS EC2 + RDS** - Full control
4. **Google Cloud Run** - Serverless
5. **Heroku** - Simple deployment

---

## 📝 **Next Steps**

### **Phase 1: Setup (Week 1)**
- [ ] Create backend folder structure
- [ ] Set up FastAPI project
- [ ] Configure Supabase connection
- [ ] Implement authentication (JWT)
- [ ] Create base models and schemas

### **Phase 2: Core Features (Week 2-3)**
- [ ] Implement Users API
- [ ] Implement Projects API
- [ ] Implement Tasks API
- [ ] Implement Teams API
- [ ] Implement Employees API

### **Phase 3: Operations (Week 4)**
- [ ] Implement Leaves API (with AI conflict detection)
- [ ] Implement Incidents API
- [ ] Implement Software Requests API
- [ ] Implement Notice Period API

### **Phase 4: Advanced Features (Week 5)**
- [ ] Implement ESP API (with simulation engine)
- [ ] Implement Events API
- [ ] Implement Business Trips API
- [ ] Implement Dashboard API
- [ ] Implement Analytics API

### **Phase 5: AI Features (Week 6)**
- [ ] Implement Chatbot API
- [ ] Implement Leave Conflict Detection
- [ ] Implement ESP Simulation Engine

### **Phase 6: Testing & Deployment (Week 7)**
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Deploy to production
- [ ] Frontend integration testing

---

## 📚 **Additional Documentation Needed**

1. **API Documentation** - Detailed Swagger/OpenAPI specs
2. **Database Schema** - ER diagrams
3. **Business Logic** - Detailed workflow diagrams
4. **Deployment Guide** - Step-by-step deployment
5. **Testing Guide** - How to run tests
6. **Contributing Guide** - For team collaboration

---

## 🎯 **Success Metrics**

- ✅ All 19 database tables created in Supabase
- ✅ 120+ API endpoints implemented
- ✅ JWT authentication working
- ✅ RBAC implemented for all endpoints
- ✅ Leave approval workflow with AI conflict detection
- ✅ ESP simulation engine working
- ✅ Dashboard KPIs calculating correctly
- ✅ Frontend integration complete
- ✅ All tests passing
- ✅ Production deployment successful

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Author:** AI Assistant  
**Status:** Planning Phase - Ready for Implementation
# 🎨 QKREW - Architecture Diagrams & Visual Guide

---

## 📊 **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React + Vite + Redux Toolkit + Tailwind CSS             │  │
│  │  ┌────────────┬────────────┬────────────┬─────────────┐  │  │
│  │  │ Dashboard  │ Projects   │ Tasks      │ Employees   │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ Teams      │ Leaves     │ Incidents  │ ESP         │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ Events     │ Analytics  │ Chatbot    │ Profile     │  │  │
│  │  └────────────┴────────────┴────────────┴─────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/REST (Axios)
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastAPI + Python 3.11+                                  │  │
│  │  ┌────────────┬────────────┬────────────┬─────────────┐  │  │
│  │  │ Auth API   │ Users API  │ Projects   │ Tasks API   │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ Teams API  │ Leaves API │ Incidents  │ ESP API     │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ Events API │ Dashboard  │ Analytics  │ Chatbot     │  │  │
│  │  └────────────┴────────────┴────────────┴─────────────┘  │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Business Logic Layer (Services)                    │  │  │
│  │  │ - AI Conflict Detection (Leaves)                   │  │  │
│  │  │ - ESP Simulation Engine                            │  │  │
│  │  │ - Dashboard KPI Calculation                        │  │  │
│  │  │ - RBAC & Security                                  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↕ Supabase Client
┌─────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Supabase (PostgreSQL 14+)                               │  │
│  │  ┌────────────┬────────────┬────────────┬─────────────┐  │  │
│  │  │ users (23) │ projects   │ tasks (18) │ teams (7)   │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ leaves(15) │ incidents  │ esp_pkgs   │ events (12) │  │  │
│  │  ├────────────┼────────────┼────────────┼─────────────┤  │  │
│  │  │ esp_l7_rec │ esp_l6_rev │ esp_pm_dec │ esp_sim     │  │  │
│  │  └────────────┴────────────┴────────────┴─────────────┘  │  │
│  │  Total: 19 Tables, 218 Columns                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 **Authentication Flow**

```
┌──────────┐                                    ┌──────────┐
│ Frontend │                                    │ Backend  │
│ (React)  │                                    │ (FastAPI)│
└────┬─────┘                                    └────┬─────┘
     │                                                │
     │  1. POST /api/v1/auth/login                   │
     │    {email, password}                          │
     ├──────────────────────────────────────────────►│
     │                                                │
     │                                          2. Validate
     │                                          credentials
     │                                          (bcrypt)
     │                                                │
     │  3. Response: {access_token, user}            │
     │◄──────────────────────────────────────────────┤
     │                                                │
     │  4. Store token in localStorage                │
     │                                                │
     │  5. All subsequent requests:                  │
     │     Authorization: Bearer <token>             │
     ├──────────────────────────────────────────────►│
     │                                                │
     │                                          6. Validate
     │                                          JWT token
     │                                                │
     │  7. Response: Protected data                  │
     │◄──────────────────────────────────────────────┤
     │                                                │
```

---

## 📋 **Leave Approval Workflow**

```
┌─────────────┐
│  Employee   │
│ Creates     │
│ Leave       │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ Status: pending_hr_review   │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────┐
│     HR      │
│  Reviews    │
│   Quota     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────┐
│ Status: forwarded_to_team_lead   │
└──────┬───────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│                    L7 Team Lead                     │
│           Runs AI Conflict Detection                │
│  ┌───────────────────────────────────────────────┐  │
│  │ 1. Check Critical Tasks (priority=critical)   │  │
│  │ 2. Check Pending Tasks (open/blocked)         │  │
│  │ 3. Check Incidents (HARD BLOCK if high/crit)  │  │
│  │ 4. Find Valid Alternate:                      │  │
│  │    - Skill Match ≥ 80%                        │  │
│  │    - Availability ≥ 30%                       │  │
│  │    - Incident-Free                            │  │
│  └───────────────────────────────────────────────┘  │
└──────┬──────────────────────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Incident    │   │ No Valid    │   │ All Clear   │
│ Hard Block  │   │ Alternate   │   │             │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └────────┬────────┘                 │
                │                          │
                ▼                          ▼
       ┌─────────────────┐        ┌─────────────────┐
       │ Status:         │        │ Status:         │
       │ escalated_to_l6 │        │ approved        │
       └────────┬────────┘        │ (with alternate)│
                │                 └─────────────────┘
                ▼
       ┌─────────────────┐
       │  L6 Principal   │
       │   Architect     │
       │   Decision      │
       └────────┬────────┘
                │
                ├─────────┬─────────┐
                ▼         ▼         ▼
          ┌─────────┐ ┌─────────┐ ┌─────────┐
          │Approved │ │Rejected │ │Deferred │
          └─────────┘ └─────────┘ └─────────┘
```

---

## 🎯 **ESP (Extra Staffing Projection) Workflow**

```
┌─────────────────────────────────────────────────────────────────┐
│                      L7 Team Lead                               │
│  Creates ESP Package with Recommendations                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ - Skill: React, Count: 2, Level: L9-L10                   │  │
│  │ - Skill: Python, Count: 1, Level: L8                      │  │
│  │ - Reason: Sprint backlog overflow                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Status: draft   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ L7 Submits Package  │
                  └────────┬────────────┘
                           │
                           ▼
                  ┌──────────────────────────┐
                  │ Status: submitted_to_l6  │
                  └────────┬─────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  L6 Principal Architect                         │
│              Runs ESP Simulation Engine                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ 1. Calculate Skill Gaps:                                  │  │
│  │    gap = hours_needed - available_capacity                │  │
│  │                                                            │  │
│  │ 2. Calculate Positions Needed:                            │  │
│  │    positions = gap / 28 (productive hours/week)           │  │
│  │                                                            │  │
│  │ 3. Calculate Risk Level:                                  │  │
│  │    - critical: utilization > 95% OR skill_gaps >= 5       │  │
│  │    - high: utilization > 85% OR skill_gaps >= 3           │  │
│  │    - medium: utilization > 70% OR skill_gaps >= 1         │  │
│  │                                                            │  │
│  │ 4. Generate Alternatives:                                 │  │
│  │    - Internal Reallocation (underutilized employees)      │  │
│  │    - Contract Workers (3-month contracts)                 │  │
│  │    - Defer Non-Critical Features (30% reduction)          │  │
│  │                                                            │  │
│  │ 5. Calculate Confidence Score (0-1)                       │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ Status: l6_reviewing│
                  └────────┬────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  L6 Reviews Package                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Approved L7 Recommendations:                              │  │
│  │ - React: 2 positions (L9-L10) ✓                           │  │
│  │                                                            │  │
│  │ Additional ESP Recommendations:                           │  │
│  │ - Python: 1 position (L8) [from simulation]              │  │
│  │ - QA: 1 position (L11) [from simulation]                 │  │
│  │                                                            │  │
│  │ Total Monthly Cost: $27,000                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────────┐
                  │ Status: l6_approved │
                  └────────┬────────────┘
                           │
                           ▼
                  ┌──────────────────────┐
                  │ L6 Forwards to PM    │
                  └────────┬─────────────┘
                           │
                           ▼
                  ┌──────────────────────┐
                  │ Status: pm_reviewing │
                  └────────┬─────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              PM (L3-L5) Makes Final Decision                    │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Approved Positions:                                       │  │
│  │ - React: 1 position (L10) [reduced from 2]               │  │
│  │ - Python: 1 position (L8)                                │  │
│  │                                                            │  │
│  │ Rejected Positions:                                       │  │
│  │ - QA: Will reallocate from Project B                     │  │
│  │                                                            │  │
│  │ Selected Alternatives:                                    │  │
│  │ - Internal Reallocation (saves $15,000/month)            │  │
│  │                                                            │  │
│  │ Final Budget Impact: $16,000/month                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ├─────────┬─────────┬─────────┐
                           ▼         ▼         ▼         ▼
                    ┌──────────┐ ┌──────────┐ ┌──────────┐
                    │pm_approved│ │pm_rejected│ │pm_modified│
                    └──────────┘ └──────────┘ └──────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Recruitment  │
                    └──────────────┘
```

---

## 🗂️ **Database Entity Relationship**

```
┌─────────────────┐
│     users       │
│ ─────────────── │
│ id (PK)         │◄───────────┐
│ email           │            │
│ password_hash   │            │
│ role            │            │
│ hierarchy_level │            │
│ manager_id (FK) ├────────────┘ (self-referencing)
│ tech_team_id(FK)├────────┐
└─────────────────┘        │
         ▲                 │
         │                 │
         │                 ▼
         │        ┌─────────────────┐
         │        │   tech_teams    │
         │        │ ─────────────── │
         │        │ id (PK)         │
         │        │ name            │
         │        │ team_lead_id(FK)├───┐
         │        └─────────────────┘   │
         │                 ▲            │
         │                 │            │
         │                 │            │
         │        ┌────────┴────────────┘
         │        │
         │        │
┌────────┴────────┴──────┐
│ tech_team_members      │
│ ────────────────────── │
│ id (PK)                │
│ team_id (FK)           │
│ user_id (FK)           │
└────────────────────────┘

┌─────────────────┐
│    projects     │
│ ─────────────── │
│ id (PK)         │
│ name            │
│ status          │
│ pm_id (FK)      ├──────► users
│ architect_id(FK)├──────► users
│ team_lead_id(FK)├──────► users
└────────┬────────┘
         │
         │
         ▼
┌─────────────────┐
│ project_members │
│ ─────────────── │
│ id (PK)         │
│ project_id (FK) │
│ user_id (FK)    │
│ allocation_%    │
└─────────────────┘

┌─────────────────┐
│     tasks       │
│ ─────────────── │
│ id (PK)         │
│ title           │
│ project_id (FK) ├──────► projects
│ assignee_id(FK) ├──────► users
│ priority        │
│ status          │
│ is_learning_task│
│ mentor_id (FK)  ├──────► users (L8)
└─────────────────┘

┌─────────────────┐
│     leaves      │
│ ─────────────── │
│ id (PK)         │
│ employee_id(FK) ├──────► users
│ leave_type      │
│ status          │
│ conflict_severity│
│ alternate_id(FK)├──────► users
│ decided_by_id(FK)├─────► users (L7/L6)
└─────────────────┘

┌─────────────────┐
│   incidents     │
│ ─────────────── │
│ id (PK)         │
│ project_id (FK) ├──────► projects
│ severity        │
│ status          │
│ assigned_to(FK) ├──────► users
│ reported_by(FK) ├──────► users
└─────────────────┘

┌─────────────────┐
│  esp_packages   │
│ ─────────────── │
│ id (PK)         │
│ project_id (FK) ├──────► projects
│ team_id (FK)    ├──────► tech_teams
│ created_by(FK)  ├──────► users (L7)
│ status          │
│ risk_level      │
└────────┬────────┘
         │
         ├──────► esp_l7_recommendations
         ├──────► esp_simulations
         ├──────► esp_l6_reviews
         └──────► esp_pm_decisions

┌─────────────────┐
│     events      │
│ ─────────────── │
│ id (PK)         │
│ name            │
│ event_type      │
│ organized_by(FK)├──────► users
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│event_participants│
│ ─────────────── │
│ id (PK)         │
│ event_id (FK)   │
│ user_id (FK)    │
└─────────────────┘
```

---

## 🔄 **Data Flow: Create Project**

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ProjectsList.jsx                                           │  │
│  │  - User clicks "Create Project"                            │  │
│  │  - Opens modal with form                                   │  │
│  │  - User fills: name, description, PM, tech stack, etc.     │  │
│  │  - User clicks "Submit"                                    │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ projectsSlice.js (Redux Toolkit)                           │  │
│  │  - dispatch(createProject(projectData))                    │  │
│  │  - createAsyncThunk triggers                               │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ projectsApi.js (Axios)                                     │  │
│  │  - axios.post('/api/v1/projects', projectData)             │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTP POST
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ api/v1/projects.py (FastAPI)                               │  │
│  │  @router.post("/projects")                                 │  │
│  │  - Validate request (Pydantic)                             │  │
│  │  - Check authentication (JWT)                              │  │
│  │  - Check authorization (RBAC)                              │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ services/project_service.py                                │  │
│  │  - create_project(project_data)                            │  │
│  │  - Validate business rules                                 │  │
│  │  - Calculate initial values                                │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ database.py (Supabase Client)                              │  │
│  │  - supabase.table('projects').insert(project_data)         │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         DATABASE                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Supabase (PostgreSQL)                                      │  │
│  │  - INSERT INTO projects (...)                              │  │
│  │  - Returns: new project with id                            │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         BACKEND                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ api/v1/projects.py                                         │  │
│  │  - Return ProjectResponse(new_project)                     │  │
│  └────────────────────────┬───────────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────────┘
                            │ HTTP 201 Created
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ projectsSlice.js                                           │  │
│  │  - createProject.fulfilled                                 │  │
│  │  - state.projects.push(action.payload)                     │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                      │
│                           ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ProjectsList.jsx                                           │  │
│  │  - useSelector(selectAllProjects)                          │  │
│  │  - Component re-renders with new project                   │  │
│  │  - Shows success toast notification                        │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎨 **Frontend Component Hierarchy**

```
App.jsx
├── Router
│   ├── LandingPage
│   ├── Login
│   └── AppLayout (Protected)
│       ├── Header
│       │   ├── SearchBar
│       │   ├── NotificationBell (frontend-only)
│       │   └── ProfileMenu
│       ├── MainSidebar
│       │   ├── Main Section
│       │   │   ├── Dashboard
│       │   │   ├── Projects
│       │   │   ├── Tasks
│       │   │   ├── Employees
│       │   │   └── Teams
│       │   ├── Operations Section
│       │   │   ├── Leaves
│       │   │   ├── Incidents
│       │   │   ├── Software Requests
│       │   │   └── Notice Period
│       │   └── Features Section
│       │       ├── Events
│       │       ├── Analytics
│       │       ├── ESP
│       │       ├── Business Trips
│       │       ├── Leave Conflicts
│       │       └── HR Chatbot
│       └── Content Area
│           ├── Dashboard
│           │   ├── KPICard (x5)
│           │   ├── HealthIndicator
│           │   ├── ProductivityChart
│           │   ├── TeamUtilizationChart
│           │   ├── TasksAtRisk
│           │   ├── UpcomingDeadlines
│           │   ├── RecentActivity
│           │   └── AlertsPanel
│           ├── ProjectsList
│           │   ├── ProjectCard (grid)
│           │   └── CreateProjectModal
│           ├── ProjectDetail
│           │   ├── SubSidebar
│           │   │   ├── Overview
│           │   │   ├── Tasks
│           │   │   ├── Team
│           │   │   ├── RACI
│           │   │   ├── Notes
│           │   │   ├── Analytics
│           │   │   └── Menu
│           │   └── Content (based on sub-route)
│           ├── TasksList
│           ├── TaskDetail
│           ├── EmployeesList
│           ├── EmployeeDetail
│           ├── TeamsList
│           ├── TeamDetail
│           ├── LeavesList
│           ├── IncidentsList
│           ├── ESPDashboard
│           └── ... (other features)
```

---

## 🔧 **Backend Service Layer Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Routes (api/v1/*.py)                                     │   │
│  │ - Request validation (Pydantic)                          │   │
│  │ - Authentication check (JWT)                             │   │
│  │ - Authorization check (RBAC)                             │   │
│  │ - Call service layer                                     │   │
│  │ - Return response                                        │   │
│  └──────────────────────┬───────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER (Business Logic)               │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Services (services/*.py)                                 │   │
│  │                                                          │   │
│  │ ┌────────────────────────────────────────────────────┐  │   │
│  │ │ project_service.py                                 │  │   │
│  │ │ - create_project()                                 │  │   │
│  │ │ - update_project()                                 │  │   │
│  │ │ - calculate_project_health()                       │  │   │
│  │ │ - get_project_analytics()                          │  │   │
│  │ └────────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │ ┌────────────────────────────────────────────────────┐  │   │
│  │ │ leave_service.py                                   │  │   │
│  │ │ - create_leave()                                   │  │   │
│  │ │ - hr_review_leave()                                │  │   │
│  │ │ - l7_decision_leave()                              │  │   │
│  │ │ - detect_leave_conflicts() ← AI Logic             │  │   │
│  │ │ - find_valid_alternate() ← Skill Matching         │  │   │
│  │ └────────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │ ┌────────────────────────────────────────────────────┐  │   │
│  │ │ esp_service.py                                     │  │   │
│  │ │ - run_esp_simulation() ← AI Engine                │  │   │
│  │ │ - calculate_skill_gaps()                           │  │   │
│  │ │ - calculate_capacity_analysis()                    │  │   │
│  │ │ - generate_system_recommendations()                │  │   │
│  │ │ - calculate_confidence_score()                     │  │   │
│  │ └────────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │ ┌────────────────────────────────────────────────────┐  │   │
│  │ │ dashboard_service.py                               │  │   │
│  │ │ - get_dashboard_data()                             │  │   │
│  │ │ - calculate_kpis()                                 │  │   │
│  │ │ - calculate_health_indicators()                    │  │   │
│  │ │ - get_productivity_trends()                        │  │   │
│  │ └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────┬───────────────────────────────────┘   │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (Supabase)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ database.py (Supabase Client)                            │   │
│  │ - supabase.table('projects').select()                    │   │
│  │ - supabase.table('projects').insert()                    │   │
│  │ - supabase.table('projects').update()                    │   │
│  │ - supabase.table('projects').delete()                    │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 **RBAC Permission Matrix**

```
┌──────────────┬───────┬────┬────┬────┬────┬──────────┐
│   Feature    │ Admin │ PM │ L6 │ L7 │ HR │ Employee │
├──────────────┼───────┼────┼────┼────┼────┼──────────┤
│ Users        │ CRUD  │ R  │ R  │ R  │ R  │ R (own)  │
│ Projects     │ CRUD  │ C* │ R  │ C* │ R  │ R (own)  │
│ Tasks        │ CRUD  │ C* │ C* │ C* │ R  │ RU (own) │
│ Teams        │ CRUD  │ R  │ R  │ C* │ R  │ R        │
│ Employees    │ CRUD  │ R  │ R  │ R  │ C* │ R (own)  │
│ Leaves       │ CRUD  │ R  │ A  │ A  │ A  │ CR (own) │
│ Incidents    │ CRUD  │ C* │ C* │ C* │ R  │ CR       │
│ ESP          │ CRUD  │ A  │ R  │ C  │ R  │ R        │
│ Events       │ CRUD  │ R  │ R  │ R  │ C* │ R        │
│ Soft Req     │ A     │ R  │ R  │ A  │ R  │ CR       │
│ Notice       │ CRUD  │ R  │ R  │ R  │ C* │ R        │
│ Analytics    │ R     │ R  │ R  │ R  │ R  │ R (lim)  │
│ Dashboard    │ R     │ R  │ R  │ R  │ R  │ R        │
└──────────────┴───────┴────┴────┴────┴────┴──────────┘

Legend:
C = Create, R = Read, U = Update, D = Delete
A = Approve/Reject
C* = Create (own projects/teams only)
R (own) = Read own data only
R (lim) = Read limited data
```

---

## 🎯 **Implementation Checklist**

### **Phase 1: Foundation ✅**
- [ ] Create Supabase project
- [ ] Set up FastAPI project structure
- [ ] Configure environment variables
- [ ] Implement JWT authentication
- [ ] Create base Pydantic models
- [ ] Set up RBAC decorators

### **Phase 2: Core Features 🔄**
- [ ] Users API (8 endpoints)
- [ ] Projects API (11 endpoints)
- [ ] Tasks API (7 endpoints)
- [ ] Teams API (9 endpoints)
- [ ] Employees API (12 endpoints)

### **Phase 3: Operations ⏳**
- [ ] Leaves API (10 endpoints) + AI conflict detection
- [ ] Incidents API (8 endpoints)
- [ ] Software Requests API (7 endpoints)
- [ ] Notice Period API (5 endpoints)

### **Phase 4: Advanced Features ⏳**
- [ ] ESP API (9 endpoints) + simulation engine
- [ ] Events API (7 endpoints)
- [ ] Business Trips API (7 endpoints)
- [ ] Dashboard API (5 endpoints)
- [ ] Analytics API (4 endpoints)

### **Phase 5: AI Features ⏳**
- [ ] Chatbot API (2 endpoints)
- [ ] Leave conflict detection algorithm
- [ ] ESP simulation algorithm

### **Phase 6: Testing & Deployment ⏳**
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] Frontend integration
- [ ] Production deployment

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Purpose:** Visual guide for understanding QKREW architecture

---

# 📊 **PROJECT PROGRESS TRACKER**

## 🎯 **Development Milestones**

### **Milestone 1: Database Setup** ⏳
**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 1-2 days

**Tasks:**
- [ ] Create `create_tables.sql` from database.md (19 tables)
- [ ] Run SQL in Supabase SQL Editor
- [ ] Verify all tables created successfully
- [ ] Create `seed_data.py` script
- [ ] Populate initial test data (users, teams, projects)
- [ ] Verify data integrity and relationships

**Deliverables:**
- ✅ All 19 tables in Supabase
- ✅ Test data populated
- ✅ Database schema verified

---

### **Milestone 2: Backend Foundation** ⏳
**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 2-3 days

**Tasks:**
- [ ] Create FastAPI project structure (250+ files)
- [ ] Set up `config.py` with environment variables
- [ ] Configure Supabase client connection
- [ ] Implement JWT authentication (`core/security.py`)
- [ ] Create RBAC system (`core/rbac.py`)
- [ ] Set up middleware (logging, error handling)
- [ ] Create base Pydantic models (`models/common.py`)
- [ ] Test authentication endpoints (login, logout, refresh)

**Deliverables:**
- ✅ FastAPI app running on `localhost:8000`
- ✅ Swagger docs accessible at `/docs`
- ✅ JWT authentication working
- ✅ RBAC decorators functional

---

### **Milestone 3: Core APIs (Users, Projects, Tasks)** ⏳
**Status:** Not Started  
**Priority:** High  
**Estimated Time:** 4-5 days

**Tasks:**
- [ ] **Users API** (8 endpoints)
  - [ ] GET /users (list with filters)
  - [ ] GET /users/{id}
  - [ ] POST /users (create)
  - [ ] PUT /users/{id} (update)
  - [ ] DELETE /users/{id}
  - [ ] GET /users/{id}/workload
  - [ ] GET /users/{id}/projects
  - [ ] GET /users/{id}/tasks
  
- [ ] **Projects API** (11 endpoints + sub-modules)
  - [ ] CRUD operations
  - [ ] Team management
  - [ ] Analytics
  - [ ] Health indicators
  - [ ] RACI matrix
  - [ ] Notes
  
- [ ] **Tasks API** (7 endpoints + sub-modules)
  - [ ] CRUD operations
  - [ ] Status updates
  - [ ] Progress tracking
  - [ ] Activity logs
  - [ ] Dependencies
  - [ ] History

**Deliverables:**
- ✅ All endpoints tested in Swagger/Postman
- ✅ RBAC working for all endpoints
- ✅ Data validation working
- ✅ Error handling implemented

---

### **Milestone 4: Team & Employee Management** ⏳
**Status:** Not Started  
**Priority:** High  
**Estimated Time:** 3-4 days

**Tasks:**
- [ ] **Teams API** (9 endpoints + sub-modules)
  - [ ] CRUD operations
  - [ ] Member management
  - [ ] Capacity calculation
  - [ ] Skills matrix
  - [ ] Project assignments
  
- [ ] **Employees API** (12 endpoints + sub-modules)
  - [ ] CRUD operations
  - [ ] Profile management
  - [ ] Workload calculation
  - [ ] Skills management
  - [ ] Projects, tasks, leaves, incidents views

**Deliverables:**
- ✅ Team management working
- ✅ Employee profiles complete
- ✅ Workload calculations accurate
- ✅ Skills matrix functional

---

### **Milestone 5: Leave Management with AI** ⏳
**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 5-6 days

**Tasks:**
- [ ] **Leaves API** (10 endpoints + workflow)
  - [ ] CRUD operations
  - [ ] HR review workflow
  - [ ] L7 decision workflow
  - [ ] L6 escalation workflow
  
- [ ] **AI Conflict Detection Engine**
  - [ ] Check critical tasks
  - [ ] Check pending tasks
  - [ ] Check incidents (hard block)
  - [ ] Find valid alternates (skill matching ≥80%)
  - [ ] Calculate conflict severity
  
- [ ] **Leave Conflicts API** (4 endpoints)
  - [ ] Conflict analysis
  - [ ] Resolution strategies
  - [ ] History tracking

**Deliverables:**
- ✅ Complete leave approval workflow
- ✅ AI conflict detection working
- ✅ Alternate assignment functional
- ✅ Leave calendar working

---

### **Milestone 6: Incident & Operations Management** ⏳
**Status:** Not Started  
**Priority:** High  
**Estimated Time:** 3-4 days

**Tasks:**
- [ ] **Incidents API** (8 endpoints + sub-modules)
  - [ ] CRUD operations
  - [ ] Status management
  - [ ] Assignment logic
  - [ ] Resolution tracking
  - [ ] Timeline generation
  
- [ ] **Software Requests API** (7 endpoints)
  - [ ] CRUD operations
  - [ ] Approval workflow
  
- [ ] **Notice Period API** (5 endpoints)
  - [ ] CRUD operations
  - [ ] Handover tracking

**Deliverables:**
- ✅ Incident management working
- ✅ SLA tracking functional
- ✅ Approval workflows complete

---

### **Milestone 7: ESP (Extra Staffing Projection)** ⏳
**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 6-7 days

**Tasks:**
- [ ] **ESP API** (10 endpoints + simulation)
  - [ ] Package CRUD
  - [ ] L7 recommendations
  - [ ] L6 review & simulation
  - [ ] PM decision
  
- [ ] **ESP Simulation Engine**
  - [ ] Calculate skill gaps
  - [ ] Calculate positions needed
  - [ ] Calculate risk level
  - [ ] Generate alternatives (internal reallocation, contract workers, defer features)
  - [ ] Calculate confidence score
  
- [ ] **ESP Workflow**
  - [ ] L7 creates package
  - [ ] L6 runs simulation
  - [ ] L6 reviews and approves
  - [ ] PM makes final decision

**Deliverables:**
- ✅ Complete ESP workflow
- ✅ Simulation engine accurate
- ✅ Alternative options generated
- ✅ Workflow history tracked

---

### **Milestone 8: Dashboard & Analytics** ⏳
**Status:** Not Started  
**Priority:** High  
**Estimated Time:** 4-5 days

**Tasks:**
- [ ] **Dashboard API** (5 endpoints)
  - [ ] KPIs calculation (active projects, completed tasks, team members, pending leaves, open incidents)
  - [ ] Health indicators (project health, task completion, capacity utilization, incident SLA)
  - [ ] Productivity trends (7-day)
  - [ ] Alerts generation
  
- [ ] **Analytics API** (4 endpoints)
  - [ ] Project analytics
  - [ ] Team analytics
  - [ ] Employee analytics
  - [ ] Task analytics

**Deliverables:**
- ✅ Real-time KPIs working
- ✅ Health indicators accurate
- ✅ Analytics charts data ready
- ✅ Alerts system functional

---

### **Milestone 9: Additional Features** ⏳
**Status:** Not Started  
**Priority:** Medium  
**Estimated Time:** 3-4 days

**Tasks:**
- [ ] **Events API** (7 endpoints)
  - [ ] CRUD operations
  - [ ] Participant registration
  - [ ] Calendar view
  
- [ ] **Business Trips API** (7 endpoints)
  - [ ] CRUD operations
  - [ ] Approval workflow
  - [ ] Itinerary, expenses, documents
  
- [ ] **Chatbot API** (2 endpoints)
  - [ ] Message handling
  - [ ] Context management
  - [ ] OpenAI integration
  
- [ ] **Profile API** (4 endpoints)
  - [ ] Profile management
  - [ ] Password change
  - [ ] Avatar upload

**Deliverables:**
- ✅ Events management working
- ✅ Business trips functional
- ✅ Chatbot responding correctly
- ✅ Profile updates working

---

### **Milestone 10: Testing, Integration & Deployment** ⏳
**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 5-7 days

**Tasks:**
- [ ] **Unit Tests**
  - [ ] Authentication tests
  - [ ] RBAC tests
  - [ ] Leave conflict detection tests
  - [ ] ESP simulation tests
  - [ ] >80% code coverage
  
- [ ] **Integration Tests**
  - [ ] Auth flow
  - [ ] Leave workflow
  - [ ] ESP workflow
  - [ ] Project CRUD
  - [ ] Dashboard data
  
- [ ] **Frontend Integration**
  - [ ] Connect all API endpoints
  - [ ] Test each feature end-to-end
  - [ ] Fix integration issues
  - [ ] Performance optimization
  
- [ ] **Deployment**
  - [ ] Set up production environment
  - [ ] Configure environment variables
  - [ ] Deploy to Railway/Render/AWS
  - [ ] Set up monitoring
  - [ ] Final testing

**Deliverables:**
- ✅ All tests passing
- ✅ Frontend fully integrated
- ✅ Backend deployed to production
- ✅ Monitoring set up
- ✅ Documentation complete

---

## 📈 **Overall Progress**

| Milestone | Status | Progress | Priority |
|-----------|--------|----------|----------|
| 1. Database Setup | ⏳ Not Started | 0% | 🔴 Critical |
| 2. Backend Foundation | ⏳ Not Started | 0% | 🔴 Critical |
| 3. Core APIs | ⏳ Not Started | 0% | 🟠 High |
| 4. Team & Employee | ⏳ Not Started | 0% | 🟠 High |
| 5. Leave Management + AI | ⏳ Not Started | 0% | 🔴 Critical |
| 6. Incident & Operations | ⏳ Not Started | 0% | 🟠 High |
| 7. ESP + Simulation | ⏳ Not Started | 0% | 🔴 Critical |
| 8. Dashboard & Analytics | ⏳ Not Started | 0% | 🟠 High |
| 9. Additional Features | ⏳ Not Started | 0% | 🟡 Medium |
| 10. Testing & Deployment | ⏳ Not Started | 0% | 🔴 Critical |

**Total Progress:** 0/10 Milestones Complete (0%)

---

## 🚀 **Next Immediate Steps**

1. **START HERE:** Create Supabase project at https://supabase.com
2. **Provide Supabase credentials** (URL, anon key, service key)
3. **I'll generate `create_tables.sql`** from database.md
4. **You run SQL in Supabase SQL Editor**
5. **Share results** (success/errors)
6. **I'll create `seed_data.py`** for test data
7. **Begin Milestone 2:** Backend Foundation

---

**Status Legend:**
- ⏳ Not Started
- 🔄 In Progress
- ✅ Completed
- ⚠️ Blocked
- ❌ Failed

**Priority Legend:**
- 🔴 Critical (Must have)
- 🟠 High (Should have)
- 🟡 Medium (Nice to have)
- 🟢 Low (Optional)

