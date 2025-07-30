"""
Enhanced Blueprint API Routes - Next-generation RESTful endpoints with advanced caching,
AI quality assurance, and performance optimization.

This module provides enhanced API endpoints that leverage the new architecture
components for superior performance and quality.
"""

import logging
import os
import time
import concurrent.futures
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from datetime import datetime
from typing import Dict, Any, List

# Import enhanced services
from ..services.enhanced_blueprint_generator import EnhancedBlueprintGenerator
from ..services.blueprint_storage import BlueprintStorageService
from ..utils.advanced_cache_manager import get_default_cache_manager
from ..utils.ai_quality_framework import get_default_quality_framework

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint for enhanced routes
enhanced_blueprint_routes = Blueprint('enhanced_blueprints', __name__)

# Simple authentication decorator (same as original, for consistency)
def require_auth(f):
    """Simple authentication decorator - replace with proper JWT implementation."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID', 'test-user-1')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(user_id, *args, **kwargs)
    return decorated_function

def performance_monitor(f):
    """Performance monitoring decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        endpoint_name = f.__name__
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Log performance metrics
            logger.info(f"Endpoint {endpoint_name} completed in {execution_time:.3f}s")
            
            # Add performance metadata to response if it's a JSON response
            if isinstance(result, tuple) and len(result) == 2:
                response_data, status_code = result
                if isinstance(response_data.get_json(), dict):
                    response_json = response_data.get_json()
                    if 'performance_metrics' not in response_json:
                        response_json['performance_metrics'] = {}
                    response_json['performance_metrics']['execution_time'] = round(execution_time, 3)
                    response_json['performance_metrics']['endpoint'] = endpoint_name
                    return jsonify(response_json), status_code
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Endpoint {endpoint_name} failed after {execution_time:.3f}s: {str(e)}")
            raise
    
    return decorated_function

def get_enhanced_generator() -> EnhancedBlueprintGenerator:
    """Get or create enhanced blueprint generator instance"""
    if not hasattr(current_app, 'enhanced_generator'):
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        current_app.enhanced_generator = EnhancedBlueprintGenerator(
            serpapi_key=serpapi_key,
            gemini_api_key=gemini_key,
            redis_host=redis_host,
            redis_port=redis_port
        )
    
    return current_app.enhanced_generator

