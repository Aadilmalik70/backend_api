"""
Payment Routes for SERP Strategist

API endpoints for payment processing, subscription management, and Razorpay integration.
Handles order creation, payment verification, webhook processing, and subscription lifecycle.
"""

import logging
from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from typing import Dict, Any

from ..services.payment_service import PaymentService, PaymentServiceError
from ..models.user import User
from ..models.subscription import db

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

def get_user_from_header():
    """Extract user from X-User-ID header"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return None
    
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

def require_user(f):
    """Decorator to require user authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user_from_header()
        if not user:
            return jsonify({
                'error': 'Authentication required',
                'message': 'X-User-ID header is required'
            }), 401
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function

def handle_payment_error(f):
    """Decorator to handle payment service errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except PaymentServiceError as e:
            logger.error(f"Payment service error: {e}")
            return jsonify({
                'error': 'Payment processing error',
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"Unexpected error in payment endpoint: {e}")
            return jsonify({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred while processing payment'
            }), 500
    
    return decorated_function

@payment_bp.route('/status', methods=['GET'])
def payment_status():
    """Get payment service status and configuration"""
    try:
        payment_service = PaymentService()
        
        return jsonify({
            'status': 'success',
            'data': {
                'payment_service_available': payment_service.is_available(),
                'supported_currencies': ['INR'],
                'supported_payment_methods': [
                    'card', 'netbanking', 'wallet', 'upi'
                ],
                'razorpay_configured': payment_service.razorpay_key_id is not None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get payment status: {e}")
        return jsonify({
            'error': 'Failed to get payment status',
            'message': str(e)
        }), 500

@payment_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        payment_service = PaymentService()
        plans = payment_service.get_subscription_plans()
        
        return jsonify({
            'status': 'success',
            'data': {
                'plans': plans,
                'count': len(plans)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get subscription plans: {e}")
        return jsonify({
            'error': 'Failed to get subscription plans',
            'message': str(e)
        }), 500

@payment_bp.route('/subscription', methods=['GET'])
@require_user
def get_user_subscription():
    """Get current user's subscription details"""
    try:
        payment_service = PaymentService()
        subscription = payment_service.get_user_subscription(request.current_user.id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'subscription': subscription,
                'has_active_subscription': subscription is not None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get user subscription: {e}")
        return jsonify({
            'error': 'Failed to get subscription details',
            'message': str(e)
        }), 500

@payment_bp.route('/create-order', methods=['POST'])
@require_user
@handle_payment_error
def create_payment_order():
    """Create a new payment order for subscription"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle', 'monthly')
        
        if not plan_id:
            return jsonify({
                'error': 'Invalid request',
                'message': 'plan_id is required'
            }), 400
        
        if billing_cycle not in ['monthly', 'yearly']:
            return jsonify({
                'error': 'Invalid request',
                'message': 'billing_cycle must be monthly or yearly'
            }), 400
        
        # Create payment order
        payment_service = PaymentService()
        order_data = payment_service.create_order(
            user_id=request.current_user.id,
            plan_id=plan_id,
            billing_cycle=billing_cycle
        )
        
        logger.info(f"Created payment order for user {request.current_user.id}, plan {plan_id}")
        
        return jsonify({
            'status': 'success',
            'data': order_data,
            'message': 'Payment order created successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to create payment order: {e}")
        return jsonify({
            'error': 'Failed to create payment order',
            'message': str(e)
        }), 500

@payment_bp.route('/verify', methods=['POST'])
@require_user
@handle_payment_error
def verify_payment():
    """Verify payment and activate subscription"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        # Validate required fields
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({
                'error': 'Invalid request',
                'message': 'razorpay_order_id, razorpay_payment_id, and razorpay_signature are required'
            }), 400
        
        # Verify payment
        payment_service = PaymentService()
        result = payment_service.verify_payment(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature
        )
        
        logger.info(f"Payment verified for user {request.current_user.id}")
        
        return jsonify({
            'status': 'success',
            'data': result,
            'message': 'Payment verified successfully'
        }), 200
        
    except PaymentServiceError as e:
        logger.error(f"Payment verification failed: {e}")
        return jsonify({
            'error': 'Payment verification failed',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error during payment verification: {e}")
        return jsonify({
            'error': 'Payment verification failed',
            'message': 'An unexpected error occurred during payment verification'
        }), 500

@payment_bp.route('/webhook', methods=['POST'])
def handle_razorpay_webhook():
    """Handle Razorpay webhook events"""
    try:
        # Get webhook signature from headers
        signature = request.headers.get('X-Razorpay-Signature')
        if not signature:
            logger.warning("Webhook received without signature")
            return jsonify({
                'error': 'Invalid webhook',
                'message': 'Webhook signature is required'
            }), 400
        
        # Get raw payload
        payload = request.get_data()
        
        # Process webhook
        payment_service = PaymentService()
        result = payment_service.handle_webhook(payload, signature)
        
        if result.get('success'):
            logger.info("Webhook processed successfully")
            return jsonify({
                'status': 'success',
                'message': result.get('message', 'Webhook processed successfully')
            }), 200
        else:
            logger.warning(f"Webhook processing failed: {result.get('message')}")
            return jsonify({
                'error': 'Webhook processing failed',
                'message': result.get('message', 'Unknown error')
            }), 400
        
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return jsonify({
            'error': 'Webhook processing error',
            'message': str(e)
        }), 500

@payment_bp.route('/subscription/cancel', methods=['POST'])
@require_user
@handle_payment_error
def cancel_subscription():
    """Cancel user's active subscription"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'User requested cancellation')
        
        payment_service = PaymentService()
        success = payment_service.cancel_subscription(
            user_id=request.current_user.id,
            reason=reason
        )
        
        if success:
            logger.info(f"Subscription cancelled for user {request.current_user.id}")
            return jsonify({
                'status': 'success',
                'message': 'Subscription cancelled successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Cancellation failed',
                'message': 'No active subscription found to cancel'
            }), 404
        
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        return jsonify({
            'error': 'Cancellation failed',
            'message': str(e)
        }), 500

@payment_bp.route('/usage/check', methods=['GET'])
@require_user
def check_usage_limits():
    """Check user's usage limits and remaining quota"""
    try:
        resource_type = request.args.get('resource_type', 'blueprint')
        
        if resource_type not in ['blueprint', 'api_call']:
            return jsonify({
                'error': 'Invalid resource type',
                'message': 'resource_type must be blueprint or api_call'
            }), 400
        
        payment_service = PaymentService()
        usage_info = payment_service.check_usage_limits(
            user_id=request.current_user.id,
            resource_type=resource_type
        )
        
        return jsonify({
            'status': 'success',
            'data': usage_info
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to check usage limits: {e}")
        return jsonify({
            'error': 'Failed to check usage limits',
            'message': str(e)
        }), 500

@payment_bp.route('/usage/record', methods=['POST'])
@require_user
def record_usage():
    """Record usage of a resource (for internal use)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request body is required'
            }), 400
        
        resource_type = data.get('resource_type')
        if not resource_type:
            return jsonify({
                'error': 'Invalid request',
                'message': 'resource_type is required'
            }), 400
        
        resource_id = data.get('resource_id')
        quantity = data.get('quantity', 1)
        
        payment_service = PaymentService()
        success = payment_service.record_usage(
            user_id=request.current_user.id,
            resource_type=resource_type,
            resource_id=resource_id,
            quantity=quantity
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Usage recorded successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Usage limit exceeded',
                'message': 'You have exceeded your subscription limits'
            }), 429
        
    except Exception as e:
        logger.error(f"Failed to record usage: {e}")
        return jsonify({
            'error': 'Failed to record usage',
            'message': str(e)
        }), 500

@payment_bp.route('/transactions', methods=['GET'])
@require_user
def get_user_transactions():
    """Get user's payment transaction history"""
    try:
        from ..models.subscription import PaymentTransaction
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Query transactions
        transactions = PaymentTransaction.query.filter_by(
            user_id=request.current_user.id
        ).order_by(PaymentTransaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'transactions': [tx.to_dict() for tx in transactions.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': transactions.total,
                    'pages': transactions.pages,
                    'has_next': transactions.has_next,
                    'has_prev': transactions.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get user transactions: {e}")
        return jsonify({
            'error': 'Failed to get transactions',
            'message': str(e)
        }), 500

@payment_bp.route('/usage/history', methods=['GET'])
@require_user
def get_usage_history():
    """Get user's usage history and analytics"""
    try:
        from ..models.subscription import UsageEvent
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        # Get date range parameters
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query usage events
        usage_events = UsageEvent.query.filter(
            UsageEvent.user_id == request.current_user.id,
            UsageEvent.created_at >= start_date
        ).all()
        
        # Get usage summary
        usage_summary = db.session.query(
            UsageEvent.event_type,
            func.count(UsageEvent.id).label('count'),
            func.sum(UsageEvent.quantity).label('total_quantity')
        ).filter(
            UsageEvent.user_id == request.current_user.id,
            UsageEvent.created_at >= start_date
        ).group_by(UsageEvent.event_type).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'usage_events': [event.to_dict() for event in usage_events],
                'usage_summary': [
                    {
                        'event_type': row.event_type,
                        'count': row.count,
                        'total_quantity': row.total_quantity
                    }
                    for row in usage_summary
                ],
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to get usage history: {e}")
        return jsonify({
            'error': 'Failed to get usage history',
            'message': str(e)
        }), 500

# Error handlers
@payment_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'message': 'The requested payment endpoint was not found'
    }), 404

@payment_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The requested method is not allowed for this payment endpoint'
    }), 405