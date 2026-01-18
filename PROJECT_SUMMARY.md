# 📊 QKREW V4 - Complete Project Analysis & Backend Plan Summary

---

## 🎯 **Executive Summary**

**QKREW V4** is a comprehensive **Employee Resource Management (ERM)** and **Project Tracking Platform** designed for hierarchical organizations (L1-L13 levels). This document provides a complete analysis of the frontend structure and a detailed backend implementation plan using **FastAPI + Supabase**.

---

## 📁 **Frontend Structure Analysis**

### **Technology Stack**
- **Framework:** React 18 + Vite
- **State Management:** Redux Toolkit (migrated from RTK Query)
- **Styling:** Tailwind CSS
- **Routing:** React Router v6
- **Animations:** Framer Motion
- **HTTP Client:** Axios

### **Total Features: 21 Modules**

#### **1. Main Features (5)**
1. **Dashboard** - KPIs, health indicators, productivity charts, alerts
2. **Projects** - Full lifecycle project management with RACI matrix
3. **Tasks** - Task assignment, tracking, progress monitoring
4. **Employees** - Employee directory, profiles, workload tracking
5. **Teams** - Team management, capacity planning, skill matrices

#### **2. Operations (4)**
6. **Leaves** - Leave requests with AI conflict detection
7. **Incidents** - Critical incident tracking with SLA management
8. **Software Requests** - Tool/software purchase requests
9. **Notice Period** - Employee exit management

#### **3. Features (6)**
10. **Events** - Company events and participation tracking
11. **Analytics** - Project, team, employee, task analytics
12. **ESP (Extra Staffing Projection)** - AI-driven staffing recommendations
13. **Business Trips** - Trip management and approval workflow
14. **Leave Conflicts** - AI conflict detection and resolution
15. **HR Chatbot** - AI-powered HR assistant

#### **4. Additional (6)**
16. **Profile** - User profile management
17. **Settings** - Application settings
18. **Notifications** - Frontend-only session-based notifications
19. **Theme** - Dark/light mode toggle
20. **Authentication** - JWT-based login/logout
21. **Landing Page** - Public landing page

---

## � **Frontend Folder & File Structure (Complete)**

### **Total Files: 204 files**

