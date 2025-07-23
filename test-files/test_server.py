#!/usr/bin/env python3
"""
Quick test to verify the server starts and routes are working
"""

import requests
import time
import json

def test_server_startup():
    """Test if the server is running and responsive"""
    print("🧪 Testing server startup...")
    
    base_url = "http://localhost:5000"
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            data = response.json()
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running or not accessible")
        print("   Start the server with: python src/main.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {str(e)}")
        return False
    
    return True

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🧪 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            data = response.json()
            api_status = data.get('api_status', {})
            print(f"   SerpAPI: {'✅' if api_status.get('serpapi_configured') else '❌ Not configured'}")
            print(f"   Gemini API: {'✅' if api_status.get('gemini_configured') else '❌ Not configured'}")
            print(f"   Database: {'✅' if api_status.get('database_connected') else '❌ Not connected'}")
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {str(e)}")
        return False
    
    return True

def test_blueprint_endpoint():
    """Test the blueprint generation endpoint (without generating)"""
    print("\n🧪 Testing blueprint endpoint availability...")
    
    try:
        # Test with missing data (should return 400, not 404)
        response = requests.post(
            "http://localhost:5000/api/blueprints/generate",
            headers={
                "Content-Type": "application/json",
                "X-User-ID": "test-user"
            },
            json={},  # Empty payload should trigger validation error
            timeout=5
        )
        
        if response.status_code == 400:
            print("✅ Blueprint endpoint is accessible")
            error_data = response.json()
            print(f"   Validation working: {error_data.get('error', 'Unknown error')}")
        elif response.status_code == 404:
            print("❌ Blueprint endpoint not found (404)")
            return False
        else:
            print(f"⚠️  Blueprint endpoint returned unexpected status {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing blueprint endpoint: {str(e)}")
        return False
    
    return True

def test_api_info():
    """Test the API info endpoint"""
    print("\n🧪 Testing API info endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/api/info", timeout=5)
        if response.status_code == 200:
            print("✅ API info endpoint is working")
            data = response.json()
            print(f"   API Version: {data.get('api_version', 'Unknown')}")
            
            blueprint_status = data.get('blueprint_generator', {}).get('status', 'Unknown')
            print(f"   Blueprint Generator: {blueprint_status}")
        else:
            print(f"❌ API info endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API info endpoint: {str(e)}")
        return False
    
    return True

def main():
    """Run all server tests"""
    print("🎯 SERP Strategist Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_server_startup,
        test_health_endpoint,
        test_api_info,
        test_blueprint_endpoint
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"🎯 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Server is ready for blueprint generation.")
        print("\n📝 Try generating a blueprint:")
        print("curl -X POST http://localhost:5000/api/blueprints/generate \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -H 'X-User-ID: test-user' \\")
        print("  -d '{\"keyword\": \"content marketing\"}'")
    else:
        print("❌ Some tests failed. Check server configuration.")
        print("💡 Make sure the server is running: python src/main.py")

if __name__ == "__main__":
    main()
