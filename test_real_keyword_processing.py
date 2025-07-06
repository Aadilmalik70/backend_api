#!/usr/bin/env python3
"""
Test Real Keyword Processing with Google APIs (No Fallback)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_real_keyword_processing():
    """Test keyword processing with real Google APIs data"""
    print("🔍 Testing Real Keyword Processing (No Fallback)")
    print("=" * 60)
    
    # Force disable fallback for testing
    os.environ['FALLBACK_TO_SERPAPI'] = 'false'
    
    # Initialize processor
    processor = KeywordProcessorEnhancedReal()
    
    print(f"📊 Google APIs enabled: {processor.google_apis_enabled}")
    print(f"🔍 Google Search configured: {processor.google_search.api_key is not None}")
    print(f"🧠 Knowledge Graph configured: {processor.knowledge_graph.api_key is not None}")
    
    if not processor.google_apis_enabled:
        print("❌ Google APIs not enabled. Please configure your .env file.")
        return False
    
    # Test with real keywords
    test_keywords = ["SEO tools", "digital marketing", "content strategy"]
    
    for keyword in test_keywords:
        print(f"\n📋 Testing keyword: '{keyword}'")
        print("-" * 40)
        
        try:
            # Test Google Search method directly
            print("🔍 Testing Google Custom Search extraction...")
            search_results = processor._get_keywords_from_google_search([keyword])
            
            if search_results:
                print(f"✅ Found {len(search_results)} related keywords from Google Search")
                
                for i, kw in enumerate(search_results[:5]):
                    print(f"  {i+1}. '{kw['keyword']}' (volume: {kw['search_volume']}, source: {kw['source']})")
                    
                # Check if this is real data
                if any('mock' in str(kw).lower() or 'fallback' in str(kw).lower() for kw in search_results):
                    print("⚠️ Some results appear to be mock/fallback data")
                else:
                    print("✅ Results appear to be real Google API data")
            else:
                print("❌ No keywords found from Google Search")
            
            # Test entity enhancement
            print("\n🧠 Testing Knowledge Graph entity enhancement...")
            if search_results:
                enhanced_results = processor._enhance_keywords_with_entities(search_results[:3])
                
                entities_found = sum(1 for kw in enhanced_results if kw.get('entities'))
                print(f"✅ Enhanced {entities_found}/{len(enhanced_results)} keywords with entities")
                
                for kw in enhanced_results[:2]:
                    if kw.get('entities'):
                        print(f"  '{kw['keyword']}' has {len(kw['entities'])} entities")
            
        except Exception as e:
            print(f"❌ Error processing '{keyword}': {str(e)}")
    
    print("\n" + "=" * 60)
    print("📊 FULL WORKFLOW TEST")
    print("=" * 60)
    
    # Test full workflow
    try:
        test_input = "SEO tools and digital marketing strategies"
        print(f"🔍 Testing full workflow with: '{test_input}'")
        
        result = processor.process_keywords(test_input)
        
        print(f"✅ Seed keywords: {len(result['seed_keywords'])} found")
        print(f"✅ Keyword metrics: {len(result['keyword_metrics'])} processed")
        print(f"✅ Related keywords: {len(result['related_keywords'])} generated")
        
        if result['related_keywords']:
            print("\n📋 Sample related keywords:")
            for i, kw in enumerate(result['related_keywords'][:5]):
                source = kw.get('source', 'unknown')
                entities = len(kw.get('entities', []))
                print(f"  {i+1}. '{kw['keyword']}' (source: {source}, entities: {entities})")
        
        # Check for real data indicators
        real_data_indicators = 0
        total_keywords = len(result['related_keywords'])
        
        for kw in result['related_keywords']:
            if kw.get('source') == 'google_search':
                real_data_indicators += 1
            if kw.get('entities'):
                real_data_indicators += 1
        
        print(f"\n📊 Real data confidence: {real_data_indicators}/{total_keywords * 2} indicators")
        
        if real_data_indicators > 0:
            print("✅ Real Google APIs data detected!")
        else:
            print("⚠️ No real data indicators found - may be using fallback")
            
        return True
        
    except Exception as e:
        print(f"❌ Full workflow test failed: {str(e)}")
        return False

def check_api_configuration():
    """Check if APIs are properly configured for real data"""
    print("\n🔧 Checking API Configuration...")
    
    issues = []
    
    # Check Google API key
    if not os.getenv('GOOGLE_API_KEY'):
        issues.append("GOOGLE_API_KEY not set")
    
    # Check Custom Search Engine ID
    if not os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID'):
        issues.append("GOOGLE_CUSTOM_SEARCH_ENGINE_ID not set")
    
    # Check fallback setting
    fallback = os.getenv('FALLBACK_TO_SERPAPI', 'false').lower()
    if fallback != 'false':
        issues.append("FALLBACK_TO_SERPAPI not set to 'false' - may use mock data")
    
    if issues:
        print("❌ Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Configuration looks good for real data testing")
        return True

if __name__ == "__main__":
    print("🚀 Real Keyword Processing Test")
    print("=" * 60)
    
    # Check configuration
    config_ok = check_api_configuration()
    
    if not config_ok:
        print("\n📋 Setup Required:")
        print("1. Configure your .env file with real Google API keys")
        print("2. Set FALLBACK_TO_SERPAPI=false")
        print("3. Follow SETUP_REAL_GOOGLE_APIS.md")
        sys.exit(1)
    
    # Run the test
    success = test_real_keyword_processing()
    
    if success:
        print("\n🎉 Real keyword processing test completed!")
        print("✅ Phase 2.4 is working with real Google APIs data")
    else:
        print("\n❌ Real keyword processing test failed")
        print("⚠️ Check your Google APIs configuration")
    
    sys.exit(0 if success else 1)
