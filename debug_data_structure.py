#!/usr/bin/env python3
"""
Debug script to examine data structure differences
"""

import sys
import os
import logging
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from utils.quick_competitor_analyzer import QuickCompetitorAnalyzer
    from services.blueprint_analyzer import BlueprintAnalyzer
    
    keyword = "python machine learning tutorial"
    
    # Test QuickCompetitorAnalyzer
    quick_analyzer = QuickCompetitorAnalyzer()
    quick_result = quick_analyzer.analyze_competitors_quick(keyword)
    
    print("=" * 60)
    print("QUICK ANALYZER RESULT STRUCTURE:")
    print("=" * 60)
    print(f"Keys: {list(quick_result.keys())}")
    print(f"'top_competitors' exists: {'top_competitors' in quick_result}")
    print(f"'competitors' exists: {'competitors' in quick_result}")
    print(f"'top_competitors' count: {len(quick_result.get('top_competitors', []))}")
    print(f"'competitors' count: {len(quick_result.get('competitors', []))}")
    
    if quick_result.get('top_competitors'):
        print("\nSample 'top_competitors' structure:")
        comp = quick_result['top_competitors'][0]
        print(f"  Keys: {list(comp.keys())}")
        print(f"  URL: {comp.get('url', 'N/A')}")
        print(f"  Title: {comp.get('title', 'N/A')[:50]}...")
        print(f"  Content Length: {comp.get('content_length', 0)}")
    
    # Test BlueprintAnalyzer competitor analysis
    blueprint_analyzer = BlueprintAnalyzer(serpapi_key=None, gemini_api_key="test")
    blueprint_result = blueprint_analyzer.analyze_competitors(keyword)
    
    print("\n" + "=" * 60)
    print("BLUEPRINT ANALYZER COMPETITOR RESULT STRUCTURE:")
    print("=" * 60)
    print(f"Keys: {list(blueprint_result.keys())}")
    print(f"'top_competitors' exists: {'top_competitors' in blueprint_result}")
    print(f"'competitors' exists: {'competitors' in blueprint_result}")
    print(f"'top_competitors' count: {len(blueprint_result.get('top_competitors', []))}")
    print(f"'competitors' count: {len(blueprint_result.get('competitors', []))}")
    
    # Test content insights directly
    print("\n" + "=" * 60)
    print("TESTING CONTENT INSIGHTS LOGIC:")
    print("=" * 60)
    
    # Test with QuickAnalyzer result
    print("Testing with QuickAnalyzer result:")
    content_insights_quick = blueprint_analyzer.analyze_competitor_content(quick_result)
    print(f"  Status: {content_insights_quick.get('analysis_status')}")
    print(f"  Avg Word Count: {content_insights_quick.get('avg_word_count')}")
    
    # Test with BlueprintAnalyzer result
    print("\nTesting with BlueprintAnalyzer result:")
    content_insights_blueprint = blueprint_analyzer.analyze_competitor_content(blueprint_result)
    print(f"  Status: {content_insights_blueprint.get('analysis_status')}")
    print(f"  Avg Word Count: {content_insights_blueprint.get('avg_word_count')}")
    
    # Check the condition that causes no_competitors
    print("\n" + "=" * 60)
    print("DEBUGGING THE CONDITION:")
    print("=" * 60)
    
    for name, result in [("QuickAnalyzer", quick_result), ("BlueprintAnalyzer", blueprint_result)]:
        print(f"\n{name} result:")
        print(f"  'top_competitors' in competitors: {'top_competitors' in result}")
        print(f"  competitors['top_competitors']: {result.get('top_competitors', 'KEY_MISSING')}")
        print(f"  bool(competitors['top_competitors']): {bool(result.get('top_competitors', []))}")
        
        # This is the condition from line 176 in blueprint_analyzer.py
        condition = 'top_competitors' not in result or not result['top_competitors']
        print(f"  Condition ('top_competitors' not in competitors or not competitors['top_competitors']): {condition}")
    
except Exception as e:
    print(f"[ERROR] Debug script failed: {e}")
    import traceback
    traceback.print_exc()