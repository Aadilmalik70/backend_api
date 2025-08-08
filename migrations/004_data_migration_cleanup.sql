-- Data Migration and Cleanup Script
-- Ensures data integrity and prepares existing data for frontend integration
-- Creates sample data for testing and development

-- 1. Clean up any inconsistent data
-- Remove blueprints with invalid project references
UPDATE blueprints 
SET project_id = NULL 
WHERE project_id IS NOT NULL 
AND project_id NOT IN (SELECT id FROM projects);

-- 2. Create sample users for development and testing
INSERT OR IGNORE INTO users (id, email, name, password_hash, email_verified, subscription_status, subscription_plan, api_usage_limit, onboarding_completed)
VALUES 
('test-user-1', 'demo@serpstrategist.com', 'Demo User', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewC5a3', 1, 'pro', 'pro', 100, 1),
('test-user-2', 'agency@serpstrategist.com', 'Agency Demo', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewC5a3', 1, 'agency', 'agency', -1, 1),
('test-user-3', 'free@serpstrategist.com', 'Free User', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewC5a3', 1, 'free', 'basic', 5, 0);

-- 3. Migrate existing blueprints to have proper user associations
-- If there are existing blueprints with generic user IDs, associate them with demo user
UPDATE blueprints 
SET user_id = 'test-user-1' 
WHERE user_id IN ('test-user-1', 'user-1', 'demo-user', 'sample-user');

UPDATE blueprints 
SET user_id = 'test-user-2' 
WHERE user_id IN ('test-user-2', 'user-2', 'agency-user');

-- 4. Migrate existing projects to have proper user associations
UPDATE projects 
SET user_id = 'test-user-1' 
WHERE user_id IN ('test-user-1', 'user-1', 'demo-user', 'sample-user');

UPDATE projects 
SET user_id = 'test-user-2' 
WHERE user_id IN ('test-user-2', 'user-2', 'agency-user');

-- 5. Create sample projects if none exist
INSERT OR IGNORE INTO projects (id, name, description, user_id)
VALUES 
('sample-project-1', 'Content Marketing Campaign', 'Sample project for content marketing strategies', 'test-user-1'),
('sample-project-2', 'SEO Optimization Project', 'Sample SEO project for agency demo', 'test-user-2'),
('sample-project-3', 'Blog Content Strategy', 'Sample blog content planning project', 'test-user-1');

-- 6. Associate some existing blueprints with sample projects (if any exist)
UPDATE blueprints 
SET project_id = 'sample-project-1' 
WHERE user_id = 'test-user-1' 
AND project_id IS NULL 
AND id IN (
    SELECT id FROM (
        SELECT id FROM blueprints 
        WHERE user_id = 'test-user-1' 
        AND project_id IS NULL 
        ORDER BY created_at DESC 
        LIMIT 3
    ) as subquery
);

UPDATE blueprints 
SET project_id = 'sample-project-2' 
WHERE user_id = 'test-user-2' 
AND project_id IS NULL 
AND id IN (
    SELECT id FROM (
        SELECT id FROM blueprints 
        WHERE user_id = 'test-user-2' 
        AND project_id IS NULL 
        ORDER BY created_at DESC 
        LIMIT 2
    ) as subquery
);

-- 7. Update API usage tracking for existing users
UPDATE users 
SET api_usage_reset_date = datetime('now', '+1 month')
WHERE api_usage_reset_date IS NULL;

-- Reset usage counts for demo
UPDATE users 
SET api_usage_count = 0
WHERE id IN ('test-user-1', 'test-user-2', 'test-user-3');

-- 8. Create sample subscription records
INSERT OR IGNORE INTO user_subscriptions (id, user_id, plan_id, status, current_period_start, current_period_end)
VALUES 
('sub-1', 'test-user-1', 'plan-pro', 'active', 
 datetime('now', '-15 days'), 
 datetime('now', '+15 days')),
('sub-2', 'test-user-2', 'plan-agency', 'active', 
 datetime('now', '-10 days'), 
 datetime('now', '+20 days'));

-- 9. Verify data integrity
-- Count orphaned records (should be 0 after cleanup)
-- This is informational for debugging

-- Create a temporary table to store validation results
CREATE TEMP TABLE IF NOT EXISTS validation_results (
    check_name TEXT,
    result_count INTEGER,
    status TEXT
);

INSERT INTO validation_results (check_name, result_count, status)
SELECT 
    'Blueprints without valid users' as check_name,
    COUNT(*) as result_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM blueprints b
LEFT JOIN users u ON b.user_id = u.id
WHERE u.id IS NULL;

INSERT INTO validation_results (check_name, result_count, status)
SELECT 
    'Projects without valid users' as check_name,
    COUNT(*) as result_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM projects p
LEFT JOIN users u ON p.user_id = u.id
WHERE u.id IS NULL;

INSERT INTO validation_results (check_name, result_count, status)
SELECT 
    'Blueprints with invalid project references' as check_name,
    COUNT(*) as result_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END as status
FROM blueprints b
LEFT JOIN projects p ON b.project_id = p.id
WHERE b.project_id IS NOT NULL AND p.id IS NULL;

-- 10. Update timestamps for consistency
UPDATE users SET updated_at = datetime('now') WHERE updated_at IS NULL;
UPDATE projects SET updated_at = datetime('now') WHERE updated_at IS NULL;
UPDATE blueprints SET updated_at = datetime('now') WHERE updated_at IS NULL;