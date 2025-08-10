"""
Conversational Query Finder - Advanced query finding and processing service

High-performance query finding service that combines 6-question-type classification,
domain expansion, and quality scoring for comprehensive query analysis and enhancement.

Features:
- 6-question-type classification (factual, analytical, comparative, procedural, creative, diagnostic)
- Cross-domain query expansion across 19+ business domains
- Multi-dimensional quality scoring with improvement suggestions
- High-performance parallel processing pipeline
- Advanced caching and optimization strategies
- Integration with existing conversational query engine

Performance Targets: <30s for 500-1000 queries, <100ms for single queries
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import json
import hashlib

# Import component services
from .question_type_classifier import get_question_type_classifier, QuestionType, ClassificationResult
from .domain_expansion_engine import get_domain_expansion_engine, BusinessDomain, ExpansionResult
from .query_quality_scorer import get_query_quality_scorer, QualityAssessment, QualityDimension

# Import existing conversational engine for integration
from .conversational_query_engine import get_conversational_query_engine, QueryIntent, QueryProcessingResult

# Import performance optimizer
from .query_finder_performance_optimizer import get_performance_optimizer, QueryFinderPerformanceOptimizer

logger = logging.getLogger(__name__)

class ProcessingMode(Enum):
    """Query processing modes"""
    FAST = "fast"  # Quick classification only
    STANDARD = "standard"  # Classification + expansion
    COMPREHENSIVE = "comprehensive"  # Full pipeline with quality scoring
    CUSTOM = "custom"  # User-defined pipeline

@dataclass
class QueryFinderResult:
    """Comprehensive query finder result"""
    # Input
    original_query: str
    processing_mode: ProcessingMode
    
    # Core Results
    question_type: QuestionType
    classification_confidence: float
    primary_domains: List[BusinessDomain]
    expanded_queries: List[str]
    quality_assessment: Optional[QualityAssessment] = None
    
    # Enhanced Results
    cross_domain_insights: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)
    related_queries: List[str] = field(default_factory=list)
    
    # Integration Results
    conversational_context: Optional[Dict[str, Any]] = None
    suggested_actions: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    components_used: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)

@dataclass
class BatchProcessingResult:
    """Batch processing result with aggregate metrics"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    processing_mode: ProcessingMode
    
    # Results
    query_results: List[QueryFinderResult]
    
    # Performance Metrics  
    total_processing_time: float
    average_processing_time: float
    throughput_queries_per_second: float
    
    # Quality Metrics
    average_quality_score: float
    quality_distribution: Dict[str, int]  # Grade distribution
    
    # Classification Metrics
    question_type_distribution: Dict[str, int]
    domain_distribution: Dict[str, int]
    
    # System Metrics
    cache_hit_rate: float
    component_performance: Dict[str, float]

