-- ============================================================================
-- PROJECT NOTES TABLE
-- Add notes functionality to projects
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'general' CHECK (category IN ('general', 'meeting', 'technical', 'feedback')),
    created_by_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_project_notes_project_id ON project_notes(project_id);
CREATE INDEX IF NOT EXISTS idx_project_notes_category ON project_notes(category);
CREATE INDEX IF NOT EXISTS idx_project_notes_created_by_id ON project_notes(created_by_id);

-- Trigger for auto-update timestamps
DROP TRIGGER IF EXISTS update_project_notes_updated_at ON project_notes;
CREATE TRIGGER update_project_notes_updated_at 
BEFORE UPDATE ON project_notes 
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMPLETED: Project Notes Table
-- Run this in your PostgreSQL database (Supabase SQL Editor)
-- ============================================================================