@enhanced_blueprint_routes.route('/api/v3/blueprints/generate', methods=['POST'])
@require_auth
@performance_monitor
def generate_enhanced_blueprint(user_id):
    """
    Generate a next-generation content blueprint with advanced features.
    
    Request JSON:
    {
        "keyword": "content marketing",
        "project_id": "optional-project-id",
        "quality_threshold": 75.0,
        "cache_enabled": true,
        "include_quality_report": true
    }
    
    Response:
    {
        "blueprint_id": "uuid",
        "keyword": "content marketing",
        "status": "completed",
        "generation_time": 25,
        "quality_score": 87.5,
        "quality_grade": "B",
        "cache_performance": {...},
        "data": { ... enhanced blueprint data ... }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        project_id = data.get('project_id')
        quality_threshold = data.get('quality_threshold', 75.0)
        cache_enabled = data.get('cache_enabled', True)
        include_quality_report = data.get('include_quality_report', True)
        
        # Validate input
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        if len(keyword) > 255:
            return jsonify({'error': 'Keyword too long (max 255 characters)'}), 400
        
        if not 0 <= quality_threshold <= 100:
            return jsonify({'error': 'Quality threshold must be between 0 and 100'}), 400
        
        logger.info(f"Generating enhanced blueprint for keyword: '{keyword}' (user: {user_id})")
        
        # Get enhanced generator
        generator = get_enhanced_generator()
        
        # Handle cache management
        if not cache_enabled:
            generator.invalidate_cache(keyword)
        
        # Generate blueprint with timeout protection
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    generator.generate_blueprint, 
                    keyword, user_id, project_id, None, quality_threshold
                )
                blueprint_data = future.result(timeout=180)  # 3 minute timeout
        except concurrent.futures.TimeoutError:
            logger.warning(f"Enhanced blueprint generation timed out for keyword: {keyword}")
            # Fallback to quick generation
            blueprint_data = generator.generate_quick_blueprint(keyword, user_id)
            blueprint_data['generation_metadata']['fallback_reason'] = 'timeout'
        except Exception as e:
            logger.error(f"Enhanced blueprint generation failed: {str(e)}")
            return jsonify({'error': f'Blueprint generation failed: {str(e)}'}), 500
        
        # Validate generated data
        if not generator.validate_blueprint_data(blueprint_data):
            return jsonify({'error': 'Blueprint generation validation failed'}), 500
        
        # Extract quality information
        quality_score = 0.0
        quality_grade = 'N/A'
        quality_report = None
        
        if 'quality_assessment' in blueprint_data:
            quality_assessment = blueprint_data['quality_assessment']
            quality_score = quality_assessment.get('overall_score', 0.0)
            quality_grade = quality_assessment.get('quality_grade', 'N/A')
            
            if include_quality_report:
                quality_report = quality_assessment
        
        # Get database session and save
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        # Save to database
        storage = BlueprintStorageService(db_session)
        blueprint_id = storage.save_blueprint(blueprint_data, user_id, project_id)
        
        # Prepare response
        generation_time = blueprint_data.get('generation_metadata', {}).get('generation_time', 0)
        cache_performance = blueprint_data.get('generation_metadata', {}).get('cache_performance', {})
        
        response_data = {
            'blueprint_id': blueprint_id,
            'keyword': keyword,
            'status': 'completed',
            'generation_time': generation_time,
            'quality_score': round(quality_score, 2),
            'quality_grade': quality_grade,
            'cache_performance': cache_performance,
            'created_at': blueprint_data.get('generation_metadata', {}).get('created_at'),
            'system_info': {
                'version': '3.0-enhanced',
                'processing_method': blueprint_data.get('system_status', {}).get('processing_method', 'enhanced_pipeline'),
                'quality_framework_enabled': True,
                'cache_enabled': cache_enabled
            },
            'data': blueprint_data
        }
        
        # Add quality report if requested
        if include_quality_report and quality_report:
            response_data['quality_report'] = quality_report
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error generating enhanced blueprint: {str(e)}")
        return jsonify({'error': f'Enhanced blueprint generation failed: {str(e)}'}), 500

@enhanced_blueprint_routes.route('/api/v3/blueprints/generate-quick', methods=['POST'])
@require_auth
@performance_monitor
def generate_quick_enhanced_blueprint(user_id):
    """
    Generate a quick enhanced blueprint optimized for speed.
    
    Request JSON:
    {
        "keyword": "content marketing",
        "project_id": "optional-project-id",
        "use_cache": true
    }
    
    Response:
    {
        "blueprint_id": "uuid",
        "keyword": "content marketing",
        "status": "completed",
        "generation_time": 5,
        "cache_hit": true,
        "data": { ... quick blueprint data ... }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keyword = data.get('keyword', '').strip()
        project_id = data.get('project_id')
        use_cache = data.get('use_cache', True)
        
        if not keyword:
            return jsonify({'error': 'Keyword is required'}), 400
        
        logger.info(f"Generating quick enhanced blueprint for keyword: '{keyword}' (user: {user_id})")
        
        # Get enhanced generator
        generator = get_enhanced_generator()
        
        # Generate quick blueprint
        blueprint_data = generator.generate_quick_blueprint(keyword, user_id, use_cache)
        
        # Save to database if possible
        blueprint_id = f"quick-enhanced-{int(time.time())}-{hash(keyword + user_id) % 10000}"
        try:
            db_session = getattr(current_app, 'db_session', None)
            if db_session:
                storage = BlueprintStorageService(db_session)
                blueprint_id = storage.save_blueprint(blueprint_data, user_id, project_id)
        except Exception as e:
            logger.warning(f"Failed to save quick enhanced blueprint to database: {e}")
        
        # Prepare response
        generation_time = blueprint_data.get('generation_metadata', {}).get('generation_time', 0)
        cache_hit = blueprint_data.get('generation_metadata', {}).get('cache_hit', False)
        cache_performance = blueprint_data.get('generation_metadata', {}).get('cache_performance', {})
        
        return jsonify({
            'blueprint_id': blueprint_id,
            'keyword': keyword,
            'status': 'completed',
            'generation_time': generation_time,
            'cache_hit': cache_hit,
            'cache_performance': cache_performance,
            'created_at': blueprint_data['generation_metadata']['created_at'],
            'system_info': {
                'version': '3.0-enhanced-quick',
                'processing_method': 'enhanced_quick_pipeline',
                'cache_optimization': True
            },
            'data': blueprint_data,
            'note': 'Quick enhanced blueprint generated with aggressive caching'
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating quick enhanced blueprint: {str(e)}")
        return jsonify({'error': f'Quick enhanced blueprint generation failed: {str(e)}'}), 500

@enhanced_blueprint_routes.route('/api/v3/blueprints/batch', methods=['POST'])
@require_auth
@performance_monitor
def generate_batch_blueprints(user_id):
    """
    Generate multiple blueprints in parallel for efficiency.
    
    Request JSON:
    {
        "keywords": ["content marketing", "seo strategy", "digital marketing"],
        "project_id": "optional-project-id",
        "max_workers": 3
    }
    
    Response:
    {
        "batch_id": "uuid",
        "total_keywords": 3,
        "successful_generations": 2,
        "failed_generations": 1,
        "total_time": 45,
        "results": [ ... ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body required'}), 400
        
        keywords = data.get('keywords', [])
        project_id = data.get('project_id')
        max_workers = min(data.get('max_workers', 3), 5)  # Limit to 5 workers
        
        if not keywords or not isinstance(keywords, list):
            return jsonify({'error': 'Keywords list is required'}), 400
        
        if len(keywords) > 10:
            return jsonify({'error': 'Maximum 10 keywords per batch request'}), 400
        
        logger.info(f"Generating batch blueprints for {len(keywords)} keywords (user: {user_id})")
        
        # Get enhanced generator
        generator = get_enhanced_generator()
        
        # Generate blueprints in batch
        start_time = time.time()
        results = generator.batch_generate_blueprints(keywords, user_id, max_workers)
        total_time = int(time.time() - start_time)
        
        # Count successes and failures
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]
        
        # Generate batch ID
        batch_id = f"batch-{int(time.time())}-{hash(str(keywords)) % 10000}"
        
        # Save successful blueprints to database
        saved_blueprints = []
        try:
            db_session = getattr(current_app, 'db_session', None)
            if db_session:
                storage = BlueprintStorageService(db_session)
                for result in successful_results:
                    try:
                        blueprint_id = storage.save_blueprint(result, user_id, project_id)
                        result['blueprint_id'] = blueprint_id
                        saved_blueprints.append(blueprint_id)
                    except Exception as e:
                        logger.warning(f"Failed to save blueprint for keyword '{result.get('keyword')}': {e}")
        except Exception as e:
            logger.warning(f"Database session not available for batch save: {e}")
        
        return jsonify({
            'batch_id': batch_id,
            'total_keywords': len(keywords),
            'successful_generations': len(successful_results),
            'failed_generations': len(failed_results),
            'saved_to_database': len(saved_blueprints),
            'total_time': total_time,
            'average_time_per_blueprint': round(total_time / len(keywords), 2),
            'system_info': {
                'version': '3.0-enhanced-batch',
                'max_workers_used': max_workers,
                'processing_method': 'parallel_quick_pipeline'
            },
            'results': results
        }), 201
        
    except Exception as e:
        logger.error(f"Error generating batch blueprints: {str(e)}")
        return jsonify({'error': f'Batch blueprint generation failed: {str(e)}'}), 500

@enhanced_blueprint_routes.route('/api/v3/blueprints/<blueprint_id>/quality', methods=['GET'])
@require_auth
@performance_monitor
def get_blueprint_quality_report(user_id, blueprint_id):
    """
    Get a comprehensive quality report for a specific blueprint.
    
    Response:
    {
        "blueprint_id": "uuid",
        "overall_score": 87.5,
        "quality_grade": "B",
        "dimension_scores": { ... },
        "recommendations": [ ... ],
        "critical_issues": [ ... ]
    }
    """
    try:
        logger.info(f"Retrieving quality report for blueprint: {blueprint_id} (user: {user_id})")
        
        # Get blueprint from database
        db_session = getattr(current_app, 'db_session', None)
        if not db_session:
            return jsonify({'error': 'Database session not available'}), 500
        
        storage = BlueprintStorageService(db_session)
        blueprint = storage.get_blueprint(blueprint_id, user_id)
        
        if not blueprint:
            return jsonify({'error': 'Blueprint not found'}), 404
        
        # Get enhanced generator for quality assessment
        generator = get_enhanced_generator()
        
        # Generate comprehensive quality report
        quality_report = generator.get_comprehensive_quality_report(blueprint)
        
        if 'error' in quality_report:
            return jsonify({
                'error': 'Quality assessment failed',
                'details': quality_report['error']
            }), 500
        
        # Add blueprint metadata
        quality_report['blueprint_id'] = blueprint_id
        quality_report['keyword'] = blueprint.get('keyword', 'N/A')
        quality_report['assessment_timestamp'] = datetime.utcnow().isoformat()
        
        return jsonify(quality_report), 200
        
    except Exception as e:
        logger.error(f"Error getting quality report: {str(e)}")
        return jsonify({'error': f'Failed to get quality report: {str(e)}'}), 500

@enhanced_blueprint_routes.route('/api/v3/cache/status', methods=['GET'])
@performance_monitor
def get_cache_status():
    """
    Get cache system status and performance metrics.
    
    Response:
    {
        "cache_available": true,
        "redis_connected": true,
        "hit_rate": 0.85,
        "total_requests": 1250,
        "cache_size": {...}
    }
    """
    try:
        cache_manager = get_default_cache_manager()
        cache_stats = cache_manager.get_cache_stats()
        
        return jsonify({
            'cache_available': True,
            'cache_stats': cache_stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting cache status: {str(e)}")
        return jsonify({
            'cache_available': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@enhanced_blueprint_routes.route('/api/v3/cache/invalidate', methods=['POST'])
@require_auth
@performance_monitor
def invalidate_cache(user_id):
    """
    Invalidate cache entries for specific keywords or namespaces.
    
    Request JSON:
    {
        "keyword": "content marketing",  // optional
        "namespace": "competitor_analysis",  // optional
        "clear_all": false  // optional
    }
    """
    try:
        data = request.get_json() or {}
        keyword = data.get('keyword')
        namespace = data.get('namespace')
        clear_all = data.get('clear_all', False)
        
        logger.info(f"Cache invalidation requested by user: {user_id}")
        
        # Get enhanced generator
        generator = get_enhanced_generator()
        
        if clear_all:
            generator.invalidate_cache()
            message = "All caches cleared"
        elif keyword:
            generator.invalidate_cache(keyword=keyword)
            message = f"Cache cleared for keyword: {keyword}"
        elif namespace:
            generator.invalidate_cache(namespace=namespace)
            message = f"Cache cleared for namespace: {namespace}"
        else:
            return jsonify({'error': 'Must specify keyword, namespace, or clear_all'}), 400
        
        return jsonify({
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}")
        return jsonify({'error': f'Cache invalidation failed: {str(e)}'}), 500

@enhanced_blueprint_routes.route('/api/v3/system/status', methods=['GET'])
@performance_monitor
def get_enhanced_system_status():
    """
    Get comprehensive system status for the enhanced blueprint service.
    
    Response:
    {
        "service_status": "fully_operational",
        "components": {...},
        "performance_metrics": {...},
        "capabilities": [...]
    }
    """
    try:
        # Get enhanced generator status
        generator = get_enhanced_generator()
        service_status = generator.get_service_status()
        
        # Add additional system information
        service_status['api_endpoints'] = {
            'enhanced_generation': '/api/v3/blueprints/generate',
            'quick_generation': '/api/v3/blueprints/generate-quick',
            'batch_generation': '/api/v3/blueprints/batch',
            'quality_report': '/api/v3/blueprints/{id}/quality',
            'cache_status': '/api/v3/cache/status',
            'cache_invalidation': '/api/v3/cache/invalidate',
            'system_status': '/api/v3/system/status'
        }
        
        service_status['system_requirements'] = {
            'redis_recommended': True,
            'api_keys_required': ['SERPAPI_KEY', 'GEMINI_API_KEY'],
            'minimum_memory': '2GB',
            'recommended_memory': '4GB'
        }
        
        return jsonify(service_status), 200
        
    except Exception as e:
        logger.error(f"Error getting enhanced system status: {str(e)}")
        return jsonify({
            'service_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Error handlers for enhanced routes
@enhanced_blueprint_routes.errorhandler(404)
def enhanced_not_found(error):
    return jsonify({
        'error': 'Enhanced endpoint not found',
        'available_endpoints': [
            '/api/v3/blueprints/generate',
            '/api/v3/blueprints/generate-quick',
            '/api/v3/blueprints/batch',
            '/api/v3/cache/status',
            '/api/v3/system/status'
        ],
        'tip': 'Use /api/v3/system/status for detailed endpoint documentation'
    }), 404

@enhanced_blueprint_routes.errorhandler(405)
def enhanced_method_not_allowed(error):
    return jsonify({'error': 'Method not allowed for this enhanced endpoint'}), 405

@enhanced_blueprint_routes.errorhandler(500)
def enhanced_internal_error(error):
    logger.error(f"Enhanced service internal error: {str(error)}")
    return jsonify({'error': 'Enhanced service internal error occurred'}), 500