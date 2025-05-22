"""
Flask application with Gemini API integration for real data processing.

This module provides a Flask application with endpoints for processing content
using real data sources and Gemini API for NLP tasks.
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import modules
from .keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
from .serp_feature_optimizer_real import SerpFeatureOptimizerReal
from .content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
from .competitor_analysis_real import CompetitorAnalysisReal
from .export_integration import ExportIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)

# Get API keys from environment variables
serpapi_key = os.getenv('SERPAPI_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

# Initialize modules with API keys
keyword_processor = KeywordProcessorEnhancedReal()
serp_optimizer = SerpFeatureOptimizerReal(serpapi_key=serpapi_key)
content_analyzer = ContentAnalyzerEnhancedReal(gemini_api_key=gemini_api_key)
competitor_analyzer = CompetitorAnalysisReal(
    gemini_api_key=gemini_api_key,
    serpapi_key=serpapi_key
)
export_integration = ExportIntegration()

@app.route('/api/process', methods=['POST'])
def process():
    """
    Process content for a keyword and URL.
    
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
        
        logger.info(f"Processing request for keyword: {keyword}, URL: {url}")
        
        # Validate input
        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Process keyword
        keyword_analysis = keyword_processor.process_keywords(keyword)
        
        # Generate SERP feature recommendations
        serp_features = serp_optimizer.generate_recommendations(keyword)
        
        # Analyze content
        content_analysis = content_analyzer.analyze_url(url)
        
        # Analyze competitors
        competitor_analysis = competitor_analyzer.analyze_competitors(keyword, num_competitors=3)
        
        # Compile result
        result = {
            "keyword_analysis": keyword_analysis,
            "serp_features": serp_features,
            "content_analysis": content_analysis,
            "competitor_analysis": competitor_analysis
        }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/blueprint', methods=['POST'])
def blueprint():
    """
    Generate a content blueprint for a keyword.
    
    Request JSON:
    {
        "keyword": "example keyword"
    }
    
    Returns:
    {
        "keyword": "example keyword",
        "outline": {...},
        "recommendations": [...]
    }
    """
    try:
        # Get request data
        data = request.get_json()
        keyword = data.get('keyword')
        
        logger.info(f"Generating blueprint for keyword: {keyword}")
        
        # Validate input
        if not keyword:
            return jsonify({"error": "Keyword is required"}), 400
        
        # Generate content blueprint
        blueprint = competitor_analyzer.generate_content_blueprint(keyword, num_competitors=3)
        
        return jsonify(blueprint)
    
    except Exception as e:
        logger.error(f"Error generating blueprint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export():
    """
    Export analysis results in various formats.
    
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
        
        logger.info(f"Exporting data in format: {export_format}")
        
        # Validate input
        if not export_data:
            return jsonify({"error": "Data is required"}), 400
        
        # Export data
        export_url = export_integration.export_data(export_data, export_format)
        
        return jsonify({"export_url": export_url})
    
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Returns:
    {
        "status": "ok",
        "version": "1.0.0",
        "apis": {
            "serpapi": true|false,
            "gemini": true|false
        }
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
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
