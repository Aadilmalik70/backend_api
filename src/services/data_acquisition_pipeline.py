"""
Data Acquisition Pipeline - Comprehensive multi-source data collection

High-performance data acquisition system for SERP Strategist that collects data from
multiple sources with async processing, rate limiting, and intelligent caching.

Features:
- Multi-source data collection (Google Autocomplete, SerpAPI PAA, Related Searches, Competitor Content)
- Parallel async processing with rate limiting and timeout protection
- Advanced caching and performance optimization
- Circuit breaker pattern for resilient API calls
- Progressive data aggregation and validation
- Integration with existing SERP Strategist infrastructure

Data Sources:
1. Google Autocomplete - Query suggestions and user intent prediction
2. SerpAPI People Also Ask - Related questions and content ideas
3. Related Searches - Keyword expansion and content clustering
4. Competitor Content - Content gap analysis and competitive intelligence

Performance Targets: <5s for single query, <30s for batch processing
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
import json

# Import async and performance utilities
from .async_request_manager import AsyncRequestManager, RequestConfig
from .rate_limiter import RateLimiter
from .timeout_protection import get_timeout_protection, TimeoutConfig, CircuitBreakerConfig, RetryConfig, CircuitBreaker

# Import data source clients
from .google_autocomplete_client import GoogleAutocompleteClient
from .serpapi_paa_client import SerpAPIPAAClient
from .related_searches_client import RelatedSearchesClient
from .competitor_content_client import CompetitorContentClient

# Import data models and utilities
from .data_models import (
    DataSourceType, PipelineRequest, PipelineResult, 
    SourceExecutionResult, AggregatedData, PipelineStatus, PipelineMode,
    AggregationStrategy, generate_request_id, validate_query, sanitize_query
)

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self.cache_data: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.ttl_seconds = 3600  # 1 hour default TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        if key in self.cache_data:
            # Check TTL
            if key in self.cache_timestamps:
                age = datetime.utcnow() - self.cache_timestamps[key]
                if age.total_seconds() > self.ttl_seconds:
                    # Expired, remove from cache
                    del self.cache_data[key]
                    del self.cache_timestamps[key]
                    return None
            
            return self.cache_data[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value"""
        self.cache_data[key] = value
        self.cache_timestamps[key] = datetime.utcnow()
        if ttl:
            self.ttl_seconds = ttl
    
    async def clear(self) -> None:
        """Clear all cached data"""
        self.cache_data.clear()
        self.cache_timestamps.clear()
    
    async def initialize(self) -> None:
        """Initialize cache (no-op for simple implementation)"""
        pass
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get cache metrics"""
        return {
            'cache_size': len(self.cache_data),
            'total_keys': len(self.cache_data)
        }

class DataAggregator:
    """Data aggregation and combination utilities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def aggregate_sources(
        self, 
        source_results: List['SourceExecutionResult'], 
        strategy: 'AggregationStrategy'
    ) -> 'AggregatedData':
        """Aggregate data from multiple sources"""
        
        if not source_results:
            return AggregatedData(query="")
        
        # Extract successful results
        successful_results = [r for r in source_results if r.success and r.data]
        
        if not successful_results:
            return AggregatedData(query="")
        
        # Get the query from the first result
        query = successful_results[0].data.get('query', '') if successful_results[0].data else ''
        
        # Aggregate data based on strategy
        if strategy == AggregationStrategy.MERGE_SIMPLE:
            return await self._merge_simple(query, successful_results)
        elif strategy == AggregationStrategy.MERGE_INTELLIGENT:
            return await self._merge_intelligent(query, successful_results)
        else:  # MERGE_COMPREHENSIVE
            return await self._merge_comprehensive(query, successful_results)
    
    async def _merge_simple(self, query: str, results: List['SourceExecutionResult']) -> 'AggregatedData':
        """Simple aggregation strategy"""
        suggestions = []
        questions = []
        data_sources = []
        
        for result in results:
            if result.data:
                data_sources.append(result.source_type)
                
                # Extract suggestions
                if 'suggestions' in result.data:
                    suggestions.extend(result.data['suggestions'][:5])
                
                # Extract questions
                if 'questions' in result.data:
                    questions.extend([{'question': q} for q in result.data['questions'][:5]])
                elif 'people_also_ask' in result.data:
                    questions.extend([{'question': q} for q in result.data['people_also_ask'][:5]])
        
        return AggregatedData(
            query=query,
            primary_suggestions=suggestions[:10],
            related_questions=questions[:10],
            data_sources_used=data_sources
        )
    
    async def _merge_intelligent(self, query: str, results: List['SourceExecutionResult']) -> 'AggregatedData':
        """Intelligent aggregation with deduplication"""
        # For now, use simple merge (can be enhanced later)
        return await self._merge_simple(query, results)
    
    async def _merge_comprehensive(self, query: str, results: List['SourceExecutionResult']) -> 'AggregatedData':
        """Comprehensive aggregation with full analysis"""
        # For now, use simple merge (can be enhanced later)
        return await self._merge_simple(query, results)

