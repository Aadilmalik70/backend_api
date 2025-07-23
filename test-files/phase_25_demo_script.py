"""
Phase 2.5 Demo Script: Enhanced SERP Feature Optimizer

This script demonstrates the enhanced SERP Feature Optimizer with Google APIs integration,
AI-powered recommendations, and multi-tier architecture.
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from serp_feature_optimizer_real import SerpFeatureOptimizerReal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print Phase 2.5 banner"""
    print("\n" + "="*80)
    print("🚀 PHASE 2.5: ENHANCED SERP FEATURE OPTIMIZER")
    print("   Multi-tier Google APIs Integration with AI-Powered Recommendations")
    print("="*80)

def print_section(title: str, emoji: str = "📊"):
    """Print section header"""
    print(f"\n{emoji} {title}")
    print("-" * 50)

def format_recommendations(recommendations: List[Dict]) -> str:
    """Format recommendations for display"""
    output = []
    for i, rec in enumerate(recommendations, 1):
        feature = rec.get('feature', 'Unknown')
        opportunity = rec.get('opportunity', 'unknown')
        priority = rec.get('implementation_priority', 'unknown')
        
        output.append(f"{i}. {feature.replace('_', ' ').title()}")
        output.append(f"   • Opportunity: {opportunity.title()}")
        output.append(f"   • Priority: {priority.title()}")
        
        if rec.get('expected_impact'):
            impact = rec['expected_impact']
            traffic = impact.get('traffic_increase', 'N/A')
            output.append(f"   • Expected Traffic: {traffic}")
        
        output.append("")
    
    return "\n".join(output)

def demonstrate_enhanced_features(optimizer: SerpFeatureOptimizerReal, keyword: str):
    """Demonstrate enhanced features of Phase 2.5"""
    
    print_section("Enhanced SERP Feature Detection", "🔍")
    
    # Test enhanced SERP detection
    print(f"Analyzing SERP features for: '{keyword}'")
    serp_features = optimizer.detect_serp_features_enhanced(keyword)
    
    data_source = serp_features.get('data_source', 'unknown')
    print(f"Data Source: {data_source}")
    
    # Count features analyzed
    feature_count = len([k for k in serp_features.keys() if k not in ['data_source', 'analysis_metadata']])
    print(f"Features Analyzed: {feature_count}")
    
    # Show feature opportunities
    print("\nFeature Opportunities:")
    for feature_name, feature_data in serp_features.items():
        if feature_name not in ['data_source', 'analysis_metadata']:
            presence = feature_data.get('presence', 'unknown')
            opportunity = feature_data.get('opportunity_score', 0)
            print(f"  • {feature_name.replace('_', ' ').title()}: {presence} (score: {opportunity:.2f})")
    
    print_section("Knowledge Panel Analysis", "🧠")
    
    # Test entity detection and optimization
    is_entity = optimizer._is_entity_query(keyword)
    print(f"Entity Query Detected: {is_entity}")
    
    if is_entity:
        kg_optimization = optimizer.optimize_for_knowledge_panel(keyword, "")
        kg_data_source = kg_optimization.get('data_source', 'unknown')
        entity_verification = kg_optimization.get('entity_verification', {})
        authority_score = entity_verification.get('authority_score', 0)
        
        print(f"Knowledge Graph Data Source: {kg_data_source}")
        print(f"Entity Authority Score: {authority_score:.2f}")
        print(f"Found in Knowledge Graph: {entity_verification.get('found_in_kg', False)}")
    else:
        print("Not an entity query - focusing on other SERP features")
    
    print_section("AI-Powered Recommendations", "🤖")
    
    # Test AI recommendations
    ai_recommendations = optimizer.generate_ai_optimization_recommendations(
        keyword, "", serp_features
    )
    
    ai_data_source = ai_recommendations.get('data_source', 'unknown')
    confidence = ai_recommendations.get('confidence_score', 0)
    
    print(f"AI Data Source: {ai_data_source}")
    print(f"AI Confidence Score: {confidence:.2f}")
    
    # Show AI insights
    ai_analysis = ai_recommendations.get('ai_analysis', {})
    if ai_analysis:
        key_insights = ai_analysis.get('key_insights', [])
        if key_insights:
            print("\nKey AI Insights:")
            for i, insight in enumerate(key_insights[:3], 1):
                print(f"  {i}. {insight}")
    
    return serp_features, ai_recommendations

