"""
Minimal Working Flask Application - Code Consolidation 

This is a minimal working version of the consolidated application that includes
only the essential functionality without the complex import dependencies.

This serves as a stepping stone to the full consolidated application.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_minimal_app():
    """
    Create a minimal working Flask application.
    
    Returns:
        Flask: Basic Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Enable CORS
    CORS(app)
    
    # Root endpoint with API information
    @app.route('/', methods=['GET'])
    def root():
        """
        Root endpoint with API information.
        """
        return jsonify({
            "name": "SERP Strategist API - Minimal",
            "version": "2.0.0-minimal",
            "status": "active",
            "description": "Minimal working version of consolidated application",
            "message": "Code consolidation in progress - this is a minimal working version",
            "endpoints": {
                "health_check": "/api/health",
                "status": "/api/status", 
                "root": "/"
            },
            "note": "Full blueprint generation will be restored after import dependency resolution"
        })
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint.
        """
        # Check environment variables
        google_api_key = os.getenv('GOOGLE_API_KEY')
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        return jsonify({
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "2.0.0-minimal",
            "environment": {
                "google_api_key": "configured" if google_api_key else "missing",
                "gemini_api_key": "configured" if gemini_api_key else "missing"
            },
            "message": "Minimal application running successfully"
        })
    
    # Status endpoint  
    @app.route('/api/status', methods=['GET'])
    def status():
        """
        Status endpoint with system information.
        """
        return jsonify({
            "application": "SERP Strategist API",
            "version": "2.0.0-minimal", 
            "status": "consolidation-in-progress",
            "description": "Minimal working application during code consolidation",
            "architecture": {
                "type": "minimal-flask-app",
                "consolidation_status": "phase-1-complete",
                "import_resolution": "in-progress"
            },
            "capabilities": {
                "health_check": True,
                "status_reporting": True,
                "blueprint_generation": False,
                "google_apis": False
            },
            "next_steps": [
                "Resolve import dependencies in services layer",
                "Restore blueprint generation functionality", 
                "Re-integrate Google APIs",
                "Complete consolidation workflow"
            ]
        })
    
    # Simple test endpoint for blueprint generation (placeholder)
    @app.route('/api/blueprints/test', methods=['POST'])
    def test_blueprint():
        """
        Test endpoint for blueprint generation (minimal implementation).
        """
        try:
            data = request.get_json()
            keyword = data.get('keyword', 'test keyword')
            
            # Minimal response structure
            response = {
                "status": "minimal-implementation",
                "keyword": keyword,
                "message": "This is a minimal test implementation",
                "blueprint": {
                    "title": f"Content Blueprint for '{keyword}'",
                    "sections": [
                        {
                            "title": "Introduction",
                            "content": f"Introduction section for {keyword}"
                        },
                        {
                            "title": "Main Content", 
                            "content": f"Main content section for {keyword}"
                        },
                        {
                            "title": "Conclusion",
                            "content": f"Conclusion section for {keyword}"
                        }
                    ],
                    "metadata": {
                        "word_count": "1000-1500",
                        "difficulty": "medium",
                        "implementation": "minimal"
                    }
                },
                "note": "Full blueprint generation will be restored after import resolution"
            }
            
            return jsonify(response)
            
        except Exception as e:
            logger.error(f"Error in test blueprint endpoint: {str(e)}")
            return jsonify({
                "error": "Test blueprint generation failed",
                "details": str(e),
                "status": "error"
            }), 500
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'available_endpoints': [
                '/',
                '/api/health', 
                '/api/status',
                '/api/blueprints/test'
            ]
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Method not allowed for this endpoint'}), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error occurred'}), 500
    
    logger.info("Minimal Flask application created successfully")
    logger.info("Available endpoints: /, /api/health, /api/status, /api/blueprints/test")
    
    return app

if __name__ == '__main__':
    logger.info("Starting SERP Strategist API server (minimal version)...")
    
    # Create the application
    app = create_minimal_app()
    
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Server starting on {host}:{port}")
    logger.info(f"Debug mode: {'enabled' if debug else 'disabled'}")
    
    # Start the server
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )