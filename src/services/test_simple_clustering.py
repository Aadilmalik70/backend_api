#!/usr/bin/env python3
"""
Simple clustering test to isolate the embedding issue
"""
import asyncio
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

async def test_embeddings():
    """Test basic embeddings generation"""
    try:
        from services.semantic_embeddings_service import SemanticEmbeddingsService, EmbeddingsConfig
        
        # Create simple config
        config = EmbeddingsConfig(
            enable_caching=False,
            max_concurrent_requests=1,
            batch_size=2
        )
        
        # Initialize service
        service = SemanticEmbeddingsService(config)
        await service.initialize()
        
        # Test simple embedding generation
        test_texts = ["hello world", "test text"]
        
        print("Generating embeddings...")
        result = await service.generate_embeddings(test_texts)
        
        print(f"Success! Generated {len(result)} embeddings")
        for i, embedding in enumerate(result):
            print(f"  Embedding {i}: vector dim {len(embedding.vector)}, text: '{embedding.text}'")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Running simple clustering embeddings test...")
    success = await test_embeddings()
    
    if success:
        print("[SUCCESS] Test passed")
    else:
        print("[FAILED] Test failed")

if __name__ == "__main__":
    asyncio.run(main())