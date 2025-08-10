"""
Coherence Scoring System - Advanced Clustering Quality Assessment

Comprehensive coherence scoring system for semantic clustering with >85% accuracy targeting.
Provides multiple validation methods, cross-validation strategies, and advanced quality metrics
for ensuring optimal clustering performance.

Features:
- Multiple coherence calculation methods (silhouette, semantic, statistical)
- Cross-validation and bootstrap validation strategies  
- Parameter optimization for target accuracy achievement
- Advanced semantic coherence with embedding analysis
- Quality assessment reporting and recommendations
- Integration with clustering results validation
- Performance benchmarking and accuracy tracking

Coherence Methods:
- Silhouette Analysis: Cluster separation and cohesion measurement
- Semantic Coherence: Embedding-based semantic similarity within clusters
- Statistical Coherence: Calinski-Harabasz, Davies-Bouldin scores
- Cross-Validation: K-fold validation for robust quality assessment
- Bootstrap Validation: Sampling-based stability analysis

Performance Target: >85% clustering accuracy with comprehensive validation
"""

import asyncio
import logging
import time
import warnings
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict
import random

# Import clustering evaluation metrics with fallback
try:
    from sklearn.metrics import (
        silhouette_score, silhouette_samples, 
        calinski_harabasz_score, davies_bouldin_score,
        adjusted_rand_score, normalized_mutual_info_score,
        homogeneity_score, completeness_score, v_measure_score
    )
    from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
    from sklearn.model_selection import KFold
    from sklearn.preprocessing import normalize
    from sklearn.decomposition import PCA
    from sklearn.cluster import DBSCAN
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Import existing models and services
from .clustering_models import (
    SemanticCluster, ClusteringResult, ClusteringConfig, EmbeddingData,
    CoherenceScore, CoherenceMethod, ClusteringStatus
)
from .timeout_protection import get_timeout_protection

logger = logging.getLogger(__name__)


@dataclass 
class ValidationConfig:
    """Configuration for coherence validation"""
    
    # Target accuracy settings
    target_accuracy: float = 0.85
    min_acceptable_accuracy: float = 0.70
    excellence_threshold: float = 0.90
    
    # Validation methods
    enable_cross_validation: bool = True
    cross_validation_folds: int = 5
    enable_bootstrap_validation: bool = True
    bootstrap_samples: int = 100
    bootstrap_sample_ratio: float = 0.8
    
    # Coherence calculation methods
    coherence_methods: List[str] = field(default_factory=lambda: [
        'silhouette', 'semantic', 'calinski_harabasz', 'davies_bouldin'
    ])
    
    # Quality thresholds
    min_silhouette_score: float = 0.3
    max_davies_bouldin_score: float = 2.0
    min_semantic_coherence: float = 0.4
    max_noise_ratio: float = 0.3
    
    # Performance settings
    max_validation_time: float = 60.0
    enable_parallel_validation: bool = True
    validation_timeout: float = 30.0


