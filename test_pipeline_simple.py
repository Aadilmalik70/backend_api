#!/usr/bin/env python3
"""
Simple Data Acquisition Pipeline Test

Basic testing of the data acquisition pipeline functionality.
"""

import asyncio
import sys
import os

# Add the source directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.data_acquisition_pipeline import DataAcquisitionPipeline, PipelineConfig
from services.data_models import PipelineMode, DataSourceType

async def test_pipeline_basic():
    """Test basic pipeline functionality"""
    print("Starting Data Acquisition Pipeline Tests...")
    
    try:
        # Test 1: Create pipeline
        print("\n1. Testing pipeline creation...")
        pipeline = DataAcquisitionPipeline()
        print("PASS: Pipeline created successfully")
        
        # Test 2: Initialize pipeline
        print("\n2. Testing pipeline initialization...")
        await pipeline.initialize()
        print("PASS: Pipeline initialized successfully")
        print(f"   Clients initialized: {len(pipeline.clients)}")
        print(f"   Rate limiters: {len(pipeline.rate_limiters)}")
        
        # Test 3: Health check
        print("\n3. Testing health check...")
        health = await pipeline.health_check()
        print("PASS: Health check completed")
        print(f"   Status: {health['pipeline_status']}")
        print(f"   Components: {len(health['components'])}")
        
        # Test 4: Get metrics
        print("\n4. Testing metrics collection...")
        metrics = await pipeline.get_pipeline_metrics()
        print("PASS: Metrics collected")
        print(f"   Total requests: {metrics['pipeline_metrics']['total_requests']}")
        
        # Test 5: Data acquisition (mock)
        print("\n5. Testing data acquisition...")
        result = await pipeline.acquire_data(
            query="test query",
            mode=PipelineMode.FAST,
            sources=[DataSourceType.GOOGLE_AUTOCOMPLETE]
        )
        print("PASS: Data acquisition completed")
        print(f"   Query: {result.query}")
        print(f"   Status: {result.status}")
        print(f"   Execution time: {result.execution_time:.3f}s")
        print(f"   Quality score: {result.quality_score:.3f}")
        
        # Test 6: Shutdown
        print("\n6. Testing pipeline shutdown...")
        await pipeline.shutdown()
        print("PASS: Pipeline shutdown completed")
        
        print("\nAll tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"FAIL: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_pipeline_basic())
    if success:
        print("\nSUCCESS: All pipeline tests passed!")
    else:
        print("\nFAILURE: Some pipeline tests failed!")
    exit(0 if success else 1)