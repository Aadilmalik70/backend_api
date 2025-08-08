#!/usr/bin/env python3
"""
Test each endpoint individually to isolate issues
"""

import requests
import json
import sys

def test_endpoint(url, method='GET', headers=None, data=None, description=""):
    """Test a single endpoint and return detailed info"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"✅ Request successful")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Try to parse response
        try:
            if response.content:
                response_data = response.json()
                print(f"Response Type: JSON")
                print(f"Response Data:")
                print(json.dumps(response_data, indent=2))
                return True, response_data
            else:
                print(f"Response Type: Empty")
                return True, None
        except json.JSONDecodeError:
            print(f"Response Type: Text/HTML")
            print(f"Response Text: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error - Server not reachable")
        return False, None
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error")
        return False, None
    except Exception as e:
        print(f"❌ Request Error: {str(e)}")
        return False, None

def main():
    print("🔍 Individual Endpoint Testing")
    print("Testing SERP Strategist API endpoints individually")
    
    base_url = "http://127.0.0.1:5000"
    results = {}
    
    # Test 1: Root endpoint
    success, data = test_endpoint(
        f"{base_url}/",
        description="Root endpoint - should return API info"
    )
    results['root'] = success
    
    # Test 2: Health endpoint
    success, data = test_endpoint(
        f"{base_url}/api/health",
        description="Health check endpoint"
    )
    results['health'] = success
    
    # Test 3: Blueprint generation (invalid request for testing)
    success, data = test_endpoint(
        f"{base_url}/api/blueprints/generate",
        method='POST',
        headers={'Content-Type': 'application/json'},
        data={},
        description="Blueprint generation (no auth - should fail with 401)"
    )
    results['auth_test'] = success  # Success means we got a response
    
    # Test 4: Blueprint generation (missing keyword)
    success, data = test_endpoint(
        f"{base_url}/api/blueprints/generate",
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-User-ID': 'test-user'
        },
        data={},
        description="Blueprint generation (no keyword - should fail with 400)"
    )
    results['validation_test'] = success
    
    # Test 5: Blueprint generation (valid request)
    success, data = test_endpoint(
        f"{base_url}/api/blueprints/generate",
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'X-User-ID': 'test-user'
        },
        data={'keyword': 'API testing'},
        description="Blueprint generation (valid request)"
    )
    results['generation'] = success
    blueprint_id = None
    if success and data and 'blueprint_id' in data:
        blueprint_id = data['blueprint_id']
    
    # Test 6: Blueprint listing
    success, data = test_endpoint(
        f"{base_url}/api/blueprints",
        headers={'X-User-ID': 'test-user'},
        description="Blueprint listing"
    )
    results['listing'] = success
    
    # Test 7: Blueprint retrieval (if we have an ID)
    if blueprint_id:
        success, data = test_endpoint(
            f"{base_url}/api/blueprints/{blueprint_id}",
            headers={'X-User-ID': 'test-user'},
            description=f"Blueprint retrieval for ID: {blueprint_id}"
        )
        results['retrieval'] = success
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 TEST SUMMARY")
    print(f"{'='*60}")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.ljust(20)}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed")
    
    if blueprint_id:
        print(f"\n📝 Generated Blueprint ID: {blueprint_id}")
        print(f"Test retrieval with:")
        print(f"curl -H 'X-User-ID: test-user' {base_url}/api/blueprints/{blueprint_id}")

if __name__ == "__main__":
    main()