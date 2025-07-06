#!/usr/bin/env python3
"""
Simple Google APIs Test - Direct API calls
"""

import os
import requests
import sys

def test_direct_custom_search():
    """Test Google Custom Search API directly"""
    print("🔍 Testing Google Custom Search API directly...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id:
        print("❌ Missing API key or Search Engine ID")
        return False
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'test query',
        'num': 1
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"With params: cx={search_engine_id[:10]}..., q='test query'")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return False
            elif 'items' in data:
                print(f"✅ Success! Found {len(data['items'])} items")
                return True
            else:
                print("⚠️ No 'items' in response")
                print(f"Full response: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_direct_knowledge_graph():
    """Test Knowledge Graph API directly"""
    print("\n🧠 Testing Knowledge Graph API directly...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ Missing API key")
        return False
    
    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        'key': api_key,
        'query': 'Google',
        'limit': 1
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"With params: query='Google', limit=1")
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'error' in data:
                print(f"❌ API Error: {data['error']}")
                return False
            elif 'itemListElement' in data:
                print(f"✅ Success! Found {len(data['itemListElement'])} entities")
                return True
            else:
                print("⚠️ No 'itemListElement' in response")
                print(f"Full response: {data}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def check_api_quotas():
    """Check API quotas and limits"""
    print("\n📊 Checking API configuration...")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    print(f"GOOGLE_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"GOOGLE_CUSTOM_SEARCH_ENGINE_ID: {'✅ Set' if search_engine_id else '❌ Missing'}")
    
    if api_key:
        print(f"API Key (first 10 chars): {api_key[:10]}...")
    if search_engine_id:
        print(f"Search Engine ID (first 10 chars): {search_engine_id[:10]}...")

def main():
    print("🚀 Direct Google APIs Test")
    print("=" * 50)
    
    check_api_quotas()
    
    # Test Custom Search
    cs_success = test_direct_custom_search()
    
    # Test Knowledge Graph
    kg_success = test_direct_knowledge_graph()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    print(f"Custom Search API: {'✅ Working' if cs_success else '❌ Failed'}")
    print(f"Knowledge Graph API: {'✅ Working' if kg_success else '❌ Failed'}")
    
    if cs_success and kg_success:
        print("\n🎉 Both APIs are working! The issue may be in the client code.")
    elif cs_success or kg_success:
        print("\n⚠️ Some APIs are working. Check individual configurations.")
    else:
        print("\n❌ APIs are not working. Check your configuration:")
        print("1. Verify API key is correct")
        print("2. Check Custom Search Engine ID")
        print("3. Ensure APIs are enabled in Google Cloud Console")
        print("4. Check quota limits")
    
    return cs_success or kg_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
