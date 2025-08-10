"""
Conversational Query Routes - REST API endpoints for conversational query processing

Provides P0 priority endpoints for the conversational query engine with:
- Natural language query processing
- Multi-turn conversation support
- Real-time query enhancement
- Comprehensive analytics and metrics
- Session management and context retention

Designed for high-performance production deployment with parallel processing.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import hashlib
from collections import defaultdict, deque

# Import conversational query engine
from services.conversational_query_engine import get_conversational_query_engine, QueryIntent, QueryContext

# Import semantic clustering service for enhanced query analysis
from services.semantic_clustering_service import get_semantic_clustering_service, ClusteringMode

logger = logging.getLogger(__name__)

# Create blueprint with updated URL prefix
conversational_query_bp = Blueprint('conversational_query', __name__, url_prefix='/api/queries/conversational')

# Global query engine instance
query_engine = None

# Authentication and rate limiting storage
user_request_counts = defaultdict(lambda: deque())
user_quotas = defaultdict(lambda: {'daily': 1000, 'hourly': 100, 'used_daily': 0, 'used_hourly': 0, 'last_reset': datetime.utcnow()})

# Rate limiting configuration
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = 100
DAILY_QUOTA = 1000

async def initialize_query_engine():
    """Initialize the global query engine instance"""
    global query_engine
    if query_engine is None:
        query_engine = await get_conversational_query_engine()
    return query_engine


# Authentication and validation decorators
def require_auth(f):
    """Decorator to require header-based authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        api_key = request.headers.get('X-API-Key')
        
        if not user_id:
            return jsonify({
                "status": "error",
                "error": "Authentication required",
                "message": "X-User-ID header is required",
                "timestamp": datetime.utcnow().isoformat()
            }), 401
        
        # Basic API key validation (optional)
        if api_key and not _validate_api_key(api_key):
            return jsonify({
                "status": "error",
                "error": "Invalid API key",
                "message": "The provided API key is invalid",
                "timestamp": datetime.utcnow().isoformat()
            }), 401
        
        # Add user_id to request context
        request.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit_check(f):
    """Decorator to enforce rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                "status": "error",
                "error": "Authentication required for rate limiting",
                "timestamp": datetime.utcnow().isoformat()
            }), 401
        
        current_time = time.time()
        
        # Clean old requests outside the window
        user_requests = user_request_counts[user_id]
        while user_requests and current_time - user_requests[0] > RATE_LIMIT_WINDOW:
            user_requests.popleft()
        
        # Check rate limit
        if len(user_requests) >= RATE_LIMIT_MAX_REQUESTS:
            return jsonify({
                "status": "error",
                "error": "Rate limit exceeded",
                "message": f"Maximum {RATE_LIMIT_MAX_REQUESTS} requests per hour allowed",
                "retry_after": int(RATE_LIMIT_WINDOW - (current_time - user_requests[0])),
                "timestamp": datetime.utcnow().isoformat()
            }), 429
        
        # Add current request
        user_requests.append(current_time)
        return f(*args, **kwargs)
    
    return decorated_function


def quota_check(f):
    """Decorator to enforce daily quotas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            return jsonify({
                "status": "error",
                "error": "Authentication required for quota tracking",
                "timestamp": datetime.utcnow().isoformat()
            }), 401
        
        quota_info = user_quotas[user_id]
        current_time = datetime.utcnow()
        
        # Reset daily quota if needed
        if (current_time - quota_info['last_reset']).days >= 1:
            quota_info['used_daily'] = 0
            quota_info['used_hourly'] = 0
            quota_info['last_reset'] = current_time
        
        # Reset hourly quota
        if (current_time - quota_info['last_reset']).total_seconds() >= 3600:
            quota_info['used_hourly'] = 0
        
        # Check daily quota
        if quota_info['used_daily'] >= quota_info['daily']:
            return jsonify({
                "status": "error",
                "error": "Daily quota exceeded",
                "message": f"Maximum {quota_info['daily']} requests per day allowed",
                "quota_reset": (current_time.replace(hour=0, minute=0, second=0) + 
                               datetime.timedelta(days=1)).isoformat(),
                "timestamp": current_time.isoformat()
            }), 429
        
        # Check hourly quota
        if quota_info['used_hourly'] >= quota_info['hourly']:
            return jsonify({
                "status": "error",
                "error": "Hourly quota exceeded", 
                "message": f"Maximum {quota_info['hourly']} requests per hour allowed",
                "timestamp": current_time.isoformat()
            }), 429
        
        # Update quotas
        quota_info['used_daily'] += 1
        quota_info['used_hourly'] += 1
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_json_input(required_fields=None, max_text_length=2000):
    """Decorator to validate JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate JSON content type
            if not request.is_json:
                return jsonify({
                    "status": "error",
                    "error": "Invalid content type",
                    "message": "Request must be JSON with Content-Type: application/json",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
            
            try:
                data = request.get_json()
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "error": "Invalid JSON",
                    "message": "Request body contains invalid JSON",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
            
            if not data:
                return jsonify({
                    "status": "error",
                    "error": "Empty request body",
                    "message": "Request body cannot be empty",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "status": "error",
                            "error": f"Missing required field: {field}",
                            "message": f"The field '{field}' is required in the request body",
                            "timestamp": datetime.utcnow().isoformat()
                        }), 400
            
            # Validate text length
            if 'query' in data and len(data['query']) > max_text_length:
                return jsonify({
                    "status": "error",
                    "error": "Query too long",
                    "message": f"Query cannot exceed {max_text_length} characters",
                    "timestamp": datetime.utcnow().isoformat()
                }), 400
            
            # Sanitize text inputs
            if 'query' in data:
                data['query'] = _sanitize_text(data['query'])
            
            request.validated_data = data
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def _validate_api_key(api_key: str) -> bool:
    """Validate API key (placeholder implementation)"""
    # TODO: Implement proper API key validation against database
    return len(api_key) >= 32


def _sanitize_text(text: str) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    
    # Strip whitespace and normalize
    text = text.strip()
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '\x00', '\x08', '\x0b', '\x0c', '\x0e', '\x0f']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text

@conversational_query_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for conversational query service
    
    Returns:
        JSON response with service status and metrics
    """
    try:
        start_time = time.time()
        
        # Check if query engine is initialized
        engine_available = query_engine is not None
        
        # Get performance metrics if available
        metrics = {}
        if engine_available:
            try:
                metrics = query_engine.get_performance_metrics()
            except Exception as e:
                logger.warning(f"Failed to get metrics: {e}")
        
        # Service status
        status = "healthy" if engine_available else "initializing"
        
        response = {
            "status": status,
            "service": "conversational_query_engine",
            "timestamp": datetime.utcnow().isoformat(),
            "response_time": time.time() - start_time,
            "components": {
                "query_engine": {
                    "available": engine_available,
                    "status": "operational" if engine_available else "initializing"
                },
                "ai_integration": metrics.get('ai_integration', {}),
                "session_management": {
                    "active_sessions": metrics.get('session_metrics', {}).get('active_sessions', 0),
                    "session_ttl_hours": metrics.get('session_metrics', {}).get('session_ttl_hours', 24)
                }
            },
            "performance_metrics": metrics.get('processing_metrics', {}),
            "configuration": metrics.get('configuration', {})
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "service": "conversational_query_engine", 
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@conversational_query_bp.route('/query', methods=['POST'])
@require_auth
@rate_limit_check
@quota_check
@validate_json_input(required_fields=['query'])
def process_query():
    """
    Process a conversational query with AI-powered intent recognition
    
    Request Body:
    {
        "query": "string (required) - Natural language query",
        "session_id": "string (optional) - Conversation session ID", 
        "user_id": "string (optional) - User identifier",
        "context": "object (optional) - Additional context data"
    }
    
    Returns:
        JSON response with query processing results, intent, entities, and suggested actions
    """
    try:
        start_time = time.time()
        
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "status": "error"
            }), 400
        
        # Use validated data from decorator
        data = request.validated_data
        user_query = data['query']
        
        # Extract optional parameters (use authenticated user_id)
        session_id = data.get('session_id')
        user_id = request.user_id  # Use authenticated user_id
        context_data = data.get('context')
        
        # Initialize query engine if needed
        async def _process_query():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            # Enhanced semantic analysis with clustering
            semantic_context = None
            try:
                clustering_service = await get_semantic_clustering_service()
                
                # Perform semantic clustering for query enhancement
                if context_data and context_data.get('enable_clustering', False):
                    related_texts = context_data.get('related_queries', [])
                    if related_texts:
                        related_texts.append(user_query)
                        
                        # Fast clustering for real-time response
                        cluster_result = await clustering_service.cluster_texts(
                            texts=related_texts,
                            mode=ClusteringMode.FAST,
                            enable_validation=False
                        )
                        
                        semantic_context = {
                            'cluster_analysis': {
                                'total_clusters': cluster_result.total_clusters,
                                'quality_score': cluster_result.overall_quality,
                                'semantic_similarity': cluster_result.get_result_summary()
                            }
                        }
            except Exception as e:
                logger.warning(f"Semantic clustering failed: {e}")
                # Continue without clustering enhancement
            
            # Process query with enhanced context
            enhanced_context = context_data or {}
            if semantic_context:
                enhanced_context['semantic_analysis'] = semantic_context
            
            result = await query_engine.process_query(
                user_query=user_query,
                session_id=session_id,
                user_id=user_id,
                context_data=enhanced_context
            )
            
            return result
        
        # Execute async query processing
        result = asyncio.run(_process_query())
        
        # Format response
        response = {
            "status": "success",
            "query": user_query,
            "session_id": session_id,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "result": {
                "intent": result.intent.value,
                "context": result.context.value,
                "confidence_score": result.confidence_score,
                "extracted_entities": result.extracted_entities,
                "parameters": result.parameters,
                "suggested_actions": result.suggested_actions,
                "enhanced_query": result.enhanced_query,
                "conversation_context": result.conversation_context
            },
            "processing_metrics": result.processing_metrics
        }
        
        logger.info(f"Query processed successfully: '{user_query[:50]}...' -> {result.intent.value}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": time.time() - start_time if 'start_time' in locals() else None
        }), 500