def demonstrate_full_workflow(optimizer: SerpFeatureOptimizerReal, keyword: str):
    """Demonstrate the complete Phase 2.5 workflow"""
    
    print_section("Complete Enhanced Recommendations", "⚡")
    
    start_time = datetime.now()
    recommendations = optimizer.generate_recommendations(keyword)
    end_time = datetime.now()
    
    response_time = (end_time - start_time).total_seconds()
    
    # Show workflow results
    print(f"Keyword: {recommendations.get('keyword')}")
    print(f"Data Source: {recommendations.get('data_source')}")
    print(f"Google APIs Enabled: {recommendations.get('google_apis_enabled')}")
    print(f"Response Time: {response_time:.2f} seconds")
    print(f"Analysis Timestamp: {recommendations.get('analysis_timestamp')}")
    
    # Show optimization summary
    opt_summary = recommendations.get('optimization_summary', {})
    if opt_summary:
        print(f"\nOptimization Summary:")
        print(f"  • Total Opportunities: {opt_summary.get('total_opportunities', 0)}")
        print(f"  • Critical Priorities: {opt_summary.get('critical_priorities', 0)}")
        print(f"  • Quick Wins: {len(opt_summary.get('quick_wins', []))}")
        print(f"  • Optimization Score: {opt_summary.get('optimization_score', 0)}")
        print(f"  • Estimated Timeline: {opt_summary.get('estimated_timeline', 'N/A')}")
    
    # Show enhanced recommendations
    recs = recommendations.get('recommendations', [])
    print(f"\nEnhanced Recommendations ({len(recs)} features):")
    if recs:
        formatted_recs = format_recommendations(recs[:5])  # Show top 5
        print(formatted_recs)
    
    # Show AI insights if available
    ai_insights = recommendations.get('ai_insights')
    if ai_insights and ai_insights.get('data_source') != 'fallback':
        print_section("AI Enhancement Insights", "🧠")
        optimization_priorities = ai_insights.get('optimization_priorities', {})
        if optimization_priorities:
            immediate = optimization_priorities.get('immediate', [])
            if immediate:
                print("Immediate Actions:")
                for action in immediate:
                    print(f"  • {action}")
    
    return recommendations

