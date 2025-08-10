"""
Clustering Pipeline Integration - Semantic Clustering Integration with Data Acquisition Pipeline

Integration layer that extends the existing SERP Strategist data acquisition pipeline with
comprehensive semantic clustering capabilities. Provides seamless integration with existing
infrastructure while adding advanced text clustering and analysis features.

Features:
- Integration with existing DataAcquisitionPipeline infrastructure
- Semantic clustering as additional data processing layer
- Query clustering and content analysis for SERP data
- Integration with existing timeout protection and error handling
- Compatible with existing API endpoints and patterns
- Performance optimization and caching integration
- Quality assessment and validation reporting
- Export capabilities for clustered insights

Integration Points:
- Data acquisition pipeline extension
- New clustering-specific data sources
- Enhanced blueprint generation with clustering insights
- API endpoint extensions for clustering functionality
- Integration with existing health monitoring and metrics

Performance Targets: <5s clustering integration, seamless pipeline flow
"""

import asyncio
import logging
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum

# Import existing pipeline infrastructure
from .data_acquisition_pipeline import DataAcquisitionPipeline, PipelineConfig
from .data_models import (
    DataSourceType, PipelineRequest, PipelineResult, 
    SourceExecutionResult, AggregatedData, PipelineStatus, PipelineMode
)

# Import semantic clustering components
from .semantic_clustering_service import (
    SemanticClusteringService, ServiceConfig, ClusteringRequest,
    ClusteringMode, ClusteringResult
)
from .clustering_models import ClusteringStatus, ClusteringConfig, ClusteringAlgorithm

logger = logging.getLogger(__name__)


class ClusteringDataSourceType(Enum):
    """Extended data source types for clustering integration"""
    QUERY_CLUSTERING = "query_clustering"
    CONTENT_CLUSTERING = "content_clustering" 
    SEMANTIC_ANALYSIS = "semantic_analysis"
    COMPETITOR_CLUSTERING = "competitor_clustering"


@dataclass
class ClusteringPipelineConfig(PipelineConfig):
    """Extended pipeline configuration with clustering capabilities"""
    
    # Clustering-specific settings
    enable_clustering: bool = True
    clustering_mode: ClusteringMode = ClusteringMode.STANDARD
    cluster_min_texts: int = 5  # Minimum texts needed for clustering
    
    # Integration settings
    cluster_query_expansions: bool = True
    cluster_competitor_content: bool = True
    cluster_paa_questions: bool = True
    
    # Performance settings
    clustering_timeout: float = 15.0
    parallel_clustering: bool = True
    
    # Quality settings
    clustering_target_accuracy: float = 0.85
    include_clustering_validation: bool = True


@dataclass
class ClusteredData:
    """Clustered data results from pipeline processing"""
    
    # Clustering results
    query_clusters: Optional[ClusteringResult] = None
    content_clusters: Optional[ClusteringResult] = None
    paa_clusters: Optional[ClusteringResult] = None
    
    # Cluster insights
    cluster_themes: List[str] = field(default_factory=list)
    semantic_groups: Dict[str, List[str]] = field(default_factory=dict)
    content_categories: Dict[str, float] = field(default_factory=dict)
    
    # Quality metrics
    clustering_quality: float = 0.0
    clustering_confidence: float = 0.0
    
    # Processing metadata
    processing_time: float = 0.0
    clusters_created: int = 0
    texts_processed: int = 0


