#!/usr/bin/env python3
"""
Test Google APIs Connection with Real Data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.google_apis.custom_search_client import CustomSearchClient
from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
from src.utils.google_apis.gemini_client import GeminiClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_apis_connection():
    """Test connection to Google APIs with real data"""
    print("🔍 Testing Google APIs Connection with Real Data...")
    print("=" * 60)
    
    results = {
        'custom_search': False,
        'knowledge_graph': False,
        'gemini': False
    }
    
    # Test Custom Search API
    print("\n📊 Testing Custom Search API...")
    try:
        search_client = CustomSearchClient()
        
        if not search_client.api_key:
            print("❌ GOOGLE_API_KEY not configured")
        elif not search_client.search_engine_id:
            print("❌ GOOGLE_CUSTOM_SEARCH_ENGINE_ID not configured")
        else:
            print(f"✅ API Key configured: {search_client.api_key[:10]}...")
            print(f"✅ Search Engine ID configured: {search_client.search_engine_id[:10]}...")
            
            # Test real search
            print("🔍 Testing real search query...")
            result = search_client.search("SEO tools", num_results=3)
            
            if 'items' in result and len(result['items']) > 0:
                print(f"✅ Custom Search API: Working! Found {len(result['items'])} results")
                print(f"📋 Sample result: {result['items'][0].get('title', 'No title')}")
                results['custom_search'] = True
            else:
                print("⚠️ Custom Search API: Connected but no results")
                if 'note' in result:
                    print(f"Note: {result['note']}")
                
    except Exception as e:
        print(f"❌ Custom Search API Error: {str(e)}")
    
    # Test Knowledge Graph API
    print("\n🧠 Testing Knowledge Graph API...")
    try:
        kg_client = KnowledgeGraphClient()
        
        if not kg_client.api_key:
            print("❌ GOOGLE_API_KEY not configured")
        else:
            print(f"✅ API Key configured: {kg_client.api_key[:10]}...")
            
            # Test real entity search
            print("🔍 Testing real entity search...")
            result = kg_client.search_entities("Google", limit=2)
            
            if 'itemListElement' in result and len(result['itemListElement']) > 0:
                print(f"✅ Knowledge Graph API: Working! Found {len(result['itemListElement'])} entities")
                entity = result['itemListElement'][0]
                print(f"📋 Sample entity: {entity.get('result', {}).get('name', 'No name')}")
                results['knowledge_graph'] = True
            else:
                print("⚠️ Knowledge Graph API: Connected but no entities")
                
    except Exception as e:
        print(f"❌ Knowledge Graph API Error: {str(e)}")
    
    # Test Gemini API
    print("\n🤖 Testing Gemini API...")
    try:
        gemini_client = GeminiClient()
        
        # Check if Gemini is properly configured
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GEMINI_API_KEY not configured")
        elif not gemini_client.model:
            print("❌ Gemini model not initialized")
        else:
            print(f"✅ API Key configured: {api_key[:10]}...")
            
            # Test real content generation
            print("🔍 Testing real content generation...")
            result = gemini_client.generate_content("What is SEO?")
            
            if result and result.get('content'):
                print(f"✅ Gemini API: Working!")
                print(f"📋 Sample response: {result['content'][:100]}...")
                results['gemini'] = True
            else:
                print("⚠️ Gemini API: Connected but no content generated")
                
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 GOOGLE APIs CONNECTION SUMMARY")
    print("=" * 60)
    
    working_apis = sum(results.values())
    total_apis = len(results)
    
    for api_name, is_working in results.items():
        status = "✅ WORKING" if is_working else "❌ NOT WORKING"
        print(f"{api_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📈 Overall Status: {working_apis}/{total_apis} APIs working")
    
    if working_apis == total_apis:
        print("🎉 ALL GOOGLE APIs ARE WORKING! Ready for real data testing.")
        return True
    elif working_apis > 0:
        print("⚠️ Some Google APIs are working. Partial functionality available.")
        return True
    else:
        print("❌ No Google APIs are working. Please check your configuration.")
        print("\n📋 Setup Instructions:")
        print("1. Get Google API key from: https://console.cloud.google.com/")
        print("2. Create Custom Search Engine: https://cse.google.com/")
        print("3. Add keys to .env file:")
        print("   GOOGLE_API_KEY=your_key_here")
        print("   GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_engine_id_here")
        return False

def test_environment_setup():
    """Test environment configuration"""
    print("\n🔧 Testing Environment Setup...")
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google API Key',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Custom Search Engine ID',
        'GEMINI_API_KEY': 'Gemini API Key'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {description}: Configured")
        else:
            print(f"❌ {description}: Not configured")
    
    # Check fallback settings
    fallback_enabled = os.getenv('FALLBACK_TO_SERPAPI', 'false').lower() == 'true'
    print(f"\n⚙️ Fallback to SerpAPI: {'Enabled' if fallback_enabled else 'Disabled'}")
    
    if not fallback_enabled:
        print("🎯 Fallback disabled - will use real Google APIs only")
    else:
        print("⚠️ Fallback enabled - may use mock data if APIs fail")

if __name__ == "__main__":
    print("🚀 Google APIs Real Data Connection Test")
    print("=" * 60)
    
    # Test environment setup
    test_environment_setup()
    
    # Test API connections
    success = test_google_apis_connection()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Run: python test_real_keyword_processing.py")
        print("2. Run: python test_phase_2_4_keyword_processor.py")
        print("3. Check for real data in results (no 'mock' or 'fallback' labels)")
    else:
        print("\n📋 Setup Required:")
        print("1. Follow SETUP_REAL_GOOGLE_APIS.md")
        print("2. Configure your .env file with real API keys")
        print("3. Run this test again")
    
    sys.exit(0 if success else 1)
