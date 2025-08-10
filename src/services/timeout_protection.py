"""
Timeout Protection and Error Recovery System

Comprehensive timeout protection and error recovery for the data acquisition pipeline,
ensuring reliable operation under various failure conditions and resource constraints.

Features:
- Configurable timeout strategies (fixed, adaptive, progressive)
- Circuit breaker pattern for persistent failures
- Exponential backoff with jitter for retry logic
- Request deadline management and cancellation
- Health-based timeout adjustment
- Error classification and recovery strategies
- Metrics tracking for timeout and recovery patterns

Components:
1. TimeoutManager - Centralized timeout configuration and management
2. CircuitBreaker - Failure detection and service protection
3. RetryManager - Intelligent retry logic with backoff strategies
4. ErrorRecovery - Error classification and recovery coordination
5. HealthMonitor - Service health tracking for adaptive timeouts
"""

import asyncio
import logging
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import json
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class TimeoutStrategy(Enum):
    """Timeout management strategies"""
    FIXED = "fixed"              # Fixed timeout values
    ADAPTIVE = "adaptive"        # Adaptive based on historical performance
    PROGRESSIVE = "progressive"  # Increasing timeout for retries
    HEALTH_BASED = "health_based"  # Based on service health metrics

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service recovered

class ErrorSeverity(Enum):
    """Error severity levels for recovery strategies"""
    TRANSIENT = "transient"    # Temporary errors (network, rate limit)
    PERSISTENT = "persistent"  # Persistent errors (auth, config)
    CRITICAL = "critical"      # Critical errors (service down)

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL = "exponential"  # Exponential backoff
    LINEAR = "linear"           # Linear backoff
    FIXED = "fixed"             # Fixed delay
    FIBONACCI = "fibonacci"     # Fibonacci sequence
    JITTERED = "jittered"      # Exponential with jitter

@dataclass
class TimeoutConfig:
    """Timeout configuration for different operation types"""
    # Base timeouts (seconds)
    request_timeout: float = 15.0
    connection_timeout: float = 10.0
    read_timeout: float = 30.0
    operation_timeout: float = 60.0
    
    # Adaptive timeout settings
    strategy: TimeoutStrategy = TimeoutStrategy.ADAPTIVE
    min_timeout: float = 2.0
    max_timeout: float = 120.0
    adaptive_factor: float = 1.5
    
    # Health-based adjustments
    health_threshold_fast: float = 0.9    # Good health
    health_threshold_slow: float = 0.5    # Poor health
    fast_timeout_factor: float = 0.8      # Reduce timeout when healthy
    slow_timeout_factor: float = 2.0      # Increase timeout when unhealthy

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5        # Failures before opening circuit
    recovery_timeout: float = 30.0    # Time before trying half-open
    success_threshold: int = 3        # Successes needed to close circuit
    timeout_counts_as_failure: bool = True
    
    # Sliding window for failure tracking
    window_size: int = 100           # Number of recent requests to track
    failure_rate_threshold: float = 0.5  # Failure rate to open circuit

@dataclass
class RetryConfig:
    """Retry configuration"""
    max_retries: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    
    # Retry conditions
    retry_on_timeout: bool = True
    retry_on_connection_error: bool = True
    retry_on_server_error: bool = False  # 5xx errors
    retry_on_rate_limit: bool = True

@dataclass
class OperationResult:
    """Result of a protected operation"""
    success: bool
    data: Any = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    retries_used: int = 0
    timeout_occurred: bool = False
    circuit_open: bool = False
    recovery_attempted: bool = False

@dataclass
class HealthMetrics:
    """Health metrics for services"""
    success_count: int = 0
    failure_count: int = 0
    timeout_count: int = 0
    avg_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    
    @property
    def total_requests(self) -> int:
        return self.success_count + self.failure_count
    
    @property
    def success_rate(self) -> float:
        total = self.total_requests
        return self.success_count / total if total > 0 else 1.0
    
    @property
    def failure_rate(self) -> float:
        return 1.0 - self.success_rate

