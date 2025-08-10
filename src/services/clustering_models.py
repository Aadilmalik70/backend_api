"""
Semantic Clustering Data Models

Comprehensive data models for semantic clustering operations including cluster representation,
embedding management, coherence scoring, and configuration structures. Designed for integration
with the existing SERP Strategist data acquisition pipeline.

Features:
- SemanticCluster: Individual cluster representation with metadata
- ClusteringResult: Complete clustering operation results
- EmbeddingData: Vector embedding management and storage
- CoherenceScore: Quality assessment and validation metrics
- ClusteringConfig: Comprehensive configuration management
- Integration with existing data pipeline patterns

Performance Targets: >85% clustering accuracy, <2s real-time, <30s batch processing
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from datetime import datetime
from enum import Enum
import numpy as np
from uuid import uuid4
import json


class ClusteringAlgorithm(Enum):
    """Supported clustering algorithms"""
    DBSCAN = "dbscan"
    KMEANS = "kmeans"
    HIERARCHICAL = "hierarchical"
    HDBSCAN = "hdbscan"


class SimilarityMetric(Enum):
    """Supported similarity metrics"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"


class ClusteringStatus(Enum):
    """Status of clustering operations"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"


class CoherenceMethod(Enum):
    """Methods for calculating cluster coherence"""
    SILHOUETTE = "silhouette"
    CALINSKI_HARABASZ = "calinski_harabasz" 
    DAVIES_BOULDIN = "davies_bouldin"
    SEMANTIC_COHERENCE = "semantic_coherence"
    COMBINED = "combined"


@dataclass
class EmbeddingData:
    """Vector embedding data with metadata"""
    
    # Core embedding data
    vector: List[float]  # The actual embedding vector
    text: str  # Original text that was embedded
    embedding_id: str = field(default_factory=lambda: str(uuid4()))
    
    # Metadata
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_timestamp: datetime = field(default_factory=datetime.utcnow)
    vector_dimension: int = 0
    
    # Processing metadata
    preprocessing_steps: List[str] = field(default_factory=list)
    text_length: int = 0
    token_count: int = 0
    
    # Quality metrics
    confidence_score: float = 1.0
    embedding_quality: float = 0.0
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.vector_dimension:
            self.vector_dimension = len(self.vector)
        
        if not self.text_length:
            self.text_length = len(self.text)
        
        if not self.token_count:
            self.token_count = len(self.text.split())
    
    def as_numpy(self) -> np.ndarray:
        """Convert embedding vector to numpy array"""
        return np.array(self.vector)
    
    def normalize(self) -> 'EmbeddingData':
        """Return normalized version of embedding"""
        vector_array = self.as_numpy()
        norm = np.linalg.norm(vector_array)
        
        if norm > 0:
            normalized_vector = (vector_array / norm).tolist()
        else:
            normalized_vector = self.vector
        
        return EmbeddingData(
            vector=normalized_vector,
            text=self.text,
            embedding_id=self.embedding_id,
            model_name=self.model_name,
            embedding_timestamp=self.embedding_timestamp,
            vector_dimension=self.vector_dimension,
            preprocessing_steps=self.preprocessing_steps + ["normalized"],
            text_length=self.text_length,
            token_count=self.token_count,
            confidence_score=self.confidence_score,
            embedding_quality=self.embedding_quality
        )


@dataclass
class SemanticCluster:
    """Individual semantic cluster with comprehensive metadata"""
    
    # Core cluster data
    cluster_id: str = field(default_factory=lambda: str(uuid4()))
    label: int = -1  # Cluster label (-1 for noise in DBSCAN)
    
    # Cluster members
    embedding_ids: List[str] = field(default_factory=list)
    texts: List[str] = field(default_factory=list)
    
    # Cluster characteristics
    centroid: Optional[List[float]] = None
    size: int = 0
    density: float = 0.0
    
    # Quality metrics
    coherence_score: float = 0.0
    silhouette_score: float = 0.0
    intra_cluster_distance: float = 0.0
    inter_cluster_distance: float = 0.0
    
    # Semantic properties
    representative_texts: List[str] = field(default_factory=list)
    cluster_keywords: List[str] = field(default_factory=list)
    topic_labels: List[str] = field(default_factory=list)
    semantic_similarity: float = 0.0
    
    # Metadata
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    algorithm_used: ClusteringAlgorithm = ClusteringAlgorithm.DBSCAN
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    
    def __post_init__(self):
        """Initialize computed fields"""
        if not self.size:
            self.size = len(self.texts)
        
        if not self.representative_texts and self.texts:
            # Use first few texts as representatives
            self.representative_texts = self.texts[:min(3, len(self.texts))]
    
    def add_member(self, embedding_id: str, text: str):
        """Add a new member to the cluster"""
        self.embedding_ids.append(embedding_id)
        self.texts.append(text)
        self.size = len(self.texts)
        
        # Update representative texts if needed
        if len(self.representative_texts) < 3:
            self.representative_texts.append(text)
    
    def get_cluster_summary(self) -> Dict[str, Any]:
        """Get a summary of the cluster"""
        return {
            'cluster_id': self.cluster_id,
            'label': self.label,
            'size': self.size,
            'coherence_score': self.coherence_score,
            'silhouette_score': self.silhouette_score,
            'representative_texts': self.representative_texts,
            'cluster_keywords': self.cluster_keywords,
            'topic_labels': self.topic_labels,
            'semantic_similarity': self.semantic_similarity,
            'algorithm_used': self.algorithm_used.value,
            'similarity_metric': self.similarity_metric.value
        }
    
    def is_noise_cluster(self) -> bool:
        """Check if this is a noise cluster"""
        return self.label == -1


@dataclass
class CoherenceScore:
    """Comprehensive coherence scoring for cluster quality assessment"""
    
    # Overall scores
    overall_coherence: float = 0.0
    target_accuracy: float = 0.85
    meets_target: bool = False
    
    # Individual coherence metrics
    silhouette_score: float = 0.0
    calinski_harabasz_score: float = 0.0
    davies_bouldin_score: float = 0.0
    semantic_coherence: float = 0.0
    
    # Cluster-specific scores
    cluster_coherence_scores: Dict[str, float] = field(default_factory=dict)
    cluster_silhouette_scores: Dict[str, float] = field(default_factory=dict)
    
    # Quality indicators
    optimal_cluster_count: int = 0
    noise_ratio: float = 0.0
    cluster_balance: float = 0.0
    
    # Method metadata
    coherence_method: CoherenceMethod = CoherenceMethod.COMBINED
    calculation_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Performance metrics
    calculation_time: float = 0.0
    validation_passed: bool = False
    
    def __post_init__(self):
        """Initialize computed fields"""
        self.meets_target = self.overall_coherence >= self.target_accuracy
        
        if not self.validation_passed:
            self.validation_passed = self._validate_scores()
    
    def _validate_scores(self) -> bool:
        """Validate coherence score ranges"""
        # Check if scores are within expected ranges
        scores_to_check = [
            self.overall_coherence,
            self.silhouette_score,
            self.semantic_coherence
        ]
        
        for score in scores_to_check:
            if not (-1.0 <= score <= 1.0):
                return False
        
        return True
    
    def get_quality_assessment(self) -> Dict[str, Any]:
        """Get comprehensive quality assessment"""
        return {
            'overall_coherence': self.overall_coherence,
            'meets_target': self.meets_target,
            'target_accuracy': self.target_accuracy,
            'quality_breakdown': {
                'silhouette_score': self.silhouette_score,
                'calinski_harabasz_score': self.calinski_harabasz_score,
                'davies_bouldin_score': self.davies_bouldin_score,
                'semantic_coherence': self.semantic_coherence
            },
            'cluster_metrics': {
                'optimal_cluster_count': self.optimal_cluster_count,
                'noise_ratio': self.noise_ratio,
                'cluster_balance': self.cluster_balance
            },
            'validation_status': {
                'validation_passed': self.validation_passed,
                'calculation_time': self.calculation_time,
                'coherence_method': self.coherence_method.value
            }
        }


@dataclass
class ClusteringConfig:
    """Comprehensive configuration for semantic clustering operations"""
    
    # Algorithm configuration
    algorithm: ClusteringAlgorithm = ClusteringAlgorithm.DBSCAN
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    
    # DBSCAN parameters
    eps: float = 0.3  # Maximum distance between samples in same cluster
    min_samples: int = 5  # Minimum samples to form a cluster
    
    # K-Means parameters (if used)
    n_clusters: int = 8
    max_iter: int = 300
    random_state: int = 42
    
    # Embedding configuration
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    max_sequence_length: int = 512
    normalize_embeddings: bool = True
    
    # Processing configuration
    min_text_length: int = 10
    max_text_length: int = 2000
    remove_duplicates: bool = True
    preprocessing_steps: List[str] = field(default_factory=lambda: [
        "lowercase", "strip_whitespace", "remove_empty"
    ])
    
    # Performance settings
    batch_size: int = 32
    max_concurrent_requests: int = 10
    timeout_seconds: float = 30.0
    enable_caching: bool = True
    enable_parallel: bool = True
    
    # Quality thresholds
    min_coherence_score: float = 0.5
    target_coherence_score: float = 0.85
    max_noise_ratio: float = 0.3
    min_cluster_size: int = 3
    
    # Output configuration
    max_representative_texts: int = 3
    include_embeddings_in_output: bool = False
    calculate_cluster_keywords: bool = True
    extract_topic_labels: bool = True
    
    # Validation settings
    enable_validation: bool = True
    cross_validation_folds: int = 5
    validation_sample_size: int = 1000
    
    def validate_config(self) -> Tuple[bool, List[str]]:
        """Validate configuration parameters"""
        errors = []
        
        # Validate DBSCAN parameters
        if self.algorithm == ClusteringAlgorithm.DBSCAN:
            if self.eps <= 0:
                errors.append("DBSCAN eps must be positive")
            if self.min_samples <= 0:
                errors.append("DBSCAN min_samples must be positive")
        
        # Validate K-Means parameters
        if self.algorithm == ClusteringAlgorithm.KMEANS:
            if self.n_clusters <= 0:
                errors.append("K-Means n_clusters must be positive")
            if self.max_iter <= 0:
                errors.append("K-Means max_iter must be positive")
        
        # Validate coherence thresholds
        if not (0.0 <= self.min_coherence_score <= 1.0):
            errors.append("min_coherence_score must be between 0 and 1")
        if not (0.0 <= self.target_coherence_score <= 1.0):
            errors.append("target_coherence_score must be between 0 and 1")
        if self.min_coherence_score > self.target_coherence_score:
            errors.append("min_coherence_score must be <= target_coherence_score")
        
        # Validate text length parameters
        if self.min_text_length >= self.max_text_length:
            errors.append("min_text_length must be < max_text_length")
        
        # Validate performance parameters
        if self.batch_size <= 0:
            errors.append("batch_size must be positive")
        if self.timeout_seconds <= 0:
            errors.append("timeout_seconds must be positive")
        
        return len(errors) == 0, errors
    
    def get_algorithm_params(self) -> Dict[str, Any]:
        """Get algorithm-specific parameters"""
        if self.algorithm == ClusteringAlgorithm.DBSCAN:
            return {
                'eps': self.eps,
                'min_samples': self.min_samples,
                'metric': self.similarity_metric.value if self.similarity_metric != SimilarityMetric.COSINE else 'cosine'
            }
        elif self.algorithm == ClusteringAlgorithm.KMEANS:
            return {
                'n_clusters': self.n_clusters,
                'max_iter': self.max_iter,
                'random_state': self.random_state
            }
        else:
            return {}


@dataclass
class ClusteringResult:
    """Complete result of a semantic clustering operation"""
    
    # Request information
    request_id: str = field(default_factory=lambda: str(uuid4()))
    query: str = ""
    input_texts: List[str] = field(default_factory=list)
    
    # Clustering results
    clusters: List[SemanticCluster] = field(default_factory=list)
    noise_points: List[str] = field(default_factory=list)
    embeddings: List[EmbeddingData] = field(default_factory=list)
    
    # Quality metrics
    coherence_score: Optional[CoherenceScore] = None
    coherence_report: Optional[Any] = None  # For backwards compatibility with CoherenceReport
    overall_quality: float = 0.0
    
    # Metadata  
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Execution metadata
    status: ClusteringStatus = ClusteringStatus.PENDING
    execution_time: float = 0.0
    processing_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Configuration used
    config: Optional[ClusteringConfig] = None
    
    # Performance metrics
    total_clusters: int = 0
    noise_cluster_size: int = 0
    largest_cluster_size: int = 0
    smallest_cluster_size: int = 0
    
    # Error handling
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize computed fields"""
        self._calculate_cluster_stats()
        
        if self.coherence_score:
            self.overall_quality = self.coherence_score.overall_coherence
    
    def _calculate_cluster_stats(self):
        """Calculate cluster statistics"""
        valid_clusters = [c for c in self.clusters if not c.is_noise_cluster()]
        
        self.total_clusters = len(valid_clusters)
        self.noise_cluster_size = len(self.noise_points)
        
        if valid_clusters:
            cluster_sizes = [c.size for c in valid_clusters]
            self.largest_cluster_size = max(cluster_sizes)
            self.smallest_cluster_size = min(cluster_sizes)
    
    def add_cluster(self, cluster: SemanticCluster):
        """Add a cluster to the results"""
        self.clusters.append(cluster)
        self._calculate_cluster_stats()
    
    def get_cluster_by_label(self, label: int) -> Optional[SemanticCluster]:
        """Get cluster by label"""
        for cluster in self.clusters:
            if cluster.label == label:
                return cluster
        return None
    
    def get_non_noise_clusters(self) -> List[SemanticCluster]:
        """Get all non-noise clusters"""
        return [c for c in self.clusters if not c.is_noise_cluster()]
    
    def get_cluster_summaries(self) -> List[Dict[str, Any]]:
        """Get summaries of all clusters"""
        return [cluster.get_cluster_summary() for cluster in self.clusters]
    
    def get_result_summary(self) -> Dict[str, Any]:
        """Get comprehensive result summary"""
        return {
            'request_id': self.request_id,
            'query': self.query,
            'input_count': len(self.input_texts),
            'status': self.status.value,
            'execution_time': self.execution_time,
            'quality_metrics': {
                'overall_quality': self.overall_quality,
                'coherence_assessment': self.coherence_score.get_quality_assessment() if self.coherence_score else None
            },
            'cluster_statistics': {
                'total_clusters': self.total_clusters,
                'noise_points': self.noise_cluster_size,
                'largest_cluster_size': self.largest_cluster_size,
                'smallest_cluster_size': self.smallest_cluster_size,
                'average_cluster_size': sum(c.size for c in self.get_non_noise_clusters()) / max(self.total_clusters, 1)
            },
            'configuration': {
                'algorithm': self.config.algorithm.value if self.config else 'unknown',
                'similarity_metric': self.config.similarity_metric.value if self.config else 'unknown',
                'embedding_model': self.config.embedding_model if self.config else 'unknown'
            },
            'error_info': {
                'error_message': self.error_message,
                'warnings': self.warnings
            }
        }
    
    def meets_quality_threshold(self, threshold: float = 0.85) -> bool:
        """Check if clustering meets quality threshold"""
        return self.overall_quality >= threshold
    
    def export_clusters_json(self) -> str:
        """Export clusters as JSON string"""
        export_data = {
            'metadata': self.get_result_summary(),
            'clusters': self.get_cluster_summaries()
        }
        return json.dumps(export_data, indent=2, default=str)


# Utility functions for data model operations

def create_clustering_config(
    algorithm: str = "dbscan",
    similarity_metric: str = "cosine", 
    **kwargs
) -> ClusteringConfig:
    """Create clustering configuration with validation"""
    
    # Convert string enums
    algorithm_enum = ClusteringAlgorithm(algorithm.lower())
    similarity_enum = SimilarityMetric(similarity_metric.lower())
    
    config = ClusteringConfig(
        algorithm=algorithm_enum,
        similarity_metric=similarity_enum,
        **kwargs
    )
    
    # Validate configuration
    is_valid, errors = config.validate_config()
    if not is_valid:
        raise ValueError(f"Invalid clustering configuration: {'; '.join(errors)}")
    
    return config


def create_embedding_batch(
    texts: List[str],
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
) -> List[EmbeddingData]:
    """Create a batch of embedding data structures"""
    
    embeddings = []
    for text in texts:
        if isinstance(text, str) and len(text.strip()) > 0:
            embedding = EmbeddingData(
                vector=[],  # Will be filled by embedding service
                text=text.strip(),
                model_name=model_name
            )
            embeddings.append(embedding)
    
    return embeddings


def merge_clustering_results(
    results: List[ClusteringResult]
) -> ClusteringResult:
    """Merge multiple clustering results into one"""
    
    if not results:
        return ClusteringResult()
    
    if len(results) == 1:
        return results[0]
    
    # Create merged result
    merged = ClusteringResult(
        query="merged_results",
        status=ClusteringStatus.COMPLETED
    )
    
    # Merge clusters and data
    cluster_label_offset = 0
    for result in results:
        # Add input texts
        merged.input_texts.extend(result.input_texts)
        
        # Add embeddings
        merged.embeddings.extend(result.embeddings)
        
        # Add clusters with adjusted labels
        for cluster in result.clusters:
            if not cluster.is_noise_cluster():
                cluster.label += cluster_label_offset
            merged.clusters.append(cluster)
        
        # Add noise points
        merged.noise_points.extend(result.noise_points)
        
        # Update label offset
        non_noise_clusters = [c for c in result.clusters if not c.is_noise_cluster()]
        if non_noise_clusters:
            cluster_label_offset += max(c.label for c in non_noise_clusters) + 1
    
    # Recalculate statistics
    merged._calculate_cluster_stats()
    
    return merged