class CacheStrategy(Enum):
    """Caching strategies for pipeline data"""
    NONE = "none"
    BASIC = "basic"
    INTELLIGENT = "intelligent"
    AGGRESSIVE = "aggressive"

@dataclass
class PipelineConfig:
    """Configuration for data acquisition pipeline"""
    
    # Source configuration
    enabled_sources: List[DataSourceType] = field(default_factory=lambda: [
        DataSourceType.GOOGLE_AUTOCOMPLETE,
        DataSourceType.SERPAPI_PAA,
        DataSourceType.RELATED_SEARCHES,
        DataSourceType.COMPETITOR_CONTENT
    ])
    
    # Performance settings
    max_parallel_requests: int = 10
    request_timeout: float = 8.0
    total_timeout: float = 30.0
    
    # Rate limiting
    rate_limits: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'google_autocomplete': {'requests_per_minute': 600, 'burst_limit': 100},
        'serpapi_paa': {'requests_per_minute': 60, 'burst_limit': 20},
        'related_searches': {'requests_per_minute': 300, 'burst_limit': 50},
        'competitor_content': {'requests_per_minute': 120, 'burst_limit': 30}
    })
    
    # Caching settings
    cache_strategy: CacheStrategy = CacheStrategy.INTELLIGENT
    cache_ttl_seconds: int = 3600
    enable_persistent_cache: bool = True
    
    # Error handling
    max_retries: int = 3
    enable_circuit_breaker: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 300
    
    # Data quality
    enable_data_validation: bool = True
    min_data_sources: int = 2  # Minimum sources for valid result
    quality_threshold: float = 0.7

@dataclass
class SourceExecutionResult:
    """Result from executing a single data source"""
    source_type: DataSourceType
    success: bool
    data: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    from_cache: bool = False
    quality_score: float = 0.0

