"""
Application Metrics for SERP Strategist Backend
Prometheus metrics collection and custom business metrics
"""

import time
import functools
from typing import Dict, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, Counter
import threading

try:
    from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

@dataclass
class MetricValue:
    """Represents a metric value with timestamp"""
    value: float
    timestamp: float
    labels: Dict[str, str] = None

class MetricsCollector:
    """Collect and expose application metrics"""
    
    def __init__(self):
        self.enabled = PROMETHEUS_AVAILABLE
        self._lock = threading.Lock()
        
        if self.enabled:
            self._init_prometheus_metrics()
        else:
            self._init_fallback_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # HTTP Request metrics
        self.http_requests_total = Counter(
            'flask_http_request_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.http_request_duration = Histogram(
            'flask_http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint']
        )
        
        self.http_request_exceptions = Counter(
            'flask_http_request_exceptions_total',
            'Total HTTP request exceptions',
            ['method', 'endpoint', 'exception']
        )
        
        # Blueprint Generation metrics
        self.blueprint_generation_total = Counter(
            'blueprint_generation_total',
            'Total blueprint generations',
            ['status']
        )
        
        self.blueprint_generation_duration = Histogram(
            'blueprint_generation_duration_seconds',
            'Blueprint generation duration in seconds',
            buckets=[1, 5, 10, 30, 60, 120, 300]
        )
        
        self.blueprint_generation_queue_size = Gauge(
            'blueprint_generation_queue_size',
            'Current blueprint generation queue size'
        )
        
        self.blueprint_generation_failures = Counter(
            'blueprint_generation_failures_total',
            'Total blueprint generation failures',
            ['error_type']
        )
        
        # WebSocket metrics
        self.websocket_connections_active = Gauge(
            'websocket_connections_active',
            'Active WebSocket connections'
        )
        
        self.websocket_messages_total = Counter(
            'websocket_messages_total',
            'Total WebSocket messages',
            ['type', 'direction']
        )
        
        # Database metrics
        self.database_queries_total = Counter(
            'database_queries_total',
            'Total database queries',
            ['operation', 'table']
        )
        
        self.database_query_duration = Histogram(
            'database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table']
        )
        
        # Cache metrics
        self.cache_operations_total = Counter(
            'cache_operations_total',
            'Total cache operations',
            ['operation', 'result']
        )
        
        # API Integration metrics
        self.api_calls_total = Counter(
            'external_api_calls_total',
            'Total external API calls',
            ['provider', 'endpoint', 'status']
        )
        
        self.api_call_duration = Histogram(
            'external_api_call_duration_seconds',
            'External API call duration in seconds',
            ['provider', 'endpoint']
        )
        
        # Application info
        self.app_info = Info(
            'serp_strategist_app_info',
            'Application information'
        )
    
    def _init_fallback_metrics(self):
        """Initialize fallback metrics when Prometheus is not available"""
        self._counters = defaultdict(lambda: defaultdict(int))
        self._histograms = defaultdict(list)
        self._gauges = defaultdict(float)
        self._info = {}
    
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        if self.enabled:
            self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
        else:
            with self._lock:
                self._counters['http_requests'][f"{method}_{endpoint}_{status}"] += 1
                self._histograms[f"http_duration_{method}_{endpoint}"].append(duration)
    
    def record_http_exception(self, method: str, endpoint: str, exception: str):
        """Record HTTP request exception"""
        if self.enabled:
            self.http_request_exceptions.labels(method=method, endpoint=endpoint, exception=exception).inc()
        else:
            with self._lock:
                self._counters['http_exceptions'][f"{method}_{endpoint}_{exception}"] += 1
    
    def record_blueprint_generation(self, status: str, duration: float):
        """Record blueprint generation metrics"""
        if self.enabled:
            self.blueprint_generation_total.labels(status=status).inc()
            self.blueprint_generation_duration.observe(duration)
        else:
            with self._lock:
                self._counters['blueprint_generation'][status] += 1
                self._histograms['blueprint_duration'].append(duration)
    
    def record_blueprint_failure(self, error_type: str):
        """Record blueprint generation failure"""
        if self.enabled:
            self.blueprint_generation_failures.labels(error_type=error_type).inc()
        else:
            with self._lock:
                self._counters['blueprint_failures'][error_type] += 1
    
    def set_blueprint_queue_size(self, size: int):
        """Set current blueprint generation queue size"""
        if self.enabled:
            self.blueprint_generation_queue_size.set(size)
        else:
            with self._lock:
                self._gauges['blueprint_queue_size'] = size
    
    def record_websocket_connection(self, delta: int = 1):
        """Record WebSocket connection change"""
        if self.enabled:
            self.websocket_connections_active.inc(delta)
        else:
            with self._lock:
                self._gauges['websocket_connections'] += delta
    
    def record_websocket_message(self, msg_type: str, direction: str):
        """Record WebSocket message"""
        if self.enabled:
            self.websocket_messages_total.labels(type=msg_type, direction=direction).inc()
        else:
            with self._lock:
                self._counters['websocket_messages'][f"{msg_type}_{direction}"] += 1
    
    def record_database_query(self, operation: str, table: str, duration: float):
        """Record database query metrics"""
        if self.enabled:
            self.database_queries_total.labels(operation=operation, table=table).inc()
            self.database_query_duration.labels(operation=operation, table=table).observe(duration)
        else:
            with self._lock:
                self._counters['database_queries'][f"{operation}_{table}"] += 1
                self._histograms[f"db_duration_{operation}_{table}"].append(duration)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation"""
        if self.enabled:
            self.cache_operations_total.labels(operation=operation, result=result).inc()
        else:
            with self._lock:
                self._counters['cache_operations'][f"{operation}_{result}"] += 1
    
    def record_api_call(self, provider: str, endpoint: str, status: int, duration: float):
        """Record external API call metrics"""
        if self.enabled:
            self.api_calls_total.labels(provider=provider, endpoint=endpoint, status=status).inc()
            self.api_call_duration.labels(provider=provider, endpoint=endpoint).observe(duration)
        else:
            with self._lock:
                self._counters['api_calls'][f"{provider}_{endpoint}_{status}"] += 1
                self._histograms[f"api_duration_{provider}_{endpoint}"].append(duration)
    
    def set_app_info(self, version: str, environment: str):
        """Set application information"""
        if self.enabled:
            self.app_info.info({
                'version': version,
                'environment': environment,
                'python_version': __import__('sys').version,
            })
        else:
            with self._lock:
                self._info.update({
                    'version': version,
                    'environment': environment,
                })
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        if self.enabled:
            return generate_latest()
        else:
            # Return simple text format for fallback
            lines = []
            lines.append("# HELP serp_strategist_metrics Application metrics")
            lines.append("# TYPE serp_strategist_metrics counter")
            
            with self._lock:
                for metric_name, counters in self._counters.items():
                    for key, value in counters.items():
                        lines.append(f"serp_strategist_{metric_name}{{labels=\"{key}\"}} {value}")
                
                for metric_name, value in self._gauges.items():
                    lines.append(f"serp_strategist_{metric_name} {value}")
            
            return '\n'.join(lines)
    
    def get_content_type(self) -> str:
        """Get metrics content type"""
        if self.enabled:
            return CONTENT_TYPE_LATEST
        else:
            return 'text/plain'

# Global metrics collector
metrics = MetricsCollector()

def time_function(metric_name: str = None, labels: Dict[str, str] = None):
    """Decorator to time function execution"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record success
                if metric_name:
                    # Custom metric recording would go here
                    pass
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                # Record failure
                if metric_name:
                    # Custom metric recording would go here
                    pass
                
                raise
        return wrapper
    return decorator

def init_metrics(app, version: str = 'unknown', environment: str = 'unknown'):
    """Initialize metrics collection for Flask app"""
    metrics.set_app_info(version, environment)
    
    # Add metrics endpoint
    @app.route('/metrics')
    def metrics_endpoint():
        return metrics.get_metrics(), 200, {'Content-Type': metrics.get_content_type()}
    
    # Add request timing middleware
    @app.before_request
    def before_request():
        from flask import g
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        from flask import g, request
        
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            metrics.record_http_request(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code,
                duration=duration
            )
        
        return response
    
    app.logger.info(f"Metrics collection initialized (Prometheus: {'enabled' if metrics.enabled else 'disabled'})")
    return metrics