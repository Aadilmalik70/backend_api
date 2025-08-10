#!/usr/bin/env python3
"""
Performance Benchmarking and Optimization for Semantic Clustering System

Comprehensive performance testing to validate clustering system meets requirements:
- <2s for real-time clustering
- <30s for batch clustering  
- >85% accuracy target
- Quality validation and metrics
"""

import asyncio
import time
import sys
import os
import json
import random
from typing import List, Dict, Any

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Sample data for testing
SAMPLE_TEXTS = [
    # Technology cluster
    "machine learning algorithms and neural networks",
    "artificial intelligence and deep learning models", 
    "data science and statistical analysis",
    "computer vision and image recognition",
    "natural language processing and text analysis",
    
    # Business cluster
    "business strategy and market analysis",
    "financial planning and investment strategies",
    "marketing campaigns and customer engagement",
    "sales optimization and revenue growth",
    "project management and team coordination",
    
    # Health cluster
    "healthcare technology and medical devices",
    "pharmaceutical research and drug development", 
    "clinical trials and patient care",
    "medical diagnosis and treatment planning",
    "wellness programs and preventive care",
    
    # Education cluster
    "online learning and educational platforms",
    "curriculum development and instructional design",
    "student assessment and academic performance",
    "educational technology and digital tools",
    "teacher training and professional development"
]

