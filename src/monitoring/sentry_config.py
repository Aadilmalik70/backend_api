"""
Sentry Configuration for SERP Strategist Backend
Error tracking and performance monitoring setup
"""

import os
import logging
from typing import Optional

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logging.warning("Sentry SDK not installed. Error tracking will be disabled.")

class SentryConfig:
    """Sentry configuration and initialization"""
    
    def __init__(self):
        self.dsn = os.environ.get('SENTRY_DSN')
        self.environment = os.environ.get('SENTRY_ENVIRONMENT', 'production')
        self.release = os.environ.get('SENTRY_RELEASE', 'unknown')
        self.sample_rate = float(os.environ.get('SENTRY_SAMPLE_RATE', '1.0'))
        self.traces_sample_rate = float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1'))
        
    def init_sentry(self, app=None) -> bool:
        """Initialize Sentry error tracking"""
        if not SENTRY_AVAILABLE:
            if app:
                app.logger.warning("Sentry SDK not available, error tracking disabled")
            return False
            
        if not self.dsn:
            if app:
                app.logger.warning("SENTRY_DSN not configured, error tracking disabled")
            return False
            
        try:
            # Configure logging integration
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Capture info and above as breadcrumbs
                event_level=logging.ERROR  # Send errors as events
            )
            
            # Initialize Sentry
            sentry_sdk.init(
                dsn=self.dsn,
                integrations=[
                    FlaskIntegration(
                        transaction_style='endpoint'
                    ),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    sentry_logging,
                ],
                traces_sample_rate=self.traces_sample_rate,
                sample_rate=self.sample_rate,
                environment=self.environment,
                release=self.release,
                before_send=self._before_send,
                before_send_transaction=self._before_send_transaction,
            )
            
            if app:
                app.logger.info(f"Sentry initialized successfully for environment: {self.environment}")
            
            return True
            
        except Exception as e:
            if app:
                app.logger.error(f"Failed to initialize Sentry: {e}")
            return False
    
    def _before_send(self, event, hint):
        """Filter events before sending to Sentry"""
        # Filter out health check requests
        if 'request' in event and event['request'].get('url', '').endswith('/health'):
            return None
            
        # Filter out certain exceptions
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            
            # Don't send connection errors
            if 'Connection' in str(exc_type):
                return None
                
            # Don't send rate limit errors
            if 'RateLimitExceeded' in str(exc_type):
                return None
                
        return event
    
    def _before_send_transaction(self, event, hint):
        """Filter transactions before sending to Sentry"""
        # Filter out health check transactions
        if event.get('transaction') == '/health':
            return None
            
        return event
    
    def capture_message(self, message: str, level: str = 'info'):
        """Capture a message with Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.capture_message(message, level)
    
    def capture_exception(self, exception: Optional[Exception] = None):
        """Capture an exception with Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.capture_exception(exception)
    
    def add_breadcrumb(self, message: str, category: str = 'default', level: str = 'info', data: dict = None):
        """Add a breadcrumb to Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {}
            )
    
    def set_user(self, user_id: str, email: str = None, username: str = None):
        """Set user context for Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_user({
                'id': user_id,
                'email': email,
                'username': username
            })
    
    def set_tag(self, key: str, value: str):
        """Set a tag for Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_tag(key, value)
    
    def set_context(self, key: str, context: dict):
        """Set context for Sentry"""
        if SENTRY_AVAILABLE and self.dsn:
            sentry_sdk.set_context(key, context)

# Global Sentry instance
sentry_config = SentryConfig()

def init_error_tracking(app):
    """Initialize error tracking for Flask app"""
    success = sentry_config.init_sentry(app)
    
    if success:
        # Add Flask error handlers
        @app.errorhandler(500)
        def handle_internal_error(error):
            sentry_config.capture_exception()
            return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            # Don't capture HTTP exceptions (4xx errors)
            if hasattr(error, 'code') and 400 <= error.code < 500:
                return error
            
            sentry_config.capture_exception()
            app.logger.error(f"Unhandled exception: {error}")
            return {'error': 'Internal server error', 'message': 'An unexpected error occurred'}, 500
    
    return success