from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    # Primary fields
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile fields
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    
    # Authentication and security
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    
    # Subscription and usage
    subscription_tier = db.Column(db.String(20), default='free', nullable=False)  # free, pro, enterprise
    api_calls_used = db.Column(db.Integer, default=0, nullable=False)
    api_calls_limit = db.Column(db.Integer, default=100, nullable=False)  # Monthly limit
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def increment_api_usage(self) -> bool:
        """Increment API usage counter. Returns False if limit exceeded."""
        if self.api_calls_used >= self.api_calls_limit:
            return False
        self.api_calls_used += 1
        db.session.commit()
        return True

    def reset_monthly_usage(self) -> None:
        """Reset monthly API usage counter."""
        self.api_calls_used = 0
        db.session.commit()

    def can_make_api_call(self) -> bool:
        """Check if user can make an API call within their limit."""
        return self.is_active and self.api_calls_used < self.api_calls_limit

    def get_full_name(self) -> str:
        """Get user's full name or username if names not provided."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert user to dictionary. Set include_sensitive=True for admin views."""
        user_dict = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company': self.company,
            'full_name': self.get_full_name(),
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'subscription_tier': self.subscription_tier,
            'api_calls_used': self.api_calls_used,
            'api_calls_limit': self.api_calls_limit,
            'api_calls_remaining': max(0, self.api_calls_limit - self.api_calls_used),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            user_dict.update({
                'verification_token': self.verification_token,
                'reset_token': self.reset_token,
                'reset_token_expires': self.reset_token_expires.isoformat() if self.reset_token_expires else None
            })
        
        return user_dict

    @staticmethod
    def find_by_email(email: str) -> Optional['User']:
        """Find user by email address."""
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def find_by_username(username: str) -> Optional['User']:
        """Find user by username."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def find_by_verification_token(token: str) -> Optional['User']:
        """Find user by verification token."""
        return User.query.filter_by(verification_token=token).first()

    @staticmethod
    def find_by_reset_token(token: str) -> Optional['User']:
        """Find user by password reset token."""
        return User.query.filter_by(reset_token=token).first()

