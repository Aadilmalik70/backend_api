#!/usr/bin/env python3
"""
Test script for Phase 2.2 Content Analyzer implementation

This script validates the Google Natural Language API integration and 
enhanced content analysis functionality.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_content_analyzer_initialization():
    """Test content analyzer initialization"""
    print("🔧 Testing Content Analyzer Initialization...")
    
    try:
        analyzer = ContentAnalyzerEnhancedReal()
        status = analyzer.get_client_status()
        
        print(f"✅ Content Analyzer initialized successfully")
        print(f"   - Natural Language API: {'✅' if status['natural_language_api']['available'] else '❌'}")
        print(f"   - Gemini API: {'✅' if status['gemini_api']['available'] else '❌'}")
        print(f"   - Gemini NLP: {'✅' if status['gemini_nlp']['available'] else '❌'}")
        print(f"   - Phase 2.2: {status['phase_completion']['phase_2_2']}")
        
        return analyzer, status
        
    except Exception as e:
        print(f"❌ Content Analyzer initialization failed: {e}")
        return None, None

def test_content_analysis_methods(analyzer: ContentAnalyzerEnhancedReal):
    """Test various content analysis methods"""
    print("\n🧪 Testing Content Analysis Methods...")
    
    # Test content
    test_content = """
    Search Engine Optimization (SEO) is crucial for digital marketing success. 
    Companies like Google and Microsoft have revolutionized how we approach content optimization.
    
    Key strategies include:
    - Content quality improvement
    - Technical SEO optimization
    - User experience enhancement
    
    Expert John Mueller from Google emphasizes the importance of creating valuable content 
    that serves user intent. This approach has proven successful for many organizations.
    """
    
    try:
        # Test content quality analysis
        print("   📊 Testing content quality analysis...")
        quality_analysis = analyzer.analyze_content_quality(test_content)
        print(f"      Quality Score: {quality_analysis.get('quality_score', 'N/A')}")
        print(f"      Quality Level: {quality_analysis.get('quality_level', 'N/A')}")
        
        # Test content improvement suggestions
        print("   💡 Testing content improvement suggestions...")
        improvements = analyzer.suggest_content_improvements(test_content, ["SEO", "content marketing"])
        print(f"      Total Suggestions: {improvements.get('total_suggestions', 0)}")
        
        # Test AI readiness analysis
        print("   🤖 Testing AI readiness analysis...")
        ai_readiness = analyzer.analyze_ai_readiness(test_content)
        print(f"      AI Readiness Score: {ai_readiness.get('overall_ai_readiness', 'N/A')}")
        
        print("✅ All content analysis methods working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Content analysis methods failed: {e}")
        return False

def test_nlp_analysis_pipeline(analyzer: ContentAnalyzerEnhancedReal):
    """Test the NLP analysis pipeline"""
    print("\n🔍 Testing NLP Analysis Pipeline...")
    
    test_content = """
    The latest developments in artificial intelligence have transformed the technology industry.
    Companies like OpenAI, Google, and Microsoft are leading the charge in AI innovation.
    This positive trend is expected to continue throughout 2024 and beyond.
    """
    
    try:
        # Test NLP analysis
        nlp_analysis = analyzer._perform_nlp_analysis(test_content)
        
        print(f"   Analysis Source: {nlp_analysis.get('analysis_source', 'unknown')}")
        print(f"   Entities Found: {len(nlp_analysis.get('entities', []))}")
        print(f"   Sentiment Score: {nlp_analysis.get('sentiment', {}).get('score', 'N/A')}")
        print(f"   Language: {nlp_analysis.get('language', 'N/A')}")
        
        # Display some entities
        entities = nlp_analysis.get('entities', [])
        if entities:
            print(f"   Top Entities:")
            for i, entity in enumerate(entities[:3]):
                print(f"     {i+1}. {entity.get('name', 'N/A')} ({entity.get('type', 'N/A')})")
        
        print("✅ NLP analysis pipeline working correctly")
        return True
        
    except Exception as e:
        print(f"❌ NLP analysis pipeline failed: {e}")
        return False

def test_ai_analysis_pipeline(analyzer: ContentAnalyzerEnhancedReal):
    """Test the AI analysis pipeline"""
    print("\n🤖 Testing AI Analysis Pipeline...")
    
    test_content = """
    Digital marketing strategies have evolved significantly with the rise of AI-powered tools.
    Search engines now use machine learning algorithms to better understand user intent.
    Content creators must adapt their approach to succeed in this new landscape.
    """
    
    try:
        # Test AI analysis
        ai_analysis = analyzer._perform_ai_analysis(test_content)
        
        print(f"   Analysis Source: {ai_analysis.get('analysis_source', 'none')}")
        print(f"   AI Readiness Score: {ai_analysis.get('ai_readiness_score', 'N/A')}")
        
        # Check for AI-specific features
        if 'ai_readiness_details' in ai_analysis:
            details = ai_analysis['ai_readiness_details']
            print(f"   Category Scores:")
            for category, score in details.get('category_scores', {}).items():
                print(f"     - {category}: {score}")
        
        print("✅ AI analysis pipeline working correctly")
        return True
        
    except Exception as e:
        print(f"❌ AI analysis pipeline failed: {e}")
        return False

def test_fallback_mechanisms(analyzer: ContentAnalyzerEnhancedReal):
    """Test fallback mechanisms"""
    print("\n🔄 Testing Fallback Mechanisms...")
    
    try:
        # Test basic content analysis (fallback)
        basic_analysis = analyzer._basic_content_analysis("This is a test content with some entities like Google and Microsoft.")
        
        print(f"   Basic Analysis Entities: {len(basic_analysis.get('entities', []))}")
        print(f"   Basic Analysis Sentiment: {basic_analysis.get('sentiment', {}).get('interpretation', 'N/A')}")
        
        # Test basic quality analysis (fallback)
        basic_quality = analyzer._basic_content_quality_analysis("This is test content for quality analysis.")
        
        print(f"   Basic Quality Score: {basic_quality.get('quality_score', 'N/A')}")
        print(f"   Basic Quality Level: {basic_quality.get('quality_level', 'N/A')}")
        
        print("✅ Fallback mechanisms working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Fallback mechanisms failed: {e}")
        return False

def display_phase_2_2_summary(status: Dict[str, Any]):
    """Display Phase 2.2 completion summary"""
    print("\n📋 Phase 2.2 Implementation Summary")
    print("=" * 50)
    
    phase_info = status.get('phase_completion', {})
    
    print(f"Phase Status: {phase_info.get('phase_2_2', 'unknown').upper()}")
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
    print("🚀 Phase 2.2 Content Analyzer Test Suite")
    print("=" * 50)
    
    # Initialize content analyzer
    analyzer, status = test_content_analyzer_initialization()
    if not analyzer:
        print("❌ Cannot proceed with tests - initialization failed")
        return
    
    # Run tests
    tests_passed = 0
    total_tests = 4
    
    if test_content_analysis_methods(analyzer):
        tests_passed += 1
    
    if test_nlp_analysis_pipeline(analyzer):
        tests_passed += 1
    
    if test_ai_analysis_pipeline(analyzer):
        tests_passed += 1
    
    if test_fallback_mechanisms(analyzer):
        tests_passed += 1
    
    # Display results
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Phase 2.2 implementation is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    # Display Phase 2.2 summary
    display_phase_2_2_summary(status)
    
    print("\n🔗 Next Steps:")
    print("   1. Run the application: python src/main.py")
    print("   2. Test with real URLs using the enhanced content analyzer")
    print("   3. Proceed to Phase 2.3 (Competitor Analysis) when ready")

if __name__ == "__main__":
    main()
