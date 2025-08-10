"""
Query Finder Performance Optimizer - High-performance optimization engine

Advanced performance optimization system for conversational query finder to achieve
<30s response time for 500-1000 queries through intelligent caching, resource 
management, and parallel processing optimization.

Features:
- Connection pooling and resource management
- Advanced caching strategies with TTL and LRU
- Batch processing optimization and queue management
- Pre-computation and pattern indexing
- Real-time performance monitoring and bottleneck detection
- Memory management and garbage collection optimization
- Adaptive concurrency control and load balancing

Performance Targets: <30s for 1000 queries, <100ms for single queries
"""

import asyncio
import logging
import time
import threading
import weakref
import gc
import psutil
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import hashlib
from enum import Enum
import statistics

# Import performance monitoring tools
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    UVLOOP_AVAILABLE = False

logger = logging.getLogger(__name__)

class PerformanceMode(Enum):
    """Performance optimization modes"""
    ECO = "eco"           # Resource-conscious mode
    BALANCED = "balanced"  # Balanced performance and resources
    TURBO = "turbo"       # Maximum performance mode
    ADAPTIVE = "adaptive"  # Dynamic adaptation based on load

class CacheStrategy(Enum):
    """Caching strategies"""
    LRU = "lru"           # Least Recently Used
    TTL = "ttl"           # Time To Live
    HYBRID = "hybrid"     # LRU + TTL combination
    ADAPTIVE = "adaptive" # Dynamic cache sizing

@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""
    queries_per_second: float = 0.0
    average_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    active_connections: int = 0
    queue_size: int = 0
    error_rate: float = 0.0
    bottleneck_indicators: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class ResourcePool:
    """Resource pool configuration"""
    max_connections: int = 100
    min_connections: int = 10
    connection_timeout: float = 30.0
    max_queue_size: int = 1000
    cleanup_interval: float = 60.0

@dataclass
class CacheConfig:
    """Advanced caching configuration"""
    strategy: CacheStrategy = CacheStrategy.HYBRID
    max_size: int = 50000
    ttl_seconds: int = 3600
    cleanup_interval: float = 300.0
    hit_ratio_target: float = 0.85
    memory_limit_mb: int = 512

@dataclass
class BatchConfig:
    """Batch processing optimization configuration"""
    optimal_batch_size: int = 100
    max_batch_size: int = 1000
    parallel_batches: int = 10
    batch_timeout: float = 25.0
    queue_strategy: str = "priority"
    load_balancing: bool = True

