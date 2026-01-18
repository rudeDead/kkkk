-- ============================================================================
-- QKREW - Complete Database Schema
-- PostgreSQL 14+ (Supabase)
-- Total Tables: 19
-- Total Columns: 218+
-- ============================================================================

-- ============================================================================
-- 1. TECH_TEAMS TABLE (7 columns) - CREATE FIRST (referenced by users)
-- Permanent technical teams
-- ============================================================================
CREATE TABLE tech_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    department VARCHAR(100),
    team_lead_id UUID,  -- Will add FK constraint later
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 2. USERS TABLE (23 columns)
-- Core user accounts with workload tracking
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name VARCHAR(255) NOT NULL,
    
    -- Role & Hierarchy
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'project_manager', 'technical_lead', 'hr', 'employee')),
    hierarchy_level VARCHAR(5) NOT NULL CHECK (hierarchy_level IN ('L1','L2','L3','L4','L5','L6','L7','L8','L9','L10','L11','L12','L13')),
    
    -- Skills & Experience
    skills TEXT[],
    experience_years INTEGER,
    weekly_capacity INTEGER DEFAULT 40,
    
    -- Organization
    department VARCHAR(100),
    manager_id UUID REFERENCES users(id) ON DELETE SET NULL,
    tech_team_id UUID REFERENCES tech_teams(id) ON DELETE SET NULL,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'on_leave', 'notice_period', 'exited')),
    avatar_url TEXT,
    
    -- Workload Tracking (auto-calculated)
    assignment_status VARCHAR(50) DEFAULT 'unassigned' CHECK (assignment_status IN ('unassigned', 'assigned', 'critical_owner')),
    current_workload_percent INTEGER DEFAULT 0,
    active_project_count INTEGER DEFAULT 0,
    active_task_count INTEGER DEFAULT 0,
    has_blocking_incident BOOLEAN DEFAULT FALSE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    updated_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- ADD FOREIGN KEY TO TECH_TEAMS (now that users table exists)
-- ============================================================================
ALTER TABLE tech_teams 
ADD CONSTRAINT fk_tech_teams_team_lead 
FOREIGN KEY (team_lead_id) REFERENCES users(id) ON DELETE SET NULL;

-- ============================================================================
-- 3. TECH_TEAM_MEMBERS TABLE (4 columns)
-- Team membership junction table
-- ============================================================================
CREATE TABLE tech_team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES tech_teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- ============================================================================
-- 4. PROJECTS TABLE (23 columns)
-- Project management with comprehensive tracking
-- ============================================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Leadership
    project_manager_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    principal_architect_id UUID REFERENCES users(id) ON DELETE SET NULL,
    team_lead_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Project Details
    required_skills TEXT[],
    tech_stack TEXT[],
    project_type VARCHAR(50) NOT NULL CHECK (project_type IN ('delivery', 'internal', 'research', 'maintenance', 'client_support')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Status & Progress
    status VARCHAR(50) DEFAULT 'planning' CHECK (status IN ('planning', 'active', 'on_hold', 'completed', 'cancelled')),
    progress FLOAT DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- Hours Tracking
    total_hours INTEGER DEFAULT 0,
    done_hours INTEGER DEFAULT 0,
    
    -- Team & Tasks
    team_size INTEGER DEFAULT 0,
    active_members INTEGER DEFAULT 0,
    active_tasks INTEGER DEFAULT 0,
    blocked_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    
    -- Risk & Health
    risk_level VARCHAR(20) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high')),
    health_indicators JSONB,
    
    -- Timeline
    start_date DATE NOT NULL,
    deadline DATE,
    
    -- Budget
    budget JSONB,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- 5. PROJECT_MEMBERS TABLE (6 columns)
-- Project team assignments with allocation
-- ============================================================================
CREATE TABLE project_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(100),
    allocation_percent INTEGER DEFAULT 100 CHECK (allocation_percent >= 0 AND allocation_percent <= 100),
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(project_id, user_id)
);

-- ============================================================================
-- 6. TASKS TABLE (18 columns)
-- Task management with learning tasks support
-- ============================================================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Assignment
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    assignee_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Priority & Status
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'blocked', 'completed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    
    -- Hours
    estimated_hours INTEGER,
    actual_hours INTEGER DEFAULT 0,
    
    -- Blocking
    blocked_reason TEXT,
    
    -- Learning Tasks (L12-L13)
    is_learning_task BOOLEAN DEFAULT FALSE,
    mentor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Timeline
    due_date DATE,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- 7. LEAVES TABLE (15 columns)
