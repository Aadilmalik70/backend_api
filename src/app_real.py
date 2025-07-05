"""
Enhanced Flask application with Blueprint Generator integration.

This module provides a Flask application with enhanced blueprint generation
capabilities using real data sources and AI-powered content structuring.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import existing modules
from .keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
from .serp_feature_optimizer_real import SerpFeatureOptimizerReal
from .content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
from .competitor_analysis_real import CompetitorAnalysisReal
from .export_integration import ExportIntegration

# Import new blueprint modules
from .models.blueprint import DatabaseManager
from .routes.blueprints import blueprint_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    CORS(app, origins=["http://localhost:3000"])
    
    # Database setup
    database_url = os.getenv('DATABASE_URL', 'sqlite:///serp_strategist.db')
    db_manager = DatabaseManager(database_url)
    
    try:
        db_manager.init_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    # Add database session to app context
    app.db_session = db_manager.get_session()
    
    # Register blueprint routes
    app.register_blueprint(blueprint_routes)
    
    # Get API keys from environment variables
    serpapi_key = os.getenv('SERPAPI_KEY')
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    # Initialize legacy modules (for backward compatibility)
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
        
        logger.info("Legacy modules initialized successfully")
        
    except Exception as e:
        logger.error(f"Legacy module initialization failed: {str(e)}")
    
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
