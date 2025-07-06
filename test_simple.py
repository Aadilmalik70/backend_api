#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_simple():
    print("🔍 Simple test...")
    
    processor = KeywordProcessorEnhancedReal()
    
    # Test just the SerpAPI fallback
    try:
        keywords = processor._get_keywords_from_serpapi(["SEO tools"])
        print(f"SerpAPI fallback returned: {len(keywords)} keywords")
        for kw in keywords:
            print(f"  - {kw}")
    except Exception as e:
        print(f"Error in SerpAPI fallback: {e}")
    
    # Test the full enhanced method
    try:
        keywords = processor._get_enhanced_keyword_ideas(["SEO tools"])
        print(f"Enhanced method returned: {len(keywords)} keywords")
        for kw in keywords:
            print(f"  - {kw}")
    except Exception as e:
        print(f"Error in enhanced method: {e}")

if __name__ == "__main__":
    test_simple()
