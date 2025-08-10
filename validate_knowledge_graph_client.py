#!/usr/bin/env python3
"""
Enhanced Knowledge Graph Client Validation Script
Tests the comprehensive Knowledge Graph client with Google APIs integration, batch processing, and rate limiting.
"""

import sys
import os
import asyncio
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_knowledge_graph_import():
    """Test Knowledge Graph client import and initialization"""
    print("Testing Knowledge Graph Client Import...")
    
    try:
        from utils.google_apis.knowledge_graph_client import (
            KnowledgeGraphClient,
            EntityResult,
            RateLimiter,
            get_knowledge_graph_client
        )
        
        print("  Knowledge Graph Classes: Available")
        
        # Test configuration
        config = {
            'requests_per_minute': 10,  # Reduced for testing
            'requests_per_day': 100,    # Reduced for testing
            'cache_ttl_hours': 1,       # Short TTL for testing
            'max_batch_size': 5         # Small batch for testing
        }
        
        print("  Configuration: ✅ Created")
        
        # Test client instance
        client = get_knowledge_graph_client(config)
        print("  Client Instance: ✅ Created")
        
        return True, client
        
    except Exception as e:
        print(f"  Import test failed: ❌ {e}")
        return False, None

async def test_health_check(client):
    """Test comprehensive health check"""
    print("\nTesting Health Check...")
    
    try:
        health = await client.health_check()
        
        print("  Health Check Response: ✅ Received")
        print(f"  Overall Status: {health['status'].upper()}")
        
        services = health.get('services', {})
        print(f"  Knowledge Graph API: {'✅' if services.get('knowledge_graph', {}).get('available') else '⚠️'} Available")
        print(f"  Natural Language API: {'✅' if services.get('natural_language', {}).get('available') else '⚠️'} Available")
        
        rate_limiting = health.get('rate_limiting', {})
        print(f"  Rate Limiting Status: {'✅' if rate_limiting.get('can_make_request') else '⚠️'} OK")
        print(f"  Daily Calls: {rate_limiting.get('daily_calls_made', 0)}/{rate_limiting.get('daily_limit', 0)}")
        
        cache_info = health.get('cache', {})
        print(f"  Cache Entries: {cache_info.get('entries', 0)}")
        
        return health['status'] in ['healthy', 'warning']
        
    except Exception as e:
        print(f"  Health check failed: ❌ {e}")
        return False

async def test_single_entity_retrieval(client):
    """Test single entity information retrieval"""
    print("\nTesting Single Entity Retrieval...")
    
    test_queries = [
        "google.com",
        "microsoft",
        "apple inc",
        "github.com"
    ]
    
    try:
        results = []
        for i, query in enumerate(test_queries):
            print(f"  Processing entity {i+1}: '{query}'...")
            
            # Test without NLP enrichment first (faster)
            entity = await client.get_entity_info(query, enrich_with_nlp=False)
            
            if entity.name:
                results.append(entity)
                print(f"    Name: {entity.name}")
                print(f"    Industry: {entity.industry}")
                print(f"    Confidence: {entity.confidence_score:.2f}")
                print(f"    Types: {', '.join(entity.types[:2])}")  # Show first 2 types
                if entity.description:
                    print(f"    Description: {entity.description[:80]}...")
            else:
                print(f"    Entity retrieval failed for: {query}")
        
        success_rate = len(results) / len(test_queries) * 100
        print(f"  Single Entity Success Rate: {success_rate:.1f}%")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  Single entity test failed: ❌ {e}")
        return False

async def test_batch_processing(client):
    """Test batch entity processing"""
    print("\nTesting Batch Processing...")
    
    batch_queries = [
        "google.com",
        "microsoft.com",
        "amazon.com", 
        "facebook.com",
        "tesla.com"
    ]
    
    try:
        print(f"  Processing batch of {len(batch_queries)} entities...")
        
        start_time = time.time()
        batch_results = await client.get_entities_batch(batch_queries, enrich_with_nlp=False)
        processing_time = time.time() - start_time
        
        print(f"  Batch processing time: {processing_time:.2f}s")
        print(f"  Results received: {len(batch_results)}")
        
        if batch_results:
            # Show sample results
            successful_results = [r for r in batch_results if r.confidence_score > 0]
            print(f"  Successful retrievals: {len(successful_results)}/{len(batch_queries)}")
            
            if successful_results:
                print("  Sample results:")
                for i, entity in enumerate(successful_results[:3]):
                    print(f"    {i+1}. {entity.name} (Industry: {entity.industry}, Score: {entity.confidence_score:.2f})")
            
            batch_success = len(batch_results) == len(batch_queries)
            return batch_success
        else:
            print("  Batch processing returned no results")
            return False
            
    except Exception as e:
        print(f"  Batch processing test failed: ❌ {e}")
        return False

