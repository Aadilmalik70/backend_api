"""
Blueprint data models for SERP Strategist.

This module defines the database models for blueprints and projects,
providing the data structure for AI-generated content blueprints.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid
import json

Base = declarative_base()

class Blueprint(Base):
    """
    Blueprint model for storing AI-generated content blueprints.
    
    Each blueprint contains competitor analysis, heading structure,
    topic clusters, and SERP feature recommendations for a specific keyword.
    """
    __tablename__ = 'blueprints'
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    keyword = Column(String(255), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey('projects.id'), nullable=True)
    
    # Blueprint content (stored as JSON)
    competitor_analysis = Column(JSON, nullable=True)
    heading_structure = Column(JSON, nullable=True)
    topic_clusters = Column(JSON, nullable=True)
    serp_features = Column(JSON, nullable=True)
    content_insights = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(50), default='generating')  # generating, completed, failed, exported
    generation_time = Column(Integer, nullable=True)  # Time taken to generate in seconds
    
    # Relationships
    user = relationship("User", back_populates="blueprints")
    project = relationship("Project", back_populates="blueprints")
    
    def to_dict(self):
        """Convert blueprint to dictionary for API responses."""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'competitor_analysis': self.competitor_analysis,
            'heading_structure': self.heading_structure,
            'topic_clusters': self.topic_clusters,
            'serp_features': self.serp_features,
            'content_insights': self.content_insights,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'status': self.status,
            'generation_time': self.generation_time
        }
    
    def to_summary(self):
        """Convert blueprint to summary format for listing views."""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'generation_time': self.generation_time
        }

class Project(Base):
    """
    Project model for organizing blueprints into logical groups.
    
    Projects allow users to group related blueprints together
    for better organization and workflow management.
    """
    __tablename__ = 'projects'
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
    blueprints = relationship("Blueprint", back_populates="project", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert project to dictionary for API responses."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'blueprint_count': len(self.blueprints) if self.blueprints else 0
        }

# Helper functions for database operations
def create_database_engine(database_url: str):
    """Create SQLAlchemy engine for the given database URL."""
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300  # Recycle connections every 5 minutes
    )
    return engine

def create_session_factory(engine):
    """Create a session factory for database operations."""
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database_tables(engine):
    """Initialize database tables (create if they don't exist)."""
    Base.metadata.create_all(bind=engine)

# Database connection helper
class DatabaseManager:
    """Helper class for managing database connections and sessions."""
    
    def __init__(self, database_url: str):
        self.engine = create_database_engine(database_url)
        self.SessionLocal = create_session_factory(self.engine)
        
    def init_tables(self):
        """Initialize all database tables."""
        init_database_tables(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def close_engine(self):
        """Close the database engine."""
        self.engine.dispose()

# Validation helpers
def validate_blueprint_data(data: dict) -> bool:
    """
    Validate blueprint data structure.
    
    Args:
        data: Blueprint data dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['keyword']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    # Validate JSON fields if present
    json_fields = ['competitor_analysis', 'heading_structure', 'topic_clusters', 'serp_features']
    for field in json_fields:
        if field in data and data[field] is not None:
            try:
                # Ensure it's JSON serializable
                json.dumps(data[field])
            except (TypeError, ValueError):
                return False
    
    return True

def sanitize_keyword(keyword: str) -> str:
    """
    Sanitize keyword input for safe storage and processing.
    
    Args:
        keyword: Raw keyword input
        
    Returns:
        Sanitized keyword string
    """
    if not keyword:
        return ""
    
    # Remove extra whitespace and convert to lowercase
    sanitized = keyword.strip().lower()
    
    # Remove special characters that might cause issues
    import re
    sanitized = re.sub(r'[^\w\s-]', '', sanitized)
    
    # Limit length to reasonable size
    return sanitized[:255]
