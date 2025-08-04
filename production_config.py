"""
Production Configuration for SERP Strategist API
Environment-specific settings for production deployment
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production configuration settings"""
    
    # Flask Configuration
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/serp_strategist_prod.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0,
        'pool_size': 10
    }
    
    # Redis Configuration (for caching and sessions)
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Will be set from REDIS_URL
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'serp:'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-User-ID']
    
    # Google APIs Configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # SerpAPI Configuration (Fallback)
    SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')
    USE_GOOGLE_APIS = os.environ.get('USE_GOOGLE_APIS', 'true').lower() == 'true'
    FALLBACK_TO_SERPAPI = os.environ.get('FALLBACK_TO_SERPAPI', 'true').lower() == 'true'
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY'))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Error Tracking
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    SENTRY_ENVIRONMENT = 'production'
    
    # WebSocket Configuration
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25
    
    # Performance Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # External API Timeouts
    API_TIMEOUT = 30
    API_RETRY_COUNT = 3
    API_RETRY_DELAY = 1
    
    # Blueprint Generation Configuration
    MAX_BLUEPRINT_GENERATION_TIME = 300  # 5 minutes
    MAX_CONCURRENT_GENERATIONS = 10
    
    @staticmethod
    def init_app(app):
        """Initialize application with production configuration"""
        # Set up logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create logs directory if it doesn't exist
        os.makedirs('/app/logs', exist_ok=True)
        
        # Configure logging
        file_handler = RotatingFileHandler(
            '/app/logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            ProductionConfig.LOG_FORMAT
        ))
        file_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        # Configure Sentry if DSN is provided
        if ProductionConfig.SENTRY_DSN:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration
                from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
                
                sentry_sdk.init(
                    dsn=ProductionConfig.SENTRY_DSN,
                    integrations=[
                        FlaskIntegration(),
                        SqlalchemyIntegration(),
                    ],
                    traces_sample_rate=0.1,
                    environment=ProductionConfig.SENTRY_ENVIRONMENT,
                    release=os.environ.get('APP_VERSION', 'unknown')
                )
            except ImportError:
                app.logger.warning("Sentry SDK not installed, error tracking disabled")
        
        # Validate required environment variables
        required_vars = ['SECRET_KEY']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        app.logger.info("Production configuration initialized successfully")