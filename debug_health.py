#!/usr/bin/env python3
"""
Debug script to check what the health endpoint is actually returning
"""

import requests
import json

def debug_health():
    """Debug the health endpoint response"""
    print("🔍 Debugging Health Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:5000/api/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Raw Response: {response.text}")
        
        if response.content:
            try:
                data = response.json()
                print(f"\nParsed JSON:")
                print(json.dumps(data, indent=2))
                
                # Check specific fields
                print(f"\nField Analysis:")
                print(f"  'status' field: {'✅' if 'status' in data else '❌'} {data.get('status', 'MISSING')}")
                print(f"  'version' field: {'✅' if 'version' in data else '❌'} {data.get('version', 'MISSING')}")
                print(f"  'features' field: {'✅' if 'features' in data else '❌'}")
                print(f"  'services' field: {'✅' if 'services' in data else '❌'}")
                print(f"  'api_keys' field: {'✅' if 'api_keys' in data else '❌'}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
        else:
            print("❌ Empty response body")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running or wrong port")
    except Exception as e:
        print(f"❌ Request error: {e}")

def debug_root():
    """Debug the root endpoint too"""
    print("\n🔍 Debugging Root Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:5000/", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Raw Response: {response.text}")
        
        if response.content:
            try:
                data = response.json()
                print(f"\nParsed JSON:")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e:
                print(f"❌ JSON Parse Error: {e}")
                
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    debug_health()
    debug_root()