@conversational_query_bp.route('/query', methods=['GET'])
@require_auth
@rate_limit_check
def get_query_status():
    """
    Get query processing status and recent queries for authenticated user
    
    Query Parameters:
        session_id (optional): Filter by session ID
        limit (optional): Limit number of queries returned (default: 10, max: 50)
        
    Returns:
        JSON response with user's recent queries and processing status
    """
    try:
        start_time = time.time()
        user_id = request.user_id
        
        # Get query parameters
        session_id_filter = request.args.get('session_id')
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Get user's quota information
        quota_info = user_quotas[user_id]
        
        # Get rate limit information
        user_requests = user_request_counts[user_id]
        current_time = time.time()
        
        # Clean old requests
        while user_requests and current_time - user_requests[0] > RATE_LIMIT_WINDOW:
            user_requests.popleft()
        
        # Initialize query engine if needed
        async def _get_user_data():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            # Get user's active sessions
            user_sessions = []
            for session_id, session in query_engine.active_sessions.items():
                if session.user_id == user_id:
                    if not session_id_filter or session_id == session_id_filter:
                        user_sessions.append({
                            'session_id': session.session_id,
                            'created_at': session.created_at.isoformat(),
                            'last_activity': session.last_activity.isoformat(),
                            'total_turns': len(session.turns),
                            'recent_queries': [turn.user_query for turn in session.turns[-3:]]
                        })
            
            return user_sessions[:limit]
        
        user_sessions = asyncio.run(_get_user_data())
        
        response = {
            'status': 'success',
            'user_id': user_id,
            'processing_time': time.time() - start_time,
            'timestamp': datetime.utcnow().isoformat(),
            'quota_status': {
                'daily_limit': quota_info['daily'],
                'daily_used': quota_info['used_daily'],
                'daily_remaining': quota_info['daily'] - quota_info['used_daily'],
                'hourly_limit': quota_info['hourly'],
                'hourly_used': quota_info['used_hourly'],
                'hourly_remaining': quota_info['hourly'] - quota_info['used_hourly']
            },
            'rate_limit_status': {
                'requests_in_window': len(user_requests),
                'window_limit': RATE_LIMIT_MAX_REQUESTS,
                'window_remaining': RATE_LIMIT_MAX_REQUESTS - len(user_requests),
                'window_reset_in': int(RATE_LIMIT_WINDOW - (current_time - user_requests[0])) if user_requests else RATE_LIMIT_WINDOW
            },
            'active_sessions': {
                'total_sessions': len(user_sessions),
                'sessions': user_sessions
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Query status retrieval failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": time.time() - start_time if 'start_time' in locals() else None
        }), 500


