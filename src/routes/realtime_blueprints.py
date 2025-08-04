"""
Realtime Blueprint API Routes - RESTful endpoints with WebSocket integration.

This module provides API endpoints for creating, retrieving, and managing
content blueprints with real-time progress updates through WebSocket connections.
"""

import logging
import os
import time
import uuid
import concurrent.futures
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime

# Import services with multiple fallback strategies
try:
    from src.services.realtime_blueprint_generator import RealtimeBlueprintGenerator
    from src.services.blueprint_storage import BlueprintStorageService, ProjectStorageService
    from src.services.websocket_service import get_websocket_service
except ImportError:
    try:
        from services.realtime_blueprint_generator import RealtimeBlueprintGenerator
        from services.blueprint_storage import BlueprintStorageService, ProjectStorageService
        from services.websocket_service import get_websocket_service
    except ImportError:
        try:
            from ..services.realtime_blueprint_generator import RealtimeBlueprintGenerator
            from ..services.blueprint_storage import BlueprintStorageService, ProjectStorageService
            from ..services.websocket_service import get_websocket_service
        except ImportError:
            # Create stub classes if services unavailable
            logger = logging.getLogger(__name__)
            logger.warning("Realtime blueprint services unavailable - creating stub implementations")
            
            class RealtimeBlueprintGenerator:
                def __init__(self, *args, **kwargs):
                    pass
                def generate_blueprint_realtime(self, *args, **kwargs):
                    return {"error": "Realtime blueprint generation service unavailable"}
                def generate_quick_blueprint_realtime(self, *args, **kwargs):
                    return {"error": "Realtime quick blueprint generation service unavailable"}
            
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
            
            def get_websocket_service():
                return None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for routes
realtime_blueprint_routes = Blueprint('realtime_blueprints', __name__)

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

