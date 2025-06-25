"""
Database models initialization for SERP Strategist.

This module initializes all database models and provides
database management utilities.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_sqlalchemy import SQLAlchemy
import os

# Flask-SQLAlchemy instance for Flask integration
db = SQLAlchemy()

# SQLAlchemy base for direct usage
Base = declarative_base()

# Import all models to ensure they're registered
from .user import User
from .blueprint import Blueprint, Project, DatabaseManager

def init_database(app=None, database_url=None):
    """
    Initialize database for Flask application or standalone usage.
    
    Args:
        app: Flask application instance (optional)
        database_url: Database URL string (optional, defaults to env var)
        
    Returns:
        Database session factory or Flask-SQLAlchemy instance
    """
    if app is not None:
        # Flask integration mode
        db_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
        
        return db
    else:
        # Standalone mode
        db_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
        db_manager = DatabaseManager(db_url)
        db_manager.init_tables()
        return db_manager.SessionLocal

def get_database_session(app=None):
    """
    Get a database session for operations.
    
    Args:
        app: Flask application instance (optional)
        
    Returns:
        Database session
    """
    if app is not None:
        # Use Flask-SQLAlchemy session
        return db.session
    else:
        # Use standalone session
        db_url = os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
        db_manager = DatabaseManager(db_url)
        return db_manager.get_session()

# Database utilities
class DatabaseUtils:
    """Utility functions for database operations."""
    
    @staticmethod
    def create_test_data(session):
        """Create sample test data for development."""
        # Import here to avoid circular imports
        from .user import User
        from .blueprint import Project
        
        # Create test user (if using SQLAlchemy directly)
        # Note: This assumes User model is updated to work with SQLAlchemy Core
        
        # Create test project
        test_project = Project(
            name="Sample SEO Project",
            description="Test project for blueprint development",
            user_id="test-user-1"
        )
        
        session.add(test_project)
        session.commit()
        
        return test_project.id
    
    @staticmethod
    def cleanup_old_blueprints(session, days_old=30):
        """Clean up old blueprint data."""
        from datetime import datetime, timedelta
        from .blueprint import Blueprint
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_blueprints = session.query(Blueprint).filter(
            Blueprint.created_at < cutoff_date,
            Blueprint.status.in_(['failed', 'completed'])
        ).all()
        
        count = len(old_blueprints)
        
        for blueprint in old_blueprints:
            session.delete(blueprint)
        
        session.commit()
        return count

# Health check function
def check_database_health(session):
    """
    Check database connectivity and basic operations.
    
    Args:
        session: Database session
        
    Returns:
        Dictionary with health status
    """
    try:
        # Try a simple query
        from .blueprint import Blueprint
        count = session.query(Blueprint).count()
        
        return {
            'status': 'healthy',
            'blueprint_count': count,
            'connected': True
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'connected': False
        }

# Export commonly used items
__all__ = [
    'db', 'Base', 'User', 'Blueprint', 'Project', 
    'init_database', 'get_database_session', 
    'DatabaseManager', 'DatabaseUtils', 'check_database_health'
]
