"""
Enhanced Flask application with WebSocket support for real-time blueprint generation.

This module extends the existing Flask application with Flask-SocketIO to provide
real-time communication capabilities during blueprint generation processes.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root and src directory to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing modules with fallback strategy
try:
    # Try absolute imports from project root
    from src.models.blueprint import DatabaseManager
    from src.routes.blueprints import blueprint_routes
    from src.routes.realtime_blueprints import realtime_blueprint_routes
    from src.services.websocket_service import init_websocket_service, get_websocket_service
    logger.info("Successfully imported all modules with src.* imports")
except ImportError as e:
    logger.warning(f"src.* imports failed: {e}. Attempting local imports...")
    try:
        # Try local imports (when run from src/ directory)
        from models.blueprint import DatabaseManager
        from routes.blueprints import blueprint_routes
        from routes.realtime_blueprints import realtime_blueprint_routes
        from services.websocket_service import init_websocket_service, get_websocket_service
        logger.info("Successfully imported all modules with local imports")
    except ImportError as local_e:
        logger.warning(f"Local imports failed: {local_e}. Attempting relative imports...")
        try:
            # Try relative imports (when imported as module)
            from .models.blueprint import DatabaseManager
            from .routes.blueprints import blueprint_routes
            from .routes.realtime_blueprints import realtime_blueprint_routes
            from .services.websocket_service import init_websocket_service, get_websocket_service
            logger.info("Successfully imported all modules with relative imports")
        except ImportError as rel_e:
            logger.error(f"All import strategies failed:")
            logger.error(f"  - src.* imports: {e}")
            logger.error(f"  - Local imports: {local_e}")
            logger.error(f"  - Relative imports: {rel_e}")
            logger.error("Creating minimal application without enhanced features...")
            
            # Create stub classes to prevent application crash
            class StubClass:
                def __init__(self, *args, **kwargs):
                    pass
            
            DatabaseManager = None
            blueprint_routes = None
            realtime_blueprint_routes = None
            init_websocket_service = None
            get_websocket_service = lambda: None

def create_realtime_app():
    """
    Application factory function for creating the Flask app with WebSocket support.
    
    Returns:
        Tuple of (Flask application instance, SocketIO instance)
    """
    # Create Flask application
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Enable CORS for frontend integration
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://*.vercel.app"])
    
    # Initialize SocketIO with CORS support
    socketio = SocketIO(
        app,
        cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://*.vercel.app"],
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    # Initialize WebSocket service
    if init_websocket_service:
        websocket_service = init_websocket_service(socketio)
        app.websocket_service = websocket_service
        logger.info("WebSocket service initialized successfully")
    else:
        logger.warning("WebSocket service initialization not available")
        app.websocket_service = None
    
    # Database setup (only if DatabaseManager is available)
    if DatabaseManager is not None:
        try:
            database_url = os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
            db_manager = DatabaseManager(database_url)
            db_manager.init_tables()
            app.db_session = db_manager.get_session()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            app.db_session = None
    else:
        logger.warning("DatabaseManager not available, skipping database setup")
        app.db_session = None
    
    # Register blueprint routes (only if available)
    if blueprint_routes is not None:
        try:
            app.register_blueprint(blueprint_routes)
            logger.info("Standard blueprint routes registered successfully")
        except Exception as e:
            logger.error(f"Standard blueprint registration failed: {str(e)}")
    else:
        logger.warning("Standard blueprint routes not available, skipping registration")
    
    # Register realtime blueprint routes (only if available)
    if realtime_blueprint_routes is not None:
        try:
            app.register_blueprint(realtime_blueprint_routes)
            logger.info("Realtime blueprint routes registered successfully")
        except Exception as e:
            logger.error(f"Realtime blueprint registration failed: {str(e)}")
    else:
        logger.warning("Realtime blueprint routes not available, skipping registration")
    
    # Enhanced health check endpoint with WebSocket status
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Enhanced health check endpoint with WebSocket status.
        
        Returns:
        {
            "status": "ok|degraded|error",
            "version": "2.0.0-realtime",
            "features": {...},
            "services": {...},
            "websocket": {...}
        }
        """
        # Check basic services
        db_available = app.db_session is not None
        websocket_available = app.websocket_service is not None
        
        # Check API configuration
        serpapi_available = bool(os.getenv('SERPAPI_KEY'))
        gemini_available = bool(os.getenv('GEMINI_API_KEY'))
        google_api_available = bool(os.getenv('GOOGLE_API_KEY'))
        
        # Determine overall status
        essential_services = [db_available, websocket_available]
        api_services = [serpapi_available or google_api_available, gemini_available]
        
        if all(essential_services) and any(api_services):
            status = "ok"
        elif any(essential_services) and any(api_services):
            status = "degraded"
        else:
            status = "error"
        
        # Get WebSocket service status
        websocket_status = {}
        if websocket_available:
            active_sessions = app.websocket_service.get_active_sessions()
            websocket_status = {
                'enabled': True,
                'active_sessions': len(active_sessions),
                'session_ids': list(active_sessions.keys()) if len(active_sessions) <= 5 else list(active_sessions.keys())[:5]
            }
        else:
            websocket_status = {'enabled': False, 'active_sessions': 0}
        
        return jsonify({
            "status": status,
            "version": "2.0.0-realtime",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "blueprint_generation": True,
                "realtime_updates": websocket_available,
                "database": db_available,
                "blueprint_routes": blueprint_routes is not None,
                "realtime_routes": realtime_blueprint_routes is not None,
                "websocket_communication": websocket_available
            },
            "services": {
                "database_connected": db_available,
                "websocket_service": websocket_available
            },
            "api_keys": {
                "serpapi": serpapi_available,
                "gemini": gemini_available,
                "google_api": google_api_available
            },
            "websocket": websocket_status
        })
    
    # WebSocket status endpoint
    @app.route('/api/websocket/status', methods=['GET'])
    def websocket_status():
        """
        Get detailed WebSocket service status.
        
        Returns:
        {
            "enabled": true,
            "active_sessions": 3,
            "sessions": [...],
            "service_info": {...}
        }
        """
        if not app.websocket_service:
            return jsonify({
                "enabled": False,
                "message": "WebSocket service not available"
            }), 503
        
        active_sessions = app.websocket_service.get_active_sessions()
        
        # Create session summaries (without sensitive data)
        session_summaries = []
        for blueprint_id, session in active_sessions.items():
            session_summaries.append({
                "blueprint_id": blueprint_id,
                "user_id": session.get('user_id', 'unknown'),
                "status": session.get('status', 'unknown'),
                "progress": session.get('progress', 0),
                "current_step": session.get('current_step', 0),
                "total_steps": session.get('total_steps', 0),
                "started_at": session.get('started_at'),
                "last_updated": session.get('last_updated')
            })
        
        return jsonify({
            "enabled": True,
            "active_sessions": len(active_sessions),
            "sessions": session_summaries,
            "service_info": {
                "service_name": "WebSocketService",
                "version": "1.0",
                "capabilities": [
                    "real_time_progress",
                    "session_management", 
                    "room_based_communication",
                    "automatic_cleanup"
                ]
            }
        })
    
    # WebSocket session cleanup endpoint
    @app.route('/api/websocket/cleanup', methods=['POST'])
    def cleanup_websocket_sessions():
        """
        Manually trigger cleanup of stale WebSocket sessions.
        
        Request JSON:
        {
            "max_age_hours": 24  // optional, defaults to 24
        }
        """
        if not app.websocket_service:
            return jsonify({"error": "WebSocket service not available"}), 503
        
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        try:
            cleaned_count = app.websocket_service.cleanup_stale_sessions(max_age_hours)
            return jsonify({
                "message": f"Cleaned up {cleaned_count} stale sessions",
                "cleaned_sessions": cleaned_count,
                "max_age_hours": max_age_hours
            })
        except Exception as e:
            logger.error(f"Error cleaning up WebSocket sessions: {str(e)}")
            return jsonify({"error": f"Cleanup failed: {str(e)}"}), 500
    
    # Enhanced root endpoint with WebSocket information
    @app.route('/', methods=['GET'])
    def root():
        """
        Root endpoint with API information including WebSocket capabilities.
        
        Returns:
        {
            "name": "SERP Strategist API",
            "version": "2.0.0-realtime",
            "status": "active",
            "endpoints": {...},
            "websocket": {...}
        }
        """
        websocket_info = {}
        if app.websocket_service:
            websocket_info = {
                "enabled": True,
                "namespace": "/",
                "events": [
                    "connect", "disconnect", "join_blueprint_room", "leave_blueprint_room",
                    "progress_update", "step_completed", "generation_complete", 
                    "generation_failed", "ping"
                ],
                "room_format": "blueprint_{blueprint_id}",
                "connection_url": f"ws://{request.host}/socket.io/"
            }
        else:
            websocket_info = {"enabled": False}
        
        return jsonify({
            "name": "SERP Strategist API",
            "version": "2.0.0-realtime",
            "status": "active",
            "description": "AI-powered content blueprint generation platform with real-time updates",
            "endpoints": {
                "realtime_blueprint_generation": "/api/blueprints/generate-realtime",
                "quick_realtime_generation": "/api/blueprints/generate-quick-realtime",
                "blueprint_status": "/api/blueprints/{id}/status",
                "active_sessions": "/api/websocket/active-sessions",
                "standard_generation": "/api/blueprints/generate",
                "blueprint_retrieval": "/api/blueprints/{id}",
                "blueprint_listing": "/api/blueprints",
                "health_check": "/api/health",
                "websocket_status": "/api/websocket/status",
                "user_statistics": "/api/user/stats"
            },
            "websocket": websocket_info,
            "features": {
                "realtime_updates": app.websocket_service is not None,
                "progress_tracking": True,
                "session_management": True,
                "auto_reconnection": True,
                "background_processing": True
            },
            "documentation": {
                "api_guide": "See README.md for API usage examples",
                "websocket_guide": "Connect to /socket.io/ for real-time updates",
                "authentication": "Use X-User-ID header (temporary - JWT coming soon)",
                "rate_limits": "Applied per user and API endpoint"
            }
        })
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'available_endpoints': [
                '/api/blueprints/generate-realtime',
                '/api/blueprints/generate-quick-realtime',
                '/api/blueprints/generate',
                '/api/blueprints',
                '/api/health',
                '/api/websocket/status',
                '/api/user/stats'
            ]
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed for this endpoint'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error occurred'}), 500
    
    # Cleanup on app teardown
    @app.teardown_appcontext
    def cleanup_db_session(error):
        if hasattr(app, 'db_session') and app.db_session:
            app.db_session.close()
    
    # Add cleanup task for WebSocket sessions
    if app.websocket_service:
        @socketio.on_error_default
        def default_error_handler(e):
            logger.error(f"WebSocket error: {str(e)}")
    
    logger.info("✅ Realtime Flask application created with WebSocket support")
    return app, socketio

