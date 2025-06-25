#!/usr/bin/env python3
"""
Simple Blueprint Test - Verify basic functionality
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test that we can import our new modules."""
    print("Testing basic imports...")
    
    try:
        # Test blueprint models
        from src.models.blueprint import Blueprint, Project, validate_blueprint_data
        print("✅ Blueprint models imported successfully")
        
        # Test services
        from src.services.blueprint_generator import BlueprintGeneratorService
        from src.services.blueprint_storage import BlueprintStorageService
        print("✅ Blueprint services imported successfully")
        
        # Test routes
        from src.routes.blueprints import blueprint_routes
        print("✅ Blueprint routes imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ General error: {e}")
        return False

def test_validation_functions():
    """Test validation functions."""
    print("Testing validation functions...")
    
    try:
        from src.models.blueprint import validate_blueprint_data, sanitize_keyword
        
        # Test keyword sanitization
        test_keyword = sanitize_keyword("  Content Marketing!@#  ")
        expected = "content marketing"
        if test_keyword == expected:
            print(f"✅ Keyword sanitization works: '{test_keyword}'")
        else:
            print(f"❌ Keyword sanitization failed: got '{test_keyword}', expected '{expected}'")
            return False
        
        # Test valid blueprint data
        valid_data = {
            'keyword': 'test keyword',
            'competitor_analysis': {'test': 'data'},
            'heading_structure': {'h1': 'Test Title'},
            'topic_clusters': {'primary_cluster': ['topic1']},
            'serp_features': {'features': []}
        }
        
        if validate_blueprint_data(valid_data):
            print("✅ Blueprint validation accepts valid data")
        else:
            print("❌ Blueprint validation rejected valid data")
            return False
        
        # Test invalid blueprint data
        invalid_data = {}
        if not validate_blueprint_data(invalid_data):
            print("✅ Blueprint validation rejects invalid data")
        else:
            print("❌ Blueprint validation accepted invalid data")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running Simple Blueprint Tests")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 2
    
    if test_basic_imports():
        tests_passed += 1
    
    if test_validation_functions():
        tests_passed += 1
    
    print("=" * 40)
    print(f"Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All basic tests passed!")
        print("\nNext steps:")
        print("1. Run the Flask app: python src/app_real.py")
        print("2. Test blueprint generation endpoint")
        print("3. Configure API keys for full functionality")
    else:
        print("❌ Some tests failed. Check the implementation.")