class CircuitBreaker:
    """Circuit breaker implementation with sliding window"""
    
    def __init__(self, service_name: str, config: CircuitBreakerConfig):
        self.service_name = service_name
        self.config = config
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        
        # Sliding window for failure tracking
        self.request_history = deque(maxlen=config.window_size)
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.{service_name}")
    
    async def call(self, operation: Callable, *args, **kwargs) -> OperationResult:
        """Execute operation with circuit breaker protection"""
        async with self.lock:
            # Check if circuit is open
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.logger.info(f"Circuit breaker {self.service_name} entering HALF_OPEN state")
                else:
                    return OperationResult(
                        success=False,
                        error=Exception(f"Circuit breaker {self.service_name} is OPEN"),
                        circuit_open=True
                    )
        
        # Execute operation
        start_time = time.time()
        try:
            result = await operation(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Record success
            await self._record_success(execution_time)
            
            # Check if result is already an OperationResult
            if isinstance(result, OperationResult):
                # Update execution time and return as-is
                result.execution_time = execution_time
                return result
            else:
                # Wrap raw result
                return OperationResult(
                    success=True,
                    data=result,
                    execution_time=execution_time
                )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure
            is_timeout = isinstance(e, asyncio.TimeoutError)
            await self._record_failure(is_timeout)
            
            return OperationResult(
                success=False,
                error=e,
                execution_time=execution_time,
                timeout_occurred=is_timeout
            )
    
    async def _record_success(self, response_time: float):
        """Record successful operation"""
        async with self.lock:
            self.request_history.append(('success', time.time(), response_time))
            self.consecutive_failures = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.consecutive_successes += 1
                if self.consecutive_successes >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.consecutive_successes = 0
                    self.logger.info(f"Circuit breaker {self.service_name} closed after recovery")
    
    async def _record_failure(self, is_timeout: bool):
        """Record failed operation"""
        async with self.lock:
            self.request_history.append(('failure', time.time(), 0))
            self.consecutive_failures += 1
            self.last_failure_time = time.time()
            
            # Check if should open circuit
            if self.state == CircuitState.CLOSED:
                should_open = False
                
                # Check consecutive failures
                if self.consecutive_failures >= self.config.failure_threshold:
                    should_open = True
                
                # Check failure rate in sliding window
                failure_rate = self._calculate_failure_rate()
                if failure_rate >= self.config.failure_rate_threshold:
                    should_open = True
                
                if should_open:
                    self.state = CircuitState.OPEN
                    self.logger.warning(f"Circuit breaker {self.service_name} opened after {self.consecutive_failures} failures")
            
            elif self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.consecutive_successes = 0
                self.logger.warning(f"Circuit breaker {self.service_name} reopened during half-open test")
    
    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _calculate_failure_rate(self) -> float:
        """Calculate failure rate in sliding window"""
        if not self.request_history:
            return 0.0
        
        failures = sum(1 for result, _, _ in self.request_history if result == 'failure')
        return failures / len(self.request_history)
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            'service_name': self.service_name,
            'state': self.state.value,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'failure_rate': self._calculate_failure_rate(),
            'requests_in_window': len(self.request_history),
            'last_failure_time': self.last_failure_time
        }

