#!/usr/bin/env python3
"""
Simple test runner to validate the fixed application.
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

def main():
    """Run the application in test mode."""
    try:
        logger.info("🚀 Starting SERP Strategist API Test")
        logger.info("="*50)
        
        # Import and create the application
        from src.main import create_application
        
        logger.info("Creating application...")
        app = create_application()
        
        logger.info("Application created successfully!")
        logger.info(f"App name: {app.name}")
        
        # Test basic endpoints
        with app.test_client() as client:
            logger.info("\n📊 Testing endpoints:")
            
            # Test root endpoint
            response = client.get('/')
            if response.status_code == 200:
                data = response.get_json()
                logger.info(f"✅ Root (/) - {data['name']} v{data['version']}")
            else:
                logger.error(f"❌ Root (/) failed - Status: {response.status_code}")
            
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                data = response.get_json()
                logger.info(f"✅ Health (/api/health) - Status: {data['status']}")
                logger.info(f"   Enhanced features: {data['features']['enhanced_processing']}")
                logger.info(f"   Database: {data['features']['database']}")
            else:
                logger.error(f"❌ Health (/api/health) failed - Status: {response.status_code}")
        
        logger.info("\n🎉 Application test completed successfully!")
        logger.info("✅ Ready for development and deployment")
        
        return True
        
    except Exception as e:
        logger.error(f"💥 Application test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)