-- Leave requests with AI conflict detection
-- ============================================================================
CREATE TABLE leaves (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Leave Details
    leave_type VARCHAR(50) NOT NULL CHECK (leave_type IN ('casual', 'sick', 'earned', 'maternity', 'paternity', 'unpaid')),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days INTEGER NOT NULL,
    reason TEXT,
    
    -- Workflow Status
    status VARCHAR(50) DEFAULT 'pending_hr_review' CHECK (status IN (
        'pending_hr_review',
        'forwarded_to_team_lead',
        'pending_l7_decision',
        'approved',
        'rejected',
        'escalated_to_l6',
        'cancelled'
    )),
    
    -- AI Conflict Detection
    conflict_severity VARCHAR(20) CHECK (conflict_severity IN ('none', 'high', 'critical')),
    conflict_details JSONB,
    alternate_assigned_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Approval Chain
    hr_reviewed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    hr_reviewed_at TIMESTAMP,
    decided_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    decision_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

-- ============================================================================
-- 8. INCIDENTS TABLE (12 columns)
-- Critical incident tracking
-- ============================================================================
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Assignment
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    
    -- People
    reported_by_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    assigned_to_id UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Resolution
    resolution_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- ============================================================================
-- 9. PROJECT_INVITATIONS TABLE (12 columns)
-- Project invitation system
-- ============================================================================
CREATE TABLE project_invitations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    invited_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invited_by_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Invitation Details
    role VARCHAR(100),
    allocation_percent INTEGER DEFAULT 100,
    message TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected', 'cancelled')),
    
    -- Response
    response_message TEXT,
    responded_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- ============================================================================
-- 10. SOFTWARE_REQUESTS TABLE (10 columns)
-- Software/tool purchase requests
-- ============================================================================
CREATE TABLE software_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requested_by_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Request Details
    software_name VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    estimated_cost DECIMAL(10, 2),
    urgency VARCHAR(20) DEFAULT 'medium' CHECK (urgency IN ('low', 'medium', 'high', 'critical')),
    
    -- Approval
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    approved_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    approval_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

-- ============================================================================
-- 11. ESP_PACKAGES TABLE (14 columns)
-- Extra Staffing Projection packages
-- ============================================================================
CREATE TABLE esp_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Project & Team
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES tech_teams(id) ON DELETE CASCADE,
    
    -- Creator (L7)
    created_by_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN (
        'draft',
        'submitted_to_l6',
        'l6_reviewing',
        'l6_approved',
        'pm_reviewing',
        'pm_approved',
        'pm_rejected',
        'pm_modified'
    )),
    
    -- Package Details
    required_headcount INTEGER NOT NULL,
    duration_months INTEGER NOT NULL,
    justification TEXT NOT NULL,
    
    -- Risk Assessment
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    
    -- Workflow History
    workflow_history JSONB,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    submitted_at TIMESTAMP,
    final_decision_at TIMESTAMP
);

-- ============================================================================
-- 12. ESP_L7_RECOMMENDATIONS TABLE (14 columns)
-- L7 staffing recommendations
-- ============================================================================
CREATE TABLE esp_l7_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    esp_package_id UUID NOT NULL REFERENCES esp_packages(id) ON DELETE CASCADE,
    
    -- Recommendation Details
    skill VARCHAR(255) NOT NULL,
    positions_needed INTEGER NOT NULL,
    suggested_level VARCHAR(50) NOT NULL,
    justification TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- L6 Review
    l6_approved BOOLEAN,
    l6_modified_positions INTEGER,
    l6_modified_level VARCHAR(50),
    l6_notes TEXT,
    
    -- PM Decision
    pm_approved BOOLEAN,
    pm_final_positions INTEGER,
    pm_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 13. ESP_SIMULATIONS TABLE (11 columns)
-- ESP simulation results (AI-generated)
-- ============================================================================
CREATE TABLE esp_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    esp_package_id UUID NOT NULL REFERENCES esp_packages(id) ON DELETE CASCADE,
    
    -- Simulation Results
    skill_gaps JSONB NOT NULL,
    capacity_analysis JSONB NOT NULL,
    system_recommendations JSONB NOT NULL,
    alternative_options JSONB NOT NULL,
    
    -- Metrics
    current_utilization FLOAT,
    projected_utilization FLOAT,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    
    -- Risk
    risk_factors JSONB,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    created_by_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================================
-- 14. ESP_L6_REVIEWS TABLE (11 columns)
-- L6 Principal Architect reviews
-- ============================================================================
CREATE TABLE esp_l6_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    esp_package_id UUID NOT NULL REFERENCES esp_packages(id) ON DELETE CASCADE,
    reviewed_by_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Review Decision
    decision VARCHAR(50) NOT NULL CHECK (decision IN ('approved', 'rejected', 'needs_modification')),
    
    -- Additional Recommendations
    additional_positions JSONB,
    cost_estimate DECIMAL(12, 2),
    
    -- Notes
    technical_notes TEXT,
    capacity_notes TEXT,
    risk_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    forwarded_to_pm_at TIMESTAMP
);

-- ============================================================================
-- 15. ESP_PM_DECISIONS TABLE (11 columns)
-- PM final decisions on ESP packages
-- ============================================================================
CREATE TABLE esp_pm_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    esp_package_id UUID NOT NULL REFERENCES esp_packages(id) ON DELETE CASCADE,
    decided_by_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    
    -- Decision
    final_decision VARCHAR(50) NOT NULL CHECK (final_decision IN ('approved', 'rejected', 'modified', 'deferred')),
    
    -- Approved Positions
    approved_positions JSONB,
    rejected_positions JSONB,
    selected_alternatives JSONB,
    
    -- Budget
    approved_budget DECIMAL(12, 2),
    
    -- Notes
    business_justification TEXT,
    decision_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 16. NOTICE_PERIODS TABLE (10 columns)
-- Employee exit management
-- ============================================================================
CREATE TABLE notice_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notice Details
    resignation_date DATE NOT NULL,
    last_working_day DATE NOT NULL,
    notice_period_days INTEGER NOT NULL,
    reason TEXT,
    
    -- Handover
    handover_status VARCHAR(50) DEFAULT 'pending' CHECK (handover_status IN ('pending', 'in_progress', 'completed')),
    handover_notes TEXT,
    
    -- Exit Interview
    exit_interview_completed BOOLEAN DEFAULT FALSE,
    exit_interview_notes TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 17. EVENTS TABLE (12 columns)
-- Company events management
-- ============================================================================
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Event Details
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('meeting', 'workshop', 'training', 'team_building', 'celebration', 'conference')),
    location VARCHAR(255),
    is_virtual BOOLEAN DEFAULT FALSE,
    meeting_link TEXT,
    
    -- Timeline
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    
    -- Organization
    organized_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    max_participants INTEGER,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- 18. EVENT_PARTICIPANTS TABLE (5 columns)
-- Event participation tracking
-- ============================================================================
CREATE TABLE event_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    registration_status VARCHAR(50) DEFAULT 'registered' CHECK (registration_status IN ('registered', 'attended', 'cancelled')),
    registered_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(event_id, user_id)
);

-- ============================================================================
-- 19. BUSINESS_TRIPS TABLE (13 columns)
-- Business trip management
-- ============================================================================
CREATE TABLE business_trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Trip Details
    destination VARCHAR(255) NOT NULL,
    purpose TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    -- Approval
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'completed', 'cancelled')),
    approved_by_id UUID REFERENCES users(id) ON DELETE SET NULL,
    approval_notes TEXT,
    
    -- Budget
    estimated_cost DECIMAL(10, 2),
    actual_cost DECIMAL(10, 2),
    
    -- Documents
    itinerary JSONB,
    expenses JSONB,
    
    -- Audit
    created_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_hierarchy_level ON users(hierarchy_level);
CREATE INDEX idx_users_manager_id ON users(manager_id);
CREATE INDEX idx_users_tech_team_id ON users(tech_team_id);
CREATE INDEX idx_users_status ON users(status);

-- Projects
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_pm_id ON projects(project_manager_id);
CREATE INDEX idx_projects_priority ON projects(priority);
CREATE INDEX idx_projects_created_at ON projects(created_at);

-- Tasks
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Leaves
CREATE INDEX idx_leaves_employee_id ON leaves(employee_id);
CREATE INDEX idx_leaves_status ON leaves(status);
CREATE INDEX idx_leaves_start_date ON leaves(start_date);

-- Incidents
CREATE INDEX idx_incidents_project_id ON incidents(project_id);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_assigned_to_id ON incidents(assigned_to_id);

-- ESP Packages
CREATE INDEX idx_esp_packages_project_id ON esp_packages(project_id);
CREATE INDEX idx_esp_packages_status ON esp_packages(status);
CREATE INDEX idx_esp_packages_created_by_id ON esp_packages(created_by_id);

-- Events
CREATE INDEX idx_events_start_datetime ON events(start_datetime);
CREATE INDEX idx_events_event_type ON events(event_type);

-- ============================================================================
-- TRIGGERS FOR AUTO-UPDATE TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tech_teams_updated_at BEFORE UPDATE ON tech_teams
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_esp_packages_updated_at BEFORE UPDATE ON esp_packages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMPLETED: 19 Tables, 218+ Columns, Indexes, Triggers
-- Ready for Supabase SQL Editor
-- ============================================================================