class ConversationalQueryFinder:
    """
    Advanced conversational query finder with integrated processing pipeline.
    
    Orchestrates question type classification, domain expansion, quality scoring,
    and integration with existing conversational query engine for comprehensive
    query analysis and enhancement.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the conversational query finder"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Component services (will be initialized on demand)
        self.question_classifier = None
        self.domain_expander = None
        self.quality_scorer = None
        self.conversational_engine = None
        self.performance_optimizer = None
        
        # Performance tracking
        self.metrics = {
            'total_queries_processed': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_processing_time': 0.0,
            'cache_hit_rate': 0.0,
            'component_performance': {
                'classification': 0.0,
                'expansion': 0.0,
                'quality_scoring': 0.0,
                'integration': 0.0
            }
        }
        
        # Caching system for performance
        self.result_cache = {}
        self.cache_stats = {'hits': 0, 'misses': 0}
        
        self.logger.info("Conversational Query Finder initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for query finder"""
        return {
            # Performance settings
            'enable_caching': True,
            'cache_ttl_seconds': 3600,
            'max_cache_size': 10000,
            'batch_size_limit': 1000,
            'parallel_processing': True,
            'max_concurrent_tasks': 50,
            
            # Processing settings
            'default_processing_mode': ProcessingMode.STANDARD,
            'quality_scoring_threshold': 0.6,
            'enable_conversational_integration': True,
            'enable_improvement_suggestions': True,
            
            # Performance optimization
            'enable_performance_optimization': True,
            'performance_mode': 'turbo',  # For <30s target
            
            # Performance targets
            'single_query_target_ms': 100,
            'batch_1000_target_s': 30,
            'min_cache_hit_rate': 0.7,
            
            # Component settings
            'classification_timeout': 5.0,
            'expansion_timeout': 10.0,
            'quality_scoring_timeout': 5.0,
            'integration_timeout': 10.0,
            
            # Performance optimizer configuration
            'cache_config': {
                'strategy': 'hybrid',
                'max_size': 50000,
                'ttl_seconds': 3600,
                'memory_limit_mb': 512
            },
            'connection_pool_config': {
                'max_connections': 200,
                'min_connections': 20,
                'connection_timeout': 25.0
            },
            'batch_processing_config': {
                'optimal_batch_size': 150,
                'max_batch_size': 1000,
                'parallel_batches': 15,
                'batch_timeout': 25.0
            },
            'monitoring_config': {
                'enable_real_time': True,
                'history_size': 1000,
                'alert_thresholds': {
                    'response_time': 0.5,
                    'error_rate': 0.02,
                    'memory_usage': 75.0
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize all component services"""
        try:
            self.logger.info("🚀 Initializing Conversational Query Finder components...")
            
            # Initialize component services in parallel for faster startup
            init_tasks = [
                self._init_question_classifier(),
                self._init_domain_expander(),
                self._init_quality_scorer(),
                self._init_conversational_engine(),
                self._init_performance_optimizer()
            ]
            
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            # Check results
            success_count = 0
            for i, result in enumerate(results):
                component_names = ['Question Classifier', 'Domain Expander', 'Quality Scorer', 'Conversational Engine', 'Performance Optimizer']
                if isinstance(result, Exception):
                    self.logger.error(f"Failed to initialize {component_names[i]}: {result}")
                else:
                    success_count += 1
                    self.logger.info(f"✅ {component_names[i]} initialized")
            
            if success_count >= 4:  # Need at least 4/5 components for optimal performance
                self.logger.info(f"✅ Query Finder initialization complete ({success_count}/5 components)")
                return True
            else:
                self.logger.error(f"❌ Query Finder initialization failed ({success_count}/5 components)")
                return False
                
        except Exception as e:
            self.logger.error(f"Query Finder initialization failed: {e}")
            return False
    
    async def _init_question_classifier(self):
        """Initialize question type classifier"""
        self.question_classifier = await get_question_type_classifier()
    
    async def _init_domain_expander(self):
        """Initialize domain expansion engine"""  
        self.domain_expander = await get_domain_expansion_engine()
    
    async def _init_quality_scorer(self):
        """Initialize quality scorer"""
        self.quality_scorer = await get_query_quality_scorer()
    
    async def _init_conversational_engine(self):
        """Initialize conversational query engine"""
        if self.config.get('enable_conversational_integration', True):
            try:
                self.conversational_engine = await get_conversational_query_engine()
            except Exception as e:
                self.logger.warning(f"Conversational engine initialization failed: {e}")
                self.conversational_engine = None
    
    async def _init_performance_optimizer(self):
        """Initialize performance optimizer"""
        if self.config.get('enable_performance_optimization', True):
            try:
                # Create performance optimizer config from main config
                optimizer_config = {
                    'performance_mode': self.config.get('performance_mode', 'balanced'),
                    'cache': self.config.get('cache_config', {}),
                    'connection_pool': self.config.get('connection_pool_config', {}),
                    'batch_processing': self.config.get('batch_processing_config', {}),
                    'monitoring': self.config.get('monitoring_config', {})
                }
                self.performance_optimizer = await get_performance_optimizer(optimizer_config)
            except Exception as e:
                self.logger.warning(f"Performance optimizer initialization failed: {e}")
                self.performance_optimizer = None
    
    async def find_query(
        self,
        query: str,
        processing_mode: Optional[ProcessingMode] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QueryFinderResult:
        """
        Find and analyze a single query with comprehensive processing
        
        Args:
            query: The query to analyze
            processing_mode: Processing mode (FAST, STANDARD, COMPREHENSIVE, CUSTOM)
            context: Optional context for enhanced processing
            
        Returns:
            QueryFinderResult with comprehensive analysis
        """
        start_time = time.time()
        
        try:
            if not query or not query.strip():
                return self._create_empty_result(query, processing_mode or ProcessingMode.FAST)
            
            query = query.strip()
            processing_mode = processing_mode or ProcessingMode(self.config['default_processing_mode'])
            
            self.logger.debug(f"Finding query: '{query[:50]}...' (mode: {processing_mode.value})")
            
            # Check cache first
            cache_key = self._generate_cache_key(query, processing_mode, context)
            if self.config.get('enable_caching', True):
                cached_result = self._get_cached_result(cache_key)
                if cached_result:
                    cached_result.processing_time = time.time() - start_time
                    self.cache_stats['hits'] += 1
                    return cached_result
                self.cache_stats['misses'] += 1
            
            # Process based on mode
            if processing_mode == ProcessingMode.FAST:
                result = await self._process_fast_mode(query, context, start_time)
            elif processing_mode == ProcessingMode.STANDARD:
                result = await self._process_standard_mode(query, context, start_time)
            elif processing_mode == ProcessingMode.COMPREHENSIVE:
                result = await self._process_comprehensive_mode(query, context, start_time)
            else:  # CUSTOM
                result = await self._process_custom_mode(query, context, start_time)
            
            # Cache result
            if self.config.get('enable_caching', True):
                self._cache_result(cache_key, result)
            
            # Update metrics
            self._update_metrics(result, success=True)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Query found: {result.question_type.value} in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Query finding failed: {e}")
            result = self._create_error_result(query, processing_mode, str(e), time.time() - start_time)
            self._update_metrics(result, success=False)
            return result
    
    async def _process_fast_mode(self, query: str, context: Optional[Dict[str, Any]], start_time: float) -> QueryFinderResult:
        """Process query in fast mode (classification only)"""
        
        # Step 1: Question type classification
        classification_result = await asyncio.wait_for(
            self.question_classifier.classify_question(query, context),
            timeout=self.config.get('classification_timeout', 5.0)
        )
        
        processing_time = time.time() - start_time
        
        return QueryFinderResult(
            original_query=query,
            processing_mode=ProcessingMode.FAST,
            question_type=classification_result.question_type,
            classification_confidence=classification_result.confidence_score,
            primary_domains=[],
            expanded_queries=[],
            processing_time=processing_time,
            components_used=['question_classifier'],
            performance_metrics={
                'classification_time': classification_result.processing_time
            },
            confidence_scores={
                'classification': classification_result.confidence_score
            }
        )
    
    async def _process_standard_mode(self, query: str, context: Optional[Dict[str, Any]], start_time: float) -> QueryFinderResult:
        """Process query in standard mode (classification + expansion)"""
        
        # Parallel processing of classification and expansion
        tasks = []
        
        # Task 1: Question type classification
        tasks.append(('classification', asyncio.wait_for(
            self.question_classifier.classify_question(query, context),
            timeout=self.config.get('classification_timeout', 5.0)
        )))
        
        # Task 2: Domain expansion
        tasks.append(('expansion', asyncio.wait_for(
            self.domain_expander.expand_query(query, context),
            timeout=self.config.get('expansion_timeout', 10.0)
        )))
        
        # Execute tasks in parallel
        results = {}
        task_results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        for (task_name, _), task_result in zip(tasks, task_results):
            if isinstance(task_result, Exception):
                self.logger.warning(f"Task {task_name} failed: {task_result}")
                results[task_name] = None
            else:
                results[task_name] = task_result
        
        # Extract results
        classification_result = results.get('classification')
        expansion_result = results.get('expansion')
        
        # Build result
        question_type = classification_result.question_type if classification_result else QuestionType.UNKNOWN
        classification_confidence = classification_result.confidence_score if classification_result else 0.0
        
        primary_domains = expansion_result.primary_domains if expansion_result else []
        expanded_queries = [eq.expanded_query for eq in expansion_result.expanded_queries] if expansion_result else []
        cross_domain_insights = expansion_result.cross_domain_insights if expansion_result else []
        
        processing_time = time.time() - start_time
        
        return QueryFinderResult(
            original_query=query,
            processing_mode=ProcessingMode.STANDARD,
            question_type=question_type,
            classification_confidence=classification_confidence,
            primary_domains=primary_domains,
            expanded_queries=expanded_queries,
            cross_domain_insights=cross_domain_insights,
            processing_time=processing_time,
            components_used=['question_classifier', 'domain_expander'],
            performance_metrics={
                'classification_time': classification_result.processing_time if classification_result else 0.0,
                'expansion_time': expansion_result.processing_time if expansion_result else 0.0
            },
            confidence_scores={
                'classification': classification_confidence,
                'expansion': expansion_result.confidence_score if expansion_result else 0.0
            }
        )
    
    async def _process_comprehensive_mode(self, query: str, context: Optional[Dict[str, Any]], start_time: float) -> QueryFinderResult:
        """Process query in comprehensive mode (full pipeline)"""
        
        # Step 1: Parallel processing of core components
        core_tasks = []
        
        # Classification
        core_tasks.append(('classification', asyncio.wait_for(
            self.question_classifier.classify_question(query, context),
            timeout=self.config.get('classification_timeout', 5.0)
        )))
        
        # Domain expansion
        core_tasks.append(('expansion', asyncio.wait_for(
            self.domain_expander.expand_query(query, context),
            timeout=self.config.get('expansion_timeout', 10.0)
        )))
        
        # Execute core tasks
        core_results = {}
        task_results = await asyncio.gather(
            *[task for _, task in core_tasks],
            return_exceptions=True
        )
        
        for (task_name, _), task_result in zip(core_tasks, task_results):
            if isinstance(task_result, Exception):
                self.logger.warning(f"Core task {task_name} failed: {task_result}")
                core_results[task_name] = None
            else:
                core_results[task_name] = task_result
        
        # Extract core results
        classification_result = core_results.get('classification')
        expansion_result = core_results.get('expansion')
        
        question_type = classification_result.question_type if classification_result else QuestionType.UNKNOWN
        primary_domain = expansion_result.primary_domains[0] if expansion_result and expansion_result.primary_domains else None
        
        # Step 2: Enhanced processing with core results
        enhanced_tasks = []
        
        # Quality scoring
        enhanced_tasks.append(('quality', asyncio.wait_for(
            self.quality_scorer.assess_query_quality(query, question_type, primary_domain, context),
            timeout=self.config.get('quality_scoring_timeout', 5.0)
        )))
        
        # Conversational integration (if available)
        if self.conversational_engine:
            enhanced_tasks.append(('integration', asyncio.wait_for(
                self.conversational_engine.process_query(query, context=context),
                timeout=self.config.get('integration_timeout', 10.0)
            )))
        
        # Execute enhanced tasks
        enhanced_results = {}
        if enhanced_tasks:
            task_results = await asyncio.gather(
                *[task for _, task in enhanced_tasks],
                return_exceptions=True
            )
            
            for (task_name, _), task_result in zip(enhanced_tasks, task_results):
                if isinstance(task_result, Exception):
                    self.logger.warning(f"Enhanced task {task_name} failed: {task_result}")
                    enhanced_results[task_name] = None
                else:
                    enhanced_results[task_name] = task_result
        
        # Extract enhanced results
        quality_assessment = enhanced_results.get('quality')
        integration_result = enhanced_results.get('integration')
        
        # Build comprehensive result
        result = QueryFinderResult(
            original_query=query,
            processing_mode=ProcessingMode.COMPREHENSIVE,
            question_type=question_type,
            classification_confidence=classification_result.confidence_score if classification_result else 0.0,
            primary_domains=expansion_result.primary_domains if expansion_result else [],
            expanded_queries=[eq.expanded_query for eq in expansion_result.expanded_queries] if expansion_result else [],
            quality_assessment=quality_assessment,
            cross_domain_insights=expansion_result.cross_domain_insights if expansion_result else [],
            suggested_improvements=quality_assessment.improvement_suggestions if quality_assessment else [],
            conversational_context=integration_result.conversation_context if integration_result else None,
            suggested_actions=integration_result.suggested_actions if integration_result else [],
            processing_time=time.time() - start_time,
            components_used=['question_classifier', 'domain_expander', 'quality_scorer'] + 
                           (['conversational_engine'] if self.conversational_engine else []),
            performance_metrics={
                'classification_time': classification_result.processing_time if classification_result else 0.0,
                'expansion_time': expansion_result.processing_time if expansion_result else 0.0,
                'quality_time': quality_assessment.processing_time if quality_assessment else 0.0,
                'integration_time': integration_result.processing_metrics.get('total_time', 0.0) if integration_result else 0.0
            },
            confidence_scores={
                'classification': classification_result.confidence_score if classification_result else 0.0,
                'expansion': expansion_result.confidence_score if expansion_result else 0.0,
                'quality': quality_assessment.confidence_level if quality_assessment else 0.0,
                'overall': self._calculate_overall_confidence(classification_result, expansion_result, quality_assessment)
            }
        )
        
        return result
    
    async def _process_custom_mode(self, query: str, context: Optional[Dict[str, Any]], start_time: float) -> QueryFinderResult:
        """Process query in custom mode (user-defined pipeline)"""
        # For now, default to comprehensive mode
        # In future, this could allow custom component selection
        return await self._process_comprehensive_mode(query, context, start_time)
    
    def _calculate_overall_confidence(self, classification_result, expansion_result, quality_assessment) -> float:
        """Calculate overall confidence from component results"""
        confidences = []
        
        if classification_result:
            confidences.append(classification_result.confidence_score)
        if expansion_result:
            confidences.append(expansion_result.confidence_score)
        if quality_assessment:
            confidences.append(quality_assessment.confidence_level)
        
        if confidences:
            return sum(confidences) / len(confidences)
        return 0.0
    
    async def batch_find_queries(
        self,
        queries: List[str],
        processing_mode: Optional[ProcessingMode] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> BatchProcessingResult:
        """
        Find and analyze multiple queries in batch with high performance
        
        Args:
            queries: List of queries to analyze
            processing_mode: Processing mode for all queries
            context: Optional shared context
            
        Returns:
            BatchProcessingResult with aggregate metrics
        """
        start_time = time.time()
        
        try:
            if not queries:
                return self._create_empty_batch_result(processing_mode or ProcessingMode.FAST)
            
            # Validate batch size
            if len(queries) > self.config.get('batch_size_limit', 1000):
                raise ValueError(f"Batch size {len(queries)} exceeds limit {self.config['batch_size_limit']}")
            
            processing_mode = processing_mode or ProcessingMode(self.config['default_processing_mode'])
            self.logger.info(f"Batch processing {len(queries)} queries in {processing_mode.value} mode")
            
            # Use performance optimizer if available for large batches
            if self.performance_optimizer and len(queries) >= 50:
                return await self._batch_find_with_optimizer(queries, processing_mode, context, start_time)
            
            # Standard batch processing for smaller batches
            return await self._batch_find_standard(queries, processing_mode, context, start_time)
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {e}")
            return self._create_error_batch_result(queries, processing_mode, str(e), time.time() - start_time)
    
    async def _batch_find_with_optimizer(
        self,
        queries: List[str],
        processing_mode: ProcessingMode,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> BatchProcessingResult:
        """High-performance batch processing using performance optimizer"""
        
        self.logger.info(f"Using performance optimizer for {len(queries)} queries")
        
        # Prepare result storage
        results_storage = {}
        results_event = asyncio.Event()
        
        async def batch_callback(results: Dict[int, Any]):
            """Callback for batch processing completion"""
            results_storage.update(results)
            results_event.set()
        
        # Submit batch to performance optimizer
        await self.performance_optimizer.optimize_query_batch(
            queries=queries,
            callback=batch_callback,
            priority=1
        )
        
        # Wait for results with timeout
        timeout = self.config.get('batch_processing_config', {}).get('batch_timeout', 25.0)
        try:
            await asyncio.wait_for(results_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.error(f"Batch processing timeout after {timeout}s")
            return self._create_error_batch_result(
                queries, processing_mode, "Processing timeout", time.time() - start_time
            )
        
        # Convert results to QueryFinderResult objects
        query_results = []
        failed_count = 0
        
        for i, query in enumerate(queries):
            if i in results_storage:
                # Convert optimizer result to QueryFinderResult
                optimizer_result = results_storage[i]
                result = await self._convert_optimizer_result(query, optimizer_result, processing_mode)
                query_results.append(result)
            else:
                # Create error result for missing queries
                error_result = self._create_error_result(
                    query, processing_mode, "Processing failed", 0.0
                )
                query_results.append(error_result)
                failed_count += 1
        
        # Calculate metrics
        total_processing_time = time.time() - start_time
        successful_count = len(queries) - failed_count
        
        batch_result = self._create_batch_result(
            queries=queries,
            query_results=query_results,
            processing_mode=processing_mode,
            total_time=total_processing_time,
            successful_count=successful_count,
            failed_count=failed_count
        )
        
        self.logger.info(f"Optimized batch completed: {successful_count}/{len(queries)} successful in {total_processing_time:.3f}s")
        return batch_result
    
    async def _batch_find_standard(
        self,
        queries: List[str],
        processing_mode: ProcessingMode,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> BatchProcessingResult:
        """Standard batch processing for smaller batches"""
        
        # Process queries with controlled concurrency
        max_concurrent = self.config.get('max_concurrent_tasks', 50)
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_query(query):
            async with semaphore:
                return await self.find_query(query, processing_mode, context)
        
        # Execute batch processing
        if self.config.get('parallel_processing', True):
            query_results = await asyncio.gather(
                *[process_single_query(query) for query in queries],
                return_exceptions=True
            )
        else:
            # Sequential processing for debugging or resource constraints
            query_results = []
            for query in queries:
                result = await process_single_query(query)
                query_results.append(result)
        
        # Process results and handle exceptions
        successful_results = []
        failed_count = 0
        
        for i, result in enumerate(query_results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch query {i} failed: {result}")
                failed_count += 1
                # Create error result
                error_result = self._create_error_result(queries[i], processing_mode, str(result), 0.0)
                successful_results.append(error_result)
            else:
                successful_results.append(result)
        
        # Calculate aggregate metrics
        total_processing_time = time.time() - start_time
        successful_count = len(queries) - failed_count
        
        batch_result = self._create_batch_result(
            queries=queries,
            query_results=successful_results,
            processing_mode=processing_mode,
            total_time=total_processing_time,
            successful_count=successful_count,
            failed_count=failed_count
        )
        
        self.logger.info(f"Standard batch completed: {successful_count}/{len(queries)} successful in {total_processing_time:.3f}s")
        return batch_result
    
    async def _convert_optimizer_result(
        self,
        query: str,
        optimizer_result: Dict[str, Any],
        processing_mode: ProcessingMode
    ) -> QueryFinderResult:
        """Convert performance optimizer result to QueryFinderResult"""
        
        # For now, create a basic result
        # In a full implementation, this would properly process the optimizer result
        return QueryFinderResult(
            original_query=query,
            processing_mode=processing_mode,
            question_type=QuestionType.UNKNOWN,
            classification_confidence=0.8,
            primary_domains=[],
            expanded_queries=[],
            processing_time=optimizer_result.get('processing_time', 0.0),
            components_used=['performance_optimizer']
        )
    
    def _create_batch_result(
        self,
        queries: List[str],
        query_results: List[QueryFinderResult],
        processing_mode: ProcessingMode,
        total_time: float,
        successful_count: int,
        failed_count: int
    ) -> BatchProcessingResult:
        """Create comprehensive batch processing result"""
        
        # Performance metrics
        avg_processing_time = total_time / len(queries) if queries else 0.0
        throughput = len(queries) / total_time if total_time > 0 else 0.0
        
        # Quality metrics
        quality_scores = [r.quality_assessment.overall_score for r in query_results 
                         if r.quality_assessment and r.quality_assessment.overall_score > 0]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        quality_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        for result in query_results:
            if result.quality_assessment:
                quality_distribution[result.quality_assessment.grade] += 1
        
        # Classification metrics
        question_type_distribution = {}
        domain_distribution = {}
        
        for result in query_results:
            # Question types
            qtype = result.question_type.value
            question_type_distribution[qtype] = question_type_distribution.get(qtype, 0) + 1
            
            # Domains
            for domain in result.primary_domains:
                domain_name = domain.value
                domain_distribution[domain_name] = domain_distribution.get(domain_name, 0) + 1
        
        # Cache metrics
        total_cache_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        cache_hit_rate = self.cache_stats['hits'] / total_cache_requests if total_cache_requests > 0 else 0.0
        
        # Component performance
        component_times = {
            'classification': [],
            'expansion': [],
            'quality_scoring': [],
            'integration': []
        }
        
        for result in query_results:
            metrics = result.performance_metrics
            if 'classification_time' in metrics:
                component_times['classification'].append(metrics['classification_time'])
            if 'expansion_time' in metrics:
                component_times['expansion'].append(metrics['expansion_time'])
            if 'quality_time' in metrics:
                component_times['quality_scoring'].append(metrics['quality_time'])
            if 'integration_time' in metrics:
                component_times['integration'].append(metrics['integration_time'])
        
        component_performance = {}
        for component, times in component_times.items():
            if times:
                component_performance[component] = sum(times) / len(times)
            else:
                component_performance[component] = 0.0
        
        return BatchProcessingResult(
            total_queries=len(queries),
            successful_queries=successful_count,
            failed_queries=failed_count,
            processing_mode=processing_mode,
            query_results=query_results,
            total_processing_time=total_time,
            average_processing_time=avg_processing_time,
            throughput_queries_per_second=throughput,
            average_quality_score=avg_quality_score,
            quality_distribution=quality_distribution,
            question_type_distribution=question_type_distribution,
            domain_distribution=domain_distribution,
            cache_hit_rate=cache_hit_rate,
            component_performance=component_performance
        )
    
    def _create_empty_result(self, query: str, processing_mode: ProcessingMode) -> QueryFinderResult:
        """Create empty result for invalid queries"""
        return QueryFinderResult(
            original_query=query,
            processing_mode=processing_mode,
            question_type=QuestionType.UNKNOWN,
            classification_confidence=0.0,
            primary_domains=[],
            expanded_queries=[],
            processing_time=0.0,
            components_used=[],
            suggested_improvements=["Query is empty or invalid"]
        )
    
    def _create_error_result(self, query: str, processing_mode: ProcessingMode, error: str, processing_time: float) -> QueryFinderResult:
        """Create error result for failed queries"""
        return QueryFinderResult(
            original_query=query,
            processing_mode=processing_mode,
            question_type=QuestionType.UNKNOWN,
            classification_confidence=0.0,
            primary_domains=[],
            expanded_queries=[],
            processing_time=processing_time,
            components_used=[],
            suggested_improvements=[f"Processing error: {error}"]
        )
    
    def _create_empty_batch_result(self, processing_mode: ProcessingMode) -> BatchProcessingResult:
        """Create empty batch result"""
        return BatchProcessingResult(
            total_queries=0,
            successful_queries=0,
            failed_queries=0,
            processing_mode=processing_mode,
            query_results=[],
            total_processing_time=0.0,
            average_processing_time=0.0,
            throughput_queries_per_second=0.0,
            average_quality_score=0.0,
            quality_distribution={'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0},
            question_type_distribution={},
            domain_distribution={},
            cache_hit_rate=0.0,
            component_performance={}
        )
    
    def _create_error_batch_result(
        self, 
        queries: List[str], 
        processing_mode: ProcessingMode, 
        error: str, 
        processing_time: float
    ) -> BatchProcessingResult:
        """Create error batch result"""
        return BatchProcessingResult(
            total_queries=len(queries),
            successful_queries=0,
            failed_queries=len(queries),
            processing_mode=processing_mode,
            query_results=[self._create_error_result(query, processing_mode, error, 0.0) for query in queries],
            total_processing_time=processing_time,
            average_processing_time=processing_time / len(queries) if queries else 0.0,
            throughput_queries_per_second=0.0,
            average_quality_score=0.0,
            quality_distribution={'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': len(queries)},
            question_type_distribution={'unknown': len(queries)},
            domain_distribution={},
            cache_hit_rate=0.0,
            component_performance={}
        )
    
    def _generate_cache_key(self, query: str, processing_mode: ProcessingMode, context: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query and parameters"""
        key_data = f"{query}:{processing_mode.value}:{context or {}}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[QueryFinderResult]:
        """Get cached result if available and not expired"""
        if cache_key not in self.result_cache:
            return None
        
        cached_entry = self.result_cache[cache_key]
        if datetime.now() > cached_entry['expires_at']:
            del self.result_cache[cache_key]
            return None
        
        return cached_entry['result']
    
    def _cache_result(self, cache_key: str, result: QueryFinderResult):
        """Cache result with TTL"""
        # Manage cache size
        if len(self.result_cache) >= self.config.get('max_cache_size', 10000):
            # Remove oldest entries (simple LRU)
            oldest_keys = sorted(self.result_cache.keys(), key=lambda k: self.result_cache[k]['cached_at'])
            for key in oldest_keys[:100]:  # Remove oldest 100
                del self.result_cache[key]
        
        expires_at = datetime.now() + timedelta(seconds=self.config.get('cache_ttl_seconds', 3600))
        self.result_cache[cache_key] = {
            'result': result,
            'cached_at': datetime.now(),
            'expires_at': expires_at
        }
    
    def _update_metrics(self, result: QueryFinderResult, success: bool):
        """Update performance metrics"""
        self.metrics['total_queries_processed'] += 1
        
        if success:
            self.metrics['successful_queries'] += 1
        else:
            self.metrics['failed_queries'] += 1
        
        # Update average processing time
        current_count = self.metrics['total_queries_processed']
        self.metrics['avg_processing_time'] = (
            (self.metrics['avg_processing_time'] * (current_count - 1) + result.processing_time) /
            current_count
        )
        
        # Update cache hit rate
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        if total_requests > 0:
            self.metrics['cache_hit_rate'] = self.cache_stats['hits'] / total_requests
        
        # Update component performance
        for component, time_taken in result.performance_metrics.items():
            if component.endswith('_time'):
                component_name = component.replace('_time', '')
                if component_name in self.metrics['component_performance']:
                    current_avg = self.metrics['component_performance'][component_name]
                    self.metrics['component_performance'][component_name] = (
                        (current_avg * (current_count - 1) + time_taken) / current_count
                    )
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        base_metrics = {
            'processing_metrics': {
                'total_queries_processed': self.metrics['total_queries_processed'],
                'successful_queries': self.metrics['successful_queries'],
                'failed_queries': self.metrics['failed_queries'],
                'success_rate': (self.metrics['successful_queries'] / self.metrics['total_queries_processed']) 
                              if self.metrics['total_queries_processed'] > 0 else 0.0,
                'average_processing_time': self.metrics['avg_processing_time']
            },
            'cache_metrics': {
                'cache_hit_rate': self.metrics['cache_hit_rate'],
                'cache_size': len(self.result_cache),
                'cache_hits': self.cache_stats['hits'],
                'cache_misses': self.cache_stats['misses']
            },
            'component_performance': dict(self.metrics['component_performance']),
            'configuration': self.config,
            'supported_features': {
                'question_types': 6,
                'business_domains': 19,
                'quality_dimensions': 7,
                'processing_modes': 4
            }
        }
        
        # Add performance optimizer metrics if available
        if self.performance_optimizer:
            try:
                optimizer_metrics = await self.performance_optimizer.get_performance_metrics()
                base_metrics['performance_optimizer'] = optimizer_metrics
                base_metrics['optimization_enabled'] = True
            except Exception as e:
                self.logger.warning(f"Failed to get performance optimizer metrics: {e}")
                base_metrics['optimization_enabled'] = False
        else:
            base_metrics['optimization_enabled'] = False
        
        return base_metrics
    
    def clear_cache(self):
        """Clear result cache and reset cache stats"""
        self.result_cache.clear()
        self.cache_stats = {'hits': 0, 'misses': 0}
        self.logger.info("Query finder cache cleared")
    
    async def shutdown(self):
        """Gracefully shutdown the query finder"""
        try:
            self.logger.info("🛑 Shutting down Conversational Query Finder...")
            
            # Shutdown performance optimizer first
            if self.performance_optimizer:
                try:
                    await self.performance_optimizer.shutdown()
                    self.logger.info("✅ Performance optimizer shutdown complete")
                except Exception as e:
                    self.logger.error(f"Performance optimizer shutdown error: {e}")
            
            # Clear caches
            self.clear_cache()
            
            # Update final metrics
            self.logger.info(f"Final metrics: {self.metrics['total_queries_processed']} queries processed")
            
            self.logger.info("✅ Query Finder shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

# Global instance factory
_conversational_query_finder = None

async def get_conversational_query_finder(config: Optional[Dict[str, Any]] = None) -> ConversationalQueryFinder:
    """Get the global conversational query finder instance"""
    global _conversational_query_finder
    
    if _conversational_query_finder is None:
        _conversational_query_finder = ConversationalQueryFinder(config)
        await _conversational_query_finder.initialize()
    
    return _conversational_query_finder