```
frontend/
├── src/
│   ├── main.jsx                           # App entry point
│   ├── App.jsx                            # Root component
│   ├── App.css                            # App styles
│   ├── index.css                          # Global styles (Tailwind)
│   ├── app.py                             # Python script (utility)
│   │
│   ├── app/                               # App configuration (3 files)
│   │   ├── store.js                       # Redux store configuration
│   │   ├── router.jsx                     # React Router setup
│   │   └── providers.jsx                  # Context providers
│   │
│   ├── assets/                            # Static assets (1 file)
│   │   └── react.svg                      # React logo
│   │
│   ├── components/                        # Shared components (8 files)
│   │   ├── layout/                        # Layout components (7 files)
│   │   │   ├── AppLayout.jsx              # Main app layout wrapper
│   │   │   ├── Header.jsx                 # Top header with search & profile
│   │   │   ├── MainSidebar.jsx            # Left sidebar navigation
│   │   │   ├── SubSidebar.jsx             # Right sidebar for detail pages
│   │   │   ├── ProfileMenu.jsx            # User profile dropdown
│   │   │   ├── SearchBar.jsx              # Global search component
│   │   │   └── ProtectedRoute.jsx         # Route protection wrapper
│   │   │
│   │   └── contexts/                      # Context providers (1 file)
│   │       └── SidebarContext.jsx         # Sidebar state context
│   │
│   ├── contexts/                          # Global contexts (1 file)
│   │   └── SidebarContext.jsx             # Sidebar context (duplicate)
│   │
│   ├── features/                          # Feature modules (170 files)
│   │   │
│   │   ├── analytics/                     # Analytics module (7 files)
│   │   │   ├── AnalyticsDashboard.jsx     # Main analytics page
│   │   │   ├── analyticsSlice.js          # Redux slice
│   │   │   ├── api/
│   │   │   │   └── analyticsApi.js        # API calls
│   │   │   └── components/                # Analytics components (4 files)
│   │   │       ├── EmployeeAnalytics.jsx  # Employee metrics
│   │   │       ├── ProjectAnalytics.jsx   # Project metrics
│   │   │       ├── TaskAnalytics.jsx      # Task metrics
│   │   │       └── TeamAnalytics.jsx      # Team metrics
│   │   │
│   │   ├── auth/                          # Authentication (3 files)
│   │   │   ├── Login.jsx                  # Login page
│   │   │   ├── authSlice.js               # Auth Redux slice
│   │   │   └── api/
│   │   │       └── authApi.js             # Auth API calls
│   │   │
│   │   ├── businessTrips/                 # Business trips (9 files)
│   │   │   ├── BusinessTripsList.jsx      # Trips list page
│   │   │   ├── BusinessTripDetail.jsx     # Trip detail page
│   │   │   ├── businessTripsSlice.js      # Redux slice
│   │   │   ├── api/
│   │   │   │   └── businessTripsApi.js    # API calls
│   │   │   └── components/                # Trip components (5 files)
│   │   │       ├── BusinessTripSubSidebar.jsx  # Detail sidebar
│   │   │       ├── TripOverview.jsx       # Overview tab
│   │   │       ├── TripItinerary.jsx      # Itinerary tab
│   │   │       ├── TripExpenses.jsx       # Expenses tab
│   │   │       └── TripDocuments.jsx      # Documents tab
│   │   │
│   │   ├── chatbot/                       # HR Chatbot (6 files)
│   │   │   ├── Chatbot.jsx                # Main chatbot page
│   │   │   ├── chatbotSlice.js            # Redux slice
│   │   │   ├── api/
│   │   │   │   └── chatbotApi.js          # API calls
│   │   │   └── components/                # Chatbot components (3 files)
│   │   │       ├── ChatWindow.jsx         # Chat window
│   │   │       ├── ChatMessage.jsx        # Message component
│   │   │       └── ChatInput.jsx          # Input component
│   │   │
│   │   ├── dashboard/                     # Dashboard (9 files)
│   │   │   ├── Dashboard.jsx              # Main dashboard page
│   │   │   ├── dashboardSlice.js          # Redux slice
│   │   │   ├── api/
│   │   │   │   └── dashboardApi.js        # API calls
│   │   │   └── components/                # Dashboard components (6 files)
│   │   │       ├── StatsGrid.jsx          # KPI cards grid
│   │   │       ├── KPICard.jsx            # Individual KPI card
│   │   │       ├── HealthIndicator.jsx    # Health metrics
│   │   │       ├── RecentActivity.jsx     # Activity feed
│   │   │       ├── QuickActions.jsx       # Quick action buttons
│   │   │       └── AlertsPanel.jsx        # Alerts & warnings
│   │   │
│   │   ├── employees/                     # Employees (14 files)
│   │   │   ├── EmployeesList.jsx          # Employees list page
│   │   │   ├── EmployeeDetail.jsx         # Employee detail page
│   │   │   ├── EmployeeCreate.jsx         # Create employee page
│   │   │   ├── employeesSlice.js          # Redux slice
│   │   │   ├── api/
│   │   │   │   └── employeesApi.js        # API calls
│   │   │   └── components/                # Employee components (9 files)
│   │   │       ├── EmployeeCard.jsx       # Employee card
│   │   │       ├── EmployeeDrawer.jsx     # Employee drawer
│   │   │       ├── EmployeeSubSidebar.jsx # Detail sidebar
│   │   │       ├── EmployeeProfile.jsx    # Profile tab
│   │   │       ├── EmployeeProjects.jsx   # Projects tab
│   │   │       ├── EmployeeTasks.jsx      # Tasks tab
│   │   │       ├── EmployeeLeaves.jsx     # Leaves tab
│   │   │       ├── EmployeeIncidents.jsx  # Incidents tab
│   │   │       └── EmployeeSkills.jsx     # Skills tab
│   │   │
│   │   ├── esp/                           # ESP (15 files)
│   │   │   ├── ESPDashboard.jsx           # ESP dashboard page
│   │   │   ├── ESPPackageDetail.jsx       # Package detail page
│   │   │   ├── espSlice.js                # Redux slice
│   │   │   ├── api/
│   │   │   │   └── espApi.js              # API calls
│   │   │   └── components/                # ESP components (11 files)
│   │   │       ├── ESPPackageCard.jsx     # Package card
│   │   │       ├── ESPSubSidebar.jsx      # Detail sidebar
│   │   │       ├── ESPOverview.jsx        # Overview tab
│   │   │       ├── L7Recommendations.jsx  # L7 recommendations
│   │   │       ├── L6Review.jsx           # L6 review tab
│   │   │       ├── PMDecision.jsx         # PM decision tab
│   │   │       ├── SimulationResults.jsx  # Simulation results
│   │   │       ├── SkillGapAnalysis.jsx   # Skill gap chart
│   │   │       ├── CapacityAnalysis.jsx   # Capacity chart
│   │   │       ├── AlternativeOptions.jsx # Alternatives
│   │   │       └── WorkflowHistory.jsx    # Workflow history
│   │   │
│   │   ├── events/                        # Events (7 files)
│   │   │   ├── EventsList.jsx             # Events list page
│   │   │   ├── EventDetail.jsx            # Event detail page
│   │   │   ├── eventsSlice.js             # Redux slice
│   │   │   ├── api/
│   │   │   │   └── eventsApi.js           # API calls
│   │   │   └── components/                # Event components (3 files)
│   │   │       ├── EventCard.jsx          # Event card
│   │   │       ├── EventCalendar.jsx      # Calendar view
│   │   │       └── EventParticipants.jsx  # Participants list
│   │   │
│   │   ├── incidents/                     # Incidents (14 files)
│   │   │   ├── IncidentsList.jsx          # Incidents list page
│   │   │   ├── IncidentDetail.jsx         # Incident detail page
│   │   │   ├── IncidentCreate.jsx         # Create incident page
│   │   │   ├── incidentsSlice.js          # Redux slice
│   │   │   ├── api/
│   │   │   │   └── incidentsApi.js        # API calls
│   │   │   └── components/                # Incident components (9 files)
│   │   │       ├── IncidentCard.jsx       # Incident card
│   │   │       ├── IncidentSubSidebar.jsx # Detail sidebar
│   │   │       ├── IncidentOverview.jsx   # Overview tab
│   │   │       ├── IncidentActivity.jsx   # Activity tab
│   │   │       ├── IncidentResolution.jsx # Resolution tab
│   │   │       ├── IncidentTimeline.jsx   # Timeline view
│   │   │       ├── SeverityBadge.jsx      # Severity badge
│   │   │       ├── StatusBadge.jsx        # Status badge
│   │   │       └── AssigneeSelect.jsx     # Assignee dropdown
│   │   │
│   │   ├── landing/                       # Landing page (1 file)
│   │   │   └── LandingPage.jsx            # Public landing page
│   │   │
│   │   ├── leaveConflicts/                # Leave conflicts (9 files)
│   │   │   ├── LeaveConflictsList.jsx     # Conflicts list page
│   │   │   ├── LeaveConflictDetail.jsx    # Conflict detail page
│   │   │   ├── leaveConflictsSlice.js     # Redux slice
│   │   │   ├── api/
│   │   │   │   └── leaveConflictsApi.js   # API calls
│   │   │   └── components/                # Conflict components (5 files)
│   │   │       ├── LeaveConflictSubSidebar.jsx  # Detail sidebar
│   │   │       ├── ConflictOverview.jsx   # Overview tab
│   │   │       ├── ConflictAnalysis.jsx   # AI analysis tab
│   │   │       ├── ConflictResolution.jsx # Resolution tab
│   │   │       └── ConflictHistory.jsx    # History tab
│   │   │
│   │   ├── leaves/                        # Leaves (9 files)
│   │   │   ├── LeavesList.jsx             # Leaves list page
│   │   │   ├── LeaveDetail.jsx            # Leave detail page
│   │   │   ├── LeaveRequest.jsx           # Create leave page
│   │   │   ├── leavesSlice.js             # Redux slice
│   │   │   ├── api/
│   │   │   │   └── leavesApi.js           # API calls
│   │   │   └── components/                # Leave components (4 files)
│   │   │       ├── LeaveCard.jsx          # Leave card
│   │   │       ├── LeaveCalendar.jsx      # Calendar view
│   │   │       ├── LeaveWorkflow.jsx      # Workflow status
│   │   │       └── LeaveConflicts.jsx     # Conflicts display
│   │   │
│   │   ├── noticePeriod/                  # Notice period (4 files)
│   │   │   ├── NoticePeriodList.jsx       # Notice periods list
│   │   │   ├── noticePeriodSlice.js       # Redux slice
│   │   │   ├── api/
│   │   │   │   └── noticePeriodApi.js     # API calls
│   │   │   └── components/
│   │   │       └── NoticePeriodCard.jsx   # Notice card
│   │   │
│   │   ├── notifications/                 # Notifications (5 files)
│   │   │   ├── notificationsSlice.js      # Redux slice (frontend-only)
│   │   │   ├── api/
│   │   │   │   └── notificationsApi.js    # API calls (mock)
│   │   │   └── components/                # Notification components (3 files)
│   │   │       ├── NotificationBell.jsx   # Bell icon with badge
│   │   │       ├── NotificationDropdown.jsx  # Dropdown menu
│   │   │       └── NotificationItem.jsx   # Individual notification
│   │   │
│   │   ├── profile/                       # Profile (3 files)
│   │   │   ├── ProfilePage.jsx            # Profile page
│   │   │   ├── profileSlice.js            # Redux slice
│   │   │   └── api/
│   │   │       └── profileApi.js          # API calls
│   │   │
│   │   ├── projects/                      # Projects (18 files)
│   │   │   ├── ProjectsList.jsx           # Projects list page
│   │   │   ├── ProjectDetail.jsx          # Project detail page
│   │   │   ├── ProjectCreate.jsx          # Create project page
│   │   │   ├── ProjectEdit.jsx            # Edit project page
│   │   │   ├── projectsSlice.js           # Redux slice
│   │   │   ├── api/
│   │   │   │   └── projectsApi.js         # API calls
│   │   │   └── components/                # Project components (12 files)
│   │   │       ├── ProjectCard.jsx        # Project card
│   │   │       ├── ProjectSubSidebar.jsx  # Detail sidebar
│   │   │       ├── ProjectOverview.jsx    # Overview tab
│   │   │       ├── ProjectTasks.jsx       # Tasks tab
│   │   │       ├── ProjectTeam.jsx        # Team tab
│   │   │       ├── ProjectRACI.jsx        # RACI matrix tab
│   │   │       ├── ProjectNotes.jsx       # Notes tab
│   │   │       ├── ProjectAnalytics.jsx   # Analytics tab
│   │   │       ├── ProjectMenu.jsx        # Menu tab
│   │   │       ├── ProjectSettings.jsx    # Settings
│   │   │       ├── ProjectIncidents.jsx   # Incidents
│   │   │       └── ProjectESP.jsx         # ESP
│   │   │
│   │   ├── settings/                      # Settings (6 files)
│   │   │   ├── Settings.jsx               # Settings page
│   │   │   ├── settingsSlice.js           # Redux slice
│   │   │   ├── api/
│   │   │   │   └── settingsApi.js         # API calls
│   │   │   └── components/                # Settings components (3 files)
│   │   │       ├── ProfileSettings.jsx    # Profile settings
│   │   │       ├── AppearanceSettings.jsx # Appearance settings
│   │   │       └── NotificationSettings.jsx  # Notification settings
│   │   │
│   │   ├── softwareRequests/              # Software requests (6 files)
│   │   │   ├── RequestsList.jsx           # Requests list page
│   │   │   ├── RequestDetail.jsx          # Request detail page
│   │   │   ├── SoftwareRequestsList.jsx   # Alternative list page
│   │   │   ├── softwareRequestsSlice.js   # Redux slice
│   │   │   ├── api/
│   │   │   │   └── softwareRequestsApi.js # API calls
│   │   │   └── components/
│   │   │       └── RequestCard.jsx        # Request card
│   │   │
│   │   ├── tasks/                         # Tasks (12 files)
│   │   │   ├── TasksList.jsx              # Tasks list page
│   │   │   ├── TaskDetail.jsx             # Task detail page
│   │   │   ├── TaskCreate.jsx             # Create task page
│   │   │   ├── tasksSlice.js              # Redux slice
│   │   │   ├── api/
│   │   │   │   └── tasksApi.js            # API calls
│   │   │   └── components/                # Task components (7 files)
│   │   │       ├── TaskCard.jsx           # Task card
│   │   │       ├── TaskDrawer.jsx         # Task drawer
│   │   │       ├── TaskSubSidebar.jsx     # Detail sidebar
│   │   │       ├── TaskOverview.jsx       # Overview tab
│   │   │       ├── TaskActivity.jsx       # Activity tab
│   │   │       ├── TaskHistory.jsx        # History tab
│   │   │       └── TaskDependencies.jsx   # Dependencies tab
│   │   │
│   │   ├── teams/                         # Teams (12 files)
│   │   │   ├── TeamsList.jsx              # Teams list page
│   │   │   ├── TeamDetail.jsx             # Team detail page
│   │   │   ├── TeamCreate.jsx             # Create team page
│   │   │   ├── teamsSlice.js              # Redux slice
│   │   │   ├── api/
│   │   │   │   └── teamsApi.js            # API calls
│   │   │   └── components/                # Team components (7 files)
│   │   │       ├── TeamCard.jsx           # Team card
│   │   │       ├── TeamSubSidebar.jsx     # Detail sidebar
│   │   │       ├── TeamOverview.jsx       # Overview tab
│   │   │       ├── TeamMembers.jsx        # Members tab
│   │   │       ├── TeamSkills.jsx         # Skills tab
│   │   │       ├── TeamProjects.jsx       # Projects tab
│   │   │       └── TeamCapacity.jsx       # Capacity tab
│   │   │
│   │   └── theme/                         # Theme (1 file)
│   │       └── themeSlice.js              # Theme Redux slice
│   │
│   ├── hooks/                             # Custom React hooks (9 files)
│   │   ├── useClickOutside.js             # Click outside detection
│   │   ├── useDebounce.js                 # Debounce hook
│   │   ├── useDrawer.js                   # Drawer state management
│   │   ├── useForm.js                     # Form state management
│   │   ├── useInfiniteScroll.js           # Infinite scroll
│   │   ├── useLocalStorage.js             # Local storage hook
│   │   ├── useMediaQuery.js               # Media query hook
│   │   ├── useModal.js                    # Modal state management
│   │   └── usePermissions.js              # RBAC permissions hook
│   │
│   └── utils/                             # Utility functions (7 files)
│       ├── api.js                         # Axios instance & interceptors
│       ├── constants.js                   # App constants
│       ├── formatters.js                  # Data formatters
│       ├── helpers.js                     # Helper functions
│       ├── mockData.js                    # Mock data for development
│       ├── rbac.js                        # RBAC utility functions
│       └── validators.js                  # Form validators
│
├── public/                                # Public assets
│   └── vite.svg                           # Vite logo
│
├── .gitignore                             # Git ignore file
├── eslint.config.js                       # ESLint configuration
├── index.html                             # HTML entry point
├── package.json                           # NPM dependencies
├── package-lock.json                      # NPM lock file
├── postcss.config.js                      # PostCSS configuration
├── tailwind.config.js                     # Tailwind CSS configuration
├── vite.config.js                         # Vite configuration
├── README.md                              # Frontend documentation
├── ANIMATIONS_COMPLETE.md                 # Animations documentation
├── standardize_apis.py                    # API standardization script
└── standardize_apis_v2.py                 # API standardization script v2
```