class AdvancedCache:
    """High-performance caching system with multiple strategies"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = OrderedDict()
        self.access_times = {}
        self.creation_times = {}
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        self.cleanup_task = None
        
        # Start cleanup task
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cache cleanup"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cache cleanup loop"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired()
                await self._manage_memory()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache with strategy-aware access"""
        with self.lock:
            if key not in self.cache:
                self.miss_count += 1
                return None
            
            # Check TTL expiration
            if self._is_expired(key):
                del self.cache[key]
                self.access_times.pop(key, None)
                self.creation_times.pop(key, None)
                self.miss_count += 1
                return None
            
            # Update access patterns
            self.access_times[key] = time.time()
            self.hit_count += 1
            
            # Move to end for LRU
            value = self.cache.pop(key)
            self.cache[key] = value
            
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set item in cache with strategy-aware eviction"""
        with self.lock:
            current_time = time.time()
            
            # Remove existing key
            if key in self.cache:
                del self.cache[key]
            
            # Add new item
            self.cache[key] = value
            self.access_times[key] = current_time
            self.creation_times[key] = current_time
            
            # Apply size limits
            await self._enforce_size_limits()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache item is expired"""
        if key not in self.creation_times:
            return True
        
        creation_time = self.creation_times[key]
        return (time.time() - creation_time) > self.config.ttl_seconds
    
    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        with self.lock:
            expired_keys = []
            current_time = time.time()
            
            for key, creation_time in self.creation_times.items():
                if (current_time - creation_time) > self.config.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.cache.pop(key, None)
                self.access_times.pop(key, None)
                self.creation_times.pop(key, None)
    
    async def _enforce_size_limits(self):
        """Enforce cache size limits using configured strategy"""
        while len(self.cache) > self.config.max_size:
            if self.config.strategy in [CacheStrategy.LRU, CacheStrategy.HYBRID]:
                # Remove least recently used
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.access_times.pop(oldest_key, None)
                self.creation_times.pop(oldest_key, None)
            else:
                # Remove oldest by creation time
                oldest_key = min(self.creation_times.keys(), 
                               key=lambda k: self.creation_times[k])
                del self.cache[oldest_key]
                self.access_times.pop(oldest_key, None)
                self.creation_times.pop(oldest_key, None)
    
    async def _manage_memory(self):
        """Manage cache memory usage"""
        try:
            import sys
            cache_size_bytes = sys.getsizeof(self.cache)
            cache_size_mb = cache_size_bytes / (1024 * 1024)
            
            if cache_size_mb > self.config.memory_limit_mb:
                # Reduce cache size by 20%
                target_size = int(len(self.cache) * 0.8)
                while len(self.cache) > target_size:
                    await self._enforce_size_limits()
        except Exception as e:
            logger.warning(f"Memory management error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'hit_rate': hit_rate,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'memory_estimate_mb': len(self.cache) * 0.001  # Rough estimate
        }
    
    async def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.creation_times.clear()
            self.hit_count = 0
            self.miss_count = 0

class ConnectionPool:
    """High-performance connection pool"""
    
    def __init__(self, config: ResourcePool):
        self.config = config
        self.connections = asyncio.Queue(maxsize=config.max_connections)
        self.active_connections = 0
        self.lock = asyncio.Lock()
        self.initialized = False
    
    async def initialize(self):
        """Initialize connection pool with minimum connections"""
        if self.initialized:
            return
        
        async with self.lock:
            for _ in range(self.config.min_connections):
                connection = await self._create_connection()
                await self.connections.put(connection)
                self.active_connections += 1
            
            self.initialized = True
    
    async def _create_connection(self) -> Dict[str, Any]:
        """Create a new connection (placeholder implementation)"""
        return {
            'id': f"conn_{time.time()}",
            'created_at': time.time(),
            'last_used': time.time(),
            'active': True
        }
    
    async def acquire(self) -> Dict[str, Any]:
        """Acquire a connection from the pool"""
        if not self.initialized:
            await self.initialize()
        
        try:
            # Try to get existing connection
            connection = await asyncio.wait_for(
                self.connections.get(),
                timeout=self.config.connection_timeout
            )
            connection['last_used'] = time.time()
            return connection
        except asyncio.TimeoutError:
            # Create new connection if under limit
            async with self.lock:
                if self.active_connections < self.config.max_connections:
                    connection = await self._create_connection()
                    self.active_connections += 1
                    return connection
                else:
                    raise Exception("Connection pool exhausted")
    
    async def release(self, connection: Dict[str, Any]):
        """Release a connection back to the pool"""
        if connection.get('active', False):
            connection['last_used'] = time.time()
            try:
                await self.connections.put_nowait(connection)
            except asyncio.QueueFull:
                # Pool is full, close connection
                self.active_connections -= 1
    
    async def cleanup(self):
        """Clean up idle connections"""
        current_time = time.time()
        cleanup_connections = []
        
        # Collect idle connections
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                if (current_time - conn['last_used']) > self.config.cleanup_interval:
                    cleanup_connections.append(conn)
                else:
                    await self.connections.put(conn)
            except asyncio.QueueEmpty:
                break
        
        # Update connection count
        self.active_connections -= len(cleanup_connections)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            'active_connections': self.active_connections,
            'available_connections': self.connections.qsize(),
            'max_connections': self.config.max_connections,
            'pool_utilization': self.active_connections / self.config.max_connections
        }

