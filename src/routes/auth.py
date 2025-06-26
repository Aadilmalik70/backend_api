"""
Authentication routes for SERP Strategist backend.
Handles user registration, login, logout, password reset, and token management.
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest
from datetime import datetime, timedelta, timezone
import re
from typing import Dict, Any, Tuple

from src.models.user import User, db
from src.utils.auth import (
    TokenManager, PasswordValidator, SecurityUtils, AuthError,
    token_required, get_current_user, create_auth_response
)

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format and requirements."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 30:
        return False, "Username must be less than 30 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, hyphens, and underscores"
    
    return True, "Username is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user account."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        # Extract required fields
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Optional fields
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        company = data.get('company', '').strip()
        
        # Validate required fields
        if not all([username, email, password]):
            return jsonify({
                'error': 'Username, email, and password are required',
                'code': 'MISSING_REQUIRED_FIELDS'
            }), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({
                'error': 'Invalid email format',
                'code': 'INVALID_EMAIL'
            }), 400
        
        # Validate username
        username_valid, username_error = validate_username(username)
        if not username_valid:
            return jsonify({
                'error': username_error,
                'code': 'INVALID_USERNAME'
            }), 400
        
        # Validate password
        password_valid, password_error = PasswordValidator.validate_password(password)
        if not password_valid:
            return jsonify({
                'error': password_error,
                'code': 'INVALID_PASSWORD'
            }), 400
        
        # Check if user already exists
        if User.find_by_email(email):
            return jsonify({
                'error': 'Email address is already registered',
                'code': 'EMAIL_EXISTS'
            }), 409
        
        if User.find_by_username(username):
            return jsonify({
                'error': 'Username is already taken',
                'code': 'USERNAME_EXISTS'
            }), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            first_name=first_name or None,
            last_name=last_name or None,
            company=company or None,
            verification_token=SecurityUtils.generate_verification_token()
        )
        user.set_password(password)
        
        # Save user to database
        db.session.add(user)
        db.session.commit()
        
        # Create authentication response
        auth_response = create_auth_response(user)
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user.id,
            **auth_response
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'error': 'Registration failed',
            'code': 'REGISTRATION_FAILED'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return access token."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        # Extract login credentials
        login_identifier = data.get('email') or data.get('username', '')
        password = data.get('password', '')
        
        if not all([login_identifier, password]):
            return jsonify({
                'error': 'Email/username and password are required',
                'code': 'MISSING_CREDENTIALS'
            }), 400
        
        # Find user by email or username
        user = None
        if '@' in login_identifier:
            user = User.find_by_email(login_identifier.lower())
        else:
            user = User.find_by_username(login_identifier)
        
        # Validate user and password
        if not user or not user.check_password(password):
            return jsonify({
                'error': 'Invalid email/username or password',
                'code': 'INVALID_CREDENTIALS'
            }), 401
        
        # Check if user account is active
        if not user.is_active:
            return jsonify({
                'error': 'Account is deactivated',
                'code': 'ACCOUNT_DEACTIVATED'
            }), 401
        
        # Update last login timestamp
        user.update_last_login()
        
        # Create authentication response
        auth_response = create_auth_response(user)
        
        return jsonify({
            'message': 'Login successful',
            **auth_response
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'Login failed',
            'code': 'LOGIN_FAILED'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token using refresh token."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({
                'error': 'Refresh token is required',
                'code': 'MISSING_REFRESH_TOKEN'
            }), 400
        
        # Decode and validate refresh token
        try:
            payload = TokenManager.decode_token(refresh_token)
        except AuthError as e:
            return jsonify({
                'error': e.message,
                'code': 'INVALID_REFRESH_TOKEN'
            }), 401
        
        # Verify token type
        if payload.get('type') != 'refresh':
            return jsonify({
                'error': 'Invalid token type',
                'code': 'INVALID_TOKEN_TYPE'
            }), 401
        
        # Get user from database
        user = User.query.get(payload['user_id'])
        if not user or not user.is_active:
            return jsonify({
                'error': 'User not found or inactive',
                'code': 'USER_NOT_FOUND'
            }), 401
        
        # Generate new access token
        access_token = TokenManager.generate_access_token(user.id)
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 24 * 3600
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'Token refresh failed',
            'code': 'REFRESH_FAILED'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user_info():
    """Get current user's profile information."""
    try:
        user = get_current_user()
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get user info error: {str(e)}")
        return jsonify({
            'error': 'Failed to get user information',
            'code': 'USER_INFO_FAILED'
        }), 500