def create_app():
    """
    Create the application (compatibility wrapper for existing imports).
    
    Returns:
        Flask application instance
    """
    app, socketio = create_realtime_app()
    # Store socketio instance in app for access
    app.socketio = socketio
    return app

# Create the application instances
app, socketio_instance = create_realtime_app()

if __name__ == '__main__':
    logger.info("Starting SERP Strategist API server with WebSocket support...")
    logger.info("Enhanced blueprint generation endpoints available:")
    logger.info("  POST /api/blueprints/generate-realtime - Generate new blueprint with real-time updates")
    logger.info("  POST /api/blueprints/generate-quick-realtime - Quick generation with real-time updates")
    logger.info("  GET  /api/blueprints/{id}/status - Real-time status checking")
    logger.info("  GET  /api/websocket/active-sessions - User's active WebSocket sessions")
    logger.info("  POST /api/blueprints/generate - Standard blueprint generation")
    logger.info("  GET  /api/blueprints/{id} - Get specific blueprint")
    logger.info("  GET  /api/blueprints - List user blueprints")
    logger.info("  GET  /api/health - API health check with WebSocket status")
    logger.info("  GET  /api/websocket/status - WebSocket service status")
    logger.info("  GET  /api/user/stats - User statistics")
    logger.info("")
    logger.info("WebSocket endpoints:")
    logger.info("  connect/disconnect - Connection management")
    logger.info("  join_blueprint_room - Join blueprint progress room")
    logger.info("  leave_blueprint_room - Leave blueprint progress room")
    logger.info("  progress_update - Real-time progress notifications")
    logger.info("  step_completed - Step completion notifications")
    logger.info("  generation_complete - Blueprint completion notifications")
    logger.info("  generation_failed - Blueprint failure notifications")
    
    # Run with SocketIO
    socketio_instance.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True  # For development only
    )