import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing routes
from src.routes.api import api_bp

# Import new blueprint routes
from src.routes.blueprints import blueprint_routes

# Import database setup
from src.models.blueprint import DatabaseManager

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all API routes

# Database setup for blueprints
database_url = os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
print(f"📊 Initializing database: {database_url}")

try:
    db_manager = DatabaseManager(database_url)
    db_manager.init_tables()
    print("✅ Database tables initialized successfully")
    
    # Store db_manager in app config for later use
    app.config['DB_MANAGER'] = db_manager
    
except Exception as e:
    print(f"⚠️  Database initialization failed: {str(e)}")
    app.config['DB_MANAGER'] = None

# Database session management
@app.before_request
def before_request():
    """Create database session before each request"""
    db_manager = app.config.get('DB_MANAGER')
    if db_manager:
        g.db_session = db_manager.get_session()
        # Also store in current_app for backward compatibility
        app.db_session = g.db_session
    else:
        g.db_session = None
        app.db_session = None

@app.teardown_appcontext
def close_db_session(error):
    """Close database session after each request"""
    db_session = getattr(g, 'db_session', None)
    if db_session:
        db_session.close()
    
    # Clean up app attribute
    if hasattr(app, 'db_session'):
        app.db_session = None

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')  # Legacy API routes
app.register_blueprint(blueprint_routes)  # New blueprint routes (already have /api prefix)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "name": "SERP Strategist API - Enhanced with Blueprint Generator",
        "version": "2.0.0",
        "description": "AI-powered content blueprint generation platform",
        "endpoints": {
            "legacy_api": [
                "/api/process",
                "/api/analyze-url", 
                "/api/export",
                "/api/publish",
                "/api/health"
            ],
            "blueprint_api": [
                "/api/blueprints/generate",
                "/api/blueprints/{id}",
                "/api/blueprints",
                "/api/user/stats"
            ]
        },
        "new_features": [
            "AI-powered blueprint generation",
            "Competitor analysis integration",
            "Database storage for blueprints",
            "Enhanced content structuring"
        ],
        "getting_started": {
            "generate_blueprint": "POST /api/blueprints/generate",
            "required_headers": "X-User-ID: your-user-id",
            "example_payload": {"keyword": "content marketing"}
        }
    })

@app.route('/api/info', methods=['GET'])
def api_info():
    """Detailed API information endpoint"""
    db_status = app.config.get('DB_MANAGER') is not None
    
    return jsonify({
        "api_version": "2.0.0",
        "blueprint_generator": {
            "status": "active",
            "features": [
                "Real-time competitor analysis",
                "AI-powered content structure",
                "SERP feature optimization", 
                "Topic clustering",
                "Database persistence"
            ]
        },
        "api_configuration": {
            "serpapi_configured": bool(os.getenv('SERPAPI_KEY')),
            "gemini_configured": bool(os.getenv('GEMINI_API_KEY')),
            "database_connected": db_status
        },
        "usage_examples": {
            "generate_blueprint": {
                "method": "POST",
                "endpoint": "/api/blueprints/generate",
                "headers": {"X-User-ID": "your-user-id", "Content-Type": "application/json"},
                "body": {"keyword": "content marketing", "project_id": "optional"}
            },
            "get_blueprint": {
                "method": "GET", 
                "endpoint": "/api/blueprints/{blueprint_id}",
                "headers": {"X-User-ID": "your-user-id"}
            },
            "list_blueprints": {
                "method": "GET",
                "endpoint": "/api/blueprints?limit=20",
                "headers": {"X-User-ID": "your-user-id"}
            }
        }
    })

@app.route('/api/debug/db', methods=['GET'])
def debug_database():
    """Debug endpoint to check database status"""
    try:
        db_manager = app.config.get('DB_MANAGER')
        has_session = hasattr(app, 'db_session') and app.db_session is not None
        g_session = hasattr(g, 'db_session') and g.db_session is not None
        
        return jsonify({
            "database_manager_available": db_manager is not None,
            "app_db_session_available": has_session,
            "g_db_session_available": g_session,
            "database_url": os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db'),
            "config_keys": list(app.config.keys())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Global error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': {
            'blueprint_generation': '/api/blueprints/generate',
            'blueprint_retrieval': '/api/blueprints/{id}',
            'blueprint_listing': '/api/blueprints',
            'api_info': '/api/info',
            'health_check': '/api/health',
            'database_debug': '/api/debug/db'
        },
        'tip': 'Check /api/info for detailed endpoint documentation'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed for this endpoint'}), 405

@app.errorhandler(500)
def internal_error(error):
    print(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    print("🚀 Starting SERP Strategist API Server...")
    print("📊 Enhanced with Blueprint Generator functionality")
    print("\n🔗 Available Endpoints:")
    print("  • POST /api/blueprints/generate - Generate AI-powered blueprints")
    print("  • GET  /api/blueprints/{id} - Retrieve specific blueprint") 
    print("  • GET  /api/blueprints - List user blueprints")
    print("  • GET  /api/health - Service health check")
    print("  • GET  /api/info - Detailed API documentation")
    print("  • GET  /api/debug/db - Database debug information")
    print("  • GET  / - API overview")
    print("\n💡 Quick Test:")
    print("  curl -X POST http://localhost:5000/api/blueprints/generate \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -H 'X-User-ID: test-user' \\")
    print("    -d '{\"keyword\": \"content marketing\"}'")
    print("\n🔧 Requirements:")
    if not os.getenv('SERPAPI_KEY'):
        print("  ⚠️  Set SERPAPI_KEY environment variable for full functionality")
    if not os.getenv('GEMINI_API_KEY'):
        print("  ⚠️  Set GEMINI_API_KEY environment variable for AI features")
    
    print(f"\n📊 Database URL: {database_url}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
