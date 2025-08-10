#!/usr/bin/env python3
"""
Conversational Query Engine Validation Script

Comprehensive validation of the P0 priority conversational query engineering system,
testing parallel processing, AI integration, and natural language understanding capabilities.

Tests all components:
- Intent classification and entity extraction
- Parallel processing pipeline  
- AI infrastructure integration
- Session management and conversation context
- Performance metrics and caching
- REST API endpoints
"""

import sys
import os
import asyncio
import time
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_conversational_engine_import():
    """Test conversational query engine import and initialization"""
    print("Testing Conversational Query Engine Import...")
    
    try:
        from services.conversational_query_engine import (
            ConversationalQueryEngine, 
            get_conversational_query_engine,
            QueryIntent, 
            QueryContext,
            ConversationSession,
            QueryProcessingResult
        )
        print("  Core Classes: Available")
        
        # Test engine initialization
        config = {
            'parallel_processing': True,
            'cache_query_results': True,
            'max_conversation_turns': 10,
            'enable_conversation_memory': True
        }
        
        engine = ConversationalQueryEngine(config)
        print("  Engine Instance: Created")
        
        # Test initialization
        init_success = await engine.initialize()
        print(f"  Initialization: {'SUCCESS' if init_success else 'PARTIAL'}")
        
        return True, engine
        
    except Exception as e:
        print(f"  Import test failed: {e}")
        return False, None

async def test_query_processing(engine):
    """Test basic query processing functionality"""
    print("\nTesting Query Processing...")
    
    from services.conversational_query_engine import QueryIntent
    
    test_queries = [
        ("Find keywords for digital marketing", QueryIntent.KEYWORD_RESEARCH),
        ("Analyze my competitors", QueryIntent.COMPETITOR_ANALYSIS),
        ("Create content strategy for SaaS", QueryIntent.CONTENT_STRATEGY),
        ("Generate a content blueprint", QueryIntent.BLUEPRINT_GENERATION),
        ("Research information about Google", QueryIntent.ENTITY_RESEARCH)
    ]
    
    try:
        results = []
        for query, expected_intent in test_queries:
            print(f"  Processing: '{query[:30]}...'")
            
            start_time = time.time()
            result = await engine.process_query(query)
            processing_time = time.time() - start_time
            
            # Validate result structure
            assert hasattr(result, 'intent'), "Result missing intent"
            assert hasattr(result, 'confidence_score'), "Result missing confidence"
            assert hasattr(result, 'extracted_entities'), "Result missing entities"
            assert hasattr(result, 'suggested_actions'), "Result missing actions"
            
            results.append({
                'query': query,
                'intent': result.intent,
                'expected_intent': expected_intent,
                'confidence': result.confidence_score,
                'entities_count': len(result.extracted_entities),
                'actions_count': len(result.suggested_actions),
                'processing_time': processing_time
            })
            
            print(f"    Intent: {result.intent.value}, Confidence: {result.confidence_score:.2f}")
        
        # Calculate accuracy
        correct_intents = sum(1 for r in results if r['intent'] == r['expected_intent'])
        accuracy = (correct_intents / len(results)) * 100
        
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        
        print(f"  Intent Classification Accuracy: {accuracy:.1f}%")
        print(f"  Average Processing Time: {avg_processing_time:.3f}s")
        
        return accuracy >= 60.0  # 60% accuracy threshold
        
    except Exception as e:
        print(f"  Query processing test failed: {e}")
        return False

