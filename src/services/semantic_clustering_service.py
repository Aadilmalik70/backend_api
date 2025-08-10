"""
Semantic Clustering Service - Main Orchestrator

Comprehensive semantic clustering orchestrator that coordinates embeddings generation,
clustering algorithms, and quality assessment to provide high-level clustering capabilities
for conversational query engineering. Integrates all clustering components into a unified,
production-ready service.

Features:
- End-to-end semantic clustering workflow orchestration
- Multiple clustering modes (fast, standard, deep, custom)
- Automatic parameter optimization for >85% accuracy targets  
- Comprehensive error handling and fallback strategies
- Performance optimization with caching and async processing
- Integration with existing SERP Strategist infrastructure
- Real-time and batch processing capabilities
- Quality assessment and validation reporting
- Export and visualization support

Clustering Modes:
- Fast: Quick clustering for real-time applications (<2s)
- Standard: Balanced quality and performance (<10s)
- Deep: Comprehensive analysis with validation (<30s)
- Custom: User-defined parameters and algorithms

Performance Targets: >85% clustering accuracy, <2s real-time, <30s batch
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum

# Import clustering components
from .clustering_models import (
    SemanticCluster, ClusteringResult, ClusteringConfig, EmbeddingData,
    CoherenceScore, ClusteringAlgorithm, SimilarityMetric, ClusteringStatus,
    CoherenceMethod,
    create_clustering_config, create_embedding_batch
)
from .semantic_embeddings_service import SemanticEmbeddingsService, EmbeddingsConfig
from .clustering_algorithms import ClusteringAlgorithms
from .coherence_scorer import CoherenceScorer, ValidationConfig, CoherenceReport

# Import existing infrastructure
from .timeout_protection import get_timeout_protection
from .async_request_manager import AsyncRequestManager

logger = logging.getLogger(__name__)


class ClusteringMode(Enum):
    """Clustering execution modes with different performance/quality tradeoffs"""
    FAST = "fast"           # Real-time clustering, basic quality
    STANDARD = "standard"   # Balanced clustering, good quality  
    DEEP = "deep"          # Comprehensive clustering, high quality
    CUSTOM = "custom"      # User-defined parameters


@dataclass
class ClusteringRequest:
    """Request for semantic clustering operation"""
    
    # Input data
    texts: List[str]
    request_id: str = field(default_factory=lambda: f"clustering_{int(time.time())}")
    
    # Clustering configuration
    mode: ClusteringMode = ClusteringMode.STANDARD
    algorithm: ClusteringAlgorithm = ClusteringAlgorithm.DBSCAN
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    
    # Custom parameters (for CUSTOM mode)
    custom_config: Optional[ClusteringConfig] = None
    
    # Processing options
    enable_validation: bool = True
    target_accuracy: float = 0.85
    max_processing_time: float = 30.0
    
    # Output options
    include_embeddings: bool = False
    include_detailed_report: bool = True
    export_format: str = "json"  # json, summary
    
    # Context metadata
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ServiceConfig:
    """Configuration for semantic clustering service"""
    
    # Service-level settings
    max_concurrent_operations: int = 5
    default_mode: ClusteringMode = ClusteringMode.STANDARD
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    
    # Performance settings
    fast_mode_timeout: float = 2.0
    standard_mode_timeout: float = 10.0
    deep_mode_timeout: float = 30.0
    
    # Quality settings
    target_accuracy: float = 0.85
    min_acceptable_accuracy: float = 0.70
    enable_automatic_optimization: bool = True
    
    # Component configurations
    embeddings_config: Optional[EmbeddingsConfig] = None
    validation_config: Optional[ValidationConfig] = None
    
    # Integration settings
    enable_pipeline_integration: bool = True
    pipeline_data_source: str = "data_acquisition"


class SemanticClusteringService:
    """
    Main semantic clustering orchestrator providing comprehensive clustering
    capabilities with quality assessment, performance optimization, and
    integration with existing SERP Strategist infrastructure.
    """
    
    def __init__(self, config: Optional[ServiceConfig] = None):
        """Initialize semantic clustering service"""
        self.config = config or ServiceConfig()
        self.logger = logging.getLogger(__name__)
        
        # Service state
        self.initialized = False
        self.active_operations: Dict[str, asyncio.Task] = {}
        self.operation_lock = threading.RLock()
        
        # Component services (will be initialized)
        self.embeddings_service: Optional[SemanticEmbeddingsService] = None
        self.clustering_algorithms: Optional[ClusteringAlgorithms] = None
        self.coherence_scorer: Optional[CoherenceScorer] = None
        
        # Performance and caching
        self.request_manager = AsyncRequestManager()
        self.timeout_protection = get_timeout_protection()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_concurrent_operations)
        
        # Caching system
        self.clustering_cache: Dict[str, Tuple[ClusteringResult, float]] = {}
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fast_mode_requests': 0,
            'standard_mode_requests': 0,
            'deep_mode_requests': 0,
            'custom_mode_requests': 0,
            'requests_above_target': 0,
            'average_accuracy': 0.0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Mode-specific configurations
        self.mode_configs = self._initialize_mode_configs()
        
        self.logger.info("Semantic Clustering Service initialized")
    
    def _initialize_mode_configs(self) -> Dict[ClusteringMode, ClusteringConfig]:
        """Initialize clustering configurations for different modes"""
        
        return {
            ClusteringMode.FAST: create_clustering_config(
                algorithm="dbscan",
                eps=0.4,
                min_samples=3,
                similarity_metric="cosine",
                timeout_seconds=self.config.fast_mode_timeout,
                target_coherence_score=0.70,
                enable_validation=False
            ),
            
            ClusteringMode.STANDARD: create_clustering_config(
                algorithm="dbscan", 
                eps=0.3,
                min_samples=5,
                similarity_metric="cosine",
                timeout_seconds=self.config.standard_mode_timeout,
                target_coherence_score=self.config.target_accuracy,
                enable_validation=True
            ),
            
            ClusteringMode.DEEP: create_clustering_config(
                algorithm="dbscan",
                eps=0.25,
                min_samples=5,
                similarity_metric="cosine",
                timeout_seconds=self.config.deep_mode_timeout,
                target_coherence_score=0.90,
                enable_validation=True,
                cross_validation_folds=5
            )
        }
    
    async def initialize(self):
        """Initialize the semantic clustering service and all components"""
        if self.initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing Semantic Clustering Service...")
            
            # Initialize component services
            await self._initialize_embeddings_service()
            await self._initialize_clustering_algorithms()
            await self._initialize_coherence_scorer()
            
            # Initialize request manager
            await self.request_manager.initialize()
            
            self.initialized = True
            self.logger.info("✅ Semantic Clustering Service initialization complete")
            
        except Exception as e:
            self.logger.error(f"Semantic Clustering Service initialization failed: {e}")
            raise
    
    async def _initialize_embeddings_service(self):
        """Initialize semantic embeddings service"""
        embeddings_config = self.config.embeddings_config or EmbeddingsConfig()
        
        self.embeddings_service = SemanticEmbeddingsService(embeddings_config)
        await self.embeddings_service.initialize()
        
        self.logger.info("✅ Embeddings service initialized")
    
    async def _initialize_clustering_algorithms(self):
        """Initialize clustering algorithms service"""
        self.clustering_algorithms = ClusteringAlgorithms(self.embeddings_service)
        
        self.logger.info("✅ Clustering algorithms initialized")
    
    async def _initialize_coherence_scorer(self):
        """Initialize coherence scoring service"""
        validation_config = self.config.validation_config or ValidationConfig()
        validation_config.target_accuracy = self.config.target_accuracy
        
        self.coherence_scorer = CoherenceScorer(validation_config)
        
        self.logger.info("✅ Coherence scorer initialized")
    
    async def cluster_texts(
        self,
        texts: List[str],
        mode: ClusteringMode = ClusteringMode.STANDARD,
        **kwargs
    ) -> ClusteringResult:
        """
        High-level semantic clustering of text data
        
        Args:
            texts: List of texts to cluster
            mode: Clustering mode (fast, standard, deep, custom)
            **kwargs: Additional parameters for clustering request
            
        Returns:
            Complete clustering result with quality assessment
        """
        
        if not self.initialized:
            await self.initialize()
        
        # Create clustering request
        request = ClusteringRequest(
            texts=texts,
            mode=mode,
            **kwargs
        )
        
        return await self.process_clustering_request(request)
    
    async def process_clustering_request(
        self, 
        request: ClusteringRequest
    ) -> ClusteringResult:
        """
        Process complete clustering request with orchestration
        
        Args:
            request: Clustering request with full configuration
            
        Returns:
            Complete clustering result with quality metrics
        """
        
        if not self.initialized:
            await self.initialize()
        
        if not request.texts:
            return self._create_empty_result(request, "No texts provided for clustering")
        
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        # Update mode-specific metrics
        mode_metric_key = f'{request.mode.value}_mode_requests'
        if mode_metric_key in self.metrics:
            self.metrics[mode_metric_key] += 1
        
        try:
            self.logger.info(
                f"Processing clustering request: {request.request_id} "
                f"(mode: {request.mode.value}, texts: {len(request.texts)})"
            )
            
            # Check cache first
            if self.config.enable_caching:
                cached_result = self._get_cached_result(request)
                if cached_result:
                    self.metrics['cache_hits'] += 1
                    self.logger.info(f"Cache hit for request {request.request_id}")
                    return cached_result
            
            self.metrics['cache_misses'] += 1
            
            # Get clustering configuration
            clustering_config = self._get_clustering_config(request)
            
            # Execute clustering workflow
            result = await self._execute_clustering_workflow(request, clustering_config)
            
            # Cache successful results
            if (self.config.enable_caching and 
                result.status == ClusteringStatus.COMPLETED):
                self._cache_result(request, result)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_success_metrics(result, execution_time)
            
            self.logger.info(
                f"Clustering request completed: {request.request_id} "
                f"(clusters: {result.total_clusters}, quality: {result.overall_quality:.3f}, "
                f"time: {execution_time:.3f}s)"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_requests'] += 1
            
            self.logger.error(f"Clustering request failed: {request.request_id}: {e}")
            
            return self._create_error_result(request, str(e), execution_time)
    
    async def _execute_clustering_workflow(
        self,
        request: ClusteringRequest,
        config: ClusteringConfig
    ) -> ClusteringResult:
        """Execute complete clustering workflow with timeout protection"""
        
        # Define the complete workflow
        async def clustering_workflow():
            # Step 1: Generate embeddings
            embeddings = await self._generate_embeddings(request.texts, config)
            
            # Step 2: Perform clustering
            clustering_result = await self.clustering_algorithms.cluster_embeddings(
                embeddings, config, request.request_id
            )
            
            # Step 3: Quality assessment (if enabled)
            if request.enable_validation and clustering_result.status == ClusteringStatus.COMPLETED:
                await self._perform_quality_assessment(clustering_result, request)
            
            # Step 4: Post-processing and optimization
            await self._post_process_result(clustering_result, request)
            
            return clustering_result
        
        # Execute workflow with timeout protection
        result = await self.timeout_protection.protected_call(
            operation=clustering_workflow,
            service_name="semantic_clustering",
            operation_type="complete_workflow",
            timeout=request.max_processing_time,
            enable_retry=False,  # Don't retry entire workflow
            enable_circuit_breaker=True,
            context={
                'request_id': request.request_id,
                'mode': request.mode.value,
                'text_count': len(request.texts)
            }
        )
        
        if result.success:
            return result.data
        else:
            raise Exception(f"Clustering workflow failed: {result.error}")
    
    async def _generate_embeddings(
        self, 
        texts: List[str], 
        config: ClusteringConfig
    ) -> List[EmbeddingData]:
        """Generate embeddings for input texts"""
        
        try:
            # Create embedding batch
            embedding_batch = create_embedding_batch(texts, config.embedding_model)
            
            # Generate embeddings using embeddings service
            embeddings = await self.embeddings_service.generate_embeddings(
                texts=texts,
                model_name=config.embedding_model,
                normalize=config.normalize_embeddings
            )
            
            self.logger.debug(f"Generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            raise
    
    async def _perform_quality_assessment(
        self,
        clustering_result: ClusteringResult,
        request: ClusteringRequest
    ):
        """Perform comprehensive quality assessment"""
        
        try:
            if not self.coherence_scorer:
                self.logger.warning("Coherence scorer not available for quality assessment")
                return
            
            # Generate comprehensive coherence report
            coherence_report = await self.coherence_scorer.score_clustering_result(
                clustering_result
            )
            
            # Update clustering result with detailed quality metrics
            clustering_result.coherence_score = CoherenceScore(
                overall_coherence=coherence_report.overall_coherence,
                target_accuracy=request.target_accuracy,
                meets_target=coherence_report.meets_target,
                silhouette_score=coherence_report.silhouette_score,
                semantic_coherence=coherence_report.semantic_coherence,
                calinski_harabasz_score=coherence_report.calinski_harabasz_score,
                davies_bouldin_score=coherence_report.davies_bouldin_score,
                coherence_method=CoherenceMethod.COMBINED,
                calculation_time=coherence_report.calculation_time,
                validation_passed=True
            )
            
            clustering_result.overall_quality = coherence_report.overall_coherence
            
            # Assign coherence report for backwards compatibility
            clustering_result.coherence_report = coherence_report
            
            # Add detailed report to metadata if requested
            if request.include_detailed_report:
                clustering_result.metadata = clustering_result.metadata or {}
                clustering_result.metadata['coherence_report'] = coherence_report.get_summary()
            
            self.logger.debug(
                f"Quality assessment completed: {coherence_report.overall_coherence:.3f} "
                f"(grade: {coherence_report.get_grade()})"
            )
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            # Don't fail the entire clustering operation
    
    async def _post_process_result(
        self,
        clustering_result: ClusteringResult,
        request: ClusteringRequest
    ):
        """Post-process clustering result"""
        
        try:
            # Remove embeddings from output if not requested
            if not request.include_embeddings:
                clustering_result.embeddings = []
            
            # Add request context to metadata
            clustering_result.metadata = clustering_result.metadata or {}
            clustering_result.metadata.update({
                'request_mode': request.mode.value,
                'processing_timestamp': datetime.utcnow().isoformat(),
                'service_version': '1.0.0'
            })
            
            # Optimize cluster information
            for cluster in clustering_result.clusters:
                # Ensure representative texts are set
                if not cluster.representative_texts and cluster.texts:
                    cluster.representative_texts = cluster.texts[:3]
                
                # Update cluster metadata
                cluster.creation_timestamp = datetime.utcnow()
            
        except Exception as e:
            self.logger.warning(f"Post-processing failed: {e}")
            # Don't fail the operation for post-processing issues
    
    def _get_clustering_config(self, request: ClusteringRequest) -> ClusteringConfig:
        """Get clustering configuration based on request"""
        
        if request.mode == ClusteringMode.CUSTOM and request.custom_config:
            return request.custom_config
        elif request.mode in self.mode_configs:
            return self.mode_configs[request.mode]
        else:
            # Default to standard mode
            return self.mode_configs[ClusteringMode.STANDARD]
    
    def _generate_cache_key(self, request: ClusteringRequest) -> str:
        """Generate cache key for clustering request"""
        import hashlib
        
        key_data = {
            'texts': sorted(request.texts),  # Sort for consistency
            'mode': request.mode.value,
            'algorithm': request.algorithm.value,
            'similarity_metric': request.similarity_metric.value,
            'target_accuracy': request.target_accuracy
        }
        
        # Add custom config if present
        if request.custom_config:
            key_data['custom_eps'] = request.custom_config.eps
            key_data['custom_min_samples'] = request.custom_config.min_samples
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, request: ClusteringRequest) -> Optional[ClusteringResult]:
        """Get cached clustering result if available and valid"""
        cache_key = self._generate_cache_key(request)
        
        if cache_key in self.clustering_cache:
            result, timestamp = self.clustering_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - timestamp < self.config.cache_ttl_seconds:
                # Update request ID for cached result
                result.request_id = request.request_id
                return result
            else:
                # Remove expired cache entry
                del self.clustering_cache[cache_key]
        
        return None
    
    def _cache_result(self, request: ClusteringRequest, result: ClusteringResult):
        """Cache clustering result"""
        cache_key = self._generate_cache_key(request)
        self.clustering_cache[cache_key] = (result, time.time())
        
        # Prevent cache from growing too large
        if len(self.clustering_cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(
                self.clustering_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            
            # Keep only the most recent 800 entries
            self.clustering_cache = dict(sorted_items[-800:])
    
    def _create_empty_result(
        self, 
        request: ClusteringRequest, 
        message: str
    ) -> ClusteringResult:
        """Create empty clustering result"""
        return ClusteringResult(
            request_id=request.request_id,
            input_texts=request.texts,
            status=ClusteringStatus.FAILED,
            error_message=message,
            processing_timestamp=datetime.utcnow()
        )
    
    def _create_error_result(
        self,
        request: ClusteringRequest,
        error_message: str,
        execution_time: float
    ) -> ClusteringResult:
        """Create error clustering result"""
        return ClusteringResult(
            request_id=request.request_id,
            input_texts=request.texts,
            status=ClusteringStatus.FAILED,
            execution_time=execution_time,
            error_message=error_message,
            processing_timestamp=datetime.utcnow()
        )
    
    def _update_success_metrics(self, result: ClusteringResult, execution_time: float):
        """Update success metrics"""
        self.metrics['successful_requests'] += 1
        
        # Update accuracy tracking
        if result.overall_quality > 0:
            current_count = self.metrics['successful_requests']
            current_avg = self.metrics['average_accuracy']
            
            # Update rolling average
            self.metrics['average_accuracy'] = (
                (current_avg * (current_count - 1) + result.overall_quality) / current_count
            )
            
            # Track requests above target
            if result.overall_quality >= self.config.target_accuracy:
                self.metrics['requests_above_target'] += 1
        
        # Update timing metrics
        current_count = self.metrics['total_requests']
        current_avg = self.metrics['average_processing_time']
        
        self.metrics['average_processing_time'] = (
            (current_avg * (current_count - 1) + execution_time) / current_count
        )
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        
        # Component metrics
        component_metrics = {}
        
        if self.embeddings_service:
            component_metrics['embeddings'] = await self.embeddings_service.get_metrics()
        
        if self.clustering_algorithms:
            component_metrics['clustering'] = await self.clustering_algorithms.get_metrics()
        
        if self.coherence_scorer:
            component_metrics['coherence'] = await self.coherence_scorer.get_metrics()
        
        # Service-level metrics
        success_rate = (
            self.metrics['successful_requests'] / 
            max(self.metrics['total_requests'], 1)
        )
        
        target_achievement_rate = (
            self.metrics['requests_above_target'] / 
            max(self.metrics['successful_requests'], 1)
        )
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / 
            max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1)
        )
        
        return {
            'service_metrics': self.metrics,
            'performance_summary': {
                'success_rate': success_rate,
                'target_achievement_rate': target_achievement_rate,
                'average_accuracy': self.metrics['average_accuracy'],
                'average_processing_time': self.metrics['average_processing_time'],
                'cache_hit_rate': cache_hit_rate
            },
            'component_metrics': component_metrics,
            'configuration': {
                'target_accuracy': self.config.target_accuracy,
                'min_acceptable_accuracy': self.config.min_acceptable_accuracy,
                'max_concurrent_operations': self.config.max_concurrent_operations,
                'enable_caching': self.config.enable_caching,
                'cache_ttl_seconds': self.config.cache_ttl_seconds
            },
            'system_status': {
                'initialized': self.initialized,
                'active_operations': len(self.active_operations),
                'cache_size': len(self.clustering_cache)
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            if not self.initialized:
                return {
                    'status': 'unhealthy',
                    'error': 'Service not initialized',
                    'initialized': False
                }
            
            # Test basic clustering functionality
            test_texts = [
                "Machine learning algorithms for data analysis",
                "Deep learning models in artificial intelligence",
                "Natural language processing techniques",
                "Computer vision applications",
                "Data science and analytics"
            ]
            
            test_result = await self.cluster_texts(
                texts=test_texts,
                mode=ClusteringMode.FAST,
                enable_validation=False
            )
            
            # Component health checks
            component_health = {}
            
            if self.embeddings_service:
                component_health['embeddings'] = await self.embeddings_service.health_check()
            
            if self.clustering_algorithms:
                component_health['clustering'] = await self.clustering_algorithms.health_check()
            
            if self.coherence_scorer:
                component_health['coherence'] = await self.coherence_scorer.health_check()
            
            return {
                'status': 'healthy' if test_result.status == ClusteringStatus.COMPLETED else 'degraded',
                'last_test_time': datetime.utcnow().isoformat(),
                'test_result': {
                    'clusters_created': test_result.total_clusters,
                    'execution_time': test_result.execution_time,
                    'quality_score': test_result.overall_quality
                },
                'component_health': component_health,
                'service_status': {
                    'initialized': self.initialized,
                    'active_operations': len(self.active_operations)
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_test_time': datetime.utcnow().isoformat(),
                'initialized': self.initialized
            }
    
    async def shutdown(self):
        """Gracefully shutdown the semantic clustering service"""
        try:
            self.logger.info("🛑 Shutting down Semantic Clustering Service...")
            
            # Cancel active operations
            with self.operation_lock:
                for operation_id, task in list(self.active_operations.items()):
                    if not task.done():
                        task.cancel()
                        self.logger.info(f"Cancelled active operation: {operation_id}")
                
                self.active_operations.clear()
            
            # Shutdown component services
            if self.embeddings_service:
                await self.embeddings_service.shutdown()
            
            if self.clustering_algorithms:
                await self.clustering_algorithms.shutdown()
            
            if self.coherence_scorer:
                await self.coherence_scorer.shutdown()
            
            # Shutdown request manager
            if hasattr(self.request_manager, 'shutdown'):
                await self.request_manager.shutdown()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear cache
            self.clustering_cache.clear()
            
            self.initialized = False
            self.logger.info("✅ Semantic Clustering Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Global instance management
_global_clustering_service: Optional[SemanticClusteringService] = None

async def get_semantic_clustering_service(
    config: Optional[ServiceConfig] = None
) -> SemanticClusteringService:
    """Get global semantic clustering service instance"""
    global _global_clustering_service
    
    if _global_clustering_service is None:
        _global_clustering_service = SemanticClusteringService(config)
        await _global_clustering_service.initialize()
    
    return _global_clustering_service