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
import concurrent.futures
from datetime import datetime

# Import services with multiple fallback strategies
try:
    from src.services.blueprint_generator import BlueprintGeneratorService
    from src.services.blueprint_storage import BlueprintStorageService, ProjectStorageService
except ImportError:
    try:
        from services.blueprint_generator import BlueprintGeneratorService
        from services.blueprint_storage import BlueprintStorageService, ProjectStorageService
    except ImportError:
        try:
            from ..services.blueprint_generator import BlueprintGeneratorService
            from ..services.blueprint_storage import BlueprintStorageService, ProjectStorageService
        except ImportError:
            # Create stub classes if services unavailable
            logger.warning("Blueprint services unavailable - creating stub implementations")
            class BlueprintGeneratorService:
                def __init__(self, *args, **kwargs):
                    pass
                def generate_blueprint(self, *args, **kwargs):
                    return {"error": "Blueprint generation service unavailable"}
            
            class BlueprintStorageService:
                def __init__(self, *args, **kwargs):
                    pass
                def save_blueprint(self, *args, **kwargs):
                    return None
                def get_blueprint(self, *args, **kwargs):
                    return None
                def list_blueprints(self, *args, **kwargs):
                    return []
                    
            class ProjectStorageService:
                def __init__(self, *args, **kwargs):
                    pass

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
        
        # Allow operation without API keys but with warning
        if not serpapi_key:
            logger.warning("SERPAPI_KEY not configured - using fallback data")
        if not gemini_key:
            logger.warning("GEMINI_API_KEY not configured - using fallback data")
        
        # If no API keys at all, return fallback immediately
        if not serpapi_key and not gemini_key:
            logger.warning("No API keys configured - using fallback blueprint generation")
            return jsonify({
                'blueprint_id': f"fallback-{int(time.time())}",
                'keyword': keyword,
                'status': 'completed',
                'generation_time': 3,
                'data': generate_quick_fallback_blueprint(keyword, user_id),
                'note': 'Generated using fallback method - configure API keys for full functionality'
            }), 201
        
        # Initialize blueprint generator
        generator = BlueprintGeneratorService(serpapi_key, gemini_key)
        
        # Generate blueprint with timeout protection
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(generator.generate_blueprint, keyword, user_id, project_id)
                blueprint_data = future.result(timeout=150)  # 2.5 minute timeout
        except concurrent.futures.TimeoutError:
            logger.warning(f"Blueprint generation timed out for keyword: {keyword}")
            blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
        except Exception as e:
            logger.error(f"Blueprint generation failed: {str(e)}")
            blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
        
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

@blueprint_routes.route('/api/blueprints/generate-quick', methods=['POST'])
@require_auth
def generate_quick_blueprint(user_id):
    """
    Generate a quick blueprint without heavy processing - for immediate testing.
    
    This endpoint returns a blueprint in under 5 seconds.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        project_id = data.get('project_id')
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        logger.info(f"Generating quick blueprint for keyword: '{keyword}' (user: {user_id})")
        
        # Generate quick blueprint
        blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
        
        # Generate a simple blueprint ID
        blueprint_id = f"quick-{int(time.time())}-{hash(keyword + user_id) % 10000}"
        
        # Save to database if possible
        try:
            db_session = getattr(current_app, 'db_session', None)
            if db_session:
                storage = BlueprintStorageService(db_session)
                blueprint_id = storage.save_blueprint(blueprint_data, user_id, project_id)
        except Exception as e:
            logger.warning(f"Failed to save quick blueprint to database: {e}")
            # Continue with generated ID
        
        return jsonify({
            'blueprint_id': blueprint_id,
            'keyword': keyword,
            'status': 'completed',
            'generation_time': 3,
            'created_at': blueprint_data['generation_metadata']['created_at'],
            'data': blueprint_data,
            'note': 'Quick blueprint generated for immediate testing'
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating quick blueprint: {str(e)}")
        return jsonify({'error': f'Quick blueprint generation failed: {str(e)}'}), 500

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

def generate_quick_fallback_blueprint(keyword: str, user_id: str) -> dict:
    """Generate a quick fallback blueprint when full generation fails or times out."""
    return {
        'keyword': keyword,
        'competitor_analysis': {
            'keyword': keyword,
            'competitors': [],
            'insights': {
                'common_topics': keyword.split() + ['guide', 'tips', 'strategy', 'best practices'],
                'content_length': {
                    'average': 2500,
                    'count': 0,
                    'max': 4000,
                    'min': 1000
                },
                'sentiment_trend': 'Positive',
                'data_quality': {
                    'competitors_analyzed': 0,
                    'content_samples': 0,
                    'entities_extracted': 0,
                    'failed_competitors': 0,
                    'sentiment_samples': 0,
                    'success_rate': 0,
                    'successful_competitors': 0
                }
            }
        },
        'heading_structure': {
            'h1': f"Complete Guide to {keyword.title()}: Strategies, Tips, and Best Practices",
            'h2_sections': [
                {
                    'title': f"What is {keyword.title()}?",
                    'h3_subsections': ['Definition and Overview', 'Key Benefits and Importance']
                },
                {
                    'title': f"How to Implement {keyword.title()}",
                    'h3_subsections': ['Step-by-Step Process', 'Best Practices and Tips']
                },
                {
                    'title': f"{keyword.title()} Strategies and Techniques",
                    'h3_subsections': ['Advanced Methods', 'Common Mistakes to Avoid']
                },
                {
                    'title': f"Measuring {keyword.title()} Success",
                    'h3_subsections': ['Key Performance Indicators', 'Tools and Analytics']
                }
            ]
        },
        'topic_clusters': {
            'primary_cluster': [keyword, f"{keyword} guide", f"{keyword} tips", f"best {keyword} practices"],
            'related_keywords': [f"{keyword} strategy", f"how to {keyword}", f"{keyword} tutorial", f"{keyword} best practices"],
            'secondary_clusters': {
                'fundamentals': [f"{keyword} basics", f"{keyword} definition", f"introduction to {keyword}"],
                'implementation': [f"how to {keyword}", f"{keyword} process", f"{keyword} steps"],
                'advanced': [f"{keyword} strategies", f"advanced {keyword}", f"{keyword} optimization"],
                'tools': [f"{keyword} tools", f"best {keyword} software", f"{keyword} resources"]
            }
        },
        'serp_features': {
            'keyword': keyword,
            'recommendations': [
                {
                    'feature': 'featured_snippets',
                    'opportunity': 'medium',
                    'status': 'Target with structured content',
                    'recommendations': [
                        'Create clear, concise answers to common questions',
                        'Use structured data markup',
                        'Format content with headers and lists'
                    ]
                }
            ],
            'serp_features': [
                {
                    'name': 'people_also_ask',
                    'presence': 'medium',
                    'data': {
                        'presence': 'medium',
                        'count': 0,
                        'data': []
                    }
                }
            ]
        },
        'content_insights': {
            'analysis_status': 'fallback',
            'avg_word_count': 2500,
            'common_sections': ['Introduction', 'Main Content', 'Best Practices', 'Conclusion'],
            'content_gaps': ['Case studies', 'Real-world examples', 'Expert interviews'],
            'structural_patterns': {
                'heading_depth': '3_levels',
                'list_usage': 'recommended',
                'image_placement': 'strategic'
            }
        },
        'generation_metadata': {
            'created_at': datetime.utcnow().isoformat(),
            'generation_time': 3,
            'version': '1.0-fallback',
            'components_used': ['fallback_generator'],
            'note': 'Generated using fallback method due to timeout or API limitations'
        }
    }

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
