"""
Blueprint API Routes - RESTful endpoints for blueprint management.

This module provides API endpoints for creating, retrieving, and managing
content blueprints through the Flask application.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import os
import time

# Import services
from ..services.blueprint_generator import BlueprintGeneratorService
from ..services.blueprint_storage import BlueprintStorageService, ProjectStorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for routes
blueprint_routes = Blueprint('blueprints', __name__)

# Simple authentication decorator (replace with proper JWT in production)
def require_auth(f):
    """Simple authentication decorator - replace with proper JWT implementation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, use a simple user_id from headers
        # In production, implement proper JWT token validation
        user_id = request.headers.get('X-User-ID', 'test-user-1')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function

@blueprint_routes.route('/api/blueprints/generate', methods=['POST'])
@require_auth
def generate_blueprint(user_id):
    """
    Generate a new content blueprint.
    
    Request JSON:
    {
        "keyword": "content marketing",
        "project_id": "optional-project-id"
    }
    
    Response:
    {
        "blueprint_id": "uuid",
        "keyword": "content marketing",
        "status": "completed",
        "generation_time": 25,
        "data": { ... blueprint data ... }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        project_id = data.get('project_id')
        
        # Validate input
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if len(keyword) > 255:
            return jsonify({'error': 'Keyword too long (max 255 characters)'}), 400
        
        logger.info(f"Generating blueprint for keyword: '{keyword}' (user: {user_id})")
        
        # Get API keys from environment
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not serpapi_key or not gemini_key:
            return jsonify({'error': 'API configuration incomplete'}), 500
        
        # Initialize blueprint generator
        generator = BlueprintGeneratorService(serpapi_key, gemini_key)
        
        # Generate blueprint
        blueprint_data = generator.generate_blueprint(keyword, user_id, project_id)
        
        # Validate generated data
        if not generator.validate_blueprint_data(blueprint_data):
            return jsonify({'error': 'Blueprint generation validation failed'}), 500
        
        # Get database session (implement proper session management)
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        # Save to database
        storage = BlueprintStorageService(db_session)
        blueprint_id = storage.save_blueprint(blueprint_data, user_id, project_id)
        
        # Return response
        generation_time = blueprint_data.get('generation_metadata', {}).get('generation_time', 0)
        
        return jsonify({
            'blueprint_id': blueprint_id,
            'keyword': keyword,
            'status': 'completed',
            'generation_time': generation_time,
            'created_at': blueprint_data.get('generation_metadata', {}).get('created_at'),
            'data': blueprint_data
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating blueprint: {str(e)}")
        return jsonify({'error': f'Blueprint generation failed: {str(e)}'}), 500

@blueprint_routes.route('/api/blueprints/<blueprint_id>', methods=['GET'])
@require_auth
def get_blueprint(user_id, blueprint_id):
    """
    Retrieve a specific blueprint.
    
    Response:
    {
        "id": "uuid",
        "keyword": "content marketing",
        "competitor_analysis": { ... },
        "heading_structure": { ... },
        "topic_clusters": { ... },
        "serp_features": { ... },
        "created_at": "2025-01-01T12:00:00",
        "status": "completed"
    }
    """
    try:
        logger.info(f"Retrieving blueprint: {blueprint_id} for user: {user_id}")
        
        # Get database session
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        blueprint = storage.get_blueprint(blueprint_id, user_id)
        
        if not blueprint:
            return jsonify({'error': 'Blueprint not found'}), 404
        
        return jsonify(blueprint), 200
        
    except Exception as e:
        logger.error(f"Error retrieving blueprint: {str(e)}")
        return jsonify({'error': f'Failed to retrieve blueprint: {str(e)}'}), 500

@blueprint_routes.route('/api/blueprints', methods=['GET'])
@require_auth
def list_blueprints(user_id):
    """
    List user's blueprints with pagination.
    
    Query Parameters:
    - limit: Number of results (default: 20, max: 100)
    - offset: Results to skip (default: 0)
    - project_id: Filter by project (optional)
    - search: Search keywords (optional)
    
    Response:
    {
        "blueprints": [
            {
                "id": "uuid",
                "keyword": "content marketing",
                "status": "completed",
                "created_at": "2025-01-01T12:00:00",
                "generation_time": 25
            }
        ],
        "total": 50,
        "limit": 20,
        "offset": 0
    }
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = max(int(request.args.get('offset', 0)), 0)
        project_id = request.args.get('project_id')
        search = request.args.get('search', '').strip()
        
        logger.info(f"Listing blueprints for user: {user_id} (limit: {limit}, offset: {offset})")
        
        # Get database session
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        
        # Search or list blueprints
        if search:
            blueprints = storage.search_blueprints(user_id, search, limit)
            total = len(blueprints)  # Simplified for search
        else:
            blueprints = storage.list_user_blueprints(user_id, limit, offset, project_id)
            # TODO: Implement proper total count query
            total = len(blueprints)  # Simplified for now
        
        return jsonify({
            'blueprints': blueprints,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid query parameters'}), 400
    except Exception as e:
        logger.error(f"Error listing blueprints: {str(e)}")
        return jsonify({'error': f'Failed to list blueprints: {str(e)}'}), 500

@blueprint_routes.route('/api/blueprints/<blueprint_id>', methods=['DELETE'])
@require_auth
def delete_blueprint(user_id, blueprint_id):
    """
    Delete a blueprint.
    
    Response:
    {
        "message": "Blueprint deleted successfully"
    }
    """
    try:
        logger.info(f"Deleting blueprint: {blueprint_id} for user: {user_id}")
        
        # Get database session
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        success = storage.delete_blueprint(blueprint_id, user_id)
        
        if not success:
            return jsonify({'error': 'Blueprint not found or could not be deleted'}), 404
        
        return jsonify({'message': 'Blueprint deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting blueprint: {str(e)}")
        return jsonify({'error': f'Failed to delete blueprint: {str(e)}'}), 500

@blueprint_routes.route('/api/blueprints/<blueprint_id>/status', methods=['PATCH'])
@require_auth
def update_blueprint_status(user_id, blueprint_id):
    """
    Update blueprint status.
    
    Request JSON:
    {
        "status": "exported"
    }
    
    Response:
    {
        "message": "Status updated successfully"
    }
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400
        
        status = data['status']
        valid_statuses = ['generating', 'completed', 'failed', 'exported']
        
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        logger.info(f"Updating blueprint status: {blueprint_id} to {status}")
        
        # Get database session
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        success = storage.update_blueprint_status(blueprint_id, user_id, status)
        
        if not success:
            return jsonify({'error': 'Blueprint not found or could not be updated'}), 404
        
        return jsonify({'message': 'Status updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error updating blueprint status: {str(e)}")
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500

@blueprint_routes.route('/api/user/stats', methods=['GET'])
@require_auth
def get_user_stats(user_id):
    """
    Get user blueprint statistics.
    
    Response:
    {
        "total_blueprints": 25,
        "completed_blueprints": 23,
        "recent_blueprints": 5,
        "latest_blueprint_date": "2025-01-01T12:00:00",
        "success_rate": 92.0
    }
    """
    try:
        logger.info(f"Getting stats for user: {user_id}")
        
        # Get database session
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        stats = storage.get_user_stats(user_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500

@blueprint_routes.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for the blueprint service.
    
    Response:
    {
        "status": "healthy",
        "timestamp": "2025-01-01T12:00:00",
        "api_status": {
            "serpapi_configured": true,
            "gemini_configured": true,
            "database_connected": true
        }
    }
    """
    try:
        # Check API configuration
        serpapi_available = bool(os.getenv('SERPAPI_KEY'))
        gemini_available = bool(os.getenv('GEMINI_API_KEY'))
        
        # Check database connection
        db_available = hasattr(current_app, 'db_session')
        
        status = 'healthy' if all([serpapi_available, gemini_available, db_available]) else 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'api_status': {
                'serpapi_configured': serpapi_available,
                'gemini_configured': gemini_available,
                'database_connected': db_available
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
        }), 500

# Error handlers
@blueprint_routes.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@blueprint_routes.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@blueprint_routes.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
