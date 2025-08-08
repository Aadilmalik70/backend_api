#!/usr/bin/env python3
"""
Test script to verify import fixes and basic functionality.
"""

import os
import sys
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_main_import():
    """Test importing main.py."""
    try:
        logger.info("Testing main.py import...")
        from src.main import create_application
        logger.info("✅ main.py import successful")
        return True
    except Exception as e:
        logger.error(f"❌ main.py import failed: {e}")
        return False

def test_app_real_import():
    """Test importing app_real.py."""
    try:
        logger.info("Testing app_real.py import...")
        from src.app_real import create_app
        logger.info("✅ app_real.py import successful")
        return True
    except Exception as e:
        logger.error(f"❌ app_real.py import failed: {e}")
        return False

def test_app_creation():
    """Test creating the Flask application."""
    try:
        logger.info("Testing application creation...")
        from src.app_real import create_app
        app = create_app()
        logger.info("✅ Application creation successful")
        logger.info(f"Application name: {app.name}")
        logger.info(f"Enhanced features available: {getattr(app, 'enhanced_features_available', 'Unknown')}")
        return True, app
    except Exception as e:
        logger.error(f"❌ Application creation failed: {e}")
        return False, None

def test_health_endpoint(app):
    """Test the health endpoint."""
    try:
        logger.info("Testing health endpoint...")
        with app.test_client() as client:
            response = client.get('/api/health')
            data = response.get_json()
            logger.info(f"✅ Health endpoint response: {data['status']}")
            logger.info(f"Features: {data['features']}")
            logger.info(f"Services: {data['services']}")
            return True
    except Exception as e:
        logger.error(f"❌ Health endpoint test failed: {e}")
        return False

def test_root_endpoint(app):
    """Test the root endpoint."""
    try:
        logger.info("Testing root endpoint...")
        with app.test_client() as client:
            response = client.get('/')
            data = response.get_json()
            logger.info(f"✅ Root endpoint response: {data['name']} v{data['version']}")
            logger.info(f"Status: {data['status']}")
            return True
    except Exception as e:
        logger.error(f"❌ Root endpoint test failed: {e}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Starting import fix validation tests...")
    logger.info("="*60)
    
    # Test imports
    main_ok = test_main_import()
    app_real_ok = test_app_real_import()
    
    if not (main_ok and app_real_ok):
        logger.error("💥 Import tests failed!")
        return False
    
    # Test application creation
    app_ok, app = test_app_creation()
    if not app_ok:
        logger.error("💥 Application creation failed!")
        return False
    
    # Test endpoints
    health_ok = test_health_endpoint(app)
    root_ok = test_root_endpoint(app)
    
    # Summary
    logger.info("="*60)
    if all([main_ok, app_real_ok, app_ok, health_ok, root_ok]):
        logger.info("🎉 All tests passed! Import fixes successful!")
        logger.info("✅ Application is ready for development")
        return True
    else:
        logger.error("💥 Some tests failed!")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)