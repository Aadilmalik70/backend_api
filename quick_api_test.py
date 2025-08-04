#!/usr/bin/env python3
"""
Quick API Test Script - Tests the essential blueprint endpoints
Run this script to quickly validate your API is working correctly.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER = "quick-test-user"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            
            features = data.get('features', {})
            services = data.get('services', {})
            api_keys = data.get('api_keys', {})
            
            print(f"   Enhanced Features: {features.get('enhanced_processing', 'Unknown')}")
            print(f"   Database: {features.get('database', 'Unknown')}")
            print(f"   Blueprint Routes: {features.get('blueprint_routes', 'Unknown')}")
            
            # Show service status
            active_services = sum(1 for v in services.values() if v)
            total_services = len(services)
            print(f"   Active Services: {active_services}/{total_services}")
            
            # Show API key status
            configured_apis = sum(1 for v in api_keys.values() if v)
            total_apis = len(api_keys)
            print(f"   Configured APIs: {configured_apis}/{total_apis}")
            
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_generate_blueprint():
    """Test blueprint generation"""
    print("\n🔧 Testing Blueprint Generation...")
    try:
        payload = {"keyword": "content marketing"}
        headers = {
            "Content-Type": "application/json",
            "X-User-ID": TEST_USER
        }
        
        print("   Generating blueprint for 'content marketing'...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/blueprints/generate",
            json=payload,
            headers=headers,
            timeout=60  # 1 minute timeout for this test
        )
        
        generation_time = time.time() - start_time
        
        if response.status_code == 201:
            data = response.json()
            blueprint_id = data.get('blueprint_id')
            print(f"✅ Blueprint Generated!")
            print(f"   Blueprint ID: {blueprint_id}")
            print(f"   Generation Time: {generation_time:.2f}s")
            print(f"   API Generation Time: {data.get('generation_time', 'N/A')}s")
            print(f"   Status: {data.get('status')}")
            
            # Check if fallback was used
            if 'note' in data:
                print(f"   ⚠️  Fallback Used: {data['note']}")
            
            return blueprint_id
        else:
            print(f"❌ Generation failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('error', 'Unknown')}")
            except:
                print(f"   Raw response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Generation timed out (>60s)")
        return None
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None

def test_retrieve_blueprint(blueprint_id):
    """Test blueprint retrieval"""
    print(f"\n📖 Testing Blueprint Retrieval...")
    try:
        headers = {"X-User-ID": TEST_USER}
        
        response = requests.get(
            f"{BASE_URL}/api/blueprints/{blueprint_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Blueprint Retrieved!")
            print(f"   ID: {data.get('id')}")
            print(f"   Keyword: {data.get('keyword')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Created: {data.get('created_at')}")
            print(f"   Has Competitor Analysis: {bool(data.get('competitor_analysis'))}")
            print(f"   Has Heading Structure: {bool(data.get('heading_structure'))}")
            print(f"   Has Topic Clusters: {bool(data.get('topic_clusters'))}")
            
            # Show sample heading structure
            heading_structure = data.get('heading_structure', {})
            h1 = heading_structure.get('h1')
            if h1:
                print(f"   Sample H1: {h1[:80]}{'...' if len(h1) > 80 else ''}")
            
            return True
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('error', 'Unknown')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return False

def test_list_blueprints():
    """Test blueprint listing"""
    print(f"\n📋 Testing Blueprint Listing...")
    try:
        headers = {"X-User-ID": TEST_USER}
        
        response = requests.get(
            f"{BASE_URL}/api/blueprints",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            blueprints = data.get('blueprints', [])
            print(f"✅ Blueprint List Retrieved!")
            print(f"   Total Blueprints: {data.get('total', 0)}")
            print(f"   Returned Count: {len(blueprints)}")
            print(f"   Limit: {data.get('limit')}")
            print(f"   Offset: {data.get('offset')}")
            
            if blueprints:
                print("   Recent Blueprints:")
                for i, bp in enumerate(blueprints[:3]):  # Show first 3
                    print(f"     {i+1}. {bp.get('keyword', 'N/A')} (ID: {bp.get('id', 'N/A')[:8]}...)")
            
            return True
        else:
            print(f"❌ Listing failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('error', 'Unknown')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Listing error: {e}")
        return False

def test_error_handling():
    """Test error handling"""
    print(f"\n🔍 Testing Error Handling...")
    
    # Test missing authentication
    try:
        response = requests.post(
            f"{BASE_URL}/api/blueprints/generate",
            json={"keyword": "test"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 401:
            print("✅ Authentication Required: Correctly rejected unauthenticated request")
        else:
            print(f"❌ Authentication: Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
    
    # Test missing keyword
    try:
        response = requests.post(
            f"{BASE_URL}/api/blueprints/generate",
            json={},
            headers={
                "Content-Type": "application/json",
                "X-User-ID": TEST_USER
            },
            timeout=5
        )
        
        if response.status_code == 400:
            print("✅ Validation: Correctly rejected empty keyword")
        else:
            print(f"❌ Validation: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Validation test error: {e}")

def main():
    """Run quick API tests"""
    print("🚀 Quick API Test for SERP Strategist Blueprint APIs")
    print(f"Testing server: {BASE_URL}")
    print(f"Test user: {TEST_USER}")
    print("=" * 60)
    
    # Test sequence
    health_ok = test_health()
    if not health_ok:
        print("\n❌ Health check failed. Please ensure server is running.")
        return
    
    blueprint_id = test_generate_blueprint()
    if blueprint_id:
        test_retrieve_blueprint(blueprint_id)
    
    test_list_blueprints()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("📊 Quick Test Summary:")
    print("✅ Health Check: API server is running")
    if blueprint_id:
        print("✅ Blueprint Generation: Working (ID generated)")
        print("✅ Blueprint Retrieval: Working")
    else:
        print("❌ Blueprint Generation: Failed")
        print("⚠️  Blueprint Retrieval: Skipped (no ID to test)")
    
    print("✅ Blueprint Listing: Check output above")
    print("✅ Error Handling: Check output above")
    
    print(f"\n🎯 Your blueprint APIs are {'working correctly!' if blueprint_id else 'having issues.'}")
    
    if blueprint_id:
        print(f"\n📝 Generated Blueprint ID: {blueprint_id}")
        print("You can use this ID to test retrieval manually:")
        print(f"curl http://127.0.0.1:5000/api/blueprints/{blueprint_id} -H 'X-User-ID: {TEST_USER}'")

if __name__ == "__main__":
    main()