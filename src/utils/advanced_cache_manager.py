"""
Advanced Cache Manager - Multi-tier intelligent caching system.

This module provides a sophisticated caching strategy with multiple tiers,
intelligent invalidation, and performance optimization for blueprint generation.
"""

import redis
import pickle
import json
import hashlib
import logging
import time
from typing import Any, Dict, Optional, Union, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import threading
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheTier(Enum):
    """Cache tier enumeration"""
    L1_MEMORY = "L1_memory"
    L2_REDIS = "L2_redis"
    L3_DATABASE = "L3_database"

@dataclass
class CacheConfig:
    """Cache configuration for different tiers"""
    tier: CacheTier
    size_limit: str
    ttl_seconds: int
    compression: bool = False
    serialization: str = "json"  # json, pickle
    
class CacheStats:
    """Cache statistics and performance metrics"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.invalidations = 0
        self.write_operations = 0
        self.total_requests = 0
        self.average_response_time = 0.0
        self._lock = threading.Lock()
    
    def record_hit(self, response_time: float):
        """Record cache hit with response time"""
        with self._lock:
            self.hits += 1
            self.total_requests += 1
            self._update_avg_response_time(response_time)
    
    def record_miss(self, response_time: float):
        """Record cache miss with response time"""
        with self._lock:
            self.misses += 1
            self.total_requests += 1
            self._update_avg_response_time(response_time)
    
    def record_write(self):
        """Record cache write operation"""
        with self._lock:
            self.write_operations += 1
    
    def record_invalidation(self):
        """Record cache invalidation"""
        with self._lock:
            self.invalidations += 1
    
    def _update_avg_response_time(self, response_time: float):
        """Update average response time"""
        if self.total_requests == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_requests - 1) + response_time) 
                / self.total_requests
            )
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hit_rate,
            'total_requests': self.total_requests,
            'invalidations': self.invalidations,
            'write_operations': self.write_operations,
            'average_response_time_ms': round(self.average_response_time * 1000, 2)
        }

class AdvancedCacheManager:
    """
    Multi-tier intelligent caching system with automatic tier management,
    smart invalidation, and performance optimization.
    """
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        """
        Initialize the advanced cache manager.
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        
        # Cache configurations
        self.cache_configs = {
            CacheTier.L1_MEMORY: CacheConfig(
                tier=CacheTier.L1_MEMORY,
                size_limit="512MB",
                ttl_seconds=300,  # 5 minutes
                compression=False,
                serialization="json"
            ),
            CacheTier.L2_REDIS: CacheConfig(
                tier=CacheTier.L2_REDIS,
                size_limit="2GB",
                ttl_seconds=3600,  # 1 hour
                compression=True,
                serialization="pickle"
            ),
            CacheTier.L3_DATABASE: CacheConfig(
                tier=CacheTier.L3_DATABASE,
                size_limit="Unlimited",
                ttl_seconds=86400,  # 24 hours
                compression=True,
                serialization="json"
            )
        }
        
        # Initialize cache tiers
        self._init_cache_tiers()
        
        # Cache statistics
        self.stats = {tier: CacheStats() for tier in CacheTier}
        
        # Cache invalidation patterns
        self.invalidation_patterns = {
            'keyword_analysis': [
                'competitor_analysis_{keyword}',
                'serp_features_{keyword}',
                'content_insights_{keyword}'
            ],
            'blueprint_generation': [
                'blueprint_{keyword}_{user_id}',
                'user_blueprints_{user_id}'
            ],
            'api_responses': [
                'google_apis_status',
                'health_check'
            ]
        }
        
        logger.info("Advanced Cache Manager initialized successfully")
    
    def _init_cache_tiers(self):
        """Initialize all cache tiers"""
        # L1: In-memory cache (Python dict with size limits)
        self.l1_cache = {}
        self.l1_access_times = {}
        self.l1_max_size = 1000  # Maximum number of items
        
        # L2: Redis cache
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=0,
                decode_responses=False,  # Keep binary for pickle
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis cache tier initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, L2 cache disabled: {e}")
            self.redis_client = None
            self.redis_available = False
        
        # L3: Database cache (will be implemented with database operations)
        self.db_cache_enabled = True
    
    def _generate_cache_key(self, namespace: str, identifier: str, 
                          additional_params: Optional[Dict] = None) -> str:
        """Generate a consistent cache key"""
        key_components = [namespace, identifier]
        
        if additional_params:
            # Sort params for consistent key generation
            sorted_params = sorted(additional_params.items())
            params_str = "_".join([f"{k}:{v}" for k, v in sorted_params])
            key_components.append(params_str)
        
        cache_key = "_".join(key_components)
        
        # Hash if key is too long
        if len(cache_key) > 200:
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
        
        return cache_key
    
    def _serialize_data(self, data: Any, serialization: str) -> bytes:
        """Serialize data based on configuration"""
        if serialization == "json":
            return json.dumps(data, default=str).encode('utf-8')
        elif serialization == "pickle":
            return pickle.dumps(data)
        else:
            raise ValueError(f"Unsupported serialization method: {serialization}")
    
    def _deserialize_data(self, data: bytes, serialization: str) -> Any:
        """Deserialize data based on configuration"""
        if serialization == "json":
            return json.loads(data.decode('utf-8'))
        elif serialization == "pickle":
            return pickle.loads(data)
        else:
            raise ValueError(f"Unsupported serialization method: {serialization}")
    
    def _get_from_l1(self, key: str) -> Optional[Any]:
        """Get data from L1 memory cache"""
        start_time = time.time()
        
        if key in self.l1_cache:
            # Update access time for LRU
            self.l1_access_times[key] = datetime.now()
            response_time = time.time() - start_time
            self.stats[CacheTier.L1_MEMORY].record_hit(response_time)
            logger.debug(f"L1 cache hit for key: {key}")
            return self.l1_cache[key]
        
        response_time = time.time() - start_time
        self.stats[CacheTier.L1_MEMORY].record_miss(response_time)
        return None
    
    def _set_to_l1(self, key: str, data: Any):
        """Set data to L1 memory cache with LRU eviction"""
        # Check size limits and evict if necessary
        if len(self.l1_cache) >= self.l1_max_size:
            self._evict_l1_lru()
        
        self.l1_cache[key] = data
        self.l1_access_times[key] = datetime.now()
        self.stats[CacheTier.L1_MEMORY].record_write()
        logger.debug(f"Data cached in L1 for key: {key}")
    
    def _evict_l1_lru(self):
        """Evict least recently used item from L1 cache"""
        if not self.l1_access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.l1_access_times.keys(), 
                     key=lambda k: self.l1_access_times[k])
        
        # Remove from cache
        del self.l1_cache[lru_key]
        del self.l1_access_times[lru_key]
        logger.debug(f"Evicted LRU item from L1: {lru_key}")
    
    def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get data from L2 Redis cache"""
        if not self.redis_available:
            return None
        
        start_time = time.time()
        
        try:
            cached_data = self.redis_client.get(key)
            response_time = time.time() - start_time
            
            if cached_data:
                config = self.cache_configs[CacheTier.L2_REDIS]
                data = self._deserialize_data(cached_data, config.serialization)
                self.stats[CacheTier.L2_REDIS].record_hit(response_time)
                logger.debug(f"L2 cache hit for key: {key}")
                
                # Also cache in L1 for faster access
                self._set_to_l1(key, data)
                
                return data
            
            self.stats[CacheTier.L2_REDIS].record_miss(response_time)
            return None
            
        except Exception as e:
            response_time = time.time() - start_time
            self.stats[CacheTier.L2_REDIS].record_miss(response_time)
            logger.warning(f"Redis get error for key {key}: {e}")
            return None
    
    def _set_to_l2(self, key: str, data: Any, ttl: Optional[int] = None):
        """Set data to L2 Redis cache"""
        if not self.redis_available:
            return
        
        try:
            config = self.cache_configs[CacheTier.L2_REDIS]
            serialized_data = self._serialize_data(data, config.serialization)
            
            ttl = ttl or config.ttl_seconds
            self.redis_client.setex(key, ttl, serialized_data)
            self.stats[CacheTier.L2_REDIS].record_write()
            logger.debug(f"Data cached in L2 for key: {key} with TTL: {ttl}")
            
        except Exception as e:
            logger.warning(f"Redis set error for key {key}: {e}")
    
    def get(self, namespace: str, identifier: str, 
           additional_params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get data from cache using tier hierarchy (L1 -> L2 -> L3)
        
        Args:
            namespace: Cache namespace (e.g., 'competitor_analysis')
            identifier: Unique identifier (e.g., keyword)
            additional_params: Additional parameters for cache key generation
            
        Returns:
            Cached data if found, None otherwise
        """
        cache_key = self._generate_cache_key(namespace, identifier, additional_params)
        
        # Try L1 first
        data = self._get_from_l1(cache_key)
        if data is not None:
            return data
        
        # Try L2 Redis
        data = self._get_from_l2(cache_key)
        if data is not None:
            return data
        
        # L3 Database cache would be checked here in a full implementation
        # For now, return None
        logger.debug(f"Cache miss for key: {cache_key}")
        return None
    
    def set(self, namespace: str, identifier: str, data: Any,
           ttl: Optional[int] = None, additional_params: Optional[Dict] = None):
        """
        Set data to cache across appropriate tiers
        
        Args:
            namespace: Cache namespace
            identifier: Unique identifier
            data: Data to cache
            ttl: Time to live in seconds (optional)
            additional_params: Additional parameters for cache key generation
        """
        cache_key = self._generate_cache_key(namespace, identifier, additional_params)
        
        # Cache in L1 (memory)
        self._set_to_l1(cache_key, data)
        
        # Cache in L2 (Redis)
        self._set_to_l2(cache_key, data, ttl)
        
        logger.debug(f"Data cached across tiers for key: {cache_key}")
    
    def invalidate(self, namespace: str, identifier: str = None,
                  pattern: str = None, tier: CacheTier = None):
        """
        Invalidate cache entries based on namespace, identifier, or pattern
        
        Args:
            namespace: Cache namespace to invalidate
            identifier: Specific identifier to invalidate (optional)
            pattern: Invalidation pattern name (optional)
            tier: Specific tier to invalidate (optional, defaults to all)
        """
        if pattern and pattern in self.invalidation_patterns:
            # Use predefined invalidation pattern
            patterns = self.invalidation_patterns[pattern]
            for p in patterns:
                self._invalidate_by_pattern(p, tier)
        elif identifier:
            # Invalidate specific key
            cache_key = self._generate_cache_key(namespace, identifier)
            self._invalidate_key(cache_key, tier)
        else:
            # Invalidate all keys with namespace
            self._invalidate_namespace(namespace, tier)
    
    def _invalidate_key(self, cache_key: str, tier: CacheTier = None):
        """Invalidate a specific cache key"""
        if tier is None or tier == CacheTier.L1_MEMORY:
            if cache_key in self.l1_cache:
                del self.l1_cache[cache_key]
                del self.l1_access_times[cache_key]
                self.stats[CacheTier.L1_MEMORY].record_invalidation()
        
        if tier is None or tier == CacheTier.L2_REDIS:
            if self.redis_available:
                try:
                    self.redis_client.delete(cache_key)
                    self.stats[CacheTier.L2_REDIS].record_invalidation()
                except Exception as e:
                    logger.warning(f"Redis delete error for key {cache_key}: {e}")
        
        logger.debug(f"Invalidated cache key: {cache_key}")
    
    def _invalidate_by_pattern(self, pattern: str, tier: CacheTier = None):
        """Invalidate cache entries matching a pattern"""
        # For L1 cache
        if tier is None or tier == CacheTier.L1_MEMORY:
            keys_to_delete = [key for key in self.l1_cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self.l1_cache[key]
                del self.l1_access_times[key]
                self.stats[CacheTier.L1_MEMORY].record_invalidation()
        
        # For L2 Redis cache
        if (tier is None or tier == CacheTier.L2_REDIS) and self.redis_available:
            try:
                pattern_key = f"*{pattern}*"
                keys = self.redis_client.keys(pattern_key)
                if keys:
                    self.redis_client.delete(*keys)
                    self.stats[CacheTier.L2_REDIS].record_invalidation()
            except Exception as e:
                logger.warning(f"Redis pattern delete error for {pattern}: {e}")
        
        logger.debug(f"Invalidated cache entries matching pattern: {pattern}")
    
    def _invalidate_namespace(self, namespace: str, tier: CacheTier = None):
        """Invalidate all cache entries in a namespace"""
        self._invalidate_by_pattern(namespace, tier)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            'tiers': {tier.value: tier_stats.get_stats() 
                     for tier, tier_stats in self.stats.items()},
            'overall': {
                'total_hits': sum(s.hits for s in self.stats.values()),
                'total_misses': sum(s.misses for s in self.stats.values()),
                'total_requests': sum(s.total_requests for s in self.stats.values()),
                'overall_hit_rate': 0.0,
                'redis_available': self.redis_available,
                'l1_cache_size': len(self.l1_cache)
            }
        }
        
        # Calculate overall hit rate
        total_requests = stats['overall']['total_requests']
        if total_requests > 0:
            stats['overall']['overall_hit_rate'] = (
                stats['overall']['total_hits'] / total_requests
            )
        
        return stats
    
    def clear_all_caches(self):
        """Clear all cache tiers"""
        # Clear L1
        self.l1_cache.clear()
        self.l1_access_times.clear()
        
        # Clear L2
        if self.redis_available:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis flush error: {e}")
        
        logger.info("All cache tiers cleared")

