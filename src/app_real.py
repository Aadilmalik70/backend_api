"""
Enhanced Flask application with Blueprint Generator integration.

This module provides a Flask application with enhanced blueprint generation
capabilities using real data sources and AI-powered content structuring.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
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
    from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
    from src.serp_feature_optimizer_real import SerpFeatureOptimizerReal
    from src.content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    from src.competitor_analysis_real import CompetitorAnalysisReal
    from src.export_integration import ExportIntegration
    from src.models.blueprint import DatabaseManager
    from src.routes.blueprints import blueprint_routes
    logger.info("Successfully imported all modules with src.* imports")
except ImportError as e:
    logger.warning(f"src.* imports failed: {e}. Attempting local imports...")
    try:
        # Try local imports (when run from src/ directory)
        from keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
        from serp_feature_optimizer_real import SerpFeatureOptimizerReal
        from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
        from competitor_analysis_real import CompetitorAnalysisReal
        from export_integration import ExportIntegration
        from models.blueprint import DatabaseManager
        from routes.blueprints import blueprint_routes
        logger.info("Successfully imported all modules with local imports")
    except ImportError as local_e:
        logger.warning(f"Local imports failed: {local_e}. Attempting relative imports...")
        try:
            # Try relative imports (when imported as module)
            from .keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
            from .serp_feature_optimizer_real import SerpFeatureOptimizerReal
            from .content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
            from .competitor_analysis_real import CompetitorAnalysisReal
            from .export_integration import ExportIntegration
            from .models.blueprint import DatabaseManager
            from .routes.blueprints import blueprint_routes
            logger.info("Successfully imported all modules with relative imports")
        except ImportError as rel_e:
            logger.error(f"All import strategies failed:")
            logger.error(f"  - src.* imports: {e}")
            logger.error(f"  - Local imports: {local_e}")
            logger.error(f"  - Relative imports: {rel_e}")
            logger.error("Creating minimal application without enhanced features...")
            
            # Import minimal components only
            try:
                from models.blueprint import DatabaseManager
                from routes.blueprints import blueprint_routes
                logger.warning("Using minimal application mode with limited features")
                KeywordProcessorEnhancedReal = None
                SerpFeatureOptimizerReal = None
                ContentAnalyzerEnhancedReal = None
                CompetitorAnalysisReal = None
                ExportIntegration = None
            except ImportError as minimal_e:
                logger.error(f"Even minimal imports failed: {minimal_e}")
                # Create stub classes to prevent application crash
                class StubClass:
                    def __init__(self, *args, **kwargs):
                        pass
                KeywordProcessorEnhancedReal = StubClass
                SerpFeatureOptimizerReal = StubClass
                ContentAnalyzerEnhancedReal = StubClass
                CompetitorAnalysisReal = StubClass
                ExportIntegration = StubClass
                DatabaseManager = None
                blueprint_routes = None

def create_app():
    """
    Application factory function for creating the Flask app.
    
    Returns:
        Flask application instance
    """
    # Create Flask application
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Enable CORS for frontend integration
    CORS(app)
    
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
            logger.info("Blueprint routes registered successfully")
        except Exception as e:
            logger.error(f"Blueprint registration failed: {str(e)}")
    else:
        logger.warning("Blueprint routes not available, skipping registration")
    
    # Get API keys from environment variables
    serpapi_key = os.getenv('SERPAPI_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    # Initialize legacy modules (for backward compatibility)
    modules_available = all([
        KeywordProcessorEnhancedReal is not None,
        SerpFeatureOptimizerReal is not None,
        ContentAnalyzerEnhancedReal is not None,
        CompetitorAnalysisReal is not None,
        ExportIntegration is not None
    ])
    
    if modules_available:
        try:
            keyword_processor = KeywordProcessorEnhancedReal()
            serp_optimizer = SerpFeatureOptimizerReal(serpapi_key=serpapi_key)
            content_analyzer = ContentAnalyzerEnhancedReal(gemini_api_key=gemini_api_key)
            competitor_analyzer = CompetitorAnalysisReal(
                gemini_api_key=gemini_api_key,
                serpapi_key=serpapi_key
            )
            export_integration = ExportIntegration()
            
            # Store in app context for legacy routes
            app.keyword_processor = keyword_processor
            app.serp_optimizer = serp_optimizer
            app.content_analyzer = content_analyzer
            app.competitor_analyzer = competitor_analyzer
            app.export_integration = export_integration
            app.enhanced_features_available = True
            
            logger.info("✅ Legacy modules initialized successfully - Enhanced features available")
            
        except Exception as e:
            logger.error(f"Legacy module initialization failed: {str(e)}")
            app.enhanced_features_available = False
    else:
        logger.warning("⚠️ Some modules unavailable - Running in limited mode")
        app.keyword_processor = None
        app.serp_optimizer = None
        app.content_analyzer = None
        app.competitor_analyzer = None
        app.export_integration = None
        app.enhanced_features_available = False
    
    # Legacy API routes (maintained for backward compatibility)
    @app.route('/api/process', methods=['POST'])
    def process():
        """
        Legacy endpoint: Process content for a keyword and URL.
        
        Request JSON:
        {
            "keyword": "example keyword",
            "url": "https://example.com"
        }
        
        Returns:
        {
            "keyword_analysis": {...},
            "serp_features": {...},
            "content_analysis": {...},
            "competitor_analysis": {...}
        }
        """
        try:
            # Check if enhanced features are available
            if not getattr(app, 'enhanced_features_available', False):
                return jsonify({
                    "error": "Enhanced features not available",
                    "message": "Application is running in limited mode due to import issues",
                    "suggestion": "Check logs for import errors and ensure all dependencies are installed"
                }), 503
            
            # Get request data
            data = request.get_json()
            keyword = data.get('keyword')
            url = data.get('url')
            
            logger.info(f"Processing legacy request for keyword: {keyword}, URL: {url}")
            
            # Validate input
            if not keyword:
                return jsonify({"error": "Keyword is required"}), 400
            
            if not url:
                return jsonify({"error": "URL is required"}), 400
            
            # Process using legacy modules
            keyword_analysis = app.keyword_processor.process_keywords(keyword)
            serp_features = app.serp_optimizer.generate_recommendations(keyword)
            content_analysis = app.content_analyzer.analyze_url(url)
            competitor_analysis = app.competitor_analyzer.analyze_competitors(keyword, num_competitors=3)
            
            # Compile result
            result = {
                "keyword_analysis": keyword_analysis,
                "serp_features": serp_features,
                "content_analysis": content_analysis,
                "competitor_analysis": competitor_analysis
            }
            
            return jsonify(result)
        
        except Exception as e:
            logger.error(f"Error processing legacy request: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/blueprint', methods=['POST'])
    def legacy_blueprint():
        """
        Legacy endpoint: Generate a content blueprint for a keyword.
        
        Note: This endpoint is deprecated. Use /api/blueprints/generate instead.
        
        Request JSON:
        {
            "keyword": "example keyword"
        }
        
        Returns:
        {
            "keyword": "example keyword",
            "outline": {...},
            "recommendations": [...],
            "deprecated": true,
            "new_endpoint": "/api/blueprints/generate"
        }
        """
        try:
            # Get request data
            data = request.get_json()
            keyword = data.get('keyword')
            
            logger.info(f"Processing legacy blueprint request for keyword: {keyword}")
            
            # Validate input
            if not keyword:
                return jsonify({"error": "Keyword is required"}), 400
            
            # Generate content blueprint using legacy method
            blueprint = app.competitor_analyzer.generate_content_blueprint(keyword, num_competitors=3)
            
            # Add deprecation notice
            blueprint['deprecated'] = True
            blueprint['new_endpoint'] = '/api/blueprints/generate'
            blueprint['message'] = 'This endpoint is deprecated. Please use /api/blueprints/generate for enhanced features.'
            
            return jsonify(blueprint)
        
        except Exception as e:
            logger.error(f"Error generating legacy blueprint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/export', methods=['POST'])
    def export():
        """
        Legacy endpoint: Export analysis results in various formats.
        
        Request JSON:
        {
            "data": {...},
            "format": "pdf|csv|json"
        }
        
        Returns:
        {
            "export_url": "path/to/exported/file"
        }
        """
        try:
            # Get request data
            data = request.get_json()
            export_data = data.get('data')
            export_format = data.get('format', 'pdf')
            
            logger.info(f"Processing legacy export request in format: {export_format}")
            
            # Validate input
            if not export_data:
                return jsonify({"error": "Data is required"}), 400
            
            # Export data using legacy integration
            export_url = app.export_integration.export_data(export_data, export_format)
            
            return jsonify({"export_url": export_url})
        
        except Exception as e:
            logger.error(f"Error processing legacy export: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/health/legacy', methods=['GET'])
    def legacy_health():
        """
        Legacy health check endpoint.
        
        Returns:
        {
            "status": "ok",
            "version": "1.0.0",
            "apis": {
                "serpapi": true|false,
                "gemini": true|false
            },
            "deprecated": true
        }
        """
        # Check API availability
        serpapi_available = serpapi_key is not None
        gemini_available = gemini_api_key is not None
        
        return jsonify({
            "status": "ok",
            "version": "1.0.0",
            "apis": {
                "serpapi": serpapi_available,
                "gemini": gemini_available
            },
            "deprecated": True,
            "new_endpoint": "/api/health",
            "message": "Use /api/health for the enhanced health check"
        })
    
    # Main health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Main health check endpoint.
        
        Returns:
        {
            "status": "ok|degraded|error",
            "version": "2.0.0",
            "features": {...},
            "services": {...}
        }
        """
        # Determine overall status
        enhanced_available = getattr(app, 'enhanced_features_available', False)
        db_available = app.db_session is not None
        
        if enhanced_available and db_available:
            status = "ok"
        elif enhanced_available or db_available:
            status = "degraded"
        else:
            status = "error"
        
        return jsonify({
            "status": status,
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "enhanced_processing": enhanced_available,
                "database": db_available,
                "blueprint_routes": blueprint_routes is not None
            },
            "services": {
                "keyword_processor": app.keyword_processor is not None,
                "serp_optimizer": app.serp_optimizer is not None,
                "content_analyzer": app.content_analyzer is not None,
                "competitor_analyzer": app.competitor_analyzer is not None,
                "export_integration": app.export_integration is not None
            },
            "api_keys": {
                "serpapi": serpapi_key is not None,
                "gemini": gemini_api_key is not None,
                "google_api": os.getenv('GOOGLE_API_KEY') is not None
            }
        })
    
    # Enhanced root endpoint with API information
    @app.route('/', methods=['GET'])
    def root():
        """
        Root endpoint with API information.
        
        Returns:
        {
            "name": "SERP Strategist API",
            "version": "2.0.0",
            "status": "active",
            "endpoints": {...}
        }
        """
        return jsonify({
            "name": "SERP Strategist API",
            "version": "2.0.0",
            "status": "active",
            "description": "AI-powered content blueprint generation platform",
            "endpoints": {
                "blueprint_generation": "/api/blueprints/generate",
                "blueprint_retrieval": "/api/blueprints/{id}",
                "blueprint_listing": "/api/blueprints",
                "health_check": "/api/health",
                "user_statistics": "/api/user/stats"
            },
            "legacy_endpoints": {
                "process": "/api/process",
                "blueprint": "/api/blueprint (deprecated)",
                "export": "/api/export",
                "health": "/api/health/legacy (deprecated)"
            },
            "documentation": {
                "api_guide": "See README.md for API usage examples",
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
                '/api/blueprints/generate',
                '/api/blueprints',
                '/api/health',
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
        if hasattr(app, 'db_session'):
            app.db_session.close()
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    logger.info("Starting SERP Strategist API server...")
    logger.info("Enhanced blueprint generation endpoints available:")
    logger.info("  POST /api/blueprints/generate - Generate new blueprint")
    logger.info("  GET  /api/blueprints/{id} - Get specific blueprint")
    logger.info("  GET  /api/blueprints - List user blueprints")
    logger.info("  GET  /api/health - API health check")
    logger.info("  GET  /api/user/stats - User statistics")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
