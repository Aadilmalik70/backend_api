#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Quick test to debug keyword extraction
def test_keyword_extraction():
    print("🔍 Testing keyword extraction...")
    
    processor = KeywordProcessorEnhancedReal()
    
    print(f"Google APIs enabled: {processor.google_apis_enabled}")
    print(f"Google Search client: {processor.google_search is not None}")
    print(f"SerpAPI available: {processor.keyword_planner.available}")
    
    # Test the enhanced keyword processing
    result = processor.process_keywords("SEO tools and digital marketing strategies")
    
    print(f"✅ Seed keywords: {result['seed_keywords']}")
    print(f"✅ Keyword metrics: {len(result['keyword_metrics'])}")
    print(f"✅ Related keywords: {len(result['related_keywords'])}")
    
    if result['related_keywords']:
        print("📋 First few related keywords:")
        for i, keyword in enumerate(result['related_keywords'][:5]):
            print(f"  {i+1}. {keyword.get('keyword', 'N/A')} (source: {keyword.get('source', 'N/A')})")
    else:
        print("❌ No related keywords found")
        
        # Let's test the fallback method directly
        print("\n🔍 Testing fallback method directly...")
        fallback_keywords = processor._get_keywords_from_serpapi(["SEO tools"])
        print(f"Fallback keywords: {len(fallback_keywords)}")
        for i, keyword in enumerate(fallback_keywords[:3]):
            print(f"  {i+1}. {keyword.get('keyword', 'N/A')} (source: {keyword.get('source', 'N/A')})")
    
    return len(result['related_keywords']) > 0

if __name__ == "__main__":
    success = test_keyword_extraction()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