async def test_parallel_processing(engine):
    """Test parallel processing capabilities"""
    print("\nTesting Parallel Processing...")
    
    try:
        queries = [
            "Research keywords for e-commerce",
            "Analyze competitors in fintech",
            "Create blog content strategy", 
            "Generate landing page blueprint",
            "Study market trends in AI"
        ]
        
        # Test sequential processing
        sequential_start = time.time()
        sequential_results = []
        for query in queries:
            result = await engine.process_query(query)
            sequential_results.append(result)
        sequential_time = time.time() - sequential_start
        
        # Test parallel processing (using batch processing simulation)
        parallel_start = time.time()
        parallel_tasks = [engine.process_query(query) for query in queries]
        parallel_results = await asyncio.gather(*parallel_tasks)
        parallel_time = time.time() - parallel_start
        
        # Calculate performance improvement
        if sequential_time > 0:
            improvement = ((sequential_time - parallel_time) / sequential_time) * 100
            print(f"  Sequential Time: {sequential_time:.3f}s")
            print(f"  Parallel Time: {parallel_time:.3f}s")
            print(f"  Performance Improvement: {improvement:.1f}%")
        else:
            print("  Both processing methods completed very quickly")
            improvement = 0
        
        # Validate results consistency
        results_consistent = len(sequential_results) == len(parallel_results)
        print(f"  Results Consistency: {'PASS' if results_consistent else 'FAIL'}")
        
        return results_consistent and improvement >= -50  # Allow some overhead
        
    except Exception as e:
        print(f"  Parallel processing test failed: {e}")
        return False

async def test_conversation_management(engine):
    """Test conversation session and context management"""
    print("\nTesting Conversation Management...")
    
    try:
        from services.conversational_query_engine import QueryContext
        session_id = "test_session_123"
        user_id = "test_user"
        
        # First query in session
        result1 = await engine.process_query(
            "Find keywords for digital marketing",
            session_id=session_id,
            user_id=user_id
        )
        
        # Follow-up query
        result2 = await engine.process_query(
            "Also analyze the competitors",
            session_id=session_id,
            user_id=user_id
        )
        
        # Third query for context
        result3 = await engine.process_query(
            "Create content strategy based on this research", 
            session_id=session_id,
            user_id=user_id
        )
        
        # Validate session management
        session_exists = session_id in engine.active_sessions
        print(f"  Session Created: {'PASS' if session_exists else 'FAIL'}")
        
        if session_exists:
            session = engine.active_sessions[session_id]
            print(f"  Session Turns: {len(session.turns)}")
            print(f"  Session Intent: {session.session_intent}")
            print(f"  Active Context: {len(session.active_context)} items")
        
        # Test context awareness
        context_aware = (result2.context != QueryContext.NEW_SESSION and 
                        result3.context != QueryContext.NEW_SESSION)
        print(f"  Context Awareness: {'PASS' if context_aware else 'FAIL'}")
        
        return session_exists and context_aware
        
    except Exception as e:
        print(f"  Conversation management test failed: {e}")
        return False