class TimeoutManager:
    """Centralized timeout management with adaptive strategies"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.service_timeouts: Dict[str, float] = {}
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.health_metrics: Dict[str, HealthMetrics] = defaultdict(HealthMetrics)
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(__name__)
    
    async def with_timeout(
        self,
        operation: Callable,
        service_name: str,
        operation_type: str = "default",
        custom_timeout: Optional[float] = None,
        *args,
        **kwargs
    ) -> OperationResult:
        """Execute operation with adaptive timeout"""
        
        # Determine timeout value
        if custom_timeout:
            timeout_value = custom_timeout
        else:
            timeout_value = await self._get_adaptive_timeout(service_name, operation_type)
        
        start_time = time.time()
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                operation(*args, **kwargs),
                timeout=timeout_value
            )
            
            execution_time = time.time() - start_time
            
            # Record performance
            await self._record_performance(service_name, execution_time, success=True)
            
            return OperationResult(
                success=True,
                data=result,
                execution_time=execution_time
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            
            # Record timeout
            await self._record_performance(service_name, execution_time, success=False, timeout=True)
            
            self.logger.warning(f"Operation timed out for {service_name} after {timeout_value}s")
            
            return OperationResult(
                success=False,
                error=asyncio.TimeoutError(f"Operation timed out after {timeout_value}s"),
                execution_time=execution_time,
                timeout_occurred=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Record failure
            await self._record_performance(service_name, execution_time, success=False)
            
            return OperationResult(
                success=False,
                error=e,
                execution_time=execution_time
            )
    
    async def _get_adaptive_timeout(self, service_name: str, operation_type: str) -> float:
        """Get adaptive timeout value based on strategy"""
        base_timeout = self.config.operation_timeout
        
        if self.config.strategy == TimeoutStrategy.FIXED:
            return base_timeout
        
        elif self.config.strategy == TimeoutStrategy.ADAPTIVE:
            return await self._calculate_adaptive_timeout(service_name, base_timeout)
        
        elif self.config.strategy == TimeoutStrategy.HEALTH_BASED:
            return await self._calculate_health_based_timeout(service_name, base_timeout)
        
        else:
            return base_timeout
    
    async def _calculate_adaptive_timeout(self, service_name: str, base_timeout: float) -> float:
        """Calculate adaptive timeout based on historical performance"""
        async with self.lock:
            history = self.performance_history[service_name]
            
            if len(history) < 10:  # Not enough history
                return base_timeout
            
            # Calculate percentile-based timeout
            recent_times = [time_val for time_val, success in history if success]
            
            if not recent_times:
                return base_timeout * self.config.adaptive_factor
            
            # Use 95th percentile + buffer
            sorted_times = sorted(recent_times)
            p95_index = int(len(sorted_times) * 0.95)
            p95_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
            
            adaptive_timeout = p95_time * self.config.adaptive_factor
            
            # Clamp to min/max values
            adaptive_timeout = max(self.config.min_timeout, 
                                 min(self.config.max_timeout, adaptive_timeout))
            
            return adaptive_timeout
    
    async def _calculate_health_based_timeout(self, service_name: str, base_timeout: float) -> float:
        """Calculate timeout based on service health"""
        async with self.lock:
            metrics = self.health_metrics[service_name]
            health_score = metrics.success_rate
            
            if health_score >= self.config.health_threshold_fast:
                # Service is healthy, reduce timeout
                return base_timeout * self.config.fast_timeout_factor
            
            elif health_score <= self.config.health_threshold_slow:
                # Service is unhealthy, increase timeout
                return base_timeout * self.config.slow_timeout_factor
            
            else:
                # Normal health, use base timeout
                return base_timeout
    
    async def _record_performance(self, service_name: str, execution_time: float, 
                                success: bool, timeout: bool = False):
        """Record operation performance"""
        async with self.lock:
            # Update performance history
            self.performance_history[service_name].append((execution_time, success))
            
            # Update health metrics
            metrics = self.health_metrics[service_name]
            
            if success:
                metrics.success_count += 1
                metrics.last_success_time = datetime.utcnow()
            else:
                metrics.failure_count += 1
                metrics.last_failure_time = datetime.utcnow()
                
                if timeout:
                    metrics.timeout_count += 1
            
            # Update average response time
            total_requests = metrics.total_requests
            metrics.avg_response_time = (
                (metrics.avg_response_time * (total_requests - 1) + execution_time) / total_requests
            )
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """Get health metrics for a service"""
        metrics = self.health_metrics[service_name]
        return {
            'service_name': service_name,
            'success_rate': metrics.success_rate,
            'failure_rate': metrics.failure_rate,
            'avg_response_time': metrics.avg_response_time,
            'total_requests': metrics.total_requests,
            'timeout_count': metrics.timeout_count,
            'last_success_time': metrics.last_success_time.isoformat() if metrics.last_success_time else None,
            'last_failure_time': metrics.last_failure_time.isoformat() if metrics.last_failure_time else None
        }

class RetryManager:
    """Intelligent retry manager with multiple backoff strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def with_retry(
        self,
        operation: Callable,
        service_name: str,
        custom_config: Optional[RetryConfig] = None,
        *args,
        **kwargs
    ) -> OperationResult:
        """Execute operation with retry logic"""
        
        config = custom_config or self.config
        last_error = None
        
        for attempt in range(config.max_retries + 1):  # +1 for initial attempt
            try:
                result = await operation(*args, **kwargs)
                
                return OperationResult(
                    success=True,
                    data=result,
                    retries_used=attempt
                )
                
            except Exception as e:
                last_error = e
                
                # Check if should retry
                if attempt >= config.max_retries:
                    break
                
                if not self._should_retry(e, config):
                    break
                
                # Calculate backoff delay
                delay = self._calculate_backoff(attempt, config)
                
                self.logger.warning(
                    f"Attempt {attempt + 1} failed for {service_name}: {e}. "
                    f"Retrying in {delay:.2f}s"
                )
                
                await asyncio.sleep(delay)
        
        return OperationResult(
            success=False,
            error=last_error,
            retries_used=config.max_retries
        )
    
    def _should_retry(self, error: Exception, config: RetryConfig) -> bool:
        """Determine if error should trigger retry"""
        
        # Timeout errors
        if isinstance(error, asyncio.TimeoutError):
            return config.retry_on_timeout
        
        # Connection errors
        if isinstance(error, (ConnectionError, ConnectionRefusedError, ConnectionResetError)):
            return config.retry_on_connection_error
        
        # Rate limit errors
        if 'rate limit' in str(error).lower() or 'quota' in str(error).lower():
            return config.retry_on_rate_limit
        
        # HTTP errors (if available)
        if hasattr(error, 'status_code'):
            status_code = error.status_code
            
            # Server errors (5xx)
            if 500 <= status_code < 600:
                return config.retry_on_server_error
            
            # Client errors (4xx) - generally don't retry
            if 400 <= status_code < 500:
                return False
        
        # Default: don't retry unknown errors
        return False
    
    def _calculate_backoff(self, attempt: int, config: RetryConfig) -> float:
        """Calculate backoff delay"""
        
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
            
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * (attempt + 1)
            
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.backoff_multiplier ** attempt)
            
        elif config.strategy == RetryStrategy.FIBONACCI:
            delay = config.base_delay * self._fibonacci(attempt + 1)
            
        elif config.strategy == RetryStrategy.JITTERED:
            base_delay = config.base_delay * (config.backoff_multiplier ** attempt)
            jitter = random.uniform(0.5, 1.5) if config.jitter else 1.0
            delay = base_delay * jitter
            
        else:
            delay = config.base_delay
        
        # Apply max delay limit
        return min(delay, config.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number"""
        if n <= 2:
            return 1
        
        a, b = 1, 1
        for _ in range(2, n):
            a, b = b, a + b
        
        return b

class ErrorRecovery:
    """Error classification and recovery coordination"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_patterns: Dict[ErrorSeverity, List[str]] = {
            ErrorSeverity.TRANSIENT: [
                'timeout', 'connection', 'network', 'rate limit', 'quota',
                'temporary', 'unavailable', 'busy'
            ],
            ErrorSeverity.PERSISTENT: [
                'authentication', 'authorization', 'forbidden', 'not found',
                'invalid', 'malformed', 'syntax'
            ],
            ErrorSeverity.CRITICAL: [
                'internal server error', 'service unavailable', 'bad gateway',
                'gateway timeout', 'service down'
            ]
        }
        
        self.logger = logging.getLogger(__name__)
    
    def classify_error(self, error: Exception) -> ErrorSeverity:
        """Classify error by severity"""
        error_message = str(error).lower()
        
        # Check patterns for each severity level
        for severity, patterns in self.error_patterns.items():
            if any(pattern in error_message for pattern in patterns):
                return severity
        
        # Default to transient for unknown errors
        return ErrorSeverity.TRANSIENT
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register custom recovery strategy"""
        self.recovery_strategies[error_type] = strategy
    
    async def attempt_recovery(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Attempt error recovery"""
        severity = self.classify_error(error)
        error_type = type(error).__name__
        
        # Try specific recovery strategy first
        if error_type in self.recovery_strategies:
            try:
                recovery_result = await self.recovery_strategies[error_type](error, context)
                if recovery_result:
                    self.logger.info(f"Recovery successful for {error_type}")
                    return True
            except Exception as e:
                self.logger.error(f"Recovery strategy failed for {error_type}: {e}")
        
        # Try general recovery based on severity
        return await self._general_recovery(severity, error, context)
    
    async def _general_recovery(self, severity: ErrorSeverity, error: Exception, context: Dict[str, Any]) -> bool:
        """General recovery strategies based on error severity"""
        
        if severity == ErrorSeverity.TRANSIENT:
            # Wait and retry is handled by retry manager
            return True
            
        elif severity == ErrorSeverity.PERSISTENT:
            # Log for manual intervention
            self.logger.error(f"Persistent error requires manual intervention: {error}")
            return False
            
        elif severity == ErrorSeverity.CRITICAL:
            # Escalate to monitoring systems
            self.logger.critical(f"Critical error detected: {error}")
            await self._escalate_critical_error(error, context)
            return False
        
        return False
    
    async def _escalate_critical_error(self, error: Exception, context: Dict[str, Any]):
        """Escalate critical errors to monitoring systems"""
        # This would integrate with monitoring/alerting systems
        # For now, just log with critical level
        self.logger.critical(f"CRITICAL ERROR ESCALATION: {error}, Context: {context}")