### **File Count by Category**

| Category | Files | Description |
|----------|-------|-------------|
| **Features** | 170 | All feature modules (21 features) |
| **Components** | 8 | Shared layout & context components |
| **Hooks** | 9 | Custom React hooks |
| **Utils** | 7 | Utility functions |
| **App Config** | 3 | Store, router, providers |
| **Root** | 4 | Main entry files |
| **Assets** | 1 | Static assets |
| **Config** | 6 | Build & lint configuration |
| **Total** | **208** | **All files** |

### **Feature Module Breakdown**

| Feature | Files | Components | API | Slice |
|---------|-------|------------|-----|-------|
| Analytics | 7 | 4 | ✓ | ✓ |
| Auth | 3 | 0 | ✓ | ✓ |
| Business Trips | 9 | 5 | ✓ | ✓ |
| Chatbot | 6 | 3 | ✓ | ✓ |
| Dashboard | 9 | 6 | ✓ | ✓ |
| Employees | 14 | 9 | ✓ | ✓ |
| ESP | 15 | 11 | ✓ | ✓ |
| Events | 7 | 3 | ✓ | ✓ |
| Incidents | 14 | 9 | ✓ | ✓ |
| Landing | 1 | 0 | - | - |
| Leave Conflicts | 9 | 5 | ✓ | ✓ |
| Leaves | 9 | 4 | ✓ | ✓ |
| Notice Period | 4 | 1 | ✓ | ✓ |
| Notifications | 5 | 3 | ✓ | ✓ |
| Profile | 3 | 0 | ✓ | ✓ |
| Projects | 18 | 12 | ✓ | ✓ |
| Settings | 6 | 3 | ✓ | ✓ |
| Software Requests | 6 | 1 | ✓ | ✓ |
| Tasks | 12 | 7 | ✓ | ✓ |
| Teams | 12 | 7 | ✓ | ✓ |
| Theme | 1 | 0 | - | ✓ |
| **Total** | **170** | **93** | **20** | **20** |

