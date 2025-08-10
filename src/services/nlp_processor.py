"""
NLP Processor Service - Production-ready NLP processing with advanced caching

Comprehensive NLP processing service integrating:
- spaCy en_core_web_lg for linguistic analysis
- sentence-transformers all-MiniLM-L6-v2 for semantic embeddings
- Advanced caching with model warmup and embedding cache
- Async processing with batch operations
- Memory optimization for 8GB constraints
- Performance monitoring and resource tracking

Designed for high-performance production deployment with intelligent fallbacks.
"""

import asyncio
import hashlib
import logging
import time
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import numpy as np
import psutil
from datetime import datetime, timedelta
import spacy

# Import caching infrastructure
from utils.advanced_cache_manager import get_global_cache_manager, ultra_cache

logger = logging.getLogger(__name__)

@dataclass
class NLPConfig:
    """Configuration for NLP Processor Service"""
    # Model Configuration
    spacy_model: str = "en_core_web_lg"
    spacy_fallback_models: List[str] = field(default_factory=lambda: ["en_core_web_md", "en_core_web_sm"])
    sentence_transformer_model: str = "all-MiniLM-L6-v2"
    
    # Performance Configuration
    max_workers: int = 4
    batch_size: int = 32
    max_text_length: int = 1000000  # 1MB max text length
    embedding_dimensions: int = 384  # all-MiniLM-L6-v2 dimensions
    
    # Caching Configuration
    enable_model_warmup: bool = True
    enable_embedding_cache: bool = True
    cache_ttl_hours: int = 24
    max_cache_size: int = 10000
    
    # Memory Management
    memory_limit_gb: float = 6.0  # Reserve 2GB for other processes
    gc_threshold: int = 1000
    model_unload_threshold_gb: float = 7.0
    
    # Processing Thresholds
    min_text_length: int = 3
    max_batch_processing_time: float = 30.0  # seconds
    similarity_threshold: float = 0.7


@dataclass
class ProcessingMetrics:
    """Metrics for NLP processing performance"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    memory_usage_mb: float = 0.0
    model_load_time: float = 0.0
    last_reset_time: float = field(default_factory=time.time)
    
    def record_request(self, processing_time: float, success: bool, cache_hit: bool):
        """Record a processing request"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            
        self.total_processing_time += processing_time
        self.avg_processing_time = self.total_processing_time / max(self.total_requests, 1)
        self.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return (self.cache_hits / total_cache_requests) * 100


class NLPProcessor:
    """
    Production-ready NLP Processor with advanced caching and async processing.
    
    Features:
    - spaCy en_core_web_lg integration with fallback models
    - sentence-transformers all-MiniLM-L6-v2 for semantic embeddings
    - Advanced caching for models and embeddings
    - Async batch processing for high throughput
    - Memory optimization and resource monitoring
    - Comprehensive error handling and fallbacks
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config: Optional[NLPConfig] = None):
        """Singleton pattern for memory efficiency"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config: Optional[NLPConfig] = None):
        if self._initialized:
            return
            
        self.config = config or NLPConfig()
        self.cache_manager = get_global_cache_manager()
        self.metrics = ProcessingMetrics()
        
        # Model instances
        self.spacy_nlp = None
        self.sentence_model = None
        self.models_loaded = False
        self.warmup_completed = False
        
        # Threading and async processing
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.max_workers, thread_name_prefix="NLP")
        self.model_lock = threading.RLock()
        self.initialization_lock = threading.Lock()
        
        # Performance tracking
        self.request_count = 0
        self.last_gc = time.time()
        
        logger.info(f"🤖 NLP Processor initialized")
        logger.info(f"   📊 Target models: {self.config.spacy_model}, {self.config.sentence_transformer_model}")
        logger.info(f"   💾 Memory limit: {self.config.memory_limit_gb}GB")
        logger.info(f"   ⚡ Workers: {self.config.max_workers}")
        
        self._initialized = True
    
    async def initialize(self) -> bool:
        """Initialize NLP models with warmup and fallback handling"""
        if self.models_loaded and self.warmup_completed:
            return True
            
        with self.initialization_lock:
            if self.models_loaded and self.warmup_completed:
                return True
                
            try:
                start_time = time.time()
                logger.info("🚀 Initializing NLP Processor models...")
                
                # Load spaCy model with fallbacks
                spacy_success = await self._load_spacy_model()
                
                # Load sentence transformer model
                transformer_success = await self._load_sentence_transformer()
                
                if spacy_success or transformer_success:
                    self.models_loaded = True
                    
                    # Perform model warmup if enabled
                    if self.config.enable_model_warmup:
                        await self._warmup_models()
                        self.warmup_completed = True
                    
                    init_time = time.time() - start_time
                    self.metrics.model_load_time = init_time
                    
                    logger.info(f"✅ NLP Processor initialized in {init_time:.2f}s")
                    logger.info(f"   🔤 spaCy model: {'✅' if spacy_success else '❌'}")
                    logger.info(f"   🌐 Sentence transformer: {'✅' if transformer_success else '❌'}")
                    
                    return True
                else:
                    logger.error("❌ Failed to load any NLP models")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ NLP Processor initialization failed: {e}")
                return False
    
    async def _load_spacy_model(self) -> bool:
        """Load spaCy model with fallback options"""
        try:
            import spacy
            
            # Try primary model first
            models_to_try = [self.config.spacy_model] + self.config.spacy_fallback_models
            
            for model_name in models_to_try:
                try:
                    logger.info(f"📚 Loading spaCy model: {model_name}")
                    
                    # Load model in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    self.spacy_nlp = await loop.run_in_executor(
                        self.thread_pool,
                        spacy.load,
                        model_name
                    )
                    
                    # Configure model for performance
                    if hasattr(self.spacy_nlp, 'max_length'):
                        self.spacy_nlp.max_length = self.config.max_text_length
                    
                    # Disable unused components for memory efficiency
                    disabled_components = []
                    for component in ["lemmatizer"]:  # Keep most components for comprehensive analysis
                        if self.spacy_nlp.has_pipe(component):
                            disabled_components.append(component)
                    
                    if disabled_components:
                        logger.debug(f"Disabled spaCy components for efficiency: {disabled_components}")
                    
                    logger.info(f"✅ spaCy model loaded: {model_name}")
                    return True
                    
                except OSError as e:
                    logger.warning(f"⚠️ Failed to load {model_name}: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Error loading {model_name}: {e}")
                    continue
            
            logger.error("❌ Failed to load any spaCy model")
            return False
            
        except ImportError as e:
            logger.error(f"❌ spaCy not available: {e}")
            logger.info("💡 Install with: pip install spacy")
            logger.info("💡 Download model with: python -m spacy download en_core_web_lg")
            return False
    
    async def _load_sentence_transformer(self) -> bool:
        """Load sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            logger.info(f"🌐 Loading sentence transformer: {self.config.sentence_transformer_model}")
            
            # Load model in thread pool
            loop = asyncio.get_event_loop()
            self.sentence_model = await loop.run_in_executor(
                self.thread_pool,
                SentenceTransformer,
                self.config.sentence_transformer_model
            )
            
            logger.info(f"✅ Sentence transformer loaded: {self.config.sentence_transformer_model}")
            return True
            
        except ImportError as e:
            logger.error(f"❌ sentence-transformers not available: {e}")
            logger.info("💡 Install with: pip install sentence-transformers")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to load sentence transformer: {e}")
            return False
    
    async def _warmup_models(self):
        """Warm up models with sample texts for faster inference"""
        try:
            logger.info("🔥 Warming up NLP models...")
            
            warmup_texts = [
                "This is a sample text for warming up the NLP models.",
                "Machine learning models perform better after warmup processing.",
                "Natural language processing requires computational resources.",
            ]
            
            # Warmup spaCy model
            if self.spacy_nlp:
                for text in warmup_texts:
                    await asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        lambda t: self.spacy_nlp(t),
                        text
                    )
            
            # Warmup sentence transformer
            if self.sentence_model:
                await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool,
                    lambda texts: self.sentence_model.encode(texts),
                    warmup_texts
                )
            
            logger.info("✅ Model warmup completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Model warmup failed: {e}")
    
    @ultra_cache("nlp_spacy", ttl=86400, include_args=True)  # 24 hours cache
    async def process_text_spacy(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Process text using spaCy for comprehensive linguistic analysis.
        
        Args:
            text: Input text to process
            
        Returns:
            Dictionary with linguistic analysis results
        """
        if not self.spacy_nlp:
            logger.warning("🔤 spaCy model not available")
            return None
        
        if len(text) < self.config.min_text_length:
            logger.debug(f"⚠️ Text too short: {len(text)} chars")
            return None
        
        try:
            start_time = time.time()
            
            # Process text in thread pool
            loop = asyncio.get_event_loop()
            doc = await loop.run_in_executor(
                self.thread_pool,
                self.spacy_nlp,
                text[:self.config.max_text_length]
            )
            
            # Extract comprehensive linguistic features
            result = {
                'tokens': [
                    {
                        'text': token.text,
                        'lemma': token.lemma_,
                        'pos': token.pos_,
                        'tag': token.tag_,
                        'dep': token.dep_,
                        'is_alpha': token.is_alpha,
                        'is_stop': token.is_stop,
                        'is_punct': token.is_punct,
                        'sentiment': getattr(token, 'sentiment', 0.0) if hasattr(token, 'sentiment') else None
                    }
                    for token in doc if not token.is_space
                ],
                'entities': [
                    {
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'description': spacy.explain(ent.label_) if hasattr(spacy, 'explain') else ent.label_
                    }
                    for ent in doc.ents
                ],
                'sentences': [
                    {
                        'text': sent.text,
                        'start': sent.start_char,
                        'end': sent.end_char
                    }
                    for sent in doc.sents
                ],
                'noun_phrases': [
                    {
                        'text': chunk.text,
                        'root': chunk.root.text,
                        'start': chunk.start_char,
                        'end': chunk.end_char
                    }
                    for chunk in doc.noun_chunks
                ],
                'language': doc.lang_,
                'text_length': len(text),
                'token_count': len([token for token in doc if not token.is_space]),
                'sentence_count': len(list(doc.sents)),
                'entity_count': len(doc.ents),
                'processing_time': time.time() - start_time
            }
            
            # Record metrics
            self.metrics.record_request(result['processing_time'], True, False)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ spaCy processing failed: {e}")
            self.metrics.record_request(0, False, False)
            return None
    
    async def compute_embeddings(self, texts: Union[str, List[str]], use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Compute semantic embeddings using sentence-transformers.
        
        Args:
            texts: Single text or list of texts
            use_cache: Whether to use embedding cache
            
        Returns:
            NumPy array of embeddings
        """
        if not self.sentence_model:
            logger.warning("🌐 Sentence transformer model not available")
            return None
        
        # Normalize input
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts or not any(len(text.strip()) >= self.config.min_text_length for text in texts):
            logger.debug("⚠️ No valid texts for embedding computation")
            return None
        
        # Filter and truncate texts
        valid_texts = [
            text[:self.config.max_text_length] 
            for text in texts 
            if len(text.strip()) >= self.config.min_text_length
        ]
        
        if not valid_texts:
            return None
        
        try:
            start_time = time.time()
            embeddings_list = []
            cache_hits = 0
            cache_misses = 0
            
            if use_cache and self.config.enable_embedding_cache:
                # Check cache for each text
                uncached_texts = []
                cached_embeddings = {}
                
                for i, text in enumerate(valid_texts):
                    cache_key = self._generate_embedding_cache_key(text)
                    cached_embedding = self.cache_manager.get("embeddings", cache_key)
                    
                    if cached_embedding is not None:
                        cached_embeddings[i] = cached_embedding
                        cache_hits += 1
                    else:
                        uncached_texts.append((i, text))
                        cache_misses += 1
                
                # Compute embeddings for uncached texts
                if uncached_texts:
                    texts_to_compute = [text for _, text in uncached_texts]
                    
                    loop = asyncio.get_event_loop()
                    new_embeddings = await loop.run_in_executor(
                        self.thread_pool,
                        lambda texts: self.sentence_model.encode(
                            texts,
                            batch_size=min(self.config.batch_size, len(texts)),
                            show_progress_bar=False,
                            convert_to_numpy=True
                        ),
                        texts_to_compute
                    )
                    
                    # Cache new embeddings
                    for (orig_idx, text), embedding in zip(uncached_texts, new_embeddings):
                        cache_key = self._generate_embedding_cache_key(text)
                        self.cache_manager.set(
                            "embeddings",
                            cache_key,
                            embedding.tolist(),  # Store as list for JSON serialization
                            ttl=self.config.cache_ttl_hours * 3600
                        )
                        cached_embeddings[orig_idx] = embedding.tolist()
                
                # Reconstruct embeddings in original order
                for i in range(len(valid_texts)):
                    embeddings_list.append(np.array(cached_embeddings[i]))
                    
            else:
                # Direct computation without caching
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    self.thread_pool,
                    lambda texts: self.sentence_model.encode(
                        texts,
                        batch_size=min(self.config.batch_size, len(texts)),
                        show_progress_bar=False,
                        convert_to_numpy=True
                    ),
                    valid_texts
                )
                embeddings_list = list(embeddings)
                cache_misses = len(valid_texts)
            
            result = np.array(embeddings_list)
            processing_time = time.time() - start_time
            
            # Record metrics
            self.metrics.record_request(processing_time, True, cache_hits > 0)
            
            logger.debug(f"🌐 Computed embeddings: {result.shape}, cache hits: {cache_hits}, misses: {cache_misses}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Embedding computation failed: {e}")
            self.metrics.record_request(0, False, False)
            return None
    
    async def compute_similarity(self, text1: str, text2: str) -> Optional[float]:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            embeddings = await self.compute_embeddings([text1, text2])
            
            if embeddings is None or len(embeddings) != 2:
                return None
            
            # Compute cosine similarity
            embedding1, embedding2 = embeddings
            
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure similarity is in [0, 1] range
            similarity = (similarity + 1) / 2
            
            return float(np.clip(similarity, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"❌ Similarity computation failed: {e}")
            return None
    
    async def semantic_search(self, query: str, corpus: List[str], top_k: int = 5) -> List[Tuple[int, str, float]]:
        """
        Perform semantic search in a corpus of texts.
        
        Args:
            query: Search query
            corpus: List of texts to search in
            top_k: Number of top results to return
            
        Returns:
            List of (index, text, similarity_score) tuples
        """
        if not corpus:
            return []
        
        try:
            # Compute embeddings for query and corpus
            all_texts = [query] + corpus
            embeddings = await self.compute_embeddings(all_texts)
            
            if embeddings is None or len(embeddings) != len(all_texts):
                return []
            
            query_embedding = embeddings[0]
            corpus_embeddings = embeddings[1:]
            
            # Compute similarities
            similarities = []
            for i, corpus_embedding in enumerate(corpus_embeddings):
                dot_product = np.dot(query_embedding, corpus_embedding)
                norm_query = np.linalg.norm(query_embedding)
                norm_corpus = np.linalg.norm(corpus_embedding)
                
                if norm_query == 0 or norm_corpus == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product / (norm_query * norm_corpus)
                    similarity = (similarity + 1) / 2  # Normalize to [0, 1]
                
                similarities.append((i, corpus[i], float(np.clip(similarity, 0.0, 1.0))))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[2], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {e}")
            return []
    
    async def batch_process_texts(self, texts: List[str], include_spacy: bool = True, 
                                include_embeddings: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple texts in batch for efficiency.
        
        Args:
            texts: List of texts to process
            include_spacy: Whether to include spaCy analysis
            include_embeddings: Whether to include embeddings
            
        Returns:
            List of processing results
        """
        if not texts:
            return []
        
        try:
            start_time = time.time()
            results = []
            
            # Process in batches to manage memory
            batch_size = min(self.config.batch_size, len(texts))
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_results = []
                
                # Process each text in the batch
                for text in batch_texts:
                    text_result = {'text': text, 'index': i + len(batch_results)}
                    
                    # spaCy analysis
                    if include_spacy:
                        spacy_result = await self.process_text_spacy(text)
                        text_result['spacy'] = spacy_result
                    
                    batch_results.append(text_result)
                
                # Compute embeddings for the entire batch
                if include_embeddings:
                    batch_embeddings = await self.compute_embeddings(batch_texts)
                    if batch_embeddings is not None:
                        for j, embedding in enumerate(batch_embeddings):
                            if j < len(batch_results):
                                batch_results[j]['embedding'] = embedding.tolist()
                
                results.extend(batch_results)
                
                # Check processing time limit
                if time.time() - start_time > self.config.max_batch_processing_time:
                    logger.warning(f"⏰ Batch processing time limit reached, processed {len(results)}/{len(texts)}")
                    break
            
            processing_time = time.time() - start_time
            logger.info(f"📊 Batch processed {len(results)} texts in {processing_time:.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            return []
    
    def _generate_embedding_cache_key(self, text: str) -> str:
        """Generate cache key for text embedding"""
        # Use hash of text for consistent cache keys
        text_hash = hashlib.blake2b(text.encode('utf-8'), digest_size=16).hexdigest()
        return f"{self.config.sentence_transformer_model}_{text_hash}"
    
    def _check_memory_usage(self):
        """Check memory usage and trigger cleanup if needed"""
        memory_info = psutil.virtual_memory()
        memory_gb = memory_info.used / (1024 ** 3)
        
        self.metrics.memory_usage_mb = psutil.Process().memory_info().rss / 1024 / 1024
        
        if memory_gb > self.config.model_unload_threshold_gb:
            logger.warning(f"⚠️ High memory usage: {memory_gb:.1f}GB")
            # Could implement model unloading logic here if needed
            
        if memory_gb > self.config.memory_limit_gb:
            logger.error(f"❌ Memory limit exceeded: {memory_gb:.1f}GB > {self.config.memory_limit_gb}GB")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        self._check_memory_usage()
        
        return {
            'models': {
                'spacy_loaded': self.spacy_nlp is not None,
                'sentence_transformer_loaded': self.sentence_model is not None,
                'models_warmed_up': self.warmup_completed,
                'spacy_model_name': self.config.spacy_model if self.spacy_nlp else None,
                'transformer_model_name': self.config.sentence_transformer_model if self.sentence_model else None
            },
            'performance': {
                'total_requests': self.metrics.total_requests,
                'success_rate': self.metrics.get_success_rate(),
                'cache_hit_rate': self.metrics.get_cache_hit_rate(),
                'avg_processing_time': self.metrics.avg_processing_time,
                'total_processing_time': self.metrics.total_processing_time,
                'model_load_time': self.metrics.model_load_time
            },
            'resources': {
                'memory_usage_mb': self.metrics.memory_usage_mb,
                'memory_limit_gb': self.config.memory_limit_gb,
                'thread_pool_workers': self.config.max_workers,
                'cache_enabled': self.config.enable_embedding_cache
            },
            'configuration': {
                'batch_size': self.config.batch_size,
                'max_text_length': self.config.max_text_length,
                'embedding_dimensions': self.config.embedding_dimensions,
                'cache_ttl_hours': self.config.cache_ttl_hours
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Basic model availability
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'models_loaded': self.models_loaded,
                'warmup_completed': self.warmup_completed,
                'components': {
                    'spacy': self.spacy_nlp is not None,
                    'sentence_transformer': self.sentence_model is not None,
                    'cache_manager': self.cache_manager is not None
                }
            }
            
            # Performance check with sample processing
            if self.models_loaded:
                test_text = "This is a health check test."
                start_time = time.time()
                
                # Test spaCy processing
                if self.spacy_nlp:
                    spacy_result = await self.process_text_spacy(test_text)
                    health_status['spacy_test'] = spacy_result is not None
                
                # Test embedding computation
                if self.sentence_model:
                    embedding_result = await self.compute_embeddings(test_text)
                    health_status['embedding_test'] = embedding_result is not None
                
                health_status['test_processing_time'] = time.time() - start_time
            
            # Memory check
            self._check_memory_usage()
            memory_info = psutil.virtual_memory()
            health_status['memory_status'] = {
                'usage_gb': memory_info.used / (1024 ** 3),
                'available_gb': memory_info.available / (1024 ** 3),
                'percentage': memory_info.percent,
                'within_limits': memory_info.used / (1024 ** 3) < self.config.memory_limit_gb
            }
            
            # Overall health determination
            if not self.models_loaded:
                health_status['status'] = 'degraded'
            elif memory_info.used / (1024 ** 3) > self.config.memory_limit_gb:
                health_status['status'] = 'warning'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Gracefully shutdown the NLP processor"""
        try:
            logger.info("🛑 Shutting down NLP Processor...")
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear model references to free memory
            self.spacy_nlp = None
            self.sentence_model = None
            self.models_loaded = False
            self.warmup_completed = False
            
            logger.info("✅ NLP Processor shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during NLP Processor shutdown: {e}")


# Global instance
_nlp_processor_instance = None
_nlp_processor_lock = threading.Lock()

def get_nlp_processor(config: Optional[NLPConfig] = None) -> NLPProcessor:
    """Get the global NLP Processor instance"""
    global _nlp_processor_instance
    
    if _nlp_processor_instance is None:
        with _nlp_processor_lock:
            if _nlp_processor_instance is None:
                _nlp_processor_instance = NLPProcessor(config)
    
    return _nlp_processor_instance


# Convenience functions
async def quick_nlp_analysis(text: str) -> Dict[str, Any]:
    """Quick NLP analysis with both spaCy and embeddings"""
    processor = get_nlp_processor()
    
    if not await processor.initialize():
        return {'error': 'NLP Processor initialization failed'}
    
    try:
        # Get spaCy analysis
        spacy_result = await processor.process_text_spacy(text)
        
        # Get embedding
        embedding = await processor.compute_embeddings(text)
        
        return {
            'text': text,
            'spacy_analysis': spacy_result,
            'embedding': embedding.tolist() if embedding is not None else None,
            'embedding_shape': embedding.shape if embedding is not None else None,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ Quick NLP analysis failed: {e}")
        return {'error': str(e), 'success': False}


async def compute_text_similarity(text1: str, text2: str) -> Dict[str, Any]:
    """Compute similarity between two texts"""
    processor = get_nlp_processor()
    
    if not await processor.initialize():
        return {'error': 'NLP Processor initialization failed'}
    
    try:
        similarity = await processor.compute_similarity(text1, text2)
        
        return {
            'text1': text1,
            'text2': text2,
            'similarity': similarity,
            'highly_similar': similarity > processor.config.similarity_threshold if similarity else False,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ Text similarity computation failed: {e}")
        return {'error': str(e), 'success': False}