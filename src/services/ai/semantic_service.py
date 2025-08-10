"""
Semantic Service - Advanced semantic analysis using sentence-transformers

Provides semantic understanding and content analysis including:
- Text embeddings and similarity computation
- Content clustering and topic modeling
- Semantic search capabilities
- Content gap analysis
- Competitor content comparison

Optimized for content strategy and SEO optimization workflows.
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import time
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import json

class SemanticService:
    """
    sentence-transformers based semantic analysis service.
    
    Features:
    - Efficient text embedding generation
    - Semantic similarity computation
    - Content clustering and topic discovery
    - Cross-content semantic analysis
    - Memory-optimized batch processing
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.model_name = "all-MiniLM-L6-v2"  # 80MB, fast and efficient
        self.initialized = False
        
        # Configuration optimized for 8GB RAM constraint
        self.config = {
            'batch_size': 16,  # Smaller batches for memory efficiency
            'max_sequence_length': 512,
            'embedding_dim': 384,  # MiniLM dimension
            'similarity_threshold': 0.7,
            'clustering_min_samples': 3,
            'max_clusters': 10
        }
        
        # Embedding cache for performance
        self.embedding_cache = {}
        self.cache_hits = 0
        self.total_requests = 0
    
    async def initialize(self):
        """Initialize sentence-transformers model with error handling."""
        if self.initialized:
            return True
        
        try:
            from sentence_transformers import SentenceTransformer
            
            self.logger.info(f"Loading sentence-transformers model: {self.model_name}")
            
            # Load model with optimizations
            self.model = SentenceTransformer(self.model_name)
            
            # Set maximum sequence length to optimize memory
            self.model.max_seq_length = self.config['max_sequence_length']
            
            self.logger.info(f"✅ Semantic model loaded (dim: {self.config['embedding_dim']})")
            self.initialized = True
            return True
            
        except ImportError as e:
            self.logger.error(f"sentence-transformers not available: {e}")
            self.logger.info("Install with: pip install sentence-transformers")
            return False
        except Exception as e:
            self.logger.error(f"Semantic service initialization failed: {e}")
            return False
    
    async def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts efficiently.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        if not self.initialized or not self.model:
            self.logger.warning("Semantic service not initialized")
            return np.array([])
        
        try:
            start_time = time.time()
            
            # Filter and preprocess texts
            valid_texts = []
            for text in texts:
                if isinstance(text, str) and text.strip():
                    # Truncate long texts
                    if len(text) > self.config['max_sequence_length'] * 4:
                        text = text[:self.config['max_sequence_length'] * 4]
                    valid_texts.append(text.strip())
            
            if not valid_texts:
                return np.array([])
            
            # Check cache for existing embeddings
            cached_embeddings = []
            texts_to_encode = []
            cache_indices = []
            
            for i, text in enumerate(valid_texts):
                text_hash = self._get_text_hash(text)
                if text_hash in self.embedding_cache:
                    cached_embeddings.append((i, self.embedding_cache[text_hash]))
                    self.cache_hits += 1
                else:
                    texts_to_encode.append(text)
                    cache_indices.append((i, text_hash))
            
            # Encode new texts
            new_embeddings = []
            if texts_to_encode:
                # Process in batches for memory efficiency
                batch_size = self.config['batch_size']
                for i in range(0, len(texts_to_encode), batch_size):
                    batch = texts_to_encode[i:i + batch_size]
                    batch_embeddings = self.model.encode(
                        batch,
                        batch_size=len(batch),
                        show_progress_bar=False,
                        convert_to_numpy=True
                    )
                    new_embeddings.extend(batch_embeddings)
                
                # Cache new embeddings
                for (original_idx, text_hash), embedding in zip(cache_indices, new_embeddings):
                    self.embedding_cache[text_hash] = embedding
            
            # Combine cached and new embeddings
            all_embeddings = np.zeros((len(valid_texts), self.config['embedding_dim']))
            
            # Insert cached embeddings
            for idx, embedding in cached_embeddings:
                all_embeddings[idx] = embedding
            
            # Insert new embeddings
            new_idx = 0
            for original_idx, _ in cache_indices:
                all_embeddings[original_idx] = new_embeddings[new_idx]
                new_idx += 1
            
            self.total_requests += len(valid_texts)
            processing_time = time.time() - start_time
            
            self.logger.debug(f"Encoded {len(valid_texts)} texts in {processing_time:.2f}s "
                            f"(cache hit rate: {self.cache_hits/self.total_requests:.2%})")
            
            return all_embeddings
            
        except Exception as e:
            self.logger.error(f"Batch encoding failed: {e}")
            return np.array([])
    
    async def analyze_batch(self, texts: List[str]) -> Dict[str, Any]:
        """
        Comprehensive semantic analysis of text batch.
        
        Args:
            texts: List of text strings to analyze
            
        Returns:
            Dictionary containing semantic analysis results
        """
        if not self.initialized:
            return {}
        
        try:
            start_time = time.time()
            
            # Generate embeddings
            embeddings = await self.encode_batch(texts)
            if embeddings.size == 0:
                return {}
            
            # Perform various semantic analyses
            analysis_results = {}
            
            # 1. Similarity matrix
            if len(texts) > 1:
                similarity_matrix = cosine_similarity(embeddings)
                analysis_results['similarity_matrix'] = similarity_matrix.tolist()
                analysis_results['similarity_stats'] = self._compute_similarity_stats(similarity_matrix)
            
            # 2. Content clustering
            if len(texts) >= self.config['clustering_min_samples']:
                clusters = await self._perform_clustering(embeddings, texts)
                analysis_results['clusters'] = clusters
            
            # 3. Content diversity metrics
            diversity_metrics = self._compute_diversity_metrics(embeddings)
            analysis_results['diversity'] = diversity_metrics
            
            # 4. Semantic keywords extraction
            if len(texts) > 1:
                semantic_keywords = await self._extract_semantic_keywords(texts, embeddings)
                analysis_results['semantic_keywords'] = semantic_keywords
            
            # 5. Content gaps analysis
            if len(texts) > 2:
                content_gaps = self._identify_content_gaps(embeddings, texts)
                analysis_results['content_gaps'] = content_gaps
            
            processing_time = time.time() - start_time
            analysis_results['processing_time'] = processing_time
            analysis_results['text_count'] = len(texts)
            
            self.logger.debug(f"Semantic analysis completed in {processing_time:.2f}s")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Semantic analysis failed: {e}")
            return {}
    
    async def compare_content_similarity(self, content1: str, content2: str) -> Dict[str, Any]:
        """
        Compare semantic similarity between two pieces of content.
        
        Args:
            content1: First content to compare
            content2: Second content to compare
            
        Returns:
            Similarity analysis results
        """
        try:
            embeddings = await self.encode_batch([content1, content2])
            if embeddings.shape[0] < 2:
                return {}
            
            similarity_score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            return {
                'similarity_score': float(similarity_score),
                'similarity_level': self._get_similarity_level(similarity_score),
                'is_similar': similarity_score > self.config['similarity_threshold'],
                'comparison_timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Content comparison failed: {e}")
            return {}
    
    async def find_similar_content(self, query_text: str, candidate_texts: List[str], 
                                 top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find most similar content pieces to a query text.
        
        Args:
            query_text: Text to find similarities for
            candidate_texts: List of candidate texts to search
            top_k: Number of top results to return
            
        Returns:
            List of similar content with scores
        """
        try:
            # Encode all texts
            all_texts = [query_text] + candidate_texts
            embeddings = await self.encode_batch(all_texts)
            
            if embeddings.shape[0] < 2:
                return []
            
            query_embedding = embeddings[0:1]  # First embedding
            candidate_embeddings = embeddings[1:]  # Rest of embeddings
            
            # Compute similarities
            similarities = cosine_similarity(query_embedding, candidate_embeddings)[0]
            
            # Get top k similar texts
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum threshold
                    results.append({
                        'text': candidate_texts[idx],
                        'similarity_score': float(similarities[idx]),
                        'similarity_level': self._get_similarity_level(similarities[idx]),
                        'index': int(idx)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Similar content search failed: {e}")
            return []
    
    async def _perform_clustering(self, embeddings: np.ndarray, texts: List[str]) -> Dict[str, Any]:
        """Perform K-means clustering on text embeddings."""
        try:
            n_texts = embeddings.shape[0]
            
            # Determine optimal number of clusters
            max_clusters = min(self.config['max_clusters'], n_texts // 2)
            if max_clusters < 2:
                return {}
            
            # Use elbow method for cluster selection (simplified)
            best_k = min(3, max_clusters)  # Default to 3 clusters
            
            # Perform clustering
            kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(embeddings)
            
            # Organize results
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = {
                        'texts': [],
                        'indices': [],
                        'centroid_distance': []
                    }
                
                clusters[label]['texts'].append(texts[i])
                clusters[label]['indices'].append(i)
                
                # Distance to centroid
                distance = np.linalg.norm(embeddings[i] - kmeans.cluster_centers_[label])
                clusters[label]['centroid_distance'].append(float(distance))
            
            # Calculate cluster characteristics
            cluster_stats = {}
            for cluster_id, cluster_data in clusters.items():
                cluster_stats[f"cluster_{cluster_id}"] = {
                    'size': len(cluster_data['texts']),
                    'avg_distance_to_centroid': np.mean(cluster_data['centroid_distance']),
                    'representative_text': cluster_data['texts'][
                        np.argmin(cluster_data['centroid_distance'])
                    ]
                }
            
            return {
                'n_clusters': best_k,
                'cluster_assignments': cluster_labels.tolist(),
                'clusters': clusters,
                'cluster_stats': cluster_stats,
                'inertia': float(kmeans.inertia_)
            }
            
        except Exception as e:
            self.logger.error(f"Clustering failed: {e}")
            return {}
    
    def _compute_similarity_stats(self, similarity_matrix: np.ndarray) -> Dict[str, float]:
        """Compute statistics from similarity matrix."""
        try:
            # Extract upper triangle (excluding diagonal)
            n = similarity_matrix.shape[0]
            upper_triangle = []
            
            for i in range(n):
                for j in range(i + 1, n):
                    upper_triangle.append(similarity_matrix[i][j])
            
            if not upper_triangle:
                return {}
            
            upper_triangle = np.array(upper_triangle)
            
            return {
                'mean_similarity': float(np.mean(upper_triangle)),
                'std_similarity': float(np.std(upper_triangle)),
                'max_similarity': float(np.max(upper_triangle)),
                'min_similarity': float(np.min(upper_triangle)),
                'median_similarity': float(np.median(upper_triangle)),
                'high_similarity_pairs': int(np.sum(upper_triangle > self.config['similarity_threshold']))
            }
            
        except Exception as e:
            self.logger.error(f"Similarity stats computation failed: {e}")
            return {}
    
    def _compute_diversity_metrics(self, embeddings: np.ndarray) -> Dict[str, float]:
        """Compute content diversity metrics."""
        try:
            if embeddings.shape[0] < 2:
                return {}
            
            # Pairwise distances
            similarity_matrix = cosine_similarity(embeddings)
            distance_matrix = 1 - similarity_matrix
            
            # Extract upper triangle
            n = distance_matrix.shape[0]
            distances = []
            
            for i in range(n):
                for j in range(i + 1, n):
                    distances.append(distance_matrix[i][j])
            
            distances = np.array(distances)
            
            return {
                'mean_distance': float(np.mean(distances)),
                'std_distance': float(np.std(distances)),
                'diversity_score': float(np.mean(distances)),  # Higher = more diverse
                'content_spread': float(np.max(distances) - np.min(distances)),
                'diversity_level': self._get_diversity_level(np.mean(distances))
            }
            
        except Exception as e:
            self.logger.error(f"Diversity metrics computation failed: {e}")
            return {}
    
    async def _extract_semantic_keywords(self, texts: List[str], embeddings: np.ndarray) -> List[Dict[str, Any]]:
        """Extract semantically important keywords from content."""
        try:
            # This is a simplified implementation
            # In production, you might want to use more sophisticated methods
            
            # Compute centroid of all embeddings
            centroid = np.mean(embeddings, axis=0)
            
            # Find texts closest to centroid (most representative)
            distances_to_centroid = []
            for embedding in embeddings:
                distance = np.linalg.norm(embedding - centroid)
                distances_to_centroid.append(distance)
            
            # Get indices of most representative texts
            representative_indices = np.argsort(distances_to_centroid)[:3]
            
            keywords = []
            for idx in representative_indices:
                # Extract key phrases from representative texts
                text = texts[idx]
                phrases = self._extract_key_phrases(text)
                
                for phrase in phrases:
                    keywords.append({
                        'phrase': phrase,
                        'source_text_index': int(idx),
                        'representativeness_score': 1.0 - (distances_to_centroid[idx] / np.max(distances_to_centroid))
                    })
            
            # Remove duplicates and sort by score
            unique_keywords = {}
            for kw in keywords:
                phrase = kw['phrase'].lower()
                if phrase not in unique_keywords or kw['representativeness_score'] > unique_keywords[phrase]['representativeness_score']:
                    unique_keywords[phrase] = kw
            
            return sorted(unique_keywords.values(), 
                         key=lambda x: x['representativeness_score'], 
                         reverse=True)[:10]
            
        except Exception as e:
            self.logger.error(f"Semantic keyword extraction failed: {e}")
            return []
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text (simple implementation)."""
        try:
            # Simple n-gram extraction
            words = text.lower().split()
            phrases = []
            
            # Extract 2-3 word phrases
            for i in range(len(words) - 1):
                if len(words[i]) > 2 and len(words[i + 1]) > 2:
                    phrase = f"{words[i]} {words[i + 1]}"
                    if len(phrase) > 5:  # Minimum phrase length
                        phrases.append(phrase)
            
            # Extract 3-word phrases
            for i in range(len(words) - 2):
                if all(len(word) > 2 for word in words[i:i + 3]):
                    phrase = " ".join(words[i:i + 3])
                    if len(phrase) > 8:
                        phrases.append(phrase)
            
            return list(set(phrases))[:5]  # Return unique phrases
            
        except Exception as e:
            return []
    
    def _identify_content_gaps(self, embeddings: np.ndarray, texts: List[str]) -> Dict[str, Any]:
        """Identify potential content gaps based on semantic analysis."""
        try:
            # Compute pairwise similarities
            similarity_matrix = cosine_similarity(embeddings)
            
            # Find texts with low similarity to all others (potential unique content)
            unique_content = []
            gap_indicators = []
            
            for i, text in enumerate(texts):
                # Get similarities to all other texts
                similarities = similarity_matrix[i]
                similarities = np.delete(similarities, i)  # Remove self-similarity
                
                avg_similarity = np.mean(similarities)
                max_similarity = np.max(similarities)
                
                if avg_similarity < 0.3:  # Low average similarity
                    unique_content.append({
                        'text': text,
                        'index': i,
                        'avg_similarity': float(avg_similarity),
                        'uniqueness_score': 1.0 - avg_similarity
                    })
                
                if max_similarity < 0.5:  # No highly similar content
                    gap_indicators.append({
                        'text': text,
                        'index': i,
                        'max_similarity': float(max_similarity),
                        'isolation_score': 1.0 - max_similarity
                    })
            
            return {
                'unique_content': sorted(unique_content, 
                                       key=lambda x: x['uniqueness_score'], 
                                       reverse=True)[:5],
                'content_gaps': sorted(gap_indicators,
                                     key=lambda x: x['isolation_score'],
                                     reverse=True)[:5],
                'gap_analysis_summary': {
                    'total_unique_pieces': len(unique_content),
                    'potential_gaps': len(gap_indicators),
                    'content_homogeneity': float(np.mean(similarity_matrix))
                }
            }
            
        except Exception as e:
            self.logger.error(f"Content gap analysis failed: {e}")
            return {}
    
    def _get_text_hash(self, text: str) -> str:
        """Generate hash for text caching."""
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_similarity_level(self, score: float) -> str:
        """Convert similarity score to descriptive level."""
        if score > 0.9:
            return "Very High"
        elif score > 0.7:
            return "High"
        elif score > 0.5:
            return "Moderate"
        elif score > 0.3:
            return "Low"
        else:
            return "Very Low"
    
    def _get_diversity_level(self, score: float) -> str:
        """Convert diversity score to descriptive level."""
        if score > 0.7:
            return "Very Diverse"
        elif score > 0.5:
            return "Diverse"
        elif score > 0.3:
            return "Moderately Diverse"
        elif score > 0.1:
            return "Similar"
        else:
            return "Very Similar"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get caching performance statistics."""
        return {
            'cache_size': len(self.embedding_cache),
            'total_requests': self.total_requests,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': self.cache_hits / max(self.total_requests, 1),
            'memory_usage_mb': len(self.embedding_cache) * self.config['embedding_dim'] * 4 / (1024 * 1024)  # Rough estimate
        }
    
    def clear_cache(self):
        """Clear embedding cache to free memory."""
        self.embedding_cache.clear()
        self.cache_hits = 0
        self.total_requests = 0
        self.logger.info("Semantic service cache cleared")