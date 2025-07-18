from flask import Blueprint, request, jsonify, current_app
import sys
import os
from datetime import datetime

# Import enhanced modules - UPDATED TO USE GOOGLE APIS
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal as ContentAnalyzer
from competitor_analysis_real import CompetitorAnalysisReal as InsightGenerator
from keyword_processor_enhanced_real import KeywordProcessorEnhancedReal as KeywordProcessor
from serp_feature_optimizer_real import SerpFeatureOptimizerReal as SerpFeatureOptimizer
from content_performance_predictor import ContentPerformancePredictor
from export_integration import ExportIntegration
from services.blueprint_generator import BlueprintGeneratorService

# Import Google APIs Migration Manager
try:
    from utils.google_apis.migration_manager import MigrationManager
    from utils.google_apis.custom_search_client import CustomSearchClient
    from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
    from utils.google_apis.natural_language_client import NaturalLanguageClient
    from utils.google_apis.gemini_client import GeminiClient
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False
    print("⚠️  Google APIs not available, using fallback")

api_bp = Blueprint('api', __name__)

def get_google_apis_clients():
    """Get Google APIs clients from app config"""
    return current_app.config.get('GOOGLE_APIS_CLIENTS', {})

def is_google_apis_enabled():
    """Check if Google APIs are enabled"""
    return current_app.config.get('GOOGLE_APIS_ENABLED', False)