@conversational_query_bp.route('/query/batch', methods=['POST'])
@require_auth
@rate_limit_check
@quota_check
@validate_json_input(required_fields=['queries'])
def process_batch_queries():
    """
    Process multiple queries in batch with parallel processing
    
    Request Body:
    {
        "queries": ["string"] - Array of natural language queries (max 10),
        "session_id": "string (optional) - Conversation session ID",
        "user_id": "string (optional) - User identifier", 
        "parallel": "boolean (optional) - Enable parallel processing (default: true)"
    }
    
    Returns:
        JSON response with batch processing results
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
        max_batch_size = 10
        if len(queries) > max_batch_size:
            return jsonify({
                "error": f"Batch size limited to {max_batch_size} queries",
                "status": "error"
            }), 400
        
        # Extract optional parameters
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        enable_parallel = data.get('parallel', True)
        
        # Initialize query engine if needed
        async def _process_batch():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            results = []
            
            if enable_parallel:
                # Parallel processing
                tasks = [
                    query_engine.process_query(
                        user_query=query,
                        session_id=session_id,
                        user_id=user_id
                    )
                    for query in queries
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"Batch query {i} failed: {result}")
                        results.append({
                            "query": queries[i],
                            "status": "error",
                            "error": str(result)
                        })
                    else:
                        results.append({
                            "query": queries[i],
                            "status": "success",
                            "intent": result.intent.value,
                            "context": result.context.value,
                            "confidence_score": result.confidence_score,
                            "extracted_entities": result.extracted_entities,
                            "parameters": result.parameters,
                            "suggested_actions": result.suggested_actions,
                            "enhanced_query": result.enhanced_query,
                            "processing_metrics": result.processing_metrics
                        })
            else:
                # Sequential processing
                for query in queries:
                    try:
                        result = await query_engine.process_query(
                            user_query=query,
                            session_id=session_id,
                            user_id=user_id
                        )
                        
                        results.append({
                            "query": query,
                            "status": "success",
                            "intent": result.intent.value,
                            "context": result.context.value,
                            "confidence_score": result.confidence_score,
                            "extracted_entities": result.extracted_entities,
                            "parameters": result.parameters,
                            "suggested_actions": result.suggested_actions,
                            "enhanced_query": result.enhanced_query,
                            "processing_metrics": result.processing_metrics
                        })
                        
                    except Exception as e:
                        logger.error(f"Sequential batch query failed: {e}")
                        results.append({
                            "query": query,
                            "status": "error", 
                            "error": str(e)
                        })
            
            return results
        
        # Execute batch processing
        batch_results = asyncio.run(_process_batch())
        
        # Calculate batch metrics
        successful_queries = len([r for r in batch_results if r.get('status') == 'success'])
        success_rate = successful_queries / len(queries) * 100
        
        response = {
            "status": "success",
            "total_queries": len(queries),
            "successful_queries": successful_queries,
            "success_rate": success_rate,
            "processing_mode": "parallel" if enable_parallel else "sequential",
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "results": batch_results
        }
        
        logger.info(f"Batch processing completed: {successful_queries}/{len(queries)} successful")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "processing_time": time.time() - start_time if 'start_time' in locals() else None
        }), 500

@conversational_query_bp.route('/session/<session_id>', methods=['GET'])
def get_conversation_session(session_id: str):
    """
    Get conversation session details and history
    
    Args:
        session_id: Conversation session identifier
        
    Returns:
        JSON response with session details and conversation history
    """
    try:
        start_time = time.time()
        
        if not session_id or not session_id.strip():
            return jsonify({
                "error": "Session ID is required",
                "status": "error"
            }), 400
        
        # Initialize query engine if needed
        async def _get_session():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            # Get session from active sessions
            if session_id in query_engine.active_sessions:
                session = query_engine.active_sessions[session_id]
                
                return {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "session_intent": session.session_intent.value if session.session_intent else None,
                    "total_turns": len(session.turns),
                    "active_context": session.active_context,
                    "conversation_history": [
                        {
                            "turn_id": turn.turn_id,
                            "user_query": turn.user_query,
                            "intent": turn.intent.value,
                            "context": turn.context.value,
                            "confidence_score": turn.confidence_score,
                            "extracted_entities": turn.extracted_entities,
                            "parameters": turn.parameters,
                            "processing_time": turn.processing_time,
                            "timestamp": turn.timestamp.isoformat()
                        }
                        for turn in session.turns[-10:]  # Last 10 turns
                    ]
                }
            else:
                return None
        
        session_data = asyncio.run(_get_session())
        
        if session_data is None:
            return jsonify({
                "error": "Session not found",
                "status": "error",
                "session_id": session_id
            }), 404
        
        response = {
            "status": "success",
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "session": session_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Session retrieval failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@conversational_query_bp.route('/sessions', methods=['GET'])
def list_active_sessions():
    """
    List all active conversation sessions
    
    Query Parameters:
        user_id (optional): Filter sessions by user ID
        limit (optional): Limit number of sessions returned (default: 50)
        
    Returns:
        JSON response with list of active sessions
    """
    try:
        start_time = time.time()
        
        # Get query parameters
        user_id_filter = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 sessions
        
        # Initialize query engine if needed
        async def _list_sessions():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            sessions_data = []
            session_count = 0
            
            for session_id, session in query_engine.active_sessions.items():
                if session_count >= limit:
                    break
                
                # Apply user filter if specified
                if user_id_filter and session.user_id != user_id_filter:
                    continue
                
                sessions_data.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "session_intent": session.session_intent.value if session.session_intent else None,
                    "total_turns": len(session.turns),
                    "has_active_context": bool(session.active_context)
                })
                
                session_count += 1
            
            return sessions_data, len(query_engine.active_sessions)
        
        sessions_data, total_sessions = asyncio.run(_list_sessions())
        
        response = {
            "status": "success",
            "total_active_sessions": total_sessions,
            "returned_sessions": len(sessions_data),
            "user_filter": user_id_filter,
            "limit": limit,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat(),
            "sessions": sessions_data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Session listing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@conversational_query_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_conversation_session(session_id: str):
    """
    Delete a conversation session
    
    Args:
        session_id: Conversation session identifier
        
    Returns:
        JSON response confirming deletion
    """
    try:
        start_time = time.time()
        
        if not session_id or not session_id.strip():
            return jsonify({
                "error": "Session ID is required",
                "status": "error"
            }), 400
        
        # Initialize query engine if needed
        async def _delete_session():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            if session_id in query_engine.active_sessions:
                del query_engine.active_sessions[session_id]
                query_engine.metrics['conversation_sessions'] = len(query_engine.active_sessions)
                return True
            else:
                return False
        
        deleted = asyncio.run(_delete_session())
        
        if not deleted:
            return jsonify({
                "error": "Session not found",
                "status": "error",
                "session_id": session_id
            }), 404
        
        response = {
            "status": "success",
            "message": "Session deleted successfully",
            "session_id": session_id,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Session deletion failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@conversational_query_bp.route('/metrics', methods=['GET'])
def get_performance_metrics():
    """
    Get comprehensive performance metrics for the conversational query engine
    
    Returns:
        JSON response with detailed performance and usage metrics
    """
    try:
        start_time = time.time()
        
        # Initialize query engine if needed
        async def _get_metrics():
            global query_engine
            if query_engine is None:
                query_engine = await initialize_query_engine()
            
            return query_engine.get_performance_metrics()
        
        metrics = asyncio.run(_get_metrics())
        
        # Add API-specific metrics
        api_metrics = {
            "api_response_time": time.time() - start_time,
            "service_uptime": "operational",
            "endpoints_available": 6,  # Number of endpoints
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = {
            "status": "success",
            "api_metrics": api_metrics,
            "engine_metrics": metrics
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@conversational_query_bp.route('/intents', methods=['GET'])
def list_supported_intents():
    """
    List all supported query intents and their descriptions
    
    Returns:
        JSON response with available intents and examples
    """
    try:
        intent_definitions = {
            "keyword_research": {
                "description": "Research and analysis of keywords for SEO optimization",
                "examples": [
                    "Find keywords for digital marketing",
                    "What are good keywords for e-commerce?",
                    "Research search terms for SaaS products"
                ]
            },
            "competitor_analysis": {
                "description": "Analysis of competitor strategies and content",
                "examples": [
                    "Analyze my competitors in the fintech space",
                    "Who are the main competitors for Shopify?", 
                    "Compare content strategies of leading brands"
                ]
            },
            "content_strategy": {
                "description": "Development of content marketing strategies and plans",
                "examples": [
                    "Create a content strategy for B2B SaaS",
                    "Plan blog content for the next quarter",
                    "Develop content calendar for social media"
                ]
            },
            "seo_optimization": {
                "description": "Search engine optimization analysis and recommendations",
                "examples": [
                    "Optimize my website for better rankings",
                    "Improve SEO for local business",
                    "Analyze on-page SEO factors"
                ]
            },
            "market_analysis": {
                "description": "Market research and industry trend analysis",
                "examples": [
                    "Analyze the AI market landscape",
                    "Research industry trends in healthcare",
                    "Study market opportunities in fintech"
                ]
            },
            "blueprint_generation": {
                "description": "Generation of structured content blueprints and outlines",
                "examples": [
                    "Create a content blueprint for landing pages",
                    "Generate article structure for tech reviews",
                    "Build template for case studies"
                ]
            },
            "entity_research": {
                "description": "Research information about companies, brands, and organizations",
                "examples": [
                    "Tell me about Tesla's business model",
                    "Research information about Stripe",
                    "What does Microsoft Azure offer?"
                ]
            },
            "trend_analysis": {
                "description": "Analysis of current trends and popular topics",
                "examples": [
                    "What's trending in artificial intelligence?",
                    "Current trends in e-commerce",
                    "Popular topics in digital marketing"
                ]
            },
            "performance_analysis": {
                "description": "Analysis of content and marketing performance metrics",
                "examples": [
                    "How is my content performing?",
                    "Analyze website traffic patterns",
                    "Track SEO performance metrics"
                ]
            }
        }
        
        response = {
            "status": "success",
            "total_intents": len(intent_definitions),
            "timestamp": datetime.utcnow().isoformat(),
            "supported_intents": intent_definitions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Intent listing failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# Initialize the query engine on blueprint registration (Flask 2.3+ compatible)
def initialize_conversational_engine():
    """Initialize conversational query engine on first request"""
    try:
        # This will be called automatically when the first request is made
        asyncio.run(initialize_query_engine())
        logger.info("Conversational Query Engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Conversational Query Engine: {e}")

# Register initialization with app context if available
@conversational_query_bp.before_request
def ensure_engine_initialized():
    """Ensure query engine is initialized before handling requests"""
    global query_engine
    if query_engine is None:
        try:
            asyncio.run(initialize_query_engine())
        except Exception as e:
            logger.warning(f"Query engine initialization warning: {e}")

# Error handlers
@conversational_query_bp.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors"""
    return jsonify({
        "status": "error",
        "error": "Bad Request",
        "message": "Invalid request format or parameters",
        "timestamp": datetime.utcnow().isoformat()
    }), 400

@conversational_query_bp.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors"""
    return jsonify({
        "status": "error", 
        "error": "Not Found",
        "message": "Requested resource not found",
        "timestamp": datetime.utcnow().isoformat()
    }), 404

@conversational_query_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server Error"""
    return jsonify({
        "status": "error",
        "error": "Internal Server Error", 
        "message": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }), 500