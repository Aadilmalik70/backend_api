from flask import Blueprint, request, jsonify
import sys
import os
from datetime import datetime

# Import enhanced modules - UPDATED TO USE REAL DATA VERSIONS
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal as ContentAnalyzer
from competitor_analysis_real import CompetitorAnalysisReal as InsightGenerator
from keyword_processor_enhanced_real import KeywordProcessorEnhancedReal as KeywordProcessor
from serp_feature_optimizer_real import SerpFeatureOptimizerReal as SerpFeatureOptimizer
from content_performance_predictor import ContentPerformancePredictor
from export_integration import ExportIntegration

api_bp = Blueprint('api', __name__)

# Get API keys from environment
serpapi_key = os.getenv('SERPAPI_KEY') or os.getenv('SERPAPI_API_KEY')  # Support both key names
gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')  # Support both key names
google_ads_credentials = {
    'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
    'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
    'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
    'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
    'login_customer_id': os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
}

# Initialize modules with real API integrations
content_analyzer = ContentAnalyzer(gemini_api_key=gemini_api_key)
insight_generator = InsightGenerator(serpapi_key=serpapi_key, gemini_api_key=gemini_api_key)
keyword_processor = KeywordProcessor(google_ads_credentials=google_ads_credentials)
serp_optimizer = SerpFeatureOptimizer(serpapi_key=serpapi_key)
performance_predictor = ContentPerformancePredictor()
export_integration = ExportIntegration()

@api_bp.route('/process', methods=['POST'])
def process_input():
    """Process user input and generate content strategy"""
    try:
        data = request.json
        input_text = data.get('input', '')
        domain = data.get('domain', '')
        
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400
            
        # Validate API keys
        if not serpapi_key:
            return jsonify({"error": "SerpAPI key not configured. Please set SERPAPI_KEY environment variable."}), 500
        
        if not gemini_api_key:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."}), 500
            
        # Process the input through all modules with proper error handling
        try:
            keyword_data = keyword_processor.process_keywords(input_text)
        except Exception as e:
            print(f"Error processing keywords: {str(e)}")
            return jsonify({"error": f"Keyword processing failed: {str(e)}"}), 500
        
        # Initialize empty data structures for failed components
        serp_data = {'serp_features': {}, 'optimization_opportunities': []}
        competitor_data = {'content_gaps': []}
        
        # Generate content blueprint using new signature
        try:
            content_blueprint = insight_generator.generate_content_blueprint(
                keyword=input_text,  # Note: parameter name change
                num_competitors=20
            )
        except Exception as e:
            print(f"Error generating content blueprint: {str(e)}")
            return jsonify({"error": f"Content blueprint generation failed: {str(e)}"}), 500
        
        # Generate SERP optimization recommendations using new signature
        try:
            optimization_recommendations = serp_optimizer.generate_recommendations(input_text)
        except Exception as e:
            print(f"Error generating optimization recommendations: {str(e)}")
            return jsonify({"error": f"SERP optimization failed: {str(e)}"}), 500
        
        # Generate performance prediction
        try:
            performance_prediction = performance_predictor.predict_performance(
                input_text,
                keyword_data,
                serp_data,
                competitor_data,
                content_blueprint
            )
        except Exception as e:
            print(f"Error generating performance prediction: {str(e)}")
            # Performance prediction is optional, so continue without it
            performance_prediction = {"error": "Performance prediction unavailable"}
        
        # Get available export formats and CMS platforms
        try:
            export_formats = export_integration.get_export_formats()
            cms_platforms = export_integration.get_cms_platforms()
        except Exception as e:
            print(f"Error getting export options: {str(e)}")
            export_formats = []
            cms_platforms = []
        
        # Compile results
        results = {
            "content_blueprint": content_blueprint,
            "keyword_data": keyword_data,
            "optimization_recommendations": optimization_recommendations,
            "performance_prediction": performance_prediction,
            "export_formats": export_formats,
            "cms_platforms": cms_platforms,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error processing input: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze a specific URL for content insights"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
            
        if not gemini_api_key:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."}), 500
            
        # Analyze the URL
        analysis = content_analyzer.analyze_url(url)
        
        return jsonify(analysis)
        
    except Exception as e:
        print(f"Error analyzing URL: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/export', methods=['POST'])
def export_content():
    """Export content in specified format"""
    try:
        data = request.json
        content_type = data.get('content_type', '')
        format_id = data.get('format', '')
        content_data = data.get('content_data', {})
        
        if not all([content_type, format_id, content_data]):
            return jsonify({"error": "Content type, format, and content data are required"}), 400
            
        # Export the content
        result = export_integration.export_data(format=format_id, data=content_data)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error exporting content: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/publish', methods=['POST'])
def publish_to_cms():
    """Publish content to CMS platform"""
    try:
        data = request.json
        content_type = data.get('content_type', '')
        platform = data.get('platform', '')
        content_data = data.get('content_data', {})
        credentials = data.get('credentials', {})
        
        if not all([content_type, platform, content_data, credentials]):
            return jsonify({"error": "Content type, platform, content data, and credentials are required"}), 400
            
        # Publish to CMS
        result = export_integration.publish_to_cms(content_type, platform, content_data, credentials)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error publishing to CMS: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check API key availability
        api_status = {
            "serpapi_configured": bool(serpapi_key),
            "gemini_configured": bool(gemini_api_key),
            "google_ads_configured": all([
                google_ads_credentials.get('developer_token'),
                google_ads_credentials.get('client_id'),
                google_ads_credentials.get('client_secret'),
                google_ads_credentials.get('refresh_token')
            ])
        }
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "api_status": api_status
        })
        
    except Exception as e:
        print(f"Error in health check: {str(e)}")
        return jsonify({"error": f"Health check failed: {str(e)}"}), 500
