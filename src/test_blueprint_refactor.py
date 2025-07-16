"""
Test script to verify the blueprint generator refactoring fixes the migration manager issue.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_blueprint_generator_import():
    """Test that the blueprint generator can be imported without the migration manager error."""
    try:
        from services.blueprint_generator import BlueprintGeneratorService
        print("✅ BlueprintGeneratorService imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_blueprint_utils_import():
    """Test that blueprint utils can be imported."""
    try:
        from services.blueprint_utils import get_migration_manager
        print("✅ Blueprint utils imported successfully")
        return True
    except Exception as e:
        print(f"❌ Blueprint utils import failed: {str(e)}")
        return False

def test_migration_manager_function():
    """Test that the migration manager function works correctly."""
    try:
        from services.blueprint_utils import get_migration_manager
        
        # This should not raise the "takes 0 positional arguments but 1 was given" error
        # since it's now a standalone function, not a class method
        result = get_migration_manager()
        print("✅ get_migration_manager() called successfully")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ get_migration_manager() failed: {str(e)}")
        return False

def test_service_initialization():
    """Test that the service can be initialized with mock API keys."""
    try:
        from services.blueprint_generator import BlueprintGeneratorService
        
        # Try to initialize with mock keys
        service = BlueprintGeneratorService(
            serpapi_key="test_serpapi_key",
            gemini_api_key="test_gemini_key"
        )
        print("✅ BlueprintGeneratorService initialized successfully")
        
        # Test service status
        status = service.get_service_status()
        print(f"Service status: {status.get('overall_status', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Service initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Blueprint Generator Refactoring")
    print("=" * 50)
    
    tests = [
        test_blueprint_generator_import,
        test_blueprint_utils_import, 
        test_migration_manager_function,
        test_service_initialization
    ]
    
    passed = 0
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The refactoring successfully fixed the migration manager issue.")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
