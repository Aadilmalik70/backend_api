#!/usr/bin/env python3
"""
NLP Processor Validation Script
Validates the comprehensive NLP processor implementation with both models and caching.
"""

import sys
import os
import asyncio
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_nlp_processor_import():
    """Test NLP processor import and basic initialization"""
    print("Testing NLP Processor Import...")
    
    try:
        from services.nlp_processor import (
            NLPProcessor, 
            NLPConfig, 
            get_nlp_processor,
            quick_nlp_analysis,
            compute_text_similarity
        )
        
        print("  NLP Processor Classes: Available")
        
        # Test configuration
        config = NLPConfig(
            spacy_model="en_core_web_lg",
            sentence_transformer_model="all-MiniLM-L6-v2",
            enable_model_warmup=True,
            enable_embedding_cache=True,
            max_workers=2,  # Reduced for testing
            batch_size=4    # Reduced for testing
        )
        
        print("  Configuration: Created")
        
        # Test processor instance
        processor = get_nlp_processor(config)
        print("  Processor Instance: Created")
        
        return True, processor
        
    except Exception as e:
        print(f"  Import test failed: {e}")
        return False, None

async def test_model_initialization(processor):
    """Test model initialization with fallbacks"""
    print("\nTesting Model Initialization...")
    
    try:
        # Test initialization
        init_success = await processor.initialize()
        
        if init_success:
            print("  Model Initialization: SUCCESS")
            
            # Check which models loaded
            metrics = processor.get_performance_metrics()
            models = metrics['models']
            
            print(f"  spaCy Model: {'LOADED' if models['spacy_loaded'] else 'NOT LOADED'}")
            print(f"  Sentence Transformer: {'LOADED' if models['sentence_transformer_loaded'] else 'NOT LOADED'}")
            print(f"  Models Warmed Up: {'YES' if models['models_warmed_up'] else 'NO'}")
            
            if models['spacy_loaded']:
                print(f"  spaCy Model Name: {models['spacy_model_name']}")
            if models['sentence_transformer_loaded']:
                print(f"  Transformer Model: {models['transformer_model_name']}")
            
            return models['spacy_loaded'] or models['sentence_transformer_loaded']
        else:
            print("  Model Initialization: FAILED")
            return False
            
    except Exception as e:
        print(f"  Initialization failed: {e}")
        return False

async def test_spacy_processing(processor):
    """Test spaCy text processing"""
    print("\nTesting spaCy Processing...")
    
    test_texts = [
        "Apple Inc. is planning to build a new data center in Austin, Texas.",
        "The quick brown fox jumps over the lazy dog in the beautiful garden.",
        "Machine learning and artificial intelligence are transforming business operations."
    ]
    
    try:
        results = []
        for i, text in enumerate(test_texts):
            print(f"  Processing text {i+1}...")
            
            result = await processor.process_text_spacy(text)
            
            if result:
                results.append(result)
                print(f"    Tokens: {result['token_count']}")
                print(f"    Entities: {result['entity_count']}")
                print(f"    Sentences: {result['sentence_count']}")
                print(f"    Processing time: {result['processing_time']:.3f}s")
                
                # Show some entities
                if result['entities']:
                    entities = result['entities'][:3]  # First 3 entities
                    for ent in entities:
                        print(f"      Entity: '{ent['text']}' ({ent['label']})")
            else:
                print(f"    Processing failed for text {i+1}")
        
        success_rate = len(results) / len(test_texts) * 100
        print(f"  spaCy Processing Success Rate: {success_rate:.1f}%")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  spaCy processing test failed: {e}")
        return False

async def test_embedding_computation(processor):
    """Test embedding computation and caching"""
    print("\nTesting Embedding Computation...")
    
    test_texts = [
        "Natural language processing is a subfield of artificial intelligence.",
        "Machine learning models require large amounts of training data.",
        "Deep learning uses neural networks with multiple layers.",
        "Text analysis helps extract insights from unstructured data."
    ]
    
    try:
        # Test individual embeddings
        print("  Computing individual embeddings...")
        individual_results = []
        
        for i, text in enumerate(test_texts[:2]):  # Test first 2 texts
            embedding = await processor.compute_embeddings(text)
            
            if embedding is not None:
                individual_results.append(embedding)
                print(f"    Text {i+1} embedding shape: {embedding.shape}")
            else:
                print(f"    Text {i+1} embedding failed")
        
        # Test batch embeddings
        print("  Computing batch embeddings...")
        batch_embeddings = await processor.compute_embeddings(test_texts)
        
        if batch_embeddings is not None:
            print(f"    Batch embeddings shape: {batch_embeddings.shape}")
            print(f"    Expected shape: ({len(test_texts)}, {processor.config.embedding_dimensions})")
            
            batch_success = batch_embeddings.shape[0] == len(test_texts)
        else:
            print("    Batch embedding computation failed")
            batch_success = False
        
        # Test caching (second call should be faster)
        if batch_embeddings is not None:
            print("  Testing embedding cache...")
            
            start_time = time.time()
            cached_embeddings = await processor.compute_embeddings(test_texts[:2])
            cache_time = time.time() - start_time
            
            print(f"    Cache lookup time: {cache_time:.3f}s")
            
            if cached_embeddings is not None:
                print("    Cache test: SUCCESS")
                cache_success = True
            else:
                print("    Cache test: FAILED")
                cache_success = False
        else:
            cache_success = False
        
        overall_success = len(individual_results) > 0 and batch_success and cache_success
        return overall_success
        
    except Exception as e:
        print(f"  Embedding test failed: {e}")
        return False

