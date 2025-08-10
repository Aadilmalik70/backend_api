"""
AI Manager - Central coordinator for all AI models and services

Manages model loading, memory optimization, and intelligent caching for:
- spaCy NLP models
- sentence-transformers embeddings
- scikit-learn ML models
- networkx graph analysis

Designed for 8GB RAM / 4-core constraints with intelligent resource management.
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import gc
import time
from functools import lru_cache
import json

class AIManager:
    """
    Central AI service coordinator with intelligent resource management.
    
    Features:
    - Singleton pattern for model sharing across requests
    - Memory-efficient model loading and caching
    - Async processing with ThreadPoolExecutor
    - Resource monitoring and garbage collection
    - Intelligent model warming and preloading
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        
        # Service instances
        self.nlp_service = None
        self.semantic_service = None
        self.ml_service = None
        self.graph_service = None
        
        # Configuration
        self.config = {
            'max_workers': min(4, (psutil.cpu_count() or 2) + 1),
            'memory_threshold': 0.85,  # 85% of 8GB = ~6.8GB
            'cache_size': 1000,
            'model_warmup': True,
            'batch_size': 32,
            'gc_interval': 100  # requests
        }
        
        # Resource monitoring
        self.request_count = 0
        self.model_cache = {}
        self.performance_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'memory_usage': [],
            'processing_times': []
        }
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        
        self.logger.info(f"AIManager initialized with {self.config['max_workers']} workers")
        self._initialized = True
    
    async def initialize_services(self) -> bool:
        """
        Initialize all AI services with lazy loading and error handling.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing AI services...")
            
            # Check memory availability
            memory_info = psutil.virtual_memory()
            available_gb = memory_info.available / (1024**3)
            
            if available_gb < 2.0:
                self.logger.warning(f"Low memory detected: {available_gb:.1f}GB available")
                self.config['batch_size'] = 16  # Reduce batch size
            
            # Initialize services in order of memory usage (lightest first)
            services_to_init = [
                ('graph_service', self._init_graph_service),
                ('ml_service', self._init_ml_service),
                ('semantic_service', self._init_semantic_service),
                ('nlp_service', self._init_nlp_service)
            ]
            
            initialized_services = []
            for service_name, init_func in services_to_init:
                try:
                    service = await init_func()
                    setattr(self, service_name, service)
                    initialized_services.append(service_name)
                    
                    # Monitor memory after each service
                    self._check_memory_usage()
                    
                except Exception as e:
                    self.logger.error(f"Failed to initialize {service_name}: {str(e)}")
                    # Continue with other services
            
            if initialized_services:
                self.logger.info(f"✅ Initialized services: {', '.join(initialized_services)}")
                
                # Warm up models if configured
                if self.config['model_warmup']:
                    await self._warm_up_models()
                
                return True
            
            self.logger.error("❌ No AI services could be initialized")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ AI services initialization failed: {str(e)}")
            return False
    
    async def _init_nlp_service(self):
        """Initialize spaCy NLP service with error handling."""
        try:
            from .nlp_service import NLPService
            service = NLPService()
            await service.initialize()
            self.logger.info("✅ NLP Service (spaCy) initialized")
            return service
        except ImportError as e:
            self.logger.warning(f"spaCy not available: {e}")
            return None
        except Exception as e:
            self.logger.error(f"NLP Service initialization failed: {e}")
            return None
    
    async def _init_semantic_service(self):
        """Initialize sentence-transformers semantic service."""
        try:
            from .semantic_service import SemanticService
            service = SemanticService()
            await service.initialize()
            self.logger.info("✅ Semantic Service (sentence-transformers) initialized")
            return service
        except ImportError as e:
            self.logger.warning(f"sentence-transformers not available: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Semantic Service initialization failed: {e}")
            return None
    
    async def _init_ml_service(self):
        """Initialize scikit-learn ML service."""
        try:
            from .ml_service import MLService
            service = MLService()
            await service.initialize()
            self.logger.info("✅ ML Service (scikit-learn) initialized")
            return service
        except ImportError as e:
            self.logger.warning(f"scikit-learn not available: {e}")
            return None
        except Exception as e:
            self.logger.error(f"ML Service initialization failed: {e}")
            return None
    
    async def _init_graph_service(self):
        """Initialize NetworkX graph service."""
        try:
            from .graph_service import GraphService
            service = GraphService()
            await service.initialize()
            self.logger.info("✅ Graph Service (NetworkX) initialized")
            return service
        except ImportError as e:
            self.logger.warning(f"NetworkX not available: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Graph Service initialization failed: {e}")
            return None
    
    async def _warm_up_models(self):
        """Warm up models with sample data to optimize performance."""
        try:
            self.logger.info("🔥 Warming up AI models...")
            
            sample_texts = [
                "Sample content for model warming",
                "SEO optimization and content strategy",
                "Competitor analysis and market research"
            ]
            
            # Warm up available services
            warm_up_tasks = []
            
            if self.nlp_service:
                warm_up_tasks.append(self.nlp_service.process_batch(sample_texts))
            
            if self.semantic_service:
                warm_up_tasks.append(self.semantic_service.encode_batch(sample_texts))
            
            if warm_up_tasks:
                await asyncio.gather(*warm_up_tasks, return_exceptions=True)
                self.logger.info("✅ Model warm-up completed")
            
        except Exception as e:
            self.logger.warning(f"Model warm-up failed: {e}")
    
    async def process_content_parallel(self, content_data: List[str]) -> Dict[str, Any]:
        """
        Process content using all available AI services in parallel.
        
        Args:
            content_data: List of text content to analyze
            
        Returns:
            Dict containing analysis results from all services
        """
        start_time = time.time()
        self.request_count += 1
        
        try:
            # Prepare processing tasks
            tasks = []
            results = {}
            
            if self.nlp_service:
                tasks.append(('nlp', self.nlp_service.process_batch(content_data)))
            
            if self.semantic_service:
                tasks.append(('semantic', self.semantic_service.analyze_batch(content_data)))
            
            if self.ml_service:
                tasks.append(('ml', self.ml_service.classify_batch(content_data)))
            
            if self.graph_service and len(content_data) > 1:
                tasks.append(('graph', self.graph_service.build_content_graph(content_data)))
            
            # Execute tasks in parallel
            if tasks:
                task_results = await asyncio.gather(
                    *[task for _, task in tasks],
                    return_exceptions=True
                )
                
                # Combine results
                for (service_name, _), result in zip(tasks, task_results):
                    if isinstance(result, Exception):
                        self.logger.warning(f"{service_name} service failed: {result}")
                        results[service_name] = None
                    else:
                        results[service_name] = result
            
            # Performance tracking
            processing_time = time.time() - start_time
            self.performance_metrics['total_requests'] += 1
            self.performance_metrics['processing_times'].append(processing_time)
            
            # Periodic cleanup
            if self.request_count % self.config['gc_interval'] == 0:
                self._perform_cleanup()
            
            self.logger.debug(f"Content processing completed in {processing_time:.2f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {str(e)}")
            return {}
    
    def _check_memory_usage(self):
        """Monitor memory usage and trigger cleanup if needed."""
        try:
            memory_info = psutil.virtual_memory()
            memory_percent = memory_info.percent / 100
            
            self.performance_metrics['memory_usage'].append(memory_percent)
            
            if memory_percent > self.config['memory_threshold']:
                self.logger.warning(f"High memory usage: {memory_percent:.1%}")
                self._perform_cleanup()
                
        except Exception as e:
            self.logger.error(f"Memory monitoring failed: {e}")
    
    def _perform_cleanup(self):
        """Perform garbage collection and cleanup operations."""
        try:
            # Clear old performance metrics
            if len(self.performance_metrics['memory_usage']) > 1000:
                self.performance_metrics['memory_usage'] = self.performance_metrics['memory_usage'][-500:]
            
            if len(self.performance_metrics['processing_times']) > 1000:
                self.performance_metrics['processing_times'] = self.performance_metrics['processing_times'][-500:]
            
            # Force garbage collection
            gc.collect()
            
            self.logger.debug("Performed cleanup and garbage collection")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    @lru_cache(maxsize=1000)
    def get_cached_result(self, content_hash: str, operation: str) -> Optional[Any]:
        """
        Get cached result for content analysis.
        
        Args:
            content_hash: Hash of the content
            operation: Type of analysis operation
            
        Returns:
            Cached result or None if not found
        """
        cache_key = f"{content_hash}_{operation}"
        result = self.model_cache.get(cache_key)
        
        if result:
            self.performance_metrics['cache_hits'] += 1
        
        return result
    
    def cache_result(self, content_hash: str, operation: str, result: Any):
        """
        Cache analysis result.
        
        Args:
            content_hash: Hash of the content
            operation: Type of analysis operation  
            result: Analysis result to cache
        """
        cache_key = f"{content_hash}_{operation}"
        self.model_cache[cache_key] = result
        
        # Limit cache size
        if len(self.model_cache) > self.config['cache_size']:
            # Remove oldest entries
            oldest_keys = list(self.model_cache.keys())[:100]
            for key in oldest_keys:
                del self.model_cache[key]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics and system status."""
        try:
            memory_info = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Calculate averages
            avg_processing_time = (
                sum(self.performance_metrics['processing_times'][-100:]) / 
                min(len(self.performance_metrics['processing_times']), 100)
            ) if self.performance_metrics['processing_times'] else 0
            
            cache_hit_rate = (
                self.performance_metrics['cache_hits'] / 
                max(self.performance_metrics['total_requests'], 1)
            )
            
            return {
                'ai_services_status': {
                    'nlp_service': self.nlp_service is not None,
                    'semantic_service': self.semantic_service is not None,
                    'ml_service': self.ml_service is not None,
                    'graph_service': self.graph_service is not None
                },
                'resource_usage': {
                    'memory_percent': memory_info.percent,
                    'memory_available_gb': memory_info.available / (1024**3),
                    'cpu_percent': cpu_percent,
                    'thread_pool_workers': self.config['max_workers']
                },
                'performance_metrics': {
                    'total_requests': self.performance_metrics['total_requests'],
                    'cache_hit_rate': cache_hit_rate,
                    'avg_processing_time': avg_processing_time,
                    'cache_size': len(self.model_cache)
                },
                'configuration': self.config
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return {}
    
    def shutdown(self):
        """Gracefully shutdown AI services and cleanup resources."""
        try:
            self.logger.info("🛑 Shutting down AI services...")
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear caches
            self.model_cache.clear()
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("✅ AI services shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

# Global AI manager instance
ai_manager = AIManager()