def get_migration_manager():
    """Get migration manager for seamless API transition"""
    google_apis_clients = get_google_apis_clients()
    return google_apis_clients.get('migration_manager')

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
    """Process user input and generate content strategy with Google APIs integration"""
    try:
        data = request.json
        input_text = data.get('input', '')
        domain = data.get('domain', '')
        
        if not input_text:
            return jsonify({"error": "Input text is required"}), 400
        
        # Check if Google APIs are enabled
        google_apis_enabled = is_google_apis_enabled()
        migration_manager = get_migration_manager()
        
        if google_apis_enabled and migration_manager:
            print("🚀 Using Google APIs for enhanced processing")
            return process_with_google_apis(input_text, domain, migration_manager)
        else:
            print("⚠️  Using fallback processing with SerpAPI")
            return process_with_fallback(input_text, domain)
            
    except Exception as e:
        print(f"❌ Error in process_input: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

def process_with_google_apis(input_text, domain, migration_manager):
    """Process input using Google APIs"""
    try:
        # Use Migration Manager for seamless processing
        results = {
            "input": input_text,
            "domain": domain,
            "processing_method": "google_apis",
            "timestamp": datetime.now().isoformat()
        }
        
        # SERP Analysis using Google Custom Search
        try:
            serp_data = migration_manager.get_serp_data(input_text)
            results["serp_analysis"] = serp_data
            print("✅ SERP analysis completed with Google APIs")
        except Exception as e:
            print(f"⚠️  SERP analysis failed: {e}")
            results["serp_analysis"] = {"error": str(e)}
        
        # Content Analysis using Google Natural Language API
        try:
            content_analysis = migration_manager.analyze_content(
                f"Content analysis for keyword: {input_text}"
            )
            results["content_analysis"] = content_analysis
            print("✅ Content analysis completed with Google APIs")
        except Exception as e:
            print(f"⚠️  Content analysis failed: {e}")
            results["content_analysis"] = {"error": str(e)}
        
        # Entity Analysis using Knowledge Graph
        try:
            entity_analysis = migration_manager.verify_entities([input_text])
            results["entity_analysis"] = entity_analysis
            print("✅ Entity analysis completed with Google APIs")
        except Exception as e:
            print(f"⚠️  Entity analysis failed: {e}")
            results["entity_analysis"] = {"error": str(e)}
        
        # Competitor Analysis using Google APIs
        try:
            competitor_analysis = migration_manager.get_competitors_analysis(input_text)
            results["competitor_analysis"] = competitor_analysis
            print("✅ Competitor analysis completed with Google APIs")
        except Exception as e:
            print(f"⚠️  Competitor analysis failed: {e}")
            results["competitor_analysis"] = {"error": str(e)}
        
        # SERP Feature Optimization using Google APIs
        try:
            serp_optimization = migration_manager.optimize_serp_features(input_text)
            results["serp_optimization"] = serp_optimization
            print("✅ SERP optimization completed with Google APIs")
        except Exception as e:
            print(f"⚠️  SERP optimization failed: {e}")
            results["serp_optimization"] = {"error": str(e)}
        
        # Content Blueprint Generation using Google APIs
        try:
            # Use BlueprintGeneratorService for content blueprint generation
            blueprint_service = BlueprintGeneratorService(
                serpapi_key=serpapi_key,
                gemini_api_key=gemini_api_key
            )
            # Use a fallback user_id if not available
            user_id = "unknown_user"
            competitors = results.get("competitor_analysis")
            content_blueprint = blueprint_service.generate_blueprint(
                keyword=input_text,
                user_id=user_id,
                competitors=competitors if competitors and not competitors.get("error") else None
            )
            results["content_blueprint"] = content_blueprint
            print("✅ Content blueprint completed with BlueprintGeneratorService")
        except Exception as e:
            print(f"⚠️  Content blueprint failed: {e}")
            results["content_blueprint"] = {"error": str(e)}
        
        # Keyword Processing (keep existing Google Ads integration)
        try:
            keyword_data = keyword_processor.process_keywords(input_text)
            results["keyword_data"] = keyword_data
            print("✅ Keyword processing completed")
        except Exception as e:
            print(f"⚠️  Keyword processing failed: {e}")
            results["keyword_data"] = {"error": str(e)}
        
        # Performance Prediction
        try:
            performance_prediction = performance_predictor.predict_performance(
                input_text,
                results.get("keyword_data", {}),
                results.get("serp_analysis", {}),
                results.get("content_analysis", {}),
                results.get("entity_analysis", {})
            )
            results["performance_prediction"] = performance_prediction
            print("✅ Performance prediction completed")
        except Exception as e:
            print(f"⚠️  Performance prediction failed: {e}")
            results["performance_prediction"] = {"error": str(e)}
        
        # Export Integration
        try:
            export_formats = export_integration.get_export_formats()
            cms_platforms = export_integration.get_cms_platforms()
            results["export_options"] = {
                "formats": export_formats,
                "cms_platforms": cms_platforms
            }
            print("✅ Export options loaded")
        except Exception as e:
            print(f"⚠️  Export options failed: {e}")
            results["export_options"] = {"error": str(e)}
        
        # Add Google APIs specific metadata
        results["google_apis_status"] = {
            "enabled": True,
            "apis_used": [
                "Custom Search API",
                "Knowledge Graph API", 
                "Natural Language API",
                "Google Ads API"
            ],
            "fallback_available": bool(serpapi_key)
        }
        
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ Google APIs processing failed: {e}")
        # Fallback to SerpAPI if Google APIs fail
        return process_with_fallback(input_text, domain)

def process_with_fallback(input_text, domain):
    """Process input using fallback APIs (SerpAPI)"""
    try:
        # Validate API keys
        if not serpapi_key:
            return jsonify({"error": "SerpAPI key not configured. Please set SERPAPI_KEY environment variable."}), 500
        
        if not gemini_api_key:
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."}), 500
        
        results = {
            "input": input_text,
            "domain": domain,
            "processing_method": "fallback_apis",
            "timestamp": datetime.now().isoformat()
        }
        
        # Process the input through all modules with proper error handling
        try:
            keyword_data = keyword_processor.process_keywords(input_text)
            results["keyword_data"] = keyword_data
        except Exception as e:
            print(f"Error processing keywords: {str(e)}")
            results["keyword_data"] = {"error": str(e)}
        
        # Initialize empty data structures for failed components
        serp_data = {'serp_features': {}, 'optimization_opportunities': []}
        competitor_data = {'content_gaps': []}
        
        # Generate content blueprint using new signature
        try:
            content_blueprint = insight_generator.generate_content_blueprint(
                keyword=input_text,  # Note: parameter name change
                num_competitors=20
            )
            results["content_blueprint"] = content_blueprint
        except Exception as e:
            print(f"Error generating content blueprint: {str(e)}")
            results["content_blueprint"] = {"error": str(e)}
        
        # Generate SERP optimization recommendations using new signature
        try:
            optimization_recommendations = serp_optimizer.generate_recommendations(input_text)
            results["serp_optimization"] = optimization_recommendations
        except Exception as e:
            print(f"Error generating optimization recommendations: {str(e)}")
            results["serp_optimization"] = {"error": str(e)}
        
        # Generate performance prediction
        try:
            performance_prediction = performance_predictor.predict_performance(
                input_text,
                results.get("keyword_data", {}),
                serp_data,
                competitor_data,
                results.get("content_blueprint", {})
            )
            results["performance_prediction"] = performance_prediction
        except Exception as e:
            print(f"Error generating performance prediction: {str(e)}")
            results["performance_prediction"] = {"error": str(e)}
        
        # Get available export formats and CMS platforms
        try:
            export_formats = export_integration.get_export_formats()
            cms_platforms = export_integration.get_cms_platforms()
            results["export_options"] = {
                "formats": export_formats,
                "cms_platforms": cms_platforms
            }
        except Exception as e:
            print(f"Error getting export options: {str(e)}")
            results["export_options"] = {"error": str(e)}
        
        # Add fallback API status
        results["google_apis_status"] = {
            "enabled": False,
            "fallback_used": True,
            "apis_used": [
                "SerpAPI",
                "Gemini API",
                "Google Ads API"
            ]
        }
        
        return jsonify(results)
        
    except Exception as e:
        print(f"❌ Fallback processing failed: {e}")
        return jsonify({"error": f"All processing methods failed: {str(e)}"}), 500

@api_bp.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze content from a URL with Google APIs integration"""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({"error": "URL is required"}), 400
        
        # Check if Google APIs are enabled
        google_apis_enabled = is_google_apis_enabled()
        google_apis_clients = get_google_apis_clients()
        
        if google_apis_enabled and 'natural_language' in google_apis_clients:
            print("🚀 Using Google Natural Language API for URL analysis")
            try:
                # Use Google Natural Language API for enhanced analysis
                natural_language_client = google_apis_clients['natural_language']
                
                # Analyze URL content
                analysis_result = content_analyzer.analyze_url(url)
                
                # Enhance with Google Natural Language API
                if 'content' in analysis_result:
                    enhanced_analysis = natural_language_client.analyze_content(
                        analysis_result['content']
                    )
                    analysis_result['google_analysis'] = enhanced_analysis
                    analysis_result['processing_method'] = 'google_apis'
                
                return jsonify(analysis_result)
                
            except Exception as e:
                print(f"⚠️  Google APIs analysis failed, using fallback: {e}")
        
        # Fallback to original method
        print("⚠️  Using fallback URL analysis")
        analysis_result = content_analyzer.analyze_url(url)
        analysis_result['processing_method'] = 'fallback'
        
        return jsonify(analysis_result)
        
    except Exception as e:
        print(f"❌ URL analysis failed: {str(e)}")
        return jsonify({"error": f"URL analysis failed: {str(e)}"}), 500

@api_bp.route('/export', methods=['POST'])
def export_content():
    """Export content with enhanced Google APIs data"""
    try:
        data = request.json
        content_data = data.get('content', {})
        export_format = data.get('format', 'json')
        
        if not content_data:
            return jsonify({"error": "Content data is required"}), 400
        
        # Add Google APIs metadata if available
        google_apis_enabled = is_google_apis_enabled()
        if google_apis_enabled:
            content_data['google_apis_enhanced'] = True
            content_data['export_timestamp'] = datetime.now().isoformat()
        
        # Export content using existing integration
        export_result = export_integration.export_content(content_data, export_format)
        
        return jsonify(export_result)
        
    except Exception as e:
        print(f"❌ Export failed: {str(e)}")
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@api_bp.route('/publish', methods=['POST'])
def publish_content():
    """Publish content to CMS platforms"""
    try:
        data = request.json
        content_data = data.get('content', {})
        platform = data.get('platform', 'wordpress')
        
        if not content_data:
            return jsonify({"error": "Content data is required"}), 400
        
        # Add Google APIs metadata if available
        google_apis_enabled = is_google_apis_enabled()
        if google_apis_enabled:
            content_data['google_apis_enhanced'] = True
            content_data['publish_timestamp'] = datetime.now().isoformat()
        
        # Publish content using existing integration
        publish_result = export_integration.publish_to_cms(content_data, platform)
        
        return jsonify(publish_result)
        
    except Exception as e:
        print(f"❌ Publishing failed: {str(e)}")
        return jsonify({"error": f"Publishing failed: {str(e)}"}), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check with Google APIs status"""
    try:
        # Basic health check
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.1.0"
        }
        
        # Check Google APIs status
        google_apis_enabled = is_google_apis_enabled()
        google_apis_clients = get_google_apis_clients()
        
        health_status["google_apis"] = {
            "enabled": google_apis_enabled,
            "clients_available": len(google_apis_clients),
            "clients": list(google_apis_clients.keys())
        }
        
        # Check fallback APIs
        health_status["fallback_apis"] = {
            "serpapi_configured": bool(serpapi_key),
            "gemini_configured": bool(gemini_api_key),
            "google_ads_configured": bool(google_ads_credentials.get('developer_token'))
        }
        
        # Overall system health
        if google_apis_enabled or serpapi_key:
            health_status["overall_status"] = "fully_operational"
        else:
            health_status["overall_status"] = "limited_functionality"
            health_status["status"] = "degraded"
        
        return jsonify(health_status)
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Additional Google APIs specific endpoints
@api_bp.route('/google-apis/migrate', methods=['POST'])
def migrate_to_google_apis():
    """Migrate specific functionality to Google APIs"""
    try:
        data = request.json
        feature = data.get('feature', 'all')
        
        if not is_google_apis_enabled():
            return jsonify({"error": "Google APIs not enabled"}), 400
        
        migration_manager = get_migration_manager()
        if not migration_manager:
            return jsonify({"error": "Migration manager not available"}), 400
        
        # Perform migration based on feature
        if feature == 'serp_analysis':
            result = migration_manager.migrate_serp_analysis()
        elif feature == 'content_analysis':
            result = migration_manager.migrate_content_analysis()
        elif feature == 'entity_analysis':
            result = migration_manager.migrate_entity_analysis()
        elif feature == 'all':
            result = migration_manager.migrate_all_features()
        else:
            return jsonify({"error": f"Unknown feature: {feature}"}), 400
        
        return jsonify({
            "migration_status": "success",
            "feature": feature,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return jsonify({"error": f"Migration failed: {str(e)}"}), 500

@api_bp.route('/google-apis/performance', methods=['GET'])
def google_apis_performance():
    """Get Google APIs performance metrics"""
    try:
        google_apis_clients = get_google_apis_clients()
        
        if not google_apis_clients:
            return jsonify({"error": "Google APIs not available"}), 400
        
        performance_data = {
            "timestamp": datetime.now().isoformat(),
            "clients": {},
            "overall_performance": "good"
        }
        
        # Get performance data from each client
        for client_name, client in google_apis_clients.items():
            try:
                if hasattr(client, 'get_performance_metrics'):
                    metrics = client.get_performance_metrics()
                    performance_data["clients"][client_name] = metrics
                else:
                    performance_data["clients"][client_name] = {
                        "status": "available",
                        "metrics": "not_implemented"
                    }
            except Exception as e:
                performance_data["clients"][client_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return jsonify(performance_data)
        
    except Exception as e:
        print(f"❌ Performance check failed: {str(e)}")
        return jsonify({"error": f"Performance check failed: {str(e)}"}), 500

# Error handlers
@api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'error': 'API endpoint not found',
        'available_endpoints': [
            '/api/process',
            '/api/analyze-url',
            '/api/export',
            '/api/publish',
            '/api/health',
            '/api/google-apis/migrate',
            '/api/google-apis/performance'
        ]
    }), 404

@api_bp.errorhandler(500)
def api_internal_error(error):
    print(f"API internal error: {str(error)}")
    return jsonify({
        'error': 'Internal server error in API',
        'google_apis_enabled': is_google_apis_enabled(),
        'fallback_available': bool(serpapi_key)
    }), 500
