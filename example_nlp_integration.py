#!/usr/bin/env python3
"""
NLP Processor Integration Example
Demonstrates how to integrate the new NLP processor with the existing SERP Strategist system.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def demonstrate_nlp_processor():
    """Demonstrate NLP processor capabilities"""
    print("NLP Processor Integration Demonstration")
    print("=" * 45)
    
    try:
        # Import the services
        from services.nlp_processor import get_nlp_processor, NLPConfig, quick_nlp_analysis
        from services.ai.nlp_enhanced_service import get_nlp_enhanced_service
        
        # Example content from SERP analysis
        sample_content = [
            "Content marketing is essential for SEO success and driving organic traffic to websites.",
            "Search engine optimization requires understanding user intent and creating valuable content.",
            "Artificial intelligence is transforming how businesses approach digital marketing strategies.",
            "Natural language processing enables better content analysis and keyword optimization.",
            "Machine learning algorithms help predict content performance and user engagement."
        ]
        
        # Competitor snippets example
        competitor_snippets = [
            "The ultimate guide to content marketing for beginners",
            "How to improve your SEO rankings with quality content",
            "AI-powered content marketing tools for 2024", 
            "Understanding search algorithms and ranking factors",
            "Content optimization strategies that actually work"
        ]
        
        print("1. Direct NLP Processor Usage")
        print("-" * 30)
        
        # Initialize processor
        config = NLPConfig(
            spacy_model="en_core_web_lg",
            sentence_transformer_model="all-MiniLM-L6-v2",
            enable_model_warmup=True,
            enable_embedding_cache=True,
            max_workers=2,
            batch_size=8
        )
        
        processor = get_nlp_processor(config)
        
        # Initialize (this may take some time for model loading)
        print("Initializing NLP models...")
        init_success = await processor.initialize()
        
        if init_success:
            print("✅ Models loaded successfully")
            
            # Analyze sample content
            print("\n📊 Analyzing sample content...")
            
            sample_text = sample_content[0]
            spacy_result = await processor.process_text_spacy(sample_text)
            
            if spacy_result:
                print(f"Text: '{sample_text}'")
                print(f"Entities found: {spacy_result['entity_count']}")
                print(f"Tokens: {spacy_result['token_count']}")
                print(f"Sentences: {spacy_result['sentence_count']}")
                
                if spacy_result['entities']:
                    print("Key entities:")
                    for entity in spacy_result['entities'][:3]:
                        print(f"  - {entity['text']} ({entity['label']})")
            
            # Compute embeddings
            print("\n🌐 Computing semantic embeddings...")
            embeddings = await processor.compute_embeddings(sample_content[:3])
            
            if embeddings is not None:
                print(f"Embeddings shape: {embeddings.shape}")
                print(f"Embedding dimensions: {embeddings.shape[1]}")
            
            # Semantic similarity
            print("\n🔍 Computing content similarity...")
            similarity = await processor.compute_similarity(
                sample_content[0], 
                sample_content[1]
            )
            
            if similarity is not None:
                print(f"Similarity between first two texts: {similarity:.3f}")
                print(f"High similarity: {'Yes' if similarity > 0.7 else 'No'}")
            
            # Semantic search
            print("\n🎯 Performing semantic search...")
            search_results = await processor.semantic_search(
                "content marketing strategies", 
                competitor_snippets, 
                top_k=3
            )
            
            if search_results:
                print("Top 3 most relevant competitor snippets:")
                for i, (idx, text, score) in enumerate(search_results, 1):
                    print(f"  {i}. Score: {score:.3f} - '{text}'")
            
            print("\n" + "=" * 45)
            print("2. Enhanced Service Integration")
            print("-" * 30)
            
            # Use the enhanced service (AI infrastructure integration)
            enhanced_service = get_nlp_enhanced_service()
            
            # Content quality analysis
            print("\n📈 Analyzing content quality...")
            quality_result = await enhanced_service.analyze_content_quality(sample_content[0])
            
            if quality_result.get('success'):
                print(f"Quality Score: {quality_result['quality_score']}/100")
                print("Quality Factors:")
                for factor in quality_result['quality_factors']:
                    print(f"  - {factor}")
                
                metrics = quality_result['metrics']
                print(f"Metrics: {metrics['token_count']} tokens, {metrics['sentence_count']} sentences")
            
            # Batch processing demonstration
            print("\n⚡ Batch processing demonstration...")
            batch_results = await enhanced_service.process_batch(sample_content[:3])
            
            if batch_results:
                print(f"Processed {len(batch_results)} texts in batch")
                for i, result in enumerate(batch_results):
                    if result.get('success'):
                        analysis = result.get('analysis', {})
                        entities = analysis.get('entities', [])
                        print(f"  Text {i+1}: {len(entities)} entities, {result.get('processing_time', 0):.3f}s")
            
            # Performance metrics
            print("\n📊 Performance Metrics")
            print("-" * 20)
            
            metrics = processor.get_performance_metrics()
            perf = metrics['performance']
            resources = metrics['resources']
            
            print(f"Total requests: {perf['total_requests']}")
            print(f"Success rate: {perf['success_rate']:.1f}%")
            print(f"Cache hit rate: {perf['cache_hit_rate']:.1f}%")
            print(f"Memory usage: {resources['memory_usage_mb']:.1f} MB")
            print(f"Average processing time: {perf['avg_processing_time']:.3f}s")
            
            # Health check
            health = await processor.health_check()
            print(f"Health status: {health['status']}")
            
            print("\n" + "=" * 45)
            print("3. SERP Strategist Integration Example")
            print("-" * 35)
            
            # Example of how this could be used in blueprint generation
            print("\n🎯 Blueprint Enhancement Scenario:")
            print("Analyzing competitor content for 'content marketing'...")
            
            # Simulate competitor analysis
            competitor_analysis = []
            for snippet in competitor_snippets:
                analysis = await enhanced_service.analyze_content_quality(snippet)
                if analysis.get('success'):
                    competitor_analysis.append({
                        'text': snippet,
                        'quality_score': analysis['quality_score'],
                        'entity_count': analysis['metrics']['entity_count']
                    })
            
            if competitor_analysis:
                # Sort by quality
                competitor_analysis.sort(key=lambda x: x['quality_score'], reverse=True)
                
                print("Top competitor content analysis:")
                for i, comp in enumerate(competitor_analysis[:3], 1):
                    print(f"  {i}. Quality: {comp['quality_score']}/100, Entities: {comp['entity_count']}")
                    print(f"     '{comp['text'][:60]}...'")
            
            # Find content gaps using semantic search
            print("\n🔍 Content gap analysis...")
            gap_analysis = await enhanced_service.find_similar_content(
                "advanced SEO techniques",
                competitor_snippets,
                top_k=2
            )
            
            if gap_analysis.get('success'):
                results = gap_analysis['results']
                if results:
                    max_similarity = max(r['similarity_score'] for r in results)
                    if max_similarity < 0.5:
                        print("✅ Content gap identified: 'advanced SEO techniques' is underrepresented")
                    else:
                        print(f"⚠️ Content overlap detected (max similarity: {max_similarity:.3f})")
            
            # Cleanup
            await processor.shutdown()
            await enhanced_service.shutdown()
            
            print("\n✅ NLP Processor demonstration complete!")
            
        else:
            print("❌ Model initialization failed")
            print("Note: This requires spaCy and sentence-transformers to be installed")
            print("Install with:")
            print("  pip install spacy sentence-transformers")
            print("  python -m spacy download en_core_web_lg")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nRequired dependencies:")
        print("  pip install spacy sentence-transformers torch")
        print("  python -m spacy download en_core_web_lg")
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")

async def quick_demonstration():
    """Quick demonstration using convenience functions"""
    print("\n" + "=" * 45)
    print("Quick NLP Analysis Demo")
    print("-" * 25)
    
    try:
        from services.nlp_processor import quick_nlp_analysis, compute_text_similarity
        
        # Quick analysis
        sample_text = "Content marketing drives organic traffic through valuable, SEO-optimized content."
        
        print("Analyzing: '{}'".format(sample_text[:50] + "..."))
        result = await quick_nlp_analysis(sample_text)
        
        if result.get('success'):
            print("✅ Analysis successful")
            if result.get('spacy_analysis'):
                spacy = result['spacy_analysis']
                print(f"   Entities: {spacy['entity_count']}")
                print(f"   Tokens: {spacy['token_count']}")
            
            if result.get('embedding'):
                print(f"   Embedding dimensions: {result['embedding_shape']}")
        else:
            print(f"❌ Analysis failed: {result.get('error')}")
        
        # Quick similarity
        text1 = "SEO content optimization strategies"
        text2 = "Content optimization for search engines"
        
        similarity_result = await compute_text_similarity(text1, text2)
        
        if similarity_result.get('success'):
            similarity = similarity_result.get('similarity')
            print(f"\nSimilarity analysis:")
            print(f"   Score: {similarity:.3f}")
            print(f"   Highly similar: {'Yes' if similarity_result.get('highly_similar') else 'No'}")
        
    except Exception as e:
        print(f"❌ Quick demo failed: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_nlp_processor())
        asyncio.run(quick_demonstration())
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")