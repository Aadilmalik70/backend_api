"""
Blueprint Storage Service - Database operations for blueprint management.

This service handles storing, retrieving, and managing blueprints in the database,
providing a clean interface for blueprint data persistence.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

from src.models.blueprint import Blueprint, Project, validate_blueprint_data, sanitize_keyword

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlueprintStorageService:
    """Service for storing and retrieving blueprints from the database."""
    
    def __init__(self, db_session: Session):
        """
        Initialize the storage service with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def save_blueprint(self, blueprint_data: Dict[str, Any], user_id: str, project_id: Optional[str] = None) -> str:
        """
        Save a new blueprint to the database.
        
        Args:
            blueprint_data: Complete blueprint data dictionary
            user_id: ID of the user creating the blueprint
            project_id: Optional project ID to associate the blueprint with
            
        Returns:
            ID of the created blueprint
            
        Raises:
            Exception: If validation fails or database operation fails
        """
        logger.info(f"Saving blueprint for keyword: {blueprint_data.get('keyword', 'Unknown')}")
        
        try:
            # Validate blueprint data
            if not validate_blueprint_data(blueprint_data):
                raise Exception("Blueprint data validation failed")
            
            # Sanitize keyword
            keyword = sanitize_keyword(blueprint_data['keyword'])
            if not keyword:
                raise Exception("Invalid keyword provided")
            
            # Extract generation time from metadata
            generation_time = None
            metadata = blueprint_data.get('generation_metadata', {})
            if 'generation_time' in metadata:
                generation_time = metadata['generation_time']
            
            # Create blueprint instance
            blueprint = Blueprint(
                keyword=keyword,
                user_id=user_id,
                project_id=project_id,
                competitor_analysis=blueprint_data.get('competitor_analysis'),
                heading_structure=blueprint_data.get('heading_structure'),
                topic_clusters=blueprint_data.get('topic_clusters'),
                serp_features=blueprint_data.get('serp_features'),
                content_insights=blueprint_data.get('content_insights'),
                status='completed',
                generation_time=generation_time
            )
            
            # Save to database
            self.db.add(blueprint)
            self.db.commit()
            self.db.refresh(blueprint)
            
            logger.info(f"Blueprint saved successfully with ID: {blueprint.id}")
            return blueprint.id
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error saving blueprint: {str(e)}")
            raise Exception(f"Failed to save blueprint: Database error")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving blueprint: {str(e)}")
            raise Exception(f"Failed to save blueprint: {str(e)}")
    
    def get_blueprint(self, blueprint_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a blueprint by ID with user ownership verification.
        
        Args:
            blueprint_id: ID of the blueprint to retrieve
            user_id: ID of the user requesting the blueprint
            
        Returns:
            Blueprint data dictionary or None if not found
        """
        logger.info(f"Retrieving blueprint: {blueprint_id} for user: {user_id}")
        
        try:
            blueprint = self.db.query(Blueprint).filter(
                Blueprint.id == blueprint_id,
                Blueprint.user_id == user_id
            ).first()
            
            if not blueprint:
                logger.warning(f"Blueprint not found: {blueprint_id}")
                return None
            
            return blueprint.to_dict()
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving blueprint: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving blueprint: {str(e)}")
            return None
    
    def list_user_blueprints(self, user_id: str, limit: int = 20, offset: int = 0, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List blueprints for a user with pagination.
        
        Args:
            user_id: ID of the user
            limit: Maximum number of blueprints to return
            offset: Number of blueprints to skip (for pagination)
            project_id: Optional project ID to filter by
            
        Returns:
            List of blueprint summary dictionaries
        """
        logger.info(f"Listing blueprints for user: {user_id} (limit: {limit}, offset: {offset})")
        
        try:
            query = self.db.query(Blueprint).filter(Blueprint.user_id == user_id)
            
            # Filter by project if specified
            if project_id:
                query = query.filter(Blueprint.project_id == project_id)
            
            blueprints = query.order_by(Blueprint.created_at.desc()).offset(offset).limit(limit).all()
            
            return [bp.to_summary() for bp in blueprints]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing blueprints: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error listing blueprints: {str(e)}")
            return []
    
    def update_blueprint_status(self, blueprint_id: str, user_id: str, status: str) -> bool:
        """
        Update the status of a blueprint.
        
        Args:
            blueprint_id: ID of the blueprint to update
            user_id: ID of the user (for ownership verification)
            status: New status value
            
        Returns:
            True if updated successfully, False otherwise
        """
        logger.info(f"Updating blueprint status: {blueprint_id} to {status}")
        
        try:
            blueprint = self.db.query(Blueprint).filter(
                Blueprint.id == blueprint_id,
                Blueprint.user_id == user_id
            ).first()
            
            if not blueprint:
                logger.warning(f"Blueprint not found for status update: {blueprint_id}")
                return False
            
            blueprint.status = status
            blueprint.updated_at = datetime.utcnow()
            
            self.db.commit()
            logger.info(f"Blueprint status updated successfully: {blueprint_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating blueprint status: {str(e)}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating blueprint status: {str(e)}")
            return False
    
    def delete_blueprint(self, blueprint_id: str, user_id: str) -> bool:
        """
        Delete a blueprint (with user ownership verification).
        
        Args:
            blueprint_id: ID of the blueprint to delete
            user_id: ID of the user (for ownership verification)
            
        Returns:
            True if deleted successfully, False otherwise
        """
        logger.info(f"Deleting blueprint: {blueprint_id} for user: {user_id}")
        
        try:
            blueprint = self.db.query(Blueprint).filter(
                Blueprint.id == blueprint_id,
                Blueprint.user_id == user_id
            ).first()
            
            if not blueprint:
                logger.warning(f"Blueprint not found for deletion: {blueprint_id}")
                return False
            
            self.db.delete(blueprint)
            self.db.commit()
            
            logger.info(f"Blueprint deleted successfully: {blueprint_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting blueprint: {str(e)}")
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting blueprint: {str(e)}")
            return False
    
    def search_blueprints(self, user_id: str, keyword_search: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search blueprints by keyword.
        
        Args:
            user_id: ID of the user
            keyword_search: Search term for keywords
            limit: Maximum number of results to return
            
        Returns:
            List of matching blueprint summaries
        """
        logger.info(f"Searching blueprints for user: {user_id}, search: {keyword_search}")
        
        try:
            blueprints = self.db.query(Blueprint).filter(
                Blueprint.user_id == user_id,
                Blueprint.keyword.contains(keyword_search.lower())
            ).order_by(Blueprint.created_at.desc()).limit(limit).all()
            
            return [bp.to_summary() for bp in blueprints]
            
        except SQLAlchemyError as e:
            logger.error(f"Database error searching blueprints: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error searching blueprints: {str(e)}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about user's blueprints.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dictionary with user statistics
        """
        logger.info(f"Getting stats for user: {user_id}")
        
        try:
            # Count total blueprints
            total_blueprints = self.db.query(Blueprint).filter(Blueprint.user_id == user_id).count()
            
            # Count by status
            completed_blueprints = self.db.query(Blueprint).filter(
                Blueprint.user_id == user_id,
                Blueprint.status == 'completed'
            ).count()
            
            # Count recent blueprints (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_blueprints = self.db.query(Blueprint).filter(
                Blueprint.user_id == user_id,
                Blueprint.created_at >= thirty_days_ago
            ).count()
            
            # Get most recent blueprint
            latest_blueprint = self.db.query(Blueprint).filter(
                Blueprint.user_id == user_id
            ).order_by(Blueprint.created_at.desc()).first()
            
            return {
                'total_blueprints': total_blueprints,
                'completed_blueprints': completed_blueprints,
                'recent_blueprints': recent_blueprints,
                'latest_blueprint_date': latest_blueprint.created_at.isoformat() if latest_blueprint else None,
                'success_rate': (completed_blueprints / total_blueprints * 100) if total_blueprints > 0 else 0
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user stats: {str(e)}")
            return {'error': 'Database error'}
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {'error': str(e)}

class ProjectStorageService:
    """Service for managing projects."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_project(self, name: str, description: str, user_id: str) -> str:
        """Create a new project."""
        try:
            project = Project(name=name, description=description, user_id=user_id)
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            return project.id
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating project: {str(e)}")
            raise Exception("Failed to create project")
    
    def get_project(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID."""
        try:
            project = self.db.query(Project).filter(
                Project.id == project_id,
                Project.user_id == user_id
            ).first()
            return project.to_dict() if project else None
        except SQLAlchemyError as e:
            logger.error(f"Database error getting project: {str(e)}")
            return None
    
    def list_user_projects(self, user_id: str) -> List[Dict[str, Any]]:
        """List all projects for a user."""
        try:
            projects = self.db.query(Project).filter(Project.user_id == user_id).order_by(Project.created_at.desc()).all()
            return [project.to_dict() for project in projects]
        except SQLAlchemyError as e:
            logger.error(f"Database error listing projects: {str(e)}")
            return []
