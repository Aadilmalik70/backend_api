"""
Payment Service for SERP Strategist

Handles Razorpay integration, subscription management, and payment processing.
Provides comprehensive payment workflows with proper error handling and security.
"""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone, timedelta

import razorpay
from flask import current_app

from ..models.subscription import (
    db, SubscriptionPlan, UserSubscription, PaymentTransaction,
    SubscriptionStatus, PaymentStatus, SubscriptionTier, UsageEvent
)
from ..models.user import User

logger = logging.getLogger(__name__)

class PaymentServiceError(Exception):
    """Custom exception for payment service errors"""
    pass

class PaymentService:
    """Service for handling payment operations and Razorpay integration"""
    
    def __init__(self):
        """Initialize Razorpay client and configuration"""
        self.razorpay_key_id = os.getenv('RAZORPAY_KEY_ID')
        self.razorpay_key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        
        if not self.razorpay_key_id or not self.razorpay_key_secret:
            logger.warning("Razorpay credentials not configured. Payment features will be limited.")
            self.client = None
        else:
            try:
                self.client = razorpay.Client(auth=(self.razorpay_key_id, self.razorpay_key_secret))
                logger.info("Razorpay client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if payment service is available"""
        return self.client is not None
    
    def create_order(self, user_id: int, plan_id: int, billing_cycle: str = 'monthly') -> Dict[str, Any]:
        """
        Create a Razorpay order for subscription payment
        
        Args:
            user_id: User ID
            plan_id: Subscription plan ID
            billing_cycle: 'monthly' or 'yearly'
            
        Returns:
            Dict containing order details
        """
        if not self.is_available():
            raise PaymentServiceError("Payment service is not available")
        
        try:
            # Get user and plan
            user = User.query.get(user_id)
            if not user:
                raise PaymentServiceError("User not found")
            
            plan = SubscriptionPlan.query.get(plan_id)
            if not plan:
                raise PaymentServiceError("Subscription plan not found")
            
            # Calculate amount based on billing cycle
            if billing_cycle == 'yearly':
                amount = float(plan.price_yearly) * 100  # Convert to paise
            else:
                amount = float(plan.price_monthly) * 100  # Convert to paise
            
            if amount <= 0:
                raise PaymentServiceError("Invalid payment amount")
            
            # Create order data
            order_data = {
                'amount': int(amount),
                'currency': plan.currency,
                'receipt': f"sub_{user_id}_{plan_id}_{int(datetime.now().timestamp())}",
                'notes': {
                    'user_id': str(user_id),
                    'plan_id': str(plan_id),
                    'plan_name': plan.name,
                    'billing_cycle': billing_cycle,
                    'user_email': user.email
                }
            }
            
            # Create order with Razorpay
            razorpay_order = self.client.order.create(data=order_data)
            
            # Create payment transaction record
            transaction = PaymentTransaction(
                user_id=user_id,
                amount=Decimal(amount) / 100,  # Convert back to rupees
                currency=plan.currency,
                status=PaymentStatus.PENDING,
                razorpay_order_id=razorpay_order['id'],
                transaction_type='subscription',
                description=f"Subscription to {plan.name} plan ({billing_cycle})"
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            logger.info(f"Created Razorpay order {razorpay_order['id']} for user {user_id}")
            
            return {
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'receipt': razorpay_order['receipt'],
                'transaction_id': transaction.id,
                'plan': plan.to_dict(),
                'billing_cycle': billing_cycle,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            db.session.rollback()
            raise PaymentServiceError(f"Failed to create payment order: {str(e)}")
    
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, 
                      razorpay_signature: str) -> Dict[str, Any]:
        """
        Verify Razorpay payment signature and process payment
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Razorpay signature
            
        Returns:
            Dict containing verification result and subscription details
        """
        if not self.is_available():
            raise PaymentServiceError("Payment service is not available")
        
        try:
            # Find the transaction
            transaction = PaymentTransaction.query.filter_by(
                razorpay_order_id=razorpay_order_id
            ).first()
            
            if not transaction:
                raise PaymentServiceError("Transaction not found")
            
            # Verify signature
            if not self._verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
                transaction.mark_failed("Invalid payment signature")
                raise PaymentServiceError("Payment verification failed")
            
            # Get payment details from Razorpay
            payment_details = self.client.payment.fetch(razorpay_payment_id)
            
            if payment_details.get('status') != 'captured':
                transaction.mark_failed(f"Payment not captured: {payment_details.get('status')}")
                raise PaymentServiceError("Payment was not successful")
            
            # Mark transaction as successful
            transaction.mark_success(razorpay_payment_id, razorpay_signature)
            transaction.payment_method = payment_details.get('method', 'unknown')
            
            # Get order details to extract plan information
            order_details = self.client.order.fetch(razorpay_order_id)
            notes = order_details.get('notes', {})
            
            user_id = int(notes.get('user_id'))
            plan_id = int(notes.get('plan_id'))
            billing_cycle = notes.get('billing_cycle', 'monthly')
            
            # Create or update subscription
            subscription = self._create_or_update_subscription(
                user_id, plan_id, billing_cycle, transaction.id
            )
            
            # Log usage event
            self._log_usage_event(
                user_id=user_id,
                event_type='subscription_payment',
                subscription_id=subscription.id,
                metadata={
                    'payment_id': razorpay_payment_id,
                    'amount': float(transaction.amount),
                    'plan_name': subscription.plan.name,
                    'billing_cycle': billing_cycle
                }
            )
            
            logger.info(f"Payment verified successfully for user {user_id}, subscription {subscription.id}")
            
            return {
                'success': True,
                'transaction': transaction.to_dict(),
                'subscription': subscription.to_dict(),
                'message': 'Payment verified and subscription activated successfully'
            }
            
        except PaymentServiceError:
            raise
        except Exception as e:
            logger.error(f"Payment verification failed: {e}")
            if 'transaction' in locals():
                transaction.mark_failed(str(e))
            raise PaymentServiceError(f"Payment verification failed: {str(e)}")
    
    def handle_webhook(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Handle Razorpay webhook events
        
        Args:
            payload: Webhook payload
            signature: Webhook signature
            
        Returns:
            Dict containing processing result
        """
        if not self.is_available():
            raise PaymentServiceError("Payment service is not available")
        
        try:
            # Verify webhook signature
            webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET')
            if not webhook_secret:
                logger.warning("Webhook secret not configured")
                return {'success': False, 'message': 'Webhook secret not configured'}
            
            if not self._verify_webhook_signature(payload, signature, webhook_secret):
                logger.warning("Invalid webhook signature")
                return {'success': False, 'message': 'Invalid webhook signature'}
            
            # Parse webhook payload
            import json
            event_data = json.loads(payload.decode('utf-8'))
            
            event_type = event_data.get('event')
            logger.info(f"Processing webhook event: {event_type}")
            
            # Handle different event types
            if event_type == 'payment.captured':
                return self._handle_payment_captured(event_data.get('payload', {}).get('payment', {}).get('entity', {}))
            elif event_type == 'payment.failed':
                return self._handle_payment_failed(event_data.get('payload', {}).get('payment', {}).get('entity', {}))
            elif event_type == 'subscription.activated':
                return self._handle_subscription_activated(event_data.get('payload', {}).get('subscription', {}).get('entity', {}))
            elif event_type == 'subscription.cancelled':
                return self._handle_subscription_cancelled(event_data.get('payload', {}).get('subscription', {}).get('entity', {}))
            else:
                logger.info(f"Unhandled webhook event type: {event_type}")
                return {'success': True, 'message': f'Event {event_type} acknowledged but not processed'}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {'success': False, 'message': f'Webhook processing failed: {str(e)}'}
    
    def get_subscription_plans(self) -> list:
        """Get all active subscription plans"""
        try:
            plans = SubscriptionPlan.query.filter_by(is_active=True).order_by(SubscriptionPlan.sort_order).all()
            return [plan.to_dict() for plan in plans]
        except Exception as e:
            logger.error(f"Failed to get subscription plans: {e}")
            return []
    
    def get_user_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's current active subscription"""
        try:
            subscription = UserSubscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
            
            if subscription and subscription.is_active():
                return subscription.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user subscription: {e}")
            return None
    
    def cancel_subscription(self, user_id: int, reason: Optional[str] = None) -> bool:
        """Cancel user's active subscription"""
        try:
            subscription = UserSubscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
            
            if not subscription:
                return False
            
            subscription.cancel_subscription(reason)
            
            # Log usage event
            self._log_usage_event(
                user_id=user_id,
                event_type='subscription_cancelled',
                subscription_id=subscription.id,
                metadata={'reason': reason}
            )
            
            logger.info(f"Cancelled subscription {subscription.id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel subscription: {e}")
            return False
    
    def check_usage_limits(self, user_id: int, resource_type: str) -> Dict[str, Any]:
        """
        Check if user can use a specific resource based on their subscription
        
        Args:
            user_id: User ID
            resource_type: 'blueprint' or 'api_call'
            
        Returns:
            Dict with usage status and limits
        """
        try:
            subscription = UserSubscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
            
            if not subscription or not subscription.is_active():
                # Check if user has a free tier fallback
                free_plan = SubscriptionPlan.query.filter_by(
                    tier=SubscriptionTier.FREE,
                    is_active=True
                ).first()
                
                if free_plan:
                    # Create a temporary free subscription
                    return {
                        'allowed': True,
                        'subscription_status': 'free_fallback',
                        'limit': free_plan.blueprint_limit if resource_type == 'blueprint' else free_plan.api_calls_limit,
                        'used': 0,
                        'remaining': free_plan.blueprint_limit if resource_type == 'blueprint' else free_plan.api_calls_limit
                    }
                else:
                    return {
                        'allowed': False,
                        'subscription_status': 'inactive',
                        'message': 'No active subscription found'
                    }
            
            if resource_type == 'blueprint':
                can_use = subscription.can_generate_blueprint()
                limit = subscription.plan.blueprint_limit
                used = subscription.blueprints_used
            elif resource_type == 'api_call':
                can_use = subscription.can_make_api_call()
                limit = subscription.plan.api_calls_limit
                used = subscription.api_calls_used
            else:
                return {
                    'allowed': False,
                    'error': f'Unknown resource type: {resource_type}'
                }
            
            return {
                'allowed': can_use,
                'subscription_status': 'active',
                'subscription': subscription.to_dict(),
                'limit': limit,
                'used': used,
                'remaining': max(0, limit - used) if limit != -1 else -1
            }
            
        except Exception as e:
            logger.error(f"Failed to check usage limits: {e}")
            return {
                'allowed': False,
                'error': f'Failed to check usage limits: {str(e)}'
            }
    
    def record_usage(self, user_id: int, resource_type: str, resource_id: Optional[str] = None, 
                    quantity: int = 1) -> bool:
        """
        Record usage of a resource
        
        Args:
            user_id: User ID
            resource_type: Type of resource used
            resource_id: ID of the specific resource
            quantity: Quantity used
            
        Returns:
            True if usage was recorded successfully
        """
        try:
            subscription = UserSubscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).first()
            
            # Record usage in subscription if exists
            if subscription and subscription.is_active():
                if resource_type == 'blueprint':
                    success = subscription.increment_blueprint_usage()
                elif resource_type == 'api_call':
                    success = subscription.increment_api_usage()
                else:
                    success = True  # Other resource types are just logged
                
                if not success:
                    logger.warning(f"Usage limit exceeded for user {user_id}, resource {resource_type}")
                    return False
            
            # Log usage event
            self._log_usage_event(
                user_id=user_id,
                event_type=f'{resource_type}_usage',
                resource_type=resource_type,
                resource_id=resource_id,
                subscription_id=subscription.id if subscription else None,
                quantity=quantity
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to record usage: {e}")
            return False
    
    def _verify_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verify Razorpay payment signature"""
        try:
            message = f"{order_id}|{payment_id}"
            generated_signature = hmac.new(
                self.razorpay_key_secret.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(generated_signature, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def _verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        try:
            generated_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(generated_signature, signature)
        except Exception as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
    
    def _create_or_update_subscription(self, user_id: int, plan_id: int, 
                                     billing_cycle: str, transaction_id: int) -> UserSubscription:
        """Create new subscription or update existing one"""
        try:
            # Cancel any existing active subscriptions
            existing_subscriptions = UserSubscription.query.filter_by(
                user_id=user_id,
                status=SubscriptionStatus.ACTIVE
            ).all()
            
            for sub in existing_subscriptions:
                sub.cancel_subscription("Upgraded to new plan")
            
            # Create new subscription
            plan = SubscriptionPlan.query.get(plan_id)
            start_date = datetime.now(timezone.utc)
            
            if billing_cycle == 'yearly':
                end_date = start_date + timedelta(days=365)
            else:
                end_date = start_date + timedelta(days=30)
            
            subscription = UserSubscription(
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.ACTIVE,
                billing_cycle=billing_cycle,
                start_date=start_date,
                end_date=end_date,
                current_period_start=start_date,
                current_period_end=end_date
            )
            
            # Link to payment transaction
            transaction = PaymentTransaction.query.get(transaction_id)
            if transaction:
                transaction.subscription_id = subscription.id
            
            db.session.add(subscription)
            db.session.commit()
            
            return subscription
            
        except Exception as e:
            logger.error(f"Failed to create subscription: {e}")
            db.session.rollback()
            raise
    
    def _log_usage_event(self, user_id: int, event_type: str, subscription_id: Optional[int] = None,
                        resource_type: Optional[str] = None, resource_id: Optional[str] = None,
                        quantity: int = 1, metadata: Optional[Dict] = None):
        """Log a usage event"""
        try:
            event = UsageEvent(
                user_id=user_id,
                subscription_id=subscription_id,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                quantity=quantity,
                metadata=metadata
            )
            
            db.session.add(event)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to log usage event: {e}")
    
    def _handle_payment_captured(self, payment_data: Dict) -> Dict[str, Any]:
        """Handle payment.captured webhook"""
        try:
            payment_id = payment_data.get('id')
            order_id = payment_data.get('order_id')
            
            transaction = PaymentTransaction.query.filter_by(
                razorpay_order_id=order_id
            ).first()
            
            if transaction and transaction.status == PaymentStatus.PENDING:
                transaction.status = PaymentStatus.SUCCESS
                transaction.razorpay_payment_id = payment_id
                transaction.processed_at = datetime.now(timezone.utc)
                db.session.commit()
                
                logger.info(f"Payment captured webhook processed for transaction {transaction.id}")
            
            return {'success': True, 'message': 'Payment captured event processed'}
            
        except Exception as e:
            logger.error(f"Failed to handle payment captured webhook: {e}")
            return {'success': False, 'message': str(e)}
    
    def _handle_payment_failed(self, payment_data: Dict) -> Dict[str, Any]:
        """Handle payment.failed webhook"""
        try:
            order_id = payment_data.get('order_id')
            error_description = payment_data.get('error_description', 'Payment failed')
            
            transaction = PaymentTransaction.query.filter_by(
                razorpay_order_id=order_id
            ).first()
            
            if transaction and transaction.status == PaymentStatus.PENDING:
                transaction.mark_failed(error_description)
                logger.info(f"Payment failed webhook processed for transaction {transaction.id}")
            
            return {'success': True, 'message': 'Payment failed event processed'}
            
        except Exception as e:
            logger.error(f"Failed to handle payment failed webhook: {e}")
            return {'success': False, 'message': str(e)}
    
    def _handle_subscription_activated(self, subscription_data: Dict) -> Dict[str, Any]:
        """Handle subscription.activated webhook"""
        # This would be used for recurring subscriptions
        logger.info("Subscription activated webhook received")
        return {'success': True, 'message': 'Subscription activated event processed'}
    
    def _handle_subscription_cancelled(self, subscription_data: Dict) -> Dict[str, Any]:
        """Handle subscription.cancelled webhook"""
        # This would be used for recurring subscriptions
        logger.info("Subscription cancelled webhook received")
        return {'success': True, 'message': 'Subscription cancelled event processed'}

def create_default_subscription_plans():
    """Create default subscription plans if they don't exist"""
    try:
        existing_plans = SubscriptionPlan.query.count()
        if existing_plans > 0:
            logger.info("Subscription plans already exist, skipping creation")
            return
        
        default_plans = SubscriptionPlan.get_default_plans()
        
        for plan_data in default_plans:
            plan = SubscriptionPlan(**plan_data)
            db.session.add(plan)
        
        db.session.commit()
        logger.info(f"Created {len(default_plans)} default subscription plans")
        
    except Exception as e:
        logger.error(f"Failed to create default subscription plans: {e}")
        db.session.rollback()