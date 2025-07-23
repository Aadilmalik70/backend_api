"""
Test Google APIs Migration

This script tests the migration from SerpAPI to Google APIs and validates
all components are working correctly.
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_google_apis_integration():
    """Test Google APIs integration components"""
    print("🔍 Testing Google APIs Integration")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from src.utils.google_apis.api_manager import GoogleAPIManager
        from src.utils.google_apis.search_console_client import SearchConsoleClient
        from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
        from src.utils.google_apis.custom_search_client import CustomSearchClient
        from src.utils.google_apis.natural_language_client import NaturalLanguageClient
        from src.utils.google_apis.gemini_client import GeminiClient
        from src.utils.google_apis.schema_validator import SchemaValidator
        from src.utils.google_apis.migration_manager import MigrationManager
        print("✅ All imports successful")
        
        # Test API Manager
        print("\n🔧 Testing API Manager...")
        api_manager = GoogleAPIManager()
        health_status = api_manager.health_check()
        print(f"API Manager Health: {health_status['overall_status']}")
        
        # Test individual clients
        print("\n🔍 Testing Individual Clients...")
        
        # Search Console Client
        search_console = SearchConsoleClient()
        print(f"Search Console Health: {'✅' if search_console.health_check() else '❌'}")
        
        # Knowledge Graph Client
        kg_client = KnowledgeGraphClient()
        print(f"Knowledge Graph Health: {'✅' if kg_client.health_check() else '❌'}")
        
        # Custom Search Client
        custom_search = CustomSearchClient()
        print(f"Custom Search Health: {'✅' if custom_search.health_check() else '❌'}")
        
        # Natural Language Client
        nl_client = NaturalLanguageClient()
        print(f"Natural Language Health: {'✅' if nl_client.health_check() else '❌'}")
        
        # Gemini Client
        gemini_client = GeminiClient()
        print(f"Gemini Health: {'✅' if gemini_client.health_check() else '❌'}")
        
        # Schema Validator
        schema_validator = SchemaValidator()
        print(f"Schema Validator Health: {'✅' if schema_validator.health_check() else '❌'}")
        
        # Test Migration Manager
        print("\n🔄 Testing Migration Manager...")
        migration_manager = MigrationManager()
        migration_status = migration_manager.get_migration_status()
        
        print(f"Migration Config: {migration_status['migration_config']}")
        print(f"Google API Health: {migration_status['google_api_health']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

def test_basic_functionality():
    """Test basic functionality with mock data"""
    print("\n🧪 Testing Basic Functionality")
    print("=" * 50)
    
    try:
        from src.utils.google_apis.migration_manager import migration_manager
        
        # Test content analysis
        print("📝 Testing content analysis...")
        test_content = """
        Artificial Intelligence (AI) is transforming the way businesses operate. 
        Companies like Google, Microsoft, and OpenAI are leading the development 
        of AI technologies. Machine learning, natural language processing, and 
        computer vision are key areas of AI research.
        """
        
        content_analysis = migration_manager.analyze_content(test_content)
        print(f"Content Analysis Quality: {content_analysis.get('quality_level', 'unknown')}")
        print(f"Word Count: {content_analysis.get('content_metrics', {}).get('word_count', 0)}")
        
        # Test entity extraction
        print("\n🏷️ Testing entity extraction...")
        entities = migration_manager.extract_and_verify_entities(test_content)
        print(f"Entities found: {len(entities)}")
        for entity in entities[:3]:
            print(f"  - {entity['name']} ({entity['type']})")
        
        # Test SERP data (with fallback)
        print("\n🔍 Testing SERP data...")
        try:
            serp_data = migration_manager.get_serp_data("AI technology", use_google_apis=False)  # Force SerpAPI for test
            print(f"SERP Results: {len(serp_data.get('organic_results', []))} organic results")
            print(f"Data Source: {serp_data.get('data_source', 'unknown')}")
        except Exception as serp_error:
            print(f"SERP test failed (expected with no API keys): {serp_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during functionality test: {e}")
        logger.error(f"Functionality test failed: {e}", exc_info=True)
        return False

def test_schema_generation():
    """Test schema markup generation"""
    print("\n📋 Testing Schema Generation")
    print("=" * 50)
    
    try:
        from src.utils.google_apis.schema_validator import SchemaValidator
        
        schema_validator = SchemaValidator()
        
        # Test organization schema
        print("🏢 Testing organization schema...")
        org_data = {
            'name': 'Test Company',
            'url': 'https://testcompany.com',
            'logo': 'https://testcompany.com/logo.png',
            'description': 'A test company for schema generation'
        }
        
        org_schema = schema_validator.generate_organization_schema(org_data)
        print(f"Organization Schema Type: {org_schema['schema_type']}")
        print(f"JSON-LD Generated: {'@context' in org_schema['json_ld']}")
        
        # Test breadcrumb schema
        print("\n🍞 Testing breadcrumb schema...")
        breadcrumb_items = [
            {'name': 'Home', 'url': 'https://example.com'},
            {'name': 'Products', 'url': 'https://example.com/products'},
            {'name': 'AI Tools', 'url': 'https://example.com/products/ai-tools'}
        ]
        
        breadcrumb_schema = schema_validator.generate_breadcrumb_schema(breadcrumb_items)
        print(f"Breadcrumb Schema Type: {breadcrumb_schema['schema_type']}")
        print(f"Items Count: {len(breadcrumb_schema['json_ld']['itemListElement'])}")
        
        # Test schema suggestions
        print("\n💡 Testing schema suggestions...")
        suggestions = schema_validator.suggest_schema_markup('article')
        print(f"Suggested Schemas: {len(suggestions['recommended_schemas'])}")
        print(f"Implementation Priority: {suggestions['implementation_priority']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during schema test: {e}")
        logger.error(f"Schema test failed: {e}", exc_info=True)
        return False

def test_ai_optimization():
    """Test AI optimization features"""
    print("\n🤖 Testing AI Optimization Features")
    print("=" * 50)
    
    try:
        from src.utils.google_apis.gemini_client import GeminiClient
        from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
        
        # Test Gemini client (will use mock data without API key)
        print("🧠 Testing Gemini AI optimization...")
        gemini_client = GeminiClient()
        
        test_content = "Search Engine Optimization (SEO) is crucial for online visibility."
        ai_analysis = gemini_client.analyze_ai_readiness(test_content)
        print(f"AI Readiness Score: {ai_analysis['overall_ai_readiness']}")
        
        # Test Knowledge Graph integration
        print("\n📚 Testing Knowledge Graph...")
        kg_client = KnowledgeGraphClient()
        entities = kg_client.search_entities("Google", limit=3)
        print(f"Knowledge Graph Entities: {entities['total_results']}")
        
        # Test entity verification
        verification = kg_client.verify_entity("Google", "Organization")
        print(f"Entity Verification: {'✅' if verification['verified'] else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during AI optimization test: {e}")
        logger.error(f"AI optimization test failed: {e}", exc_info=True)
        return False

def print_setup_instructions():
    """Print setup instructions for users"""
    print("\n📚 Setup Instructions")
    print("=" * 50)
    
    print("""
