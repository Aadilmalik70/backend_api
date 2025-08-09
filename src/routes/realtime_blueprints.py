"""
Realtime Blueprint API Routes - RESTful endpoints with WebSocket integration.

This module provides API endpoints for creating, retrieving, and managing
content blueprints with real-time progress updates through WebSocket connections.
Includes usage tracking and subscription limit enforcement.
"""

import logging
import os
import time
import uuid
import concurrent.futures
from flask import Blueprint, request, jsonify, current_app, g
from functools import wraps
from datetime import datetime

# Import services with multiple fallback strategies
try:
    from src.services.realtime_blueprint_generator import RealtimeBlueprintGenerator
    from src.services.blueprint_storage import BlueprintStorageService, ProjectStorageService
    from src.services.websocket_service import get_websocket_service
    from src.middleware.usage_tracker import track_blueprint_generation, set_generated_blueprint_id
except ImportError:
    try:
        from services.realtime_blueprint_generator import RealtimeBlueprintGenerator
        from services.blueprint_storage import BlueprintStorageService, ProjectStorageService
        from services.websocket_service import get_websocket_service
        from middleware.usage_tracker import track_blueprint_generation, set_generated_blueprint_id
    except ImportError:
        try:
            from ..services.realtime_blueprint_generator import RealtimeBlueprintGenerator
            from ..services.blueprint_storage import BlueprintStorageService, ProjectStorageService
            from ..services.websocket_service import get_websocket_service
            from ..middleware.usage_tracker import track_blueprint_generation, set_generated_blueprint_id
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
                def get_user_blueprints(self, *args, **kwargs):
                    return []
            
            class ProjectStorageService:
                def __init__(self, *args, **kwargs):
                    pass
                def save_project(self, *args, **kwargs):
                    return None
                def get_project(self, *args, **kwargs):
                    return None
            
            def get_websocket_service():
                return None
            
            def track_blueprint_generation(f):
                """Stub decorator for usage tracking"""
                return f
            
            def set_generated_blueprint_id(blueprint_id):
                """Stub function for setting blueprint ID"""
                pass

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
@track_blueprint_generation  # Add usage tracking
@require_auth
def generate_blueprint_realtime(user_id):
    """
    Generate a new content blueprint with real-time WebSocket updates.
    
    This endpoint enforces subscription limits and tracks usage.
    
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
        "message": "Blueprint generation started. Connect to WebSocket for real-time updates.",
        "subscription_info": {
            "plan": "pro",
            "remaining_blueprints": 95
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        project_id = data.get('project_id')
        enable_websocket = data.get('enable_websocket', True)
        
        # Generate unique blueprint ID
        blueprint_id = str(uuid.uuid4())
        
        # Set the blueprint ID for usage tracking
        set_generated_blueprint_id(blueprint_id)
        
        logger.info(f"Starting realtime blueprint generation for user {user_id}, keyword: {keyword}")
        
        # Initialize services
        storage_service = BlueprintStorageService()
        project_service = ProjectStorageService()
        generator = RealtimeBlueprintGenerator()
        
        # Get WebSocket service for real-time updates
        websocket_service = get_websocket_service()
        websocket_room = f"blueprint_{blueprint_id}" if enable_websocket and websocket_service else None
        
        # Initial blueprint data
        initial_blueprint = {
            'id': blueprint_id,
            'user_id': user_id,
            'keyword': keyword,
            'project_id': project_id,
            'status': 'in_progress',
            'progress': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'websocket_room': websocket_room,
            'enable_websocket': enable_websocket,
            'data': {},
            'error_message': None
        }
        
        # Save initial blueprint
        try:
            storage_service.save_blueprint(blueprint_id, initial_blueprint)
            logger.info(f"Initial blueprint {blueprint_id} saved successfully")
        except Exception as e:
            logger.error(f"Failed to save initial blueprint: {str(e)}")
            # Continue anyway - the generation process might still work
        
        # Get subscription info for response
        subscription_info = {}
        if hasattr(g, 'usage_info') and g.usage_info:
            usage_info = g.usage_info
            if usage_info.get('subscription_status') == 'active':
                subscription = usage_info.get('subscription', {})
                plan_info = subscription.get('plan', {})
                subscription_info = {
                    'plan': plan_info.get('name', 'unknown'),
                    'remaining_blueprints': usage_info.get('remaining', 0),
                    'total_limit': usage_info.get('limit', 0)
                }
        
        # Start blueprint generation in background with WebSocket updates
        def generate_in_background():
            try:
                if enable_websocket and websocket_service and websocket_room:
                    # Emit initial progress update
                    websocket_service.emit_to_room(websocket_room, 'progress_update', {
                        'blueprint_id': blueprint_id,
                        'progress': 0,
                        'status': 'started',
                        'message': 'Blueprint generation started...',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Generate the blueprint with real-time updates
                result = generator.generate_blueprint_realtime(
                    keyword=keyword,
                    user_id=user_id,
                    blueprint_id=blueprint_id,
                    websocket_room=websocket_room,
                    project_id=project_id
                )
                
                if result.get('success', False):
                    # Update blueprint with final results
                    final_blueprint = initial_blueprint.copy()
                    final_blueprint.update({
                        'status': 'completed',
                        'progress': 100,
                        'updated_at': datetime.utcnow().isoformat(),
                        'data': result.get('data', {}),
                        'generation_time': result.get('generation_time', 0)
                    })
                    
                    # Save final blueprint
                    storage_service.save_blueprint(blueprint_id, final_blueprint)
                    
                    if enable_websocket and websocket_service and websocket_room:
                        # Emit completion update
                        websocket_service.emit_to_room(websocket_room, 'generation_complete', {
                            'blueprint_id': blueprint_id,
                            'progress': 100,
                            'status': 'completed',
                            'message': 'Blueprint generation completed successfully!',
                            'timestamp': datetime.utcnow().isoformat(),
                            'data': result.get('data', {})
                        })
                    
                    logger.info(f"Blueprint {blueprint_id} generation completed successfully")
                
                else:
                    # Handle generation failure
                    error_message = result.get('error', 'Unknown error during generation')
                    failed_blueprint = initial_blueprint.copy()
                    failed_blueprint.update({
                        'status': 'failed',
                        'updated_at': datetime.utcnow().isoformat(),
                        'error_message': error_message
                    })
                    
                    # Save failed blueprint
                    storage_service.save_blueprint(blueprint_id, failed_blueprint)
                    
                    if enable_websocket and websocket_service and websocket_room:
                        # Emit failure update
                        websocket_service.emit_to_room(websocket_room, 'generation_failed', {
                            'blueprint_id': blueprint_id,
                            'status': 'failed',
                            'message': error_message,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    
                    logger.error(f"Blueprint {blueprint_id} generation failed: {error_message}")
                
            except Exception as e:
                error_message = f"Unexpected error during background generation: {str(e)}"
                logger.error(error_message)
                
                # Save error state
                error_blueprint = initial_blueprint.copy()
                error_blueprint.update({
                    'status': 'failed',
                    'updated_at': datetime.utcnow().isoformat(),
                    'error_message': error_message
                })
                
                try:
                    storage_service.save_blueprint(blueprint_id, error_blueprint)
                except:
                    pass  # Don't fail if we can't save the error state
                
                if enable_websocket and websocket_service and websocket_room:
                    try:
                        websocket_service.emit_to_room(websocket_room, 'generation_failed', {
                            'blueprint_id': blueprint_id,
                            'status': 'failed',
                            'message': error_message,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    except:
                        pass  # Don't fail if we can't emit the error
        
        # Start background generation
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(generate_in_background)
            
            # Return immediate response
            response_data = {
                'success': True,
                'blueprint_id': blueprint_id,
                'keyword': keyword,
                'status': 'started',
                'progress': 0,
                'websocket_room': websocket_room,
                'enable_websocket': enable_websocket,
                'estimated_time': 45,  # seconds
                'message': 'Blueprint generation started. Connect to WebSocket for real-time updates.' if enable_websocket else 'Blueprint generation started.',
                'created_at': initial_blueprint['created_at']
            }
            
            # Add subscription info if available
            if subscription_info:
                response_data['subscription_info'] = subscription_info
            
            return jsonify(response_data), 202  # 202 Accepted
            
        except Exception as e:
            logger.error(f"Failed to start background generation: {str(e)}")
            return jsonify({
                'error': 'Failed to start blueprint generation',
                'message': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Blueprint generation request failed: {str(e)}")
        return jsonify({
            'error': 'Blueprint generation failed',
            'message': str(e)
        }), 500

@realtime_blueprint_routes.route('/api/blueprints/generate-quick-realtime', methods=['POST'])
@track_blueprint_generation  # Add usage tracking
@require_auth
def generate_quick_blueprint_realtime(user_id):
    """
    Generate a quick content blueprint with reduced analysis depth and real-time updates.
    
    This endpoint enforces subscription limits and tracks usage.
    Optimized for faster generation (target: <30 seconds).
    
    Request JSON:
    {
        "keyword": "content marketing",
        "project_id": "optional-project-id",
        "enable_websocket": true  // optional, defaults to true
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        project_id = data.get('project_id')
        enable_websocket = data.get('enable_websocket', True)
        
        # Generate unique blueprint ID
        blueprint_id = str(uuid.uuid4())
        
        # Set the blueprint ID for usage tracking
        set_generated_blueprint_id(blueprint_id)
        
        logger.info(f"Starting quick realtime blueprint generation for user {user_id}, keyword: {keyword}")
        
        # Initialize services
        storage_service = BlueprintStorageService()
        generator = RealtimeBlueprintGenerator()
        
        # Get WebSocket service for real-time updates
        websocket_service = get_websocket_service()
        websocket_room = f"blueprint_{blueprint_id}" if enable_websocket and websocket_service else None
        
        # Initial blueprint data
        initial_blueprint = {
            'id': blueprint_id,
            'user_id': user_id,
            'keyword': keyword,
            'project_id': project_id,
            'status': 'in_progress',
            'progress': 0,
            'blueprint_type': 'quick',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'websocket_room': websocket_room,
            'enable_websocket': enable_websocket,
            'data': {},
            'error_message': None
        }
        
        # Save initial blueprint
        try:
            storage_service.save_blueprint(blueprint_id, initial_blueprint)
            logger.info(f"Initial quick blueprint {blueprint_id} saved successfully")
        except Exception as e:
            logger.error(f"Failed to save initial quick blueprint: {str(e)}")
        
        # Get subscription info for response
        subscription_info = {}
        if hasattr(g, 'usage_info') and g.usage_info:
            usage_info = g.usage_info
            if usage_info.get('subscription_status') == 'active':
                subscription = usage_info.get('subscription', {})
                plan_info = subscription.get('plan', {})
                subscription_info = {
                    'plan': plan_info.get('name', 'unknown'),
                    'remaining_blueprints': usage_info.get('remaining', 0),
                    'total_limit': usage_info.get('limit', 0)
                }
        
        # Start quick blueprint generation in background
        def generate_quick_in_background():
            try:
                if enable_websocket and websocket_service and websocket_room:
                    # Emit initial progress update
                    websocket_service.emit_to_room(websocket_room, 'progress_update', {
                        'blueprint_id': blueprint_id,
                        'progress': 0,
                        'status': 'started',
                        'message': 'Quick blueprint generation started...',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Generate the quick blueprint with real-time updates
                result = generator.generate_quick_blueprint_realtime(
                    keyword=keyword,
                    user_id=user_id,
                    blueprint_id=blueprint_id,
                    websocket_room=websocket_room,
                    project_id=project_id
                )
                
                if result.get('success', False):
                    # Update blueprint with final results
                    final_blueprint = initial_blueprint.copy()
                    final_blueprint.update({
                        'status': 'completed',
                        'progress': 100,
                        'updated_at': datetime.utcnow().isoformat(),
                        'data': result.get('data', {}),
                        'generation_time': result.get('generation_time', 0)
                    })
                    
                    # Save final blueprint
                    storage_service.save_blueprint(blueprint_id, final_blueprint)
                    
                    if enable_websocket and websocket_service and websocket_room:
                        # Emit completion update
                        websocket_service.emit_to_room(websocket_room, 'generation_complete', {
                            'blueprint_id': blueprint_id,
                            'progress': 100,
                            'status': 'completed',
                            'message': 'Quick blueprint generation completed successfully!',
                            'timestamp': datetime.utcnow().isoformat(),
                            'data': result.get('data', {})
                        })
                    
                    logger.info(f"Quick blueprint {blueprint_id} generation completed successfully")
                
                else:
                    # Handle generation failure
                    error_message = result.get('error', 'Unknown error during quick generation')
                    failed_blueprint = initial_blueprint.copy()
                    failed_blueprint.update({
                        'status': 'failed',
                        'updated_at': datetime.utcnow().isoformat(),
                        'error_message': error_message
                    })
                    
                    # Save failed blueprint
                    storage_service.save_blueprint(blueprint_id, failed_blueprint)
                    
                    if enable_websocket and websocket_service and websocket_room:
                        # Emit failure update
                        websocket_service.emit_to_room(websocket_room, 'generation_failed', {
                            'blueprint_id': blueprint_id,
                            'status': 'failed',
                            'message': error_message,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    
                    logger.error(f"Quick blueprint {blueprint_id} generation failed: {error_message}")
                
            except Exception as e:
                error_message = f"Unexpected error during quick background generation: {str(e)}"
                logger.error(error_message)
                
                # Save error state
                error_blueprint = initial_blueprint.copy()
                error_blueprint.update({
                    'status': 'failed',
                    'updated_at': datetime.utcnow().isoformat(),
                    'error_message': error_message
                })
                
                try:
                    storage_service.save_blueprint(blueprint_id, error_blueprint)
                except:
                    pass
                
                if enable_websocket and websocket_service and websocket_room:
                    try:
                        websocket_service.emit_to_room(websocket_room, 'generation_failed', {
                            'blueprint_id': blueprint_id,
                            'status': 'failed',
                            'message': error_message,
                            'timestamp': datetime.utcnow().isoformat()
                        })
                    except:
                        pass
        
        # Start background generation
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(generate_quick_in_background)
            
            # Return immediate response
            response_data = {
                'success': True,
                'blueprint_id': blueprint_id,
                'keyword': keyword,
                'status': 'started',
                'progress': 0,
                'blueprint_type': 'quick',
                'websocket_room': websocket_room,
                'enable_websocket': enable_websocket,
                'estimated_time': 20,  # seconds (faster than full blueprint)
                'message': 'Quick blueprint generation started. Connect to WebSocket for real-time updates.' if enable_websocket else 'Quick blueprint generation started.',
                'created_at': initial_blueprint['created_at']
            }
            
            # Add subscription info if available
            if subscription_info:
                response_data['subscription_info'] = subscription_info
            
            return jsonify(response_data), 202  # 202 Accepted
            
        except Exception as e:
            logger.error(f"Failed to start quick background generation: {str(e)}")
            return jsonify({
                'error': 'Failed to start quick blueprint generation',
                'message': str(e)
            }), 500
        
    except Exception as e:
        logger.error(f"Quick blueprint generation request failed: {str(e)}")
        return jsonify({
            'error': 'Quick blueprint generation failed',
            'message': str(e)
        }), 500

@realtime_blueprint_routes.route('/api/blueprints/<blueprint_id>/status', methods=['GET'])
@require_auth
def get_blueprint_status(user_id, blueprint_id):
    """
    Get the current status of a blueprint generation process.
    
    Response includes progress, current status, and any available data.
    """
    try:
        storage_service = BlueprintStorageService()
        blueprint = storage_service.get_blueprint(blueprint_id)
        
        if not blueprint:
            return jsonify({
                'error': 'Blueprint not found',
                'blueprint_id': blueprint_id
            }), 404
        
        # Check if user owns this blueprint
        if blueprint.get('user_id') != user_id:
            return jsonify({
                'error': 'Access denied',
                'message': 'You do not have permission to access this blueprint'
            }), 403
        
        # Return blueprint status
        status_data = {
            'blueprint_id': blueprint_id,
            'status': blueprint.get('status', 'unknown'),
            'progress': blueprint.get('progress', 0),
            'keyword': blueprint.get('keyword'),
            'blueprint_type': blueprint.get('blueprint_type', 'standard'),
            'created_at': blueprint.get('created_at'),
            'updated_at': blueprint.get('updated_at'),
            'websocket_room': blueprint.get('websocket_room'),
            'enable_websocket': blueprint.get('enable_websocket', False)
        }
        
        # Include error message if failed
        if blueprint.get('status') == 'failed':
            status_data['error_message'] = blueprint.get('error_message')
        
        # Include data if completed
        if blueprint.get('status') == 'completed':
            status_data['data'] = blueprint.get('data', {})
            status_data['generation_time'] = blueprint.get('generation_time')
        
        return jsonify(status_data), 200
        
    except Exception as e:
        logger.error(f"Failed to get blueprint status: {str(e)}")
        return jsonify({
            'error': 'Failed to get blueprint status',
            'message': str(e)
        }), 500

@realtime_blueprint_routes.route('/api/websocket/active-sessions', methods=['GET'])
@require_auth
def get_user_websocket_sessions(user_id):
    """
    Get active WebSocket sessions for the current user.
    
    Useful for reconnecting to ongoing blueprint generations.
    """
    try:
        websocket_service = get_websocket_service()
        
        if not websocket_service:
            return jsonify({
                'active_sessions': [],
                'count': 0,
                'message': 'WebSocket service is not available'
            }), 200
        
        # Get user's active sessions
        user_sessions = []
        for session_id, session_info in websocket_service.active_sessions.items():
            if session_info.get('user_id') == user_id:
                user_sessions.append({
                    'session_id': session_id,
                    'blueprint_id': session_info.get('blueprint_id'),
                    'websocket_room': session_info.get('websocket_room'),
                    'connected_at': session_info.get('connected_at'),
                    'last_activity': session_info.get('last_activity')
                })
        
        return jsonify({
            'active_sessions': user_sessions,
            'count': len(user_sessions),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get user WebSocket sessions: {str(e)}")
        return jsonify({
            'error': 'Failed to get active sessions',
            'message': str(e)
        }), 500

# Error handlers for the blueprint
@realtime_blueprint_routes.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested realtime blueprint endpoint was not found'
    }), 404

@realtime_blueprint_routes.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The requested method is not allowed for this realtime blueprint endpoint'
    }), 405

@realtime_blueprint_routes.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred in the realtime blueprint service'
    }), 500