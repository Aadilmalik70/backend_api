"""
Comprehensive test suite for SERP Strategist authentication system.
Tests user registration, login, token management, and security features.
"""

import unittest
import json
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.app import create_app
from src.models.user import User, db
from src.utils.auth import TokenManager, PasswordValidator, SecurityUtils

class AuthenticationTestCase(unittest.TestCase):
    """Base test case for authentication tests."""
    
    def setUp(self):
        """Set up test environment before each test."""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test database
        db.create_all()
        
        # Test user data
        self.test_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'company': 'Test Company'
        }
        
        # Create a test user for login tests
        self.test_user = User(
            username='existinguser',
            email='existing@example.com',
            first_name='Existing',
            last_name='User'
        )
        self.test_user.set_password('ExistingPass123!')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def get_auth_headers(self, user=None):
        """Get authorization headers for authenticated requests."""
        if user is None:
            user = self.test_user
        
        token = TokenManager.generate_access_token(user.id)
        return {'Authorization': f'Bearer {token}'}

class UserRegistrationTests(AuthenticationTestCase):
    """Test user registration functionality."""
    
    def test_successful_registration(self):
        """Test successful user registration."""
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(self.test_user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('message', data)
        self.assertIn('user_id', data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        
        # Verify user was created in database
        user = User.find_by_email(self.test_user_data['email'])
        self.assertIsNotNone(user)
        self.assertEqual(user.username, self.test_user_data['username'])
        self.assertTrue(user.check_password(self.test_user_data['password']))
    
    def test_registration_missing_fields(self):
        """Test registration with missing required fields."""
        incomplete_data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # Missing password
        }
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'MISSING_REQUIRED_FIELDS')
    
    def test_registration_invalid_email(self):
        """Test registration with invalid email format."""
        invalid_data = self.test_user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_EMAIL')
    
    def test_registration_weak_password(self):
        """Test registration with weak password."""
        weak_data = self.test_user_data.copy()
        weak_data['password'] = 'weak'
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(weak_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_PASSWORD')
    
    def test_registration_duplicate_email(self):
        """Test registration with already registered email."""
        duplicate_data = self.test_user_data.copy()
        duplicate_data['email'] = self.test_user.email
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'EMAIL_EXISTS')
    
    def test_registration_duplicate_username(self):
        """Test registration with already taken username."""
        duplicate_data = self.test_user_data.copy()
        duplicate_data['username'] = self.test_user.username
        
        response = self.client.post(
            '/api/auth/register',
            data=json.dumps(duplicate_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'USERNAME_EXISTS')

class UserLoginTests(AuthenticationTestCase):
    """Test user login functionality."""
    
    def test_successful_login_with_email(self):
        """Test successful login using email."""
        login_data = {
            'email': self.test_user.email,
            'password': 'ExistingPass123!'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('message', data)
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)
        self.assertIn('user', data)
        
        # Verify token is valid
        token = data['access_token']
        payload = TokenManager.decode_token(token)
        self.assertEqual(payload['user_id'], self.test_user.id)
    
    def test_successful_login_with_username(self):
        """Test successful login using username."""
        login_data = {
            'username': self.test_user.username,
            'password': 'ExistingPass123!'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access_token', data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {
            'email': self.test_user.email,
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_CREDENTIALS')
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_CREDENTIALS')
    
    def test_login_inactive_user(self):
        """Test login with inactive user account."""
        # Deactivate test user
        self.test_user.is_active = False
        db.session.commit()
        
        login_data = {
            'email': self.test_user.email,
            'password': 'ExistingPass123!'
        }
        
        response = self.client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'ACCOUNT_DEACTIVATED')

class TokenManagementTests(AuthenticationTestCase):
    """Test JWT token management functionality."""
    
    def test_token_refresh(self):
        """Test refreshing access token with refresh token."""
        # Generate refresh token
        refresh_token = TokenManager.generate_refresh_token(self.test_user.id)
        
        refresh_data = {
            'refresh_token': refresh_token
        }
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response structure
        self.assertIn('access_token', data)
        self.assertIn('token_type', data)
        self.assertIn('expires_in', data)
        
        # Verify new token is valid
        new_token = data['access_token']
        payload = TokenManager.decode_token(new_token)
        self.assertEqual(payload['user_id'], self.test_user.id)
    
    def test_token_refresh_invalid_token(self):
        """Test token refresh with invalid refresh token."""
        refresh_data = {
            'refresh_token': 'invalid-token'
        }
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_REFRESH_TOKEN')
    
    def test_token_refresh_wrong_type(self):
        """Test token refresh with access token instead of refresh token."""
        # Use access token instead of refresh token
        access_token = TokenManager.generate_access_token(self.test_user.id)
        
        refresh_data = {
            'refresh_token': access_token
        }
        
        response = self.client.post(
            '/api/auth/refresh',
            data=json.dumps(refresh_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_TOKEN_TYPE')

class ProtectedRouteTests(AuthenticationTestCase):
    """Test protected route access and authentication decorators."""
    
    def test_get_current_user_info(self):
        """Test getting current user information with valid token."""
        headers = self.get_auth_headers()
        
        response = self.client.get(
            '/api/auth/me',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('user', data)
        user_data = data['user']
        self.assertEqual(user_data['id'], self.test_user.id)
        self.assertEqual(user_data['email'], self.test_user.email)
    
    def test_protected_route_no_token(self):
        """Test accessing protected route without token."""
        response = self.client.get('/api/auth/me')
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'TOKEN_MISSING')
    
    def test_protected_route_invalid_token(self):
        """Test accessing protected route with invalid token."""
        headers = {'Authorization': 'Bearer invalid-token'}
        
        response = self.client.get(
            '/api/auth/me',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'AUTH_ERROR')
    
    def test_update_user_profile(self):
        """Test updating user profile information."""
        headers = self.get_auth_headers()
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'company': 'New Company'
        }
        
        response = self.client.put(
            '/api/auth/me',
            data=json.dumps(update_data),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify updates
        self.assertEqual(data['user']['first_name'], 'Updated')
        self.assertEqual(data['user']['last_name'], 'Name')
        self.assertEqual(data['user']['company'], 'New Company')

class PasswordManagementTests(AuthenticationTestCase):
    """Test password change and reset functionality."""
    
    def test_change_password(self):
        """Test changing user password."""
        headers = self.get_auth_headers()
        
        change_data = {
            'current_password': 'ExistingPass123!',
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(
            '/api/auth/change-password',
            data=json.dumps(change_data),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify password was changed
        user = User.query.get(self.test_user.id)
        self.assertTrue(user.check_password('NewPassword123!'))
        self.assertFalse(user.check_password('ExistingPass123!'))
    
    def test_change_password_wrong_current(self):
        """Test changing password with wrong current password."""
        headers = self.get_auth_headers()
        
        change_data = {
            'current_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(
            '/api/auth/change-password',
            data=json.dumps(change_data),
            content_type='application/json',
            headers=headers
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['code'], 'INVALID_CURRENT_PASSWORD')
    
    def test_forgot_password(self):
        """Test forgot password functionality."""
        forgot_data = {
            'email': self.test_user.email
        }
        
        response = self.client.post(
            '/api/auth/forgot-password',
            data=json.dumps(forgot_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify reset token was generated
        user = User.query.get(self.test_user.id)
        self.assertIsNotNone(user.reset_token)
        self.assertIsNotNone(user.reset_token_expires)
    
    def test_reset_password(self):
        """Test password reset with valid token."""
        # Set up reset token
        reset_token = SecurityUtils.generate_reset_token()
        self.test_user.reset_token = reset_token
        self.test_user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        
        reset_data = {
            'reset_token': reset_token,
            'new_password': 'ResetPassword123!'
        }
        
        response = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps(reset_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify password was reset
        user = User.query.get(self.test_user.id)
        self.assertTrue(user.check_password('ResetPassword123!'))
        self.assertIsNone(user.reset_token)

class UtilityTests(AuthenticationTestCase):
    """Test authentication utility functions."""
    
    def test_password_validation(self):
        """Test password validation utility."""
        # Valid password
        valid, message = PasswordValidator.validate_password('ValidPass123!')
        self.assertTrue(valid)
        
        # Too short
        valid, message = PasswordValidator.validate_password('short')
        self.assertFalse(valid)
        self.assertIn('8 characters', message)
        
        # No uppercase
        valid, message = PasswordValidator.validate_password('lowercase123!')
        self.assertFalse(valid)
        self.assertIn('uppercase', message)
        
        # No lowercase
        valid, message = PasswordValidator.validate_password('UPPERCASE123!')
        self.assertFalse(valid)
        self.assertIn('lowercase', message)
        
        # No numbers
        valid, message = PasswordValidator.validate_password('NoNumbers!')
        self.assertFalse(valid)
        self.assertIn('number', message)
        
        # No special characters
        valid, message = PasswordValidator.validate_password('NoSpecial123')
        self.assertFalse(valid)
        self.assertIn('special character', message)
    
    def test_token_generation_and_validation(self):
        """Test JWT token generation and validation."""
        # Generate access token
        token = TokenManager.generate_access_token(self.test_user.id)
        self.assertIsInstance(token, str)
        
        # Decode token
        payload = TokenManager.decode_token(token)
        self.assertEqual(payload['user_id'], self.test_user.id)
        self.assertEqual(payload['type'], 'access')
        
        # Generate refresh token
        refresh_token = TokenManager.generate_refresh_token(self.test_user.id)
        refresh_payload = TokenManager.decode_token(refresh_token)
        self.assertEqual(refresh_payload['type'], 'refresh')
    
    def test_secure_token_generation(self):
        """Test secure token generation utilities."""
        # Generate verification token
        verification_token = SecurityUtils.generate_verification_token()
        self.assertIsInstance(verification_token, str)
        self.assertEqual(len(verification_token), 48)
        
        # Generate reset token
        reset_token = SecurityUtils.generate_reset_token()
        self.assertIsInstance(reset_token, str)
        self.assertEqual(len(reset_token), 48)
        
        # Ensure tokens are different
        self.assertNotEqual(verification_token, reset_token)

if __name__ == '__main__':
    unittest.main()

