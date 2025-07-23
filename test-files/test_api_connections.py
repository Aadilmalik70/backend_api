#!/usr/bin/env python3
"""
Quick API Test Script

This script tests your API configurations to make sure everything works
before running the full application.
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_serpapi():
    """Test SerpAPI connection."""
    print("🔍 Testing SerpAPI...")
    
    api_key = os.getenv('SERPAPI_KEY') or os.getenv('SERPAPI_API_KEY')
    if not api_key:
        print("❌ SerpAPI key not found in environment variables")
        return False
    
    try:
        # Make a simple test request
        params = {
            "engine": "google",
            "q": "test query",
            "api_key": api_key,
            "num": 1,
            "hl": "en",
            "gl": "us"
        }
        
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        
        if response.status_code == 200:
            print("✅ SerpAPI connection successful")
            data = response.json()
            results_count = len(data.get("organic_results", []))
            print(f"   Retrieved {results_count} search results")
            return True
        elif response.status_code == 429:
            print("⚠️  SerpAPI rate limit hit - this is normal during testing")
            print("   Your API key is valid, but you've made too many requests")
            return True  # API key is valid
        else:
            print(f"❌ SerpAPI error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ SerpAPI connection failed: {str(e)}")
        return False

def test_gemini():
    """Test Gemini API connection."""
    print("\n🤖 Testing Gemini API...")
    
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Gemini API key not found in environment variables")
        return False
    
    try:
        # Test Gemini API with a simple request
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": "Hello, this is a test message. Please respond with 'API test successful'."
                }]
            }]
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Gemini API connection successful")
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"   Response: {text[:100]}...")
            return True
        else:
            print(f"❌ Gemini API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Gemini API connection failed: {str(e)}")
        return False

def test_backend_server():
    """Test if the backend server is running."""
    print("\n🖥️  Testing Backend Server...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend server is running")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            
            api_status = data.get('api_status', {})
            print(f"   SerpAPI configured: {api_status.get('serpapi_configured', False)}")
            print(f"   Gemini configured: {api_status.get('gemini_configured', False)}")
            return True
        else:
            print(f"❌ Backend server error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print("❌ Backend server not running")
        print(f"   Error: {str(e)}")
        print("   💡 Make sure to start the server with: python src/app_real.py")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing API Configurations")
    print("=" * 50)
    
    results = []
    
    # Test individual APIs
    results.append(("SerpAPI", test_serpapi()))
    results.append(("Gemini API", test_gemini()))
    results.append(("Backend Server", test_backend_server()))
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<15} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 You can now start using the application:")
        print("   1. Make sure backend is running: python src/app_real.py")
        print("   2. Open frontend and try analyzing a keyword")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\n🛠️  Common fixes:")
        print("   • Check your .env file has the correct API keys")
        print("   • Make sure the backend server is running")
        print("   • Check your internet connection")
        print("   • Verify API keys are not expired or rate limited")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
