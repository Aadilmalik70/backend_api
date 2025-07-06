#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer

# Test the SerpAPI analyzer directly
def test_serpapi_analyzer():
    print("🔍 Testing SerpAPI analyzer directly...")
    
    analyzer = SerpAPIKeywordAnalyzer()
    
    print(f"Available: {analyzer.available}")
    
    # Test keyword ideas
    try:
        ideas = analyzer.get_keyword_ideas(["SEO tools"])
        print(f"Keyword ideas returned: {len(ideas)}")
        for keyword, data in ideas.items():
            print(f"  - {keyword}: {data.get('search_volume', 'N/A')} searches/month")
    except Exception as e:
        print(f"Error: {e}")
    
    return True

if __name__ == "__main__":
    test_serpapi_analyzer()
