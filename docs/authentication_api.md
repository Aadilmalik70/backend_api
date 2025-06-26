# SERP Strategist Authentication API Documentation

## Overview

The SERP Strategist Authentication API provides comprehensive user management and security features for the platform. This RESTful API handles user registration, authentication, profile management, and security operations using JWT (JSON Web Tokens) for stateless authentication.

## Base URL

```
https://api.serpstrategists.com/api/auth
```

For development:
```
http://localhost:5000/api/auth
```

## Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Token Types

The API uses two types of JWT tokens:

- **Access Token**: Short-lived (24 hours) token for API access
- **Refresh Token**: Long-lived (30 days) token for obtaining new access tokens

## API Endpoints

### User Registration

Register a new user account.

**Endpoint:** `POST /register`

**Request Body:**
```json
{
  "username": "string (required, 3-30 chars, alphanumeric + _ -)",
  "email": "string (required, valid email format)",
  "password": "string (required, min 8 chars, must include uppercase, lowercase, number, special char)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "company": "string (optional)"
}
```

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": 123,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": 123,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "company": "Example Corp",
    "full_name": "John Doe",
    "is_active": true,
    "is_verified": false,
    "subscription_tier": "free",
    "api_calls_used": 0,
    "api_calls_limit": 100,
    "api_calls_remaining": 100,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_login": null
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields, invalid email/username format, weak password
- `409 Conflict`: Email or username already exists

### User Login

Authenticate user and receive access tokens.

**Endpoint:** `POST /login`

**Request Body:**
```json
{
  "email": "string (email or username)",
  "password": "string"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    // User object (same as registration)
  }
}
```

**Error Responses:**
- `400 Bad Request`: Missing credentials
- `401 Unauthorized`: Invalid credentials or deactivated account

### Token Refresh

Obtain a new access token using a refresh token.

**Endpoint:** `POST /refresh`

