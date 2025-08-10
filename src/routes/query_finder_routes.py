"""
Query Finder Routes - REST API endpoints for conversational query finder

Provides comprehensive REST API endpoints for the advanced query finder service
with 6-question-type classification, domain expansion, and quality scoring.

Features:
- Single query processing with multiple modes
- Batch processing with performance optimization
- Quality assessment and improvement suggestions
- Domain expansion and cross-domain insights
- Component metrics and performance analytics
- Real-time processing status and health checks

Designed for high-performance API access with <30s response time for 1000 queries.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, current_app

# Import query finder service
from services.conversational_query_finder import (
    get_conversational_query_finder,
    ProcessingMode,
    QueryFinderResult,
    BatchProcessingResult
)

logger = logging.getLogger(__name__)

# Create blueprint
query_finder_bp = Blueprint('query_finder', __name__, url_prefix='/api/query-finder')

# Global query finder instance
query_finder = None

async def initialize_query_finder():
    """Initialize the global query finder instance"""
    global query_finder
    if query_finder is None:
        query_finder = await get_conversational_query_finder()
    return query_finder

@query_finder_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for query finder service
    
    Returns:
        JSON response with service status, component health, and performance metrics
    """
    try:
        start_time = time.time()
        
        # Check if query finder is initialized
        finder_available = query_finder is not None
        
        # Get performance metrics if available
        metrics = {}
        if finder_available:
            try:
                metrics = query_finder.get_performance_metrics()
            except Exception as e:
                logger.warning(f"Failed to get metrics: {e}")
        
        # Service status
        status = "healthy" if finder_available else "initializing"
        
        response = {
            "status": status,
            "service": "conversational_query_finder",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time": time.time() - start_time,
            "version": "1.0.0",
            "components": {
                "query_finder": {
                    "available": finder_available,
                    "status": "operational" if finder_available else "initializing"
                },
                "question_classifier": {
                    "available": finder_available and hasattr(query_finder, 'question_classifier') and query_finder.question_classifier is not None,
                    "supported_types": 6
                },
                "domain_expander": {
                    "available": finder_available and hasattr(query_finder, 'domain_expander') and query_finder.domain_expander is not None,
                    "supported_domains": 19
                },
                "quality_scorer": {
                    "available": finder_available and hasattr(query_finder, 'quality_scorer') and query_finder.quality_scorer is not None,
                    "quality_dimensions": 7
                },
                "conversational_engine": {
                    "available": finder_available and hasattr(query_finder, 'conversational_engine') and query_finder.conversational_engine is not None,
                    "integration": "enabled" if finder_available else "unknown"
                }
            },
            "performance_metrics": metrics.get('processing_metrics', {}),
            "cache_metrics": metrics.get('cache_metrics', {}),
            "supported_features": metrics.get('supported_features', {})
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "service": "conversational_query_finder",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/find', methods=['POST'])
def find_query():
    """
    Find and analyze a single query with comprehensive processing
    
    Request Body:
    {
        "query": "string (required) - Query to analyze",
        "processing_mode": "string (optional) - fast|standard|comprehensive|custom",
        "context": "object (optional) - Additional context data"
    }
    
    Returns:
        JSON response with query analysis results including classification, expansion, and quality assessment
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required field: query",
                "status": "error"
            }), 400
        
        user_query = data['query']
        if not user_query or not user_query.strip():
            return jsonify({
                "error": "Query cannot be empty",
                "status": "error"
            }), 400
        
        # Extract optional parameters
        processing_mode_str = data.get('processing_mode', 'standard')
        context_data = data.get('context')
        
        # Validate processing mode
        try:
            processing_mode = ProcessingMode(processing_mode_str.lower())
        except ValueError:
            return jsonify({
                "error": f"Invalid processing mode: {processing_mode_str}. Valid modes: fast, standard, comprehensive, custom",
                "status": "error"
            }), 400
        
        # Initialize query finder if needed
        async def _process_query():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            # Process query
            result = await query_finder.find_query(
                query=user_query,
                processing_mode=processing_mode,
                context=context_data
            )
            
            return result
        
        # Execute async query processing
        result = asyncio.run(_process_query())
        
        # Format response
        response = {
            "status": "success",
            "query": user_query,
            "processing_mode": processing_mode.value,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "result": _format_query_finder_result(result)
        }
        
        logger.info(f"Query processed: '{user_query[:50]}...' -> {result.question_type.value} in {result.processing_time:.3f}s")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Query finding failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": time.time() - start_time if 'start_time' in locals() else None
        }), 500

@query_finder_bp.route('/find/batch', methods=['POST'])
def find_queries_batch():
    """
    Find and analyze multiple queries in batch with high performance
    
    Request Body:
    {
        "queries": ["string"] - Array of queries to analyze (max 1000),
        "processing_mode": "string (optional) - fast|standard|comprehensive|custom",
        "context": "object (optional) - Shared context for all queries"
    }
    
    Returns:
        JSON response with batch processing results and aggregate metrics
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'queries' not in data:
            return jsonify({
                "error": "Missing required field: queries",
                "status": "error"
            }), 400
        
        queries = data['queries']
        if not isinstance(queries, list) or not queries:
            return jsonify({
                "error": "Queries must be a non-empty array",
                "status": "error"
            }), 400
        
        # Limit batch size
        max_batch_size = 1000
        if len(queries) > max_batch_size:
            return jsonify({
                "error": f"Batch size limited to {max_batch_size} queries",
                "status": "error"
            }), 400
        
        # Extract optional parameters
        processing_mode_str = data.get('processing_mode', 'standard')
        context_data = data.get('context')
        
        # Validate processing mode
        try:
            processing_mode = ProcessingMode(processing_mode_str.lower())
        except ValueError:
            return jsonify({
                "error": f"Invalid processing mode: {processing_mode_str}. Valid modes: fast, standard, comprehensive, custom",
                "status": "error"
            }), 400
        
        # Initialize query finder if needed
        async def _process_batch():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            # Process batch
            result = await query_finder.batch_find_queries(
                queries=queries,
                processing_mode=processing_mode,
                context=context_data
            )
            
            return result
        
        # Execute batch processing
        batch_result = asyncio.run(_process_batch())
        
        # Format response
        response = {
            "status": "success",
            "total_queries": len(queries),
            "processing_mode": processing_mode.value,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "batch_result": _format_batch_processing_result(batch_result)
        }
        
        logger.info(f"Batch processing completed: {batch_result.successful_queries}/{len(queries)} successful in {batch_result.total_processing_time:.3f}s")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": time.time() - start_time if 'start_time' in locals() else None
        }), 500

