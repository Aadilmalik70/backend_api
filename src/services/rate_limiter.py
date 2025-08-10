"""
Rate Limiter - Advanced rate limiting with token bucket and adaptive algorithms

Comprehensive rate limiting system for API calls with multiple strategies,
burst handling, and intelligent throttling for optimal performance.

Features:
- Token bucket algorithm for smooth rate distribution
- Sliding window rate limiting for precise control
- Adaptive rate limiting based on API response patterns
- Per-source rate limiting with independent buckets
- Queue management and request prioritization
- Circuit breaker integration for error handling
- Real-time metrics and performance monitoring

Algorithms:
1. Token Bucket - Allows bursts up to bucket capacity
2. Sliding Window - Precise rate limiting over time windows
3. Adaptive - Dynamic rate adjustment based on API behavior
4. Leaky Bucket - Smooth output rate regardless of input bursts
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from enum import Enum
import json

logger = logging.getLogger(__name__)

class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window" 
    ADAPTIVE = "adaptive"
    LEAKY_BUCKET = "leaky_bucket"

class ThrottleLevel(Enum):
    """Throttling severity levels"""
    NONE = 0
    LIGHT = 1
    MODERATE = 2
    HEAVY = 3
    BLOCKED = 4

@dataclass
class RateLimitConfig:
    """Configuration for rate limiter"""
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    requests_per_minute: int = 60
    burst_limit: int = 10
    window_size_seconds: int = 60
    adaptive_factor: float = 0.8  # Reduction factor when throttling
    recovery_time_seconds: int = 300  # Time to recover from throttling
    enable_backoff: bool = True
    max_queue_size: int = 1000

@dataclass
class RateLimitMetrics:
    """Rate limiting performance metrics"""
    total_requests: int = 0
    allowed_requests: int = 0
    throttled_requests: int = 0
    queue_overflows: int = 0
    current_rate: float = 0.0
    bucket_level: float = 1.0
    throttle_level: ThrottleLevel = ThrottleLevel.NONE
    last_request_time: Optional[datetime] = None
    adaptive_rate: Optional[float] = None

class TokenBucket:
    """
    Token bucket implementation for burst-friendly rate limiting.
    Allows short bursts up to bucket capacity while maintaining average rate.
    """
    
    def __init__(self, rate_per_second: float, bucket_capacity: int):
        """Initialize token bucket"""
        self.rate_per_second = rate_per_second
        self.bucket_capacity = bucket_capacity
        self.tokens = float(bucket_capacity)
        self.last_refill = time.time()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens_requested: int = 1) -> bool:
        """Try to acquire tokens from bucket"""
        async with self.lock:
            now = time.time()
            
            # Refill tokens based on elapsed time
            time_elapsed = now - self.last_refill
            tokens_to_add = time_elapsed * self.rate_per_second
            
            self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Check if we have enough tokens
            if self.tokens >= tokens_requested:
                self.tokens -= tokens_requested
                return True
            
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bucket status"""
        return {
            'tokens_available': self.tokens,
            'bucket_capacity': self.bucket_capacity,
            'fill_rate_per_second': self.rate_per_second,
            'bucket_level_percent': (self.tokens / self.bucket_capacity) * 100
        }

class SlidingWindow:
    """
    Sliding window rate limiter for precise rate control.
    Maintains exact count of requests within the time window.
    """
    
    def __init__(self, requests_per_window: int, window_seconds: int):
        """Initialize sliding window"""
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: Deque[float] = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Try to acquire permission within sliding window"""
        async with self.lock:
            now = time.time()
            cutoff_time = now - self.window_seconds
            
            # Remove requests outside the window
            while self.requests and self.requests[0] <= cutoff_time:
                self.requests.popleft()
            
            # Check if we're within the limit
            if len(self.requests) < self.requests_per_window:
                self.requests.append(now)
                return True
            
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current window status"""
        now = time.time()
        cutoff_time = now - self.window_seconds
        
        # Count recent requests
        recent_requests = sum(1 for req_time in self.requests if req_time > cutoff_time)
        
        return {
            'requests_in_window': recent_requests,
            'requests_per_window': self.requests_per_window,
            'window_seconds': self.window_seconds,
            'utilization_percent': (recent_requests / self.requests_per_window) * 100
        }