class DataAcquisitionPipeline:
    """
    High-performance data acquisition pipeline with multi-source collection,
    async processing, rate limiting, and intelligent caching.
    """
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the data acquisition pipeline"""
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.async_manager = AsyncRequestManager()
        
        # Timeout protection system
        self.timeout_protection = get_timeout_protection()
        
        # Initialize caching (simplified for now)
        self.cache_data: Dict[str, Any] = {}
        self.cache = SimpleCache()  # Simple in-memory cache implementation
        
        # Data source clients
        self.clients: Dict[DataSourceType, Any] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
        # Circuit breakers for error handling
        self.circuit_breakers: Dict[str, Any] = {}
        
        # Data aggregator for combining results
        self.data_aggregator = DataAggregator()
        
        # Performance tracking
        self.metrics = {
            'total_requests': 0, 
            'successful_requests': 0, 
            'failed_requests': 0,
            'partial_requests': 0,
            'timeout_requests': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_hit_rate': 0.0
        }
        self.execution_history = []
        
        # Pipeline state
        self.initialized = False
        self.active_requests = {}
        
        self.logger.info("Data Acquisition Pipeline initialized")
    
    async def initialize(self):
        """Initialize pipeline components and data source clients"""
        if self.initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing Data Acquisition Pipeline...")
            
            # Initialize async request manager
            await self.async_manager.initialize()
            
            # Initialize data source clients
            await self._initialize_clients()
            
            # Setup rate limiters
            self._setup_rate_limiters()
            
            # Setup circuit breakers
            self._setup_circuit_breakers()
            
            # Initialize cache
            await self.cache.initialize()
            
            self.initialized = True
            self.logger.info("✅ Data Acquisition Pipeline initialization complete")
            
        except Exception as e:
            self.logger.error(f"Pipeline initialization failed: {e}")
            raise
    
    async def _initialize_clients(self):
        """Initialize all data source clients"""
        
        # Google Autocomplete Client
        if DataSourceType.GOOGLE_AUTOCOMPLETE in self.config.enabled_sources:
            self.clients[DataSourceType.GOOGLE_AUTOCOMPLETE] = GoogleAutocompleteClient()
            await self.clients[DataSourceType.GOOGLE_AUTOCOMPLETE].initialize()
        
        # SerpAPI PAA Client
        if DataSourceType.SERPAPI_PAA in self.config.enabled_sources:
            self.clients[DataSourceType.SERPAPI_PAA] = SerpAPIPAAClient()
            await self.clients[DataSourceType.SERPAPI_PAA].initialize()
        
        # Related Searches Client
        if DataSourceType.RELATED_SEARCHES in self.config.enabled_sources:
            self.clients[DataSourceType.RELATED_SEARCHES] = RelatedSearchesClient()
            await self.clients[DataSourceType.RELATED_SEARCHES].initialize()
        
        # Competitor Content Client
        if DataSourceType.COMPETITOR_CONTENT in self.config.enabled_sources:
            self.clients[DataSourceType.COMPETITOR_CONTENT] = CompetitorContentClient()
            await self.clients[DataSourceType.COMPETITOR_CONTENT].initialize()
        
        self.logger.info(f"Initialized {len(self.clients)} data source clients")
    
    def _setup_rate_limiters(self):
        """Setup rate limiters for each data source"""
        for source, limits in self.config.rate_limits.items():
            self.rate_limiters[source] = RateLimiter(
                requests_per_minute=limits['requests_per_minute'],
                burst_limit=limits['burst_limit']
            )
        
        self.logger.info("Rate limiters configured for all data sources")
    
    def _setup_circuit_breakers(self):
        """Setup circuit breakers for resilient API calls"""
        if not self.config.enable_circuit_breaker:
            return
        
        for source_type in self.config.enabled_sources:
            source_name = source_type.value
            circuit_config = CircuitBreakerConfig(
                failure_threshold=self.config.circuit_breaker_failure_threshold,
                recovery_timeout=self.config.circuit_breaker_timeout
            )
            self.circuit_breakers[source_name] = CircuitBreaker(source_name, circuit_config)
        
        self.logger.info("Circuit breakers configured for all data sources")
    
    async def acquire_data(
        self,
        query: str,
        mode: PipelineMode = PipelineMode.STANDARD,
        sources: Optional[List[DataSourceType]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> PipelineResult:
        """
        Acquire data from multiple sources with async processing and optimization
        
        Args:
            query: The search query or topic for data acquisition
            mode: Pipeline execution mode (fast, standard, deep, custom)
            sources: Custom list of sources (overrides mode defaults)
            context: Additional context for data acquisition
        
        Returns:
            PipelineResult with aggregated data from all sources
        """
        
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Create pipeline request
        pipeline_request = PipelineRequest(
            request_id=request_id,
            query=query,
            mode=mode,
            sources=sources or self._get_sources_for_mode(mode),
            context=context or {},
            timestamp=datetime.utcnow()
        )
        
        self.logger.info(f"🔍 Starting data acquisition for query: '{query}' (mode: {mode.value})")
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(pipeline_request)
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                self.logger.info(f"✨ Cache hit for query: '{query}'")
                cached_result.from_cache = True
                cached_result.execution_time = time.time() - start_time
                return cached_result
            
            # Execute data acquisition from all sources
            source_results = await self._execute_parallel_acquisition(pipeline_request)
            
            # Aggregate results from all sources
            aggregated_data = await self.data_aggregator.aggregate_sources(
                source_results,
                strategy=self._get_aggregation_strategy(mode)
            )
            
            # Validate and score data quality
            quality_score = await self._calculate_quality_score(source_results, aggregated_data)
            
            # Create pipeline result
            pipeline_result = PipelineResult(
                request_id=request_id,
                query=query,
                status=self._determine_pipeline_status(source_results),
                aggregated_data=aggregated_data,
                source_results=source_results,
                execution_time=time.time() - start_time,
                quality_score=quality_score,
                from_cache=False,
                metadata={
                    'mode': mode.value,
                    'sources_attempted': len(pipeline_request.sources),
                    'sources_successful': sum(1 for r in source_results if r.success),
                    'cache_key': cache_key
                }
            )
            
            # Cache successful results
            if pipeline_result.status in [PipelineStatus.COMPLETED, PipelineStatus.PARTIAL_SUCCESS]:
                await self.cache.set(cache_key, pipeline_result)
            
            # Update metrics
            await self._update_pipeline_metrics(pipeline_result)
            
            self.logger.info(f"✅ Data acquisition complete: {pipeline_result.status.value} "
                           f"({pipeline_result.execution_time:.2f}s, quality: {quality_score:.2f})")
            
            return pipeline_result
            
        except asyncio.TimeoutError:
            self.logger.error(f"⏰ Data acquisition timeout for query: '{query}'")
            return self._create_timeout_result(pipeline_request, time.time() - start_time)
            
        except Exception as e:
            self.logger.error(f"❌ Data acquisition failed for query: '{query}': {e}")
            return self._create_error_result(pipeline_request, str(e), time.time() - start_time)
    
    async def _execute_parallel_acquisition(
        self,
        pipeline_request: PipelineRequest
    ) -> List[SourceExecutionResult]:
        """Execute data acquisition from all sources in parallel"""
        
        # Create acquisition tasks for each source
        acquisition_tasks = []
        
        for source_type in pipeline_request.sources:
            if source_type in self.clients:
                task = asyncio.create_task(
                    self._execute_source_acquisition(source_type, pipeline_request)
                )
                acquisition_tasks.append(task)
        
        # Execute all tasks with timeout
        try:
            source_results = await asyncio.wait_for(
                asyncio.gather(*acquisition_tasks, return_exceptions=True),
                timeout=self.config.total_timeout
            )
            
            # Process results and exceptions
            processed_results = []
            for i, result in enumerate(source_results):
                if isinstance(result, Exception):
                    source_type = pipeline_request.sources[i]
                    processed_results.append(SourceExecutionResult(
                        source_type=source_type,
                        success=False,
                        error_message=str(result),
                        execution_time=0.0
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except asyncio.TimeoutError:
            self.logger.warning(f"Parallel acquisition timeout after {self.config.total_timeout}s")
            raise
    
    async def _execute_source_acquisition(
        self,
        source_type: DataSourceType,
        pipeline_request: PipelineRequest
    ) -> SourceExecutionResult:
        """Execute data acquisition from a single source"""
        
        start_time = time.time()
        source_name = source_type.value
        
        # Define the data acquisition operation
        async def acquire_data():
            client = self.clients[source_type]
            
            if source_type == DataSourceType.GOOGLE_AUTOCOMPLETE:
                return await client.get_autocomplete_suggestions(
                    query=pipeline_request.query,
                    context=pipeline_request.context
                )
            elif source_type == DataSourceType.SERPAPI_PAA:
                return await client.get_people_also_ask(
                    query=pipeline_request.query,
                    context=pipeline_request.context
                )
            elif source_type == DataSourceType.RELATED_SEARCHES:
                return await client.get_related_searches(
                    query=pipeline_request.query,
                    context=pipeline_request.context
                )
            elif source_type == DataSourceType.COMPETITOR_CONTENT:
                return await client.get_competitor_content(
                    query=pipeline_request.query,
                    context=pipeline_request.context
                )
            else:
                raise ValueError(f"Unknown source type: {source_type}")
        
        try:
            # Execute with full timeout protection
            result = await self.timeout_protection.protected_call(
                operation=acquire_data,
                service_name=source_name,
                operation_type="data_acquisition",
                timeout=self.config.request_timeout,
                enable_retry=True,
                enable_circuit_breaker=True,
                enable_recovery=True,
                context={'source_type': source_type.value, 'query': pipeline_request.query}
            )
            
            if result.success:
                data = result.data
                execution_time = result.execution_time
                
                # Calculate quality score for this source
                quality_score = await self._calculate_source_quality_score(source_type, data)
                
                self.logger.debug(f"Source {source_name} completed successfully in {execution_time:.2f}s")
                
                return SourceExecutionResult(
                    source_type=source_type,
                    success=True,
                    data=data,
                    execution_time=execution_time,
                    quality_score=quality_score,
                    timeout_occurred=result.timeout_occurred,
                    retries_used=result.retries_used
                )
            else:
                # Handle failure from timeout protection system
                error_message = str(result.error) if result.error else "Unknown error"
                
                self.logger.error(f"Source acquisition failed for {source_name}: {error_message}")
                
                return SourceExecutionResult(
                    source_type=source_type,
                    success=False,
                    error_message=error_message,
                    execution_time=result.execution_time,
                    timeout_occurred=result.timeout_occurred,
                    retries_used=result.retries_used
                )
                
        except Exception as e:
            # Handle any unexpected errors
            execution_time = time.time() - start_time
            self.logger.error(f"Unexpected error in source execution for {source_name}: {e}")
            
            return SourceExecutionResult(
                source_type=source_type,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _get_sources_for_mode(self, mode: PipelineMode) -> List[DataSourceType]:
        """Get enabled sources based on pipeline mode"""
        if mode == PipelineMode.FAST:
            return [
                DataSourceType.GOOGLE_AUTOCOMPLETE,
                DataSourceType.SERPAPI_PAA
            ]
        elif mode == PipelineMode.STANDARD:
            return [
                DataSourceType.GOOGLE_AUTOCOMPLETE,
                DataSourceType.SERPAPI_PAA,
                DataSourceType.RELATED_SEARCHES
            ]
        elif mode == PipelineMode.DEEP:
            return self.config.enabled_sources
        else:  # CUSTOM mode
            return self.config.enabled_sources
    
    def _get_aggregation_strategy(self, mode: PipelineMode) -> AggregationStrategy:
        """Get data aggregation strategy based on pipeline mode"""
        if mode == PipelineMode.FAST:
            return AggregationStrategy.MERGE_SIMPLE
        elif mode == PipelineMode.STANDARD:
            return AggregationStrategy.MERGE_INTELLIGENT
        else:  # DEEP or CUSTOM
            return AggregationStrategy.MERGE_COMPREHENSIVE
    
    async def _calculate_source_quality_score(
        self,
        source_type: DataSourceType,
        data: Dict[str, Any]
    ) -> float:
        """Calculate quality score for data from a single source"""
        
        if not data:
            return 0.0
        
        score = 0.0
        
        # Base score for successful data retrieval
        score += 0.3
        
        # Data completeness score
        if isinstance(data, dict):
            non_empty_fields = sum(1 for v in data.values() if v)
            total_fields = len(data)
            completeness = non_empty_fields / total_fields if total_fields > 0 else 0
            score += completeness * 0.4
        
        # Source-specific quality metrics
        if source_type == DataSourceType.GOOGLE_AUTOCOMPLETE:
            suggestions = data.get('suggestions', [])
            score += min(len(suggestions) / 10, 1.0) * 0.3  # More suggestions = higher quality
        
        elif source_type == DataSourceType.SERPAPI_PAA:
            paa_questions = data.get('people_also_ask', [])
            score += min(len(paa_questions) / 8, 1.0) * 0.3
        
        elif source_type == DataSourceType.RELATED_SEARCHES:
            related_terms = data.get('related_searches', [])
            score += min(len(related_terms) / 12, 1.0) * 0.3
        
        elif source_type == DataSourceType.COMPETITOR_CONTENT:
            analyzed_pages = data.get('analyzed_pages', [])
            score += min(len(analyzed_pages) / 5, 1.0) * 0.3
        
        return min(score, 1.0)
    
    async def _calculate_quality_score(
        self,
        source_results: List[SourceExecutionResult],
        aggregated_data: AggregatedData
    ) -> float:
        """Calculate overall quality score for the pipeline result"""
        
        if not source_results:
            return 0.0
        
        # Success rate component
        successful_sources = sum(1 for r in source_results if r.success)
        total_sources = len(source_results)
        success_rate = successful_sources / total_sources
        
        # Average source quality
        source_qualities = [r.quality_score for r in source_results if r.success]
        avg_source_quality = sum(source_qualities) / len(source_qualities) if source_qualities else 0.0
        
        # Data diversity score (more sources = higher diversity)
        diversity_score = min(successful_sources / len(self.config.enabled_sources), 1.0)
        
        # Aggregated data completeness
        aggregation_completeness = aggregated_data.calculate_completeness() if aggregated_data else 0.0
        
        # Weighted final score
        final_score = (
            success_rate * 0.3 +
            avg_source_quality * 0.3 +
            diversity_score * 0.2 +
            aggregation_completeness * 0.2
        )
        
        return min(final_score, 1.0)
    
    def _determine_pipeline_status(self, source_results: List[SourceExecutionResult]) -> PipelineStatus:
        """Determine overall pipeline status based on source results"""
        
        if not source_results:
            return PipelineStatus.FAILED
        
        successful_sources = sum(1 for r in source_results if r.success)
        total_sources = len(source_results)
        
        if successful_sources == 0:
            return PipelineStatus.FAILED
        elif successful_sources == total_sources:
            return PipelineStatus.COMPLETED
        elif successful_sources >= self.config.min_data_sources:
            return PipelineStatus.PARTIAL_SUCCESS
        else:
            return PipelineStatus.FAILED
    
    def _generate_cache_key(self, pipeline_request: PipelineRequest) -> str:
        """Generate cache key for pipeline request"""
        import hashlib
        
        key_data = {
            'query': pipeline_request.query,
            'mode': pipeline_request.mode.value,
            'sources': sorted([s.value for s in pipeline_request.sources])
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _create_timeout_result(self, pipeline_request: PipelineRequest, execution_time: float) -> PipelineResult:
        """Create result for timeout scenarios"""
        return PipelineResult(
            request_id=pipeline_request.request_id,
            query=pipeline_request.query,
            status=PipelineStatus.TIMEOUT,
            aggregated_data=None,
            source_results=[],
            execution_time=execution_time,
            quality_score=0.0,
            error_message="Pipeline execution timeout",
            metadata={'timeout_duration': self.config.total_timeout}
        )
    
    def _create_error_result(
        self,
        pipeline_request: PipelineRequest,
        error_message: str,
        execution_time: float
    ) -> PipelineResult:
        """Create result for error scenarios"""
        return PipelineResult(
            request_id=pipeline_request.request_id,
            query=pipeline_request.query,
            status=PipelineStatus.FAILED,
            aggregated_data=None,
            source_results=[],
            execution_time=execution_time,
            quality_score=0.0,
            error_message=error_message
        )
    
    async def _update_pipeline_metrics(self, result: PipelineResult):
        """Update pipeline performance metrics"""
        self.metrics['total_requests'] += 1
        
        if result.status == PipelineStatus.COMPLETED:
            self.metrics['successful_requests'] += 1
        elif result.status == PipelineStatus.PARTIAL_SUCCESS:
            self.metrics['partial_requests'] += 1
        elif result.status == PipelineStatus.FAILED:
            self.metrics['failed_requests'] += 1
        elif result.status == PipelineStatus.TIMEOUT:
            self.metrics['timeout_requests'] += 1
        
        self.metrics['total_execution_time'] += result.execution_time
        self.metrics['average_execution_time'] = (
            self.metrics['total_execution_time'] / self.metrics['total_requests']
        )
        
        if result.from_cache:
            self.metrics['cache_hits'] += 1
        else:
            self.metrics['cache_misses'] += 1
        
        self.metrics['cache_hit_rate'] = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0.0
        )
    
    async def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline performance metrics"""
        
        # Get component metrics
        cache_metrics = await self.cache.get_metrics()
        
        # Get rate limiter status
        rate_limiter_status = {
            name: limiter.get_status() 
            for name, limiter in self.rate_limiters.items()
        }
        
        # Get circuit breaker status
        circuit_breaker_status = {
            name: breaker.get_status()
            for name, breaker in self.circuit_breakers.items()
        }
        
        return {
            'pipeline_metrics': {
                'total_requests': self.metrics['total_requests'],
                'successful_requests': self.metrics['successful_requests'],
                'partial_requests': self.metrics['partial_requests'],
                'failed_requests': self.metrics['failed_requests'],
                'timeout_requests': self.metrics['timeout_requests'],
                'success_rate': self.metrics['successful_requests'] / max(self.metrics['total_requests'], 1),
                'average_execution_time': self.metrics['average_execution_time'],
                'cache_hit_rate': self.metrics['cache_hit_rate']
            },
            'cache_performance': cache_metrics,
            'rate_limiters': rate_limiter_status,
            'circuit_breakers': circuit_breaker_status,
            'active_sources': list(self.clients.keys()),
            'configuration': {
                'enabled_sources': [s.value for s in self.config.enabled_sources],
                'max_parallel_requests': self.config.max_parallel_requests,
                'total_timeout': self.config.total_timeout,
                'cache_strategy': self.config.cache_strategy.value
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for the pipeline"""
        
        health_status = {
            'pipeline_status': 'healthy' if self.initialized else 'initializing',
            'timestamp': datetime.utcnow().isoformat(),
            'components': {}
        }
        
        # Check data source clients
        for source_type, client in self.clients.items():
            try:
                client_health = await client.health_check() if hasattr(client, 'health_check') else {'status': 'unknown'}
                health_status['components'][source_type.value] = client_health
            except Exception as e:
                health_status['components'][source_type.value] = {'status': 'unhealthy', 'error': str(e)}
        
        # Check circuit breakers
        for name, breaker in self.circuit_breakers.items():
            health_status['components'][f'{name}_circuit_breaker'] = {
                'status': breaker.state.value,
                'consecutive_failures': breaker.consecutive_failures
            }
        
        # Overall health determination
        unhealthy_components = sum(
            1 for comp in health_status['components'].values()
            if comp.get('status') in ['unhealthy', 'open']
        )
        
        if unhealthy_components == 0:
            health_status['pipeline_status'] = 'healthy'
        elif unhealthy_components < len(health_status['components']) / 2:
            health_status['pipeline_status'] = 'degraded'
        else:
            health_status['pipeline_status'] = 'unhealthy'
        
        return health_status
    
    async def shutdown(self):
        """Gracefully shutdown the pipeline"""
        try:
            self.logger.info("🛑 Shutting down Data Acquisition Pipeline...")
            
            # Shutdown data source clients
            for client in self.clients.values():
                if hasattr(client, 'shutdown'):
                    await client.shutdown()
            
            # Shutdown async manager
            if hasattr(self.async_manager, 'shutdown'):
                await self.async_manager.shutdown()
            
            # Clear cache
            await self.cache.clear()
            
            self.initialized = False
            self.logger.info("✅ Data Acquisition Pipeline shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

# Global instance factory
_data_acquisition_pipeline = None

async def get_data_acquisition_pipeline(config: Optional[PipelineConfig] = None) -> DataAcquisitionPipeline:
    """Get the global data acquisition pipeline instance"""
    global _data_acquisition_pipeline
    
    if _data_acquisition_pipeline is None:
        _data_acquisition_pipeline = DataAcquisitionPipeline(config)
        await _data_acquisition_pipeline.initialize()
    
    return _data_acquisition_pipeline