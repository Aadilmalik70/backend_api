-- Add Foreign Key Constraints Migration
-- Adds user relationships to existing blueprints and projects tables
-- Ensures data integrity between frontend auth and backend blueprint storage

-- First, let's create a default user for existing data if needed
INSERT OR IGNORE INTO users (id, email, name, email_verified, subscription_status, subscription_plan, api_usage_limit)
VALUES ('default-user-id', 'admin@serpstrategist.com', 'Default Admin User', 1, 'agency', 'agency', -1);

-- Update any existing blueprints/projects without user_id to use default user
UPDATE blueprints SET user_id = 'default-user-id' WHERE user_id IS NULL OR user_id = '';
UPDATE projects SET user_id = 'default-user-id' WHERE user_id IS NULL OR user_id = '';

-- Update any user_id values that reference non-existent users to use default user
UPDATE blueprints 
SET user_id = 'default-user-id' 
WHERE user_id NOT IN (SELECT id FROM users);

UPDATE projects 
SET user_id = 'default-user-id' 
WHERE user_id NOT IN (SELECT id FROM users);

-- Now add the foreign key constraints

-- Add foreign key constraint for blueprints -> users
-- Note: We'll handle this with application-level constraints for SQLite compatibility
-- For production MySQL, uncomment the following:
-- ALTER TABLE blueprints 
-- ADD CONSTRAINT fk_blueprints_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add foreign key constraint for projects -> users  
-- For production MySQL, uncomment the following:
-- ALTER TABLE projects 
-- ADD CONSTRAINT fk_projects_user_id 
-- FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- The blueprints -> projects foreign key already exists from 001_blueprint_tables.sql
-- Verify it's working by adding some additional constraints for data integrity

-- Add NOT NULL constraints to ensure user_id is always present
-- Note: For SQLite, we need to handle this with application logic
-- For production MySQL, you can use:
-- ALTER TABLE blueprints MODIFY user_id VARCHAR(36) NOT NULL;
-- ALTER TABLE projects MODIFY user_id VARCHAR(36) NOT NULL;

-- Add some additional useful indexes for performance
CREATE INDEX IF NOT EXISTS idx_blueprints_user_created ON blueprints(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_projects_user_created ON projects(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_blueprints_status_user ON blueprints(status, user_id);

-- Create a view for user blueprint statistics (useful for dashboard)
CREATE VIEW IF NOT EXISTS user_blueprint_stats AS
SELECT 
    u.id as user_id,
    u.email,
    u.name,
    COUNT(b.id) as total_blueprints,
    COUNT(CASE WHEN b.status = 'completed' THEN 1 END) as completed_blueprints,
    COUNT(CASE WHEN b.status = 'generating' THEN 1 END) as generating_blueprints,
    COUNT(CASE WHEN b.status = 'failed' THEN 1 END) as failed_blueprints,
    COUNT(p.id) as total_projects,
    MAX(b.created_at) as last_blueprint_date,
    AVG(b.generation_time) as avg_generation_time
FROM users u
LEFT JOIN blueprints b ON u.id = b.user_id
LEFT JOIN projects p ON u.id = p.user_id
GROUP BY u.id, u.email, u.name;

-- Create a view for project summaries (useful for project management)
CREATE VIEW IF NOT EXISTS project_summaries AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.description,
    p.user_id,
    p.created_at as project_created_at,
    COUNT(b.id) as blueprint_count,
    COUNT(CASE WHEN b.status = 'completed' THEN 1 END) as completed_count,
    MAX(b.created_at) as last_blueprint_date,
    AVG(b.generation_time) as avg_generation_time
FROM projects p
LEFT JOIN blueprints b ON p.id = b.project_id
GROUP BY p.id, p.name, p.description, p.user_id, p.created_at;