@dataclass
class CoherenceReport:
    """Comprehensive coherence assessment report"""
    
    # Overall assessment
    overall_coherence: float = 0.0
    accuracy_grade: str = "F"  # A, B, C, D, F
    meets_target: bool = False
    
    # Individual metric scores
    silhouette_score: float = 0.0
    semantic_coherence: float = 0.0
    calinski_harabasz_score: float = 0.0
    davies_bouldin_score: float = 0.0
    
    # Advanced metrics
    homogeneity_score: float = 0.0
    completeness_score: float = 0.0
    v_measure_score: float = 0.0
    
    # Validation results
    cross_validation_scores: List[float] = field(default_factory=list)
    bootstrap_scores: List[float] = field(default_factory=list)
    stability_score: float = 0.0
    
    # Cluster analysis
    cluster_quality_distribution: Dict[str, int] = field(default_factory=dict)
    problematic_clusters: List[str] = field(default_factory=list)
    high_quality_clusters: List[str] = field(default_factory=list)
    
    # Recommendations
    improvement_recommendations: List[str] = field(default_factory=list)
    parameter_suggestions: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    calculation_time: float = 0.0
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_grade(self) -> str:
        """Calculate letter grade based on coherence score"""
        if self.overall_coherence >= 0.90:
            return "A"
        elif self.overall_coherence >= 0.85:
            return "B"
        elif self.overall_coherence >= 0.75:
            return "C"
        elif self.overall_coherence >= 0.65:
            return "D"
        else:
            return "F"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive report summary"""
        return {
            'overall_assessment': {
                'coherence_score': self.overall_coherence,
                'accuracy_grade': self.get_grade(),
                'meets_target': self.meets_target,
                'stability_score': self.stability_score
            },
            'quality_metrics': {
                'silhouette_score': self.silhouette_score,
                'semantic_coherence': self.semantic_coherence,
                'calinski_harabasz_score': self.calinski_harabasz_score,
                'davies_bouldin_score': self.davies_bouldin_score
            },
            'validation_summary': {
                'cross_validation_mean': np.mean(self.cross_validation_scores) if self.cross_validation_scores else 0.0,
                'cross_validation_std': np.std(self.cross_validation_scores) if self.cross_validation_scores else 0.0,
                'bootstrap_mean': np.mean(self.bootstrap_scores) if self.bootstrap_scores else 0.0,
                'bootstrap_std': np.std(self.bootstrap_scores) if self.bootstrap_scores else 0.0
            },
            'cluster_analysis': {
                'quality_distribution': self.cluster_quality_distribution,
                'problematic_clusters': len(self.problematic_clusters),
                'high_quality_clusters': len(self.high_quality_clusters)
            },
            'recommendations': {
                'improvement_suggestions': self.improvement_recommendations,
                'parameter_suggestions': self.parameter_suggestions
            }
        }


class CoherenceScorer:
    """
    Advanced coherence scoring system with comprehensive validation,
    cross-validation, and quality assessment targeting >85% accuracy.
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        """Initialize coherence scorer"""
        self.config = config or ValidationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Performance management
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.timeout_protection = get_timeout_protection()
        self.scoring_lock = threading.RLock()
        
        # Validation cache
        self.validation_cache = {}
        
        # Performance metrics
        self.metrics = {
            'scoring_operations': 0,
            'successful_scorings': 0,
            'failed_scorings': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0,
            'scores_above_target': 0,
            'validation_operations': 0,
            'cache_hits': 0
        }
        
        # Check dependencies
        if not SKLEARN_AVAILABLE:
            self.logger.warning(
                "scikit-learn not available. Some coherence scoring functionality will be limited."
            )
        
        self.logger.info("Coherence Scorer initialized")
    
    async def score_clustering_result(
        self,
        clustering_result: ClusteringResult,
        embedding_matrix: Optional[np.ndarray] = None,
        true_labels: Optional[np.ndarray] = None
    ) -> CoherenceReport:
        """
        Comprehensive coherence scoring for clustering result
        
        Args:
            clustering_result: The clustering result to evaluate
            embedding_matrix: Original embedding matrix used for clustering
            true_labels: Ground truth labels if available (for supervised metrics)
            
        Returns:
            Comprehensive coherence report with quality assessment
        """
        
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for coherence scoring. "
                "Install with: pip install scikit-learn"
            )
        
        if not clustering_result.embeddings or not clustering_result.clusters:
            return self._create_empty_report("No clustering data provided")
        
        start_time = time.time()
        self.metrics['scoring_operations'] += 1
        
        try:
            self.logger.info(
                f"Starting comprehensive coherence scoring for "
                f"{len(clustering_result.clusters)} clusters"
            )
            
            # Prepare embedding matrix if not provided
            if embedding_matrix is None:
                embedding_matrix = self._extract_embedding_matrix(clustering_result.embeddings)
            
            # Extract cluster labels
            cluster_labels = self._extract_cluster_labels(clustering_result)
            
            # Create coherence report
            report = CoherenceReport(
                validation_timestamp=datetime.utcnow()
            )
            
            # Calculate basic coherence metrics
            await self._calculate_basic_metrics(
                embedding_matrix, cluster_labels, report
            )
            
            # Calculate advanced semantic coherence
            await self._calculate_semantic_coherence(
                embedding_matrix, cluster_labels, clustering_result.clusters, report
            )
            
            # Perform validation if enabled
            if self.config.enable_cross_validation:
                await self._perform_cross_validation(
                    embedding_matrix, clustering_result, report
                )
            
            if self.config.enable_bootstrap_validation:
                await self._perform_bootstrap_validation(
                    embedding_matrix, clustering_result, report
                )
            
            # Analyze cluster quality distribution
            await self._analyze_cluster_quality(
                embedding_matrix, cluster_labels, clustering_result.clusters, report
            )
            
            # Calculate supervised metrics if true labels provided
            if true_labels is not None:
                await self._calculate_supervised_metrics(
                    cluster_labels, true_labels, report
                )
            
            # Calculate overall coherence score
            self._calculate_overall_coherence(report)
            
            # Generate improvement recommendations
            self._generate_recommendations(report, clustering_result)
            
            # Update metrics
            report.calculation_time = time.time() - start_time
            self._update_success_metrics(report)
            
            self.logger.info(
                f"Coherence scoring completed: {report.overall_coherence:.3f} "
                f"(grade: {report.get_grade()}, time: {report.calculation_time:.3f}s)"
            )
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics['failed_scorings'] += 1
            
            self.logger.error(f"Coherence scoring failed: {e}")
            
            return CoherenceReport(
                overall_coherence=0.0,
                accuracy_grade="F",
                meets_target=False,
                calculation_time=execution_time,
                improvement_recommendations=[f"Scoring failed: {str(e)}"]
            )
    
    def _extract_embedding_matrix(self, embeddings: List[EmbeddingData]) -> np.ndarray:
        """Extract embedding matrix from embedding data"""
        vectors = []
        
        for embedding in embeddings:
            if embedding.vector and len(embedding.vector) > 0:
                vector = np.array(embedding.vector)
                if not np.isnan(vector).any() and not np.isinf(vector).any():
                    vectors.append(vector)
        
        if not vectors:
            raise ValueError("No valid embedding vectors found")
        
        matrix = np.vstack(vectors)
        return normalize(matrix, norm='l2')
    
    def _extract_cluster_labels(self, clustering_result: ClusteringResult) -> np.ndarray:
        """Extract cluster labels from clustering result"""
        labels = []
        
        # Create mapping from text to cluster label
        text_to_label = {}
        
        for cluster in clustering_result.clusters:
            for text in cluster.texts:
                text_to_label[text] = cluster.label
        
        # Add noise points
        for noise_text in clustering_result.noise_points:
            text_to_label[noise_text] = -1
        
        # Create label array
        for embedding in clustering_result.embeddings:
            label = text_to_label.get(embedding.text, -1)
            labels.append(label)
        
        return np.array(labels)
    
    async def _calculate_basic_metrics(
        self,
        embedding_matrix: np.ndarray,
        cluster_labels: np.ndarray,
        report: CoherenceReport
    ):
        """Calculate basic coherence metrics"""
        
        try:
            # Silhouette score
            if len(set(cluster_labels)) > 1:
                silhouette_avg = silhouette_score(
                    embedding_matrix, cluster_labels, metric='cosine'
                )
                report.silhouette_score = silhouette_avg
            else:
                report.silhouette_score = 0.0
        except Exception as e:
            self.logger.warning(f"Silhouette score calculation failed: {e}")
            report.silhouette_score = 0.0
        
        try:
            # Calinski-Harabasz score
            if len(set(cluster_labels)) > 1:
                ch_score = calinski_harabasz_score(embedding_matrix, cluster_labels)
                # Normalize to 0-1 range
                report.calinski_harabasz_score = min(ch_score / 1000.0, 1.0)
            else:
                report.calinski_harabasz_score = 0.0
        except Exception as e:
            self.logger.warning(f"Calinski-Harabasz score calculation failed: {e}")
            report.calinski_harabasz_score = 0.0
        
        try:
            # Davies-Bouldin score (lower is better)
            if len(set(cluster_labels)) > 1:
                db_score = davies_bouldin_score(embedding_matrix, cluster_labels)
                # Invert and normalize
                report.davies_bouldin_score = max(0.0, 1.0 - (db_score / 10.0))
            else:
                report.davies_bouldin_score = 0.0
        except Exception as e:
            self.logger.warning(f"Davies-Bouldin score calculation failed: {e}")
            report.davies_bouldin_score = 0.0
    
    async def _calculate_semantic_coherence(
        self,
        embedding_matrix: np.ndarray,
        cluster_labels: np.ndarray,
        clusters: List[SemanticCluster],
        report: CoherenceReport
    ):
        """Calculate advanced semantic coherence metrics"""
        
        try:
            coherence_scores = []
            
            for cluster in clusters:
                if cluster.size < 2:
                    continue
                
                # Get cluster embeddings
                cluster_indices = [
                    i for i, label in enumerate(cluster_labels) 
                    if label == cluster.label
                ]
                
                if len(cluster_indices) < 2:
                    continue
                
                cluster_embeddings = embedding_matrix[cluster_indices]
                
                # Calculate semantic coherence for this cluster
                cluster_coherence = await self._calculate_cluster_semantic_coherence(
                    cluster_embeddings, cluster.texts
                )
                coherence_scores.append(cluster_coherence)
            
            if coherence_scores:
                report.semantic_coherence = np.mean(coherence_scores)
            else:
                report.semantic_coherence = 0.0
                
        except Exception as e:
            self.logger.warning(f"Semantic coherence calculation failed: {e}")
            report.semantic_coherence = 0.0
    
    async def _calculate_cluster_semantic_coherence(
        self,
        cluster_embeddings: np.ndarray,
        cluster_texts: List[str]
    ) -> float:
        """Calculate semantic coherence for a single cluster"""
        
        try:
            if len(cluster_embeddings) < 2:
                return 0.0
            
            # Calculate pairwise cosine similarities
            similarities = cosine_similarity(cluster_embeddings)
            
            # Get mean similarity (excluding diagonal)
            mask = np.ones(similarities.shape, dtype=bool)
            np.fill_diagonal(mask, False)
            mean_similarity = np.mean(similarities[mask])
            
            # Additional semantic analysis based on text content
            text_coherence = self._analyze_text_coherence(cluster_texts)
            
            # Combine embedding similarity with text coherence
            combined_coherence = 0.7 * mean_similarity + 0.3 * text_coherence
            
            return combined_coherence
            
        except Exception as e:
            self.logger.warning(f"Cluster semantic coherence calculation failed: {e}")
            return 0.5  # Default moderate score
    
    def _analyze_text_coherence(self, texts: List[str]) -> float:
        """Analyze text coherence based on content similarity"""
        
        if not texts or len(texts) < 2:
            return 0.0
        
        try:
            # Simple text-based coherence analysis
            all_words = set()
            text_word_sets = []
            
            for text in texts:
                words = set(text.lower().split())
                text_word_sets.append(words)
                all_words.update(words)
            
            if not all_words:
                return 0.0
            
            # Calculate word overlap scores
            overlap_scores = []
            
            for i in range(len(text_word_sets)):
                for j in range(i + 1, len(text_word_sets)):
                    set1, set2 = text_word_sets[i], text_word_sets[j]
                    
                    if len(set1) == 0 or len(set2) == 0:
                        continue
                    
                    # Jaccard similarity
                    intersection = len(set1 & set2)
                    union = len(set1 | set2)
                    
                    if union > 0:
                        overlap_scores.append(intersection / union)
            
            if overlap_scores:
                return np.mean(overlap_scores)
            else:
                return 0.0
                
        except Exception as e:
            self.logger.warning(f"Text coherence analysis failed: {e}")
            return 0.0
    
    async def _perform_cross_validation(
        self,
        embedding_matrix: np.ndarray,
        clustering_result: ClusteringResult,
        report: CoherenceReport
    ):
        """Perform k-fold cross-validation on clustering"""
        
        try:
            if len(embedding_matrix) < self.config.cross_validation_folds:
                report.cross_validation_scores = []
                return
            
            kfold = KFold(
                n_splits=self.config.cross_validation_folds,
                shuffle=True,
                random_state=42
            )
            
            cv_scores = []
            
            for train_idx, test_idx in kfold.split(embedding_matrix):
                try:
                    # Get training embeddings
                    train_embeddings = embedding_matrix[train_idx]
                    
                    # Re-cluster training data
                    if clustering_result.config:
                        cv_labels = await self._re_cluster_for_validation(
                            train_embeddings, clustering_result.config
                        )
                        
                        # Calculate coherence for this fold
                        if len(set(cv_labels)) > 1:
                            cv_score = silhouette_score(
                                train_embeddings, cv_labels, metric='cosine'
                            )
                            cv_scores.append(cv_score)
                    
                except Exception as e:
                    self.logger.warning(f"Cross-validation fold failed: {e}")
                    continue
            
            report.cross_validation_scores = cv_scores
            
        except Exception as e:
            self.logger.warning(f"Cross-validation failed: {e}")
            report.cross_validation_scores = []
    
    async def _perform_bootstrap_validation(
        self,
        embedding_matrix: np.ndarray,
        clustering_result: ClusteringResult,
        report: CoherenceReport
    ):
        """Perform bootstrap validation on clustering"""
        
        try:
            bootstrap_scores = []
            n_samples = len(embedding_matrix)
            sample_size = int(n_samples * self.config.bootstrap_sample_ratio)
            
            for _ in range(self.config.bootstrap_samples):
                try:
                    # Random sample with replacement
                    sample_indices = np.random.choice(
                        n_samples, size=sample_size, replace=True
                    )
                    sample_embeddings = embedding_matrix[sample_indices]
                    
                    # Re-cluster sample
                    if clustering_result.config:
                        sample_labels = await self._re_cluster_for_validation(
                            sample_embeddings, clustering_result.config
                        )
                        
                        # Calculate coherence for this sample
                        if len(set(sample_labels)) > 1:
                            sample_score = silhouette_score(
                                sample_embeddings, sample_labels, metric='cosine'
                            )
                            bootstrap_scores.append(sample_score)
                    
                except Exception as e:
                    self.logger.warning(f"Bootstrap sample failed: {e}")
                    continue
            
            report.bootstrap_scores = bootstrap_scores
            
            # Calculate stability score
            if len(bootstrap_scores) > 1:
                report.stability_score = 1.0 - (np.std(bootstrap_scores) / (np.mean(bootstrap_scores) + 1e-8))
            
        except Exception as e:
            self.logger.warning(f"Bootstrap validation failed: {e}")
            report.bootstrap_scores = []
    
    async def _re_cluster_for_validation(
        self,
        embedding_matrix: np.ndarray,
        config: ClusteringConfig
    ) -> np.ndarray:
        """Re-cluster embeddings for validation purposes"""
        
        try:
            # Simple DBSCAN re-clustering for validation
            dbscan = DBSCAN(
                eps=config.eps,
                min_samples=config.min_samples,
                metric='cosine'
            )
            
            return dbscan.fit_predict(embedding_matrix)
            
        except Exception as e:
            self.logger.warning(f"Re-clustering for validation failed: {e}")
            # Return dummy labels
            return np.zeros(len(embedding_matrix))
    
    async def _analyze_cluster_quality(
        self,
        embedding_matrix: np.ndarray,
        cluster_labels: np.ndarray,
        clusters: List[SemanticCluster],
        report: CoherenceReport
    ):
        """Analyze individual cluster quality"""
        
        try:
            if len(clusters) == 0:
                return
            
            # Calculate per-cluster silhouette scores
            sample_silhouette_values = silhouette_samples(
                embedding_matrix, cluster_labels, metric='cosine'
            )
            
            quality_counts = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
            
            for cluster in clusters:
                cluster_indices = [
                    i for i, label in enumerate(cluster_labels)
                    if label == cluster.label
                ]
                
                if not cluster_indices:
                    continue
                
                cluster_silhouettes = [sample_silhouette_values[i] for i in cluster_indices]
                avg_cluster_silhouette = np.mean(cluster_silhouettes)
                
                # Categorize cluster quality
                if avg_cluster_silhouette >= 0.7:
                    quality = 'excellent'
                    report.high_quality_clusters.append(cluster.cluster_id)
                elif avg_cluster_silhouette >= 0.5:
                    quality = 'good'
                elif avg_cluster_silhouette >= 0.3:
                    quality = 'fair'
                else:
                    quality = 'poor'
                    report.problematic_clusters.append(cluster.cluster_id)
                
                quality_counts[quality] += 1
            
            report.cluster_quality_distribution = quality_counts
            
        except Exception as e:
            self.logger.warning(f"Cluster quality analysis failed: {e}")
            report.cluster_quality_distribution = {}
    
    async def _calculate_supervised_metrics(
        self,
        cluster_labels: np.ndarray,
        true_labels: np.ndarray,
        report: CoherenceReport
    ):
        """Calculate supervised evaluation metrics"""
        
        try:
            # Remove noise points for supervised metrics
            mask = cluster_labels != -1
            filtered_cluster_labels = cluster_labels[mask]
            filtered_true_labels = true_labels[mask]
            
            if len(filtered_cluster_labels) == 0:
                return
            
            # Calculate supervised metrics
            report.homogeneity_score = homogeneity_score(
                filtered_true_labels, filtered_cluster_labels
            )
            report.completeness_score = completeness_score(
                filtered_true_labels, filtered_cluster_labels
            )
            report.v_measure_score = v_measure_score(
                filtered_true_labels, filtered_cluster_labels
            )
            
        except Exception as e:
            self.logger.warning(f"Supervised metrics calculation failed: {e}")
    
    def _calculate_overall_coherence(self, report: CoherenceReport):
        """Calculate overall coherence score from individual metrics"""
        
        # Define weights for different metrics
        weights = {
            'silhouette': 0.3,
            'semantic': 0.25,
            'calinski_harabasz': 0.15,
            'davies_bouldin': 0.1,
            'stability': 0.1,
            'validation': 0.1
        }
        
        # Calculate weighted score
        overall_score = (
            report.silhouette_score * weights['silhouette'] +
            report.semantic_coherence * weights['semantic'] +
            report.calinski_harabasz_score * weights['calinski_harabasz'] +
            report.davies_bouldin_score * weights['davies_bouldin'] +
            report.stability_score * weights['stability']
        )
        
        # Add validation bonus if available
        if report.cross_validation_scores:
            cv_mean = np.mean(report.cross_validation_scores)
            overall_score += cv_mean * weights['validation']
        
        # Ensure score is in valid range
        overall_score = max(0.0, min(1.0, overall_score))
        
        report.overall_coherence = overall_score
        report.accuracy_grade = report.get_grade()
        report.meets_target = overall_score >= self.config.target_accuracy
    
    def _generate_recommendations(
        self,
        report: CoherenceReport,
        clustering_result: ClusteringResult
    ):
        """Generate improvement recommendations"""
        
        recommendations = []
        parameter_suggestions = {}
        
        # Silhouette score recommendations
        if report.silhouette_score < self.config.min_silhouette_score:
            recommendations.append(
                f"Low silhouette score ({report.silhouette_score:.3f}). "
                "Consider adjusting eps parameter or trying different clustering algorithm."
            )
            
            if clustering_result.config and clustering_result.config.eps:
                parameter_suggestions['eps'] = clustering_result.config.eps * 0.8
        
        # Semantic coherence recommendations
        if report.semantic_coherence < self.config.min_semantic_coherence:
            recommendations.append(
                f"Low semantic coherence ({report.semantic_coherence:.3f}). "
                "Consider using different embedding model or preprocessing steps."
            )
            parameter_suggestions['embedding_model'] = 'sentence-transformers/all-mpnet-base-v2'
        
        # Davies-Bouldin recommendations
        if report.davies_bouldin_score < 0.5:
            recommendations.append(
                "High Davies-Bouldin score indicates overlapping clusters. "
                "Consider increasing min_samples or using different similarity metric."
            )
            
            if clustering_result.config and clustering_result.config.min_samples:
                parameter_suggestions['min_samples'] = clustering_result.config.min_samples + 2
        
        # Cluster quality recommendations
        if report.problematic_clusters:
            recommendations.append(
                f"{len(report.problematic_clusters)} clusters have poor quality. "
                "Consider manual review or parameter adjustment."
            )
        
        # Stability recommendations
        if report.stability_score < 0.7:
            recommendations.append(
                f"Low stability score ({report.stability_score:.3f}). "
                "Clustering may be sensitive to data variations. Consider ensemble methods."
            )
        
        # Overall accuracy recommendations
        if not report.meets_target:
            recommendations.append(
                f"Overall coherence ({report.overall_coherence:.3f}) below target "
                f"({self.config.target_accuracy}). Review clustering parameters and data quality."
            )
        
        if not recommendations:
            recommendations.append("Clustering quality meets expectations. Consider fine-tuning for optimal performance.")
        
        report.improvement_recommendations = recommendations
        report.parameter_suggestions = parameter_suggestions
    
    def _create_empty_report(self, message: str) -> CoherenceReport:
        """Create empty coherence report"""
        return CoherenceReport(
            overall_coherence=0.0,
            accuracy_grade="F",
            meets_target=False,
            improvement_recommendations=[message]
        )
    
    def _update_success_metrics(self, report: CoherenceReport):
        """Update success metrics"""
        self.metrics['successful_scorings'] += 1
        self.metrics['total_processing_time'] += report.calculation_time
        
        if report.meets_target:
            self.metrics['scores_above_target'] += 1
        
        if self.metrics['scoring_operations'] > 0:
            self.metrics['average_processing_time'] = (
                self.metrics['total_processing_time'] / 
                self.metrics['scoring_operations']
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scorer metrics"""
        
        success_rate = (
            self.metrics['successful_scorings'] / 
            max(self.metrics['scoring_operations'], 1)
        )
        
        target_achievement_rate = (
            self.metrics['scores_above_target'] / 
            max(self.metrics['successful_scorings'], 1)
        )
        
        return {
            'scorer_metrics': self.metrics,
            'performance_summary': {
                'success_rate': success_rate,
                'target_achievement_rate': target_achievement_rate,
                'average_processing_time': self.metrics['average_processing_time'],
                'total_operations': self.metrics['scoring_operations']
            },
            'configuration': {
                'target_accuracy': self.config.target_accuracy,
                'min_acceptable_accuracy': self.config.min_acceptable_accuracy,
                'coherence_methods': self.config.coherence_methods,
                'enable_cross_validation': self.config.enable_cross_validation,
                'enable_bootstrap_validation': self.config.enable_bootstrap_validation
            },
            'system_status': {
                'sklearn_available': SKLEARN_AVAILABLE
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on coherence scorer"""
        try:
            if not SKLEARN_AVAILABLE:
                return {
                    'status': 'unhealthy',
                    'error': 'scikit-learn not available',
                    'sklearn_available': False
                }
            
            # Test with sample data
            sample_embeddings = np.random.rand(20, 5)
            sample_labels = np.array([0] * 10 + [1] * 10)
            
            # Quick coherence calculation
            score = silhouette_score(sample_embeddings, sample_labels)
            
            return {
                'status': 'healthy',
                'last_test_time': datetime.utcnow().isoformat(),
                'sklearn_available': SKLEARN_AVAILABLE,
                'test_silhouette_score': score
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'sklearn_available': SKLEARN_AVAILABLE
            }
    
    async def shutdown(self):
        """Gracefully shutdown coherence scorer"""
        try:
            self.logger.info("🛑 Shutting down Coherence Scorer...")
            
            # Shutdown thread pool
            self.thread_pool.shutdown(wait=True)
            
            # Clear validation cache
            self.validation_cache.clear()
            
            self.logger.info("✅ Coherence Scorer shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


# Global instance management
_global_coherence_scorer: Optional[CoherenceScorer] = None

async def get_coherence_scorer(config: Optional[ValidationConfig] = None) -> CoherenceScorer:
    """Get global coherence scorer instance"""
    global _global_coherence_scorer
    
    if _global_coherence_scorer is None:
        _global_coherence_scorer = CoherenceScorer(config)
    
    return _global_coherence_scorer