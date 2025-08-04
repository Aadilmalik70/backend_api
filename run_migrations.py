#!/usr/bin/env python3
"""
Database Migration Runner for SERP Strategist MVP Integration
Executes database migrations in the correct order for frontend-backend integration
"""

import sqlite3
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_path():
    """Get the path to the database file."""
    # Check for environment variable first
    db_path = os.getenv('DATABASE_URL')
    if db_path and db_path.startswith('sqlite:///'):
        return db_path.replace('sqlite:///', '')
    
    # Default to local database
    return 'serp_strategist.db'

def execute_sql_file(cursor, file_path):
    """Execute SQL commands from a file."""
    logger.info(f"Executing migration: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
        
        logger.info(f"✅ Successfully executed: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to execute {file_path}: {str(e)}")
        return False

def create_migration_table(cursor):
    """Create a table to track executed migrations."""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS migration_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT UNIQUE NOT NULL,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed'
        )
    ''')

def is_migration_executed(cursor, migration_name):
    """Check if a migration has already been executed."""
    cursor.execute(
        'SELECT COUNT(*) FROM migration_history WHERE migration_name = ?',
        (migration_name,)
    )
    return cursor.fetchone()[0] > 0

def record_migration(cursor, migration_name, status='completed'):
    """Record a migration execution."""
    cursor.execute(
        'INSERT OR REPLACE INTO migration_history (migration_name, status) VALUES (?, ?)',
        (migration_name, status)
    )

def run_migrations():
    """Run all pending migrations."""
    db_path = get_database_path()
    migrations_dir = Path(__file__).parent / 'migrations'
    
    logger.info(f"🚀 Starting database migrations...")
    logger.info(f"Database path: {db_path}")
    logger.info(f"Migrations directory: {migrations_dir}")
    
    # Define migration order
    migration_files = [
        '001_blueprint_tables.sql',
        '002_user_management_tables.sql', 
        '003_add_foreign_key_constraints.sql',
        '004_data_migration_cleanup.sql'
    ]
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Enable foreign key support for SQLite
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # Create migration tracking table
        create_migration_table(cursor)
        
        executed_count = 0
        skipped_count = 0
        
        # Execute migrations in order
        for migration_file in migration_files:
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                logger.warning(f"⚠️  Migration file not found: {migration_path}")
                continue
            
            # Check if already executed
            if is_migration_executed(cursor, migration_file):
                logger.info(f"⏭️  Skipping already executed migration: {migration_file}")
                skipped_count += 1
                continue
            
            # Execute migration
            if execute_sql_file(cursor, migration_path):
                record_migration(cursor, migration_file)
                executed_count += 1
            else:
                record_migration(cursor, migration_file, 'failed')
                logger.error(f"💥 Migration failed: {migration_file}")
                conn.rollback()
                return False
        
        # Commit all changes
        conn.commit()
        
        logger.info(f"✅ Migrations completed successfully!")
        logger.info(f"📊 Summary: {executed_count} executed, {skipped_count} skipped")
        
        # Verify database structure
        verify_database_structure(cursor)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def verify_database_structure(cursor):
    """Verify that all required tables exist."""
    logger.info("🔍 Verifying database structure...")
    
    required_tables = [
        'users', 'accounts', 'sessions', 'verification_tokens',
        'subscription_plans', 'user_subscriptions', 'payment_transactions',
        'blueprints', 'projects'
    ]
    
    for table in required_tables:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        if cursor.fetchone():
            logger.info(f"✅ Table exists: {table}")
        else:
            logger.error(f"❌ Missing table: {table}")
    
    # Check for views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = cursor.fetchall()
    logger.info(f"📋 Created views: {[view[0] for view in views]}")
    
    # Check for sample data
    cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE '%serpstrategist.com'")
    sample_users = cursor.fetchone()[0]
    logger.info(f"👥 Sample users created: {sample_users}")

def rollback_migration(migration_name):
    """Rollback a specific migration (basic implementation)."""
    logger.warning(f"🔄 Rollback not fully implemented for: {migration_name}")
    logger.info("For rollback, restore from backup or manually drop tables")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('--rollback', help='Rollback specific migration')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be executed')
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration(args.rollback)
    elif args.dry_run:
        logger.info("🔍 Dry run mode - would execute these migrations:")
        migrations_dir = Path(__file__).parent / 'migrations'
        for file in sorted(migrations_dir.glob('*.sql')):
            logger.info(f"  - {file.name}")
    else:
        success = run_migrations()
        sys.exit(0 if success else 1)