### **Key Frontend Patterns**

#### **1. Feature Module Structure**
Each feature follows this pattern:
```
features/[feature]/
├── [Feature]List.jsx          # List/grid view
├── [Feature]Detail.jsx        # Detail view with tabs
├── [Feature]Create.jsx        # Create form (if applicable)
├── [feature]Slice.js          # Redux Toolkit slice
├── api/
│   └── [feature]Api.js        # Axios API calls
└── components/                # Feature-specific components
    ├── [Feature]Card.jsx      # Card component
    ├── [Feature]SubSidebar.jsx # Detail page sidebar
    └── [Feature]*.jsx         # Tab components
```

#### **2. Redux Toolkit Pattern**
```javascript
// Slice structure
export const getItems = createAsyncThunk('feature/getItems', async (params) => {
  const data = await fetchItems(params)
  return data
})

const featureSlice = createSlice({
  name: 'feature',
  initialState: { data: [], isLoading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(getItems.pending, (state) => { state.isLoading = true })
      .addCase(getItems.fulfilled, (state, action) => { 
        state.data = action.payload 
      })
  }
})
```

#### **3. Component Usage Pattern**
```javascript
// Component pattern
import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { getItems, selectAllItems } from './featureSlice'

export default function ItemsList() {
  const dispatch = useDispatch()
  const items = useSelector(selectAllItems)
  
  useEffect(() => {
    dispatch(getItems())
  }, [dispatch])
  
  return <div>{items.map(item => <ItemCard key={item.id} item={item} />)}</div>
}
```

