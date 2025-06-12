# Zoho Mail SMTP Configuration Guide
# File: backend_api/config/email_config.py

import os
from datetime import datetime
from flask_mail import Mail

class ZohoEmailConfig:
    """Zoho Mail SMTP Configuration for Flask-Mail"""
    
    # Zoho SMTP settings
    MAIL_SERVER = 'smtp.zoho.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    
    # Your Zoho credentials (use environment variables)
    MAIL_USERNAME = os.environ.get('ZOHO_EMAIL') or 'noreply@yourdomain.com'
    MAIL_PASSWORD = os.environ.get('ZOHO_PASSWORD') or 'your-password'
    MAIL_DEFAULT_SENDER = os.environ.get('ZOHO_EMAIL') or 'noreply@yourdomain.com'
    
    # Rate limiting to avoid being flagged
    MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = False

# Initialize Flask-Mail
def init_mail(app):
    """Initialize Flask-Mail with Zoho configuration"""
    app.config.update(
        MAIL_SERVER=ZohoEmailConfig.MAIL_SERVER,
        MAIL_PORT=ZohoEmailConfig.MAIL_PORT,
        MAIL_USE_TLS=ZohoEmailConfig.MAIL_USE_TLS,
        MAIL_USE_SSL=ZohoEmailConfig.MAIL_USE_SSL,
        MAIL_USERNAME=ZohoEmailConfig.MAIL_USERNAME,
        MAIL_PASSWORD=ZohoEmailConfig.MAIL_PASSWORD,
        MAIL_DEFAULT_SENDER=ZohoEmailConfig.MAIL_DEFAULT_SENDER
    )
    
    mail = Mail(app)
    return mail

# Email service class for sending different types of emails
class EmailService:
    def __init__(self, mail):
        self.mail = mail
    
    def send_welcome_email(self, user_email, user_name):
        """Send welcome email to new users"""
        from flask_mail import Message
        
        msg = Message(
            subject="Welcome to SEO Analytics Pro!",
            recipients=[user_email],
            html=self._get_welcome_template(user_name),
            sender=ZohoEmailConfig.MAIL_DEFAULT_SENDER
        )
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send welcome email: {str(e)}")
            return False
    
    def send_verification_email(self, user_email, verification_token):
        """Send email verification"""
        from flask_mail import Message
        
        verification_url = f"{os.environ.get('FRONTEND_URL')}/auth/verify-email?token={verification_token}"
        
        msg = Message(
            subject="Verify Your Email Address",
            recipients=[user_email],
            html=self._get_verification_template(verification_url),
            sender=ZohoEmailConfig.MAIL_DEFAULT_SENDER
        )
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, user_email, reset_token, user_name):
        """Send password reset email"""
        from flask_mail import Message
        
        reset_url = f"{os.environ.get('FRONTEND_URL')}/auth/reset-password?token={reset_token}"
        
        msg = Message(
            subject="Reset Your Password",
            recipients=[user_email],
            html=self._get_password_reset_template(user_name, reset_url),
            sender=ZohoEmailConfig.MAIL_DEFAULT_SENDER
        )
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send password reset email: {str(e)}")
            return False
    
    def send_subscription_confirmation(self, user_email, user_name, plan_name, amount):
        """Send subscription confirmation"""
        from flask_mail import Message
        
        msg = Message(
            subject=f"Subscription Confirmed - {plan_name}",
            recipients=[user_email],
            html=self._get_subscription_template(user_name, plan_name, amount),
            sender=ZohoEmailConfig.MAIL_DEFAULT_SENDER
        )
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            print(f"Failed to send subscription email: {str(e)}")
            return False
    
    # Email templates (simplified for space)
    def _get_welcome_template(self, user_name):
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Welcome to SEO Analytics Pro!</h2>
            <p>Hi {user_name}, thank you for joining us!</p>
            <a href="{os.environ.get('FRONTEND_URL', 'https://yourapp.com')}/dashboard" 
               style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Start Analyzing →
            </a>
        </div>
        """
    
    def _get_verification_template(self, verification_url):
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Verify Your Email</h2>
            <a href="{verification_url}" 
               style="background: #48bb78; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Verify Email →
            </a>
        </div>
        """
    
    def _get_password_reset_template(self, user_name, reset_url):
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Reset Your Password</h2>
            <p>Hi {user_name}, click below to reset your password:</p>
            <a href="{reset_url}" 
               style="background: #f56565; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Reset Password →
            </a>
        </div>
        """
    
    def _get_subscription_template(self, user_name, plan_name, amount):
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #667eea;">Subscription Confirmed! 🎉</h2>
            <p>Hi {user_name}, thank you for upgrading to {plan_name} (${amount})!</p>
            <a href="{os.environ.get('FRONTEND_URL', 'https://yourapp.com')}/dashboard" 
               style="background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px;">
                Access Dashboard →
            </a>
        </div>
        """

# Rate limiting for email sending
class EmailRateLimiter:
    """Rate limiter to prevent email spam and stay within Zoho limits"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.daily_limit = 1000  # Zoho Mail Lite typical limit
        self.hourly_limit = 100   # Conservative hourly limit
    
    def can_send_email(self, email_type='general'):
        """Check if we can send an email based on rate limits"""
        if not self.redis:
            return True, "OK"  # Allow if no Redis (fallback)
        
        today_key = f"email_count:daily:{datetime.now().strftime('%Y-%m-%d')}"
        hour_key = f"email_count:hourly:{datetime.now().strftime('%Y-%m-%d:%H')}"
        
        daily_count = int(self.redis.get(today_key) or 0)
        hourly_count = int(self.redis.get(hour_key) or 0)
        
        if daily_count >= self.daily_limit:
            return False, "Daily email limit reached"
        
        if hourly_count >= self.hourly_limit:
            return False, "Hourly email limit reached"
        
        return True, "OK"
    
    def increment_email_count(self):
        """Increment email counters"""
        if not self.redis:
            return
        
        today_key = f"email_count:daily:{datetime.now().strftime('%Y-%m-%d')}"
        hour_key = f"email_count:hourly:{datetime.now().strftime('%Y-%m-%d:%H')}"
        
        # Increment counters with expiration
        self.redis.incr(today_key)
        self.redis.expire(today_key, 86400)  # 24 hours
        
        self.redis.incr(hour_key)
        self.redis.expire(hour_key, 3600)   # 1 hour
