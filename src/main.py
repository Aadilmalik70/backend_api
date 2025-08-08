#!/usr/bin/env python3
"""
Main Application Entry Point - SERP Strategist API with WebSocket Support

Single entry point for the consolidated Flask application with optional WebSocket support.
Uses the production-ready app_real.py as fallback and app_realtime.py for full features.

This replaces the previous fragmented architecture:
- app.py (legacy, non-functional)
- app_enhanced.py (enhanced features, non-functional)  
- app_real.py (production, functional) -> INTEGRATED
- app_realtime.py (with WebSocket support) -> NEW

Author: Code Consolidation Workflow + WebSocket Integration
Version: 2.1.0
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import the working application factory
# First try the full realtime app, fallback to regular app
try:
    from app_realtime import create_realtime_app, create_app as create_realtime_app_compat
    print("Successfully imported realtime application factory from app_realtime.py")
    APP_MODE = "realtime"
    create_app = create_realtime_app_compat  # Compatibility wrapper
    create_full_app = create_realtime_app    # Full app with socketio
except ImportError as e:
    print(f"Realtime app import failed ({e}), trying regular app...")
    try:
        from app_real import create_app
        print("Successfully imported regular application factory from app_real.py")
        APP_MODE = "regular"
        create_full_app = lambda: (create_app(), None)  # No socketio
    except ImportError as regular_e:
        print(f"Regular app import failed ({regular_e}), using minimal application...")
        try:
            from app_minimal import create_minimal_app as create_app
            print("Successfully imported minimal application factory")
            APP_MODE = "minimal"
            create_full_app = lambda: (create_app(), None)  # No socketio
        except ImportError as minimal_e:
            print(f"All app imports failed: realtime={e}, regular={regular_e}, minimal={minimal_e}")
            print("Ensure application files are available and dependencies are installed")
            sys.exit(1)

# Configure logging for main entry point
def setup_main_logging():
    """Configure logging for the main application entry point."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('serp_strategist.log', encoding='utf-8')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Main application logging configured at {log_level} level")
    return logger

def validate_environment():
    """
    Validate critical environment variables and configuration.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    logger = logging.getLogger(__name__)
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google API key for Custom Search and other services',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Custom Search Engine ID',
        'GEMINI_API_KEY': 'Google Gemini API key for AI features'
    }
    
    optional_vars = {
        'SERPAPI_KEY': 'SerpAPI key for fallback search functionality'
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"{var} ({description})")
    
    for var, description in optional_vars.items():
        if not os.getenv(var):
            missing_optional.append(f"{var} ({description})")
    
    if missing_required:
        logger.warning("Missing required environment variables:")
        for var in missing_required:
            logger.warning(f"  - {var}")
        logger.warning("Application may have limited functionality")
    
    if missing_optional:
        logger.info("Missing optional environment variables:")
        for var in missing_optional:
            logger.info(f"  - {var}")
    
    if not missing_required:
        logger.info("✅ All required environment variables are configured")
        return True
    
    return False

def create_application():
    """
    Create and configure the Flask application with optional WebSocket support.
    
    Returns:
        Tuple: (Flask app, SocketIO instance or None)
    """
    logger = logging.getLogger(__name__)
    
    # Validate environment
    env_valid = validate_environment()
    
    try:
        # Create the application using the factory pattern
        if APP_MODE == "realtime":
            app, socketio = create_full_app()
            logger.info(f"✅ Flask application with WebSocket support created successfully")
        else:
            app, socketio = create_full_app()
            logger.info(f"✅ Flask application created successfully (mode: {APP_MODE})")
        
        logger.info("🚀 SERP Strategist API is ready to serve requests")
        
        # Log available endpoints based on mode
        logger.info("📋 Available API endpoints:")
        if APP_MODE == "realtime":
            logger.info("  Realtime Blueprint Generation:")
            logger.info("    POST /api/blueprints/generate-realtime - Generate with WebSocket updates")
            logger.info("    POST /api/blueprints/generate-quick-realtime - Quick generation with updates")
            logger.info("    GET  /api/blueprints/{id}/status - Real-time status checking")
            logger.info("    GET  /api/websocket/active-sessions - User's active sessions")
            logger.info("  Standard Blueprint Generation:")
            logger.info("    POST /api/blueprints/generate - Standard blueprint generation")
            logger.info("    GET  /api/blueprints/{id} - Retrieve specific blueprint")
            logger.info("    GET  /api/blueprints - List user blueprints")
            logger.info("  WebSocket Support:")
            logger.info("    WS   /socket.io/ - WebSocket connection endpoint")
            logger.info("    GET  /api/websocket/status - WebSocket service status")
        elif APP_MODE == "regular":
            logger.info("  Blueprint Generation:")
            logger.info("    POST /api/blueprints/generate - Generate content blueprint")
            logger.info("    GET  /api/blueprints/{id} - Retrieve specific blueprint")
            logger.info("    GET  /api/blueprints - List user blueprints")
        elif APP_MODE == "minimal":
            logger.info("  Minimal Implementation:")
            logger.info("    POST /api/blueprints/test - Test blueprint generation")
            logger.info("    ⚠️  Full blueprint features being restored...")
        
        logger.info("  System Endpoints:")
        logger.info("    GET  /api/health - Health check and status")
        logger.info("    GET  /api/status - System status")
        logger.info("    GET  / - API information and documentation")
        
        if APP_MODE == "realtime":
            logger.info("  WebSocket Events:")
            logger.info("    connect/disconnect - Connection management")
            logger.info("    join_blueprint_room - Join blueprint progress room")
            logger.info("    leave_blueprint_room - Leave blueprint progress room")
            logger.info("    progress_update - Real-time progress notifications")
            logger.info("    step_completed - Step completion notifications")
            logger.info("    generation_complete - Blueprint completion notifications")
            logger.info("    generation_failed - Blueprint failure notifications")
        
        if not env_valid:
            logger.warning("⚠️  Application started with missing environment variables")
            logger.warning("   Some features may not work correctly")
        
        return app, socketio
        
    except Exception as e:
        logger.error(f"❌ Failed to create Flask application: {str(e)}")
        logger.error("💡 Check that all dependencies are installed and configured")
        raise

if __name__ == '__main__':
    # Setup logging
    logger = setup_main_logging()
    logger.info("🚀 Starting SERP Strategist API server...")
    logger.info(f"📦 Consolidated Application Architecture v2.1.0 (mode: {APP_MODE})")
    
    try:
        # Create the application
        app, socketio = create_application()
        
        # Get configuration from environment
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Server starting on {host}:{port}")
        logger.info(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
        logger.info(f"🔌 WebSocket support: {'enabled' if APP_MODE == 'realtime' else 'disabled'}")
        
        # Start the server
        if APP_MODE == "realtime" and socketio:
            logger.info("🔄 Starting server with WebSocket support...")
            socketio.run(
                app,
                host=host,
                port=port,
                debug=debug,
                allow_unsafe_werkzeug=debug  # Only allow in debug mode
            )
        else:
            logger.info("🔄 Starting standard Flask server...")
            app.run(
                host=host,
                port=port,
                debug=debug,
                threaded=True
            )
        
    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Server startup failed: {str(e)}")
        logger.error("🔍 Check logs above for configuration issues")
        sys.exit(1)
    finally:
        logger.info("👋 SERP Strategist API server stopped")