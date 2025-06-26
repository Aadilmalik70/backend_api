"""
Authentication utilities for SERP Strategist backend.
Handles JWT token generation, validation, and authentication decorators.
"""

import jwt
import secrets
import string
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Optional, Dict, Any, Tuple
from flask import current_app, request, jsonify, g
from src.models.user import User

class AuthError(Exception):
    """Custom exception for authentication errors."""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TokenManager:
    """Handles JWT token operations."""
    
    @staticmethod
    def generate_access_token(user_id: int, expires_hours: int = 24) -> str:
        """Generate a JWT access token for the user."""
        try:
            payload = {
                'user_id': user_id,
                'type': 'access',
                'exp': datetime.now(timezone.utc) + timedelta(hours=expires_hours),
                'iat': datetime.now(timezone.utc),
                'jti': secrets.token_urlsafe(16)  # JWT ID for token revocation
            }
            
            token = jwt.encode(
                payload,
                current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key'),
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            raise AuthError(f"Failed to generate access token: {str(e)}")
    
    @staticmethod
    def generate_refresh_token(user_id: int, expires_days: int = 30) -> str:
        """Generate a JWT refresh token for the user."""
        try:
            payload = {
                'user_id': user_id,
                'type': 'refresh',
                'exp': datetime.now(timezone.utc) + timedelta(days=expires_days),
                'iat': datetime.now(timezone.utc),
                'jti': secrets.token_urlsafe(16)
            }
            
            token = jwt.encode(
                payload,
                current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key'),
                algorithm='HS256'
            )
            
            return token
            
        except Exception as e:
            raise AuthError(f"Failed to generate refresh token: {str(e)}")
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                current_app.config.get('JWT_SECRET_KEY', 'dev-secret-key'),
                algorithms=['HS256']
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthError("Token has expired", 401)
        except jwt.InvalidTokenError:
            raise AuthError("Invalid token", 401)
        except Exception as e:
            raise AuthError(f"Token validation failed: {str(e)}", 401)
    
    @staticmethod
    def extract_token_from_header() -> Optional[str]:
        """Extract JWT token from Authorization header."""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            scheme, token = auth_header.split(' ', 1)
            if scheme.lower() != 'bearer':
                return None
            return token
        except ValueError:
            return None

class PasswordValidator:
    """Validates password strength and requirements."""
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        Returns (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters long"
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"

class SecurityUtils:
    """General security utilities."""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a token for email verification."""
        return SecurityUtils.generate_secure_token(48)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a token for password reset."""
        return SecurityUtils.generate_secure_token(48)
    
    @staticmethod
    def is_safe_url(target: str) -> bool:
        """Check if a URL is safe for redirects."""
        # Basic implementation - in production, use more sophisticated validation
        if not target:
            return False
        
        # Prevent open redirects
        if target.startswith(('http://', 'https://', '//')):
            return False
        
        # Allow relative URLs starting with /
        return target.startswith('/')

# Authentication decorators
def token_required(f):
    """Decorator to require valid JWT token for route access."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            # Extract token from header
            token = TokenManager.extract_token_from_header()
            if not token:
                return jsonify({
                    'error': 'Authentication token is required',
                    'code': 'TOKEN_MISSING'
                }), 401
            
            # Decode and validate token
            payload = TokenManager.decode_token(token)
            
            # Verify token type
            if payload.get('type') != 'access':
                return jsonify({
                    'error': 'Invalid token type',
                    'code': 'INVALID_TOKEN_TYPE'
                }), 401
            
            # Get user from database
            user = User.query.get(payload['user_id'])
            if not user:
                return jsonify({
                    'error': 'User not found',
                    'code': 'USER_NOT_FOUND'
                }), 401
            
            # Check if user is active
            if not user.is_active:
                return jsonify({
                    'error': 'User account is deactivated',
                    'code': 'ACCOUNT_DEACTIVATED'
                }), 401
            
            # Store user in Flask's g object for use in the route
            g.current_user = user
            
            return f(*args, **kwargs)
            
        except AuthError as e:
            return jsonify({
                'error': e.message,
                'code': 'AUTH_ERROR'
            }), e.status_code
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_FAILED'
            }), 401
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user = g.current_user
        
        # Check if user has admin privileges (you can customize this logic)
        if user.subscription_tier != 'enterprise' and user.username != 'admin':
            return jsonify({
                'error': 'Admin privileges required',
                'code': 'INSUFFICIENT_PRIVILEGES'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

def api_limit_required(f):
    """Decorator to check API usage limits."""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        user = g.current_user
        
        # Check if user can make API calls
        if not user.can_make_api_call():
            return jsonify({
                'error': 'API usage limit exceeded',
                'code': 'API_LIMIT_EXCEEDED',
                'details': {
                    'used': user.api_calls_used,
                    'limit': user.api_calls_limit,
                    'subscription_tier': user.subscription_tier
                }
            }), 429
        
        # Increment usage counter
        user.increment_api_usage()
        
        return f(*args, **kwargs)
    
    return decorated

def get_current_user() -> Optional[User]:
    """Get the current authenticated user from Flask's g object."""
    return getattr(g, 'current_user', None)

def create_auth_response(user: User, include_refresh: bool = True) -> Dict[str, Any]:
    """Create a standardized authentication response."""
    try:
        access_token = TokenManager.generate_access_token(user.id)
        
        response = {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 24 * 3600,  # 24 hours in seconds
            'user': user.to_dict()
        }
        
        if include_refresh:
            refresh_token = TokenManager.generate_refresh_token(user.id)
            response['refresh_token'] = refresh_token
        
        return response
        
    except Exception as e:
        raise AuthError(f"Failed to create auth response: {str(e)}")

