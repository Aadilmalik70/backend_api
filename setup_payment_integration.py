#!/usr/bin/env python3
"""
Setup script for SERP Strategist Payment Integration

This script sets up the payment integration system including:
- Database initialization with subscription models
- Default subscription plans creation
- Environment validation
- System health checks

Usage:
    python setup_payment_integration.py
"""

import os
import sys
import logging
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

def setup_logging():
    """Configure logging for setup script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    logger = logging.getLogger(__name__)
    
    required_vars = {
        'SECRET_KEY': 'Flask secret key for sessions',
        'DATABASE_URL': 'Database connection URL'
    }
    
    payment_vars = {
        'RAZORPAY_KEY_ID': 'Razorpay API key ID',
        'RAZORPAY_KEY_SECRET': 'Razorpay API secret key',
        'RAZORPAY_WEBHOOK_SECRET': 'Razorpay webhook secret'
    }
    
    google_vars = {
        'GOOGLE_API_KEY': 'Google API key for services',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Google Custom Search Engine ID',
        'GEMINI_API_KEY': 'Google Gemini API key'
    }
    
    missing_required = []
    missing_payment = []
    missing_google = []
    
    # Check required variables
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_required.append(f"{var} ({description})")
    
    # Check payment variables
    for var, description in payment_vars.items():
        if not os.getenv(var):
            missing_payment.append(f"{var} ({description})")
    
    # Check Google API variables
    for var, description in google_vars.items():
        if not os.getenv(var):
            missing_google.append(f"{var} ({description})")
    
    # Report results
    if missing_required:
        logger.error("❌ Missing required environment variables:")
        for var in missing_required:
            logger.error(f"  - {var}")
        return False
    
    if missing_payment:
        logger.warning("⚠️  Missing Razorpay environment variables (payment features will be limited):")
        for var in missing_payment:
            logger.warning(f"  - {var}")
    
    if missing_google:
        logger.warning("⚠️  Missing Google API environment variables (some features will be limited):")
        for var in missing_google:
            logger.warning(f"  - {var}")
    
    logger.info("✅ Core environment variables are configured")
    return True

def setup_database():
    """Initialize database with all models including payment tables"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import Flask app factory
        from app_realtime import create_realtime_app
        
        logger.info("🗄️  Initializing database with payment models...")
        
        # Create Flask app to initialize database
        app, _ = create_realtime_app()
        
        with app.app_context():
            # Check if database was initialized successfully
            if hasattr(app, 'db') and app.db is not None:
                logger.info("✅ Database initialized successfully with payment models")
                
                # Try to query subscription plans to verify setup
                from src.models.subscription import SubscriptionPlan
                plan_count = SubscriptionPlan.query.count()
                logger.info(f"📋 Found {plan_count} subscription plans in database")
                
                if plan_count == 0:
                    logger.warning("⚠️  No subscription plans found - they should be created automatically")
                
                return True
            else:
                logger.error("❌ Database initialization failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        return False

def verify_payment_service():
    """Verify payment service configuration"""
    logger = logging.getLogger(__name__)
    
    try:
        from src.services.payment_service import PaymentService
        
        logger.info("💳 Verifying payment service configuration...")
        
        payment_service = PaymentService()
        
        if payment_service.is_available():
            logger.info("✅ Payment service is available and configured")
        else:
            logger.warning("⚠️  Payment service is not available (Razorpay credentials missing)")
        
        # Test getting subscription plans
        plans = payment_service.get_subscription_plans()
        logger.info(f"📋 Retrieved {len(plans)} subscription plans:")
        
        for plan in plans:
            logger.info(f"  - {plan['name']}: ₹{plan['price_monthly']}/month ({plan['blueprint_limit']} blueprints)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Payment service verification failed: {str(e)}")
        return False

def verify_models():
    """Verify all database models are working correctly"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🔍 Verifying database models...")
        
        # Import all models
        from src.models.user import User
        from src.models.blueprint import Blueprint
        from src.models.subscription import (
            SubscriptionPlan, UserSubscription, PaymentTransaction, UsageEvent
        )
        
        # Create Flask app context
        from app_realtime import create_realtime_app
        app, _ = create_realtime_app()
        
        with app.app_context():
            # Test each model with a simple count query
            models_to_test = [
                ('Users', User),
                ('Blueprints', Blueprint),
                ('Subscription Plans', SubscriptionPlan),
                ('User Subscriptions', UserSubscription),
                ('Payment Transactions', PaymentTransaction),
                ('Usage Events', UsageEvent)
            ]
            
            for model_name, model_class in models_to_test:
                try:
                    count = model_class.query.count()
                    logger.info(f"  ✅ {model_name}: {count} records")
                except Exception as e:
                    logger.error(f"  ❌ {model_name}: Query failed - {str(e)}")
                    return False
        
        logger.info("✅ All database models are working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model verification failed: {str(e)}")
        return False

def run_health_check():
    """Run system health check"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🏥 Running system health check...")
        
        from app_realtime import create_realtime_app
        app, _ = create_realtime_app()
        
        with app.app_context():
            # Test health check endpoint logic
            from src.models import check_database_health
            
            if hasattr(app, 'db') and app.db is not None:
                db_health = check_database_health(app.db.session)
                
                if db_health['status'] == 'healthy':
                    logger.info("✅ Database health check passed")
                    logger.info(f"   📊 Database counts: {db_health.get('counts', {})}")
                else:
                    logger.error(f"❌ Database health check failed: {db_health.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error("❌ Database not available for health check")
                return False
        
        logger.info("✅ System health check completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    logger = setup_logging()
    
    print("🚀 SERP Strategist Payment Integration Setup")
    print("=" * 60)
    print(f"⏰ Setup Time: {datetime.now().isoformat()}")
    print()
    
    success = True
    
    # Step 1: Validate environment
    logger.info("📋 Step 1: Validating environment variables...")
    if not validate_environment():
        success = False
        logger.error("❌ Environment validation failed")
    else:
        logger.info("✅ Environment validation completed")
    print()
    
    # Step 2: Setup database
    logger.info("🗄️  Step 2: Setting up database...")
    if not setup_database():
        success = False
        logger.error("❌ Database setup failed")
    else:
        logger.info("✅ Database setup completed")
    print()
    
    # Step 3: Verify payment service
    logger.info("💳 Step 3: Verifying payment service...")
    if not verify_payment_service():
        success = False
        logger.error("❌ Payment service verification failed")
    else:
        logger.info("✅ Payment service verification completed")
    print()
    
    # Step 4: Verify models
    logger.info("🔍 Step 4: Verifying database models...")
    if not verify_models():
        success = False
        logger.error("❌ Model verification failed")
    else:
        logger.info("✅ Model verification completed")
    print()
    
    # Step 5: Run health check
    logger.info("🏥 Step 5: Running system health check...")
    if not run_health_check():
        success = False
        logger.error("❌ Health check failed")
    else:
        logger.info("✅ Health check completed")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 SETUP SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 Payment integration setup completed successfully!")
        print()
        print("✅ Next steps:")
        print("1. Start the Flask server: python src/main.py")
        print("2. Test the payment endpoints with: python test_payment_integration.py")
        print("3. Configure Razorpay credentials for full payment functionality")
        print("4. Set up webhook endpoint in Razorpay dashboard")
        print()
        print("🔗 Available endpoints:")
        print("- Payment: http://localhost:5000/api/payment/*")
        print("- Health: http://localhost:5000/api/health")
        print("- Blueprints: http://localhost:5000/api/blueprints/*")
        
    else:
        print("❌ Payment integration setup failed!")
        print()
        print("🔧 Troubleshooting:")
        print("1. Check environment variables in .env file")
        print("2. Ensure database is accessible")
        print("3. Verify all required dependencies are installed")
        print("4. Check logs above for specific error details")
    
    print()
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Setup crashed: {str(e)}")
        sys.exit(1)