---

## �🗄️ **Database Schema (19 Tables)**

### **Core Tables (6)**
1. **users** (23 columns) - User accounts with workload tracking
   - Key fields: `assignment_status`, `current_workload_percent`, `active_project_count`, `active_task_count`, `has_blocking_incident`
   
2. **tech_teams** (7 columns) - Permanent technical teams
   
3. **tech_team_members** (4 columns) - Team membership junction
   
4. **projects** (23 columns) - Project management
   - Key fields: `project_type`, `priority`, `risk_level`, `capacity_committed_hours`, `current_active_members`
   
5. **project_members** (6 columns) - Project assignments junction
   
6. **tasks** (18 columns) - Task management
   - Key fields: `is_learning_task`, `mentor_id`, `blocked_reason`

### **Operations Tables (4)**
7. **leaves** (15 columns) - Leave requests with AI conflict detection
   - Key fields: `conflict_severity`, `alternate_assigned_id`, `status` (workflow)
   
8. **incidents** (12 columns) - Incident tracking
   
9. **project_invitations** (12 columns) - Project invitations
   
10. **software_requests** (10 columns) - Software purchase requests

### **ESP Tables (6)**
11. **esp_packages** (14 columns) - ESP package management
    - Key fields: `status`, `current_stage`, `confidence_score`, `risk_level`
    
12. **esp_l7_recommendations** (14 columns) - L7 staffing recommendations
    
13. **esp_simulations** (11 columns) - ESP simulation results
    - Key fields: `skill_gaps`, `system_recommendations`, `alternative_options`
    
14. **esp_l6_reviews** (11 columns) - L6 reviews
    
15. **esp_pm_decisions** (11 columns) - PM final decisions
    
16. **notice_periods** (10 columns) - Notice period tracking

### **Additional Tables (3)**
17. **events** (12 columns) - Company events
    
18. **event_participants** (5 columns) - Event participation junction

**Note:** Notifications are **frontend-only** (React state arrays), no database table.

---

## 🔐 **Organizational Hierarchy & RBAC**

### **Hierarchy Levels**
```
L1-L2:  CTO, VP Engineering (Admin)
L3-L5:  Director, Engineering Manager, Senior Manager (Project Manager)
L6:     Principal Architect (Technical Architect)
L7:     Team Lead (Technical Lead)
L8-L11: Senior Engineers, Engineers, Junior Engineers (Employee)
L12-L13: Trainees, Interns (Learning Employees)
```

