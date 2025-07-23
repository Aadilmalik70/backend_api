#!/usr/bin/env python3
"""
Google APIs Environment Validation Script

This script validates that all required Google APIs environment variables
are properly configured and that the APIs are accessible.
"""

import os
import sys
from dotenv import load_dotenv

def validate_google_apis_environment():
    """Validate Google APIs environment configuration"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Google APIs Environment Validation")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        'GOOGLE_API_KEY': 'Google API Key (for Custom Search, Knowledge Graph, etc.)',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Custom Search Engine ID',
        'GOOGLE_APPLICATION_CREDENTIALS': 'Service Account Credentials Path',
        'SEARCH_CONSOLE_SITE_URL': 'Search Console Site URL',
        'GEMINI_API_KEY': 'Gemini API Key'
    }
    
    # Optional environment variables
    optional_vars = {
        'GOOGLE_ADS_DEVELOPER_TOKEN': 'Google Ads Developer Token',
        'GOOGLE_ADS_CLIENT_ID': 'Google Ads Client ID',
        'GOOGLE_ADS_CLIENT_SECRET': 'Google Ads Client Secret',
        'GOOGLE_ADS_REFRESH_TOKEN': 'Google Ads Refresh Token',
        'GOOGLE_ADS_LOGIN_CUSTOMER_ID': 'Google Ads Customer ID'
    }
    
    # Migration settings
    migration_vars = {
        'USE_GOOGLE_APIS': 'Enable Google APIs',
        'FALLBACK_TO_SERPAPI': 'Enable SerpAPI Fallback',
        'MIGRATE_SERP_ANALYSIS': 'Migrate SERP Analysis',
        'MIGRATE_COMPETITOR_ANALYSIS': 'Migrate Competitor Analysis',
        'MIGRATE_CONTENT_ANALYSIS': 'Migrate Content Analysis',
        'MIGRATE_ENTITY_ANALYSIS': 'Migrate Entity Analysis'
    }
    
    all_good = True
    
    # Check required variables
    print("\n🔧 Required Environment Variables:")
    print("-" * 40)
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != "your_api_key_here" and value != "your_custom_search_engine_id":
            if var == 'GOOGLE_APPLICATION_CREDENTIALS':
                # Check if file exists
                if os.path.exists(value):
                    print(f"✅ {var}: File exists")
                else:
                    print(f"❌ {var}: File not found at {value}")
                    all_good = False
            else:
                print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set or placeholder value")
            all_good = False
    
    # Check optional variables
    print("\n🔧 Optional Environment Variables:")
    print("-" * 40)
    google_ads_complete = True
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value != "your_developer_token" and value != "your_client_id":
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set (Google Ads features disabled)")
            google_ads_complete = False
    
    # Check migration settings
    print("\n🔧 Migration Settings:")
    print("-" * 40)
    for var, description in migration_vars.items():
        value = os.getenv(var, 'false').lower()
        status = "✅ Enabled" if value == 'true' else "⚠️  Disabled"
        print(f"{status} {var}: {value}")
    
    # Test API connectivity
    print("\n🧪 Testing API Connectivity:")
    print("-" * 40)
    
    try:
        # Test Google APIs
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from utils.google_apis.custom_search_client import CustomSearchClient
        from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
        from utils.google_apis.natural_language_client import NaturalLanguageClient
        from utils.google_apis.gemini_client import GeminiClient
        
        # Test Custom Search
        try:
            custom_search = CustomSearchClient()
            if custom_search.api_key and custom_search.search_engine_id:
                print("✅ Custom Search API: Configuration looks good")
            else:
                print("❌ Custom Search API: Missing configuration")
                all_good = False
        except Exception as e:
            print(f"❌ Custom Search API: {str(e)}")
            all_good = False
        
        # Test Knowledge Graph
        try:
            knowledge_graph = KnowledgeGraphClient()
            if knowledge_graph.api_key:
                print("✅ Knowledge Graph API: Configuration looks good")
            else:
                print("❌ Knowledge Graph API: Missing configuration")
                all_good = False
        except Exception as e:
            print(f"❌ Knowledge Graph API: {str(e)}")
            all_good = False
        
        # Test Natural Language
        try:
            natural_language = NaturalLanguageClient()
            print("✅ Natural Language API: Configuration looks good")
        except Exception as e:
            print(f"❌ Natural Language API: {str(e)}")
            all_good = False
        
        # Test Gemini
        try:
            gemini = GeminiClient()
            if gemini.model:
                print("✅ Gemini API: Configuration looks good")
            else:
                print("❌ Gemini API: Missing configuration")
                all_good = False
        except Exception as e:
            print(f"❌ Gemini API: {str(e)}")
            all_good = False
            
    except ImportError as e:
        print(f"❌ Cannot import Google APIs modules: {str(e)}")
        all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 SUCCESS: All required environment variables are configured!")
        print("✅ Google APIs integration is ready to use")
        print("\n🚀 Next steps:")
        print("   1. Run: python verify_google_apis.py")
        print("   2. Test your application with Google APIs")
        print("   3. Monitor API usage and costs")
        return True
    else:
        print("❌ ISSUES FOUND: Some environment variables need attention")
        print("\n🔧 Action items:")
        print("   1. Fix the issues marked with ❌ above")
        print("   2. Check your .env file configuration")
        print("   3. Verify your Google Cloud project setup")
        print("   4. Re-run this validation script")
        return False

if __name__ == "__main__":
    success = validate_google_apis_environment()
    sys.exit(0 if success else 1)