@realtime_blueprint_routes.route('/api/blueprints/generate-realtime', methods=['POST'])
@require_auth
def generate_blueprint_realtime(user_id):
    """
    Generate a new content blueprint with real-time WebSocket updates.
    
    Request JSON:
    {
        "keyword": "content marketing",
        "project_id": "optional-project-id",
        "enable_websocket": true  // optional, defaults to true
    }
    
    Response:
    {
        "blueprint_id": "uuid",
        "keyword": "content marketing",
        "status": "started|completed",
        "websocket_room": "blueprint_uuid",
        "estimated_time": 45,
        "message": "Blueprint generation started. Connect to WebSocket for real-time updates."
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        project_id = data.get('project_id')
        enable_websocket = data.get('enable_websocket', True)
        
        # Validate input
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if len(keyword) > 255:
            return jsonify({'error': 'Keyword too long (max 255 characters)'}), 400
        
        logger.info(f"Generating realtime blueprint for keyword: '{keyword}' "
                   f"(user: {user_id}, websocket: {enable_websocket})")
        
        # Get API keys from environment
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Check if we have minimal API requirements
        if not serpapi_key and not gemini_key and not os.getenv('GOOGLE_API_KEY'):
            logger.warning("No API keys configured - using fallback blueprint generation")
            return jsonify({
                'blueprint_id': f"fallback-{int(time.time())}",
                'keyword': keyword,
                'status': 'completed',
                'generation_time': 3,
                'data': generate_quick_fallback_blueprint(keyword, user_id),
                'websocket_enabled': False,
                'note': 'Generated using fallback method - configure API keys for full functionality'
            }), 201
        
        # Generate unique blueprint ID
        blueprint_id = str(uuid.uuid4())
        websocket_room = f"blueprint_{blueprint_id}"
        
        # Initialize realtime blueprint generator
        generator = RealtimeBlueprintGenerator(serpapi_key, gemini_key)
        
        # Check WebSocket service availability
        websocket_service = get_websocket_service()
        websocket_available = websocket_service is not None and enable_websocket
        
        if websocket_available:
            # Return immediately and process in background for real-time updates
            def generate_in_background():
                try:
                    # Generate blueprint with real-time updates
                    blueprint_data = generator.generate_blueprint_realtime(
                        keyword, user_id, project_id
                    )
                    
                    # Save to database
                    try:
                        db_session = getattr(current_app, 'db_session', None)
                        if db_session:
                            storage = BlueprintStorageService(db_session)
                            storage.save_blueprint(blueprint_data, user_id, project_id)
                            logger.info(f"Blueprint saved to database: {blueprint_id}")
                    except Exception as db_error:
                        logger.error(f"Failed to save blueprint to database: {str(db_error)}")
                        # Continue - the blueprint data is still valid
                
                except Exception as e:
                    logger.error(f"Background blueprint generation failed: {str(e)}")
                    # The WebSocket service will handle the error notification
            
            # Start background task
            if hasattr(current_app, 'socketio'):
                current_app.socketio.start_background_task(target=generate_in_background)
            else:
                # Fallback to thread executor
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(generate_in_background)
            
            # Return immediate response
            return jsonify({
                'blueprint_id': blueprint_id,
                'keyword': keyword,
                'status': 'started',
                'websocket_enabled': True,
                'websocket_room': websocket_room,
                'estimated_time': 45,
                'message': 'Blueprint generation started. Connect to WebSocket for real-time updates.',
                'websocket_events': [
                    'progress_update', 'step_completed', 'generation_complete', 'generation_failed'
                ],
                'connection_info': {
                    'join_room_event': 'join_blueprint_room',
                    'room_data': {'blueprint_id': blueprint_id, 'user_id': user_id}
                }
            }), 202  # 202 Accepted - processing started
        
        else:
            # No WebSocket - generate synchronously with timeout protection
            try:
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        generator.generate_blueprint_realtime, keyword, user_id, project_id
                    )
                    blueprint_data = future.result(timeout=150)  # 2.5 minute timeout
            except concurrent.futures.TimeoutError:
                logger.warning(f"Blueprint generation timed out for keyword: {keyword}")
                blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
            except Exception as e:
                logger.error(f"Blueprint generation failed: {str(e)}")
                blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
            
            # Save to database
            try:
                db_session = getattr(current_app, 'db_session', None)
                if db_session:
                    storage = BlueprintStorageService(db_session)
                    saved_id = storage.save_blueprint(blueprint_data, user_id, project_id)
                    blueprint_data['id'] = saved_id
            except Exception as db_error:
                logger.error(f"Failed to save blueprint to database: {str(db_error)}")
            
            # Return completed blueprint
            generation_time = blueprint_data.get('generation_metadata', {}).get('generation_time', 0)
            
            return jsonify({
                'blueprint_id': blueprint_data.get('id', blueprint_id),
                'keyword': keyword,
                'status': 'completed',
                'generation_time': generation_time,
                'websocket_enabled': False,
                'created_at': blueprint_data.get('generation_metadata', {}).get('created_at'),
                'data': blueprint_data,
                'note': 'Generated without real-time updates (WebSocket not available)'
            }), 201
        
    except Exception as e:
        logger.error(f"Error in realtime blueprint generation: {str(e)}")
        return jsonify({'error': f'Realtime blueprint generation failed: {str(e)}'}), 500

@realtime_blueprint_routes.route('/api/blueprints/generate-quick-realtime', methods=['POST'])
@require_auth
def generate_quick_blueprint_realtime(user_id):
    """
    Generate a quick blueprint with real-time updates (faster processing).
    
    Request JSON:
    {
        "keyword": "content marketing",
        "enable_websocket": true  // optional, defaults to true
    }
    
    Response:
    {
        "blueprint_id": "uuid",
        "keyword": "content marketing",
        "status": "started|completed",
        "websocket_room": "blueprint_uuid",
        "estimated_time": 15
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        enable_websocket = data.get('enable_websocket', True)
        
        # Validate input
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if len(keyword) > 255:
            return jsonify({'error': 'Keyword too long (max 255 characters)'}), 400
        
        logger.info(f"Generating quick realtime blueprint for keyword: '{keyword}' "
                   f"(user: {user_id}, websocket: {enable_websocket})")
        
        # Get API keys from environment
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Generate unique blueprint ID
        blueprint_id = str(uuid.uuid4())
        websocket_room = f"blueprint_{blueprint_id}"
        
        # Initialize realtime blueprint generator
        generator = RealtimeBlueprintGenerator(serpapi_key, gemini_key)
        
        # Check WebSocket service availability
        websocket_service = get_websocket_service()
        websocket_available = websocket_service is not None and enable_websocket
        
        if websocket_available:
            # Return immediately and process in background
            def generate_quick_in_background():
                try:
                    # Generate quick blueprint with real-time updates
                    blueprint_data = generator.generate_quick_blueprint_realtime(keyword, user_id)
                    
                    # Save to database
                    try:
                        db_session = getattr(current_app, 'db_session', None)
                        if db_session:
                            storage = BlueprintStorageService(db_session)
                            storage.save_blueprint(blueprint_data, user_id)
                            logger.info(f"Quick blueprint saved to database: {blueprint_id}")
                    except Exception as db_error:
                        logger.error(f"Failed to save quick blueprint to database: {str(db_error)}")
                
                except Exception as e:
                    logger.error(f"Background quick blueprint generation failed: {str(e)}")
            
            # Start background task
            if hasattr(current_app, 'socketio'):
                current_app.socketio.start_background_task(target=generate_quick_in_background)
            else:
                # Fallback to thread executor
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.submit(generate_quick_in_background)
            
            # Return immediate response
            return jsonify({
                'blueprint_id': blueprint_id,
                'keyword': keyword,
                'status': 'started',
                'websocket_enabled': True,
                'websocket_room': websocket_room,
                'estimated_time': 15,
                'message': 'Quick blueprint generation started. Connect to WebSocket for real-time updates.',
                'blueprint_type': 'quick'
            }), 202
        
        else:
            # No WebSocket - generate synchronously
            try:
                blueprint_data = generator.generate_quick_blueprint_realtime(keyword, user_id)
            except Exception as e:
                logger.error(f"Quick blueprint generation failed: {str(e)}")
                blueprint_data = generate_quick_fallback_blueprint(keyword, user_id)
            
            # Save to database
            try:
                db_session = getattr(current_app, 'db_session', None)
                if db_session:
                    storage = BlueprintStorageService(db_session)
                    saved_id = storage.save_blueprint(blueprint_data, user_id)
                    blueprint_data['id'] = saved_id
            except Exception as db_error:
                logger.error(f"Failed to save quick blueprint to database: {str(db_error)}")
            
            # Return completed blueprint
            generation_time = blueprint_data.get('generation_metadata', {}).get('generation_time', 0)
            
            return jsonify({
                'blueprint_id': blueprint_data.get('id', blueprint_id),
                'keyword': keyword,
                'status': 'completed',
                'generation_time': generation_time,
                'websocket_enabled': False,
                'blueprint_type': 'quick',
                'data': blueprint_data
            }), 201
    
    except Exception as e:
        logger.error(f"Error in quick realtime blueprint generation: {str(e)}")
        return jsonify({'error': f'Quick realtime blueprint generation failed: {str(e)}'}), 500

@realtime_blueprint_routes.route('/api/blueprints/<blueprint_id>/status', methods=['GET'])
@require_auth
def get_blueprint_status(user_id, blueprint_id):
    """
    Get the current status of a blueprint generation session.
    
    Response:
    {
        "blueprint_id": "uuid",
        "status": "started|in_progress|completed|failed",
        "progress": 65,
        "current_step": 3,
        "total_steps": 6,
        "message": "Generating topic clusters...",
        "websocket_session_active": true
    }
    """
    try:
        logger.info(f"Getting blueprint status: {blueprint_id} for user: {user_id}")
        
        # Check WebSocket service for active session
        websocket_service = get_websocket_service()
        if websocket_service:
            session_status = websocket_service.get_session_status(blueprint_id)
            if session_status:
                return jsonify({
                    'blueprint_id': blueprint_id,
                    'status': session_status.get('status', 'unknown'),
                    'progress': session_status.get('progress', 0),
                    'current_step': session_status.get('current_step', 0),
                    'total_steps': session_status.get('total_steps', 0),
                    'message': session_status.get('current_message', 'Processing...'),
                    'websocket_session_active': True,
                    'started_at': session_status.get('started_at'),
                    'last_updated': session_status.get('last_updated')
                }), 200
        
        # Check database for completed blueprint
        db_session = getattr(current_app, 'db_session', None)
        if db_session:
            storage = BlueprintStorageService(db_session)
            blueprint = storage.get_blueprint(blueprint_id, user_id)
            
            if blueprint:
                return jsonify({
                    'blueprint_id': blueprint_id,
                    'status': 'completed',
                    'progress': 100,
                    'message': 'Blueprint generation completed',
                    'websocket_session_active': False,
                    'created_at': blueprint.get('created_at'),
                    'keyword': blueprint.get('keyword')
                }), 200
        
        # Blueprint not found
        return jsonify({
            'blueprint_id': blueprint_id,
            'status': 'not_found',
            'message': 'Blueprint not found or session expired'
        }), 404
    
    except Exception as e:
        logger.error(f"Error getting blueprint status: {str(e)}")
        return jsonify({'error': f'Failed to get blueprint status: {str(e)}'}), 500

@realtime_blueprint_routes.route('/api/websocket/active-sessions', methods=['GET'])
@require_auth
def get_active_websocket_sessions(user_id):
    """
    Get active WebSocket sessions for the current user.
    
    Response:
    {
        "user_sessions": [
            {
                "blueprint_id": "uuid",
                "keyword": "content marketing",
                "status": "in_progress",
                "progress": 45,
                "started_at": "2025-01-01T12:00:00"
            }
        ],
        "total_active": 2
    }
    """
    try:
        websocket_service = get_websocket_service()
        if not websocket_service:
            return jsonify({
                'user_sessions': [],
                'total_active': 0,
                'message': 'WebSocket service not available'
            }), 200
        
        active_sessions = websocket_service.get_active_sessions()
        
        # Filter sessions for the current user
        user_sessions = []
        for blueprint_id, session in active_sessions.items():
            if session.get('user_id') == user_id:
                user_sessions.append({
                    'blueprint_id': blueprint_id,
                    'status': session.get('status', 'unknown'),
                    'progress': session.get('progress', 0),
                    'current_step': session.get('current_step', 0),
                    'total_steps': session.get('total_steps', 0),
                    'started_at': session.get('started_at'),
                    'last_updated': session.get('last_updated'),
                    'websocket_room': f"blueprint_{blueprint_id}"
                })
        
        return jsonify({
            'user_sessions': user_sessions,
            'total_active': len(user_sessions)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting active WebSocket sessions: {str(e)}")
        return jsonify({'error': f'Failed to get active sessions: {str(e)}'}), 500

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
            ]
        },
        'content_insights': {
            'analysis_status': 'fallback',
            'avg_word_count': 2500,
            'common_sections': ['Introduction', 'Main Content', 'Best Practices', 'Conclusion'],
            'content_gaps': ['Case studies', 'Real-world examples', 'Expert interviews']
        },
        'generation_metadata': {
            'created_at': datetime.utcnow().isoformat(),
            'generation_time': 3,
            'version': '1.0-fallback-realtime',
            'components_used': ['fallback_generator'],
            'note': 'Generated using fallback method due to timeout or API limitations',
            'realtime_enabled': False
        }
    }

# Error handlers
@realtime_blueprint_routes.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@realtime_blueprint_routes.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@realtime_blueprint_routes.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500