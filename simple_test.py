#!/usr/bin/env python3
"""
Simple test to check API responses and bypass the quick test validation
"""

import requests
import json

def test_health_raw():
    """Test health endpoint with raw output"""
    print("Testing /api/health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Structure:")
            for key, value in data.items():
                print(f"  {key}: {type(value).__name__} = {value}")
                
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_blueprint_generation_simple():
    """Test blueprint generation with minimal validation"""
    print("\nTesting /api/blueprints/generate endpoint...")
    try:
        payload = {"keyword": "test keyword"}
        headers = {
            "Content-Type": "application/json", 
            "X-User-ID": "test-user"
        }
        
        response = requests.post(
            "http://127.0.0.1:5000/api/blueprints/generate",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}{'...' if len(response.text) > 500 else ''}")
        
        if response.status_code == 201:
            data = response.json()
            blueprint_id = data.get('blueprint_id')
            print(f"\n✅ Success! Blueprint ID: {blueprint_id}")
            return blueprint_id
        else:
            print(f"\n❌ Failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_blueprint_listing_simple():
    """Test blueprint listing"""
    print("\nTesting /api/blueprints endpoint...")
    try:
        headers = {"X-User-ID": "test-user"}
        response = requests.get(
            "http://127.0.0.1:5000/api/blueprints",
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}{'...' if len(response.text) > 300 else ''}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Simple API Test")
    print("=" * 40)
    
    # Test each endpoint individually
    health_ok = test_health_raw()
    blueprint_id = test_blueprint_generation_simple()
    listing_ok = test_blueprint_listing_simple()
    
    print("\n" + "=" * 40)
    print("Summary:")
    print(f"Health: {'✅' if health_ok else '❌'}")
    print(f"Generation: {'✅' if blueprint_id else '❌'}")
    print(f"Listing: {'✅' if listing_ok else '❌'}")
    
    if blueprint_id:
        print(f"\nGenerated Blueprint ID: {blueprint_id}")
        print("You can retrieve it with:")
        print(f"curl -H 'X-User-ID: test-user' http://127.0.0.1:5000/api/blueprints/{blueprint_id}")