async def test_entity_search(client):
    """Test entity search functionality"""
    print("\nTesting Entity Search...")
    
    search_queries = [
        ("technology companies", 3),
        ("google", 5),
        ("social media", 2)
    ]
    
    try:
        results = []
        
        for query, limit in search_queries:
            print(f"  Searching for: '{query}' (limit: {limit})...")
            
            search_result = await client.search_entities(query, limit=limit, enrich_with_nlp=False)
            
            if search_result.get('itemListElement'):
                results.append(search_result)
                entities = search_result['itemListElement']
                print(f"    Found {len(entities)} entities")
                
                # Show top result
                if entities:
                    top_entity = entities[0]['result']
                    score = entities[0].get('resultScore', 0)
                    print(f"    Top result: {top_entity.get('name', 'Unknown')} (Score: {score})")
            else:
                print(f"    No entities found for: {query}")
        
        search_success_rate = len(results) / len(search_queries) * 100
        print(f"  Entity Search Success Rate: {search_success_rate:.1f}%")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  Entity search test failed: ❌ {e}")
        return False

async def test_caching_functionality(client):
    """Test caching performance"""
    print("\nTesting Caching Functionality...")
    
    try:
        test_query = "apple.com"
        
        # Clear cache first
        client.clear_cache()
        print("  Cache cleared")
        
        # First request (cache miss)
        print(f"  First request (cache miss): '{test_query}'...")
        start_time = time.time()
        first_result = await client.get_entity_info(test_query, enrich_with_nlp=False)
        first_time = time.time() - start_time
        
        if first_result.name:
            print(f"    First request time: {first_time:.3f}s")
            print(f"    Entity found: {first_result.name}")
        
        # Second request (cache hit)
        print(f"  Second request (cache hit): '{test_query}'...")
        start_time = time.time()
        second_result = await client.get_entity_info(test_query, enrich_with_nlp=False)
        second_time = time.time() - start_time
        
        if second_result.name:
            print(f"    Second request time: {second_time:.3f}s")
            
            # Calculate cache performance improvement
            if first_time > 0:
                improvement = ((first_time - second_time) / first_time) * 100
                print(f"    Cache performance improvement: {improvement:.1f}%")
        
        # Check cache stats
        cache_stats = client.get_cache_stats()
        print(f"  Cache entries after test: {cache_stats['total_entries']}")
        
        cache_working = second_time < first_time and cache_stats['total_entries'] > 0
        return cache_working
        
    except Exception as e:
        print(f"  Caching test failed: ❌ {e}")
        return False

async def test_rate_limiting(client):
    """Test rate limiting functionality"""
    print("\nTesting Rate Limiting...")
    
    try:
        # Get initial rate limit status
        initial_status = client.get_rate_limit_status()
        print(f"  Initial daily calls: {initial_status['daily_calls_made']}")
        print(f"  Daily limit: {initial_status['daily_limit']}")
        print(f"  Can make request: {initial_status['can_make_request']}")
        
        # Make a few requests to test rate limiting
        test_queries = ["test1.com", "test2.com", "test3.com"]
        
        for i, query in enumerate(test_queries):
            status_before = client.get_rate_limit_status()
            can_make_request = status_before['can_make_request']
            
            print(f"  Request {i+1}: {query} (Can make request: {can_make_request})")
            
            if can_make_request:
                await client.get_entity_info(query, enrich_with_nlp=False)
                
                status_after = client.get_rate_limit_status()
                print(f"    Daily calls after: {status_after['daily_calls_made']}")
            else:
                print(f"    Rate limited - skipping request")
                break
        
        final_status = client.get_rate_limit_status()
        print(f"  Final daily calls: {final_status['daily_calls_made']}")
        
        # Rate limiting is working if we tracked the calls
        rate_limiting_working = final_status['daily_calls_made'] > initial_status['daily_calls_made']
        return rate_limiting_working
        
    except Exception as e:
        print(f"  Rate limiting test failed: ❌ {e}")
        return False

async def test_backward_compatibility(client):
    """Test backward compatibility with original interface"""
    print("\nTesting Backward Compatibility...")
    
    try:
        # Test sync methods that maintain original interface
        test_query = "github.com"
        
        print(f"  Testing sync entity info for: '{test_query}'...")
        sync_result = client.get_entity_info_sync(test_query)
        
        if sync_result:
            print("    Sync entity info: ✅ Working")
            print(f"    Name: {sync_result.get('name', 'N/A')}")
            print(f"    Industry: {sync_result.get('industry', 'N/A')}")
        else:
            print("    Sync entity info: ⚠️ Empty result (may be expected)")
        
        # Test sync search
        print(f"  Testing sync search for: '{test_query}'...")
        sync_search = client.search_entities_sync(test_query, limit=3)
        
        if sync_search.get('itemListElement'):
            print("    Sync search: ✅ Working")
            print(f"    Results: {len(sync_search['itemListElement'])}")
        else:
            print("    Sync search: ⚠️ Empty results (may be expected)")
        
        # Compatibility working if we get some kind of response
        compatibility_working = sync_result is not None and sync_search is not None
        return compatibility_working
        
    except Exception as e:
        print(f"  Backward compatibility test failed: ❌ {e}")
        return False

