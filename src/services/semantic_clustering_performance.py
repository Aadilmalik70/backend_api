"""
Semantic Clustering Performance Optimization and Benchmarking Framework

Advanced performance optimization system for semantic clustering with comprehensive benchmarking,
bottleneck identification, and intelligent configuration recommendations. Targets >85% accuracy
with <2s real-time and <30s batch processing performance.

Features:
- Comprehensive performance profiling and bottleneck detection
- Intelligent configuration optimization for different use cases
- Memory usage optimization and resource management
- Caching strategy optimization and hit rate analysis
- Concurrent processing optimization and thread pool tuning
- Algorithm parameter optimization for accuracy/speed trade-offs
- Real-time monitoring and performance degradation detection
- Automated performance regression testing and alerting

Performance Optimization Areas:
- Embedding generation: Batch processing, model selection, caching
- Clustering algorithms: Parameter tuning, algorithm selection, parallel processing
- Quality assessment: Fast vs comprehensive validation trade-offs
- Pipeline integration: Async optimization, resource sharing
- Memory management: Efficient data structures, garbage collection optimization
- I/O optimization: Async file operations, network request optimization

Target Performance Metrics: <2s real-time, <30s batch, >85% accuracy, <99th percentile latency
"""

import asyncio
import logging
import time
import json
import psutil
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
import numpy as np
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import gc
import warnings
from collections import defaultdict, deque

# Import clustering components for optimization
from .semantic_clustering_service import (
    SemanticClusteringService, ServiceConfig, ClusteringRequest,
    ClusteringMode, get_semantic_clustering_service
)
from .clustering_pipeline_integration import (
    ClusteringPipelineIntegration, ClusteringPipelineConfig,
    get_clustering_pipeline_integration
)
from .clustering_models import ClusteringAlgorithm, SimilarityMetric
from .test_semantic_clustering import SemanticClusteringTestSuite, run_comprehensive_tests

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    
    # Execution time metrics
    total_execution_time: float = 0.0
    embedding_time: float = 0.0
    clustering_time: float = 0.0
    validation_time: float = 0.0
    overhead_time: float = 0.0
    
    # Throughput metrics
    texts_per_second: float = 0.0
    clusters_per_second: float = 0.0
    operations_per_minute: float = 0.0
    
    # Quality metrics
    average_coherence_score: float = 0.0
    accuracy_achievement_rate: float = 0.0
    quality_consistency_score: float = 0.0
    
    # Resource utilization
    peak_memory_mb: float = 0.0
    average_memory_mb: float = 0.0
    cpu_utilization_percent: float = 0.0
    io_wait_time: float = 0.0
    
    # Concurrency metrics
    concurrent_operations: int = 0
    thread_pool_utilization: float = 0.0
    async_task_efficiency: float = 0.0
    
    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_size_mb: float = 0.0
    cache_effectiveness: float = 0.0
    
    # Error and reliability metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    retry_success_rate: float = 0.0
    
    def meets_performance_targets(self) -> bool:
        """Check if metrics meet performance targets"""
        return (
            self.total_execution_time <= 2.0 or  # Real-time target
            (self.total_execution_time <= 30.0 and self.texts_per_second >= 10) and  # Batch target
            self.average_coherence_score >= 0.85 and  # Accuracy target
            self.error_rate <= 0.05  # Reliability target
        )
    
    def get_performance_grade(self) -> str:
        """Get performance grade A-F"""
        if self.meets_performance_targets() and self.average_coherence_score >= 0.90:
            return "A"
        elif self.meets_performance_targets():
            return "B"
        elif self.average_coherence_score >= 0.80 and self.total_execution_time <= 5.0:
            return "C"
        elif self.average_coherence_score >= 0.70:
            return "D"
        else:
            return "F"


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    
    category: str  # embedding, clustering, validation, caching, concurrency
    priority: str  # critical, high, medium, low
    recommendation: str
    expected_improvement: str
    implementation_effort: str  # low, medium, high
    configuration_changes: Dict[str, Any] = field(default_factory=dict)
    code_changes_required: bool = False
    estimated_performance_gain: float = 0.0  # Percentage improvement


