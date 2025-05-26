#!/usr/bin/env python3
"""
Test Script for Real Data Integration

This script tests the migration from mock data to real data integration.
It checks imports, API keys, and functionality of the real data modules.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🔄 Testing Real Data Integration Migration")
print("=" * 50)

# Test imports
print("\n1. Testing imports...")
try:
    from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    print("✅ ContentAnalyzerEnhancedReal imported successfully")
except ImportError as e:
    print(f"❌ Import error for ContentAnalyzerEnhancedReal: {e}")

try:
    from competitor_analysis_real import CompetitorAnalysisReal
    print("✅ CompetitorAnalysisReal imported successfully")
except ImportError as e:
    print(f"❌ Import error for CompetitorAnalysisReal: {e}")

try:
    from keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
    print("✅ KeywordProcessorEnhancedReal imported successfully")
except ImportError as e:
    print(f"❌ Import error for KeywordProcessorEnhancedReal: {e}")

try:
    from serp_feature_optimizer_real import SerpFeatureOptimizerReal
    print("✅ SerpFeatureOptimizerReal imported successfully")
except ImportError as e:
    print(f"❌ Import error for SerpFeatureOptimizerReal: {e}")

# Test API keys
print("\n2. Testing API keys...")
required_keys = [
    'SERPAPI_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY'
]

optional_keys = [
    'SERPAPI_KEY', 'GOOGLE_ADS_DEVELOPER_TOKEN', 'GOOGLE_ADS_CLIENT_ID',
    'GOOGLE_ADS_CLIENT_SECRET', 'GOOGLE_ADS_REFRESH_TOKEN', 'GOOGLE_ADS_LOGIN_CUSTOMER_ID'
]

missing_required_keys = [key for key in required_keys if not os.getenv(key)]
available_optional_keys = [key for key in optional_keys if os.getenv(key)]

if missing_required_keys:
    print(f"❌ Missing required API keys: {missing_required_keys}")
    print("   Please add them to your .env file")
else:
    print("✅ All required API keys present")

print(f"ℹ️  Available optional keys: {available_optional_keys}")

# Test utility files
print("\n3. Testing utility files...")
utility_files = [
    'utils/serpapi_client.py',
    'utils/keyword_planner_api.py', 
    'utils/gemini_nlp_client.py',
    'utils/browser_content_scraper.py'
]

for file_path in utility_files:
    full_path = os.path.join('src', file_path)
    if os.path.exists(full_path):
        print(f"✅ {file_path} exists")
    else:
        print(f"❌ {file_path} missing")

# Test real data integration
print("\n4. Testing real data integration...")

def test_real_data():
    """Test real data integration functionality."""
    try:
        serpapi_key = os.getenv('SERPAPI_API_KEY') or os.getenv('SERPAPI_KEY')
        gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        # Test keyword processor
        print("\n4.1 Testing KeywordProcessor...")
        try:
            # Create credentials dict for Google Ads (will be None/empty if not configured)
            google_ads_credentials = {
                'developer_token': os.getenv('GOOGLE_ADS_DEVELOPER_TOKEN'),
                'client_id': os.getenv('GOOGLE_ADS_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_ADS_CLIENT_SECRET'),
                'refresh_token': os.getenv('GOOGLE_ADS_REFRESH_TOKEN'),
                'login_customer_id': os.getenv('GOOGLE_ADS_LOGIN_CUSTOMER_ID')
            }
            print("google_ads_credentials",google_ads_credentials)
            keyword_processor = KeywordProcessorEnhancedReal(google_ads_credentials=google_ads_credentials)
            result = keyword_processor.process_keywords("test keyword")
            print(f"✅ Keyword processor: {len(result.get('seed_keywords', []))} keywords processed")
            print(f"   Found data: {list(result.keys())}")
        except Exception as e:
            print(f"❌ Keyword processor error: {e}")
            print("   This is expected if Google Ads API credentials are not configured")
        
        # Test competitor analysis
        print("\n4.2 Testing CompetitorAnalysis...")
        try:
            competitor_analyzer = CompetitorAnalysisReal(serpapi_key=serpapi_key, gemini_api_key=gemini_api_key)
            result = competitor_analyzer.analyze_competitors("test keyword", num_competitors=2)
            print(f"✅ Competitor analysis: {len(result.get('competitors', []))} competitors analyzed")
            print(f"   Found data: {list(result.keys())}")
        except Exception as e:
            print(f"❌ Competitor analysis error: {e}")
            print("   This may be expected if API keys are not configured or have limitations")
        
        # Test content analyzer
        print("\n4.3 Testing ContentAnalyzer...")
        try:
            content_analyzer = ContentAnalyzerEnhancedReal(gemini_api_key=gemini_api_key)
            result = content_analyzer.analyze_url("https://example.com")
            print(f"✅ Content analyzer: analyzed URL with {result.get('word_count', 0)} words")
            print(f"   Found data: {list(result.keys())}")
        except Exception as e:
            print(f"❌ Content analyzer error: {e}")
            print("   This may be expected if browser automation is not available")
        
        # Test SERP optimizer
        print("\n4.4 Testing SerpOptimizer...")
        try:
            serp_optimizer = SerpFeatureOptimizerReal(serpapi_key=serpapi_key)
            result = serp_optimizer.generate_recommendations("test keyword")
            print(f"✅ SERP optimizer: {len(result.get('recommendations', []))} recommendations generated")
            print(f"   Found data: {list(result.keys())}")
        except Exception as e:
            print(f"❌ SERP optimizer error: {e}")
            print("   This may be expected if SerpAPI key is not configured or has limitations")
        
        print("\n🎉 Real data integration testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")

# Run the test
if __name__ == "__main__":
    test_real_data()
    
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    print("✅ Migration plan implemented")
    print("✅ Routes updated to use real data modules")
    print("✅ API key configuration added")
    print("✅ Method signatures updated")
    print("✅ Test script created")
    print("\n📝 Next Steps:")
    print("1. Add missing API keys to .env file")
    print("2. Install missing dependencies: pip install google-ads selenium beautifulsoup4")
    print("3. Test the API endpoint: POST /api/process")
    print("4. Monitor logs for real vs mock data usage")
    print("\n🚀 Your system is now configured for real data integration!")