@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_current_user():
    """Update current user's profile information."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name'].strip() or None
        
        if 'last_name' in data:
            user.last_name = data['last_name'].strip() or None
        
        if 'company' in data:
            user.company = data['company'].strip() or None
        
        # Update username if provided and valid
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username != user.username:
                username_valid, username_error = validate_username(new_username)
                if not username_valid:
                    return jsonify({
                        'error': username_error,
                        'code': 'INVALID_USERNAME'
                    }), 400
                
                # Check if username is already taken
                if User.find_by_username(new_username):
                    return jsonify({
                        'error': 'Username is already taken',
                        'code': 'USERNAME_EXISTS'
                    }), 409
                
                user.username = new_username
        
        # Update email if provided and valid
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if new_email != user.email:
                if not validate_email(new_email):
                    return jsonify({
                        'error': 'Invalid email format',
                        'code': 'INVALID_EMAIL'
                    }), 400
                
                # Check if email is already taken
                if User.find_by_email(new_email):
                    return jsonify({
                        'error': 'Email address is already registered',
                        'code': 'EMAIL_EXISTS'
                    }), 409
                
                user.email = new_email
                user.is_verified = False  # Require re-verification for new email
        
        # Update timestamp
        user.updated_at = datetime.now(timezone.utc)
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update user error: {str(e)}")
        return jsonify({
            'error': 'Failed to update profile',
            'code': 'UPDATE_FAILED'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user's password."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not all([current_password, new_password]):
            return jsonify({
                'error': 'Current password and new password are required',
                'code': 'MISSING_PASSWORDS'
            }), 400
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'error': 'Current password is incorrect',
                'code': 'INVALID_CURRENT_PASSWORD'
            }), 401
        
        # Validate new password
        password_valid, password_error = PasswordValidator.validate_password(new_password)
        if not password_valid:
            return jsonify({
                'error': password_error,
                'code': 'INVALID_NEW_PASSWORD'
            }), 400
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Change password error: {str(e)}")
        return jsonify({
            'error': 'Failed to change password',
            'code': 'PASSWORD_CHANGE_FAILED'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset process."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        email = data.get('email', '').strip().lower()
        if not email:
            return jsonify({
                'error': 'Email is required',
                'code': 'MISSING_EMAIL'
            }), 400
        
        # Find user by email
        user = User.find_by_email(email)
        
        # Always return success to prevent email enumeration
        # In a real implementation, you would send an email here
        if user and user.is_active:
            # Generate reset token
            reset_token = SecurityUtils.generate_reset_token()
            user.reset_token = reset_token
            user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            db.session.commit()
            
            # TODO: Send password reset email
            current_app.logger.info(f"Password reset requested for user {user.id}")
        
        return jsonify({
            'message': 'If the email address is registered, a password reset link has been sent'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({
            'error': 'Failed to process password reset request',
            'code': 'FORGOT_PASSWORD_FAILED'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        reset_token = data.get('reset_token', '')
        new_password = data.get('new_password', '')
        
        if not all([reset_token, new_password]):
            return jsonify({
                'error': 'Reset token and new password are required',
                'code': 'MISSING_REQUIRED_FIELDS'
            }), 400
        
        # Find user by reset token
        user = User.find_by_reset_token(reset_token)
        if not user:
            return jsonify({
                'error': 'Invalid or expired reset token',
                'code': 'INVALID_RESET_TOKEN'
            }), 400
        
        # Check if token is expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
            return jsonify({
                'error': 'Reset token has expired',
                'code': 'EXPIRED_RESET_TOKEN'
            }), 400
        
        # Validate new password
        password_valid, password_error = PasswordValidator.validate_password(new_password)
        if not password_valid:
            return jsonify({
                'error': password_error,
                'code': 'INVALID_PASSWORD'
            }), 400
        
        # Update password and clear reset token
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Password reset successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({
            'error': 'Failed to reset password',
            'code': 'RESET_PASSWORD_FAILED'
        }), 500

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Verify user's email address using verification token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'MISSING_REQUEST_BODY'
            }), 400
        
        verification_token = data.get('verification_token', '')
        if not verification_token:
            return jsonify({
                'error': 'Verification token is required',
                'code': 'MISSING_VERIFICATION_TOKEN'
            }), 400
        
        # Find user by verification token
        user = User.find_by_verification_token(verification_token)
        if not user:
            return jsonify({
                'error': 'Invalid verification token',
                'code': 'INVALID_VERIFICATION_TOKEN'
            }), 400
        
        # Mark user as verified
        user.is_verified = True
        user.verification_token = None
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'message': 'Email verified successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({
            'error': 'Failed to verify email',
            'code': 'EMAIL_VERIFICATION_FAILED'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (token invalidation would be handled by client)."""
    try:
        user = get_current_user()
        current_app.logger.info(f"User {user.id} logged out")
        
        # In a production system, you might want to maintain a token blacklist
        # For now, we'll just return a success response
        return jsonify({
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'Logout failed',
            'code': 'LOGOUT_FAILED'
        }), 500

# Error handlers for the auth blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request',
        'code': 'BAD_REQUEST'
    }), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'error': 'Unauthorized',
        'code': 'UNAUTHORIZED'
    }), 401

@auth_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Forbidden',
        'code': 'FORBIDDEN'
    }), 403

@auth_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found',
        'code': 'NOT_FOUND'
    }), 404

@auth_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

