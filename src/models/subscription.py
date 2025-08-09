"""
Subscription and Payment Models for SERP Strategist

Handles subscription plans, user subscriptions, usage tracking, and payment transactions.
Designed for Razorpay integration with comprehensive quota management.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import json

db = SQLAlchemy()

class SubscriptionTier(Enum):
    """Subscription tier enumeration"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"
    SUSPENDED = "suspended"

class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

class SubscriptionPlan(db.Model):
    """Subscription plan definitions with features and pricing"""
    __tablename__ = 'subscription_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # free, pro, enterprise
    tier = db.Column(db.Enum(SubscriptionTier), nullable=False)
    
    # Pricing
    price_monthly = db.Column(Numeric(10, 2), nullable=False, default=0)
    price_yearly = db.Column(Numeric(10, 2), nullable=False, default=0)
    currency = db.Column(db.String(3), nullable=False, default='INR')
    
    # Features and limits
    blueprint_limit = db.Column(db.Integer, nullable=False, default=10)  # Monthly blueprint generation limit
    api_calls_limit = db.Column(db.Integer, nullable=False, default=100)  # Monthly API calls
    competitor_analysis_depth = db.Column(db.Integer, nullable=False, default=5)  # Number of competitors analyzed
    export_formats = db.Column(db.JSON, nullable=False, default=lambda: ['json'])  # Supported export formats
    features = db.Column(db.JSON, nullable=False, default=dict)  # Additional features
    
    # Plan metadata
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    subscriptions = db.relationship('UserSubscription', backref='plan', lazy=True)

    def __repr__(self):
        return f'<SubscriptionPlan {self.name}>'

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'tier': self.tier.value,
            'price_monthly': float(self.price_monthly),
            'price_yearly': float(self.price_yearly),
            'currency': self.currency,
            'blueprint_limit': self.blueprint_limit,
            'api_calls_limit': self.api_calls_limit,
            'competitor_analysis_depth': self.competitor_analysis_depth,
            'export_formats': self.export_formats,
            'features': self.features,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def get_default_plans():
        """Get default subscription plans configuration"""
        return [
            {
                'name': 'Free',
                'tier': SubscriptionTier.FREE,
                'price_monthly': 0,
                'price_yearly': 0,
                'blueprint_limit': 5,
                'api_calls_limit': 50,
                'competitor_analysis_depth': 3,
                'export_formats': ['json'],
                'features': {
                    'basic_blueprint_generation': True,
                    'competitor_analysis': True,
                    'export_json': True,
                    'email_support': False,
                    'priority_support': False,
                    'api_access': False
                },
                'description': 'Perfect for getting started with content strategy',
                'sort_order': 1
            },
            {
                'name': 'Pro',
                'tier': SubscriptionTier.PRO,
                'price_monthly': 999,  # ₹999/month
                'price_yearly': 9999,  # ₹9999/year (2 months free)
                'blueprint_limit': 100,
                'api_calls_limit': 1000,
                'competitor_analysis_depth': 10,
                'export_formats': ['json', 'pdf', 'csv', 'docx'],
                'features': {
                    'advanced_blueprint_generation': True,
                    'deep_competitor_analysis': True,
                    'export_all_formats': True,
                    'email_support': True,
                    'priority_support': False,
                    'api_access': True,
                    'batch_processing': True,
                    'custom_templates': True
                },
                'description': 'Ideal for content marketers and SEO professionals',
                'sort_order': 2
            },
            {
                'name': 'Enterprise',
                'tier': SubscriptionTier.ENTERPRISE,
                'price_monthly': 4999,  # ₹4999/month
                'price_yearly': 49999,  # ₹49999/year (2 months free)
                'blueprint_limit': -1,  # Unlimited
                'api_calls_limit': -1,  # Unlimited
                'competitor_analysis_depth': 25,
                'export_formats': ['json', 'pdf', 'csv', 'docx', 'xlsx'],
                'features': {
                    'unlimited_blueprints': True,
                    'unlimited_api_calls': True,
                    'advanced_competitor_analysis': True,
                    'white_label_reports': True,
                    'export_all_formats': True,
                    'email_support': True,
                    'priority_support': True,
                    'phone_support': True,
                    'api_access': True,
                    'batch_processing': True,
                    'custom_templates': True,
                    'team_collaboration': True,
                    'custom_integrations': True
                },
                'description': 'Complete solution for agencies and large teams',
                'sort_order': 3
            }
        ]

