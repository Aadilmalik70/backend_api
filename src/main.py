import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# ============================================================================
# GOOGLE APIS INTEGRATION
# ============================================================================

# Import Google APIs clients
try:
    from src.utils.google_apis.api_manager import google_api_manager
    from src.utils.google_apis.migration_manager import MigrationManager
    from src.utils.google_apis.custom_search_client import CustomSearchClient
    from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
    from src.utils.google_apis.natural_language_client import NaturalLanguageClient
    from src.utils.google_apis.gemini_client import GeminiClient
    from src.utils.google_apis.search_console_client import SearchConsoleClient
    print("✅ Google APIs modules imported successfully")
except ImportError as e:
    print(f"⚠️  Google APIs modules not available: {e}")
    google_api_manager = None
    MigrationManager = None

# Import existing routes
from src.routes.api import api_bp

# Import new blueprint routes
from src.routes.blueprints import blueprint_routes

# Import database setup
from src.models.blueprint import DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all API routes

# ============================================================================
# GOOGLE APIS INITIALIZATION
# ============================================================================

def initialize_google_apis():
    """Initialize Google APIs clients and store in app config"""
    try:
        # Check if Google APIs are enabled
        use_google_apis = os.getenv('USE_GOOGLE_APIS', 'true').lower() == 'true'
        
        if not use_google_apis:
            print("⚠️  Google APIs disabled via USE_GOOGLE_APIS environment variable")
            return False
        
        # Initialize Google APIs clients
        google_apis_clients = {}
        
        # Initialize Custom Search Client
        try:
            custom_search_client = CustomSearchClient()
            if custom_search_client.api_key and custom_search_client.search_engine_id:
                google_apis_clients['custom_search'] = custom_search_client
                print("✅ Custom Search API initialized")
            else:
                print("⚠️  Custom Search API: Missing configuration")
        except Exception as e:
            print(f"❌ Custom Search API initialization failed: {e}")
        
        # Initialize Knowledge Graph Client
        try:
            knowledge_graph_client = KnowledgeGraphClient()
            if knowledge_graph_client.api_key:
                google_apis_clients['knowledge_graph'] = knowledge_graph_client
                print("✅ Knowledge Graph API initialized")
            else:
                print("⚠️  Knowledge Graph API: Missing configuration")
        except Exception as e:
            print(f"❌ Knowledge Graph API initialization failed: {e}")
        
        # Initialize Natural Language Client
        try:
            natural_language_client = NaturalLanguageClient()
            google_apis_clients['natural_language'] = natural_language_client
            print("✅ Natural Language API initialized")
        except Exception as e:
            print(f"❌ Natural Language API initialization failed: {e}")
        
        # Initialize Gemini Client
        try:
            gemini_client = GeminiClient()
            if gemini_client:
                google_apis_clients['gemini'] = gemini_client
                print("✅ Gemini API initialized")
            else:
                print("⚠️  Gemini API: Missing configuration")
        except Exception as e:
            print(f"❌ Gemini API initialization failed: {e}")
        
        # Initialize Search Console Client
        try:
            search_console_client = SearchConsoleClient()
            google_apis_clients['search_console'] = search_console_client
            print("✅ Search Console API initialized")
        except Exception as e:
            print(f"❌ Search Console API initialization failed: {e}")
        
        # Initialize Migration Manager
        try:
            if MigrationManager:
                migration_manager = MigrationManager()
                google_apis_clients['migration_manager'] = migration_manager
                print("✅ Migration Manager initialized")
            else:
                print("⚠️  Migration Manager not available")
        except Exception as e:
            print(f"❌ Migration Manager initialization failed: {e}")
        
        # Store clients in app config
        app.config['GOOGLE_APIS_CLIENTS'] = google_apis_clients
        app.config['GOOGLE_APIS_ENABLED'] = len(google_apis_clients) > 0
        
        print(f"✅ Google APIs initialization complete: {len(google_apis_clients)} clients available")
        return True
        
    except Exception as e:
        print(f"❌ Google APIs initialization failed: {e}")
        app.config['GOOGLE_APIS_CLIENTS'] = {}
        app.config['GOOGLE_APIS_ENABLED'] = False
        return False

# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

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

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

# Initialize Google APIs
google_apis_status = initialize_google_apis()

# Database session management
@app.before_request
def before_request():
    """Create database session before each request"""
    db_manager = app.config.get('DB_MANAGER')
    if db_manager:
        try:
            g.db_session = db_manager.get_session()
            # Also store in current_app for backward compatibility
            app.db_session = g.db_session
        except Exception as e:
            logger.error(f"Failed to create database session: {str(e)}")
            g.db_session = None
            app.db_session = None
    else:
        g.db_session = None
        app.db_session = None

@app.teardown_appcontext
def close_db_session(error):
    """Close database session after each request"""
    db_session = getattr(g, 'db_session', None)
    if db_session:
        try:
            if error:
                db_session.rollback()
            else:
                db_session.commit()
            db_session.close()
        except Exception as e:
            logger.error(f"Database session cleanup error: {str(e)}")
    
    # Clean up app attribute
    if hasattr(app, 'db_session'):
        app.db_session = None

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')  # Legacy API routes
app.register_blueprint(blueprint_routes)  # New blueprint routes (already have /api prefix)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/')
def index():
    google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    return jsonify({
        "status": "online",
        "name": "SERP Strategist API - Enhanced with Google APIs",
        "version": "2.1.0",
        "description": "AI-powered content blueprint generation platform with Google APIs integration",
        "google_apis": {
            "enabled": google_apis_enabled,
            "available_clients": list(google_apis_clients.keys()),
            "total_clients": len(google_apis_clients)
        },
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
            ],
            "google_apis": [
                "/api/google-apis/status",
                "/api/google-apis/health",
                "/api/google-apis/test"
            ]
        },
        "new_features": [
            "Google APIs integration",
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
    google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    return jsonify({
        "api_version": "2.1.0",
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
        "google_apis_integration": {
            "enabled": google_apis_enabled,
            "available_clients": list(google_apis_clients.keys()),
            "migration_status": "active" if 'migration_manager' in google_apis_clients else "inactive"
        },
        "api_configuration": {
            "google_apis_configured": google_apis_enabled,
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

@app.route('/api/google-apis/status', methods=['GET'])
def google_apis_status():
    """Get Google APIs status"""
    google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    status = {
        "google_apis_enabled": google_apis_enabled,
        "clients_available": len(google_apis_clients),
        "clients": {}
    }
    
    for client_name, client in google_apis_clients.items():
        try:
            # Try to get basic info about each client
            if hasattr(client, 'health_check'):
                health = client.health_check()
                status["clients"][client_name] = {
                    "available": True,
                    "healthy": health,
                    "type": type(client).__name__
                }
            else:
                status["clients"][client_name] = {
                    "available": True,
                    "healthy": True,
                    "type": type(client).__name__
                }
        except Exception as e:
            status["clients"][client_name] = {
                "available": False,
                "healthy": False,
                "error": str(e),
                "type": type(client).__name__
            }
    
    return jsonify(status)

@app.route('/api/google-apis/health', methods=['GET'])
def google_apis_health():
    """Health check for Google APIs"""
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    health_status = {
        "overall_status": "healthy",
        "clients": {},
        "timestamp": datetime.now().isoformat()
    }
    
    failed_clients = 0
    
    for client_name, client in google_apis_clients.items():
        try:
            if hasattr(client, 'health_check'):
                health = client.health_check()
                health_status["clients"][client_name] = {
                    "status": "healthy" if health else "unhealthy",
                    "healthy": health
                }
                if not health:
                    failed_clients += 1
            else:
                health_status["clients"][client_name] = {
                    "status": "healthy",
                    "healthy": True
                }
        except Exception as e:
            health_status["clients"][client_name] = {
                "status": "unhealthy",
                "healthy": False,
                "error": str(e)
            }
            failed_clients += 1
    
    if failed_clients > 0:
        health_status["overall_status"] = "degraded" if failed_clients < len(google_apis_clients) else "unhealthy"
    
    return jsonify(health_status)

@app.route('/api/google-apis/test', methods=['GET'])
def google_apis_test():
    """Test Google APIs functionality"""
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "clients_tested": len(google_apis_clients),
        "results": {}
    }
    
    # Test Custom Search
    if 'custom_search' in google_apis_clients:
        try:
            client = google_apis_clients['custom_search']
            result = client.search('test query', num_results=1)
            test_results["results"]["custom_search"] = {
                "status": "success",
                "response_received": bool(result),
                "has_results": bool(result.get('results', []))
            }
        except Exception as e:
            test_results["results"]["custom_search"] = {
                "status": "error",
                "error": str(e)
            }
    
    # Test Knowledge Graph
    if 'knowledge_graph' in google_apis_clients:
        try:
            client = google_apis_clients['knowledge_graph']
            result = client.search_entities('Google')
            test_results["results"]["knowledge_graph"] = {
                "status": "success",
                "response_received": bool(result),
                "has_entities": bool(result.get('entities', []))
            }
        except Exception as e:
            test_results["results"]["knowledge_graph"] = {
                "status": "error",
                "error": str(e)
            }
    
    # Test Natural Language
    if 'natural_language' in google_apis_clients:
        try:
            client = google_apis_clients['natural_language']
            result = client.analyze_content('This is a test sentence.')
            test_results["results"]["natural_language"] = {
                "status": "success",
                "response_received": bool(result),
                "has_entities": bool(result.get('entities', []))
            }
        except Exception as e:
            test_results["results"]["natural_language"] = {
                "status": "error",
                "error": str(e)
            }
    
    # Test Gemini
    if 'gemini' in google_apis_clients:
        try:
            client = google_apis_clients['gemini']
            result = client.analyze_ai_readiness('This is test content for analysis.')
            test_results["results"]["gemini"] = {
                "status": "success",
                "response_received": bool(result),
                "has_analysis": bool(result.get('analysis'))
            }
        except Exception as e:
            test_results["results"]["gemini"] = {
                "status": "error",
                "error": str(e)
            }
    
    return jsonify(test_results)

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
            'google_apis_status': '/api/google-apis/status',
            'google_apis_health': '/api/google-apis/health',
            'google_apis_test': '/api/google-apis/test',
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
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    print("🚀 Starting SERP Strategist API Server...")
    print("📊 Enhanced with Google APIs Integration")
    print("\n🔗 Available Endpoints:")
    print("  • POST /api/blueprints/generate - Generate AI-powered blueprints")
    print("  • GET  /api/blueprints/{id} - Retrieve specific blueprint") 
    print("  • GET  /api/blueprints - List user blueprints")
    print("  • GET  /api/google-apis/status - Google APIs status")
    print("  • GET  /api/google-apis/health - Google APIs health check")
    print("  • GET  /api/google-apis/test - Test Google APIs functionality")
    print("  • GET  /api/health - Service health check")
    print("  • GET  /api/info - Detailed API documentation")
    print("  • GET  /api/debug/db - Database debug information")
    print("  • GET  / - API overview")
    print("\n💡 Quick Test:")
    print("  curl -X POST http://localhost:5000/api/blueprints/generate \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -H 'X-User-ID: test-user' \\")
    print("    -d '{\"keyword\": \"content marketing\"}'")
    print("\n🔧 Google APIs Status:")
    google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
    google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
    
    if google_apis_enabled:
        print(f"  ✅ Google APIs enabled: {len(google_apis_clients)} clients available")
        for client_name in google_apis_clients.keys():
            print(f"    • {client_name}")
    else:
        print("  ⚠️  Google APIs not enabled")
    
    print("\n🔧 Requirements:")
    if not os.getenv('GOOGLE_API_KEY'):
        print("  ⚠️  Set GOOGLE_API_KEY environment variable for Google APIs")
    if not os.getenv('SERPAPI_KEY'):
        print("  ⚠️  Set SERPAPI_KEY environment variable for fallback functionality")
    if not os.getenv('GEMINI_API_KEY'):
        print("  ⚠️  Set GEMINI_API_KEY environment variable for AI features")
    
    print(f"\n📊 Database URL: {database_url}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
