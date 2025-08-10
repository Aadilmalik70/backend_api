"""
NLP Enhanced Service - Integration wrapper for the comprehensive NLP processor

This service provides a bridge between the new NLP processor and the existing AI infrastructure,
ensuring seamless integration with the AI manager and other services while maintaining 
backward compatibility.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Import the new NLP processor
from ..nlp_processor import (
    NLPProcessor,
    NLPConfig, 
    get_nlp_processor,
    ProcessingMetrics
)

logger = logging.getLogger(__name__)

class NLPEnhancedService:
    """
    Enhanced NLP service that integrates the comprehensive NLP processor
    with the existing AI infrastructure while maintaining compatibility.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced NLP service.
        
        Args:
            config: Configuration dictionary for NLP processor
        """
        self.logger = logging.getLogger(__name__)
        
        # Create NLP processor configuration
        processor_config = NLPConfig()
        if config:
            # Map configuration parameters
            if 'spacy_model' in config:
                processor_config.spacy_model = config['spacy_model']
            if 'sentence_transformer_model' in config:
                processor_config.sentence_transformer_model = config['sentence_transformer_model']
            if 'enable_caching' in config:
                processor_config.enable_embedding_cache = config['enable_caching']
                processor_config.enable_model_warmup = config['enable_caching']
            if 'max_workers' in config:
                processor_config.max_workers = config['max_workers']
            if 'batch_size' in config:
                processor_config.batch_size = config['batch_size']
        
        # Get the NLP processor instance
        self.processor = get_nlp_processor(processor_config)
        self.initialized = False
        
        self.logger.info("🔤 NLP Enhanced Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize the NLP processor"""
        if self.initialized:
            return True
        
        try:
            success = await self.processor.initialize()
            self.initialized = success
            
            if success:
                self.logger.info("✅ NLP Enhanced Service ready")
            else:
                self.logger.error("❌ NLP Enhanced Service initialization failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ NLP Enhanced Service initialization error: {e}")
            return False
    
    async def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Process a batch of texts - maintains compatibility with existing AI infrastructure.
        
        Args:
            texts: List of texts to process
            
        Returns:
            List of processing results compatible with existing format
        """
        if not self.initialized:
            await self.initialize()
        
        if not texts:
            return []
        
        try:
            # Use the comprehensive batch processing
            results = await self.processor.batch_process_texts(
                texts, 
                include_spacy=True, 
                include_embeddings=True
            )
            
            # Convert to compatible format
            compatible_results = []
            for result in results:
                compatible_result = {
                    'text': result.get('text', ''),
                    'success': True,
                    'processing_time': 0,
                    'analysis': {}
                }
                
                # Add spaCy analysis in compatible format
                spacy_data = result.get('spacy')
                if spacy_data:
                    compatible_result['analysis'] = {
                        'entities': spacy_data.get('entities', []),
                        'tokens': spacy_data.get('tokens', []),
                        'sentences': spacy_data.get('sentences', []),
                        'noun_phrases': spacy_data.get('noun_phrases', []),
                        'language': spacy_data.get('language', 'en'),
                        'readability': {
                            'token_count': spacy_data.get('token_count', 0),
                            'sentence_count': spacy_data.get('sentence_count', 0),
                            'avg_sentence_length': (
                                spacy_data.get('token_count', 0) / 
                                max(spacy_data.get('sentence_count', 1), 1)
                            )
                        },
                        'seo_elements': {
                            'questions': [],  # Could be enhanced with question detection
                            'lists': [],
                            'headings': []
                        }
                    }
                    compatible_result['processing_time'] = spacy_data.get('processing_time', 0)
                
                # Add embedding data
                if result.get('embedding'):
                    compatible_result['embedding'] = result['embedding']
                    compatible_result['embedding_dimensions'] = len(result['embedding'])
                
                compatible_results.append(compatible_result)
            
            return compatible_results
            
        except Exception as e:
            self.logger.error(f"❌ Batch processing failed: {e}")
            return [{'text': text, 'success': False, 'error': str(e)} for text in texts]
    
    async def analyze_content_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze content quality using both spaCy and semantic analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Quality analysis results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get spaCy analysis
            spacy_result = await self.processor.process_text_spacy(text)
            
            # Get embedding for semantic analysis
            embedding = await self.processor.compute_embeddings(text)
            
            if not spacy_result:
                return {'error': 'spaCy processing failed', 'success': False}
            
            # Calculate quality metrics
            quality_score = 0
            factors = []
            
            # Text length factor
            text_length = len(text)
            if text_length >= 300:
                quality_score += 25
                factors.append("Good content length")
            elif text_length >= 100:
                quality_score += 15
                factors.append("Adequate content length")
            else:
                factors.append("Content too short")
            
            # Entity richness
            entity_count = spacy_result.get('entity_count', 0)
            if entity_count >= 5:
                quality_score += 20
                factors.append("Rich entity content")
            elif entity_count >= 2:
                quality_score += 10
                factors.append("Some entity content")
            else:
                factors.append("Limited entity content")
            
            # Sentence structure
            sentence_count = spacy_result.get('sentence_count', 0)
            token_count = spacy_result.get('token_count', 0)
            
            if sentence_count > 0:
                avg_sentence_length = token_count / sentence_count
                if 10 <= avg_sentence_length <= 25:
                    quality_score += 20
                    factors.append("Good sentence structure")
                elif 5 <= avg_sentence_length <= 35:
                    quality_score += 10
                    factors.append("Acceptable sentence structure")
                else:
                    factors.append("Poor sentence structure")
            
            # Vocabulary diversity (unique words / total words)
            tokens = spacy_result.get('tokens', [])
            if tokens:
                unique_words = len(set(token['lemma'].lower() for token in tokens if token['is_alpha']))
                total_words = len([token for token in tokens if token['is_alpha']])
                
                if total_words > 0:
                    diversity_ratio = unique_words / total_words
                    if diversity_ratio >= 0.7:
                        quality_score += 15
                        factors.append("High vocabulary diversity")
                    elif diversity_ratio >= 0.5:
                        quality_score += 10
                        factors.append("Good vocabulary diversity")
                    else:
                        factors.append("Limited vocabulary diversity")
            
            # Readability (simplified)
            if sentence_count > 0 and token_count > 0:
                avg_sentence_length = token_count / sentence_count
                if avg_sentence_length <= 20:
                    quality_score += 20
                    factors.append("Good readability")
                elif avg_sentence_length <= 30:
                    quality_score += 10
                    factors.append("Acceptable readability")
                else:
                    factors.append("Poor readability")
            
            return {
                'success': True,
                'quality_score': min(quality_score, 100),  # Cap at 100
                'quality_factors': factors,
                'metrics': {
                    'text_length': text_length,
                    'sentence_count': sentence_count,
                    'token_count': token_count,
                    'entity_count': entity_count,
                    'avg_sentence_length': avg_sentence_length if sentence_count > 0 else 0
                },
                'has_embedding': embedding is not None,
                'processing_time': spacy_result.get('processing_time', 0)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Content quality analysis failed: {e}")
            return {'error': str(e), 'success': False}
    
    async def find_similar_content(self, query_text: str, content_corpus: List[str], 
                                 top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find similar content using semantic search.
        
        Args:
            query_text: Text to search for
            content_corpus: List of content to search in
            top_k: Number of results to return
            
        Returns:
            List of similar content with scores
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            results = await self.processor.semantic_search(query_text, content_corpus, top_k)
            
            # Convert to compatible format
            similar_content = []
            for idx, text, score in results:
                similar_content.append({
                    'index': idx,
                    'text': text,
                    'similarity_score': score,
                    'highly_similar': score > self.processor.config.similarity_threshold
                })
            
            return {
                'success': True,
                'query': query_text,
                'results': similar_content,
                'total_searched': len(content_corpus)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Similar content search failed: {e}")
            return {'error': str(e), 'success': False}
    
    async def compute_content_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        """
        Compute embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Embedding results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            embeddings = await self.processor.compute_embeddings(texts)
            
            if embeddings is not None:
                return {
                    'success': True,
                    'embeddings': embeddings.tolist(),
                    'shape': embeddings.shape,
                    'dimensions': embeddings.shape[1] if len(embeddings.shape) > 1 else embeddings.shape[0],
                    'count': len(texts)
                }
            else:
                return {'error': 'Embedding computation failed', 'success': False}
                
        except Exception as e:
            self.logger.error(f"❌ Embedding computation failed: {e}")
            return {'error': str(e), 'success': False}
    
    async def analyze_text_similarity(self, text1: str, text2: str) -> Dict[str, Any]:
        """
        Analyze similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity analysis results
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            similarity = await self.processor.compute_similarity(text1, text2)
            
            if similarity is not None:
                return {
                    'success': True,
                    'similarity_score': similarity,
                    'highly_similar': similarity > self.processor.config.similarity_threshold,
                    'similarity_level': self._get_similarity_level(similarity),
                    'text1_preview': text1[:100] + "..." if len(text1) > 100 else text1,
                    'text2_preview': text2[:100] + "..." if len(text2) > 100 else text2
                }
            else:
                return {'error': 'Similarity computation failed', 'success': False}
                
        except Exception as e:
            self.logger.error(f"❌ Similarity analysis failed: {e}")
            return {'error': str(e), 'success': False}
    
    def _get_similarity_level(self, score: float) -> str:
        """Convert similarity score to descriptive level"""
        if score >= 0.8:
            return "Very High"
        elif score >= 0.6:
            return "High"
        elif score >= 0.4:
            return "Moderate"
        elif score >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and metrics"""
        try:
            if not self.initialized:
                return {
                    'status': 'not_initialized',
                    'initialized': False
                }
            
            # Get processor metrics
            metrics = self.processor.get_performance_metrics()
            
            return {
                'status': 'operational' if self.initialized else 'not_initialized',
                'initialized': self.initialized,
                'models': metrics['models'],
                'performance': metrics['performance'],
                'resources': metrics['resources'],
                'service_type': 'nlp_enhanced',
                'version': '1.0.0',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Status check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            if not self.initialized:
                await self.initialize()
            
            if self.initialized:
                health = await self.processor.health_check()
                return {
                    'service': 'nlp_enhanced',
                    'status': health['status'],
                    'details': health,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'service': 'nlp_enhanced',
                    'status': 'unhealthy',
                    'error': 'Service not initialized',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return {
                'service': 'nlp_enhanced',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the service"""
        try:
            if self.processor:
                await self.processor.shutdown()
            self.initialized = False
            self.logger.info("✅ NLP Enhanced Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Shutdown error: {e}")


# Global instance for compatibility
_nlp_enhanced_service = None

def get_nlp_enhanced_service(config: Optional[Dict[str, Any]] = None) -> NLPEnhancedService:
    """Get the global NLP Enhanced Service instance"""
    global _nlp_enhanced_service
    
    if _nlp_enhanced_service is None:
        _nlp_enhanced_service = NLPEnhancedService(config)
    
    return _nlp_enhanced_service