class ClusteringPipelineIntegration:
    """
    Integration layer that extends the data acquisition pipeline with
    comprehensive semantic clustering capabilities for enhanced SERP analysis.
    """
    
    def __init__(
        self,
        pipeline_config: Optional[ClusteringPipelineConfig] = None,
        clustering_service: Optional[SemanticClusteringService] = None
    ):
        """Initialize clustering pipeline integration"""
        self.config = pipeline_config or ClusteringPipelineConfig()
        self.logger = logging.getLogger(__name__)
        
        # Core services
        self.data_pipeline: Optional[DataAcquisitionPipeline] = None
        self.clustering_service = clustering_service
        
        # Integration state
        self.initialized = False
        
        # Performance metrics
        self.metrics = {
            'clustering_requests': 0,
            'successful_clusterings': 0,
            'failed_clusterings': 0,
            'total_clustering_time': 0.0,
            'average_clustering_time': 0.0,
            'texts_clustered': 0,
            'clusters_generated': 0
        }
        
        self.logger.info("Clustering Pipeline Integration initialized")
    
    async def initialize(self):
        """Initialize the clustering pipeline integration"""
        if self.initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing Clustering Pipeline Integration...")
            
            # Initialize data acquisition pipeline
            self.data_pipeline = DataAcquisitionPipeline(self.config)
            await self.data_pipeline.initialize()
            
            # Initialize clustering service if not provided
            if not self.clustering_service:
                clustering_config = ServiceConfig(
                    target_accuracy=self.config.clustering_target_accuracy,
                    default_mode=self.config.clustering_mode,
                    fast_mode_timeout=5.0,
                    standard_mode_timeout=self.config.clustering_timeout,
                    deep_mode_timeout=30.0
                )
                
                from .semantic_clustering_service import get_semantic_clustering_service
                self.clustering_service = await get_semantic_clustering_service(clustering_config)
            
            self.initialized = True
            self.logger.info("✅ Clustering Pipeline Integration initialization complete")
            
        except Exception as e:
            self.logger.error(f"Clustering Pipeline Integration initialization failed: {e}")
            raise
    
    async def acquire_and_cluster_data(
        self,
        query: str,
        mode: PipelineMode = PipelineMode.STANDARD,
        enable_clustering: bool = None,
        clustering_mode: ClusteringMode = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[PipelineResult, Optional[ClusteredData]]:
        """
        Acquire data using existing pipeline and perform semantic clustering
        
        Args:
            query: The search query for data acquisition
            mode: Pipeline execution mode
            enable_clustering: Override clustering enablement
            clustering_mode: Override clustering mode
            context: Additional context for processing
            
        Returns:
            Tuple of (pipeline_result, clustered_data)
        """
        
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        self.metrics['clustering_requests'] += 1
        
        try:
            self.logger.info(
                f"Starting data acquisition and clustering for query: '{query}' "
                f"(mode: {mode.value})"
            )
            
            # Step 1: Acquire data using existing pipeline
            pipeline_result = await self.data_pipeline.acquire_data(
                query=query,
                mode=mode,
                context=context or {}
            )
            
            # Step 2: Perform clustering if enabled and successful data acquisition
            clustered_data = None
            
            enable_clustering = (
                enable_clustering if enable_clustering is not None 
                else self.config.enable_clustering
            )
            
            if (enable_clustering and 
                pipeline_result.status in [PipelineStatus.COMPLETED, PipelineStatus.PARTIAL_SUCCESS] and
                pipeline_result.aggregated_data):
                
                clustering_mode = clustering_mode or self.config.clustering_mode
                
                clustered_data = await self._perform_pipeline_clustering(
                    pipeline_result, query, clustering_mode, context or {}
                )
            
            # Step 3: Update metrics
            execution_time = time.time() - start_time
            self._update_integration_metrics(clustered_data, execution_time)
            
            self.logger.info(
                f"Data acquisition and clustering completed for '{query}' "
                f"(time: {execution_time:.3f}s, clusters: "
                f"{clustered_data.clusters_created if clustered_data else 0})"
            )
            
            return pipeline_result, clustered_data
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_clusterings'] += 1
            
            self.logger.error(f"Data acquisition and clustering failed for '{query}': {e}")
            
            # Return pipeline result even if clustering fails
            if 'pipeline_result' in locals():
                return pipeline_result, None
            else:
                raise
    
    async def _perform_pipeline_clustering(
        self,
        pipeline_result: PipelineResult,
        query: str,
        clustering_mode: ClusteringMode,
        context: Dict[str, Any]
    ) -> Optional[ClusteredData]:
        """Perform clustering on pipeline data"""
        
        try:
            clustered_data = ClusteredData()
            start_time = time.time()
            
            # Extract texts for clustering from pipeline result
            clustering_tasks = []
            
            # Task 1: Cluster query suggestions if available
            if (self.config.cluster_query_expansions and 
                pipeline_result.aggregated_data.primary_suggestions):
                
                suggestion_texts = pipeline_result.aggregated_data.primary_suggestions[:20]  # Limit for performance
                
                if len(suggestion_texts) >= self.config.cluster_min_texts:
                    clustering_tasks.append(
                        self._cluster_query_suggestions(suggestion_texts, clustering_mode)
                    )
            
            # Task 2: Cluster PAA questions if available
            if (self.config.cluster_paa_questions and 
                pipeline_result.aggregated_data.related_questions):
                
                question_texts = [
                    q.get('question', '') for q in pipeline_result.aggregated_data.related_questions
                    if q.get('question')
                ]
                
                if len(question_texts) >= self.config.cluster_min_texts:
                    clustering_tasks.append(
                        self._cluster_paa_questions(question_texts, clustering_mode)
                    )
            
            # Task 3: Cluster competitor content if available
            if self.config.cluster_competitor_content:
                competitor_texts = self._extract_competitor_texts(pipeline_result)
                
                if len(competitor_texts) >= self.config.cluster_min_texts:
                    clustering_tasks.append(
                        self._cluster_competitor_content(competitor_texts, clustering_mode)
                    )
            
            # Execute clustering tasks in parallel if enabled
            if clustering_tasks:
                if self.config.parallel_clustering:
                    clustering_results = await asyncio.gather(
                        *clustering_tasks, 
                        return_exceptions=True
                    )
                else:
                    clustering_results = []
                    for task in clustering_tasks:
                        try:
                            result = await task
                            clustering_results.append(result)
                        except Exception as e:
                            clustering_results.append(e)
                
                # Process clustering results
                await self._process_clustering_results(
                    clustering_results, clustered_data, query
                )
            
            # Calculate overall clustering metrics
            clustered_data.processing_time = time.time() - start_time
            
            if clustered_data.clusters_created > 0:
                self.metrics['successful_clusterings'] += 1
                
                # Generate cluster insights
                await self._generate_cluster_insights(clustered_data, query)
            
            return clustered_data
            
        except Exception as e:
            self.logger.error(f"Pipeline clustering failed: {e}")
            return None
    
    async def _cluster_query_suggestions(
        self, 
        suggestions: List[str], 
        mode: ClusteringMode
    ) -> ClusteringResult:
        """Cluster query suggestions"""
        
        return await self.clustering_service.cluster_texts(
            texts=suggestions,
            mode=mode,
            enable_validation=self.config.include_clustering_validation,
            target_accuracy=self.config.clustering_target_accuracy,
            max_processing_time=self.config.clustering_timeout
        )
    
    async def _cluster_paa_questions(
        self, 
        questions: List[str], 
        mode: ClusteringMode
    ) -> ClusteringResult:
        """Cluster People Also Ask questions"""
        
        return await self.clustering_service.cluster_texts(
            texts=questions,
            mode=mode,
            enable_validation=self.config.include_clustering_validation,
            target_accuracy=self.config.clustering_target_accuracy,
            max_processing_time=self.config.clustering_timeout
        )
    
    async def _cluster_competitor_content(
        self, 
        content_texts: List[str], 
        mode: ClusteringMode
    ) -> ClusteringResult:
        """Cluster competitor content"""
        
        return await self.clustering_service.cluster_texts(
            texts=content_texts,
            mode=mode,
            enable_validation=self.config.include_clustering_validation,
            target_accuracy=self.config.clustering_target_accuracy,
            max_processing_time=self.config.clustering_timeout
        )
    
    def _extract_competitor_texts(self, pipeline_result: PipelineResult) -> List[str]:
        """Extract competitor content texts from pipeline result"""
        
        competitor_texts = []
        
        # Extract from source results
        for source_result in pipeline_result.source_results:
            if source_result.success and source_result.data:
                # Extract text content from various source types
                if 'content' in source_result.data:
                    content = source_result.data['content']
                    if isinstance(content, list):
                        competitor_texts.extend([str(c) for c in content if c])
                    elif isinstance(content, str):
                        competitor_texts.append(content)
                
                # Extract from analyzed pages
                if 'analyzed_pages' in source_result.data:
                    pages = source_result.data['analyzed_pages']
                    for page in pages[:5]:  # Limit for performance
                        if isinstance(page, dict) and 'content' in page:
                            competitor_texts.append(str(page['content'])[:500])  # Truncate long content
        
        # Clean and filter texts
        cleaned_texts = []
        for text in competitor_texts:
            text = str(text).strip()
            if len(text) > 20 and len(text) < 1000:  # Reasonable text length
                cleaned_texts.append(text)
        
        return cleaned_texts[:50]  # Limit total texts for performance
    
    async def _process_clustering_results(
        self,
        clustering_results: List[Union[ClusteringResult, Exception]],
        clustered_data: ClusteredData,
        query: str
    ):
        """Process clustering results and update clustered data"""
        
        total_quality = 0.0
        successful_clusterings = 0
        
        for i, result in enumerate(clustering_results):
            if isinstance(result, Exception):
                self.logger.warning(f"Clustering task {i} failed: {result}")
                continue
            
            if not isinstance(result, ClusteringResult):
                continue
            
            if result.status == ClusteringStatus.COMPLETED:
                successful_clusterings += 1
                
                # Assign results based on task order
                if i == 0:  # Query suggestions
                    clustered_data.query_clusters = result
                elif i == 1:  # PAA questions
                    clustered_data.paa_clusters = result
                elif i == 2:  # Competitor content
                    clustered_data.content_clusters = result
                
                # Update metrics
                clustered_data.clusters_created += result.total_clusters
                clustered_data.texts_processed += len(result.input_texts)
                
                if result.overall_quality > 0:
                    total_quality += result.overall_quality
        
        # Calculate average clustering quality
        if successful_clusterings > 0:
            clustered_data.clustering_quality = total_quality / successful_clusterings
            clustered_data.clustering_confidence = min(successful_clusterings / 3.0, 1.0)  # Max 3 clustering tasks
    
    async def _generate_cluster_insights(
        self, 
        clustered_data: ClusteredData, 
        query: str
    ):
        """Generate high-level insights from clustering results"""
        
        try:
            cluster_themes = set()
            semantic_groups = {}
            content_categories = {}
            
            # Process each clustering result
            clustering_results = [
                clustered_data.query_clusters,
                clustered_data.paa_clusters, 
                clustered_data.content_clusters
            ]
            
            for result in clustering_results:
                if not result or result.status != ClusteringStatus.COMPLETED:
                    continue
                
                # Extract cluster themes
                for cluster in result.clusters:
                    if cluster.cluster_keywords:
                        cluster_themes.update(cluster.cluster_keywords[:3])
                    
                    if cluster.topic_labels:
                        cluster_themes.update(cluster.topic_labels)
                    
                    # Group semantically similar clusters
                    if cluster.representative_texts:
                        group_key = f"group_{len(semantic_groups)}"
                        semantic_groups[group_key] = cluster.representative_texts[:2]
                
                # Analyze content categories (simplified)
                if len(result.clusters) > 0:
                    category_distribution = {}
                    
                    for cluster in result.clusters:
                        if cluster.topic_labels:
                            for topic in cluster.topic_labels:
                                category_distribution[topic] = category_distribution.get(topic, 0) + cluster.size
                    
                    # Normalize to percentages
                    total_items = sum(category_distribution.values())
                    if total_items > 0:
                        for topic, count in category_distribution.items():
                            content_categories[topic] = count / total_items
            
            # Update clustered data with insights
            clustered_data.cluster_themes = list(cluster_themes)[:10]  # Top 10 themes
            clustered_data.semantic_groups = dict(list(semantic_groups.items())[:5])  # Top 5 groups
            clustered_data.content_categories = content_categories
            
        except Exception as e:
            self.logger.warning(f"Cluster insights generation failed: {e}")
    
    def _update_integration_metrics(
        self, 
        clustered_data: Optional[ClusteredData], 
        execution_time: float
    ):
        """Update integration performance metrics"""
        
        self.metrics['total_clustering_time'] += execution_time
        
        if self.metrics['clustering_requests'] > 0:
            self.metrics['average_clustering_time'] = (
                self.metrics['total_clustering_time'] / 
                self.metrics['clustering_requests']
            )
        
        if clustered_data:
            self.metrics['texts_clustered'] += clustered_data.texts_processed
            self.metrics['clusters_generated'] += clustered_data.clusters_created
    
    async def create_enhanced_pipeline_result(
        self,
        pipeline_result: PipelineResult,
        clustered_data: Optional[ClusteredData]
    ) -> Dict[str, Any]:
        """Create enhanced pipeline result with clustering data"""
        
        # Start with standard pipeline result
        enhanced_result = {
            'pipeline_data': {
                'request_id': pipeline_result.request_id,
                'query': pipeline_result.query,
                'status': pipeline_result.status.value,
                'execution_time': pipeline_result.execution_time,
                'quality_score': pipeline_result.quality_score,
                'aggregated_data': pipeline_result.aggregated_data.__dict__ if pipeline_result.aggregated_data else None
            }
        }
        
        # Add clustering data if available
        if clustered_data:
            clustering_summary = {
                'clustering_enabled': True,
                'clusters_created': clustered_data.clusters_created,
                'texts_processed': clustered_data.texts_processed,
                'clustering_quality': clustered_data.clustering_quality,
                'processing_time': clustered_data.processing_time,
                'cluster_themes': clustered_data.cluster_themes,
                'semantic_groups': clustered_data.semantic_groups,
                'content_categories': clustered_data.content_categories
            }
            
            # Add detailed cluster data
            cluster_details = {}
            
            if clustered_data.query_clusters:
                cluster_details['query_clusters'] = clustered_data.query_clusters.get_cluster_summaries()
            
            if clustered_data.paa_clusters:
                cluster_details['paa_clusters'] = clustered_data.paa_clusters.get_cluster_summaries()
            
            if clustered_data.content_clusters:
                cluster_details['content_clusters'] = clustered_data.content_clusters.get_cluster_summaries()
            
            enhanced_result['clustering_data'] = {
                'summary': clustering_summary,
                'details': cluster_details
            }
        else:
            enhanced_result['clustering_data'] = {
                'clustering_enabled': False,
                'message': 'Clustering was not performed or failed'
            }
        
        return enhanced_result
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive integration metrics"""
        
        # Get component metrics
        component_metrics = {}
        
        if self.data_pipeline:
            component_metrics['data_pipeline'] = await self.data_pipeline.get_pipeline_metrics()
        
        if self.clustering_service:
            component_metrics['clustering_service'] = await self.clustering_service.get_service_metrics()
        
        # Calculate integration-specific metrics
        success_rate = (
            self.metrics['successful_clusterings'] / 
            max(self.metrics['clustering_requests'], 1)
        )
        
        avg_clusters_per_request = (
            self.metrics['clusters_generated'] / 
            max(self.metrics['successful_clusterings'], 1)
        )
        
        return {
            'integration_metrics': self.metrics,
            'performance_summary': {
                'success_rate': success_rate,
                'average_clustering_time': self.metrics['average_clustering_time'],
                'avg_clusters_per_request': avg_clusters_per_request,
                'total_requests': self.metrics['clustering_requests']
            },
            'component_metrics': component_metrics,
            'configuration': {
                'enable_clustering': self.config.enable_clustering,
                'clustering_mode': self.config.clustering_mode.value,
                'clustering_timeout': self.config.clustering_timeout,
                'parallel_clustering': self.config.parallel_clustering,
                'target_accuracy': self.config.clustering_target_accuracy
            },
            'system_status': {
                'initialized': self.initialized,
                'data_pipeline_available': self.data_pipeline is not None,
                'clustering_service_available': self.clustering_service is not None
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on integration"""
        try:
            if not self.initialized:
                return {
                    'status': 'unhealthy',
                    'error': 'Integration not initialized',
                    'initialized': False
                }
            
            # Test integration with sample query
            test_pipeline_result, test_clustered_data = await self.acquire_and_cluster_data(
                query="test clustering integration",
                mode=PipelineMode.FAST,
                clustering_mode=ClusteringMode.FAST
            )
            
            # Component health checks
            component_health = {}
            
            if self.data_pipeline:
                component_health['data_pipeline'] = await self.data_pipeline.health_check()
            
            if self.clustering_service:
                component_health['clustering_service'] = await self.clustering_service.health_check()
            
            return {
                'status': 'healthy',
                'last_test_time': datetime.utcnow().isoformat(),
                'test_result': {
                    'pipeline_status': test_pipeline_result.status.value,
                    'clustering_performed': test_clustered_data is not None,
                    'clusters_created': test_clustered_data.clusters_created if test_clustered_data else 0
                },
                'component_health': component_health,
                'integration_status': {
                    'initialized': self.initialized,
                    'services_available': all([
                        self.data_pipeline is not None,
                        self.clustering_service is not None
                    ])
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
        """Gracefully shutdown clustering pipeline integration"""
        try:
            self.logger.info("🛑 Shutting down Clustering Pipeline Integration...")
            
            # Shutdown component services
            if self.data_pipeline:
                await self.data_pipeline.shutdown()
            
            if self.clustering_service:
                await self.clustering_service.shutdown()
            
            self.initialized = False
            self.logger.info("✅ Clustering Pipeline Integration shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Global instance management
_global_integration: Optional[ClusteringPipelineIntegration] = None

async def get_clustering_pipeline_integration(
    config: Optional[ClusteringPipelineConfig] = None
) -> ClusteringPipelineIntegration:
    """Get global clustering pipeline integration instance"""
    global _global_integration
    
    if _global_integration is None:
        _global_integration = ClusteringPipelineIntegration(config)
        await _global_integration.initialize()
    
    return _global_integration