class UserSubscription(db.Model):
    """User subscription tracking and management"""
    __tablename__ = 'user_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Subscription details
    status = db.Column(db.Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    billing_cycle = db.Column(db.String(10), nullable=False, default='monthly')  # monthly, yearly
    
    # Dates
    start_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime, nullable=False)
    trial_end_date = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    # Razorpay integration
    razorpay_subscription_id = db.Column(db.String(255), nullable=True)
    razorpay_customer_id = db.Column(db.String(255), nullable=True)
    
    # Usage tracking (current period)
    current_period_start = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    current_period_end = db.Column(db.DateTime, nullable=False)
    blueprints_used = db.Column(db.Integer, nullable=False, default=0)
    api_calls_used = db.Column(db.Integer, nullable=False, default=0)
    
    # Metadata
    subscription_metadata = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='subscriptions')
    payments = db.relationship('PaymentTransaction', backref='subscription', lazy=True)

    def __init__(self, **kwargs):
        super(UserSubscription, self).__init__(**kwargs)
        if not self.end_date:
            # Set default end date based on billing cycle
            if self.billing_cycle == 'yearly':
                self.end_date = self.start_date + timedelta(days=365)
                self.current_period_end = self.start_date + timedelta(days=365)
            else:
                self.end_date = self.start_date + timedelta(days=30)
                self.current_period_end = self.start_date + timedelta(days=30)

    def __repr__(self):
        return f'<UserSubscription user_id={self.user_id} plan_id={self.plan_id}>'

    def is_active(self) -> bool:
        """Check if subscription is currently active"""
        now = datetime.now(timezone.utc)
        return (
            self.status == SubscriptionStatus.ACTIVE and
            now >= self.start_date and
            now <= self.end_date
        )

    def is_trial(self) -> bool:
        """Check if subscription is in trial period"""
        if not self.trial_end_date:
            return False
        now = datetime.now(timezone.utc)
        return now <= self.trial_end_date

    def days_remaining(self) -> int:
        """Get number of days remaining in subscription"""
        now = datetime.now(timezone.utc)
        if now > self.end_date:
            return 0
        return (self.end_date - now).days

    def can_generate_blueprint(self) -> bool:
        """Check if user can generate another blueprint"""
        if not self.is_active():
            return False
        
        # Unlimited for enterprise
        if self.plan.blueprint_limit == -1:
            return True
        
        return self.blueprints_used < self.plan.blueprint_limit

    def can_make_api_call(self) -> bool:
        """Check if user can make another API call"""
        if not self.is_active():
            return False
        
        # Unlimited for enterprise
        if self.plan.api_calls_limit == -1:
            return True
        
        return self.api_calls_used < self.plan.api_calls_limit

    def increment_blueprint_usage(self) -> bool:
        """Increment blueprint usage. Returns False if limit exceeded."""
        if not self.can_generate_blueprint():
            return False
        
        self.blueprints_used += 1
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return True

    def increment_api_usage(self) -> bool:
        """Increment API usage. Returns False if limit exceeded."""
        if not self.can_make_api_call():
            return False
        
        self.api_calls_used += 1
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return True

    def reset_usage_for_new_period(self):
        """Reset usage counters for new billing period"""
        self.blueprints_used = 0
        self.api_calls_used = 0
        
        # Update period dates
        if self.billing_cycle == 'yearly':
            self.current_period_start = datetime.now(timezone.utc)
            self.current_period_end = self.current_period_start + timedelta(days=365)
        else:
            self.current_period_start = datetime.now(timezone.utc)
            self.current_period_end = self.current_period_start + timedelta(days=30)
        
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def cancel_subscription(self, reason: Optional[str] = None):
        """Cancel the subscription"""
        self.status = SubscriptionStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
        if reason and self.subscription_metadata:
            self.subscription_metadata['cancellation_reason'] = reason
        elif reason:
            self.subscription_metadata = {'cancellation_reason': reason}
        
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan.to_dict() if self.plan else None,
            'status': self.status.value,
            'billing_cycle': self.billing_cycle,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'days_remaining': self.days_remaining(),
            'is_active': self.is_active(),
            'is_trial': self.is_trial(),
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'blueprints_used': self.blueprints_used,
            'blueprints_remaining': max(0, self.plan.blueprint_limit - self.blueprints_used) if self.plan.blueprint_limit != -1 else -1,
            'api_calls_used': self.api_calls_used,
            'api_calls_remaining': max(0, self.plan.api_calls_limit - self.api_calls_used) if self.plan.api_calls_limit != -1 else -1,
            'razorpay_subscription_id': self.razorpay_subscription_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PaymentTransaction(db.Model):
    """Payment transaction tracking for Razorpay integration"""
    __tablename__ = 'payment_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    
    # Transaction details
    amount = db.Column(Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='INR')
    status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    payment_method = db.Column(db.String(50), nullable=True)
    
    # Razorpay integration
    razorpay_order_id = db.Column(db.String(255), nullable=True)
    razorpay_payment_id = db.Column(db.String(255), nullable=True)
    razorpay_signature = db.Column(db.String(255), nullable=True)
    
    # Transaction metadata
    transaction_type = db.Column(db.String(50), nullable=False, default='subscription')  # subscription, top_up, refund
    description = db.Column(db.Text, nullable=True)
    failure_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='payment_transactions')

    def __repr__(self):
        return f'<PaymentTransaction {self.id} {self.status.value}>'

    def mark_success(self, razorpay_payment_id: str, razorpay_signature: str):
        """Mark payment as successful"""
        self.status = PaymentStatus.SUCCESS
        self.razorpay_payment_id = razorpay_payment_id
        self.razorpay_signature = razorpay_signature
        self.processed_at = datetime.now(timezone.utc)
        db.session.commit()

    def mark_failed(self, reason: str):
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.processed_at = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status.value,
            'payment_method': self.payment_method,
            'razorpay_order_id': self.razorpay_order_id,
            'razorpay_payment_id': self.razorpay_payment_id,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'failure_reason': self.failure_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class UsageEvent(db.Model):
    """Track individual usage events for analytics and billing"""
    __tablename__ = 'usage_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    
    # Event details
    event_type = db.Column(db.String(50), nullable=False)  # blueprint_generation, api_call, export, etc.
    resource_type = db.Column(db.String(50), nullable=True)  # blueprint, competitor_analysis, etc.
    resource_id = db.Column(db.String(255), nullable=True)  # ID of the resource used
    
    # Usage metrics
    quantity = db.Column(db.Integer, default=1, nullable=False)
    cost_units = db.Column(db.Integer, default=1, nullable=False)  # How many units this event consumed
    
    # Metadata
    event_metadata = db.Column(db.JSON, nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='usage_events')
    subscription = db.relationship('UserSubscription', backref='usage_events')

    def __repr__(self):
        return f'<UsageEvent {self.event_type} user_id={self.user_id}>'

    def to_dict(self) -> Dict[str, Any]:
        """Convert usage event to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'event_type': self.event_type,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'quantity': self.quantity,
            'cost_units': self.cost_units,
            'metadata': self.event_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }