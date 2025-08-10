"""
Semantic Embeddings Service - Advanced text embedding generation

High-performance semantic embeddings service using sentence-transformers for the semantic
clustering pipeline. Provides efficient batch processing, caching, and comprehensive
error handling with integration into the existing SERP Strategist infrastructure.

Features:
- Sentence-transformers integration with multiple model support
- Async batch processing with configurable batch sizes
- Intelligent caching with TTL and LRU eviction
- Comprehensive error handling and timeout protection
- Model management with automatic fallback strategies
- Performance optimization and memory management
- Integration with existing pipeline patterns

Supported Models:
- sentence-transformers/all-MiniLM-L6-v2 (default, fast, 384d)
- sentence-transformers/all-mpnet-base-v2 (high quality, 768d) 
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (multilingual)
- Custom model loading from HuggingFace Hub

Performance Targets: <2s for real-time, <30s for batch processing, >85% accuracy
"""

import asyncio
import logging
import time
import hashlib
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from collections import OrderedDict
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor
import traceback

# Import existing infrastructure
from .async_request_manager import AsyncRequestManager
from .timeout_protection import get_timeout_protection, TimeoutConfig
from .clustering_models import EmbeddingData, ClusteringConfig

# Sentence transformers imports with fallback
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    torch = None

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingsConfig:
    """Configuration for semantic embeddings service"""
    
    # Model configuration
    default_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    model_cache_dir: Optional[str] = None
    device: str = "auto"  # auto, cpu, cuda
    
    # Processing configuration
    batch_size: int = 32
    max_sequence_length: int = 512
    normalize_embeddings: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 4
    request_timeout: float = 30.0
    model_load_timeout: float = 60.0
    
    # Caching settings
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour
    max_cache_size: int = 10000
    
    # Memory management
    enable_gc: bool = True
    gc_threshold: int = 1000  # Run GC after N operations
    max_memory_mb: int = 2048
    
    # Fallback configuration
    enable_fallback: bool = True
    fallback_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    fallback_embedding_size: int = 384


@dataclass
class ModelInfo:
    """Information about loaded embedding models"""
    model_name: str
    embedding_dimension: int
    max_sequence_length: int
    device: str
    load_time: float
    memory_usage_mb: float
    last_used: datetime = field(default_factory=datetime.utcnow)
    use_count: int = 0
    
    def update_usage(self):
        """Update usage statistics"""
        self.last_used = datetime.utcnow()
        self.use_count += 1


class EmbeddingCache:
    """LRU cache with TTL for embeddings"""
    
    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Tuple[EmbeddingData, float]] = OrderedDict()
        self.lock = threading.RLock()
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
    
    def _generate_key(self, text: str, model_name: str, normalize: bool) -> str:
        """Generate cache key for text and model"""
        key_data = {
            'text': text,
            'model_name': model_name,
            'normalize': normalize
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, text: str, model_name: str, normalize: bool = True) -> Optional[EmbeddingData]:
        """Get cached embedding if available and valid"""
        key = self._generate_key(text, model_name, normalize)
        
        with self.lock:
            if key in self.cache:
                embedding_data, timestamp = self.cache[key]
                
                # Check TTL
                if time.time() - timestamp < self.ttl_seconds:
                    # Move to end (most recently used)
                    self.cache.move_to_end(key)
                    self.hits += 1
                    return embedding_data
                else:
                    # Expired - remove
                    del self.cache[key]
            
            self.misses += 1
            return None
    
    def put(self, text: str, model_name: str, embedding_data: EmbeddingData, normalize: bool = True):
        """Cache embedding data"""
        key = self._generate_key(text, model_name, normalize)
        
        with self.lock:
            # Add to cache
            self.cache[key] = (embedding_data, time.time())
            self.cache.move_to_end(key)
            
            # Enforce size limit
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.evictions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
            
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate,
                'ttl_seconds': self.ttl_seconds
            }
    
    def clear(self):
        """Clear all cached embeddings"""
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0


