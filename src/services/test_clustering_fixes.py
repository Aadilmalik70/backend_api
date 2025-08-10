#!/usr/bin/env python3
"""
Test clustering fixes for missing attributes
"""
import asyncio
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

async def test_clustering():
    """Test clustering with accuracy validation"""
    try:
        from services.semantic_clustering_service import (
            SemanticClusteringService, ServiceConfig, ClusteringMode
        )
        
        # Test texts
        test_texts = [
            "machine learning and artificial intelligence",
            "deep learning neural networks", 
            "data science and analytics",
            "business strategy and planning",
            "marketing and sales optimization",
            "financial planning and investment"
        ]
        
        config = ServiceConfig(target_accuracy=0.85)
        service = SemanticClusteringService(config)
        await service.initialize()
        
        print("Testing clustering with validation...")
        result = await service.cluster_texts(
            texts=test_texts,
            mode=ClusteringMode.STANDARD,
            enable_validation=True
        )
        
        if result:
            print(f"Status: {result.status.value}")
            print(f"Clusters created: {result.total_clusters}")
            print(f"Overall quality: {result.overall_quality:.3f}")
            print(f"Has coherence_report: {result.coherence_report is not None}")
            print(f"Has metadata: {bool(result.metadata)}")
            
            if result.coherence_report:
                print(f"Accuracy target met: {result.coherence_report.meets_target}")
                print(f"Overall coherence: {result.coherence_report.overall_coherence:.3f}")
            
            return True
        else:
            print("No result returned")
            return False
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("Testing clustering fixes...")
    success = await test_clustering()
    
    if success:
        print("\n[SUCCESS] Clustering fixes working")
    else:
        print("\n[FAILED] Clustering fixes need more work")

if __name__ == "__main__":
    asyncio.run(main())