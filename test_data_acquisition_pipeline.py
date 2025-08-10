#!/usr/bin/env python3
"""
Data Acquisition Pipeline Integration Test

Comprehensive testing of the data acquisition pipeline with all components,
including async processing, rate limiting, timeout protection, and data aggregation.
"""

import asyncio
import sys
import os

# Add the source directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.data_acquisition_pipeline import DataAcquisitionPipeline, PipelineConfig
from services.data_models import PipelineMode, DataSourceType

async def test_basic_pipeline_creation():
    """Test basic pipeline creation and initialization"""
    print("TEST: Testing pipeline creation...")
    
    try:
        # Create pipeline with default configuration
        pipeline = DataAcquisitionPipeline()
        
        print("PASS: Pipeline created successfully")
        print(f"   Configuration: {len(pipeline.config.enabled_sources)} sources enabled")
        
        return True
    except Exception as e:
        print(f"❌ Pipeline creation failed: {e}")
        return False

async def test_pipeline_initialization():
    """Test pipeline initialization with all components"""
    print("\n🧪 Testing pipeline initialization...")
    
    try:
        pipeline = DataAcquisitionPipeline()
        
        # Initialize pipeline
        await pipeline.initialize()
        
        print("✅ Pipeline initialized successfully")
        print(f"   Clients initialized: {len(pipeline.clients)}")
        print(f"   Rate limiters: {len(pipeline.rate_limiters)}")
        print(f"   Initialized status: {pipeline.initialized}")
        
        return pipeline
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_pipeline_health_check():
    """Test pipeline health check functionality"""
    print("\n🧪 Testing pipeline health check...")
    
    try:
        pipeline = DataAcquisitionPipeline()
        await pipeline.initialize()
        
        # Get health status
        health_status = await pipeline.health_check()
        
        print("✅ Health check completed successfully")
        print(f"   Pipeline status: {health_status['pipeline_status']}")
        print(f"   Components checked: {len(health_status['components'])}")
        
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

async def test_pipeline_metrics():
    """Test pipeline metrics collection"""
    print("\n🧪 Testing pipeline metrics...")
    
    try:
        pipeline = DataAcquisitionPipeline()
        await pipeline.initialize()
        
        # Get pipeline metrics
        metrics = await pipeline.get_pipeline_metrics()
        
        print("✅ Metrics collection successful")
        print(f"   Total requests: {metrics['pipeline_metrics']['total_requests']}")
        print(f"   Active sources: {len(metrics['active_sources'])}")
        print(f"   Cache performance: {len(metrics['cache_performance'])} metrics")
        
        return True
    except Exception as e:
        print(f"❌ Metrics collection failed: {e}")
        return False

async def test_data_acquisition_mock():
    """Test data acquisition with mock query"""
    print("\n🧪 Testing data acquisition (mock mode)...")
    
    try:
        pipeline = DataAcquisitionPipeline()
        await pipeline.initialize()
        
        # Test with a simple query
        test_query = "artificial intelligence trends"
        
        # Perform data acquisition
        result = await pipeline.acquire_data(
            query=test_query,
            mode=PipelineMode.FAST,  # Use fast mode for testing
            sources=[DataSourceType.GOOGLE_AUTOCOMPLETE]  # Use single source
        )
        
        print("✅ Data acquisition completed")
        print(f"   Query: {result.query}")
        print(f"   Status: {result.status}")
        print(f"   Execution time: {result.execution_time:.2f}s")
        print(f"   Quality score: {result.quality_score:.2f}")
        print(f"   Source results: {len(result.source_results)}")
        
        if result.aggregated_data:
            print(f"   Aggregated suggestions: {len(result.aggregated_data.primary_suggestions)}")
            print(f"   Related questions: {len(result.aggregated_data.related_questions)}")
        
        return True
    except Exception as e:
        print(f"❌ Data acquisition failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_pipeline_configuration():
    """Test custom pipeline configuration"""
    print("\n🧪 Testing custom pipeline configuration...")
    
    try:
        # Create custom configuration
        config = PipelineConfig(
            max_parallel_requests=5,
            request_timeout=5.0,
            total_timeout=15.0,
            enabled_sources=[
                DataSourceType.GOOGLE_AUTOCOMPLETE,
                DataSourceType.SERPAPI_PAA
            ]
        )
        
        pipeline = DataAcquisitionPipeline(config)
        await pipeline.initialize()
        
        print("✅ Custom configuration applied successfully")
        print(f"   Max parallel requests: {config.max_parallel_requests}")
        print(f"   Request timeout: {config.request_timeout}s")
        print(f"   Enabled sources: {len(config.enabled_sources)}")
        
        return True
    except Exception as e:
        print(f"❌ Custom configuration failed: {e}")
        return False

async def test_pipeline_shutdown():
    """Test graceful pipeline shutdown"""
    print("\n🧪 Testing pipeline shutdown...")
    
    try:
        pipeline = DataAcquisitionPipeline()
        await pipeline.initialize()
        
        # Shutdown pipeline
        await pipeline.shutdown()
        
        print("✅ Pipeline shutdown completed successfully")
        print(f"   Initialized status: {pipeline.initialized}")
        
        return True
    except Exception as e:
        print(f"❌ Pipeline shutdown failed: {e}")
        return False

async def run_comprehensive_tests():
    """Run comprehensive pipeline tests"""
    print("🚀 Starting Data Acquisition Pipeline Integration Tests\n")
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_basic_pipeline_creation())
    test_results.append(await test_pipeline_configuration())
    
    pipeline = await test_pipeline_initialization()
    if pipeline:
        test_results.append(True)
        
        test_results.append(await test_pipeline_health_check())
        test_results.append(await test_pipeline_metrics())
        test_results.append(await test_data_acquisition_mock())
        test_results.append(await test_pipeline_shutdown())
    else:
        test_results.extend([False] * 5)
    
    # Summary
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n📊 Test Results Summary:")
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Data acquisition pipeline is ready for integration.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review the issues above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(run_comprehensive_tests())
    exit(0 if success else 1)