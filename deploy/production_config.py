"""
Production Configuration for SERP Strategist API
Enterprise-grade deployment settings with security and performance optimization
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production environment configuration"""
    
    # Application Settings
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///serp_strategist_prod.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Google APIs Configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # API Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_HEADERS_ENABLED = True
    
    # Performance Settings
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=12)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_TO_STDOUT = True
    
    # CORS Settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Health Check Settings
    HEALTH_CHECK_PATH = '/health'
    METRICS_PATH = '/metrics'
    
    # Backup Configuration
    BACKUP_ENABLED = True
    BACKUP_SCHEDULE = '0 2 * * *'  # Daily at 2 AM
    
    @staticmethod
    def validate_config():
        """Validate required environment variables"""
        required_vars = [
            'GOOGLE_API_KEY',
            'GOOGLE_CUSTOM_SEARCH_ENGINE_ID',
            'GEMINI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        return True

class SecurityConfig:
    """Security hardening configuration"""
    
    # HTTPS Enforcement
    FORCE_HTTPS = True
    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    
    # API Security
    API_KEY_REQUIRED = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Content Security Policy
    CSP_POLICY = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'connect-src': "'self' https://api.google.com"
    }
    
    # Request Validation
    MAX_REQUEST_SIZE = 1024 * 1024  # 1MB
    REQUEST_TIMEOUT = 30  # seconds
    
    # IP Whitelist (optional)
    ALLOWED_IPS = os.environ.get('ALLOWED_IPS', '').split(',') if os.environ.get('ALLOWED_IPS') else []

class MonitoringConfig:
    """Monitoring and observability configuration"""
    
    # Application Metrics
    ENABLE_METRICS = True
    METRICS_ENDPOINT = '/metrics'
    
    # Health Checks
    HEALTH_CHECKS = {
        'database': True,
        'google_apis': True,
        'disk_space': True,
        'memory': True
    }
    
    # Performance Monitoring
    SLOW_QUERY_THRESHOLD = 1.0  # seconds
    ENABLE_QUERY_LOGGING = True
    
    # Error Tracking
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    ERROR_EMAIL_RECIPIENTS = os.environ.get('ERROR_EMAIL_RECIPIENTS', '').split(',')
    
    # Alerting Thresholds
    CPU_ALERT_THRESHOLD = 80  # percentage
    MEMORY_ALERT_THRESHOLD = 85  # percentage
    DISK_ALERT_THRESHOLD = 90  # percentage
    ERROR_RATE_THRESHOLD = 5  # percentage

# Environment Detection
def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'production':
        ProductionConfig.validate_config()
        return ProductionConfig
    else:
        # Fallback to production config with warnings
        print("⚠️  Unknown environment, using production config")
        return ProductionConfig