### **Role Mapping**
- **Admin** → L1-L2
- **Project Manager** → L3-L5
- **Technical Lead** → L6-L7
- **HR** → HR role
- **Employee** → L8-L13

### **Access Control Matrix**

| Feature | Admin | PM | L6 | L7 | HR | Employee |
|---------|-------|----|----|----|----|----------|
| Users | CRUD | R | R | R | R | R (own) |
| Projects | CRUD | CRUD (own) | R | CRUD (assigned) | R | R (assigned) |
| Tasks | CRUD | CRUD (own) | CRUD | CRUD | R | RU (assigned) |
| Teams | CRUD | R | R | CRUD (own) | R | R |
| Leaves | CRUD | R | R | Approve | Approve | CR (own) |
| Incidents | CRUD | CRUD | CRUD | CRUD | R | CR |
| ESP | CRUD | Approve | Review | Create | R | R |
| Events | CRUD | R | R | R | CRUD | R |

---

## 🚀 **Backend Architecture**

### **Technology Stack**
- **Framework:** FastAPI 0.109+
- **Database:** Supabase (PostgreSQL 14+)
- **Authentication:** JWT + Supabase Auth
- **ORM:** Supabase Python Client
- **Validation:** Pydantic v2
- **AI/ML:** OpenAI API (for chatbot & ESP simulation)
- **Testing:** Pytest

### **Folder Structure**
```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Environment config
│   ├── database.py                # Supabase connection
│   ├── core/                      # Security, RBAC, dependencies
│   ├── models/                    # Pydantic schemas (21 files)
│   ├── api/v1/                    # API routes (17 files)
│   ├── services/                  # Business logic (15 files)
│   ├── utils/                     # Utilities (4 files)
│   └── tests/                     # Unit & integration tests
├── scripts/
│   ├── seed_data.py               # Seed initial data
│   └── create_tables.sql          # Supabase table creation
├── requirements.txt
└── README.md
```

---

## 📡 **API Endpoints Summary**

### **Total Endpoints: ~120+**

#### **Authentication (4 endpoints)**
- POST `/api/v1/auth/login`
- POST `/api/v1/auth/logout`
- POST `/api/v1/auth/refresh`
- GET `/api/v1/auth/me`

#### **Users (8 endpoints)**
- GET/POST `/api/v1/users`
- GET/PUT/DELETE `/api/v1/users/{id}`
- GET `/api/v1/users/{id}/workload`
- GET `/api/v1/users/{id}/projects`
- GET `/api/v1/users/{id}/tasks`

#### **Projects (11 endpoints)**
- GET/POST `/api/v1/projects`
- GET/PUT/DELETE `/api/v1/projects/{id}`
- GET/POST `/api/v1/projects/{id}/team`
- DELETE `/api/v1/projects/{id}/team/{user_id}`
- GET `/api/v1/projects/{id}/tasks`
- GET `/api/v1/projects/{id}/analytics`
- GET `/api/v1/projects/{id}/health`

#### **Tasks (7 endpoints)**
- GET/POST `/api/v1/tasks`
- GET/PUT/DELETE `/api/v1/tasks/{id}`
- PATCH `/api/v1/tasks/{id}/status`
- PATCH `/api/v1/tasks/{id}/progress`

#### **Teams (9 endpoints)**
- GET/POST `/api/v1/teams`
- GET/PUT/DELETE `/api/v1/teams/{id}`
- GET/POST `/api/v1/teams/{id}/members`
- DELETE `/api/v1/teams/{id}/members/{user_id}`
- GET `/api/v1/teams/{id}/capacity`
- GET `/api/v1/teams/{id}/skills`

#### **Employees (12 endpoints)**
- GET/POST `/api/v1/employees`
- GET/PUT/DELETE `/api/v1/employees/{id}`
- GET `/api/v1/employees/{id}/profile`
- GET `/api/v1/employees/{id}/workload`
- GET `/api/v1/employees/{id}/skills`
- GET `/api/v1/employees/{id}/projects`
- GET `/api/v1/employees/{id}/tasks`
- GET `/api/v1/employees/{id}/leaves`
- GET `/api/v1/employees/{id}/incidents`

#### **Leaves (10 endpoints)**
- GET/POST `/api/v1/leaves`
- GET/PUT/DELETE `/api/v1/leaves/{id}`
- POST `/api/v1/leaves/{id}/hr-review`
- POST `/api/v1/leaves/{id}/l7-decision`
- POST `/api/v1/leaves/{id}/l6-decision`
- GET `/api/v1/leaves/{id}/conflicts`
- POST `/api/v1/leaves/{id}/assign-alternate`

#### **Incidents (8 endpoints)**
- GET/POST `/api/v1/incidents`
- GET/PUT/DELETE `/api/v1/incidents/{id}`
- PATCH `/api/v1/incidents/{id}/status`
- PATCH `/api/v1/incidents/{id}/assign`
- POST `/api/v1/incidents/{id}/resolve`

#### **ESP (9 endpoints)**
- GET/POST `/api/v1/esp/packages`
- GET/PUT `/api/v1/esp/packages/{id}`
- POST `/api/v1/esp/packages/{id}/simulate`
- POST `/api/v1/esp/packages/{id}/l6-review`
- POST `/api/v1/esp/packages/{id}/pm-decision`
- GET `/api/v1/esp/packages/{id}/recommendations`
- GET `/api/v1/esp/packages/{id}/simulation`

