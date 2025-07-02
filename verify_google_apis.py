"""
Google APIs Verification and Health Check Script

Run this script to verify your Google APIs are properly configured
and returning real data (not mock data).
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

try:
    from src.utils.google_apis.api_manager import google_api_manager
    from src.utils.google_apis.migration_manager import migration_manager
    from src.utils.google_apis.search_console_client import SearchConsoleClient
    from src.utils.google_apis.custom_search_client import CustomSearchClient
    from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
    from src.utils.google_apis.natural_language_client import NaturalLanguageClient
    from src.utils.google_apis.gemini_client import GeminiClient
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure all dependencies are installed:")
    print("pip install google-cloud-language google-api-python-client google-auth google-generativeai requests")
    sys.exit(1)


def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    
    required_vars = {
        'GOOGLE_APPLICATION_CREDENTIALS': 'Service account credentials file path',
        'GOOGLE_API_KEY': 'Google API key for Custom Search and Knowledge Graph',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Custom Search Engine ID',
        'SEARCH_CONSOLE_SITE_URL': 'Your verified domain in Search Console',
    }
    
    optional_vars = {
        'GEMINI_API_KEY': 'Gemini AI API key (optional)',
        'USE_GOOGLE_APIS': 'Enable Google APIs (should be true)',
        'SERPAPI_API_KEY': 'SerpAPI key for fallback'
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_required.append(f"  ❌ {var}: {description}")
        else:
            print(f"  ✅ {var}: {'*' * min(len(value), 20)}...")
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            missing_optional.append(f"  ⚠️ {var}: {description}")
        else:
            print(f"  ✅ {var}: {'*' * min(len(value), 20)}...")
    
    if missing_required:
        print("\n❌ Missing Required Environment Variables:")
        for var in missing_required:
            print(var)
        return False
    
    if missing_optional:
        print("\n⚠️ Missing Optional Environment Variables:")
        for var in missing_optional:
            print(var)
    
    # Check if credentials file exists
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if creds_path and not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        return False
    
    return True


def test_individual_apis():
    """Test each API individually"""
    print("\n🧪 Testing Individual APIs...")
    
    results = {}
    
    # Test Search Console
    print("\n📊 Testing Search Console API...")
    try:
        sc_client = SearchConsoleClient()
        if sc_client.service and sc_client.site_url:
            # Try to get performance data
            perf_data = sc_client.get_performance_data()
            if 'note' in perf_data and 'Mock data' in perf_data['note']:
                results['search_console'] = "❌ Returning mock data - check credentials and site verification"
            else:
                results['search_console'] = f"✅ Real data - {perf_data.get('total_rows', 0)} rows returned"
        else:
            results['search_console'] = "❌ Not configured - check credentials and SEARCH_CONSOLE_SITE_URL"
    except Exception as e:
        results['search_console'] = f"❌ Error: {str(e)[:100]}"
    
    # Test Custom Search
    print("🔍 Testing Custom Search API...")
    try:
        cs_client = CustomSearchClient()
        if cs_client.api_key and cs_client.search_engine_id:
            search_results = cs_client.search("test query", num_results=1)
            if 'note' in search_results and 'Mock data' in search_results['note']:
                results['custom_search'] = "❌ Returning mock data - check API key and Search Engine ID"
            else:
                results['custom_search'] = f"✅ Real data - {len(search_results.get('results', []))} results returned"
        else:
            results['custom_search'] = "❌ Not configured - check GOOGLE_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID"
    except Exception as e:
        results['custom_search'] = f"❌ Error: {str(e)[:100]}"
    
    # Test Knowledge Graph
    print("🧠 Testing Knowledge Graph API...")
    try:
        kg_client = KnowledgeGraphClient()
        if kg_client.api_key:
            entities = kg_client.search_entities("Google", limit=1)
            if 'note' in entities and 'Mock data' in entities['note']:
                results['knowledge_graph'] = "❌ Returning mock data - check API key"
            else:
                results['knowledge_graph'] = f"✅ Real data - {len(entities.get('entities', []))} entities returned"
        else:
            results['knowledge_graph'] = "❌ Not configured - check GOOGLE_API_KEY"
    except Exception as e:
        results['knowledge_graph'] = f"❌ Error: {str(e)[:100]}"
    
    # Test Natural Language
    print("📝 Testing Natural Language API...")
    try:
        nl_client = NaturalLanguageClient()
        if nl_client.client:
            analysis = nl_client.analyze_content("This is a test sentence with Google mentioned.")
            if 'note' in analysis and 'Mock data' in analysis['note']:
                results['natural_language'] = "❌ Returning mock data - check credentials"
            else:
                results['natural_language'] = f"✅ Real data - {len(analysis.get('entities', []))} entities found"
        else:
            results['natural_language'] = "❌ Not configured - check GOOGLE_APPLICATION_CREDENTIALS"
    except Exception as e:
        results['natural_language'] = f"❌ Error: {str(e)[:100]}"
    
    # Test Gemini
    print("🤖 Testing Gemini API...")
    try:
        gemini_client = GeminiClient()
        if gemini_client.model:
            analysis = gemini_client.analyze_ai_readiness("This is test content for AI analysis.")
            if 'note' in analysis and 'Mock data' in analysis['note']:
                results['gemini'] = "❌ Returning mock data - check GEMINI_API_KEY"
            else:
                results['gemini'] = f"✅ Real data - AI readiness score: {analysis.get('overall_ai_readiness', 'N/A')}"
        else:
            results['gemini'] = "❌ Not configured - check GEMINI_API_KEY"
    except Exception as e:
        results['gemini'] = f"❌ Error: {str(e)[:100]}"
    
    return results


def test_migration_manager():
    """Test the migration manager with real queries"""
    print("\n🔄 Testing Migration Manager (Your Main Interface)...")
    
    test_results = {}
    
    # Test SERP data
    print("  Testing SERP data retrieval...")
    try:
        serp_data = migration_manager.get_serp_data("Python SEO tools", use_google_apis=True)
        if serp_data.get('data_source') == 'google_apis':
            test_results['serp_analysis'] = "✅ Using Google APIs successfully"
        elif serp_data.get('data_source') == 'serpapi':
            test_results['serp_analysis'] = "⚠️ Fell back to SerpAPI - check Google APIs configuration"
        else:
            test_results['serp_analysis'] = "❌ Unknown data source"
    except Exception as e:
        test_results['serp_analysis'] = f"❌ Error: {str(e)[:100]}"
    
    # Test content analysis
    print("  Testing content analysis...")
    try:
        content = "This is a comprehensive guide about Search Engine Optimization. Google uses complex algorithms to rank websites."
        analysis = migration_manager.analyze_content(content, enhanced_analysis=True)
        if 'note' not in analysis or 'Mock data' not in str(analysis.get('note', '')):
            test_results['content_analysis'] = "✅ Real content analysis working"
        else:
            test_results['content_analysis'] = "❌ Returning mock data"
    except Exception as e:
        test_results['content_analysis'] = f"❌ Error: {str(e)[:100]}"
    
    # Test entity verification
    print("  Testing entity verification...")
    try:
        entities = migration_manager.extract_and_verify_entities("Google is a technology company founded by Larry Page and Sergey Brin.")
        real_entities = [e for e in entities if e.get('verified', False)]
        if real_entities:
            test_results['entity_verification'] = f"✅ Verified {len(real_entities)} entities"
        else:
            test_results['entity_verification'] = "❌ No entities verified - check Knowledge Graph API"
    except Exception as e:
        test_results['entity_verification'] = f"❌ Error: {str(e)[:100]}"
    
    return test_results


def generate_health_report():
    """Generate comprehensive health report"""
    print("\n📋 Generating Health Report...")
    
    try:
        health_status = google_api_manager.health_check()
        usage_report = google_api_manager.get_usage_report()
        migration_status = migration_manager.get_migration_status()
        
        print(f"  Overall API Health: {health_status.get('overall_status', 'unknown')}")
        print(f"  Total API Calls Made: {usage_report.get('total_calls', 0)}")
        print(f"  Google API Success Rate: {migration_status['performance_metrics']['google_success_rate']:.1f}%")
        print(f"  SerpAPI Fallback Rate: {migration_status['performance_metrics']['fallback_rate']:.1f}%")
        
        return True
    except Exception as e:
        print(f"  ❌ Health report generation failed: {e}")
        return False


def main():
    """Main verification function"""
    print("🚀 Google APIs Integration Verification")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check environment variables
    if not check_environment_variables():
        print("\n❌ Environment setup incomplete. Please check GOOGLE_APIS_SETUP.md")
        return False
    
    # Step 2: Test individual APIs
    api_results = test_individual_apis()
    print("\n📊 Individual API Test Results:")
    for api_name, result in api_results.items():
        print(f"  {api_name}: {result}")
    
    # Step 3: Test migration manager
    migration_results = test_migration_manager()
    print("\n🔄 Migration Manager Test Results:")
    for test_name, result in migration_results.items():
        print(f"  {test_name}: {result}")
    
    # Step 4: Generate health report
    health_ok = generate_health_report()
    
    # Final summary
    print("\n" + "=" * 50)
    
    # Count successful tests
    total_tests = len(api_results) + len(migration_results)
    successful_tests = sum(1 for result in list(api_results.values()) + list(migration_results.values()) 
                          if result.startswith("✅"))
    
    if successful_tests == total_tests and health_ok:
        print("🎉 ALL TESTS PASSED! You're getting real data from Google APIs!")
        print("\n✅ Your migration from SerpAPI to Google APIs is working correctly.")
        print("✅ No more mock/sample data - you're getting real API responses.")
    elif successful_tests > 0:
        print(f"⚠️ PARTIAL SUCCESS: {successful_tests}/{total_tests} tests passed")
        print("\n🔧 Some APIs are working, others need configuration.")
        print("📖 Check GOOGLE_APIS_SETUP.md for detailed setup instructions.")
    else:
        print("❌ SETUP REQUIRED: No APIs are working correctly")
        print("\n📖 Please follow the setup guide in GOOGLE_APIS_SETUP.md")
        print("🔧 You're currently getting mock data because APIs aren't configured.")
    
    return successful_tests == total_tests and health_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