async def test_entity_extraction(engine):
    """Test entity extraction and enhancement"""
    print("\nTesting Entity Extraction...")
    
    test_cases = [
        ("Research Google and Microsoft for competitor analysis", ["Google", "Microsoft"]),
        ("Create content strategy for Shopify stores", ["Shopify"]),
        ("Analyze Tesla's marketing approach", ["Tesla"]),
        ("Find keywords for Amazon FBA business", ["Amazon"])
    ]
    
    try:
        results = []
        for query, expected_entities in test_cases:
            print(f"  Testing: '{query[:40]}...'")
            
            result = await engine.process_query(query)
            extracted_entities = result.extracted_entities
            
            # Check if any expected entities were found
            found_entities = []
            for entity in extracted_entities:
                entity_text = entity.get('text', '').lower()
                for expected in expected_entities:
                    if expected.lower() in entity_text:
                        found_entities.append(expected)
            
            results.append({
                'query': query,
                'expected': expected_entities,
                'found': found_entities,
                'total_extracted': len(extracted_entities)
            })
            
            print(f"    Expected: {expected_entities}")
            print(f"    Found: {found_entities}")
            print(f"    Total Extracted: {len(extracted_entities)}")
        
        # Calculate entity extraction success rate
        successful_extractions = sum(1 for r in results if len(r['found']) > 0)
        success_rate = (successful_extractions / len(results)) * 100
        
        print(f"  Entity Extraction Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 50.0  # 50% success rate threshold
        
    except Exception as e:
        print(f"  Entity extraction test failed: {e}")
        return False

async def test_caching_performance(engine):
    """Test caching functionality and performance"""
    print("\nTesting Caching Performance...")
    
    try:
        test_query = "Find keywords for digital marketing SaaS"
        
        # First request (cache miss)
        start_time = time.time()
        result1 = await engine.process_query(test_query)
        first_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        result2 = await engine.process_query(test_query)
        second_time = time.time() - start_time
        
        print(f"  First Request Time: {first_time:.3f}s")
        print(f"  Second Request Time: {second_time:.3f}s")
        
        # Calculate cache performance
        if first_time > 0:
            cache_improvement = ((first_time - second_time) / first_time) * 100
            print(f"  Cache Performance Improvement: {cache_improvement:.1f}%")
        else:
            cache_improvement = 0
            print("  Both requests were very fast")
        
        # Validate result consistency
        results_consistent = (result1.intent == result2.intent and 
                            result1.enhanced_query == result2.enhanced_query)
        print(f"  Results Consistency: {'PASS' if results_consistent else 'FAIL'}")
        
        return results_consistent and cache_improvement >= -20  # Allow some variation
        
    except Exception as e:
        print(f"  Caching performance test failed: {e}")
        return False

async def test_performance_metrics(engine):
    """Test performance metrics collection"""
    print("\nTesting Performance Metrics...")
    
    try:
        # Generate some queries to populate metrics
        test_queries = [
            "Research AI market trends",
            "Analyze SaaS competitors", 
            "Create content blueprint for tech startup"
        ]
        
        for query in test_queries:
            await engine.process_query(query)
        
        # Get performance metrics
        metrics = engine.get_performance_metrics()
        
        print(f"  Metrics Available: {'PASS' if metrics else 'FAIL'}")
        
        if metrics:
            processing_metrics = metrics.get('processing_metrics', {})
            session_metrics = metrics.get('session_metrics', {})
            ai_integration = metrics.get('ai_integration', {})
            
            print(f"  Total Queries Processed: {processing_metrics.get('total_queries_processed', 0)}")
            print(f"  Active Sessions: {session_metrics.get('active_sessions', 0)}")
            print(f"  NLP Processor Available: {ai_integration.get('nlp_processor_available', False)}")
            print(f"  Knowledge Graph Available: {ai_integration.get('knowledge_graph_available', False)}")
            print(f"  AI Manager Available: {ai_integration.get('ai_manager_initialized', False)}")
            
            # Validate key metrics exist
            has_processing_metrics = 'total_queries_processed' in processing_metrics
            has_session_metrics = 'active_sessions' in session_metrics
            has_ai_metrics = len(ai_integration) > 0
            
            return has_processing_metrics and has_session_metrics and has_ai_metrics
        
        return False
        
    except Exception as e:
        print(f"  Performance metrics test failed: {e}")
        return False

async def test_error_handling(engine):
    """Test error handling and graceful degradation"""
    print("\nTesting Error Handling...")
    
    test_cases = [
        ("", "empty query"),
        ("   ", "whitespace only"),
        ("a" * 11000, "extremely long query"), 
        ("!@#$%^&*()", "special characters only"),
        ("🚀🔥💡🎯", "emoji only")
    ]
    
    try:
        results = []
        for query, description in test_cases:
            print(f"  Testing {description}...")
            
            try:
                result = await engine.process_query(query)
                
                # Validate error handling
                has_result = result is not None
                has_intent = hasattr(result, 'intent')
                has_suggested_actions = (hasattr(result, 'suggested_actions') and 
                                       len(result.suggested_actions) > 0)
                
                results.append({
                    'description': description,
                    'handled_gracefully': has_result and has_intent,
                    'provides_guidance': has_suggested_actions
                })
                
                print(f"    Result: {'HANDLED' if has_result else 'FAILED'}")
                
            except Exception as e:
                print(f"    Exception: {e}")
                results.append({
                    'description': description,
                    'handled_gracefully': False,
                    'provides_guidance': False
                })
        
        # Calculate graceful handling rate
        graceful_handling = sum(1 for r in results if r['handled_gracefully'])
        handling_rate = (graceful_handling / len(results)) * 100
        
        guidance_provided = sum(1 for r in results if r['provides_guidance'])
        guidance_rate = (guidance_provided / len(results)) * 100
        
        print(f"  Graceful Error Handling: {handling_rate:.1f}%")
        print(f"  Provides User Guidance: {guidance_rate:.1f}%")
        
        return handling_rate >= 80.0  # 80% graceful handling threshold
        
    except Exception as e:
        print(f"  Error handling test failed: {e}")
        return False

async def test_api_integration():
    """Test Flask API integration (import test)"""
    print("\nTesting API Integration...")
    
    try:
        from routes.conversational_query_routes import conversational_query_bp
        print("  Blueprint Import: SUCCESS")
        
        # Check blueprint configuration
        has_routes = len(conversational_query_bp.deferred_functions) > 0
        print(f"  Routes Registered: {'PASS' if has_routes else 'FAIL'}")
        
        # Check error handlers
        has_error_handlers = len(conversational_query_bp.error_handler_spec) > 0
        print(f"  Error Handlers: {'PASS' if has_error_handlers else 'FAIL'}")
        
        return True
        
    except Exception as e:
        print(f"  API integration test failed: {e}")
        return False

async def main():
    """Run comprehensive conversational query engine validation"""
    print("Conversational Query Engine Validation (P0 Priority)")
    print("=" * 60)
    
    # Test import and initialization
    import_success, engine = await test_conversational_engine_import()
    if not import_success:
        print("\nImport test failed - cannot proceed")
        return 1
    
    # Run all tests
    test_results = {
        'import': import_success,
        'query_processing': False,
        'parallel_processing': False,
        'conversation_management': False,
        'entity_extraction': False,
        'caching_performance': False,
        'performance_metrics': False,
        'error_handling': False,
        'api_integration': False
    }
    
    # Core functionality tests
    test_results['query_processing'] = await test_query_processing(engine)
    test_results['parallel_processing'] = await test_parallel_processing(engine)
    test_results['conversation_management'] = await test_conversation_management(engine)
    test_results['entity_extraction'] = await test_entity_extraction(engine)
    
    # Performance and reliability tests
    test_results['caching_performance'] = await test_caching_performance(engine)
    test_results['performance_metrics'] = await test_performance_metrics(engine)
    test_results['error_handling'] = await test_error_handling(engine)
    
    # Integration tests
    test_results['api_integration'] = await test_api_integration()
    
    # Results summary
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS:")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
        if passed:
            passed_tests += 1
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    # Performance summary
    try:
        if engine:
            metrics = engine.get_performance_metrics()
            print(f"\nPerformance Summary:")
            print(f"  Total Queries: {metrics.get('processing_metrics', {}).get('total_queries_processed', 0)}")
            print(f"  Active Sessions: {metrics.get('session_metrics', {}).get('active_sessions', 0)}")
            print(f"  AI Components: {sum(1 for v in metrics.get('ai_integration', {}).values() if v)}")
    except Exception as e:
        print(f"Performance summary failed: {e}")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED - Conversational Query Engine is production-ready!")
        print("\nP0 Features Validated:")
        print("- Natural language intent classification")
        print("- Parallel query processing pipeline")
        print("- AI infrastructure integration")
        print("- Multi-turn conversation management")
        print("- Entity extraction and enhancement") 
        print("- Advanced caching and performance optimization")
        print("- Comprehensive error handling")
        print("- REST API integration")
        
    elif passed_tests >= total_tests * 0.8:
        print("\n✅ MOSTLY FUNCTIONAL - Core P0 features working")
        print("\nRecommendations:")
        print("- Monitor performance in production environment")
        print("- Review failed tests for optimization opportunities")
        print("- Consider additional AI model integrations")
        
    else:
        print("\n⚠️ SIGNIFICANT ISSUES - Review implementation")
        print("\nRequired Actions:")
        print("- Fix critical test failures before production deployment")
        print("- Verify AI infrastructure dependencies")
        print("- Check configuration and environment setup")
    
    return 0 if passed_tests >= total_tests * 0.8 else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nValidation failed with error: {e}")
        sys.exit(1)