@query_finder_bp.route('/classify', methods=['POST'])
def classify_question_type():
    """
    Classify query into one of 6 question types (fast mode only)
    
    Request Body:
    {
        "query": "string (required) - Query to classify",
        "context": "object (optional) - Additional context data"
    }
    
    Returns:
        JSON response with question type classification and confidence
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required field: query",
                "status": "error"
            }), 400
        
        user_query = data['query']
        context_data = data.get('context')
        
        # Process using fast mode
        async def _classify_query():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            result = await query_finder.find_query(
                query=user_query,
                processing_mode=ProcessingMode.FAST,
                context=context_data
            )
            
            return result
        
        result = asyncio.run(_classify_query())
        
        # Format classification response
        response = {
            "status": "success",
            "query": user_query,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "classification": {
                "question_type": result.question_type.value,
                "confidence": result.classification_confidence,
                "reasoning": f"Classified as {result.question_type.value} with {result.classification_confidence:.3f} confidence"
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Question classification failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/expand', methods=['POST'])
def expand_query_domains():
    """
    Expand query across business domains (domain expansion only)
    
    Request Body:
    {
        "query": "string (required) - Query to expand",
        "context": "object (optional) - Additional context data"
    }
    
    Returns:
        JSON response with domain expansion results and cross-domain insights
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required field: query",
                "status": "error"
            }), 400
        
        user_query = data['query']
        context_data = data.get('context')
        
        # Process using standard mode to get expansion
        async def _expand_query():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            result = await query_finder.find_query(
                query=user_query,
                processing_mode=ProcessingMode.STANDARD,
                context=context_data
            )
            
            return result
        
        result = asyncio.run(_expand_query())
        
        # Format expansion response
        response = {
            "status": "success",
            "query": user_query,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "expansion": {
                "primary_domains": [domain.value for domain in result.primary_domains],
                "expanded_queries": result.expanded_queries,
                "cross_domain_insights": result.cross_domain_insights,
                "domain_count": len(result.primary_domains)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/assess', methods=['POST'])
def assess_query_quality():
    """
    Assess query quality with multi-dimensional scoring
    
    Request Body:
    {
        "query": "string (required) - Query to assess",
        "question_type": "string (optional) - Known question type",
        "context": "object (optional) - Additional context data"
    }
    
    Returns:
        JSON response with quality assessment and improvement suggestions
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required field: query",
                "status": "error"
            }), 400
        
        user_query = data['query']
        context_data = data.get('context')
        
        # Process using comprehensive mode to get quality assessment
        async def _assess_query():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            result = await query_finder.find_query(
                query=user_query,
                processing_mode=ProcessingMode.COMPREHENSIVE,
                context=context_data
            )
            
            return result
        
        result = asyncio.run(_assess_query())
        
        # Format quality assessment response
        quality = result.quality_assessment
        response = {
            "status": "success",
            "query": user_query,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "quality_assessment": {
                "overall_score": quality.overall_score if quality else 0.0,
                "grade": quality.grade if quality else "F",
                "confidence_level": quality.confidence_level if quality else 0.0,
                "individual_metrics": [
                    {
                        "dimension": metric.dimension.value,
                        "score": metric.score,
                        "reasoning": metric.reasoning,
                        "weight": metric.weight
                    }
                    for metric in quality.individual_metrics
                ] if quality else [],
                "strengths": quality.strengths if quality else [],
                "improvement_suggestions": quality.improvement_suggestions if quality else [],
                "question_type": result.question_type.value
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Quality assessment failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/types', methods=['GET'])
def list_question_types():
    """
    List all supported question types with descriptions and examples
    
    Returns:
        JSON response with question type definitions and usage examples
    """
    try:
        # Initialize query finder if needed  
        async def _get_definitions():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            if query_finder.question_classifier:
                return query_finder.question_classifier.get_type_definitions()
            else:
                return {}
        
        definitions = asyncio.run(_get_definitions())
        
        response = {
            "status": "success",
            "total_question_types": len(definitions),
            "timestamp": datetime.utcnow().isoformat(),
            "question_types": definitions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Question types listing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/domains', methods=['GET'])
def list_business_domains():
    """
    List all supported business domains with descriptions
    
    Returns:
        JSON response with business domain definitions and relationships
    """
    try:
        # Initialize query finder if needed
        async def _get_definitions():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            if query_finder.domain_expander:
                return query_finder.domain_expander.get_domain_definitions()
            else:
                return {}
        
        definitions = asyncio.run(_get_definitions())
        
        response = {
            "status": "success",
            "total_business_domains": len(definitions),
            "timestamp": datetime.utcnow().isoformat(),
            "business_domains": definitions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Business domains listing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/quality/dimensions', methods=['GET'])
def list_quality_dimensions():
    """
    List all supported quality dimensions with descriptions
    
    Returns:
        JSON response with quality dimension definitions and factors
    """
    try:
        # Initialize query finder if needed
        async def _get_definitions():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            if query_finder.quality_scorer:
                return query_finder.quality_scorer.get_dimension_definitions()
            else:
                return {}
        
        definitions = asyncio.run(_get_definitions())
        
        response = {
            "status": "success",
            "total_quality_dimensions": len(definitions),
            "timestamp": datetime.utcnow().isoformat(),
            "quality_dimensions": definitions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Quality dimensions listing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/metrics', methods=['GET'])
def get_performance_metrics():
    """
    Get comprehensive performance metrics for the query finder service
    
    Returns:
        JSON response with detailed performance, cache, and component metrics
    """
    try:
        start_time = time.time()
        
        # Initialize query finder if needed
        async def _get_metrics():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            return query_finder.get_performance_metrics()
        
        metrics = asyncio.run(_get_metrics())
        
        # Add API-specific metrics
        api_metrics = {
            "api_response_time": time.time() - start_time,
            "service_uptime": "operational",
            "endpoints_available": 8,  # Number of endpoints
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = {
            "status": "success",
            "api_metrics": api_metrics,
            "query_finder_metrics": metrics
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@query_finder_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear query finder cache (admin endpoint)
    
    Returns:
        JSON response confirming cache clearance
    """
    try:
        # Initialize query finder if needed
        async def _clear_cache():
            global query_finder
            if query_finder is None:
                query_finder = await initialize_query_finder()
            
            query_finder.clear_cache()
            return True
        
        asyncio.run(_clear_cache())
        
        response = {
            "status": "success",
            "message": "Query finder cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Cache clearing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

def _format_query_finder_result(result: QueryFinderResult) -> Dict[str, Any]:
    """Format QueryFinderResult for JSON response"""
    formatted_result = {
        "question_type": result.question_type.value,
        "classification_confidence": result.classification_confidence,
        "primary_domains": [domain.value for domain in result.primary_domains],
        "expanded_queries": result.expanded_queries,
        "cross_domain_insights": result.cross_domain_insights,
        "suggested_improvements": result.suggested_improvements,
        "related_queries": result.related_queries,
        "suggested_actions": result.suggested_actions,
        "processing_time": result.processing_time,
        "components_used": result.components_used,
        "confidence_scores": result.confidence_scores
    }
    
    # Add quality assessment if available
    if result.quality_assessment:
        quality = result.quality_assessment
        formatted_result["quality_assessment"] = {
            "overall_score": quality.overall_score,
            "grade": quality.grade,
            "confidence_level": quality.confidence_level,
            "individual_metrics": [
                {
                    "dimension": metric.dimension.value,
                    "score": metric.score,
                    "reasoning": metric.reasoning,
                    "weight": metric.weight
                }
                for metric in quality.individual_metrics
            ],
            "strengths": quality.strengths,
            "improvement_suggestions": quality.improvement_suggestions
        }
    
    # Add conversational context if available
    if result.conversational_context:
        formatted_result["conversational_context"] = result.conversational_context
    
    return formatted_result

def _format_batch_processing_result(result: BatchProcessingResult) -> Dict[str, Any]:
    """Format BatchProcessingResult for JSON response"""
    return {
        "summary": {
            "total_queries": result.total_queries,
            "successful_queries": result.successful_queries,
            "failed_queries": result.failed_queries,
            "success_rate": (result.successful_queries / result.total_queries * 100) if result.total_queries > 0 else 0.0,
            "processing_mode": result.processing_mode.value
        },
        "performance": {
            "total_processing_time": result.total_processing_time,
            "average_processing_time": result.average_processing_time,
            "throughput_queries_per_second": result.throughput_queries_per_second,
            "cache_hit_rate": result.cache_hit_rate
        },
        "quality_metrics": {
            "average_quality_score": result.average_quality_score,
            "quality_distribution": result.quality_distribution
        },
        "analysis_metrics": {
            "question_type_distribution": result.question_type_distribution,
            "domain_distribution": result.domain_distribution
        },
        "component_performance": result.component_performance,
        "query_results": [_format_query_finder_result(query_result) for query_result in result.query_results]
    }

# Initialize the query finder on blueprint registration
@query_finder_bp.before_request
def ensure_finder_initialized():
    """Ensure query finder is initialized before handling requests"""
    global query_finder
    if query_finder is None:
        try:
            asyncio.run(initialize_query_finder())
        except Exception as e:
            logger.warning(f"Query finder initialization warning: {e}")

# Error handlers
@query_finder_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        "status": "error",
        "error": "Bad Request",
        "message": "Invalid request format or parameters",
        "timestamp": datetime.utcnow().isoformat()
    }), 400

@query_finder_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        "status": "error",
        "error": "Not Found",
        "message": "Requested endpoint not found",
        "available_endpoints": [
            "GET /api/query-finder/health",
            "POST /api/query-finder/find",
            "POST /api/query-finder/find/batch",
            "POST /api/query-finder/classify",
            "POST /api/query-finder/expand",
            "POST /api/query-finder/assess",
            "GET /api/query-finder/types",
            "GET /api/query-finder/domains",
            "GET /api/query-finder/quality/dimensions",
            "GET /api/query-finder/metrics",
            "POST /api/query-finder/cache/clear"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }), 404

@query_finder_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    return jsonify({
        "status": "error",
        "error": "Internal Server Error",
        "message": "An unexpected error occurred during query processing",
        "timestamp": datetime.utcnow().isoformat()
    }), 500