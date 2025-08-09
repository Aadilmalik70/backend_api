"""
Usage Tracking Middleware for SERP Strategist

Middleware to track usage and enforce subscription limits across all blueprint endpoints.
Integrates with the payment service to check quotas and record usage events.
"""

import logging
from functools import wraps
from flask import request, jsonify, g
from typing import Optional, Dict, Any

from ..services.payment_service import PaymentService, PaymentServiceError
from ..models.user import User

logger = logging.getLogger(__name__)

class UsageTracker:
    """Middleware class for tracking usage and enforcing limits"""
    
    def __init__(self):
        self.payment_service = PaymentService()
    
    def require_usage_quota(self, resource_type: str = 'blueprint', cost: int = 1):
        """
        Decorator to check and enforce usage quotas
        
        Args:
            resource_type: Type of resource being consumed ('blueprint', 'api_call')
            cost: Number of units this operation consumes
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get user from header
                user_id = request.headers.get('X-User-ID')
                if not user_id:
                    return jsonify({
                        'error': 'Authentication required',
                        'message': 'X-User-ID header is required',
                        'code': 'AUTH_REQUIRED'
                    }), 401
                
                try:
                    user_id = int(user_id)
                except (ValueError, TypeError):
                    return jsonify({
                        'error': 'Invalid user ID',
                        'message': 'X-User-ID must be a valid integer',
                        'code': 'INVALID_USER_ID'
                    }), 400
                
                # Check if user exists
                user = User.query.get(user_id)
                if not user:
                    return jsonify({
                        'error': 'User not found',
                        'message': 'The specified user does not exist',
                        'code': 'USER_NOT_FOUND'
                    }), 404
                
                # Check usage limits
                try:
                    usage_check = self.payment_service.check_usage_limits(user_id, resource_type)
                    
                    if not usage_check.get('allowed', False):
                        # Handle different failure scenarios
                        if usage_check.get('subscription_status') == 'inactive':
                            return jsonify({
                                'error': 'Subscription required',
                                'message': 'An active subscription is required to use this feature',
                                'code': 'SUBSCRIPTION_REQUIRED',
                                'upgrade_url': '/api/payment/plans'
                            }), 402  # Payment Required
                        
                        elif usage_check.get('subscription_status') == 'active':
                            return jsonify({
                                'error': 'Usage limit exceeded',
                                'message': f'You have reached your {resource_type} limit for this billing period',
                                'code': 'USAGE_LIMIT_EXCEEDED',
                                'subscription': usage_check.get('subscription'),
                                'usage_info': {
                                    'limit': usage_check.get('limit'),
                                    'used': usage_check.get('used'),
                                    'remaining': usage_check.get('remaining')
                                },
                                'upgrade_url': '/api/payment/plans'
                            }), 429  # Too Many Requests
                        
                        else:
                            return jsonify({
                                'error': 'Access denied',
                                'message': usage_check.get('message', 'Access to this resource is not allowed'),
                                'code': 'ACCESS_DENIED'
                            }), 403
                    
                    # Store usage info in Flask's g object for the view function
                    g.usage_info = usage_check
                    g.user_id = user_id
                    g.resource_type = resource_type
                    g.resource_cost = cost
                    
                except PaymentServiceError as e:
                    logger.error(f"Payment service error during usage check: {e}")
                    return jsonify({
                        'error': 'Payment service error',
                        'message': 'Unable to verify usage limits at this time',
                        'code': 'PAYMENT_SERVICE_ERROR'
                    }), 503  # Service Unavailable
                
                except Exception as e:
                    logger.error(f"Unexpected error during usage check: {e}")
                    return jsonify({
                        'error': 'Usage check failed',
                        'message': 'An unexpected error occurred while checking usage limits',
                        'code': 'USAGE_CHECK_FAILED'
                    }), 500
                
                # Call the original function
                try:
                    result = f(*args, **kwargs)
                    
                    # If the function executed successfully, record the usage
                    # Only record if the response indicates success (status code 200-299)
                    if hasattr(result, 'status_code'):
                        status_code = result.status_code
                    elif isinstance(result, tuple) and len(result) > 1:
                        status_code = result[1]
                    else:
                        status_code = 200
                    
                    if 200 <= status_code < 300:
                        self._record_successful_usage(user_id, resource_type, cost)
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in decorated function: {e}")
                    # Don't record usage for failed operations
                    raise
            
            return decorated_function
        return decorator
    
    def _record_successful_usage(self, user_id: int, resource_type: str, cost: int):
        """Record successful usage after operation completion"""
        try:
            # Get additional context from the request
            resource_id = None
            if hasattr(g, 'generated_blueprint_id'):
                resource_id = g.generated_blueprint_id
            elif hasattr(g, 'resource_id'):
                resource_id = g.resource_id
            
            # Record the usage
            success = self.payment_service.record_usage(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                quantity=cost
            )
            
            if success:
                logger.info(f"Recorded {resource_type} usage for user {user_id} (cost: {cost})")
            else:
                logger.warning(f"Failed to record {resource_type} usage for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            # Don't fail the request if usage recording fails

def track_blueprint_generation(f):
    """Convenience decorator for blueprint generation endpoints"""
    tracker = UsageTracker()
    return tracker.require_usage_quota('blueprint', 1)(f)

def track_api_call(cost: int = 1):
    """Convenience decorator for API call tracking"""
    def decorator(f):
        tracker = UsageTracker()
        return tracker.require_usage_quota('api_call', cost)(f)
    return decorator

def get_user_usage_info() -> Optional[Dict[str, Any]]:
    """Get usage information for the current request"""
    return getattr(g, 'usage_info', None)

def set_resource_id(resource_id: str):
    """Set the resource ID for usage tracking"""
    g.resource_id = resource_id

def set_generated_blueprint_id(blueprint_id: str):
    """Set the generated blueprint ID for usage tracking"""
    g.generated_blueprint_id = blueprint_id

class UsageMiddleware:
    """Flask middleware for usage tracking"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        self.payment_service = PaymentService()
        
        @app.before_request
        def before_request():
            # Initialize usage tracking context
            g.usage_tracked = False
            g.usage_info = None
        
        @app.after_request
        def after_request(response):
            # Add usage information to response headers for debugging
            if hasattr(g, 'usage_info') and g.usage_info:
                usage_info = g.usage_info
                if usage_info.get('subscription_status') == 'active':
                    subscription = usage_info.get('subscription', {})
                    response.headers['X-Usage-Limit'] = str(usage_info.get('limit', 0))
                    response.headers['X-Usage-Used'] = str(usage_info.get('used', 0))
                    response.headers['X-Usage-Remaining'] = str(usage_info.get('remaining', 0))
                    response.headers['X-Subscription-Plan'] = subscription.get('plan', {}).get('name', 'unknown')
            
            return response

# Utility functions for blueprint generation endpoints
def check_can_generate_blueprint(user_id: int) -> Dict[str, Any]:
    """
    Check if user can generate a blueprint
    
    Returns:
        Dict with permission status and details
    """
    try:
        payment_service = PaymentService()
        return payment_service.check_usage_limits(user_id, 'blueprint')
    except Exception as e:
        logger.error(f"Error checking blueprint generation permission: {e}")
        return {
            'allowed': False,
            'error': str(e)
        }

def record_blueprint_generation(user_id: int, blueprint_id: str) -> bool:
    """
    Record a blueprint generation event
    
    Returns:
        True if recorded successfully
    """
    try:
        payment_service = PaymentService()
        return payment_service.record_usage(
            user_id=user_id,
            resource_type='blueprint',
            resource_id=blueprint_id,
            quantity=1
        )
    except Exception as e:
        logger.error(f"Error recording blueprint generation: {e}")
        return False

def get_user_subscription_info(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user's subscription information
    
    Returns:
        Subscription details or None
    """
    try:
        payment_service = PaymentService()
        return payment_service.get_user_subscription(user_id)
    except Exception as e:
        logger.error(f"Error getting user subscription info: {e}")
        return None