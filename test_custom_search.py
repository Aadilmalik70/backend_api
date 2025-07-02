"""
Simple test script to check if Custom Search is working with real data
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_custom_search():
    """Test Custom Search API with real data"""
    print("🔍 Testing Custom Search API...")
    print("-" * 40)
    
    try:
        from utils.google_apis.custom_search_client import CustomSearchClient
        
        # Initialize client
        client = CustomSearchClient()
        
        # Check configuration
        if not client.api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        if not client.search_engine_id:
            print("❌ GOOGLE_CUSTOM_SEARCH_ENGINE_ID not found in environment")
            return False
        
        print(f"✅ API Key: {client.api_key[:20]}...")
        print(f"✅ Search Engine ID: {client.search_engine_id}")
        
        # Test search
        print("\n🧪 Testing search for 'python seo tools'...")
        results = client.search('python seo tools', num_results=3)
        
        # Check if we got real data or mock data
        if 'note' in results and 'Mock data' in results['note']:
            print("❌ Still getting mock data")
            print("Possible issues:")
            print("   - API key might be invalid")
            print("   - Search Engine ID might be wrong")
            print("   - Custom Search API might not be enabled")
            return False
        else:
            print(f"✅ SUCCESS! Got real data!")
            print(f"📊 Total results available: {results.get('search_information', {}).get('total_results', 'N/A')}")
            print(f"🔍 Results returned: {len(results.get('results', []))}")
            
            # Show first few results
            for i, result in enumerate(results.get('results', [])[:3], 1):
                print(f"\n{i}. {result.get('title', 'N/A')}")
                print(f"   URL: {result.get('link', 'N/A')}")
                print(f"   Snippet: {result.get('snippet', 'N/A')[:100]}...")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_environment_variables():
    """Test if environment variables are properly loaded"""
    print("\n🔍 Checking Environment Variables...")
    print("-" * 40)
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google API Key',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Custom Search Engine ID',
        'SERPAPI_API_KEY': 'SerpAPI Key (fallback)',
        'GEMINI_API_KEY': 'Gemini API Key'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "YOUR_SEARCH_ENGINE_ID_HERE":
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set or placeholder")
            all_good = False
    
    return all_good

def main():
    """Main test function"""
    print("🧪 Google APIs Test Suite")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables not properly set")
        print("📋 Next steps:")
        print("   1. Run: python update_search_id.py")
        print("   2. Check your .env file")
        return
    
    # Test Custom Search
    search_ok = test_custom_search()
    
    print("\n" + "=" * 50)
    if search_ok:
        print("🎉 SUCCESS! Custom Search is working with REAL data!")
        print("\n📋 What's working:")
        print("   ✅ Custom Search API - Real Google search results")
        print("   ✅ Environment variables properly configured")
        print("\n🚀 Next steps:")
        print("   1. Run full verification: python verify_google_apis.py")
        print("   2. Try the production integration: python examples/production_integration.py")
        print("   3. Replace your SerpAPI calls with Google APIs")
    else:
        print("❌ Custom Search needs more configuration")
        print("\n📋 Troubleshooting:")
        print("   1. Make sure Custom Search API is enabled in Google Cloud Console")
        print("   2. Check your API key has proper permissions")
        print("   3. Verify your Search Engine ID is correct")
        print("   4. Run: python update_search_id.py")

if __name__ == "__main__":
    main()
