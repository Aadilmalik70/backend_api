#!/usr/bin/env python3
"""
Test script to verify the SERP Strategist API fixes.
"""

import requests
import json
import time
import sys

def test_quick_endpoint():
    """Test the quick blueprint generation endpoint."""
    print("🧪 Testing quick blueprint generation...")
    
    url = "http://localhost:5000/api/blueprints/generate-quick"
    payload = {
        "keyword": "content marketing",
        "project_id": "test-project"
    }
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user-1"
    }
    
    try:
        print(f"📡 Sending request to {url}")
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Response time: {duration:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Quick endpoint working!")
            print(f"📋 Blueprint ID: {data.get('blueprint_id')}")
            print(f"🎯 Keyword: {data.get('keyword')}")
            print(f"📝 Status: {data.get('status')}")
            print(f"⚡ Generation time: {data.get('generation_time')} seconds")
            
            # Check data structure
            blueprint_data = data.get('data', {})
            print(f"🏗️  Has heading structure: {'heading_structure' in blueprint_data}")
            print(f"🎯 Has topic clusters: {'topic_clusters' in blueprint_data}")
            print(f"🔍 Has competitor analysis: {'competitor_analysis' in blueprint_data}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out!")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - is the server running?")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint."""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working!")
            print(f"📊 Status: {data.get('status')}")
            print(f"🔧 Google APIs: {data.get('google_apis', {}).get('enabled', False)}")
            print(f"🔄 Fallback APIs: {data.get('fallback_apis', {})}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_full_endpoint():
    """Test the full blueprint generation endpoint."""
    print("\n🚀 Testing full blueprint generation...")
    
    url = "http://localhost:5000/api/blueprints/generate"
    payload = {
        "keyword": "digital marketing",
        "project_id": "test-project"
    }
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user-1"
    }
    
    try:
        print(f"📡 Sending request to {url}")
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers, timeout=180)  # 3 minute timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Response time: {duration:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Full endpoint working!")
            print(f"📋 Blueprint ID: {data.get('blueprint_id')}")
            print(f"🎯 Keyword: {data.get('keyword')}")
            print(f"📝 Status: {data.get('status')}")
            print(f"⚡ Generation time: {data.get('generation_time')} seconds")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (this might be expected if the fix isn't complete)")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 SERP Strategist API Test Suite")
    print("=" * 50)
    
    # Test health endpoint first
    health_ok = test_health_endpoint()
    
    if not health_ok:
        print("\n❌ Health check failed - server might not be running")
        print("💡 Start the server with: python src/main.py")
        sys.exit(1)
    
    # Test quick endpoint
    quick_ok = test_quick_endpoint()
    
    # Test full endpoint (might fail due to hanging issue)
    full_ok = test_full_endpoint()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"✅ Health endpoint: {'PASS' if health_ok else 'FAIL'}")
    print(f"⚡ Quick endpoint: {'PASS' if quick_ok else 'FAIL'}")
    print(f"🚀 Full endpoint: {'PASS' if full_ok else 'FAIL'}")
    
    if quick_ok:
        print("\n🎉 Basic functionality is working!")
        print("💡 Use the quick endpoint (/api/blueprints/generate-quick) for now")
        print("🔧 Work on fixing the full endpoint for production")
    else:
        print("\n❌ Basic functionality is not working")
        print("🔧 Check server logs for errors")

if __name__ == "__main__":
    main()