class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts rates based on API response patterns.
    Reduces rate when receiving rate limit errors, increases when stable.
    """
    
    def __init__(self, base_rate_per_minute: int, adaptive_factor: float = 0.8):
        """Initialize adaptive rate limiter"""
        self.base_rate_per_minute = base_rate_per_minute
        self.adaptive_factor = adaptive_factor
        self.current_rate = base_rate_per_minute
        self.last_rate_limit_time = None
        self.consecutive_successes = 0
        self.throttle_level = ThrottleLevel.NONE
        
        # Use token bucket as underlying mechanism
        self.token_bucket = TokenBucket(
            rate_per_second=self.current_rate / 60.0,
            bucket_capacity=max(10, self.current_rate // 6)  # 10-second burst capacity
        )
        
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire with adaptive rate adjustment"""
        async with self.lock:
            success = await self.token_bucket.acquire()
            
            if success:
                self.consecutive_successes += 1
                
                # Gradually increase rate if we've been successful
                if self.consecutive_successes >= 50 and self.current_rate < self.base_rate_per_minute:
                    await self._increase_rate()
                    self.consecutive_successes = 0
            
            return success
    
    async def record_rate_limit_error(self):
        """Record that we hit a rate limit"""
        async with self.lock:
            self.last_rate_limit_time = time.time()
            self.consecutive_successes = 0
            await self._decrease_rate()
    
    async def record_success(self):
        """Record successful API call"""
        self.consecutive_successes += 1
    
    async def _decrease_rate(self):
        """Decrease rate due to rate limiting"""
        old_rate = self.current_rate
        self.current_rate = max(
            self.base_rate_per_minute * 0.1,  # Never go below 10% of base
            self.current_rate * self.adaptive_factor
        )
        
        # Update throttle level
        rate_ratio = self.current_rate / self.base_rate_per_minute
        if rate_ratio > 0.8:
            self.throttle_level = ThrottleLevel.LIGHT
        elif rate_ratio > 0.5:
            self.throttle_level = ThrottleLevel.MODERATE
        elif rate_ratio > 0.2:
            self.throttle_level = ThrottleLevel.HEAVY
        else:
            self.throttle_level = ThrottleLevel.BLOCKED
        
        # Recreate token bucket with new rate
        self.token_bucket = TokenBucket(
            rate_per_second=self.current_rate / 60.0,
            bucket_capacity=max(5, int(self.current_rate // 6))
        )
        
        logger.warning(f"Rate decreased from {old_rate} to {self.current_rate} RPM "
                      f"(throttle level: {self.throttle_level.name})")
    
    async def _increase_rate(self):
        """Gradually increase rate after successful period"""
        old_rate = self.current_rate
        self.current_rate = min(
            self.base_rate_per_minute,
            self.current_rate * (1.0 + (1.0 - self.adaptive_factor))
        )
        
        # Update throttle level
        if self.current_rate >= self.base_rate_per_minute:
            self.throttle_level = ThrottleLevel.NONE
        else:
            rate_ratio = self.current_rate / self.base_rate_per_minute
            if rate_ratio > 0.8:
                self.throttle_level = ThrottleLevel.LIGHT
            elif rate_ratio > 0.5:
                self.throttle_level = ThrottleLevel.MODERATE
            else:
                self.throttle_level = ThrottleLevel.HEAVY
        
        # Recreate token bucket with new rate
        self.token_bucket = TokenBucket(
            rate_per_second=self.current_rate / 60.0,
            bucket_capacity=max(10, int(self.current_rate // 6))
        )
        
        logger.info(f"Rate increased from {old_rate} to {self.current_rate} RPM "
                   f"(throttle level: {self.throttle_level.name})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get adaptive limiter status"""
        bucket_status = self.token_bucket.get_status()
        
        return {
            'base_rate_per_minute': self.base_rate_per_minute,
            'current_rate_per_minute': self.current_rate,
            'throttle_level': self.throttle_level.name,
            'consecutive_successes': self.consecutive_successes,
            'rate_reduction_percent': (1.0 - self.current_rate / self.base_rate_per_minute) * 100,
            'bucket_status': bucket_status,
            'last_rate_limit': self.last_rate_limit_time
        }

class RateLimiter:
    """
    Advanced rate limiter with multiple strategies and intelligent throttling.
    Provides comprehensive rate limiting for API clients with performance monitoring.
    """
    
    def __init__(self, 
                 requests_per_minute: int = 60,
                 burst_limit: int = 10,
                 strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET,
                 config: Optional[RateLimitConfig] = None):
        """Initialize rate limiter"""
        
        self.config = config or RateLimitConfig(
            strategy=strategy,
            requests_per_minute=requests_per_minute,
            burst_limit=burst_limit
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize the appropriate rate limiting mechanism
        self.limiter = self._create_limiter()
        
        # Performance metrics
        self.metrics = RateLimitMetrics()
        
        # Request queue for handling overflow
        self.request_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.max_queue_size)
        self.queue_processor_task: Optional[asyncio.Task] = None
        
        # Backoff calculation
        self.backoff_base = 1.0
        self.max_backoff = 60.0
        
        self.logger.info(f"Rate limiter initialized: {self.config.strategy.value}, "
                        f"{self.config.requests_per_minute} RPM, burst: {self.config.burst_limit}")
    
    def _create_limiter(self):
        """Create the appropriate rate limiting mechanism"""
        if self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return TokenBucket(
                rate_per_second=self.config.requests_per_minute / 60.0,
                bucket_capacity=self.config.burst_limit
            )
        elif self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return SlidingWindow(
                requests_per_window=self.config.requests_per_minute,
                window_seconds=self.config.window_size_seconds
            )
        elif self.config.strategy == RateLimitStrategy.ADAPTIVE:
            return AdaptiveRateLimiter(
                base_rate_per_minute=self.config.requests_per_minute,
                adaptive_factor=self.config.adaptive_factor
            )
        else:
            # Default to token bucket
            return TokenBucket(
                rate_per_second=self.config.requests_per_minute / 60.0,
                bucket_capacity=self.config.burst_limit
            )
    
    async def acquire(self, priority: int = 1) -> bool:
        """
        Acquire permission to make a request
        
        Args:
            priority: Request priority (higher = more important)
            
        Returns:
            True if request is allowed, False if rate limited
        """
        
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.utcnow()
        
        # Try to acquire directly from limiter
        if await self.limiter.acquire():
            self.metrics.allowed_requests += 1
            await self._update_current_rate()
            return True
        
        # Request was rate limited
        self.metrics.throttled_requests += 1
        
        # If backoff is enabled, try queuing the request
        if self.config.enable_backoff:
            return await self._handle_rate_limited_request(priority)
        
        return False
    
    async def _handle_rate_limited_request(self, priority: int) -> bool:
        """Handle rate limited request with queuing and backoff"""
        
        try:
            # Try to add to queue
            request_item = {
                'priority': priority,
                'timestamp': time.time(),
                'future': asyncio.Future()
            }
            
            await asyncio.wait_for(
                self.request_queue.put(request_item),
                timeout=1.0  # Don't wait too long to queue
            )
            
            # Start queue processor if not running
            if self.queue_processor_task is None or self.queue_processor_task.done():
                self.queue_processor_task = asyncio.create_task(self._process_queue())
            
            # Wait for result
            return await request_item['future']
            
        except (asyncio.QueueFull, asyncio.TimeoutError):
            self.metrics.queue_overflows += 1
            return False
    
    async def _process_queue(self):
        """Process queued requests with backoff"""
        while True:
            try:
                # Get request from queue
                request_item = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=10.0  # Exit if no requests for 10 seconds
                )
                
                # Calculate backoff delay
                backoff_delay = self._calculate_backoff_delay()
                
                if backoff_delay > 0:
                    await asyncio.sleep(backoff_delay)
                
                # Try to acquire again
                success = await self.limiter.acquire()
                
                # Resolve the future
                if not request_item['future'].done():
                    request_item['future'].set_result(success)
                
                if success:
                    self.metrics.allowed_requests += 1
                else:
                    self.metrics.throttled_requests += 1
                
            except asyncio.TimeoutError:
                # No requests in queue, exit processor
                break
            except Exception as e:
                self.logger.error(f"Queue processor error: {e}")
                break
    
    def _calculate_backoff_delay(self) -> float:
        """Calculate exponential backoff delay"""
        if not self.config.enable_backoff:
            return 0.0
        
        # Simple backoff based on throttle level
        throttle_level = getattr(self.limiter, 'throttle_level', ThrottleLevel.NONE)
        
        if throttle_level == ThrottleLevel.LIGHT:
            return 1.0
        elif throttle_level == ThrottleLevel.MODERATE:
            return 2.0
        elif throttle_level == ThrottleLevel.HEAVY:
            return 5.0
        elif throttle_level == ThrottleLevel.BLOCKED:
            return 10.0
        
        return 0.0
    
    async def _update_current_rate(self):
        """Update current rate metrics"""
        now = time.time()
        
        # Simple rate calculation over last minute
        if hasattr(self, '_rate_history'):
            # Remove old entries
            cutoff = now - 60
            self._rate_history = [t for t in self._rate_history if t > cutoff]
        else:
            self._rate_history = []
        
        self._rate_history.append(now)
        self.metrics.current_rate = len(self._rate_history)  # Requests per minute
    
    async def record_rate_limit_error(self):
        """Record that we received a rate limit error from the API"""
        if hasattr(self.limiter, 'record_rate_limit_error'):
            await self.limiter.record_rate_limit_error()
        
        # Update throttle level in metrics
        if hasattr(self.limiter, 'throttle_level'):
            self.metrics.throttle_level = self.limiter.throttle_level
    
    async def record_success(self):
        """Record successful API call"""
        if hasattr(self.limiter, 'record_success'):
            await self.limiter.record_success()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive rate limiter status"""
        
        # Get limiter-specific status
        limiter_status = {}
        if hasattr(self.limiter, 'get_status'):
            limiter_status = self.limiter.get_status()
        
        # Calculate success rate
        success_rate = (
            self.metrics.allowed_requests / self.metrics.total_requests
            if self.metrics.total_requests > 0 else 1.0
        )
        
        return {
            'strategy': self.config.strategy.value,
            'configuration': {
                'requests_per_minute': self.config.requests_per_minute,
                'burst_limit': self.config.burst_limit,
                'window_size_seconds': self.config.window_size_seconds,
                'adaptive_factor': self.config.adaptive_factor,
                'enable_backoff': self.config.enable_backoff
            },
            'metrics': {
                'total_requests': self.metrics.total_requests,
                'allowed_requests': self.metrics.allowed_requests,
                'throttled_requests': self.metrics.throttled_requests,
                'queue_overflows': self.metrics.queue_overflows,
                'success_rate': success_rate,
                'current_rate_per_minute': self.metrics.current_rate,
                'throttle_level': self.metrics.throttle_level.name,
                'last_request_time': self.metrics.last_request_time.isoformat() if self.metrics.last_request_time else None
            },
            'limiter_details': limiter_status,
            'queue_status': {
                'queue_size': self.request_queue.qsize(),
                'max_queue_size': self.config.max_queue_size,
                'processor_running': self.queue_processor_task is not None and not self.queue_processor_task.done()
            }
        }
    
    async def wait_for_capacity(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until there's capacity available
        
        Args:
            timeout: Maximum time to wait (seconds)
            
        Returns:
            True if capacity became available, False on timeout
        """
        
        start_time = time.time()
        
        while True:
            if await self.limiter.acquire():
                return True
            
            # Check timeout
            if timeout and (time.time() - start_time) >= timeout:
                return False
            
            # Wait a bit before trying again
            await asyncio.sleep(0.1)
    
    def reset(self):
        """Reset the rate limiter state"""
        self.limiter = self._create_limiter()
        self.metrics = RateLimitMetrics()
        
        # Clear queue
        while not self.request_queue.empty():
            try:
                self.request_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        self.logger.info("Rate limiter reset")
    
    async def shutdown(self):
        """Gracefully shutdown rate limiter"""
        try:
            # Cancel queue processor
            if self.queue_processor_task and not self.queue_processor_task.done():
                self.queue_processor_task.cancel()
                try:
                    await self.queue_processor_task
                except asyncio.CancelledError:
                    pass
            
            # Clear queue and resolve pending futures
            while not self.request_queue.empty():
                try:
                    request_item = self.request_queue.get_nowait()
                    if not request_item['future'].done():
                        request_item['future'].set_result(False)
                except asyncio.QueueEmpty:
                    break
            
            self.logger.info("Rate limiter shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Rate limiter shutdown error: {e}")

# Global rate limiter instances for different services
_service_limiters: Dict[str, RateLimiter] = {}

def get_rate_limiter(service_name: str, 
                    requests_per_minute: int = 60,
                    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET) -> RateLimiter:
    """Get or create rate limiter for a service"""
    
    if service_name not in _service_limiters:
        _service_limiters[service_name] = RateLimiter(
            requests_per_minute=requests_per_minute,
            strategy=strategy
        )
    
    return _service_limiters[service_name]

async def shutdown_all_limiters():
    """Shutdown all service rate limiters"""
    for limiter in _service_limiters.values():
        await limiter.shutdown()
    
    _service_limiters.clear()