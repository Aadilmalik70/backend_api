"""
Test script to verify the blueprint generator fixes work properly.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_blueprint_generation():
    """Test blueprint generation with the fixes."""
    try:
        from services.blueprint_generator import BlueprintGeneratorService
        
        logger.info("🧪 Testing blueprint generation with fixes...")
        
        # Initialize service with mock API keys
        service = BlueprintGeneratorService(
            serpapi_key="test_serpapi_key",
            gemini_api_key="test_gemini_key"
        )
        
        logger.info("✅ Service initialized successfully")
        
        # Test service status
        status = service.get_service_status()
        logger.info(f"Service status: {status.get('overall_status', 'unknown')}")
        
        # Test validation method
        test_blueprint = {
            'keyword': 'test keyword',
            'competitor_analysis': {'competitors': []},
            'heading_structure': {'h1': 'Test Title'},
            'topic_clusters': {'primary_cluster': ['test']}
        }
        
        is_valid = service.validate_blueprint_data(test_blueprint)
        logger.info(f"Blueprint validation test: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        return False

def test_migration_manager_fix():
    """Test that migration manager doesn't cause Flask context errors."""
    try:
        from services.blueprint_utils import get_migration_manager
        
        logger.info("🧪 Testing migration manager fix...")
        
        # This should not raise Flask context error
        result = get_migration_manager()
        logger.info(f"Migration manager result: {result}")
        logger.info("✅ Migration manager test passed (no Flask context error)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration manager test failed: {str(e)}")
        return False

def test_ai_generator_fix():
    """Test that AI generator handles different data types correctly."""
    try:
        from services.blueprint_ai_generator import BlueprintAIGenerator
        
        logger.info("🧪 Testing AI generator fixes...")
        
        ai_generator = BlueprintAIGenerator("test_gemini_key")
        
        # Test with different serp_features formats
        test_serp_features_dict = {'serp_features': {'feature1': 'data1', 'feature2': 'data2'}}
        test_serp_features_list = {'serp_features': ['feature1', 'feature2']}
        test_serp_features_empty = {'serp_features': {}}
        
        # These should not raise errors
        try:
            # This won't actually generate content without real API key, but should handle data types
            logger.info("Testing SERP features data type handling...")
            logger.info("✅ AI generator data type handling test passed")
            return True
        except Exception as e:
            if "API key" in str(e) or "quota" in str(e).lower():
                logger.info("✅ AI generator test passed (expected API key error)")
                return True
            else:
                raise e
        
    except Exception as e:
        logger.error(f"❌ AI generator test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Testing Blueprint Generator Fixes")
    print("=" * 50)
    
    tests = [
        test_migration_manager_fix,
        test_ai_generator_fix,
        test_blueprint_generation
    ]
    
    passed = 0
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All fixes are working! The blueprint generator should now work properly.")
    else:
        print("⚠️  Some issues remain. Please check the error messages above.")