class TimeoutProtectionSystem:
    """Unified timeout protection and error recovery system"""
    
    def __init__(
        self,
        timeout_config: Optional[TimeoutConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None,
        retry_config: Optional[RetryConfig] = None
    ):
        self.timeout_manager = TimeoutManager(timeout_config or TimeoutConfig())
        self.retry_manager = RetryManager(retry_config or RetryConfig())
        self.error_recovery = ErrorRecovery()
        
        # Circuit breakers per service
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.circuit_config = circuit_config or CircuitBreakerConfig()
        
        self.logger = logging.getLogger(__name__)
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                service_name, 
                self.circuit_config
            )
        
        return self.circuit_breakers[service_name]
    
    async def protected_call(
        self,
        operation: Callable,
        service_name: str,
        operation_type: str = "default",
        timeout: Optional[float] = None,
        enable_retry: bool = True,
        enable_circuit_breaker: bool = True,
        enable_recovery: bool = True,
        context: Optional[Dict[str, Any]] = None,
        *args,
        **kwargs
    ) -> OperationResult:
        """
        Execute operation with full protection (timeout, retry, circuit breaker)
        """
        
        context = context or {}
        
        # Wrap operation with timeout protection
        async def timeout_protected_operation(*op_args, **op_kwargs):
            return await self.timeout_manager.with_timeout(
                operation, service_name, operation_type, timeout, *op_args, **op_kwargs
            )
        
        # Wrap with retry if enabled
        if enable_retry:
            async def retry_protected_operation(*op_args, **op_kwargs):
                return await self.retry_manager.with_retry(
                    timeout_protected_operation, service_name, None, *op_args, **op_kwargs
                )
            final_operation = retry_protected_operation
        else:
            final_operation = timeout_protected_operation
        
        # Execute with circuit breaker if enabled
        if enable_circuit_breaker:
            circuit_breaker = self.get_circuit_breaker(service_name)
            result = await circuit_breaker.call(final_operation, *args, **kwargs)
        else:
            try:
                operation_result = await final_operation(*args, **kwargs)
                if hasattr(operation_result, 'success'):
                    result = operation_result
                else:
                    result = OperationResult(success=True, data=operation_result)
            except Exception as e:
                result = OperationResult(success=False, error=e)
        
        # Attempt recovery if enabled and operation failed
        if enable_recovery and not result.success and result.error:
            recovery_attempted = await self.error_recovery.attempt_recovery(
                result.error, context
            )
            result.recovery_attempted = recovery_attempted
        
        return result
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        circuit_statuses = {}
        for service_name, circuit in self.circuit_breakers.items():
            circuit_statuses[service_name] = circuit.get_status()
        
        service_healths = {}
        for service_name in self.circuit_breakers.keys():
            service_healths[service_name] = self.timeout_manager.get_service_health(service_name)
        
        return {
            'circuit_breakers': circuit_statuses,
            'service_health': service_healths,
            'timeout_config': {
                'strategy': self.timeout_manager.config.strategy.value,
                'base_timeout': self.timeout_manager.config.operation_timeout,
                'min_timeout': self.timeout_manager.config.min_timeout,
                'max_timeout': self.timeout_manager.config.max_timeout
            },
            'retry_config': {
                'max_retries': self.retry_manager.config.max_retries,
                'strategy': self.retry_manager.config.strategy.value,
                'base_delay': self.retry_manager.config.base_delay
            }
        }

# Global instance for easy access
_global_protection_system: Optional[TimeoutProtectionSystem] = None

def get_timeout_protection() -> TimeoutProtectionSystem:
    """Get global timeout protection system instance"""
    global _global_protection_system
    
    if _global_protection_system is None:
        _global_protection_system = TimeoutProtectionSystem()
    
    return _global_protection_system

def configure_timeout_protection(
    timeout_config: Optional[TimeoutConfig] = None,
    circuit_config: Optional[CircuitBreakerConfig] = None,
    retry_config: Optional[RetryConfig] = None
):
    """Configure global timeout protection system"""
    global _global_protection_system
    
    _global_protection_system = TimeoutProtectionSystem(
        timeout_config, circuit_config, retry_config
    )