#### **Events (7 endpoints)**
- GET/POST `/api/v1/events`
- GET/PUT/DELETE `/api/v1/events/{id}`
- POST `/api/v1/events/{id}/register`
- DELETE `/api/v1/events/{id}/unregister`
- GET `/api/v1/events/{id}/participants`

#### **Business Trips (7 endpoints)**
- GET/POST `/api/v1/business-trips`
- GET/PUT/DELETE `/api/v1/business-trips/{id}`
- POST `/api/v1/business-trips/{id}/approve`
- POST `/api/v1/business-trips/{id}/reject`

#### **Software Requests (7 endpoints)**
- GET/POST `/api/v1/software-requests`
- GET/PUT/DELETE `/api/v1/software-requests/{id}`
- POST `/api/v1/software-requests/{id}/approve`
- POST `/api/v1/software-requests/{id}/reject`

#### **Notice Period (5 endpoints)**
- GET/POST `/api/v1/notice-period`
- GET/PUT/DELETE `/api/v1/notice-period/{id}`

#### **Dashboard (5 endpoints)**
- GET `/api/v1/dashboard`
- GET `/api/v1/dashboard/kpis`
- GET `/api/v1/dashboard/health`
- GET `/api/v1/dashboard/productivity`
- GET `/api/v1/dashboard/alerts`

#### **Analytics (4 endpoints)**
- GET `/api/v1/analytics/projects`
- GET `/api/v1/analytics/teams`
- GET `/api/v1/analytics/employees`
- GET `/api/v1/analytics/tasks`

#### **Chatbot (2 endpoints)**
- POST `/api/v1/chatbot/message`
- GET `/api/v1/chatbot/history`

#### **Profile (4 endpoints)**
- GET `/api/v1/profile`
- PUT `/api/v1/profile`
- PUT `/api/v1/profile/password`
- PUT `/api/v1/profile/avatar`

---

## 🧠 **Key Business Logic**

### **1. Leave Approval Workflow**

```
Employee creates leave
    ↓
HR reviews quota → status: forwarded_to_team_lead
    ↓
L7 runs AI conflict detection:
    - Check critical tasks (priority = critical)
    - Check pending tasks (open/blocked)
    - Check incidents (HARD BLOCK if high/critical)
    - Find valid alternate:
        * Skill match ≥ 80%
        * Availability ≥ 30%
        * Incident-free
    ↓
L7 Decision:
    - If incident_hard_block OR no valid_alternate → ESCALATE TO L6
    - If resource_hold OR pending_tasks → ESCALATE TO L6
    - Else → APPROVE (with alternate assigned)
    ↓
L6 Decision (if escalated):
    - APPROVE or REJECT
```

### **2. ESP Workflow**

```
L7 creates ESP package → status: draft
    ↓
L7 submits → status: submitted_to_l6
    ↓
L6 runs simulation:
    - Calculate skill gaps (hours_needed - available_capacity)
    - Generate system recommendations
    - Analyze capacity (utilization %)
    - Provide alternatives (internal reallocation, contract workers, defer features)
    ↓
L6 reviews:
    - Approve/modify L7 recommendations
    - Add ESP simulation recommendations
    - status: l6_approved
    ↓
L6 forwards to PM → status: pm_reviewing
    ↓
PM makes final decision:
    - Approve positions
    - Reject positions (with reason)
    - Defer positions (with revisit date)
    - Select alternatives
    - status: pm_approved / pm_rejected / pm_modified
```

### **3. ESP Simulation Engine**

```python
def run_esp_simulation(project_id, team_id):
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
    #    - Internal reallocation (find underutilized employees < 70%)
    #    - Contract workers (3-month contracts)
    #    - Defer non-critical features (reduces staffing by 30%)
    # 8. Calculate confidence score (0-1):
    #    base: 0.5
    #    +0.2 if team_members >= 5
    #    +0.2 if required_skills >= 3
    #    +0.1 for historical data
    return simulation_result
```

### **4. Task Assignment Rules**

- **L6/L7** can assign regular tasks to **L8-L11**
- **L8** can create learning tasks for **L12-L13** (with mentor_id = L8)
- **Critical tasks** update user's `assignment_status` to `critical_owner`
- **Blocked tasks** must have `blocked_reason`
- **Progress = 100%** auto-sets `status = completed` and `completed_at = NOW()`

### **5. Incident Management**

- **Critical/High incidents** set `has_blocking_incident = TRUE` on assigned user
- **Blocking incidents** prevent leave approvals (HARD BLOCK)
- **Resolved incidents** set `resolved_at = NOW()` and `has_blocking_incident = FALSE`

---

## 📊 **Data Flow Examples**

### **Example 1: Create Project**

```
Frontend (ProjectsList.jsx)
    ↓ dispatch(createProject(projectData))
    ↓
Redux Slice (projectsSlice.js)
    ↓ createAsyncThunk → projectsApi.createProject()
    ↓
Backend API (POST /api/v1/projects)
    ↓ project_service.create_project()
    ↓
Supabase (INSERT INTO projects)
    ↓
Response (ProjectResponse)
    ↓
Redux Slice (state.projects.push(newProject))
    ↓
Frontend (UI updates with new project)
```