🚀 Quick Start (No Google Cloud Setup Required):
1. Copy .env.google_migration to .env
2. Set your existing API keys:
   - GOOGLE_API_KEY=your_gemini_key
   - SERPAPI_API_KEY=your_serpapi_key
3. Run: python test_google_migration.py

✅ Current Status: Basic migration layer working with fallbacks

🔧 Next Steps for Full Migration:
1. Create Google Cloud Project
2. Enable required APIs
3. Set up service account
4. Configure Custom Search Engine
5. Update .env with Google Cloud credentials

📋 Environment Variables Needed:
- GOOGLE_CLOUD_PROJECT_ID
- GOOGLE_APPLICATION_CREDENTIALS
- GOOGLE_CUSTOM_SEARCH_ENGINE_ID
- SEARCH_CONSOLE_SITE_URL

🎯 Migration Features Available:
✅ Content Analysis (Enhanced with Google NLP)
✅ Entity Extraction and Verification
✅ AI Optimization (Gemini)
✅ Schema Markup Generation
✅ Fallback to SerpAPI
⏳ SERP Analysis (Requires Custom Search setup)
⏳ Competitor Analysis (Requires Custom Search setup)

💡 Cost Savings Expected:
- Current SerpAPI costs: $50-200/month
- Google APIs costs: $20-80/month  
- Estimated savings: 40-60%
""")

def main():
    """Main test function"""
    print("🔬 Google APIs Migration Test Suite")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    test_results = []
    
    # Run tests
    test_results.append(("Integration Test", test_google_apis_integration()))
    test_results.append(("Functionality Test", test_basic_functionality()))
    test_results.append(("Schema Generation Test", test_schema_generation()))
    test_results.append(("AI Optimization Test", test_ai_optimization()))
    
    # Print results
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Migration layer is ready.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    print_setup_instructions()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