class QueryFinderPerformanceOptimizer:
    """
    Advanced performance optimization engine for conversational query finder.
    
    Provides comprehensive performance enhancements including connection pooling,
    advanced caching, batch processing optimization, and real-time monitoring.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the performance optimizer"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Performance components
        self.cache = AdvancedCache(CacheConfig(**self.config.get('cache', {})))
        self.connection_pool = ConnectionPool(ResourcePool(**self.config.get('connection_pool', {})))
        
        # Performance monitoring
        self.metrics = PerformanceMetrics()
        self.performance_history = []
        self.bottleneck_detector = BottleneckDetector()
        
        # Optimization state
        self.performance_mode = PerformanceMode(self.config.get('performance_mode', 'balanced'))
        self.optimization_tasks = []
        self.monitoring_task = None
        
        # Pre-computation cache
        self.pattern_cache = {}
        self.query_templates = {}
        
        # Batch processing
        self.batch_queue = asyncio.Queue(maxsize=self.config.get('max_queue_size', 1000))
        self.batch_processors = []
        
        self.logger.info(f"Performance Optimizer initialized in {self.performance_mode.value} mode")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default performance optimization configuration"""
        return {
            'performance_mode': 'balanced',
            'cache': {
                'strategy': 'hybrid',
                'max_size': 50000,
                'ttl_seconds': 3600,
                'memory_limit_mb': 512
            },
            'connection_pool': {
                'max_connections': 100,
                'min_connections': 10,
                'connection_timeout': 30.0
            },
            'batch_processing': {
                'optimal_batch_size': 100,
                'max_batch_size': 1000,
                'parallel_batches': 10,
                'batch_timeout': 25.0
            },
            'monitoring': {
                'enable_real_time': True,
                'history_size': 1000,
                'alert_thresholds': {
                    'response_time': 1.0,
                    'error_rate': 0.05,
                    'memory_usage': 80.0
                }
            },
            'precomputation': {
                'enable_pattern_caching': True,
                'enable_query_templating': True,
                'background_precompute': True
            }
        }
    
    async def initialize(self):
        """Initialize performance optimization components"""
        try:
            self.logger.info("🚀 Initializing Performance Optimizer...")
            
            # Initialize connection pool
            await self.connection_pool.initialize()
            
            # Start monitoring
            if self.config.get('monitoring', {}).get('enable_real_time', True):
                self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            # Initialize batch processors
            await self._initialize_batch_processors()
            
            # Start precomputation if enabled
            if self.config.get('precomputation', {}).get('background_precompute', True):
                asyncio.create_task(self._precomputation_loop())
            
            # Set event loop policy for better performance
            if UVLOOP_AVAILABLE and self.performance_mode in [PerformanceMode.TURBO, PerformanceMode.ADAPTIVE]:
                import uvloop
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
                self.logger.info("✅ uvloop enabled for maximum performance")
            
            self.logger.info("✅ Performance Optimizer initialization complete")
            
        except Exception as e:
            self.logger.error(f"Performance optimizer initialization failed: {e}")
            raise
    
    async def _initialize_batch_processors(self):
        """Initialize batch processing workers"""
        batch_config = BatchConfig(**self.config.get('batch_processing', {}))
        
        for i in range(batch_config.parallel_batches):
            processor = asyncio.create_task(self._batch_processor_worker(f"worker_{i}"))
            self.batch_processors.append(processor)
    
    async def _batch_processor_worker(self, worker_id: str):
        """Batch processor worker for parallel processing"""
        self.logger.info(f"Batch processor {worker_id} started")
        
        while True:
            try:
                # Get batch from queue
                batch_data = await self.batch_queue.get()
                
                if batch_data is None:  # Shutdown signal
                    break
                
                # Process batch
                start_time = time.time()
                await self._process_batch(batch_data, worker_id)
                processing_time = time.time() - start_time
                
                # Update performance metrics
                self._update_batch_metrics(processing_time, len(batch_data.get('queries', [])))
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Batch processor {worker_id} error: {e}")
    
    async def _process_batch(self, batch_data: Dict[str, Any], worker_id: str):
        """Process a batch of queries with optimization"""
        queries = batch_data.get('queries', [])
        callback = batch_data.get('callback')
        
        if not queries or not callback:
            return
        
        try:
            # Check cache for batch results
            cached_results = await self._get_cached_batch_results(queries)
            
            # Identify queries that need processing
            uncached_queries = []
            results = {}
            
            for i, query in enumerate(queries):
                cache_key = self._generate_query_cache_key(query)
                if cache_key in cached_results:
                    results[i] = cached_results[cache_key]
                else:
                    uncached_queries.append((i, query))
            
            # Process uncached queries
            if uncached_queries:
                processed_results = await self._process_uncached_queries(uncached_queries)
                results.update(processed_results)
                
                # Cache new results
                await self._cache_batch_results(uncached_queries, processed_results)
            
            # Execute callback with results
            if callback:
                await callback(results)
                
        except Exception as e:
            self.logger.error(f"Batch processing failed in {worker_id}: {e}")
    
    async def _get_cached_batch_results(self, queries: List[str]) -> Dict[str, Any]:
        """Get cached results for batch queries"""
        cached_results = {}
        
        for query in queries:
            cache_key = self._generate_query_cache_key(query)
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                cached_results[cache_key] = cached_result
        
        return cached_results
    
    async def _process_uncached_queries(self, uncached_queries: List[Tuple[int, str]]) -> Dict[int, Any]:
        """Process queries that weren't found in cache"""
        # This would integrate with the actual query finder
        # For now, return placeholder results
        results = {}
        
        for index, query in uncached_queries:
            # Placeholder processing
            results[index] = {
                'query': query,
                'processed': True,
                'timestamp': time.time()
            }
        
        return results
    
    async def _cache_batch_results(self, uncached_queries: List[Tuple[int, str]], results: Dict[int, Any]):
        """Cache results from batch processing"""
        for index, query in uncached_queries:
            if index in results:
                cache_key = self._generate_query_cache_key(query)
                await self.cache.set(cache_key, results[index])
    
    def _generate_query_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(f"query:{query}".encode()).hexdigest()
    
    async def _monitoring_loop(self):
        """Real-time performance monitoring loop"""
        while True:
            try:
                await asyncio.sleep(1.0)  # Monitor every second
                
                # Collect current metrics
                current_metrics = await self._collect_performance_metrics()
                self.metrics = current_metrics
                
                # Store in history
                self.performance_history.append({
                    'timestamp': time.time(),
                    'metrics': current_metrics
                })
                
                # Trim history
                max_history = self.config.get('monitoring', {}).get('history_size', 1000)
                if len(self.performance_history) > max_history:
                    self.performance_history = self.performance_history[-max_history:]
                
                # Detect bottlenecks
                await self.bottleneck_detector.analyze(current_metrics)
                
                # Adaptive optimization
                if self.performance_mode == PerformanceMode.ADAPTIVE:
                    await self._adaptive_optimization(current_metrics)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
    
    async def _collect_performance_metrics(self) -> PerformanceMetrics:
        """Collect comprehensive performance metrics"""
        try:
            # System metrics
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_usage_mb = memory_info.rss / (1024 * 1024)
            cpu_usage = process.cpu_percent()
            
            # Cache metrics
            cache_stats = self.cache.get_stats()
            
            # Connection pool metrics
            pool_stats = self.connection_pool.get_stats()
            
            # Calculate queries per second from recent history
            qps = self._calculate_queries_per_second()
            
            # Calculate average response time
            avg_response_time = self._calculate_average_response_time()
            
            return PerformanceMetrics(
                queries_per_second=qps,
                average_response_time=avg_response_time,
                cache_hit_rate=cache_stats['hit_rate'],
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage,
                active_connections=pool_stats['active_connections'],
                queue_size=self.batch_queue.qsize(),
                error_rate=0.0,  # Would be calculated from actual error tracking
                bottleneck_indicators=[],
                optimization_suggestions=[]
            )
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            return PerformanceMetrics()
    
    def _calculate_queries_per_second(self) -> float:
        """Calculate queries per second from recent history"""
        if len(self.performance_history) < 2:
            return 0.0
        
        # Use last 10 seconds of data
        current_time = time.time()
        recent_history = [
            h for h in self.performance_history 
            if current_time - h['timestamp'] <= 10
        ]
        
        if len(recent_history) < 2:
            return 0.0
        
        # Simple calculation based on history points
        return len(recent_history) / 10.0
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time from recent operations"""
        if not self.performance_history:
            return 0.0
        
        # Use last 30 seconds of data
        current_time = time.time()
        recent_times = []
        
        for history_point in self.performance_history:
            if current_time - history_point['timestamp'] <= 30:
                # Would extract actual response times from metrics
                recent_times.append(0.1)  # Placeholder
        
        return statistics.mean(recent_times) if recent_times else 0.0
    
    async def _adaptive_optimization(self, metrics: PerformanceMetrics):
        """Adaptive performance optimization based on current metrics"""
        try:
            # Adjust cache size based on hit rate
            if metrics.cache_hit_rate < 0.8:
                # Increase cache size if memory allows
                if metrics.memory_usage_mb < 400:
                    self.cache.config.max_size = min(self.cache.config.max_size * 1.2, 100000)
            
            # Adjust batch size based on throughput
            if metrics.queries_per_second < 50:
                # Reduce batch size for better responsiveness
                batch_config = self.config.get('batch_processing', {})
                batch_config['optimal_batch_size'] = max(batch_config.get('optimal_batch_size', 100) * 0.8, 10)
            
            # Memory pressure response
            if metrics.memory_usage_mb > 600:
                await self.cache.clear()
                gc.collect()
                self.logger.info("Memory pressure detected - cache cleared")
            
        except Exception as e:
            self.logger.error(f"Adaptive optimization error: {e}")
    
    async def _precomputation_loop(self):
        """Background precomputation for common patterns"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Precompute common query patterns
                await self._precompute_query_patterns()
                
                # Precompute domain mappings
                await self._precompute_domain_mappings()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Precomputation error: {e}")
    
    async def _precompute_query_patterns(self):
        """Precompute common query patterns"""
        common_patterns = [
            "how to", "what is", "compare", "best practices",
            "create", "implement", "optimize", "analyze"
        ]
        
        for pattern in common_patterns:
            cache_key = f"pattern:{pattern}"
            if not await self.cache.get(cache_key):
                # Generate pattern analysis
                pattern_data = {
                    'pattern': pattern,
                    'classification': 'procedural' if pattern == 'how to' else 'factual',
                    'precomputed_at': time.time()
                }
                await self.cache.set(cache_key, pattern_data)
    
    async def _precompute_domain_mappings(self):
        """Precompute domain expansion mappings"""
        common_domains = [
            'marketing', 'technology', 'finance', 'sales', 'operations'
        ]
        
        for domain in common_domains:
            cache_key = f"domain:{domain}"
            if not await self.cache.get(cache_key):
                domain_data = {
                    'domain': domain,
                    'related_domains': [],
                    'keywords': [],
                    'precomputed_at': time.time()
                }
                await self.cache.set(cache_key, domain_data)
    
    def _update_batch_metrics(self, processing_time: float, batch_size: int):
        """Update batch processing metrics"""
        # Update internal metrics tracking
        pass
    
    async def optimize_query_batch(
        self, 
        queries: List[str], 
        callback: Callable,
        priority: int = 0
    ):
        """Submit batch for optimized processing"""
        batch_data = {
            'queries': queries,
            'callback': callback,
            'priority': priority,
            'submitted_at': time.time()
        }
        
        try:
            await self.batch_queue.put(batch_data)
            self.logger.debug(f"Batch of {len(queries)} queries submitted for processing")
        except asyncio.QueueFull:
            self.logger.warning("Batch queue full - consider scaling up processors")
            raise Exception("Query processing queue is full")
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        cache_stats = self.cache.get_stats()
        pool_stats = self.connection_pool.get_stats()
        
        return {
            'current_metrics': {
                'queries_per_second': self.metrics.queries_per_second,
                'average_response_time': self.metrics.average_response_time,
                'cache_hit_rate': self.metrics.cache_hit_rate,
                'memory_usage_mb': self.metrics.memory_usage_mb,
                'cpu_usage_percent': self.metrics.cpu_usage_percent,
                'active_connections': self.metrics.active_connections,
                'queue_size': self.metrics.queue_size
            },
            'cache_performance': cache_stats,
            'connection_pool': pool_stats,
            'optimization_mode': self.performance_mode.value,
            'bottlenecks': self.metrics.bottleneck_indicators,
            'suggestions': self.metrics.optimization_suggestions,
            'performance_targets': {
                'single_query_target_ms': 100,
                'batch_1000_target_s': 30,
                'target_cache_hit_rate': 0.85,
                'target_qps': 100
            }
        }
    
    async def shutdown(self):
        """Gracefully shutdown performance optimizer"""
        try:
            self.logger.info("🛑 Shutting down Performance Optimizer...")
            
            # Cancel monitoring task
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
            
            # Shutdown batch processors
            for _ in self.batch_processors:
                await self.batch_queue.put(None)  # Shutdown signal
            
            # Wait for batch processors to complete
            for processor in self.batch_processors:
                processor.cancel()
                try:
                    await processor
                except asyncio.CancelledError:
                    pass
            
            # Clear caches
            await self.cache.clear()
            
            # Connection pool cleanup
            await self.connection_pool.cleanup()
            
            self.logger.info("✅ Performance Optimizer shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

class BottleneckDetector:
    """Real-time bottleneck detection and analysis"""
    
    def __init__(self):
        self.alert_thresholds = {
            'response_time': 1.0,
            'memory_usage': 80.0,
            'cpu_usage': 80.0,
            'cache_hit_rate': 0.7,
            'queue_size': 500
        }
        self.bottleneck_history = []
    
    async def analyze(self, metrics: PerformanceMetrics):
        """Analyze metrics for bottlenecks"""
        bottlenecks = []
        suggestions = []
        
        # Response time bottleneck
        if metrics.average_response_time > self.alert_thresholds['response_time']:
            bottlenecks.append("High response time")
            suggestions.append("Consider increasing cache size or enabling pre-computation")
        
        # Memory bottleneck
        if metrics.memory_usage_mb > self.alert_thresholds['memory_usage']:
            bottlenecks.append("High memory usage")
            suggestions.append("Clear caches or reduce batch sizes")
        
        # CPU bottleneck
        if metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage']:
            bottlenecks.append("High CPU usage")
            suggestions.append("Scale up processing capacity or optimize algorithms")
        
        # Cache performance
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            bottlenecks.append("Low cache hit rate")
            suggestions.append("Adjust cache strategy or increase cache size")
        
        # Queue bottleneck
        if metrics.queue_size > self.alert_thresholds['queue_size']:
            bottlenecks.append("Large processing queue")
            suggestions.append("Add more batch processors or increase batch sizes")
        
        # Update metrics
        metrics.bottleneck_indicators = bottlenecks
        metrics.optimization_suggestions = suggestions
        
        # Store in history
        self.bottleneck_history.append({
            'timestamp': time.time(),
            'bottlenecks': bottlenecks,
            'suggestions': suggestions
        })

# Global instance factory
_performance_optimizer = None

async def get_performance_optimizer(config: Optional[Dict[str, Any]] = None) -> QueryFinderPerformanceOptimizer:
    """Get the global performance optimizer instance"""
    global _performance_optimizer
    
    if _performance_optimizer is None:
        _performance_optimizer = QueryFinderPerformanceOptimizer(config)
        await _performance_optimizer.initialize()
    
    return _performance_optimizer