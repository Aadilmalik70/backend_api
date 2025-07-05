# Filename: app_enhanced.py
import logging
import json
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import enhanced modules
from input_handler import InputHandler
from serp_collector import SerpCollector
from keyword_processor_enhanced import KeywordProcessorEnhanced
from content_analyzer_enhanced import ContentAnalyzerEnhanced
from insight_generator_enhanced import InsightGeneratorEnhanced
from serp_feature_optimizer import SerpFeatureOptimizer
from content_performance_predictor import ContentPerformancePredictor
from export_integration import ExportIntegrationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
input_handler = InputHandler()
serp_collector = SerpCollector()
keyword_processor = KeywordProcessorEnhanced()
content_analyzer = ContentAnalyzerEnhanced()
insight_generator = InsightGeneratorEnhanced()
serp_feature_optimizer = SerpFeatureOptimizer()
performance_predictor = ContentPerformancePredictor()
export_manager = ExportIntegrationManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_input():
    """Process user input and return content strategy insights."""
    try:
        # Get input data
        if request.is_json:
            data = request.get_json()
            input_text = data.get('input', '')
            domain = data.get('domain', '')
        else:
            input_text = request.form.get('input', '')
            domain = request.form.get('domain', '')
            
        # Process input to extract keywords
        keywords = input_handler.process_input(input_text)
        
        # Collect SERP data
        serp_data = serp_collector.collect_serp_data(keywords)
        
        # Process keywords with enhanced metrics
        keyword_data = keyword_processor.process_keywords(keywords, serp_data)
        
        # Analyze competitor content
        competitor_data = content_analyzer.analyze_competitors(keywords, serp_data)
        
        # Generate enhanced content insights
        content_insights = insight_generator.generate_insights(keywords, keyword_data, serp_data, competitor_data)
        
        # Generate SERP feature optimization recommendations
        serp_features = serp_data.get('features', {})
        optimization_recommendations = serp_feature_optimizer.generate_optimization_recommendations(serp_features, keyword_data)
        
        # Generate content blueprint
        content_blueprint = insight_generator.generate_content_blueprint(
            keywords[0] if keywords else '',
            keyword_data,
            competitor_data,
            optimization_recommendations
        )
        
        # Predict content performance
        performance_prediction = performance_predictor.predict_performance(
            keywords[0] if keywords else '',
            keyword_data,
            competitor_data,
            content_blueprint,
            domain_authority=30.0  # Default domain authority
        )
        
        # Get available export formats
        export_formats = export_manager.get_available_export_formats()
        
        # Get available CMS platforms
        cms_platforms = export_manager.get_available_cms_platforms()
        
        # Prepare response
        response = {
            'success': True,
            'keywords': keywords,
            'keyword_data': keyword_data,
            'content_insights': content_insights,
            'content_blueprint': content_blueprint,
            'optimization_recommendations': optimization_recommendations,
            'performance_prediction': performance_prediction.dict() if hasattr(performance_prediction, 'dict') else performance_prediction,
            'export_formats': export_formats,
            'cms_platforms': cms_platforms
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing input: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export', methods=['POST'])
def export_content():
    """Export content in specified format."""
    try:
        # Get export parameters
        data = request.get_json()
        content_type = data.get('content_type', 'content_blueprint')
        format_id = data.get('format', 'json')
        content_data = data.get('content_data', {})
        
        # Create output filename
        filename = f"{content_type}_{format_id}_{secure_filename(content_data.get('title', 'export'))}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Export content
        if content_type == 'content_blueprint':
            result = export_manager.export_content_blueprint(content_data, format_id, output_path)
        elif content_type == 'keyword_data':
            result = export_manager.export_keyword_data(content_data, format_id, output_path)
        elif content_type == 'competitor_analysis':
            result = export_manager.export_competitor_analysis(content_data, format_id, output_path)
        elif content_type == 'performance_prediction':
            result = export_manager.export_performance_prediction(content_data, format_id, output_path)
        else:
            return jsonify({
                'success': False,
                'error': f"Unsupported content type: {content_type}"
            }), 400
            
        # Return result
        return jsonify({
            'success': result['success'],
            'file_path': result.get('file_path'),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error exporting content: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/publish', methods=['POST'])
def publish_to_cms():
    """Publish content to CMS platform."""
    try:
        # Get publish parameters
        data = request.get_json()
        content_type = data.get('content_type', 'content_blueprint')
        platform_id = data.get('platform', '')
        content_data = data.get('content_data', {})
        credentials = data.get('credentials', {})
        
        # Validate required parameters
        if not platform_id:
            return jsonify({
                'success': False,
                'error': "Platform ID is required"
            }), 400
            
        # Publish content
        result = export_manager.publish_to_cms(content_data, platform_id, credentials, content_type)
        
        # Return result
        return jsonify({
            'success': result['success'],
            'details': result.get('details'),
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error publishing to CMS: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze content from a URL."""
    try:
        # Get URL
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({
                'success': False,
                'error': "URL is required"
            }), 400
            
        # Analyze URL content
        analysis = content_analyzer.analyze_url(url)
        
        # Return analysis
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing URL: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