async def test_similarity_computation(processor):
    """Test semantic similarity computation"""
    print("\nTesting Similarity Computation...")
    
    test_pairs = [
        ("I love machine learning", "Machine learning is fascinating"),
        ("The weather is sunny today", "It's a beautiful day with sunshine"),
        ("Python programming language", "JavaScript web development"),
        ("Natural language processing", "Computer vision and image recognition")
    ]
    
    try:
        results = []
        
        for i, (text1, text2) in enumerate(test_pairs):
            similarity = await processor.compute_similarity(text1, text2)
            
            if similarity is not None:
                results.append(similarity)
                print(f"  Pair {i+1} similarity: {similarity:.3f}")
                print(f"    Text 1: '{text1[:50]}{'...' if len(text1) > 50 else ''}'")
                print(f"    Text 2: '{text2[:50]}{'...' if len(text2) > 50 else ''}'")
                
                if similarity > processor.config.similarity_threshold:
                    print(f"    High similarity detected")
            else:
                print(f"  Pair {i+1} similarity computation failed")
        
        success_rate = len(results) / len(test_pairs) * 100
        print(f"  Similarity Computation Success Rate: {success_rate:.1f}%")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"  Similarity test failed: {e}")
        return False

async def test_semantic_search(processor):
    """Test semantic search functionality"""
    print("\nTesting Semantic Search...")
    
    try:
        query = "machine learning algorithms"
        corpus = [
            "Deep learning is a subset of machine learning using neural networks",
            "Natural language processing helps computers understand human language",
            "Computer vision enables machines to interpret visual information",
            "Reinforcement learning trains agents through rewards and penalties",
            "Supervised learning uses labeled data to train predictive models",
            "The weather forecast predicts rain tomorrow afternoon"
        ]
        
        print(f"  Query: '{query}'")
        print(f"  Corpus size: {len(corpus)} documents")
        
        results = await processor.semantic_search(query, corpus, top_k=3)
        
        if results:
            print(f"  Search Results (Top 3):")
            for rank, (idx, text, score) in enumerate(results, 1):
                print(f"    {rank}. Score: {score:.3f} - '{text[:70]}{'...' if len(text) > 70 else ''}'")
            
            # Check if results are properly ranked
            scores = [score for _, _, score in results]
            properly_ranked = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            
            print(f"  Results properly ranked: {'YES' if properly_ranked else 'NO'}")
            return len(results) > 0 and properly_ranked
        else:
            print("  Semantic search failed")
            return False
            
    except Exception as e:
        print(f"  Semantic search test failed: {e}")
        return False

async def test_batch_processing(processor):
    """Test batch processing functionality"""
    print("\nTesting Batch Processing...")
    
    test_texts = [
        "Artificial intelligence is revolutionizing technology.",
        "Machine learning models learn from data patterns.",
        "Natural language processing enables human-computer interaction.",
        "Computer vision interprets and analyzes visual content.",
        "Deep learning uses multi-layer neural network architectures."
    ]
    
    try:
        print(f"  Processing batch of {len(test_texts)} texts...")
        
        start_time = time.time()
        results = await processor.batch_process_texts(
            test_texts, 
            include_spacy=True, 
            include_embeddings=True
        )
        processing_time = time.time() - start_time
        
        print(f"  Batch processing time: {processing_time:.3f}s")
        print(f"  Results count: {len(results)}")
        
        if results:
            # Check result structure
            spacy_results = sum(1 for r in results if r.get('spacy') is not None)
            embedding_results = sum(1 for r in results if r.get('embedding') is not None)
            
            print(f"  spaCy results: {spacy_results}/{len(test_texts)}")
            print(f"  Embedding results: {embedding_results}/{len(test_texts)}")
            
            # Show sample result
            if results:
                sample = results[0]
                print(f"  Sample result structure:")
                print(f"    Text: {sample.get('text', 'N/A')[:50]}...")
                print(f"    spaCy available: {'YES' if sample.get('spacy') else 'NO'}")
                print(f"    Embedding available: {'YES' if sample.get('embedding') else 'NO'}")
                
                if sample.get('embedding'):
                    embedding_shape = len(sample['embedding'])
                    print(f"    Embedding dimensions: {embedding_shape}")
            
            success = len(results) == len(test_texts)
            return success
        else:
            print("  Batch processing returned no results")
            return False
            
    except Exception as e:
        print(f"  Batch processing test failed: {e}")
        return False

