"""
Quick test to verify Custom Search API is working after enabling it
"""

import os
import requests
from dotenv import load_dotenv

def test_custom_search_api():
    """Test if Custom Search API is working"""
    print("🔍 Testing Custom Search API...")
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id:
        print("❌ Missing API key or Search Engine ID")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"🔍 Search Engine ID: {search_engine_id}")
    
    # Test API call
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'python seo tools',
        'num': 3
    }
    
    try:
        print("\n🧪 Making API request...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            print("✅ SUCCESS! Custom Search API is working!")
            
            data = response.json()
            search_info = data.get('searchInformation', {})
            items = data.get('items', [])
            
            print(f"📊 Total results: {search_info.get('totalResults', 'N/A')}")
            print(f"⏱️ Search time: {search_info.get('searchTime', 'N/A')}s")
            print(f"🎯 Results returned: {len(items)}")
            
            print("\n🔍 Sample results:")
            for i, item in enumerate(items[:3], 1):
                print(f"{i}. {item.get('title', 'N/A')}")
                print(f"   {item.get('link', 'N/A')}")
                print(f"   {item.get('snippet', 'N/A')[:80]}...")
                print()
            
            return True
            
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Custom Search API not enabled")
            print("\n📋 To fix:")
            print("1. Go to: https://console.cloud.google.com")
            print("2. APIs & Services → Library")
            print("3. Search for 'Custom Search API'")
            print("4. Click ENABLE")
            print("5. Make sure billing is enabled")
            return False
            
        elif response.status_code == 400:
            print("❌ 400 Bad Request - Check your Search Engine ID")
            print(f"Current ID: {search_engine_id}")
            print("Make sure it matches your Custom Search Engine")
            return False
            
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Custom Search API Test")
    print("=" * 40)
    
    if test_custom_search_api():
        print("\n🎉 GREAT! Your Custom Search API is working!")
        print("\n📋 What this means:")
        print("   ✅ No more mock data")
        print("   ✅ Real Google search results")
        print("   ✅ Up to 100 results per query")
        print("   ✅ SERP features analysis")
        print("   ✅ Competitor analysis")
        print("\n🚀 Next steps:")
        print("   1. Run: python verify_google_apis.py")
        print("   2. Test: python examples/production_integration.py")
        print("   3. Replace SerpAPI calls in your application")
    else:
        print("\n📋 Next steps:")
        print("   1. Enable Custom Search API in Google Cloud Console")
        print("   2. Enable billing if not already done")
        print("   3. Run this test again")

if __name__ == "__main__":
    main()
