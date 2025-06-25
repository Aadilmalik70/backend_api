-- Blueprint Generator Database Migration
-- Creates tables for blueprints and projects

-- Create projects table first (referenced by blueprints)
CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create blueprints table
CREATE TABLE IF NOT EXISTS blueprints (
    id VARCHAR(36) PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    project_id VARCHAR(36),
    competitor_analysis JSON,
    heading_structure JSON,
    topic_clusters JSON,
    serp_features JSON,
    content_insights JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'generating',
    generation_time INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_blueprints_user_id ON blueprints(user_id);
CREATE INDEX IF NOT EXISTS idx_blueprints_keyword ON blueprints(keyword);
CREATE INDEX IF NOT EXISTS idx_blueprints_created_at ON blueprints(created_at);
CREATE INDEX IF NOT EXISTS idx_blueprints_status ON blueprints(status);
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);

-- Insert sample data for testing (optional)
-- INSERT INTO projects (id, name, description, user_id) 
-- VALUES ('test-project-1', 'Sample Project', 'A test project for blueprint development', 'test-user-1');