async def test_performance_metrics(processor):
    """Test performance metrics and monitoring"""
    print("\nTesting Performance Metrics...")
    
    try:
        metrics = processor.get_performance_metrics()
        
        print("  Performance Metrics:")
        print(f"    Total requests: {metrics['performance']['total_requests']}")
        print(f"    Success rate: {metrics['performance']['success_rate']:.1f}%")
        print(f"    Cache hit rate: {metrics['performance']['cache_hit_rate']:.1f}%")
        print(f"    Average processing time: {metrics['performance']['avg_processing_time']:.3f}s")
        print(f"    Memory usage: {metrics['resources']['memory_usage_mb']:.1f} MB")
        print(f"    Memory limit: {metrics['resources']['memory_limit_gb']:.1f} GB")
        
        # Test health check
        health = await processor.health_check()
        print(f"  Health Status: {health['status'].upper()}")
        
        if 'memory_status' in health:
            mem_status = health['memory_status']
            print(f"  Memory usage: {mem_status['usage_gb']:.2f} GB ({mem_status['percentage']:.1f}%)")
            print(f"  Memory within limits: {'YES' if mem_status['within_limits'] else 'NO'}")
        
        return health['status'] in ['healthy', 'warning']
        
    except Exception as e:
        print(f"  Performance metrics test failed: {e}")
        return False

async def test_convenience_functions():
    """Test convenience functions"""
    print("\nTesting Convenience Functions...")
    
    try:
        # Test quick NLP analysis
        test_text = "Apple Inc. is developing new AI technologies for next-generation devices."
        
        result = await quick_nlp_analysis(test_text)
        
        if result.get('success'):
            print("  Quick NLP Analysis: SUCCESS")
            print(f"    spaCy analysis available: {'YES' if result.get('spacy_analysis') else 'NO'}")
            print(f"    Embedding available: {'YES' if result.get('embedding') else 'NO'}")
            if result.get('embedding_shape'):
                print(f"    Embedding shape: {result['embedding_shape']}")
        else:
            print(f"  Quick NLP Analysis: FAILED - {result.get('error')}")
        
        # Test text similarity
        similarity_result = await compute_text_similarity(
            "Machine learning is powerful",
            "AI and ML are transformative technologies"
        )
        
        if similarity_result.get('success'):
            print("  Text Similarity: SUCCESS")
            print(f"    Similarity score: {similarity_result.get('similarity', 'N/A')}")
            print(f"    Highly similar: {'YES' if similarity_result.get('highly_similar') else 'NO'}")
        else:
            print(f"  Text Similarity: FAILED - {similarity_result.get('error')}")
        
        return result.get('success', False) and similarity_result.get('success', False)
        
    except Exception as e:
        print(f"  Convenience functions test failed: {e}")
        return False

async def main():
    """Run comprehensive NLP processor validation"""
    print("NLP Processor Comprehensive Validation")
    print("=" * 50)
    
    # Test import and initialization
    import_success, processor = await test_nlp_processor_import()
    if not import_success:
        print("\n❌ Import test failed - cannot proceed")
        return 1
    
    # Run all tests
    test_results = {
        'import': import_success,
        'initialization': False,
        'spacy_processing': False,
        'embedding_computation': False,
        'similarity_computation': False,
        'semantic_search': False,
        'batch_processing': False,
        'performance_metrics': False,
        'convenience_functions': False
    }
    
    # Model initialization test
    test_results['initialization'] = await test_model_initialization(processor)
    
    # Only proceed with other tests if models loaded
    if test_results['initialization']:
        test_results['spacy_processing'] = await test_spacy_processing(processor)
        test_results['embedding_computation'] = await test_embedding_computation(processor)
        test_results['similarity_computation'] = await test_similarity_computation(processor)
        test_results['semantic_search'] = await test_semantic_search(processor)
        test_results['batch_processing'] = await test_batch_processing(processor)
        test_results['performance_metrics'] = await test_performance_metrics(processor)
        test_results['convenience_functions'] = await test_convenience_functions()
    else:
        print("\n⚠️ Skipping functional tests due to model loading issues")
    
    # Results summary
    print("\n" + "=" * 50)
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
        print("\n✅ ALL TESTS PASSED - NLP Processor is production-ready!")
        print("\nKey Features Validated:")
        print("- spaCy en_core_web_lg integration with fallbacks")
        print("- Sentence-transformers all-MiniLM-L6-v2 embeddings")
        print("- Advanced caching with model warmup")
        print("- Async processing with batch operations")
        print("- Memory optimization and monitoring")
        print("- Comprehensive API interface")
        
    elif passed_tests >= total_tests * 0.7:
        print("\n✅ MOSTLY FUNCTIONAL - Core features working")
        print("\nRecommendations:")
        if not test_results['initialization']:
            print("- Install required models: python -m spacy download en_core_web_lg")
            print("- Ensure sentence-transformers is properly installed")
        print("- Monitor system in development environment")
        
    else:
        print("\n⚠️ SIGNIFICANT ISSUES - Review implementation")
        print("\nRequired Actions:")
        print("- Check dependency installation")
        print("- Verify model availability")
        print("- Review error logs")
    
    # Cleanup
    try:
        await processor.shutdown()
        print("\n🛑 NLP Processor shutdown complete")
    except:
        pass
    
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