class PerformanceBenchmark:
    """Comprehensive performance benchmark for clustering system"""
    
    def __init__(self):
        self.results = {
            'embedding_performance': {},
            'clustering_performance': {},
            'accuracy_validation': {},
            'system_metrics': {},
            'overall_assessment': {}
        }
        
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run complete performance benchmark suite"""
        
        print("=== SEMANTIC CLUSTERING PERFORMANCE BENCHMARK ===")
        print()
        
        # Test 1: Embeddings Performance
        print("1. Testing Embeddings Performance...")
        await self._benchmark_embeddings()
        
        # Test 2: Clustering Performance  
        print("2. Testing Clustering Performance...")
        await self._benchmark_clustering()
        
        # Test 3: Accuracy Validation
        print("3. Testing Clustering Accuracy...")
        await self._benchmark_accuracy()
        
        # Test 4: System Metrics
        print("4. Collecting System Metrics...")
        await self._collect_system_metrics()
        
        # Test 5: Overall Assessment
        print("5. Generating Overall Assessment...")
        self._generate_assessment()
        
        return self.results
    
    async def _benchmark_embeddings(self):
        """Benchmark embedding generation performance"""
        try:
            from services.semantic_embeddings_service import SemanticEmbeddingsService, EmbeddingsConfig
            
            config = EmbeddingsConfig(
                batch_size=16,
                enable_caching=False,
                max_concurrent_requests=4
            )
            
            service = SemanticEmbeddingsService(config)
            await service.initialize()
            
            # Test 1: Small batch (real-time scenario)
            small_batch = SAMPLE_TEXTS[:5]
            start_time = time.time()
            result = await service.generate_embeddings(small_batch)
            small_batch_time = time.time() - start_time
            
            # Test 2: Medium batch
            medium_batch = SAMPLE_TEXTS[:15]
            start_time = time.time()
            result = await service.generate_embeddings(medium_batch)
            medium_batch_time = time.time() - start_time
            
            # Test 3: Large batch (batch scenario)
            large_batch = SAMPLE_TEXTS * 4  # 80 texts
            start_time = time.time()
            result = await service.generate_embeddings(large_batch)
            large_batch_time = time.time() - start_time
            
            self.results['embedding_performance'] = {
                'small_batch': {
                    'texts': len(small_batch),
                    'time': f"{small_batch_time:.3f}s",
                    'texts_per_second': len(small_batch) / small_batch_time,
                    'meets_realtime_target': small_batch_time < 2.0
                },
                'medium_batch': {
                    'texts': len(medium_batch),
                    'time': f"{medium_batch_time:.3f}s", 
                    'texts_per_second': len(medium_batch) / medium_batch_time
                },
                'large_batch': {
                    'texts': len(large_batch),
                    'time': f"{large_batch_time:.3f}s",
                    'texts_per_second': len(large_batch) / large_batch_time,
                    'meets_batch_target': large_batch_time < 30.0
                }
            }
            
            print(f"   Small batch ({len(small_batch)} texts): {small_batch_time:.3f}s")
            print(f"   Medium batch ({len(medium_batch)} texts): {medium_batch_time:.3f}s")  
            print(f"   Large batch ({len(large_batch)} texts): {large_batch_time:.3f}s")
            
        except Exception as e:
            print(f"   [ERROR] Embeddings benchmark failed: {e}")
            self.results['embedding_performance'] = {'error': str(e)}
    
    async def _benchmark_clustering(self):
        """Benchmark clustering performance"""
        try:
            from services.semantic_clustering_service import (
                SemanticClusteringService, ServiceConfig, ClusteringMode
            )
            
            config = ServiceConfig(
                target_accuracy=0.85,
                enable_caching=False,
                fast_mode_timeout=5.0
            )
            
            service = SemanticClusteringService(config)
            await service.initialize()
            
            # Test 1: Fast mode (real-time)
            start_time = time.time()
            result = await service.cluster_texts(
                texts=SAMPLE_TEXTS[:10],
                mode=ClusteringMode.FAST,
                enable_validation=False
            )
            fast_mode_time = time.time() - start_time
            
            # Test 2: Standard mode
            start_time = time.time()
            result = await service.cluster_texts(
                texts=SAMPLE_TEXTS,
                mode=ClusteringMode.STANDARD,
                enable_validation=True
            )
            standard_mode_time = time.time() - start_time
            
            # Test 3: Deep mode (comprehensive)
            start_time = time.time()
            result = await service.cluster_texts(
                texts=SAMPLE_TEXTS,
                mode=ClusteringMode.DEEP,
                enable_validation=True
            )
            deep_mode_time = time.time() - start_time
            
            self.results['clustering_performance'] = {
                'fast_mode': {
                    'texts': 10,
                    'time': f"{fast_mode_time:.3f}s",
                    'meets_realtime_target': fast_mode_time < 2.0,
                    'clusters_created': result.total_clusters if result else 0
                },
                'standard_mode': {
                    'texts': len(SAMPLE_TEXTS),
                    'time': f"{standard_mode_time:.3f}s",
                    'clusters_created': result.total_clusters if result else 0
                },
                'deep_mode': {
                    'texts': len(SAMPLE_TEXTS),
                    'time': f"{deep_mode_time:.3f}s",
                    'meets_batch_target': deep_mode_time < 30.0,
                    'clusters_created': result.total_clusters if result else 0
                }
            }
            
            print(f"   Fast mode (10 texts): {fast_mode_time:.3f}s")
            print(f"   Standard mode ({len(SAMPLE_TEXTS)} texts): {standard_mode_time:.3f}s")
            print(f"   Deep mode ({len(SAMPLE_TEXTS)} texts): {deep_mode_time:.3f}s")
            
        except Exception as e:
            print(f"   [ERROR] Clustering benchmark failed: {e}")
            self.results['clustering_performance'] = {'error': str(e)}
    
    async def _benchmark_accuracy(self):
        """Benchmark clustering accuracy using coherence scoring"""
        try:
            from services.semantic_clustering_service import (
                SemanticClusteringService, ServiceConfig, ClusteringMode
            )
            
            config = ServiceConfig(target_accuracy=0.85)
            service = SemanticClusteringService(config)
            await service.initialize()
            
            # Run clustering with validation
            result = await service.cluster_texts(
                texts=SAMPLE_TEXTS,
                mode=ClusteringMode.STANDARD,
                enable_validation=True
            )
            
            if result and result.coherence_report:
                report = result.coherence_report
                
                self.results['accuracy_validation'] = {
                    'overall_coherence': f"{report.overall_coherence:.3f}",
                    'accuracy_grade': report.get_grade(),
                    'meets_target': report.meets_target,
                    'silhouette_score': f"{report.silhouette_score:.3f}",
                    'semantic_coherence': f"{report.semantic_coherence:.3f}",
                    'stability_score': f"{report.stability_score:.3f}",
                    'clusters_created': result.total_clusters,
                    'quality_distribution': report.cluster_quality_distribution,
                    'recommendations': len(report.improvement_recommendations)
                }
                
                print(f"   Overall coherence: {report.overall_coherence:.3f} (Grade: {report.get_grade()})")
                print(f"   Meets 85% target: {report.meets_target}")
                print(f"   Clusters created: {result.total_clusters}")
                
            else:
                print("   [WARNING] No coherence report available")
                self.results['accuracy_validation'] = {'error': 'No coherence report'}
                
        except Exception as e:
            print(f"   [ERROR] Accuracy benchmark failed: {e}")
            self.results['accuracy_validation'] = {'error': str(e)}
    
    async def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            from services.semantic_clustering_service import get_semantic_clustering_service
            from services.semantic_embeddings_service import get_embeddings_service
            
            # Get clustering service metrics
            clustering_service = await get_semantic_clustering_service()
            clustering_metrics = await clustering_service.get_service_metrics()
            
            # Get embeddings service metrics
            embeddings_service = await get_embeddings_service()
            embeddings_metrics = await embeddings_service.get_metrics()
            
            self.results['system_metrics'] = {
                'clustering_service': {
                    'total_operations': clustering_metrics.get('service_metrics', {}).get('total_operations', 0),
                    'successful_operations': clustering_metrics.get('service_metrics', {}).get('successful_operations', 0),
                    'average_processing_time': clustering_metrics.get('performance_summary', {}).get('average_processing_time', 0),
                    'system_status': clustering_metrics.get('system_status', {})
                },
                'embeddings_service': {
                    'total_requests': embeddings_metrics.get('service_metrics', {}).get('total_requests', 0),
                    'successful_requests': embeddings_metrics.get('service_metrics', {}).get('successful_requests', 0),
                    'cache_performance': embeddings_metrics.get('cache_performance', {}),
                    'system_status': embeddings_metrics.get('system_status', {})
                }
            }
            
            print("   System metrics collected successfully")
            
        except Exception as e:
            print(f"   [ERROR] System metrics collection failed: {e}")
            self.results['system_metrics'] = {'error': str(e)}
    
    def _generate_assessment(self):
        """Generate overall performance assessment"""
        
        # Check performance targets
        embedding_perf = self.results.get('embedding_performance', {})
        clustering_perf = self.results.get('clustering_performance', {})
        accuracy = self.results.get('accuracy_validation', {})
        
        realtime_target_met = (
            embedding_perf.get('small_batch', {}).get('meets_realtime_target', False) and
            clustering_perf.get('fast_mode', {}).get('meets_realtime_target', False)
        )
        
        batch_target_met = (
            embedding_perf.get('large_batch', {}).get('meets_batch_target', False) and
            clustering_perf.get('deep_mode', {}).get('meets_batch_target', False)
        )
        
        accuracy_target_met = accuracy.get('meets_target', False)
        
        # Overall grade
        if realtime_target_met and batch_target_met and accuracy_target_met:
            grade = "A"
            status = "EXCELLENT"
        elif (realtime_target_met or batch_target_met) and accuracy_target_met:
            grade = "B" 
            status = "GOOD"
        elif accuracy_target_met:
            grade = "C"
            status = "ACCEPTABLE"
        else:
            grade = "F"
            status = "NEEDS_IMPROVEMENT"
        
        self.results['overall_assessment'] = {
            'grade': grade,
            'status': status,
            'realtime_performance': realtime_target_met,
            'batch_performance': batch_target_met,
            'accuracy_target': accuracy_target_met,
            'ready_for_production': grade in ["A", "B"]
        }
        
        print(f"   Overall Grade: {grade} ({status})")
        print(f"   Production Ready: {grade in ['A', 'B']}")

async def main():
    """Main benchmark execution"""
    print("Starting Semantic Clustering Performance Benchmark...\n")
    
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_comprehensive_benchmark()
    
    print("\n=== BENCHMARK RESULTS ===")
    print(json.dumps(results, indent=2, default=str))
    
    return results

if __name__ == "__main__":
    asyncio.run(main())