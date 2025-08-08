#!/usr/bin/env python3
"""
Debug script to test competitor analysis directly
"""

import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from utils.quick_competitor_analyzer import QuickCompetitorAnalyzer
    from services.blueprint_analyzer import BlueprintAnalyzer
    
    print("[TEST] Testing QuickCompetitorAnalyzer directly")
    print("=" * 50)
    
    # Test QuickCompetitorAnalyzer
    quick_analyzer = QuickCompetitorAnalyzer()
    
    keyword = "python machine learning tutorial"
    print(f"[TEST] Analyzing keyword: {keyword}")
    
    result = quick_analyzer.analyze_competitors_quick(keyword)
    
    print(f"[RESULT] Analysis Status: {result.get('analysis_status', 'N/A')}")
    print(f"[RESULT] Analysis Method: {result.get('analysis_method', 'N/A')}")
    print(f"[RESULT] Total Competitors: {result.get('total_competitors', 0)}")
    print(f"[RESULT] Successful Analyses: {result.get('successful_analyses', 0)}")
    print(f"[RESULT] Top Competitors Count: {len(result.get('top_competitors', []))}")
    print(f"[RESULT] Competitors Count: {len(result.get('competitors', []))}")
    
    if result.get('competitors'):
        print(f"\n[COMPETITORS] Sample competitor data:")
        for i, comp in enumerate(result['competitors'][:2]):
            print(f"   {i+1}. URL: {comp.get('url', 'N/A')}")
            print(f"      Title: {comp.get('title', 'N/A')[:50]}...")
            print(f"      Word Count: {comp.get('content_length', 0)}")
    
    print(f"\n[INSIGHTS] Common Topics: {result.get('insights', {}).get('common_topics', [])}")
    
    # Now test BlueprintAnalyzer
    print(f"\n[TEST] Testing BlueprintAnalyzer")
    print("=" * 30)
    
    blueprint_analyzer = BlueprintAnalyzer(serpapi_key=None, gemini_api_key="test")
    
    # Test direct competitor analysis
    competitors = blueprint_analyzer.analyze_competitors(keyword)
    
    print(f"[ANALYZER] Analysis Status: {competitors.get('analysis_status', 'N/A')}")
    print(f"[ANALYZER] Total Competitors: {competitors.get('total_competitors', 0)}")
    print(f"[ANALYZER] Top Competitors Count: {len(competitors.get('top_competitors', []))}")
    
    # Test content insights 
    content_insights = blueprint_analyzer.analyze_competitor_content(competitors)
    print(f"[INSIGHTS] Analysis Status: {content_insights.get('analysis_status', 'N/A')}")
    print(f"[INSIGHTS] Avg Word Count: {content_insights.get('avg_word_count', 0)}")
    
    # Test content gaps
    content_gaps = blueprint_analyzer.analyze_content_gaps(competitors, keyword)
    print(f"[GAPS] Analysis Status: {content_gaps.get('analysis_status', 'N/A')}")
    print(f"[GAPS] Content Opportunities: {len(content_gaps.get('content_opportunities', []))}")
    
    print(f"\n[SUCCESS] Direct testing completed successfully!")
    
except Exception as e:
    print(f"[ERROR] Direct testing failed: {e}")
    import traceback
    traceback.print_exc()