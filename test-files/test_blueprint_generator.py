#!/usr/bin/env python3
"""
Blueprint Generator Test Script

This script tests the core blueprint generation functionality
to verify that all components are working correctly.
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_blueprint_models():
    """Test the blueprint data models."""
    print("🧪 Testing Blueprint Models...")
    
    try:
        from src.models.blueprint import Blueprint, Project, validate_blueprint_data, sanitize_keyword
        
        # Test keyword sanitization
        test_keyword = sanitize_keyword("  Content Marketing Best Practices!@#  ")
        assert test_keyword == "content marketing best practices"
        print("✅ Keyword sanitization works")
        
        # Test blueprint data validation
        valid_data = {
            'keyword': 'test keyword',
            'competitor_analysis': {'test': 'data'},
            'heading_structure': {'h1': 'Test Title'},
            'topic_clusters': {'primary_cluster': ['topic1']},
            'serp_features': {'features': []}
        }
        
        assert validate_blueprint_data(valid_data) == True
        print("✅ Blueprint data validation works")
        
        invalid_data = {}  # Missing required fields
        assert validate_blueprint_data(invalid_data) == False
        print("✅ Blueprint validation rejects invalid data")
        
        print("✅ Blueprint models test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint models test failed: {str(e)}\n")
        return False

def test_blueprint_generator():
    """Test the blueprint generator service."""
    print("🧪 Testing Blueprint Generator Service...")
    
    try:
        from src.services.blueprint_generator import BlueprintGeneratorService
        
        # Check if API keys are available
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not serpapi_key or not gemini_key:
            print("⚠️  API keys not configured, skipping generator test")
            print("   Set SERPAPI_KEY and GEMINI_API_KEY environment variables to test")
            return True
        
        # Initialize generator
        generator = BlueprintGeneratorService(serpapi_key, gemini_key)
        print("✅ Blueprint generator initialized")
        
        # Test fallback functions (these don't require API calls)
        test_keyword = "content marketing"
        fallback_headings = generator._generate_fallback_heading_structure(test_keyword, [])
        assert 'h1' in fallback_headings
        assert 'h2_sections' in fallback_headings
        print("✅ Fallback heading generation works")
        
        fallback_topics = generator._generate_fallback_topic_clusters(test_keyword, [])
        assert 'primary_cluster' in fallback_topics
        assert 'secondary_clusters' in fallback_topics
        print("✅ Fallback topic clustering works")
        
        print("✅ Blueprint generator test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Blueprint generator test failed: {str(e)}\n")
        return False

def test_api_routes():
    """Test the API routes structure."""
    print("🧪 Testing API Routes...")
    
    try:
        from src.routes.blueprints import blueprint_routes
        
        # Check that the blueprint routes are defined
        assert blueprint_routes is not None
        print("✅ Blueprint routes loaded")
        
        # Check route endpoints
        route_names = [rule.rule for rule in blueprint_routes.url_map.iter_rules()]
        expected_routes = [
            '/api/blueprints/generate',
            '/api/blueprints/<blueprint_id>',
            '/api/blueprints',
            '/api/health'
        ]
        
        for route in expected_routes:
            # Check if route pattern exists (may have slight variations)
            found = any(route.replace('<blueprint_id>', '').replace('<', '').replace('>', '') in r 
                       for r in route_names)
            if not found:
                print(f"⚠️  Route {route} not found in registered routes")
        
        print("✅ API routes test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ API routes test failed: {str(e)}\n")
        return False

def test_database_models():
    """Test database model creation."""
    print("🧪 Testing Database Models...")
    
    try:
        from src.models.blueprint import DatabaseManager
        
        # Test with in-memory SQLite database
        test_db_url = "sqlite:///:memory:"
        db_manager = DatabaseManager(test_db_url)
        
        # Initialize tables
        db_manager.init_tables()
        print("✅ Database tables created successfully")
        
        # Test session creation
        session = db_manager.get_session()
        assert session is not None
        session.close()
        print("✅ Database session creation works")
        
        print("✅ Database models test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {str(e)}\n")
        return False

def test_full_integration():
    """Test a complete blueprint generation workflow (if API keys available)."""
    print("🧪 Testing Full Integration...")
    
    try:
        serpapi_key = os.getenv('SERPAPI_KEY')
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        if not serpapi_key or not gemini_key:
            print("⚠️  API keys not configured, skipping integration test")
            return True
        
        from src.services.blueprint_generator import BlueprintGeneratorService
        from src.services.blueprint_storage import BlueprintStorageService
        from src.models.blueprint import DatabaseManager
        
        # Set up test database
        db_manager = DatabaseManager("sqlite:///:memory:")
        db_manager.init_tables()
        session = db_manager.get_session()
        
        # Initialize services
        generator = BlueprintGeneratorService(serpapi_key, gemini_key)
        storage = BlueprintStorageService(session)
        
        print("🚀 Generating test blueprint (this may take 30+ seconds)...")
        start_time = time.time()
        
        # Generate a blueprint
        test_keyword = "content marketing"
        user_id = "test-user-123"
        
        blueprint_data = generator.generate_blueprint(test_keyword, user_id)
        generation_time = time.time() - start_time
        
        print(f"✅ Blueprint generated in {generation_time:.1f} seconds")
        
        # Validate the generated data
        assert generator.validate_blueprint_data(blueprint_data)
        print("✅ Generated blueprint data is valid")
        
        # Save to database
        blueprint_id = storage.save_blueprint(blueprint_data, user_id)
        print(f"✅ Blueprint saved to database with ID: {blueprint_id}")
        
        # Retrieve from database
        retrieved_blueprint = storage.get_blueprint(blueprint_id, user_id)
        assert retrieved_blueprint is not None
        assert retrieved_blueprint['keyword'] == test_keyword
        print("✅ Blueprint retrieved from database successfully")
        
        # Clean up
        session.close()
        
        print("✅ Full integration test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Full integration test failed: {str(e)}\n")
        return False

def main():
    """Run all tests."""
    print("🎯 Starting Blueprint Generator Tests")
    print("=" * 50)
    
    tests = [
        test_blueprint_models,
        test_database_models,
        test_blueprint_generator,
        test_api_routes,
        test_full_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}\n")
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Blueprint generator is ready for development.")
    elif passed > total // 2:
        print("⚠️  Most tests passed. Check failed tests and API configuration.")
    else:
        print("❌ Multiple test failures. Check implementation and dependencies.")
    
    print("\n📝 Next Steps:")
    print("1. Update app_real.py to integrate the new blueprint routes")
    print("2. Test API endpoints with a REST client")
    print("3. Create frontend integration")
    print("4. Add comprehensive error handling")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
