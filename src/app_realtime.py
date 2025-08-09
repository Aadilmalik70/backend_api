"""
Enhanced Flask application with WebSocket support for real-time blueprint generation.

This module extends the existing Flask application with Flask-SocketIO to provide
real-time communication capabilities during blueprint generation processes.
Includes payment integration and subscription management.
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
    from src.models import init_database
    from src.routes.blueprints import blueprint_routes
    from src.routes.realtime_blueprints import realtime_blueprint_routes
    from src.routes.payment import payment_bp
    from src.services.websocket_service import init_websocket_service, get_websocket_service
    from src.middleware import UsageMiddleware
    logger.info("Successfully imported all modules with src.* imports")
except ImportError as e:
    logger.warning(f"src.* imports failed: {e}. Attempting local imports...")
    try:
        # Try local imports (when run from src/ directory)
        from models.blueprint import DatabaseManager
        from models import init_database
        from routes.blueprints import blueprint_routes
        from routes.realtime_blueprints import realtime_blueprint_routes
        from routes.payment import payment_bp
        from services.websocket_service import init_websocket_service, get_websocket_service
        from middleware import UsageMiddleware
        logger.info("Successfully imported all modules with local imports")
    except ImportError as local_e:
        logger.warning(f"Local imports failed: {local_e}. Attempting relative imports...")
        try:
            # Try relative imports (when imported as module)
            from .models.blueprint import DatabaseManager
            from .models import init_database
            from .routes.blueprints import blueprint_routes
            from .routes.realtime_blueprints import realtime_blueprint_routes
            from .routes.payment import payment_bp
            from .services.websocket_service import init_websocket_service, get_websocket_service
            from .middleware import UsageMiddleware
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
            init_database = None
            blueprint_routes = None
            realtime_blueprint_routes = None
            payment_bp = None
            init_websocket_service = None
            get_websocket_service = lambda: None
            UsageMiddleware = None

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
    
    # Database setup with Flask-SQLAlchemy (includes subscription models)
    if init_database is not None:
        try:
            db = init_database(app)
            app.db = db
            logger.info("Database initialized successfully with payment models")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            app.db = None
    else:
        # Fallback to old DatabaseManager if init_database not available
        if DatabaseManager is not None:
            try:
                # Create database manager instance
                db_url = os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
                db_manager = DatabaseManager(db_url)
                db_manager.init_tables()
                app.db_manager = db_manager
                app.db_session = db_manager.get_session()
                logger.info("Database manager setup completed successfully (fallback mode)")
            except Exception as e:
                logger.error(f"Database manager setup failed: {str(e)}")
                app.db_manager = None
                app.db_session = None
        else:
            logger.warning("DatabaseManager not available, skipping database setup")
            app.db_session = None
    
    # Initialize usage tracking middleware
    if UsageMiddleware is not None:
        try:
            usage_middleware = UsageMiddleware(app)
            logger.info("Usage tracking middleware initialized successfully")
        except Exception as e:
            logger.error(f"Usage middleware initialization failed: {str(e)}")
    else:
        logger.warning("Usage middleware not available, skipping initialization")
    
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
    
    # Register payment routes (only if available)
    if payment_bp is not None:
        try:
            app.register_blueprint(payment_bp)
            logger.info("Payment routes registered successfully")
        except Exception as e:
            logger.error(f"Payment routes registration failed: {str(e)}")
    else:
        logger.warning("Payment routes not available, skipping registration")
    
    # Enhanced health check endpoint with WebSocket and payment status
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Enhanced health check endpoint with WebSocket and payment status.
        
        Returns:
            JSON response with comprehensive health status
        """
        try:
            # Basic health info
            health_info = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '2.1.0',
                'mode': 'realtime',
                'features': {
                    'websocket_support': app.websocket_service is not None,
                    'database_available': hasattr(app, 'db') and app.db is not None,
                    'blueprint_generation': blueprint_routes is not None,
                    'realtime_generation': realtime_blueprint_routes is not None,
                    'payment_processing': payment_bp is not None,
                    'usage_tracking': UsageMiddleware is not None
                }
            }
            
            # WebSocket service status
            if app.websocket_service:
                ws_service = get_websocket_service()
                if ws_service:
                    health_info['websocket'] = {
                        'status': 'active',
                        'active_sessions': len(ws_service.active_sessions),
                        'total_connections': ws_service.connection_count
                    }
                else:
                    health_info['websocket'] = {'status': 'unavailable'}
            else:
                health_info['websocket'] = {'status': 'disabled'}
            
            # Database health check
            if hasattr(app, 'db') and app.db is not None:
                try:
                    from .models import check_database_health
                    db_health = check_database_health(app.db.session)
                    health_info['database'] = db_health
                except Exception as db_e:
                    health_info['database'] = {
                        'status': 'unhealthy',
                        'error': str(db_e)
                    }
            elif hasattr(app, 'db_session') and app.db_session:
                try:
                    # Test basic database connectivity
                    from .models.blueprint import Blueprint
                    count = app.db_session.query(Blueprint).count()
                    health_info['database'] = {
                        'status': 'healthy',
                        'blueprint_count': count,
                        'mode': 'legacy'
                    }
                except Exception as db_e:
                    health_info['database'] = {
                        'status': 'unhealthy',
                        'error': str(db_e),
                        'mode': 'legacy'
                    }
            else:
                health_info['database'] = {'status': 'unavailable'}
            
            # Payment service health check
            if payment_bp is not None:
                try:
                    from .services.payment_service import PaymentService
                    payment_service = PaymentService()
                    health_info['payment'] = {
                        'status': 'available' if payment_service.is_available() else 'configured_but_unavailable',
                        'razorpay_configured': payment_service.razorpay_key_id is not None,
                        'supported_currencies': ['INR']
                    }
                except Exception as pay_e:
                    health_info['payment'] = {
                        'status': 'error',
                        'error': str(pay_e)
                    }
            else:
                health_info['payment'] = {'status': 'unavailable'}
            
            # Environment checks
            health_info['environment'] = {
                'google_api_configured': bool(os.getenv('GOOGLE_API_KEY')),
                'gemini_api_configured': bool(os.getenv('GEMINI_API_KEY')),
                'search_engine_configured': bool(os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')),
                'razorpay_configured': bool(os.getenv('RAZORPAY_KEY_ID')),
                'database_url': bool(os.getenv('DATABASE_URL'))
            }
            
            return jsonify(health_info), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'version': '2.1.0',
                'mode': 'realtime'
            }), 500
    
    # WebSocket connection status endpoint
    @app.route('/api/websocket/status', methods=['GET'])
    def websocket_status():
        """
        Get WebSocket service status and active connections.
        
        Returns:
            JSON response with WebSocket status
        """
        try:
            if not app.websocket_service:
                return jsonify({
                    'status': 'disabled',
                    'message': 'WebSocket service is not available'
                }), 200
            
            ws_service = get_websocket_service()
            if not ws_service:
                return jsonify({
                    'status': 'unavailable',
                    'message': 'WebSocket service instance not found'
                }), 200
            
            return jsonify({
                'status': 'active',
                'active_sessions': len(ws_service.active_sessions),
                'total_connections': ws_service.connection_count,
                'features': {
                    'real_time_blueprints': True,
                    'progress_tracking': True,
                    'multi_user_support': True
                }
            }), 200
            
        except Exception as e:
            logger.error(f"WebSocket status check failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    # User's active WebSocket sessions endpoint
    @app.route('/api/websocket/active-sessions', methods=['GET'])
    def active_sessions():
        """
        Get active WebSocket sessions for the authenticated user.
        
        Returns:
            JSON response with user's active sessions
        """
        try:
            user_id = request.headers.get('X-User-ID')
            if not user_id:
                return jsonify({
                    'error': 'Authentication required',
                    'message': 'X-User-ID header is required'
                }), 401
            
            if not app.websocket_service:
                return jsonify({
                    'active_sessions': [],
                    'count': 0,
                    'message': 'WebSocket service is disabled'
                }), 200
            
            ws_service = get_websocket_service()
            if not ws_service:
                return jsonify({
                    'active_sessions': [],
                    'count': 0,
                    'message': 'WebSocket service unavailable'
                }), 200
            
            # Get user's active sessions
            user_sessions = [
                session_info for session_id, session_info in ws_service.active_sessions.items()
                if session_info.get('user_id') == user_id
            ]
            
            return jsonify({
                'active_sessions': user_sessions,
                'count': len(user_sessions),
                'user_id': user_id
            }), 200
            
        except Exception as e:
            logger.error(f"Active sessions check failed: {str(e)}")
            return jsonify({
                'error': 'Failed to get active sessions',
                'message': str(e)
            }), 500
    
    # Basic API information endpoint
    @app.route('/', methods=['GET'])
    def api_info():
        """
        Basic API information and available endpoints.
        
        Returns:
            JSON response with API information
        """
        return jsonify({
            'name': 'SERP Strategist API',
            'version': '2.1.0',
            'mode': 'realtime',
            'description': 'AI-powered content blueprint generation with real-time WebSocket support and payment integration',
            'features': {
                'blueprint_generation': blueprint_routes is not None,
                'realtime_generation': realtime_blueprint_routes is not None,
                'websocket_support': app.websocket_service is not None,
                'payment_processing': payment_bp is not None,
                'usage_tracking': UsageMiddleware is not None
            },
            'endpoints': {
                'health': '/api/health',
                'websocket_status': '/api/websocket/status',
                'active_sessions': '/api/websocket/active-sessions',
                'blueprints': '/api/blueprints/*' if blueprint_routes else None,
                'realtime_blueprints': '/api/blueprints/generate-realtime' if realtime_blueprint_routes else None,
                'payment': '/api/payment/*' if payment_bp else None,
                'websocket': '/socket.io/' if app.websocket_service else None
            },
            'documentation': 'https://docs.serpstrategist.com'
        }), 200
    
    return app, socketio

# Compatibility wrapper for existing code
def create_app():
    """
    Create Flask app without WebSocket support (compatibility wrapper).
    
    Returns:
        Flask application instance
    """
    app, _ = create_realtime_app()
    return app

if __name__ == '__main__':
    # This allows the file to be run directly for testing
    app, socketio = create_realtime_app()
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting SERP Strategist API server on {host}:{port}")
    logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
    logger.info("WebSocket support: enabled")
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=debug  # Only allow in debug mode
    )