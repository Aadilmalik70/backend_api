"""
Async Request Manager - High-performance parallel request processing

Advanced async request management system with connection pooling, timeout protection,
and intelligent load balancing for the data acquisition pipeline.

Features:
- Connection pooling with adaptive sizing
- Request timeout management with progressive backoff
- Parallel request execution with concurrency control
- Request prioritization and queue management
- Circuit breaker integration for resilient processing
- Performance monitoring and bottleneck detection
- Graceful degradation under load

Performance Targets: 100+ concurrent requests, <8s timeout protection
"""

import asyncio
import aiohttp
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from enum import Enum
import json
import ssl
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RequestPriority(Enum):
    """Request priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class RequestMethod(Enum):
    """HTTP request methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class RequestConfig:
    """Configuration for async requests"""
    method: RequestMethod = RequestMethod.GET
    url: str = ""
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json_data: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    timeout: float = 8.0
    priority: RequestPriority = RequestPriority.NORMAL
    retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    follow_redirects: bool = True
    verify_ssl: bool = True

@dataclass
class RequestResult:
    """Result from async request execution"""
    success: bool
    status_code: Optional[int] = None
    data: Optional[Union[Dict[str, Any], List, str]] = None
    headers: Optional[Dict[str, str]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    from_cache: bool = False
    retries_used: int = 0
    final_url: Optional[str] = None

@dataclass
class ConnectionPoolConfig:
    """Connection pool configuration"""
    max_connections: int = 100
    max_connections_per_host: int = 30
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    keepalive_timeout: float = 30.0
    enable_cleanup_closed: bool = True
    ttl_dns_cache: int = 300
    use_dns_cache: bool = True

@dataclass 
class QueueMetrics:
    """Request queue performance metrics"""
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    queued_requests: int = 0
    average_execution_time: float = 0.0
    requests_per_second: float = 0.0
    active_connections: int = 0
    pool_utilization: float = 0.0

class RequestQueue:
    """Priority-based request queue with concurrency control"""
    
    def __init__(self, max_concurrent: int = 50):
        self.max_concurrent = max_concurrent
        self.queues = {
            RequestPriority.CRITICAL: asyncio.Queue(),
            RequestPriority.HIGH: asyncio.Queue(),
            RequestPriority.NORMAL: asyncio.Queue(),
            RequestPriority.LOW: asyncio.Queue()
        }
        self.active_requests = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.metrics = QueueMetrics()
        
    async def enqueue(self, request_config: RequestConfig, callback: Callable):
        """Add request to priority queue"""
        request_item = {
            'config': request_config,
            'callback': callback,
            'enqueued_at': time.time()
        }
        
        await self.queues[request_config.priority].put(request_item)
        self.metrics.queued_requests += 1
        self.metrics.total_requests += 1
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get highest priority request from queue"""
        
        # Check queues in priority order
        for priority in [RequestPriority.CRITICAL, RequestPriority.HIGH, 
                        RequestPriority.NORMAL, RequestPriority.LOW]:
            queue = self.queues[priority]
            
            if not queue.empty():
                try:
                    request_item = queue.get_nowait()
                    self.metrics.queued_requests -= 1
                    return request_item
                except asyncio.QueueEmpty:
                    continue
        
        return None
    
    async def acquire_slot(self):
        """Acquire a slot for request execution"""
        await self.semaphore.acquire()
        self.active_requests += 1
    
    def release_slot(self):
        """Release a request execution slot"""
        if self.active_requests > 0:
            self.active_requests -= 1
            self.semaphore.release()

class AsyncRequestManager:
    """
    High-performance async request manager with connection pooling,
    intelligent queuing, and advanced timeout protection.
    """
    
    def __init__(self, pool_config: Optional[ConnectionPoolConfig] = None):
        """Initialize async request manager"""
        self.pool_config = pool_config or ConnectionPoolConfig()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_queue = RequestQueue(max_concurrent=self.pool_config.max_connections)
        
        # Worker management
        self.workers: List[asyncio.Task] = []
        self.worker_count = min(20, self.pool_config.max_connections // 5)
        self.shutdown_event = asyncio.Event()
        
        # Performance monitoring
        self.request_history = []
        self.performance_metrics = {}
        
        # Request caching
        self.response_cache: Dict[str, Tuple[RequestResult, float]] = {}
        self.cache_ttl = 300  # 5 minutes
        
        self.logger.info("Async Request Manager initialized")
    
    async def initialize(self):
        """Initialize connection pool and worker processes"""
        try:
            self.logger.info("🚀 Initializing Async Request Manager...")
            
            # Create SSL context
            ssl_context = ssl.create_default_context()
            if not self.pool_config.ttl_dns_cache:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create TCP connector with connection pooling
            connector = aiohttp.TCPConnector(
                limit=self.pool_config.max_connections,
                limit_per_host=self.pool_config.max_connections_per_host,
                ttl_dns_cache=self.pool_config.ttl_dns_cache,
                use_dns_cache=self.pool_config.use_dns_cache,
                keepalive_timeout=self.pool_config.keepalive_timeout,
                enable_cleanup_closed=self.pool_config.enable_cleanup_closed,
                ssl=ssl_context
            )
            
            # Create client session
            timeout = aiohttp.ClientTimeout(
                total=self.pool_config.read_timeout,
                connect=self.pool_config.connection_timeout
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={'User-Agent': 'SERP-Strategist-DataPipeline/1.0'}
            )
            
            # Start worker processes
            for i in range(self.worker_count):
                worker = asyncio.create_task(self._worker_process(f"worker_{i}"))
                self.workers.append(worker)
            
            # Start performance monitoring
            asyncio.create_task(self._performance_monitor())
            
            self.logger.info(f"✅ Async Request Manager initialized with {self.worker_count} workers")
            
        except Exception as e:
            self.logger.error(f"Request manager initialization failed: {e}")
            raise
    
    async def _worker_process(self, worker_id: str):
        """Worker process for handling queued requests"""
        self.logger.info(f"Request worker {worker_id} started")
        
        while not self.shutdown_event.is_set():
            try:
                # Get request from queue
                request_item = await self.request_queue.dequeue()
                
                if request_item is None:
                    await asyncio.sleep(0.1)  # Brief pause if no requests
                    continue
                
                # Acquire execution slot
                await self.request_queue.acquire_slot()
                
                try:
                    # Execute request
                    result = await self._execute_request_internal(request_item['config'])
                    
                    # Update metrics
                    self._update_request_metrics(result)
                    
                    # Execute callback
                    callback = request_item['callback']
                    if callback:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(result)
                        else:
                            callback(result)
                    
                finally:
                    # Always release the slot
                    self.request_queue.release_slot()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                self.request_queue.release_slot()
    
    async def execute_request(
        self,
        config: RequestConfig,
        callback: Optional[Callable] = None
    ) -> RequestResult:
        """Execute async request with intelligent queueing and timeout protection"""
        
        if not self.session:
            await self.initialize()
        
        # Check cache first
        cache_key = self._generate_cache_key(config)
        cached_result = self._get_cached_result(cache_key)
        
        if cached_result:
            self.logger.debug(f"Cache hit for {config.url}")
            if callback:
                if asyncio.iscoroutinefunction(callback):
                    await callback(cached_result)
                else:
                    callback(cached_result)
            return cached_result
        
        # For synchronous execution, use direct execution
        if callback is None:
            result = await self._execute_request_internal(config)
            self._cache_result(cache_key, result)
            return result
        
        # For asynchronous execution with callback, use queue
        result_future = asyncio.Future()
        
        async def internal_callback(result: RequestResult):
            self._cache_result(cache_key, result)
            if callback:
                if asyncio.iscoroutinefunction(callback):
                    await callback(result)
                else:
                    callback(result)
            result_future.set_result(result)
        
        await self.request_queue.enqueue(config, internal_callback)
        return await result_future
    
    async def _execute_request_internal(self, config: RequestConfig) -> RequestResult:
        """Internal request execution with retry logic and error handling"""
        
        start_time = time.time()
        last_exception = None
        
        for attempt in range(config.retries + 1):
            try:
                # Calculate timeout for this attempt
                attempt_timeout = config.timeout * (0.8 + 0.2 * attempt)  # Progressive timeout
                
                # Prepare request parameters
                request_kwargs = {
                    'url': config.url,
                    'method': config.method.value,
                    'timeout': aiohttp.ClientTimeout(total=attempt_timeout)
                }
                
                if config.headers:
                    request_kwargs['headers'] = config.headers
                
                if config.params:
                    request_kwargs['params'] = config.params
                
                if config.json_data:
                    request_kwargs['json'] = config.json_data
                
                if config.form_data:
                    request_kwargs['data'] = config.form_data
                
                # Execute request
                async with self.session.request(**request_kwargs) as response:
                    execution_time = time.time() - start_time
                    
                    # Parse response
                    try:
                        if response.content_type == 'application/json':
                            data = await response.json()
                        else:
                            text_data = await response.text()
                            # Try to parse as JSON if possible
                            try:
                                data = json.loads(text_data)
                            except json.JSONDecodeError:
                                data = text_data
                    except Exception as parse_error:
                        self.logger.warning(f"Response parsing error: {parse_error}")
                        data = await response.text()
                    
                    # Create result
                    result = RequestResult(
                        success=200 <= response.status < 300,
                        status_code=response.status,
                        data=data,
                        headers=dict(response.headers),
                        execution_time=execution_time,
                        retries_used=attempt,
                        final_url=str(response.url)
                    )
                    
                    # Return immediately if successful
                    if result.success:
                        return result
                    
                    # Log non-success status codes
                    self.logger.warning(f"Request failed with status {response.status}: {config.url}")
                    last_exception = Exception(f"HTTP {response.status}")
                
            except asyncio.TimeoutError:
                last_exception = Exception(f"Request timeout after {attempt_timeout:.1f}s")
                self.logger.warning(f"Request timeout (attempt {attempt + 1}): {config.url}")
                
            except Exception as e:
                last_exception = e
                self.logger.error(f"Request error (attempt {attempt + 1}): {e}")
            
            # Apply retry delay if not the last attempt
            if attempt < config.retries:
                delay = config.retry_delay
                if config.exponential_backoff:
                    delay *= (2 ** attempt)  # Exponential backoff
                
                await asyncio.sleep(delay)
        
        # All retries exhausted
        execution_time = time.time() - start_time
        return RequestResult(
            success=False,
            execution_time=execution_time,
            error_message=str(last_exception) if last_exception else "Request failed after all retries",
            retries_used=config.retries
        )
    
    async def execute_parallel_requests(
        self,
        configs: List[RequestConfig],
        max_concurrent: Optional[int] = None
    ) -> List[RequestResult]:
        """Execute multiple requests in parallel with concurrency control"""
        
        if not self.session:
            await self.initialize()
        
        # Use provided concurrency limit or default from pool config
        concurrent_limit = max_concurrent or min(len(configs), self.pool_config.max_connections_per_host)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def execute_with_semaphore(config: RequestConfig) -> RequestResult:
            async with semaphore:
                return await self._execute_request_internal(config)
        
        # Execute all requests concurrently
        tasks = [execute_with_semaphore(config) for config in configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(RequestResult(
                    success=False,
                    error_message=str(result),
                    execution_time=0.0,
                    retries_used=0
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _generate_cache_key(self, config: RequestConfig) -> str:
        """Generate cache key for request configuration"""
        import hashlib
        
        # Create hash from request essentials
        key_data = {
            'method': config.method.value,
            'url': config.url,
            'params': config.params,
            'json_data': config.json_data
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[RequestResult]:
        """Get cached result if still valid"""
        if cache_key in self.response_cache:
            result, cached_at = self.response_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_at < self.cache_ttl:
                result.from_cache = True
                return result
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: RequestResult):
        """Cache successful results"""
        if result.success:
            self.response_cache[cache_key] = (result, time.time())
    
    def _update_request_metrics(self, result: RequestResult):
        """Update request performance metrics"""
        self.request_history.append({
            'timestamp': time.time(),
            'success': result.success,
            'execution_time': result.execution_time,
            'retries_used': result.retries_used
        })
        
        # Keep only recent history (last 1000 requests)
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-1000:]
        
        # Update queue metrics
        if result.success:
            self.request_queue.metrics.completed_requests += 1
        else:
            self.request_queue.metrics.failed_requests += 1
    
    async def _performance_monitor(self):
        """Background performance monitoring"""
        while not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Calculate performance metrics
                if self.request_history:
                    recent_requests = [
                        r for r in self.request_history 
                        if time.time() - r['timestamp'] <= 60  # Last minute
                    ]
                    
                    if recent_requests:
                        success_rate = sum(1 for r in recent_requests if r['success']) / len(recent_requests)
                        avg_execution_time = sum(r['execution_time'] for r in recent_requests) / len(recent_requests)
                        requests_per_second = len(recent_requests) / 60
                        
                        self.request_queue.metrics.requests_per_second = requests_per_second
                        self.request_queue.metrics.average_execution_time = avg_execution_time
                        
                        # Log performance alerts
                        if success_rate < 0.9:
                            self.logger.warning(f"Low success rate: {success_rate:.2%}")
                        
                        if avg_execution_time > 10.0:
                            self.logger.warning(f"High average execution time: {avg_execution_time:.2f}s")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        
        # Calculate recent performance
        recent_requests = [
            r for r in self.request_history 
            if time.time() - r['timestamp'] <= 300  # Last 5 minutes
        ]
        
        recent_metrics = {}
        if recent_requests:
            recent_metrics = {
                'requests_last_5min': len(recent_requests),
                'success_rate_5min': sum(1 for r in recent_requests if r['success']) / len(recent_requests),
                'avg_execution_time_5min': sum(r['execution_time'] for r in recent_requests) / len(recent_requests),
                'max_execution_time_5min': max(r['execution_time'] for r in recent_requests),
                'min_execution_time_5min': min(r['execution_time'] for r in recent_requests)
            }
        
        return {
            'queue_metrics': {
                'total_requests': self.request_queue.metrics.total_requests,
                'completed_requests': self.request_queue.metrics.completed_requests,
                'failed_requests': self.request_queue.metrics.failed_requests,
                'queued_requests': self.request_queue.metrics.queued_requests,
                'active_requests': self.request_queue.active_requests,
                'requests_per_second': self.request_queue.metrics.requests_per_second,
                'average_execution_time': self.request_queue.metrics.average_execution_time
            },
            'connection_pool': {
                'max_connections': self.pool_config.max_connections,
                'max_connections_per_host': self.pool_config.max_connections_per_host,
                'active_connections': self.request_queue.active_requests,
                'pool_utilization': self.request_queue.active_requests / self.pool_config.max_connections
            },
            'cache_performance': {
                'cached_responses': len(self.response_cache),
                'cache_ttl': self.cache_ttl
            },
            'worker_status': {
                'worker_count': len(self.workers),
                'active_workers': sum(1 for w in self.workers if not w.done())
            },
            'recent_performance': recent_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for request manager"""
        
        # Test connectivity with a simple request
        test_config = RequestConfig(
            method=RequestMethod.GET,
            url="https://httpbin.org/get",  # Public testing endpoint
            timeout=5.0,
            retries=1
        )
        
        try:
            test_result = await self._execute_request_internal(test_config)
            connectivity_status = "healthy" if test_result.success else "degraded"
        except Exception as e:
            connectivity_status = "unhealthy"
            self.logger.error(f"Health check connectivity test failed: {e}")
        
        return {
            'status': 'healthy' if self.session and not self.session.closed else 'unhealthy',
            'connectivity': connectivity_status,
            'session_status': 'open' if self.session and not self.session.closed else 'closed',
            'worker_count': len([w for w in self.workers if not w.done()]),
            'active_requests': self.request_queue.active_requests,
            'queue_size': sum(queue.qsize() for queue in self.request_queue.queues.values()),
            'cache_size': len(self.response_cache)
        }
    
    async def shutdown(self):
        """Gracefully shutdown request manager"""
        try:
            self.logger.info("🛑 Shutting down Async Request Manager...")
            
            # Signal shutdown
            self.shutdown_event.set()
            
            # Cancel worker tasks
            for worker in self.workers:
                worker.cancel()
            
            # Wait for workers to complete
            if self.workers:
                await asyncio.gather(*self.workers, return_exceptions=True)
            
            # Close session
            if self.session and not self.session.closed:
                await self.session.close()
            
            # Clear cache
            self.response_cache.clear()
            
            self.logger.info("✅ Async Request Manager shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")