### **Example 2: Leave Approval**

```
Frontend (LeavesList.jsx)
    ↓ dispatch(createLeave(leaveData))
    ↓
Backend API (POST /api/v1/leaves)
    ↓ leave_service.create_leave()
    ↓ status: pending_hr_review
    ↓
HR clicks "Approve" (POST /api/v1/leaves/{id}/hr-review)
    ↓ leave_service.hr_review_leave()
    ↓ status: forwarded_to_team_lead
    ↓
L7 clicks "Review" (POST /api/v1/leaves/{id}/l7-decision)
    ↓ leave_service.l7_decision_leave()
    ↓ leave_service.detect_leave_conflicts()
        - Check critical tasks
        - Check pending tasks
        - Check incidents (HARD BLOCK)
        - Find valid alternate
    ↓ Decision:
        - If conflict → status: escalated_to_l6
        - Else → status: approved (with alternate)
```

---

## 🔧 **Environment Setup**

### **Backend (.env)**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-key
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
OPENAI_API_KEY=your-openai-api-key
```

### **Frontend (.env)**
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=QKREW V4
```

---

## 📋 **Supabase Setup Steps**

### **Step 1: Create Supabase Project**
1. Go to https://supabase.com
2. Create new project
3. Copy project URL and API keys

### **Step 2: Create Tables**
1. Open Supabase SQL Editor
2. Paste `scripts/create_tables.sql` (all 19 tables)
3. Execute SQL

### **Step 3: Enable Row Level Security (RLS)**
```sql
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
-- ... (repeat for all tables)

-- Create policies (example for users)
CREATE POLICY "Users can view all users"
  ON users FOR SELECT
  USING (true);

CREATE POLICY "Only admins can insert users"
  ON users FOR INSERT
  WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

### **Step 4: Seed Data**
```bash
python scripts/seed_data.py
```

---

## 🚀 **Implementation Timeline**

### **Week 1: Foundation**
- [ ] Set up FastAPI project structure
- [ ] Configure Supabase connection
- [ ] Implement JWT authentication
- [ ] Create base models and schemas
- [ ] Set up RBAC decorators

### **Week 2-3: Core Features**
- [ ] Users API
- [ ] Projects API
- [ ] Tasks API
- [ ] Teams API
- [ ] Employees API

### **Week 4: Operations**
- [ ] Leaves API (with AI conflict detection)
- [ ] Incidents API
- [ ] Software Requests API
- [ ] Notice Period API

### **Week 5: Advanced Features**
- [ ] ESP API (with simulation engine)
- [ ] Events API
- [ ] Business Trips API
- [ ] Dashboard API
- [ ] Analytics API

### **Week 6: AI Features**
- [ ] Chatbot API
- [ ] Leave Conflict Detection
- [ ] ESP Simulation Engine

### **Week 7: Testing & Deployment**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Frontend integration
- [ ] Production deployment

---

## ✅ **Success Criteria**

- ✅ All 19 database tables created in Supabase
- ✅ 120+ API endpoints implemented
- ✅ JWT authentication working
- ✅ RBAC implemented for all endpoints
- ✅ Leave approval workflow with AI conflict detection
- ✅ ESP simulation engine working
- ✅ Dashboard KPIs calculating correctly
- ✅ Frontend integration complete
- ✅ All tests passing (>80% coverage)
- ✅ Production deployment successful
- ✅ API documentation (Swagger) complete

---

## 📚 **Documentation Deliverables**

1. ✅ **BACKEND_ARCHITECTURE_PLAN.md** - Complete backend architecture
2. ✅ **FOLDER_STRUCTURE.md** - Detailed folder structure
3. ✅ **PROJECT_SUMMARY.md** - This document
4. ⏳ **API_DOCUMENTATION.md** - Detailed API specs (Swagger)
5. ⏳ **DATABASE_SCHEMA.md** - ER diagrams (already have database.md)
6. ⏳ **DEPLOYMENT_GUIDE.md** - Step-by-step deployment
7. ⏳ **TESTING_GUIDE.md** - How to run tests

---

## 🎯 **Next Steps for You**

### **Immediate Actions:**
1. **Create Supabase Project**
   - Sign up at https://supabase.com
   - Create new project
   - Copy project URL and API keys

2. **Provide API Keys**
   - Share Supabase URL
   - Share Supabase anon key
   - Share Supabase service key

3. **Review Documents**
   - Read `BACKEND_ARCHITECTURE_PLAN.md`
   - Read `FOLDER_STRUCTURE.md`
   - Read `database.md`

### **After Providing API Keys:**
1. I will create `scripts/create_tables.sql` with all 19 tables
2. You will paste it into Supabase SQL Editor
3. I will create `scripts/seed_data.py` to populate initial data
4. We will start implementing the backend step-by-step

---

## 📞 **Support & Questions**

If you have any questions about:
- Frontend structure
- Backend architecture
- Database schema
- API endpoints
- Business logic
- Implementation approach

Please ask! I'm here to help you understand the complete project.

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-09  
**Status:** Planning Complete - Ready for Implementation  
**Next Phase:** Supabase Setup + Backend Development