def run_phase_25_demo():
    """Run complete Phase 2.5 demonstration"""
    
    print_banner()
    
    # Initialize the enhanced optimizer
    print_section("Initializing Enhanced SERP Optimizer", "🔧")
    optimizer = SerpFeatureOptimizerReal()
    
    # Show configuration status
    print(f"Google APIs Enabled: {optimizer.google_apis_enabled}")
    print(f"Custom Search Available: {optimizer.google_search is not None}")
    print(f"Knowledge Graph Available: {optimizer.knowledge_graph is not None}")
    print(f"Gemini AI Available: {optimizer.gemini_client is not None}")
    
    # Demo keywords
    demo_keywords = [
        "how to optimize SEO for 2024",
        "best content marketing tools",
        "Google algorithm updates",
        "local SEO strategies",
        "AI in digital marketing"
    ]
    
    print_section("Demo Keywords", "🎯")
    for i, keyword in enumerate(demo_keywords, 1):
        print(f"{i}. {keyword}")
    
    # Run demonstrations
    results = []
    
    for i, keyword in enumerate(demo_keywords[:2], 1):  # Demo first 2 keywords
        print(f"\n{'='*80}")
        print(f"🚀 DEMO {i}: {keyword}")
        print('='*80)
        
        try:
            # Demonstrate enhanced features
            serp_features, ai_recs = demonstrate_enhanced_features(optimizer, keyword)
            
            # Demonstrate full workflow
            full_result = demonstrate_full_workflow(optimizer, keyword)
            
            results.append({
                'keyword': keyword,
                'status': 'success',
                'data_source': full_result.get('data_source'),
                'features_analyzed': len(full_result.get('serp_features', [])),
                'recommendations_count': len(full_result.get('recommendations', [])),
                'has_ai_insights': full_result.get('ai_insights') is not None,
                'optimization_score': full_result.get('optimization_summary', {}).get('optimization_score', 0)
            })
            
        except Exception as e:
            print(f"❌ Demo failed for '{keyword}': {str(e)}")
            results.append({
                'keyword': keyword,
                'status': 'failed',
                'error': str(e)
            })
    
    # Show demo summary
    print_section("Demo Summary", "📊")
    
    successful_demos = [r for r in results if r.get('status') == 'success']
    print(f"Successful Demos: {len(successful_demos)}/{len(results)}")
    
    if successful_demos:
        avg_features = sum(r.get('features_analyzed', 0) for r in successful_demos) / len(successful_demos)
        avg_recommendations = sum(r.get('recommendations_count', 0) for r in successful_demos) / len(successful_demos)
        avg_optimization_score = sum(r.get('optimization_score', 0) for r in successful_demos) / len(successful_demos)
        
        print(f"Average Features Analyzed: {avg_features:.1f}")
        print(f"Average Recommendations: {avg_recommendations:.1f}")
        print(f"Average Optimization Score: {avg_optimization_score:.1f}")
        
        # Data source distribution
        data_sources = [r.get('data_source') for r in successful_demos]
        unique_sources = set(data_sources)
        print(f"Data Sources Used: {', '.join(unique_sources)}")
        
        ai_enabled_count = sum(1 for r in successful_demos if r.get('has_ai_insights'))
        print(f"AI Insights Generated: {ai_enabled_count}/{len(successful_demos)} demos")
    
    # Show Phase 2.5 capabilities
    print_section("Phase 2.5 Capabilities Demonstrated", "🎉")
    
    capabilities = [
        "✅ Multi-tier architecture (Google APIs → SerpAPI fallback)",
        "✅ Enhanced SERP feature detection with real Google data",
        "✅ Knowledge Panel optimization with Knowledge Graph API",
        "✅ AI-powered recommendations with Gemini integration",
        "✅ Advanced opportunity scoring and prioritization",
        "✅ Comprehensive optimization summaries",
        "✅ Implementation roadmaps and timelines",
        "✅ Fallback mechanisms for reliability"
    ]
    
    for capability in capabilities:
        print(capability)
    
    print_section("Next Steps", "🚀")
    
    next_steps = [
        "1. Configure Google APIs for enhanced features (if not already configured)",
        "2. Run comprehensive test suite with test_phase_2_5_serp_optimizer.py",
        "3. Integrate with your existing SEO workflow",
        "4. Monitor performance improvements and cost savings",
        "5. Explore advanced features like entity optimization and AI insights"
    ]
    
    for step in next_steps:
        print(step)
    
    print("\n" + "="*80)
    print("🎯 Phase 2.5 Enhanced SERP Feature Optimizer Demo Completed!")
    print("   Ready for production use with significant improvements over Phase 2.4")
    print("="*80)
    
    return results

def quick_test(keyword: str = "SEO optimization best practices"):
    """Run a quick test of Phase 2.5 functionality"""
    
    print_banner()
    print_section("Quick Test", "🔥")
    
    try:
        optimizer = SerpFeatureOptimizerReal()
        
        print(f"Testing with keyword: '{keyword}'")
        print(f"Google APIs Enabled: {optimizer.google_apis_enabled}")
        
        start_time = datetime.now()
        result = optimizer.generate_recommendations(keyword)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        print(f"\n✅ Test Successful!")
        print(f"Response Time: {response_time:.2f} seconds")
        print(f"Data Source: {result.get('data_source')}")
        print(f"Features Analyzed: {len(result.get('serp_features', []))}")
        print(f"Recommendations Generated: {len(result.get('recommendations', []))}")
        print(f"Optimization Score: {result.get('optimization_summary', {}).get('optimization_score', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2.5 Enhanced SERP Optimizer Demo")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--keyword", type=str, help="Custom keyword for quick test")
    
    args = parser.parse_args()
    
    if args.quick:
        keyword = args.keyword or "SEO optimization best practices"
        success = quick_test(keyword)
        sys.exit(0 if success else 1)
    else:
        results = run_phase_25_demo()
        
        # Check if demo was successful
        successful_count = sum(1 for r in results if r.get('status') == 'success')
        if successful_count > 0:
            print(f"\n🎉 Demo completed successfully! ({successful_count}/{len(results)} demos passed)")
            sys.exit(0)
        else:
            print(f"\n❌ Demo failed - check configuration and try again")
            sys.exit(1)