**Request Body:**
```json
{
  "refresh_token": "string (required)"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Error Responses:**
- `400 Bad Request`: Missing refresh token
- `401 Unauthorized`: Invalid or expired refresh token

### Get Current User

Get the authenticated user's profile information.

**Endpoint:** `GET /me`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200):**
```json
{
  "user": {
    // User object (same as registration)
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token

### Update User Profile

Update the authenticated user's profile information.

**Endpoint:** `PUT /me`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "username": "string (optional)",
  "email": "string (optional)",
  "first_name": "string (optional)",
  "last_name": "string (optional)",
  "company": "string (optional)"
}
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    // Updated user object
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid data format
- `401 Unauthorized`: Missing or invalid token
- `409 Conflict`: Username or email already taken

### Change Password

Change the authenticated user's password.

**Endpoint:** `POST /change-password`

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "current_password": "string (required)",
  "new_password": "string (required, must meet password requirements)"
}
```

**Success Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Missing passwords or weak new password
- `401 Unauthorized`: Invalid current password or missing token

### Forgot Password

Initiate password reset process.

**Endpoint:** `POST /forgot-password`

**Request Body:**
```json
{
  "email": "string (required)"
}
```

**Success Response (200):**
```json
{
  "message": "If the email address is registered, a password reset link has been sent"
}
```

**Note:** This endpoint always returns success to prevent email enumeration attacks.

### Reset Password

Reset password using a reset token.

**Endpoint:** `POST /reset-password`

**Request Body:**
```json
{
  "reset_token": "string (required, received via email)",
  "new_password": "string (required, must meet password requirements)"
}
```

**Success Response (200):**
```json
{
  "message": "Password reset successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid or expired reset token, weak password

### Verify Email

Verify user's email address using verification token.

**Endpoint:** `POST /verify-email`

**Request Body:**
```json
{
  "verification_token": "string (required, received via email)"
}
```

**Success Response (200):**
```json
{
  "message": "Email verified successfully",
  "user": {
    // Updated user object with is_verified: true
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid verification token

### Logout

Logout the authenticated user.

**Endpoint:** `POST /logout`

**Headers:** `Authorization: Bearer <access_token>`

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

**Note:** Client should discard stored tokens after logout.

## Error Response Format

All error responses follow this format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE_CONSTANT"
}
```

Common error codes:
- `MISSING_REQUEST_BODY`: Request body is required
- `MISSING_REQUIRED_FIELDS`: Required fields are missing
- `INVALID_EMAIL`: Email format is invalid
- `INVALID_USERNAME`: Username format is invalid
- `INVALID_PASSWORD`: Password doesn't meet requirements
- `EMAIL_EXISTS`: Email is already registered
- `USERNAME_EXISTS`: Username is already taken
- `INVALID_CREDENTIALS`: Login credentials are incorrect
- `ACCOUNT_DEACTIVATED`: User account is deactivated
- `TOKEN_MISSING`: Authorization token is required
- `AUTH_ERROR`: Authentication failed
- `INSUFFICIENT_PRIVILEGES`: Admin privileges required
- `API_LIMIT_EXCEEDED`: API usage limit exceeded

## Password Requirements

Passwords must meet the following criteria:
- Minimum 8 characters, maximum 128 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

## Username Requirements

Usernames must meet the following criteria:
- Minimum 3 characters, maximum 30 characters
- Only letters, numbers, hyphens (-), and underscores (_) allowed
- Must be unique across the platform

## Rate Limiting

The API implements rate limiting to prevent abuse:
- Registration: 5 attempts per hour per IP
- Login: 10 attempts per hour per IP
- Password reset: 3 attempts per hour per email
- General API calls: Based on user's subscription tier

## Security Features

### JWT Token Security
- Tokens are signed with HS256 algorithm
- Access tokens expire after 24 hours
- Refresh tokens expire after 30 days
- Each token includes a unique JWT ID (jti) for potential revocation

### Password Security
- Passwords are hashed using Werkzeug's secure password hashing
- Original passwords are never stored in the database
- Password strength validation enforced

### Additional Security Measures
- Email enumeration protection in forgot password endpoint
- Secure token generation for verification and reset tokens
- Input validation and sanitization
- CORS protection configured
- SQL injection prevention through SQLAlchemy ORM

## Usage Examples

### JavaScript/Node.js Example

```javascript
// Registration
const registerUser = async (userData) => {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(userData),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  } else {
    const error = await response.json();
    throw new Error(error.error);
  }
};

// Login
const loginUser = async (credentials) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  } else {
    const error = await response.json();
    throw new Error(error.error);
  }
};

// Authenticated API call
const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (response.status === 401) {
    // Token might be expired, try to refresh
    await refreshToken();
    // Retry the request
    return makeAuthenticatedRequest(url, options);
  }
  
  return response;
};

// Token refresh
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  
  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    return data;
  } else {
    // Refresh token is invalid, redirect to login
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
};
```

### Python Example

```python
import requests
import json

class SERPStrategistAuth:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.access_token = None
        self.refresh_token = None
    
    def register(self, user_data):
        """Register a new user."""
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=user_data
        )
        
        if response.status_code == 201:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return data
        else:
            raise Exception(f"Registration failed: {response.json()['error']}")
    
    def login(self, credentials):
        """Login with email/username and password."""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json=credentials
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            return data
        else:
            raise Exception(f"Login failed: {response.json()['error']}")
    
    def get_headers(self):
        """Get authorization headers."""
        if not self.access_token:
            raise Exception("Not authenticated")
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self):
        """Get current user information."""
        response = requests.get(
            f"{self.base_url}/api/auth/me",
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get user info: {response.json()['error']}")
    
    def update_profile(self, update_data):
        """Update user profile."""
        response = requests.put(
            f"{self.base_url}/api/auth/me",
            json=update_data,
            headers=self.get_headers()
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to update profile: {response.json()['error']}")

# Usage example
auth = SERPStrategistAuth()

# Register new user
user_data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
}

try:
    result = auth.register(user_data)
    print(f"Registration successful: {result['user']['username']}")
except Exception as e:
    print(f"Registration failed: {e}")

# Login
credentials = {
    "email": "john@example.com",
    "password": "SecurePass123!"
}

try:
    result = auth.login(credentials)
    print(f"Login successful: {result['user']['username']}")
except Exception as e:
    print(f"Login failed: {e}")
```

## Integration with Frontend

### React Integration Example

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserInfo();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUserInfo = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      setUser(data.user);
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

## Testing

The authentication system includes comprehensive test coverage. Run tests using:

```bash
python -m pytest test_authentication.py -v
```

Test categories:
- User registration tests
- Login functionality tests
- Token management tests
- Protected route access tests
- Password management tests
- Utility function tests

## Deployment Considerations

### Environment Variables

Set the following environment variables in production:

```bash
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=your-database-connection-string
FLASK_ENV=production
```

### Security Checklist

- [ ] Use strong JWT secret key in production
- [ ] Enable HTTPS in production
- [ ] Configure proper CORS settings
- [ ] Set up rate limiting
- [ ] Enable logging and monitoring
- [ ] Configure email service for password resets
- [ ] Set up database backups
- [ ] Implement token blacklisting for enhanced security

## Support

For questions or issues with the authentication API, please contact:
- Email: support@serpstrategists.com
- Documentation: https://docs.serpstrategists.com
- GitHub Issues: https://github.com/Aadilmalik70/backend_api/issues