# Decorator for automatic caching
def cache_result(namespace: str, ttl: int = 3600, 
                include_args: bool = True, cache_manager: AdvancedCacheManager = None):
    """
    Decorator for automatic caching of function results
    
    Args:
        namespace: Cache namespace
        ttl: Time to live in seconds
        include_args: Include function arguments in cache key
        cache_manager: Cache manager instance (optional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use global cache manager if not provided
            nonlocal cache_manager
            if cache_manager is None:
                cache_manager = get_default_cache_manager()
            
            # Generate cache identifier
            if include_args:
                identifier = f"{func.__name__}_{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            else:
                identifier = func.__name__
            
            # Try to get from cache
            cached_result = cache_manager.get(namespace, identifier)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(namespace, identifier, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global cache manager instance
_global_cache_manager = None

def get_default_cache_manager() -> AdvancedCacheManager:
    """Get the default global cache manager instance"""
    global _global_cache_manager
    if _global_cache_manager is None:
        _global_cache_manager = AdvancedCacheManager()
    return _global_cache_manager

def initialize_cache_manager(redis_host: str = 'localhost', 
                           redis_port: int = 6379) -> AdvancedCacheManager:
    """Initialize and configure the global cache manager"""
    global _global_cache_manager
    _global_cache_manager = AdvancedCacheManager(redis_host, redis_port)
    return _global_cache_manager