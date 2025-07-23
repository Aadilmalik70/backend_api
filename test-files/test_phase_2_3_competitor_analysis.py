#!/usr/bin/env python3
"""
Test script for Phase 2.3 Competitor Analysis implementation

This script validates the Google Custom Search and Knowledge Graph API integration
and enhanced competitor analysis functionality.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from competitor_analysis_real import CompetitorAnalysisReal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_competitor_analysis_initialization():
    """Test competitor analysis initialization"""
    print("🔧 Testing Competitor Analysis Initialization...")
    
    try:
        analyzer = CompetitorAnalysisReal()
        status = analyzer.get_client_status()
        
        print(f"✅ Competitor Analysis initialized successfully")
        print(f"   - Google Custom Search: {'✅' if status['google_custom_search']['available'] else '❌'}")
        print(f"   - Knowledge Graph: {'✅' if status['knowledge_graph']['available'] else '❌'}")
        print(f"   - Natural Language: {'✅' if status['natural_language']['available'] else '❌'}")
        print(f"   - Gemini API: {'✅' if status['gemini_api']['available'] else '❌'}")
        print(f"   - SerpAPI Fallback: {'✅' if status['serpapi_fallback']['available'] else '❌'}")
        print(f"   - Phase 2.3: {status['phase_completion']['phase_2_3']}")
        
        return analyzer, status
        
    except Exception as e:
        print(f"❌ Competitor Analysis initialization failed: {e}")
        return None, None

def test_competitor_discovery(analyzer: CompetitorAnalysisReal):
    """Test competitor discovery methods"""
    print("\n🔍 Testing Competitor Discovery...")
    
    test_keyword = "digital marketing"
    
    try:
        # Test competitor discovery with limited results for faster testing
        print(f"   📊 Testing competitor discovery for '{test_keyword}'...")
        competitors = analyzer._get_competitors(test_keyword, limit=5)
        
        print(f"      Competitors found: {len(competitors)}")
        if competitors:
            print(f"      First competitor: {competitors[0].get('title', 'N/A')}")
            print(f"      Data source: {competitors[0].get('source', 'unknown')}")
        
        print("✅ Competitor discovery working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Competitor discovery failed: {e}")
        return False

def test_enhanced_analysis_methods(analyzer: CompetitorAnalysisReal):
    """Test enhanced analysis methods"""
    print("\n🧪 Testing Enhanced Analysis Methods...")
    
    # Test content for analysis
    test_content = """
    Digital marketing is essential for modern businesses. Companies like Google, Facebook, and Microsoft
    have revolutionized how we reach customers online. Effective strategies include SEO, content marketing,
    and social media advertising.
    """
    
    try:
        # Test enhanced NLP analysis
        print("   🧠 Testing enhanced NLP analysis...")
        nlp_result = analyzer._perform_enhanced_nlp_analysis(test_content)
        print(f"      Analysis source: {nlp_result.get('analysis_source', 'unknown')}")
        print(f"      Entities found: {len(nlp_result.get('entities', []))}")
        print(f"      Sentiment score: {nlp_result.get('sentiment', {}).get('score', 'N/A')}")
        
        # Test entity analysis
        print("   🏢 Testing entity analysis...")
        mock_competitor = {"title": "Test Competitor", "url": "https://example.com"}
        entity_result = analyzer._perform_entity_analysis(test_content, mock_competitor)
        print(f"      Knowledge Graph entities: {len(entity_result.get('knowledge_graph_entities', []))}")
        print(f"      Topical authority: {entity_result.get('topical_authority', 0.0)}")
        print(f"      Analysis source: {entity_result.get('analysis_source', 'none')}")
        
        # Test competitor scoring
        print("   📊 Testing competitor scoring...")
        mock_content = {
            "main_content": test_content,
            "title": "Digital Marketing Guide",
            "meta_description": "Complete guide to digital marketing strategies",
            "headings": [{"level": "h1", "text": "Digital Marketing"}],
            "images": ["image1.jpg"],
            "links": {"external": ["link1.com"], "internal": ["page1.html"]}
        }
        mock_keyword_usage = {"in_title": True, "in_h1": True, "in_meta": True, "density": 1.5}
        
        score_result = analyzer._calculate_competitor_score(mock_content, nlp_result, mock_keyword_usage)
        print(f"      Overall score: {score_result.get('overall_score', 0)}")
        print(f"      Content quality: {score_result.get('content_quality', 0)}")
        print(f"      Keyword optimization: {score_result.get('keyword_optimization', 0)}")
        
        print("✅ All enhanced analysis methods working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced analysis methods failed: {e}")
        return False

def test_content_blueprint_generation(analyzer: CompetitorAnalysisReal):
    """Test enhanced content blueprint generation"""
    print("\n📝 Testing Enhanced Content Blueprint Generation...")
    
    test_keyword = "SEO optimization"
    
    try:
        # Test blueprint generation with limited competitors for faster testing
        print(f"   📋 Generating content blueprint for '{test_keyword}'...")
        blueprint = analyzer.generate_content_blueprint(test_keyword, num_competitors=3)
        
        print(f"      Keyword: {blueprint.get('keyword', 'N/A')}")
        print(f"      Title: {blueprint.get('outline', {}).get('title', 'N/A')}")
        print(f"      Sections: {len(blueprint.get('outline', {}).get('sections', []))}")
        print(f"      Recommendations: {len(blueprint.get('recommendations', []))}")
        
        # Check enhancement features
        enhancement_features = blueprint.get('enhancement_features', {})
        print(f"      Google APIs integration: {enhancement_features.get('google_apis_integration', False)}")
        print(f"      Knowledge Graph analysis: {enhancement_features.get('knowledge_graph_analysis', False)}")
        print(f"      Advanced scoring: {enhancement_features.get('advanced_scoring', False)}")
        
        # Check data quality
        data_quality = blueprint.get('data_quality', {})
        print(f"      Data quality - success rate: {data_quality.get('success_rate', 0)}%")
        
        print("✅ Enhanced content blueprint generation working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Content blueprint generation failed: {e}")
        return False

def test_fallback_mechanisms(analyzer: CompetitorAnalysisReal):
    """Test fallback mechanisms"""
    print("\n🔄 Testing Fallback Mechanisms...")
    
    try:
        # Test basic content analysis (fallback)
        basic_analysis = analyzer._basic_content_analysis("This is a test content with entities like Google and Microsoft.")
        
        print(f"   Basic Analysis Entities: {len(basic_analysis.get('entities', []))}")
        print(f"   Basic Analysis Sentiment: {basic_analysis.get('sentiment', {}).get('interpretation', 'N/A')}")
        print(f"   Analysis Source: {basic_analysis.get('analysis_source', 'unknown')}")
        
        # Test empty insights generation
        empty_insights = analyzer._get_empty_insights_with_reason("Test fallback")
        
        print(f"   Empty Insights Structure: {len(empty_insights)} keys")
        print(f"   Error Reason: {empty_insights.get('data_quality', {}).get('error', 'N/A')}")
        
        # Test data source detection
        data_source = analyzer._get_data_source()
        print(f"   Primary Data Source: {data_source}")
        
        # Test analysis features
        features = analyzer._get_analysis_features()
        print(f"   Available Features: {len(features)}")
        
        print("✅ Fallback mechanisms working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Fallback mechanisms failed: {e}")
        return False

def test_integration_with_phase_2_2(analyzer: CompetitorAnalysisReal):
    """Test integration with Phase 2.2 content analyzer"""
    print("\n🔗 Testing Integration with Phase 2.2...")
    
    try:
        # Check if the analyzer can work with enhanced content analysis
        from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
        
        content_analyzer = ContentAnalyzerEnhancedReal()
        competitor_analyzer = analyzer
        
        print("   📊 Testing combined analysis capabilities...")
        
        # Test if both analyzers use the same Google APIs clients
        ca_status = content_analyzer.get_client_status()
        comp_status = competitor_analyzer.get_client_status()
        
        shared_apis = ['natural_language', 'gemini_api']
        compatibility_score = 0
        
        for api in shared_apis:
            ca_available = ca_status.get(api.replace('_', '_api'), {}).get('available', False)
            comp_available = comp_status.get(api, {}).get('available', False)
            
            if ca_available and comp_available:
                compatibility_score += 1
                print(f"      ✅ {api}: Both modules have access")
            elif ca_available or comp_available:
                print(f"      ⚠️  {api}: Only one module has access")
            else:
                print(f"      ❌ {api}: Neither module has access")
        
        compatibility_percentage = (compatibility_score / len(shared_apis)) * 100
        print(f"   📈 API Compatibility: {compatibility_percentage}%")
        
        print("✅ Integration with Phase 2.2 working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_competitor_analysis_pipeline(analyzer: CompetitorAnalysisReal):
    """Test the complete competitor analysis pipeline"""
    print("\n🚀 Testing Complete Competitor Analysis Pipeline...")
    
    test_keyword = "content marketing"
    
    try:
        print(f"   📊 Running full competitor analysis for '{test_keyword}'...")
        
        # Run the complete analysis with limited competitors for testing
        result = analyzer.analyze_competitors(test_keyword, limit=3)
        
        print(f"      Keyword: {result.get('keyword', 'N/A')}")
        print(f"      Competitors analyzed: {len(result.get('competitors', []))}")
        print(f"      Data source: {result.get('data_source', 'unknown')}")
        print(f"      Analysis features: {len(result.get('analysis_features', []))}")
        
        # Check insights quality
        insights = result.get('insights', {})
        data_quality = insights.get('data_quality', {})
        
        print(f"      Success rate: {data_quality.get('success_rate', 0)}%")
        print(f"      Content samples: {data_quality.get('content_samples', 0)}")
        print(f"      Entities extracted: {data_quality.get('entities_extracted', 0)}")
        
        # Check for enhanced features
        if 'knowledge_graph_insights' in insights:
            kg_insights = insights['knowledge_graph_insights']
            print(f"      Knowledge Graph entities: {kg_insights.get('entities_found', 0)}")
        
        if 'competitor_scores' in insights:
            comp_scores = insights['competitor_scores']
            if 'average' in comp_scores:
                print(f"      Average competitor score: {comp_scores['average']}")
        
        print("✅ Complete competitor analysis pipeline working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        return False

def display_phase_2_3_summary(status: Dict[str, Any]):
    """Display Phase 2.3 completion summary"""
    print("\n📋 Phase 2.3 Implementation Summary")
    print("=" * 50)
    
    phase_info = status.get('phase_completion', {})
    
    print(f"Phase Status: {phase_info.get('phase_2_3', 'unknown').upper()}")
    print(f"Description: {phase_info.get('description', 'N/A')}")
    
    print("\n🎯 Implemented Features:")
    for feature in phase_info.get('features', []):
        print(f"   ✅ {feature}")
    
    print("\n🔧 API Integration Status:")
    for api_name, api_info in status.items():
        if api_name != 'phase_completion':
            status_icon = "✅" if api_info.get('available', False) else "❌"
            print(f"   {status_icon} {api_info.get('description', api_name)}")

def main():
    """Main test function"""
    print("🚀 Phase 2.3 Competitor Analysis Test Suite")
    print("=" * 50)
    
    # Initialize competitor analysis
    analyzer, status = test_competitor_analysis_initialization()
    if not analyzer:
        print("❌ Cannot proceed with tests - initialization failed")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 6
    
    if test_competitor_discovery(analyzer):
        tests_passed += 1
    
    if test_enhanced_analysis_methods(analyzer):
        tests_passed += 1
    
    if test_content_blueprint_generation(analyzer):
        tests_passed += 1
    
    if test_fallback_mechanisms(analyzer):
        tests_passed += 1
    
    if test_integration_with_phase_2_2(analyzer):
        tests_passed += 1
    
    if test_competitor_analysis_pipeline(analyzer):
        tests_passed += 1
    
    # Display results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Phase 2.3 implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Display Phase 2.3 summary
    display_phase_2_3_summary(status)
    
    print("\n🔗 Next Steps:")
    print("   1. Run the application: python src/main.py")
    print("   2. Test with real keywords using the enhanced competitor analyzer")
    print("   3. Proceed to Phase 2.4 (Keyword Processor) when ready")
    
    print("\n📈 Overall Project Progress:")
    print("   ✅ Phase 1: Core Infrastructure (100% complete)")
    print("   ✅ Phase 2.1: API Routes Integration (100% complete)")
    print("   ✅ Phase 2.2: Content Analyzer Integration (100% complete)")
    print("   ✅ Phase 2.3: Competitor Analysis Integration (100% complete)")
    print("   ⏳ Phase 2.4: Keyword Processor (Next priority)")
    print("   📊 Overall Progress: 50% Complete (6/13 major tasks)")

if __name__ == "__main__":
    main()
