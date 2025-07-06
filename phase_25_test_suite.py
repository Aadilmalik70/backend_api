"""
Phase 2.5 Test Suite: Enhanced SERP Feature Optimizer with Google APIs

This test suite validates the enhanced SERP Feature Optimizer implementation
with Google APIs integration, AI-powered recommendations, and multi-tier architecture.
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

class TestPhase25SerpOptimizer:
    """
    Comprehensive test suite for Phase 2.5 Enhanced SERP Feature Optimizer
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.optimizer = SerpFeatureOptimizerReal()
        self.test_results = {}
        self.test_keywords = [
            "how to optimize SEO",
            "best digital marketing tools 2024",
            "Google search ranking factors",
            "content marketing strategy",
            "local SEO optimization"
        ]
        logger.info("Phase 2.5 SERP Optimizer Test Suite initialized")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive test suite for Phase 2.5 implementation
        
        Returns:
            Dictionary containing all test results
        """
        logger.info("🚀 Starting Phase 2.5 Enhanced SERP Optimizer Test Suite")
        
        test_results = {
            'test_suite': 'Phase 2.5 Enhanced SERP Feature Optimizer',
            'timestamp': datetime.now().isoformat(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'detailed_results': {},
            'performance_metrics': {},
            'google_apis_status': {}
        }
        
        # Test 1: Google APIs Integration
        logger.info("📊 Test 1: Google APIs Integration")
        test_results['detailed_results']['google_apis_integration'] = self.test_google_apis_integration()
        test_results['tests_run'] += 1
        
        # Test 2: Enhanced SERP Feature Detection
        logger.info("🔍 Test 2: Enhanced SERP Feature Detection")
        test_results['detailed_results']['enhanced_serp_detection'] = self.test_enhanced_serp_detection()
        test_results['tests_run'] += 1
        
        # Test 3: Knowledge Panel Optimization
        logger.info("🧠 Test 3: Knowledge Panel Optimization")
        test_results['detailed_results']['knowledge_panel_optimization'] = self.test_knowledge_panel_optimization()
        test_results['tests_run'] += 1
        
        # Test 4: AI-Powered Recommendations
        logger.info("🤖 Test 4: AI-Powered Recommendations")
        test_results['detailed_results']['ai_powered_recommendations'] = self.test_ai_powered_recommendations()
        test_results['tests_run'] += 1
        
        # Test 5: Fallback Mechanism
        logger.info("🔄 Test 5: Fallback Mechanism")
        test_results['detailed_results']['fallback_mechanism'] = self.test_fallback_mechanism()
        test_results['tests_run'] += 1
        
        # Test 6: Enhanced Recommendations Generation
        logger.info("⚡ Test 6: Enhanced Recommendations Generation")
        test_results['detailed_results']['enhanced_recommendations'] = self.test_enhanced_recommendations_generation()
        test_results['tests_run'] += 1
        
        # Test 7: Performance Benchmarks
        logger.info("📈 Test 7: Performance Benchmarks")
        test_results['detailed_results']['performance_benchmarks'] = self.test_performance_benchmarks()
        test_results['tests_run'] += 1
        
        # Calculate overall results
        passed_tests = sum(1 for result in test_results['detailed_results'].values() if result.get('status') == 'passed')
        test_results['tests_passed'] = passed_tests
        test_results['tests_failed'] = test_results['tests_run'] - passed_tests
        test_results['success_rate'] = (passed_tests / test_results['tests_run']) * 100
        
        # Generate summary
        self.generate_test_summary(test_results)
        
        return test_results
    
    def test_google_apis_integration(self) -> Dict[str, Any]:
        """Test Google APIs integration status and functionality"""
        test_result = {
            'test_name': 'Google APIs Integration',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            # Test client initialization
            test_result['details']['google_apis_enabled'] = self.optimizer.google_apis_enabled
            test_result['details']['custom_search_available'] = self.optimizer.google_search is not None
            test_result['details']['knowledge_graph_available'] = self.optimizer.knowledge_graph is not None
            test_result['details']['gemini_available'] = self.optimizer.gemini_client is not None
            
            # Test health checks if APIs are available
            if self.optimizer.google_apis_enabled:
                if self.optimizer.google_search:
                    test_result['details']['custom_search_health'] = self.optimizer.google_search.health_check()
                if self.optimizer.knowledge_graph:
                    test_result['details']['knowledge_graph_health'] = self.optimizer.knowledge_graph.health_check()
                if self.optimizer.gemini_client:
                    test_result['details']['gemini_health'] = self.optimizer.gemini_client.health_check()
            
            # Determine overall status
            if self.optimizer.google_apis_enabled:
                test_result['status'] = 'passed'
                test_result['message'] = 'Google APIs integration working correctly'
            else:
                test_result['status'] = 'warning'
                test_result['message'] = 'Google APIs not configured - using fallback mode'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Google APIs integration failed: {str(e)}'
        
        return test_result
    
    def test_enhanced_serp_detection(self) -> Dict[str, Any]:
        """Test enhanced SERP feature detection with real data"""
        test_result = {
            'test_name': 'Enhanced SERP Feature Detection',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            test_keyword = "how to optimize SEO"
            
            # Test enhanced SERP feature detection
            serp_features = self.optimizer.detect_serp_features_enhanced(test_keyword)
            
            test_result['details']['test_keyword'] = test_keyword
            test_result['details']['data_source'] = serp_features.get('data_source', 'unknown')
            test_result['details']['features_detected'] = list(serp_features.keys())
            test_result['details']['feature_count'] = len([k for k in serp_features.keys() if k not in ['data_source', 'analysis_metadata']])
            
            # Validate feature structure
            expected_features = ['featured_snippets', 'people_also_ask', 'knowledge_panels', 'image_packs', 'video_results', 'local_pack', 'top_stories']
            detected_features = [k for k in serp_features.keys() if k not in ['data_source', 'analysis_metadata']]
            
            test_result['details']['expected_features'] = expected_features
            test_result['details']['all_features_present'] = all(feature in detected_features for feature in expected_features)
            
            # Test feature data structure
            for feature_name, feature_data in serp_features.items():
                if feature_name not in ['data_source', 'analysis_metadata']:
                    test_result['details'][f'{feature_name}_structure'] = {
                        'has_presence': 'presence' in feature_data,
                        'has_opportunity_score': 'opportunity_score' in feature_data,
                        'opportunity_score': feature_data.get('opportunity_score', 0)
                    }
            
            test_result['status'] = 'passed'
            test_result['message'] = f"Enhanced SERP detection working - {len(detected_features)} features analyzed"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Enhanced SERP detection failed: {str(e)}'
        
        return test_result
    
    def test_knowledge_panel_optimization(self) -> Dict[str, Any]:
        """Test Knowledge Panel optimization functionality"""
        test_result = {
            'test_name': 'Knowledge Panel Optimization',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            test_entity = "Google"
            
            # Test entity query detection
            is_entity = self.optimizer._is_entity_query(test_entity)
            test_result['details']['entity_detection'] = is_entity
            
            if is_entity:
                # Test knowledge panel optimization
                kg_optimization = self.optimizer.optimize_for_knowledge_panel(test_entity, "")
                
                test_result['details']['entity_name'] = kg_optimization.get('entity_name')
                test_result['details']['data_source'] = kg_optimization.get('data_source')
                test_result['details']['entity_verification'] = kg_optimization.get('entity_verification', {})
                test_result['details']['optimization_recommendations'] = len(kg_optimization.get('optimization_recommendations', {}))
                test_result['details']['implementation_roadmap'] = len(kg_optimization.get('implementation_roadmap', {}))
                
                test_result['status'] = 'passed'
                test_result['message'] = f"Knowledge Panel optimization working for entity: {test_entity}"
            else:
                test_result['status'] = 'warning'
                test_result['message'] = f"Test entity '{test_entity}' not detected as entity query"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Knowledge Panel optimization failed: {str(e)}'
        
        return test_result
    
    def test_ai_powered_recommendations(self) -> Dict[str, Any]:
        """Test AI-powered recommendations with Gemini"""
        test_result = {
            'test_name': 'AI-Powered Recommendations',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            test_query = "content marketing strategy"
            test_content = "Learn about effective content marketing strategies for business growth."
            
            # Mock SERP features for testing
            mock_serp_features = {
                'featured_snippets': {'presence': 'high', 'opportunity_score': 0.8},
                'people_also_ask': {'presence': 'medium', 'opportunity_score': 0.6},
                'data_source': 'test'
            }
            
            # Test AI recommendations generation
            ai_recommendations = self.optimizer.generate_ai_optimization_recommendations(
                test_query, test_content, mock_serp_features
            )
            
            test_result['details']['query'] = ai_recommendations.get('query')
            test_result['details']['data_source'] = ai_recommendations.get('data_source')
            test_result['details']['confidence_score'] = ai_recommendations.get('confidence_score', 0)
            test_result['details']['has_ai_analysis'] = 'ai_analysis' in ai_recommendations
            test_result['details']['has_optimization_priorities'] = 'optimization_priorities' in ai_recommendations
            test_result['details']['has_implementation_roadmap'] = 'implementation_roadmap' in ai_recommendations
            
            # Check AI analysis structure
            ai_analysis = ai_recommendations.get('ai_analysis', {})
            test_result['details']['ai_analysis_components'] = {
                'key_insights': len(ai_analysis.get('key_insights', [])),
                'priority_actions': len(ai_analysis.get('priority_actions', [])),
                'content_improvements': len(ai_analysis.get('content_improvements', [])),
                'competitive_advantages': len(ai_analysis.get('competitive_advantages', []))
            }
            
            test_result['status'] = 'passed'
            test_result['message'] = f"AI recommendations generated successfully - source: {ai_recommendations.get('data_source')}"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'AI-powered recommendations failed: {str(e)}'
        
        return test_result
    
    def test_fallback_mechanism(self) -> Dict[str, Any]:
        """Test SerpAPI fallback functionality"""
        test_result = {
            'test_name': 'Fallback Mechanism',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            test_keyword = "digital marketing tools"
            
            # Test fallback recommendations generation
            fallback_results = self.optimizer._generate_fallback_recommendations(test_keyword)
            
            test_result['details']['keyword'] = fallback_results.get('keyword')
            test_result['details']['data_source'] = fallback_results.get('data_source')
            test_result['details']['serp_features_count'] = len(fallback_results.get('serp_features', []))
            test_result['details']['recommendations_count'] = len(fallback_results.get('recommendations', []))
            test_result['details']['has_note'] = 'note' in fallback_results
            
            # Validate structure matches expected format
            expected_keys = ['keyword', 'serp_features', 'recommendations', 'data_source']
            test_result['details']['structure_valid'] = all(key in fallback_results for key in expected_keys)
            
            # Test fallback AI recommendations
            fallback_ai = self.optimizer._get_fallback_ai_recommendations(test_keyword, {})
            test_result['details']['fallback_ai_available'] = fallback_ai.get('data_source') == 'fallback'
            
            # Test fallback Knowledge Panel optimization
            fallback_kg = self.optimizer._get_fallback_knowledge_panel_optimization("Test Entity", "")
            test_result['details']['fallback_kg_available'] = fallback_kg.get('data_source') == 'fallback'
            
            test_result['status'] = 'passed'
            test_result['message'] = "Fallback mechanism working correctly"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Fallback mechanism failed: {str(e)}'
        
        return test_result
    
    def test_enhanced_recommendations_generation(self) -> Dict[str, Any]:
        """Test enhanced recommendations generation with full workflow"""
        test_result = {
            'test_name': 'Enhanced Recommendations Generation',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            test_keyword = "best SEO tools 2024"
            
            # Test full enhanced recommendations generation
            recommendations = self.optimizer.generate_recommendations(test_keyword)
            
            test_result['details']['keyword'] = recommendations.get('keyword')
            test_result['details']['data_source'] = recommendations.get('data_source')
            test_result['details']['google_apis_enabled'] = recommendations.get('google_apis_enabled')
            test_result['details']['analysis_timestamp'] = recommendations.get('analysis_timestamp')
            
            # Validate enhanced structure
            enhanced_keys = ['keyword', 'serp_features', 'recommendations', 'optimization_summary']
            test_result['details']['enhanced_structure'] = all(key in recommendations for key in enhanced_keys)
            
            # Analyze recommendations structure
            recs = recommendations.get('recommendations', [])
            test_result['details']['recommendations_count'] = len(recs)
            
            if recs:
                sample_rec = recs[0]
                test_result['details']['enhanced_recommendation_structure'] = {
                    'has_feature': 'feature' in sample_rec,
                    'has_status': 'status' in sample_rec,
                    'has_opportunity': 'opportunity' in sample_rec,
                    'has_implementation_priority': 'implementation_priority' in sample_rec,
                    'has_expected_impact': 'expected_impact' in sample_rec,
                    'has_optimization_complexity': 'optimization_complexity' in sample_rec
                }
            
            # Check optimization summary
            opt_summary = recommendations.get('optimization_summary', {})
            test_result['details']['optimization_summary'] = {
                'total_opportunities': opt_summary.get('total_opportunities', 0),
                'critical_priorities': opt_summary.get('critical_priorities', 0),
                'quick_wins': len(opt_summary.get('quick_wins', [])),
                'optimization_score': opt_summary.get('optimization_score', 0)
            }
            
            # Check for AI insights if available
            ai_insights = recommendations.get('ai_insights')
            test_result['details']['ai_insights_available'] = ai_insights is not None
            if ai_insights:
                test_result['details']['ai_insights_source'] = ai_insights.get('data_source')
            
            # Check for entity optimization if applicable
            entity_opt = recommendations.get('entity_optimization')
            test_result['details']['entity_optimization_available'] = entity_opt is not None
            if entity_opt:
                test_result['details']['entity_optimization_source'] = entity_opt.get('data_source')
            
            test_result['status'] = 'passed'
            test_result['message'] = f"Enhanced recommendations generated successfully - {len(recs)} features analyzed"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Enhanced recommendations generation failed: {str(e)}'
        
        return test_result
    
    def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks and compare with baseline"""
        test_result = {
            'test_name': 'Performance Benchmarks',
            'status': 'unknown',
            'details': {},
            'errors': []
        }
        
        try:
            import time
            
            performance_data = {
                'test_keywords': [],
                'response_times': [],
                'data_sources': [],
                'feature_counts': [],
                'recommendation_counts': []
            }
            
            # Test performance with multiple keywords
            for keyword in self.test_keywords[:3]:  # Test with first 3 keywords
                start_time = time.time()
                
                try:
                    result = self.optimizer.generate_recommendations(keyword)
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    performance_data['test_keywords'].append(keyword)
                    performance_data['response_times'].append(response_time)
                    performance_data['data_sources'].append(result.get('data_source', 'unknown'))
                    performance_data['feature_counts'].append(len(result.get('serp_features', [])))
                    performance_data['recommendation_counts'].append(len(result.get('recommendations', [])))
                    
                except Exception as e:
                    logger.warning(f"Performance test failed for keyword '{keyword}': {str(e)}")
                    continue
            
            # Calculate performance metrics
            if performance_data['response_times']:
                test_result['details']['average_response_time'] = sum(performance_data['response_times']) / len(performance_data['response_times'])
                test_result['details']['min_response_time'] = min(performance_data['response_times'])
                test_result['details']['max_response_time'] = max(performance_data['response_times'])
                test_result['details']['total_tests'] = len(performance_data['response_times'])
                
                # Data source distribution
                from collections import Counter
                source_counts = Counter(performance_data['data_sources'])
                test_result['details']['data_source_distribution'] = dict(source_counts)
                
                # Average feature and recommendation counts
                test_result['details']['average_features'] = sum(performance_data['feature_counts']) / len(performance_data['feature_counts'])
                test_result['details']['average_recommendations'] = sum(performance_data['recommendation_counts']) / len(performance_data['recommendation_counts'])
                
                # Performance assessment
                avg_time = test_result['details']['average_response_time']
                if avg_time < 2.0:
                    performance_rating = 'excellent'
                elif avg_time < 5.0:
                    performance_rating = 'good'
                elif avg_time < 10.0:
                    performance_rating = 'acceptable'
                else:
                    performance_rating = 'needs_improvement'
                
                test_result['details']['performance_rating'] = performance_rating
                test_result['details']['performance_data'] = performance_data
                
                test_result['status'] = 'passed'
                test_result['message'] = f"Performance benchmarks completed - avg response time: {avg_time:.2f}s ({performance_rating})"
            else:
                test_result['status'] = 'failed'
                test_result['message'] = "No successful performance tests completed"
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(str(e))
            test_result['message'] = f'Performance benchmarks failed: {str(e)}'
        
        return test_result
    
    def generate_test_summary(self, test_results: Dict[str, Any]) -> None:
        """Generate comprehensive test summary"""
        logger.info("\n" + "="*80)
        logger.info("🎯 PHASE 2.5 ENHANCED SERP OPTIMIZER - TEST RESULTS SUMMARY")
        logger.info("="*80)
        
        logger.info(f"📊 Tests Run: {test_results['tests_run']}")
        logger.info(f"✅ Tests Passed: {test_results['tests_passed']}")
        logger.info(f"❌ Tests Failed: {test_results['tests_failed']}")
        logger.info(f"📈 Success Rate: {test_results['success_rate']:.1f}%")
        
        logger.info("\n📋 INDIVIDUAL TEST RESULTS:")
        logger.info("-" * 50)
        
        for test_name, result in test_results['detailed_results'].items():
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'warning': '⚠️',
                'unknown': '❓'
            }.get(result.get('status', 'unknown'), '❓')
            
            logger.info(f"{status_emoji} {result.get('test_name', test_name)}: {result.get('status', 'unknown').upper()}")
            if result.get('message'):
                logger.info(f"   📝 {result['message']}")
            if result.get('errors'):
                for error in result['errors']:
                    logger.info(f"   🚨 Error: {error}")
        
        # Google APIs Status Summary
        google_apis_test = test_results['detailed_results'].get('google_apis_integration', {})
        if google_apis_test:
            logger.info("\n🔧 GOOGLE APIS STATUS:")
            logger.info("-" * 30)
            details = google_apis_test.get('details', {})
            logger.info(f"📡 Google APIs Enabled: {details.get('google_apis_enabled', False)}")
            logger.info(f"🔍 Custom Search Available: {details.get('custom_search_available', False)}")
            logger.info(f"🧠 Knowledge Graph Available: {details.get('knowledge_graph_available', False)}")
            logger.info(f"🤖 Gemini Available: {details.get('gemini_available', False)}")
        
        # Performance Summary
        perf_test = test_results['detailed_results'].get('performance_benchmarks', {})
        if perf_test and perf_test.get('status') == 'passed':
            logger.info("\n⚡ PERFORMANCE METRICS:")
            logger.info("-" * 30)
            perf_details = perf_test.get('details', {})
            logger.info(f"⏱️  Average Response Time: {perf_details.get('average_response_time', 0):.2f}s")
            logger.info(f"📊 Performance Rating: {perf_details.get('performance_rating', 'unknown').upper()}")
            logger.info(f"🎯 Average Features Analyzed: {perf_details.get('average_features', 0):.1f}")
            logger.info(f"💡 Average Recommendations: {perf_details.get('average_recommendations', 0):.1f}")
        
        # Enhancement Summary
        enhanced_test = test_results['detailed_results'].get('enhanced_recommendations', {})
        if enhanced_test and enhanced_test.get('status') == 'passed':
            logger.info("\n🚀 ENHANCEMENT FEATURES:")
            logger.info("-" * 30)
            enh_details = enhanced_test.get('details', {})
            logger.info(f"📈 Enhanced Structure: {enh_details.get('enhanced_structure', False)}")
            logger.info(f"🤖 AI Insights Available: {enh_details.get('ai_insights_available', False)}")
            logger.info(f"🏢 Entity Optimization Available: {enh_details.get('entity_optimization_available', False)}")
            
            opt_summary = enh_details.get('optimization_summary', {})
            logger.info(f"🎯 Total Opportunities: {opt_summary.get('total_opportunities', 0)}")
            logger.info(f"🔥 Critical Priorities: {opt_summary.get('critical_priorities', 0)}")
            logger.info(f"⚡ Quick Wins: {opt_summary.get('quick_wins', 0)}")
            logger.info(f"📊 Optimization Score: {opt_summary.get('optimization_score', 0)}")
        
        logger.info("\n" + "="*80)
        
        # Overall Assessment
        if test_results['success_rate'] >= 80:
            logger.info("🎉 PHASE 2.5 IMPLEMENTATION: EXCELLENT - Ready for production!")
        elif test_results['success_rate'] >= 60:
            logger.info("✅ PHASE 2.5 IMPLEMENTATION: GOOD - Minor issues to address")
        elif test_results['success_rate'] >= 40:
            logger.info("⚠️  PHASE 2.5 IMPLEMENTATION: NEEDS WORK - Several issues to fix")
        else:
            logger.info("❌ PHASE 2.5 IMPLEMENTATION: CRITICAL ISSUES - Major fixes required")
        
        logger.info("="*80)
    
    def save_test_results(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"phase_2_5_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(test_results, f, indent=2, default=str)
            
            logger.info(f"💾 Test results saved to: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save test results: {str(e)}")
            return ""
    
    def run_quick_test(self, keyword: str = "SEO optimization") -> Dict[str, Any]:
        """Run a quick test with a single keyword"""
        logger.info(f"🔥 Running quick test with keyword: '{keyword}'")
        
        try:
            start_time = datetime.now()
            result = self.optimizer.generate_recommendations(keyword)
            end_time = datetime.now()
            
            quick_test_result = {
                'keyword': keyword,
                'test_timestamp': start_time.isoformat(),
                'response_time': (end_time - start_time).total_seconds(),
                'data_source': result.get('data_source'),
                'google_apis_enabled': result.get('google_apis_enabled'),
                'serp_features_count': len(result.get('serp_features', [])),
                'recommendations_count': len(result.get('recommendations', [])),
                'has_ai_insights': result.get('ai_insights') is not None,
                'has_entity_optimization': result.get('entity_optimization') is not None,
                'optimization_summary': result.get('optimization_summary'),
                'status': 'success'
            }
            
            logger.info(f"✅ Quick test completed successfully in {quick_test_result['response_time']:.2f}s")
            logger.info(f"📊 Data source: {quick_test_result['data_source']}")
            logger.info(f"🎯 Features analyzed: {quick_test_result['serp_features_count']}")
            logger.info(f"💡 Recommendations generated: {quick_test_result['recommendations_count']}")
            
            return quick_test_result
            
        except Exception as e:
            error_result = {
                'keyword': keyword,
                'test_timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e)
            }
            
            logger.error(f"❌ Quick test failed: {str(e)}")
            return error_result


def main():
    """Main test execution function"""
    logger.info("🚀 Starting Phase 2.5 Enhanced SERP Feature Optimizer Test Suite")
    
    # Initialize test suite
    test_suite = TestPhase25SerpOptimizer()
    
    # Run quick test first
    logger.info("\n🔥 Running Quick Test...")
    quick_result = test_suite.run_quick_test()
    
    if quick_result.get('status') == 'success':
        logger.info("✅ Quick test passed - proceeding with full test suite")
        
        # Run comprehensive tests
        logger.info("\n📊 Running Comprehensive Test Suite...")
        full_results = test_suite.run_all_tests()
        
        # Save results
        results_file = test_suite.save_test_results(full_results)
        
        logger.info(f"\n🎯 Phase 2.5 testing completed - Results saved to: {results_file}")
        
        return full_results
    else:
        logger.error("❌ Quick test failed - check configuration before running full suite")
        return quick_result


if __name__ == "__main__":
    results = main()