@dataclass
class BenchmarkResult:
    """Comprehensive benchmark result"""
    
    benchmark_name: str
    configuration: Dict[str, Any]
    metrics: PerformanceMetrics
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    environment_info: Dict[str, Any] = field(default_factory=dict)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get benchmark summary"""
        return {
            'benchmark_info': {
                'name': self.benchmark_name,
                'timestamp': self.timestamp.isoformat(),
                'performance_grade': self.metrics.get_performance_grade(),
                'meets_targets': self.metrics.meets_performance_targets()
            },
            'performance_summary': {
                'execution_time': f"{self.metrics.total_execution_time:.3f}s",
                'throughput': f"{self.metrics.texts_per_second:.1f} texts/s",
                'accuracy': f"{self.metrics.average_coherence_score:.3f}",
                'memory_usage': f"{self.metrics.peak_memory_mb:.1f}MB",
                'cache_hit_rate': f"{self.metrics.cache_hit_rate:.1%}"
            },
            'optimization_priorities': {
                'critical': len([r for r in self.recommendations if r.priority == 'critical']),
                'high': len([r for r in self.recommendations if r.priority == 'high']),
                'medium': len([r for r in self.recommendations if r.priority == 'medium']),
                'total_recommendations': len(self.recommendations)
            }
        }


class PerformanceProfiler:
    """Advanced performance profiling and monitoring system"""
    
    def __init__(self):
        """Initialize performance profiler"""
        self.logger = logging.getLogger(__name__)
        
        # Profiling state
        self.profiling_active = False
        self.current_profile = {}
        self.profile_stack = []
        
        # Metrics collection
        self.metrics_history = deque(maxlen=1000)
        self.resource_monitor = ResourceMonitor()
        
        # Performance thresholds
        self.thresholds = {
            'real_time_target': 2.0,
            'batch_target': 30.0,
            'accuracy_target': 0.85,
            'memory_limit_mb': 1000,
            'cpu_limit_percent': 80,
            'cache_hit_rate_target': 0.70
        }
    
    async def profile_operation(
        self,
        operation: Callable,
        operation_name: str,
        *args,
        **kwargs
    ) -> Tuple[Any, PerformanceMetrics]:
        """Profile a specific operation with comprehensive metrics"""
        
        # Start profiling
        start_time = time.time()
        start_memory = self.resource_monitor.get_memory_usage()
        start_cpu = self.resource_monitor.get_cpu_usage()
        
        # Execute operation
        try:
            self.logger.debug(f"Starting profiling: {operation_name}")
            
            # Monitor resource usage during execution
            self.resource_monitor.start_monitoring()
            
            result = await operation(*args, **kwargs)
            
            # Stop monitoring
            resource_stats = self.resource_monitor.stop_monitoring()
            
            # Calculate metrics
            execution_time = time.time() - start_time
            end_memory = self.resource_monitor.get_memory_usage()
            
            metrics = PerformanceMetrics(
                total_execution_time=execution_time,
                peak_memory_mb=resource_stats.get('peak_memory_mb', 0),
                average_memory_mb=resource_stats.get('average_memory_mb', 0),
                cpu_utilization_percent=resource_stats.get('average_cpu_percent', 0),
                error_rate=0.0
            )
            
            self.logger.debug(
                f"Profiling complete: {operation_name} "
                f"({execution_time:.3f}s, {metrics.peak_memory_mb:.1f}MB peak)"
            )
            
            return result, metrics
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.resource_monitor.stop_monitoring()
            
            metrics = PerformanceMetrics(
                total_execution_time=execution_time,
                error_rate=1.0
            )
            
            self.logger.error(f"Profiling failed: {operation_name}: {e}")
            
            raise e
    
    def analyze_bottlenecks(self, metrics: PerformanceMetrics) -> List[OptimizationRecommendation]:
        """Analyze performance metrics and identify bottlenecks"""
        
        recommendations = []
        
        # Analyze execution time bottlenecks
        if metrics.total_execution_time > self.thresholds['real_time_target']:
            if metrics.embedding_time > metrics.total_execution_time * 0.4:
                recommendations.append(OptimizationRecommendation(
                    category="embedding",
                    priority="high",
                    recommendation="Optimize embedding generation with batch processing and caching",
                    expected_improvement="30-50% faster embedding generation",
                    implementation_effort="medium",
                    configuration_changes={
                        "enable_embedding_cache": True,
                        "embedding_batch_size": 32,
                        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
                    },
                    estimated_performance_gain=35.0
                ))
            
            if metrics.clustering_time > metrics.total_execution_time * 0.5:
                recommendations.append(OptimizationRecommendation(
                    category="clustering",
                    priority="high",
                    recommendation="Optimize clustering algorithm parameters and enable parallelization",
                    expected_improvement="25-40% faster clustering",
                    implementation_effort="low",
                    configuration_changes={
                        "enable_parallel": True,
                        "n_jobs": -1,
                        "algorithm": "DBSCAN",
                        "eps": 0.4,
                        "min_samples": 3
                    },
                    estimated_performance_gain=30.0
                ))
            
            if metrics.validation_time > metrics.total_execution_time * 0.3:
                recommendations.append(OptimizationRecommendation(
                    category="validation",
                    priority="medium",
                    recommendation="Use fast validation mode for real-time applications",
                    expected_improvement="50-70% faster validation",
                    implementation_effort="low",
                    configuration_changes={
                        "enable_validation": False,
                        "quick_quality_check": True
                    },
                    estimated_performance_gain=60.0
                ))
        
        # Analyze memory bottlenecks
        if metrics.peak_memory_mb > self.thresholds['memory_limit_mb']:
            recommendations.append(OptimizationRecommendation(
                category="memory",
                priority="critical",
                recommendation="Implement memory optimization strategies",
                expected_improvement="40-60% memory reduction",
                implementation_effort="medium",
                configuration_changes={
                    "batch_processing": True,
                    "max_batch_size": 100,
                    "clear_cache_frequently": True
                },
                code_changes_required=True,
                estimated_performance_gain=50.0
            ))
        
        # Analyze cache performance
        if metrics.cache_hit_rate < self.thresholds['cache_hit_rate_target']:
            recommendations.append(OptimizationRecommendation(
                category="caching",
                priority="high",
                recommendation="Optimize caching strategies and increase cache size",
                expected_improvement="20-35% performance improvement through better caching",
                implementation_effort="low",
                configuration_changes={
                    "enable_caching": True,
                    "cache_size": 10000,
                    "cache_ttl_seconds": 7200
                },
                estimated_performance_gain=25.0
            ))
        
        # Analyze accuracy vs speed trade-offs
        if metrics.average_coherence_score < self.thresholds['accuracy_target']:
            recommendations.append(OptimizationRecommendation(
                category="accuracy",
                priority="critical",
                recommendation="Improve clustering accuracy through parameter optimization",
                expected_improvement="10-15% accuracy improvement",
                implementation_effort="medium",
                configuration_changes={
                    "clustering_mode": "DEEP",
                    "enable_validation": True,
                    "cross_validation_folds": 5,
                    "target_accuracy": 0.87
                },
                estimated_performance_gain=12.0
            ))
        
        return recommendations


class ResourceMonitor:
    """System resource monitoring for performance analysis"""
    
    def __init__(self):
        """Initialize resource monitor"""
        self.monitoring = False
        self.metrics = []
        self.monitor_thread = None
        self.monitor_interval = 0.1  # 100ms intervals
    
    def start_monitoring(self):
        """Start resource monitoring"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.metrics = []
        
        def monitor_resources():
            while self.monitoring:
                try:
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    cpu_percent = process.cpu_percent()
                    
                    self.metrics.append({
                        'timestamp': time.time(),
                        'memory_mb': memory_info.rss / 1024 / 1024,
                        'cpu_percent': cpu_percent
                    })
                    
                    time.sleep(self.monitor_interval)
                    
                except Exception:
                    break
        
        self.monitor_thread = threading.Thread(target=monitor_resources, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> Dict[str, float]:
        """Stop monitoring and return statistics"""
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        if not self.metrics:
            return {}
        
        memory_values = [m['memory_mb'] for m in self.metrics]
        cpu_values = [m['cpu_percent'] for m in self.metrics if m['cpu_percent'] > 0]
        
        return {
            'peak_memory_mb': max(memory_values),
            'average_memory_mb': sum(memory_values) / len(memory_values),
            'average_cpu_percent': sum(cpu_values) / len(cpu_values) if cpu_values else 0
        }
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            return psutil.cpu_percent()
        except:
            return 0.0


class SemanticClusteringOptimizer:
    """
    Advanced performance optimizer for semantic clustering system with
    intelligent configuration recommendations and automated benchmarking.
    """
    
    def __init__(self):
        """Initialize semantic clustering optimizer"""
        self.logger = logging.getLogger(__name__)
        
        # Optimization components
        self.profiler = PerformanceProfiler()
        self.test_suite = SemanticClusteringTestSuite()
        
        # Optimization history
        self.benchmark_history = []
        self.optimization_runs = 0
        
        # Configuration templates
        self.config_templates = self._initialize_config_templates()
        
        self.logger.info("Semantic Clustering Optimizer initialized")
    
    def _initialize_config_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize configuration templates for different use cases"""
        return {
            'real_time_optimized': {
                'clustering_mode': ClusteringMode.FAST,
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'enable_validation': False,
                'enable_caching': True,
                'cache_ttl_seconds': 3600,
                'eps': 0.4,
                'min_samples': 3,
                'enable_parallel': True,
                'max_concurrent_operations': 5,
                'timeout_seconds': 5.0
            },
            'accuracy_optimized': {
                'clustering_mode': ClusteringMode.DEEP,
                'embedding_model': 'sentence-transformers/all-mpnet-base-v2',
                'enable_validation': True,
                'cross_validation_folds': 5,
                'target_accuracy': 0.90,
                'eps': 0.25,
                'min_samples': 5,
                'enable_bootstrap_validation': True,
                'timeout_seconds': 60.0
            },
            'balanced_optimized': {
                'clustering_mode': ClusteringMode.STANDARD,
                'embedding_model': 'sentence-transformers/all-MiniLM-L12-v2',
                'enable_validation': True,
                'enable_caching': True,
                'target_accuracy': 0.85,
                'eps': 0.3,
                'min_samples': 5,
                'enable_parallel': True,
                'timeout_seconds': 15.0
            },
            'memory_optimized': {
                'clustering_mode': ClusteringMode.FAST,
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
                'enable_validation': False,
                'batch_processing': True,
                'max_batch_size': 50,
                'enable_caching': False,  # Reduce memory usage
                'clear_embeddings_after_clustering': True,
                'enable_parallel': False  # Reduce memory overhead
            }
        }
    
    async def run_comprehensive_benchmark(
        self,
        test_configurations: Optional[List[str]] = None
    ) -> List[BenchmarkResult]:
        """Run comprehensive performance benchmark"""
        
        if test_configurations is None:
            test_configurations = ['real_time_optimized', 'balanced_optimized', 'accuracy_optimized']
        
        benchmark_results = []
        
        self.logger.info(f"🚀 Starting comprehensive benchmark with {len(test_configurations)} configurations...")
        
        for config_name in test_configurations:
            if config_name not in self.config_templates:
                self.logger.warning(f"Unknown configuration: {config_name}")
                continue
            
            self.logger.info(f"📊 Benchmarking configuration: {config_name}")
            
            try:
                # Run benchmark for this configuration
                result = await self._benchmark_configuration(config_name)
                benchmark_results.append(result)
                
                self.logger.info(
                    f"✅ {config_name} benchmark complete: "
                    f"Grade {result.metrics.get_performance_grade()}, "
                    f"{len(result.recommendations)} recommendations"
                )
                
            except Exception as e:
                self.logger.error(f"❌ Benchmark failed for {config_name}: {e}")
                
                # Create failed benchmark result
                failed_result = BenchmarkResult(
                    benchmark_name=f"{config_name}_failed",
                    configuration=self.config_templates.get(config_name, {}),
                    metrics=PerformanceMetrics(error_rate=1.0),
                    recommendations=[OptimizationRecommendation(
                        category="system",
                        priority="critical",
                        recommendation=f"Fix benchmark execution error: {str(e)}",
                        expected_improvement="Enable benchmark execution",
                        implementation_effort="high"
                    )]
                )
                benchmark_results.append(failed_result)
        
        self.optimization_runs += 1
        self.benchmark_history.extend(benchmark_results)
        
        self.logger.info(
            f"🎯 Comprehensive benchmark complete: {len(benchmark_results)} configurations tested"
        )
        
        return benchmark_results
    
    async def _benchmark_configuration(self, config_name: str) -> BenchmarkResult:
        """Benchmark a specific configuration"""
        
        config_template = self.config_templates[config_name]
        
        # Create test data for benchmarking
        test_texts = self._generate_benchmark_data()
        
        # Initialize metrics
        metrics = PerformanceMetrics()
        
        try:
            # Create service with optimized configuration
            service_config = ServiceConfig(
                max_concurrent_operations=config_template.get('max_concurrent_operations', 5),
                enable_caching=config_template.get('enable_caching', True),
                cache_ttl_seconds=config_template.get('cache_ttl_seconds', 3600),
                target_accuracy=config_template.get('target_accuracy', 0.85)
            )
            
            service = SemanticClusteringService(service_config)
            
            # Profile the clustering operation
            async def clustering_operation():
                return await service.cluster_texts(
                    texts=test_texts,
                    mode=config_template.get('clustering_mode', ClusteringMode.STANDARD),
                    enable_validation=config_template.get('enable_validation', True),
                    target_accuracy=config_template.get('target_accuracy', 0.85),
                    max_processing_time=config_template.get('timeout_seconds', 30.0)
                )
            
            result, profiled_metrics = await self.profiler.profile_operation(
                clustering_operation,
                f"benchmark_{config_name}"
            )
            
            # Extract detailed metrics
            if result and hasattr(result, 'overall_quality'):
                metrics.average_coherence_score = result.overall_quality
                metrics.texts_per_second = len(test_texts) / max(profiled_metrics.total_execution_time, 0.001)
                
                if result.clusters:
                    metrics.clusters_per_second = len(result.clusters) / max(profiled_metrics.total_execution_time, 0.001)
            
            # Combine profiled metrics
            metrics.total_execution_time = profiled_metrics.total_execution_time
            metrics.peak_memory_mb = profiled_metrics.peak_memory_mb
            metrics.average_memory_mb = profiled_metrics.average_memory_mb
            metrics.cpu_utilization_percent = profiled_metrics.cpu_utilization_percent
            metrics.error_rate = 0.0 if result else 1.0
            
            # Get service metrics if available
            try:
                service_metrics = await service.get_service_metrics()
                if 'performance_summary' in service_metrics:
                    perf_summary = service_metrics['performance_summary']
                    metrics.cache_hit_rate = perf_summary.get('cache_hit_rate', 0.0)
                    metrics.accuracy_achievement_rate = perf_summary.get('target_achievement_rate', 0.0)
            except:
                pass
            
        except Exception as e:
            metrics.error_rate = 1.0
            metrics.total_execution_time = 999.0  # High execution time for failure
            self.logger.error(f"Configuration benchmark failed: {e}")
        
        # Generate optimization recommendations
        recommendations = self.profiler.analyze_bottlenecks(metrics)
        
        # Add configuration-specific recommendations
        config_recommendations = self._get_configuration_recommendations(config_name, metrics)
        recommendations.extend(config_recommendations)
        
        return BenchmarkResult(
            benchmark_name=config_name,
            configuration=config_template,
            metrics=metrics,
            recommendations=recommendations,
            environment_info={
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'available_memory_gb': psutil.virtual_memory().total / (1024**3),
                'cpu_count': psutil.cpu_count(),
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def _generate_benchmark_data(self) -> List[str]:
        """Generate diverse benchmark data"""
        benchmark_texts = [
            # Technology cluster
            "Machine learning algorithms for predictive analytics",
            "Deep learning neural networks and AI applications",
            "Natural language processing and text analysis",
            "Computer vision and image recognition systems",
            "Data science methodologies and statistical modeling",
            
            # Business cluster
            "Strategic business planning and market analysis",
            "Customer relationship management and retention",
            "Financial planning and investment strategies",
            "Operations management and process optimization",
            "Supply chain logistics and distribution networks",
            
            # Health cluster
            "Medical research and clinical trial methodologies",
            "Healthcare technology and digital transformation",
            "Patient care protocols and treatment guidelines",
            "Pharmaceutical development and drug discovery",
            "Public health policy and preventive medicine",
            
            # Science cluster
            "Scientific research methodologies and peer review",
            "Laboratory data collection and statistical analysis",
            "Research collaboration and interdisciplinary studies",
            "Grant funding and research proposal development",
            "Scientific publication and knowledge dissemination",
            
            # Mixed/challenging cluster
            "AI applications in medical diagnosis and treatment",
            "Business intelligence using machine learning models",
            "Scientific computing and research data management",
            "Healthcare business models and technology adoption",
            "Data-driven approaches to scientific discovery"
        ]
        
        return benchmark_texts
    
    def _get_configuration_recommendations(
        self,
        config_name: str,
        metrics: PerformanceMetrics
    ) -> List[OptimizationRecommendation]:
        """Get configuration-specific recommendations"""
        
        recommendations = []
        
        if config_name == 'real_time_optimized':
            if metrics.total_execution_time > 2.0:
                recommendations.append(OptimizationRecommendation(
                    category="real_time",
                    priority="high",
                    recommendation="Consider using even faster embedding model or reduce validation",
                    expected_improvement="Achieve <2s real-time target",
                    implementation_effort="low",
                    configuration_changes={
                        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                        "enable_validation": False,
                        "eps": 0.5
                    }
                ))
        
        elif config_name == 'accuracy_optimized':
            if metrics.average_coherence_score < 0.90:
                recommendations.append(OptimizationRecommendation(
                    category="accuracy",
                    priority="high",
                    recommendation="Fine-tune clustering parameters for higher accuracy",
                    expected_improvement="Achieve >90% accuracy target",
                    implementation_effort="medium",
                    configuration_changes={
                        "eps": 0.2,
                        "min_samples": 6,
                        "bootstrap_samples": 200
                    }
                ))
        
        elif config_name == 'memory_optimized':
            if metrics.peak_memory_mb > 500:
                recommendations.append(OptimizationRecommendation(
                    category="memory",
                    priority="critical",
                    recommendation="Implement more aggressive memory optimization",
                    expected_improvement="50% memory reduction",
                    implementation_effort="high",
                    configuration_changes={
                        "max_batch_size": 25,
                        "enable_caching": False,
                        "garbage_collect_frequency": 10
                    },
                    code_changes_required=True
                ))
        
        return recommendations
    
    async def generate_optimization_report(
        self,
        benchmark_results: List[BenchmarkResult]
    ) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        
        if not benchmark_results:
            return {'error': 'No benchmark results available'}
        
        # Analyze results
        best_overall = max(benchmark_results, key=lambda r: (
            r.metrics.get_performance_grade() == 'A',
            r.metrics.meets_performance_targets(),
            r.metrics.average_coherence_score,
            -r.metrics.total_execution_time
        ))
        
        fastest_config = min(benchmark_results, key=lambda r: r.metrics.total_execution_time)
        most_accurate = max(benchmark_results, key=lambda r: r.metrics.average_coherence_score)
        most_efficient = max(benchmark_results, key=lambda r: r.metrics.texts_per_second)
        
        # Collect all recommendations by priority
        all_recommendations = []
        for result in benchmark_results:
            all_recommendations.extend(result.recommendations)
        
        recommendations_by_priority = defaultdict(list)
        for rec in all_recommendations:
            recommendations_by_priority[rec.priority].append(rec)
        
        # Calculate overall system performance
        avg_execution_time = np.mean([r.metrics.total_execution_time for r in benchmark_results])
        avg_accuracy = np.mean([r.metrics.average_coherence_score for r in benchmark_results])
        avg_memory = np.mean([r.metrics.peak_memory_mb for r in benchmark_results])
        
        system_grade = "A" if (
            avg_execution_time <= 2.0 and avg_accuracy >= 0.90
        ) else "B" if (
            avg_execution_time <= 5.0 and avg_accuracy >= 0.85
        ) else "C" if (
            avg_execution_time <= 15.0 and avg_accuracy >= 0.75
        ) else "D" if avg_accuracy >= 0.65 else "F"
        
        return {
            'optimization_report': {
                'report_timestamp': datetime.utcnow().isoformat(),
                'optimization_run': self.optimization_runs,
                'system_performance_grade': system_grade,
                'configurations_tested': len(benchmark_results)
            },
            'performance_summary': {
                'average_execution_time': f"{avg_execution_time:.3f}s",
                'average_accuracy': f"{avg_accuracy:.3f}",
                'average_memory_usage': f"{avg_memory:.1f}MB",
                'meets_real_time_target': avg_execution_time <= 2.0,
                'meets_accuracy_target': avg_accuracy >= 0.85
            },
            'best_configurations': {
                'overall_best': {
                    'name': best_overall.benchmark_name,
                    'grade': best_overall.metrics.get_performance_grade(),
                    'execution_time': f"{best_overall.metrics.total_execution_time:.3f}s",
                    'accuracy': f"{best_overall.metrics.average_coherence_score:.3f}",
                    'memory': f"{best_overall.metrics.peak_memory_mb:.1f}MB"
                },
                'fastest': {
                    'name': fastest_config.benchmark_name,
                    'execution_time': f"{fastest_config.metrics.total_execution_time:.3f}s"
                },
                'most_accurate': {
                    'name': most_accurate.benchmark_name,
                    'accuracy': f"{most_accurate.metrics.average_coherence_score:.3f}"
                },
                'most_efficient': {
                    'name': most_efficient.benchmark_name,
                    'throughput': f"{most_efficient.metrics.texts_per_second:.1f} texts/s"
                }
            },
            'optimization_recommendations': {
                'critical': [
                    {
                        'category': rec.category,
                        'recommendation': rec.recommendation,
                        'expected_improvement': rec.expected_improvement,
                        'implementation_effort': rec.implementation_effort,
                        'configuration_changes': rec.configuration_changes
                    }
                    for rec in recommendations_by_priority['critical'][:5]  # Top 5
                ],
                'high_priority': [
                    {
                        'category': rec.category,
                        'recommendation': rec.recommendation,
                        'expected_improvement': rec.expected_improvement
                    }
                    for rec in recommendations_by_priority['high'][:3]  # Top 3
                ],
                'total_recommendations': len(all_recommendations)
            },
            'configuration_recommendations': {
                'real_time_applications': 'real_time_optimized',
                'accuracy_critical_applications': 'accuracy_optimized',
                'balanced_applications': 'balanced_optimized',
                'memory_constrained_environments': 'memory_optimized'
            },
            'next_steps': [
                "Review and implement critical optimization recommendations",
                "Test the best configuration in your specific environment",
                "Monitor performance metrics in production",
                "Consider implementing gradual optimizations",
                "Run regular performance benchmarks to track improvements"
            ]
        }
    
    async def run_quick_performance_check(self) -> Dict[str, Any]:
        """Run quick performance validation check"""
        
        self.logger.info("🔍 Running quick performance check...")
        
        # Test with single optimized configuration
        try:
            benchmark_results = await self.run_comprehensive_benchmark(['balanced_optimized'])
            
            if benchmark_results:
                result = benchmark_results[0]
                
                return {
                    'quick_performance_check': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'configuration': result.benchmark_name,
                        'performance_grade': result.metrics.get_performance_grade(),
                        'meets_targets': result.metrics.meets_performance_targets(),
                        'execution_time': f"{result.metrics.total_execution_time:.3f}s",
                        'accuracy': f"{result.metrics.average_coherence_score:.3f}",
                        'memory_usage': f"{result.metrics.peak_memory_mb:.1f}MB",
                        'recommendations_count': len(result.recommendations),
                        'status': 'healthy' if result.metrics.meets_performance_targets() else 'needs_optimization'
                    }
                }
            else:
                return {
                    'quick_performance_check': {
                        'timestamp': datetime.utcnow().isoformat(),
                        'status': 'failed',
                        'error': 'No benchmark results available'
                    }
                }
                
        except Exception as e:
            return {
                'quick_performance_check': {
                    'timestamp': datetime.utcnow().isoformat(),
                    'status': 'error',
                    'error': str(e)
                }
            }
    
    def get_optimization_history(self) -> Dict[str, Any]:
        """Get optimization history and trends"""
        
        if not self.benchmark_history:
            return {'message': 'No optimization history available'}
        
        # Group by configuration
        history_by_config = defaultdict(list)
        for result in self.benchmark_history:
            history_by_config[result.benchmark_name].append(result)
        
        # Calculate trends
        trends = {}
        for config_name, results in history_by_config.items():
            if len(results) >= 2:
                execution_times = [r.metrics.total_execution_time for r in results]
                accuracy_scores = [r.metrics.average_coherence_score for r in results]
                
                trends[config_name] = {
                    'execution_time_trend': 'improving' if execution_times[-1] < execution_times[0] else 'declining',
                    'accuracy_trend': 'improving' if accuracy_scores[-1] > accuracy_scores[0] else 'declining',
                    'total_runs': len(results)
                }
        
        return {
            'optimization_history': {
                'total_optimization_runs': self.optimization_runs,
                'total_benchmarks': len(self.benchmark_history),
                'configurations_tested': len(history_by_config),
                'performance_trends': trends
            }
        }


# Utility functions
async def run_performance_optimization() -> Dict[str, Any]:
    """Run complete performance optimization analysis"""
    optimizer = SemanticClusteringOptimizer()
    
    # Run comprehensive benchmark
    benchmark_results = await optimizer.run_comprehensive_benchmark()
    
    # Generate optimization report
    report = await optimizer.generate_optimization_report(benchmark_results)
    
    return report


async def run_quick_performance_validation() -> Dict[str, Any]:
    """Run quick performance validation"""
    optimizer = SemanticClusteringOptimizer()
    return await optimizer.run_quick_performance_check()


if __name__ == "__main__":
    async def main():
        """Run performance optimization if executed directly"""
        print("🚀 Starting Semantic Clustering Performance Optimization...")
        
        try:
            report = await run_performance_optimization()
            
            print("\n" + "="*80)
            print("SEMANTIC CLUSTERING PERFORMANCE OPTIMIZATION REPORT")
            print("="*80)
            
            # Print report summary
            opt_report = report.get('optimization_report', {})
            print(f"\n📊 Optimization Summary:")
            print(f"   System Performance Grade: {opt_report.get('system_performance_grade', 'Unknown')}")
            print(f"   Configurations Tested: {opt_report.get('configurations_tested', 0)}")
            
            # Print performance summary
            perf_summary = report.get('performance_summary', {})
            print(f"\n⚡ Performance Summary:")
            print(f"   Average Execution Time: {perf_summary.get('average_execution_time', 'N/A')}")
            print(f"   Average Accuracy: {perf_summary.get('average_accuracy', 'N/A')}")
            print(f"   Average Memory Usage: {perf_summary.get('average_memory_usage', 'N/A')}")
            print(f"   Meets Real-time Target: {'✅' if perf_summary.get('meets_real_time_target') else '❌'}")
            print(f"   Meets Accuracy Target: {'✅' if perf_summary.get('meets_accuracy_target') else '❌'}")
            
            # Print best configurations
            best_configs = report.get('best_configurations', {})
            print(f"\n🎯 Best Configurations:")
            for config_type, config_info in best_configs.items():
                print(f"   {config_type.replace('_', ' ').title()}: {config_info.get('name', 'N/A')}")
            
            # Print optimization recommendations
            opt_recs = report.get('optimization_recommendations', {})
            critical_count = len(opt_recs.get('critical', []))
            high_count = len(opt_recs.get('high_priority', []))
            
            print(f"\n🔧 Optimization Recommendations:")
            print(f"   Critical: {critical_count}")
            print(f"   High Priority: {high_count}")
            print(f"   Total: {opt_recs.get('total_recommendations', 0)}")
            
            if critical_count > 0:
                print(f"\n   Top Critical Recommendations:")
                for i, rec in enumerate(opt_recs.get('critical', [])[:3], 1):
                    print(f"   {i}. {rec.get('recommendation', 'N/A')}")
                    print(f"      Expected: {rec.get('expected_improvement', 'N/A')}")
            
            # Print configuration recommendations
            config_recs = report.get('configuration_recommendations', {})
            print(f"\n📋 Configuration Recommendations:")
            for use_case, config in config_recs.items():
                print(f"   {use_case.replace('_', ' ').title()}: {config}")
            
            print(f"\n{'='*80}")
            print(f"✅ Performance Optimization Complete!")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"❌ Performance optimization failed: {e}")
    
    asyncio.run(main())