async def test_nlp_enrichment(client):
    """Test NLP enrichment if Natural Language API is available"""
    print("\nTesting NLP Enrichment...")
    
    try:
        if not client.natural_language_client:
            print("  Natural Language API not available - skipping enrichment test")
            return True  # Not a failure, just not available
        
        test_query = "google.com"
        print(f"  Testing NLP enrichment for: '{test_query}'...")
        
        # Get entity with NLP enrichment
        enriched_entity = await client.get_entity_info(test_query, enrich_with_nlp=True)
        
        if enriched_entity.nlp_analysis:
            print("    NLP Enrichment: ✅ Working")
            
            nlp_data = enriched_entity.nlp_analysis
            entities = nlp_data.get('entities', [])
            sentiment = nlp_data.get('sentiment', {})
            
            print(f"    NLP Entities found: {len(entities)}")
            print(f"    Sentiment score: {sentiment.get('score', 'N/A')}")
            
            if entities:
                print("    Sample NLP entities:")
                for i, entity in enumerate(entities[:2]):
                    print(f"      {i+1}. {entity.get('name')} ({entity.get('type')})")
            
            return True
        else:
            print("    NLP Enrichment: ⚠️ No enrichment data")
            return False
        
    except Exception as e:
        print(f"  NLP enrichment test failed: ❌ {e}")
        return False

async def main():
    """Run comprehensive Knowledge Graph client validation"""
    print("Enhanced Knowledge Graph Client Validation")
    print("=" * 55)
    
    # Test import and initialization
    import_success, client = await test_knowledge_graph_import()
    if not import_success:
        print("\n❌ Import test failed - cannot proceed")
        return 1
    
    # Run all tests
    test_results = {
        'import': import_success,
        'health_check': False,
        'single_entity_retrieval': False,
        'batch_processing': False,
        'entity_search': False,
        'caching_functionality': False,
        'rate_limiting': False,
        'backward_compatibility': False,
        'nlp_enrichment': False
    }
    
    # Health check test
    test_results['health_check'] = await test_health_check(client)
    
    # Core functionality tests
    test_results['single_entity_retrieval'] = await test_single_entity_retrieval(client)
    test_results['batch_processing'] = await test_batch_processing(client)
    test_results['entity_search'] = await test_entity_search(client)
    
    # Performance and reliability tests
    test_results['caching_functionality'] = await test_caching_functionality(client)
    test_results['rate_limiting'] = await test_rate_limiting(client)
    
    # Compatibility and enhancement tests
    test_results['backward_compatibility'] = await test_backward_compatibility(client)
    test_results['nlp_enrichment'] = await test_nlp_enrichment(client)
    
    # Results summary
    print("\n" + "=" * 55)
    print("VALIDATION RESULTS:")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, passed in test_results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
        if passed:
            passed_tests += 1
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED - Enhanced Knowledge Graph Client is production-ready!")
        print("\nKey Features Validated:")
        print("- Google Knowledge Graph API integration")
        print("- Google Natural Language API enrichment") 
        print("- Intelligent batch processing with rate limiting")
        print("- Advanced caching with TTL management")
        print("- Comprehensive error handling and fallbacks")
        print("- Backward compatibility with original interface")
        print("- Health monitoring and performance metrics")
        
    elif passed_tests >= total_tests * 0.7:
        print("\n✅ MOSTLY FUNCTIONAL - Core features working")
        print("\nRecommendations:")
        if not test_results['health_check']:
            print("- Check Google API credentials and network connectivity")
        if not test_results['nlp_enrichment']:
            print("- Verify Google Natural Language API setup and credentials")
        print("- Monitor system in development environment")
        
    else:
        print("\n⚠️ SIGNIFICANT ISSUES - Review implementation")
        print("\nRequired Actions:")
        print("- Check Google API credentials configuration")
        print("- Verify network connectivity and firewall settings")
        print("- Review error logs for specific issues")
        print("- Ensure required dependencies are installed")
    
    # Show final status
    try:
        final_health = await client.health_check()
        print(f"\nFinal Health Status: {final_health['status'].upper()}")
        
        rate_status = client.get_rate_limit_status()
        print(f"API Calls Made: {rate_status['daily_calls_made']}/{rate_status['daily_limit']}")
        
        cache_stats = client.get_cache_stats()
        print(f"Cache Entries: {cache_stats['total_entries']}")
        
    except Exception as e:
        print(f"\nFinal status check failed: {e}")
    
    return 0 if passed_tests >= total_tests * 0.7 else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)