class SemanticEmbeddingsService:
    """
    Advanced semantic embeddings service with sentence-transformers integration,
    batch processing, caching, and comprehensive error handling.
    """
    
    def __init__(self, config: Optional[EmbeddingsConfig] = None):
        """Initialize embeddings service"""
        self.config = config or EmbeddingsConfig()
        self.logger = logging.getLogger(__name__)
        
        # Service state
        self.initialized = False
        self.models: Dict[str, Any] = {}  # Loaded SentenceTransformer models
        self.model_info: Dict[str, ModelInfo] = {}
        
        # Threading and async management
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_concurrent_requests)
        self.model_lock = threading.RLock()
        self.operation_count = 0
        
        # Performance and caching
        if self.config.enable_caching:
            self.cache = EmbeddingCache(
                max_size=self.config.max_cache_size,
                ttl_seconds=self.config.cache_ttl_seconds
            )
        else:
            self.cache = None
        
        # Timeout protection
        self.timeout_protection = get_timeout_protection()
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'embeddings_generated': 0,
            'models_loaded': 0,
            'fallback_used': 0
        }
        
        # Check sentence-transformers availability
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            self.logger.warning(
                "sentence-transformers not available. Some functionality will be limited."
            )
        
        self.logger.info("Semantic Embeddings Service initialized")
    
    async def initialize(self):
        """Initialize the embeddings service"""
        if self.initialized:
            return
        
        try:
            self.logger.info("🚀 Initializing Semantic Embeddings Service...")
            
            # Check dependencies
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError(
                    "sentence-transformers is required for embeddings service. "
                    "Install with: pip install sentence-transformers"
                )
            
            # Load default model
            await self._load_model(self.config.default_model)
            
            self.initialized = True
            self.logger.info("✅ Semantic Embeddings Service initialization complete")
            
        except Exception as e:
            self.logger.error(f"Embeddings service initialization failed: {e}")
            raise
    
    async def _load_model(self, model_name: str, force_reload: bool = False) -> bool:
        """Load a sentence-transformers model"""
        
        if model_name in self.models and not force_reload:
            self.model_info[model_name].update_usage()
            return True
        
        try:
            self.logger.info(f"Loading embedding model: {model_name}")
            start_time = time.time()
            
            # Load model in thread pool to avoid blocking
            def _load_model_sync():
                try:
                    # Determine device
                    if self.config.device == "auto":
                        device = "cuda" if torch and torch.cuda.is_available() else "cpu"
                    else:
                        device = self.config.device
                    
                    # Load model
                    model = SentenceTransformer(model_name, cache_folder=self.config.model_cache_dir)
                    
                    # Move to device if specified
                    if device != "cpu":
                        model = model.to(device)
                    
                    return model, device
                    
                except Exception as e:
                    self.logger.error(f"Failed to load model {model_name}: {e}")
                    raise
            
            # Execute model loading with timeout
            result = await self.timeout_protection.protected_call(
                operation=lambda: asyncio.get_event_loop().run_in_executor(
                    self.thread_pool, _load_model_sync
                ),
                service_name="embeddings_service",
                operation_type="model_loading",
                timeout=self.config.model_load_timeout,
                enable_retry=False,
                enable_circuit_breaker=False
            )
            
            if not result.success:
                raise Exception(f"Model loading failed: {result.error}")
            
            model, device = result.data
            load_time = time.time() - start_time
            
            # Get model info
            embedding_dim = model.get_sentence_embedding_dimension()
            max_seq_length = getattr(model, 'max_seq_length', self.config.max_sequence_length)
            
            # Estimate memory usage (rough approximation)
            memory_usage_mb = embedding_dim * 4 / (1024 * 1024)  # Float32 bytes to MB
            
            with self.model_lock:
                self.models[model_name] = model
                self.model_info[model_name] = ModelInfo(
                    model_name=model_name,
                    embedding_dimension=embedding_dim,
                    max_sequence_length=max_seq_length,
                    device=device,
                    load_time=load_time,
                    memory_usage_mb=memory_usage_mb
                )
            
            self.metrics['models_loaded'] += 1
            self.logger.info(
                f"✅ Model {model_name} loaded successfully "
                f"(dim: {embedding_dim}, device: {device}, time: {load_time:.2f}s)"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model {model_name}: {e}")
            return False
    
    async def generate_embedding(
        self,
        text: str,
        model_name: Optional[str] = None,
        normalize: bool = None
    ) -> EmbeddingData:
        """Generate embedding for a single text"""
        
        embeddings = await self.generate_embeddings(
            texts=[text],
            model_name=model_name,
            normalize=normalize
        )
        
        if embeddings:
            return embeddings[0]
        else:
            raise Exception("Failed to generate embedding")
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model_name: Optional[str] = None,
        normalize: bool = None
    ) -> List[EmbeddingData]:
        """
        Generate embeddings for multiple texts with batch processing and caching
        
        Args:
            texts: List of texts to embed
            model_name: Model to use (defaults to config default)
            normalize: Whether to normalize embeddings (defaults to config setting)
            
        Returns:
            List of EmbeddingData objects with generated embeddings
        """
        
        if not self.initialized:
            await self.initialize()
        
        if not texts:
            return []
        
        # Use default values if not specified
        model_name = model_name or self.config.default_model
        normalize = normalize if normalize is not None else self.config.normalize_embeddings
        
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        try:
            # Filter and preprocess texts
            processed_texts = self._preprocess_texts(texts)
            
            if not processed_texts:
                self.logger.warning("No valid texts to process after preprocessing")
                return []
            
            # Check cache for existing embeddings
            embeddings_result = []
            texts_to_process = []
            cache_hits = 0
            
            if self.cache:
                for text in processed_texts:
                    cached_embedding = self.cache.get(text, model_name, normalize)
                    if cached_embedding:
                        embeddings_result.append(cached_embedding)
                        cache_hits += 1
                    else:
                        texts_to_process.append(text)
                        embeddings_result.append(None)  # Placeholder
            else:
                texts_to_process = processed_texts
                embeddings_result = [None] * len(processed_texts)
            
            self.metrics['cache_hits'] += cache_hits
            
            # Process remaining texts if any
            if texts_to_process:
                # Load model if needed
                if not await self._ensure_model_loaded(model_name):
                    # Try fallback model
                    if self.config.enable_fallback and model_name != self.config.fallback_model:
                        self.logger.warning(f"Falling back to model: {self.config.fallback_model}")
                        model_name = self.config.fallback_model
                        if not await self._ensure_model_loaded(model_name):
                            raise Exception("Failed to load primary and fallback models")
                        self.metrics['fallback_used'] += 1
                    else:
                        raise Exception(f"Failed to load model: {model_name}")
                
                # Generate embeddings for remaining texts
                new_embeddings = await self._generate_embeddings_batch(
                    texts_to_process, model_name, normalize
                )
                
                # Merge results and update cache
                new_embedding_idx = 0
                for i, existing_embedding in enumerate(embeddings_result):
                    if existing_embedding is None:
                        new_embedding = new_embeddings[new_embedding_idx]
                        embeddings_result[i] = new_embedding
                        new_embedding_idx += 1
                        
                        # Cache the new embedding
                        if self.cache:
                            self.cache.put(
                                processed_texts[i], model_name, new_embedding, normalize
                            )
            
            # Update metrics
            execution_time = time.time() - start_time
            self.metrics['successful_requests'] += 1
            self.metrics['embeddings_generated'] += len(embeddings_result)
            self._update_timing_metrics(execution_time)
            
            # Garbage collection if enabled
            if self.config.enable_gc:
                self.operation_count += 1
                if self.operation_count % self.config.gc_threshold == 0:
                    await self._run_garbage_collection()
            
            self.logger.info(
                f"Generated {len(embeddings_result)} embeddings "
                f"(cache hits: {cache_hits}, processing time: {execution_time:.3f}s)"
            )
            
            return embeddings_result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_requests'] += 1
            self._update_timing_metrics(execution_time)
            
            self.logger.error(f"Failed to generate embeddings: {e}")
            
            # Try fallback strategy
            if self.config.enable_fallback:
                return await self._generate_fallback_embeddings(texts, model_name)
            
            raise
    
    async def _ensure_model_loaded(self, model_name: str) -> bool:
        """Ensure model is loaded and available"""
        if model_name not in self.models:
            return await self._load_model(model_name)
        
        # Update usage statistics
        if model_name in self.model_info:
            self.model_info[model_name].update_usage()
        
        return True
    
    async def _generate_embeddings_batch(
        self,
        texts: List[str],
        model_name: str,
        normalize: bool
    ) -> List[EmbeddingData]:
        """Generate embeddings for a batch of texts"""
        
        try:
            model = self.models[model_name]
            model_info = self.model_info[model_name]
            
            # Process in batches if needed
            all_embeddings = []
            batch_size = self.config.batch_size
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Generate embeddings in thread pool
                def _generate_batch():
                    try:
                        vectors = model.encode(
                            batch_texts,
                            convert_to_numpy=True,
                            normalize_embeddings=normalize,
                            show_progress_bar=False
                        )
                        return vectors
                    except Exception as e:
                        self.logger.error(f"Batch embedding generation failed: {e}")
                        raise
                
                # Execute with timeout protection
                result = await self.timeout_protection.protected_call(
                    operation=lambda: asyncio.get_event_loop().run_in_executor(
                        self.thread_pool, _generate_batch
                    ),
                    service_name="embeddings_service",
                    operation_type="embedding_generation",
                    timeout=self.config.request_timeout,
                    enable_retry=True,
                    enable_circuit_breaker=True
                )
                
                if not result.success:
                    raise Exception(f"Embedding generation failed: {result.error}")
                
                vectors = result.data
                
                # Handle nested OperationResult (timeout protection issue)
                from .timeout_protection import OperationResult
                if isinstance(vectors, OperationResult):
                    if not vectors.success:
                        raise Exception(f"Nested operation failed: {vectors.error}")
                    vectors = vectors.data
                
                # Validate vectors result
                if vectors is None:
                    raise Exception("No vectors returned from embedding generation")
                
                if not hasattr(vectors, '__iter__') or not hasattr(vectors, '__len__'):
                    raise Exception(f"Invalid vectors format: {type(vectors)}")
                
                # Create EmbeddingData objects
                for j, (text, vector) in enumerate(zip(batch_texts, vectors)):
                    embedding_data = EmbeddingData(
                        vector=vector.tolist() if hasattr(vector, 'tolist') else list(vector),
                        text=text,
                        model_name=model_name,
                        embedding_timestamp=datetime.utcnow(),
                        vector_dimension=len(vector),
                        text_length=len(text),
                        token_count=len(text.split()),
                        confidence_score=1.0,
                        embedding_quality=self._estimate_embedding_quality(text, vector)
                    )
                    all_embeddings.append(embedding_data)
            
            return all_embeddings
            
        except Exception as e:
            self.logger.error(f"Batch embedding generation failed: {e}")
            raise
    
    def _preprocess_texts(self, texts: List[str]) -> List[str]:
        """Preprocess texts for embedding generation"""
        processed = []
        
        for text in texts:
            if not isinstance(text, str):
                continue
            
            # Basic preprocessing
            text = text.strip()
            
            # Length filtering
            if len(text) < 1:
                continue
            
            if len(text) > self.config.max_sequence_length * 4:  # Rough token estimate
                text = text[:self.config.max_sequence_length * 4]
            
            processed.append(text)
        
        return processed
    
    def _estimate_embedding_quality(self, text: str, vector: np.ndarray) -> float:
        """Estimate quality of generated embedding"""
        try:
            # Basic quality indicators
            quality_score = 0.8  # Base score
            
            # Check vector properties
            vector_norm = np.linalg.norm(vector)
            if vector_norm > 0:
                quality_score += 0.1
            
            # Check text properties
            if len(text.split()) > 3:  # Multi-word text generally better
                quality_score += 0.05
            
            if any(char.isalnum() for char in text):  # Contains meaningful characters
                quality_score += 0.05
            
            return min(quality_score, 1.0)
            
        except Exception:
            return 0.8  # Default quality score
    
    async def _generate_fallback_embeddings(
        self,
        texts: List[str],
        original_model: str
    ) -> List[EmbeddingData]:
        """Generate fallback embeddings when primary method fails"""
        
        try:
            self.logger.info("Attempting fallback embedding generation")
            
            # Try different fallback strategies
            fallback_strategies = [
                # Strategy 1: Use fallback model
                lambda: self.generate_embeddings(texts, self.config.fallback_model),
                
                # Strategy 2: Generate random embeddings (last resort)
                lambda: self._generate_random_embeddings(texts)
            ]
            
            for strategy in fallback_strategies:
                try:
                    result = await strategy()
                    if result:
                        self.metrics['fallback_used'] += 1
                        return result
                except Exception as e:
                    self.logger.warning(f"Fallback strategy failed: {e}")
                    continue
            
            # If all fallback strategies fail, generate minimal embeddings
            return self._generate_random_embeddings(texts)
            
        except Exception as e:
            self.logger.error(f"All fallback strategies failed: {e}")
            raise
    
    def _generate_random_embeddings(self, texts: List[str]) -> List[EmbeddingData]:
        """Generate random embeddings as last resort"""
        
        self.logger.warning("Generating random embeddings as fallback")
        embeddings = []
        
        for text in texts:
            # Generate random vector with proper dimension
            vector = np.random.normal(0, 1, self.config.fallback_embedding_size)
            vector = vector / np.linalg.norm(vector)  # Normalize
            
            embedding_data = EmbeddingData(
                vector=vector.tolist(),
                text=text,
                model_name="random_fallback",
                embedding_timestamp=datetime.utcnow(),
                vector_dimension=len(vector),
                text_length=len(text),
                token_count=len(text.split()),
                confidence_score=0.1,  # Very low confidence for random embeddings
                embedding_quality=0.1
            )
            embeddings.append(embedding_data)
        
        return embeddings
    
    async def _run_garbage_collection(self):
        """Run garbage collection to manage memory"""
        try:
            import gc
            gc.collect()
            
            if torch and torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            self.logger.warning(f"Garbage collection failed: {e}")
    
    def _update_timing_metrics(self, execution_time: float):
        """Update timing-related metrics"""
        self.metrics['total_processing_time'] += execution_time
        
        if self.metrics['total_requests'] > 0:
            self.metrics['average_processing_time'] = (
                self.metrics['total_processing_time'] / self.metrics['total_requests']
            )
    
    async def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about loaded models"""
        if model_name:
            if model_name in self.model_info:
                info = self.model_info[model_name]
                return {
                    'model_name': info.model_name,
                    'embedding_dimension': info.embedding_dimension,
                    'max_sequence_length': info.max_sequence_length,
                    'device': info.device,
                    'load_time': info.load_time,
                    'memory_usage_mb': info.memory_usage_mb,
                    'last_used': info.last_used.isoformat(),
                    'use_count': info.use_count
                }
            else:
                return {'error': f'Model {model_name} not loaded'}
        else:
            # Return info for all loaded models
            return {
                name: {
                    'model_name': info.model_name,
                    'embedding_dimension': info.embedding_dimension,
                    'max_sequence_length': info.max_sequence_length,
                    'device': info.device,
                    'load_time': info.load_time,
                    'memory_usage_mb': info.memory_usage_mb,
                    'last_used': info.last_used.isoformat(),
                    'use_count': info.use_count
                }
                for name, info in self.model_info.items()
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service metrics"""
        
        cache_stats = self.cache.get_stats() if self.cache else {
            'cache_size': 0, 'hits': 0, 'misses': 0, 'hit_rate': 0.0
        }
        
        return {
            'service_metrics': self.metrics,
            'cache_performance': cache_stats,
            'model_information': await self.get_model_info(),
            'configuration': {
                'default_model': self.config.default_model,
                'batch_size': self.config.batch_size,
                'max_sequence_length': self.config.max_sequence_length,
                'normalize_embeddings': self.config.normalize_embeddings,
                'enable_caching': self.config.enable_caching,
                'max_concurrent_requests': self.config.max_concurrent_requests
            },
            'system_status': {
                'initialized': self.initialized,
                'models_loaded': len(self.models),
                'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
                'torch_available': torch is not None,
                'cuda_available': torch.cuda.is_available() if torch else False
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the embeddings service"""
        try:
            # Test embedding generation
            test_result = await self.generate_embedding("health check test")
            
            return {
                'status': 'healthy' if test_result else 'degraded',
                'last_test_time': datetime.utcnow().isoformat(),
                'models_loaded': len(self.models),
                'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE,
                'cache_status': self.cache.get_stats() if self.cache else None,
                'performance': {
                    'average_processing_time': self.metrics['average_processing_time'],
                    'success_rate': (
                        self.metrics['successful_requests'] / 
                        max(self.metrics['total_requests'], 1)
                    )
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_test_time': datetime.utcnow().isoformat(),
                'traceback': traceback.format_exc()
            }
    
    async def shutdown(self):
        """Gracefully shutdown the embeddings service"""
        try:
            self.logger.info("🛑 Shutting down Semantic Embeddings Service...")
            
            # Clear cache
            if self.cache:
                self.cache.clear()
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear models to free memory
            with self.model_lock:
                self.models.clear()
                self.model_info.clear()
            
            # Run final garbage collection
            await self._run_garbage_collection()
            
            self.initialized = False
            self.logger.info("✅ Semantic Embeddings Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Global instance management
_global_embeddings_service: Optional[SemanticEmbeddingsService] = None

async def get_embeddings_service(config: Optional[EmbeddingsConfig] = None) -> SemanticEmbeddingsService:
    """Get global embeddings service instance"""
    global _global_embeddings_service
    
    if _global_embeddings_service is None:
        _global_embeddings_service = SemanticEmbeddingsService(config)
        await _global_embeddings_service.initialize()
    
    return _global_embeddings_service


def configure_embeddings_service(config: EmbeddingsConfig):
    """Configure global embeddings service"""
    global _global_embeddings_service
    _global_embeddings_service = SemanticEmbeddingsService(config)