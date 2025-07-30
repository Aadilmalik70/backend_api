#!/usr/bin/env python3
"""
Main Application Entry Point - SERP Strategist API

Single entry point for the consolidated Flask application.
Uses the production-ready app_real.py factory pattern as the foundation.

This replaces the previous fragmented architecture:
- app.py (legacy, non-functional)
- app_enhanced.py (enhanced features, non-functional)  
- app_real.py (production, functional) -> NOW INTEGRATED

Author: Code Consolidation Workflow
Version: 2.0.0
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import the working application factory
# First try the full app_real.py, fallback to minimal version
try:
    from app_real import create_app
    print("Successfully imported full application factory from app_real.py")
    APP_MODE = "full"
except ImportError as e:
    print(f"Full app import failed ({e}), using minimal application...")
    try:
        from app_minimal import create_minimal_app as create_app
        print("Successfully imported minimal application factory")
        APP_MODE = "minimal"
    except ImportError as minimal_e:
        print(f"Both full and minimal app imports failed: {e}, {minimal_e}")
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
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.warning("Missing environment variables:")
        for var in missing_vars:
            logger.warning(f"  - {var}")
        logger.warning("Application may have limited functionality")
        return False
    
    logger.info("✅ All required environment variables are configured")
    return True

def create_application():
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    logger = logging.getLogger(__name__)
    
    # Validate environment
    env_valid = validate_environment()
    
    try:
        # Create the application using the factory pattern
        app = create_app()
        
        logger.info(f"✅ Flask application created successfully (mode: {APP_MODE})")
        logger.info("🚀 SERP Strategist API is ready to serve requests")
        
        # Log available endpoints based on mode
        logger.info("📋 Available API endpoints:")
        if APP_MODE == "full":
            logger.info("  Blueprint Generation:")
            logger.info("    POST /api/blueprints/generate - Generate content blueprint")
            logger.info("    GET  /api/blueprints/{id} - Retrieve specific blueprint")
            logger.info("    GET  /api/blueprints - List user blueprints")
            logger.info("  Enhanced Features (v3):")
            logger.info("    POST /api/v3/blueprints/generate - Next-generation blueprint")
            logger.info("    POST /api/v3/blueprints/batch - Batch processing")
        elif APP_MODE == "minimal":
            logger.info("  Minimal Implementation:")
            logger.info("    POST /api/blueprints/test - Test blueprint generation")
            logger.info("    ⚠️  Full blueprint features being restored...")
        
        logger.info("  System Endpoints:")
        logger.info("    GET  /api/health - Health check and status")
        logger.info("    GET  /api/status - System status")
        logger.info("    GET  / - API information and documentation")
        
        if not env_valid:
            logger.warning("⚠️  Application started with missing environment variables")
            logger.warning("   Some features may not work correctly")
        
        return app
        
    except Exception as e:
        logger.error(f"❌ Failed to create Flask application: {str(e)}")
        logger.error("💡 Check that all dependencies are installed and configured")
        raise

if __name__ == '__main__':
    # Setup logging
    logger = setup_main_logging()
    logger.info("🚀 Starting SERP Strategist API server...")
    logger.info("📦 Consolidated Application Architecture v2.0.0")
    
    try:
        # Create the application
        app = create_application()
        
        # Get configuration from environment
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Server starting on {host}:{port}")
        logger.info(f"🔧 Debug mode: {'enabled' if debug else 'disabled'}")
        
        # Start the server
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