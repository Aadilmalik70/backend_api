"""
Data Models - Structured data types for data acquisition pipeline

Comprehensive data models and validation schemas for the multi-source
data acquisition pipeline, ensuring type safety and data consistency.

Features:
- Type-safe data structures using dataclasses
- Input validation and sanitization
- Flexible data aggregation models
- Performance metrics tracking
- Cache-friendly serialization
- Integration with existing SERP Strategist models

Model Categories:
1. Request/Response Models - Pipeline input/output structures
2. Data Source Models - Source-specific data formats
3. Aggregation Models - Combined data structures
4. Metrics Models - Performance and quality tracking
5. Configuration Models - Settings and parameters
"""

import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum
import hashlib

class DataSourceType(Enum):
    """Supported data sources for pipeline"""
    GOOGLE_AUTOCOMPLETE = "google_autocomplete"
    SERPAPI_PAA = "serpapi_paa"
    RELATED_SEARCHES = "related_searches"
    COMPETITOR_CONTENT = "competitor_content"

class AggregationStrategy(Enum):
    """Data aggregation strategies"""
    MERGE_SIMPLE = "merge_simple"           # Basic merging
    MERGE_INTELLIGENT = "merge_intelligent" # Smart deduplication
    MERGE_COMPREHENSIVE = "merge_comprehensive" # Full analysis
    WEIGHTED_MERGE = "weighted_merge"       # Quality-weighted

class ContentType(Enum):
    """Content types for competitor analysis"""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"
    FAQ = "faq"
    GUIDE = "guide"

class DataQuality(Enum):
    """Data quality levels"""
    EXCELLENT = "excellent"  # 0.9+
    GOOD = "good"           # 0.7-0.9
    FAIR = "fair"           # 0.5-0.7
    POOR = "poor"           # <0.5

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class PipelineMode(Enum):
    """Pipeline execution modes"""
    STANDARD = "standard"        # Normal processing
    FAST = "fast"               # Reduced timeout, fewer sources
    COMPREHENSIVE = "comprehensive"  # Extended processing, all sources
    CACHED_ONLY = "cached_only" # Only use cached data

# =============================================================================
# Request/Response Models
# =============================================================================

@dataclass
class PipelineRequest:
    """Request structure for data acquisition pipeline"""
    request_id: str
    query: str
    mode: 'PipelineMode'  # Forward reference
    sources: List[DataSourceType]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    priority: int = 1
    
    def __post_init__(self):
        """Validate and sanitize request data"""
        if not self.query.strip():
            raise ValueError("Query cannot be empty")
        
        if not self.sources:
            self.sources = [DataSourceType.GOOGLE_AUTOCOMPLETE, DataSourceType.SERPAPI_PAA]
        
        # Sanitize query
        self.query = self.query.strip()[:500]  # Limit query length

@dataclass
class PipelineResult:
    """Complete result from data acquisition pipeline"""
    request_id: str
    query: str
    status: 'PipelineStatus'  # Forward reference
    aggregated_data: Optional['AggregatedData'] = None
    source_results: List['SourceExecutionResult'] = field(default_factory=list)
    execution_time: float = 0.0
    quality_score: float = 0.0
    from_cache: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'request_id': self.request_id,
            'query': self.query,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'aggregated_data': self.aggregated_data.to_dict() if self.aggregated_data else None,
            'source_results': [
                {
                    'source_type': sr.source_type.value,
                    'success': sr.success,
                    'execution_time': sr.execution_time,
                    'quality_score': sr.quality_score,
                    'from_cache': sr.from_cache,
                    'data_summary': self._summarize_source_data(sr.data) if sr.data else None
                }
                for sr in self.source_results
            ],
            'execution_time': self.execution_time,
            'quality_score': self.quality_score,
            'from_cache': self.from_cache,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    def _summarize_source_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary of source data for API response"""
        if not data:
            return {}
        
        summary = {'data_points': 0, 'categories': []}
        
        for key, value in data.items():
            if isinstance(value, list):
                summary['data_points'] += len(value)
                summary['categories'].append(f"{key} ({len(value)})")
            elif isinstance(value, dict):
                summary['data_points'] += len(value)
                summary['categories'].append(f"{key} (object)")
            else:
                summary['categories'].append(key)
        
        return summary

@dataclass
class SourceExecutionResult:
    """Result of executing a single data source"""
    source_type: DataSourceType
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    quality_score: float = 0.0
    from_cache: bool = False
    timeout_occurred: bool = False
    retries_used: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DataSourceResult:
    """Legacy compatibility for SourceExecutionResult"""
    def __init__(self, source_type: DataSourceType, success: bool, **kwargs):
        # Convert to SourceExecutionResult for compatibility
        self.__dict__.update(SourceExecutionResult(source_type, success, **kwargs).__dict__)

# =============================================================================
# Data Source Models
# =============================================================================

@dataclass
class AutocompleteData:
    """Google Autocomplete data structure"""
    query: str
    suggestions: List[str] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    search_volumes: List[int] = field(default_factory=list)
    trending_queries: List[str] = field(default_factory=list)
    geo_data: Dict[str, List[str]] = field(default_factory=dict)
    collection_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_top_suggestions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top suggestions with metadata"""
        suggestions_with_meta = []
        
        for i, suggestion in enumerate(self.suggestions[:limit]):
            meta = {
                'suggestion': suggestion,
                'confidence': self.confidence_scores[i] if i < len(self.confidence_scores) else 0.0,
                'search_volume': self.search_volumes[i] if i < len(self.search_volumes) else 0
            }
            suggestions_with_meta.append(meta)
        
        return suggestions_with_meta

@dataclass
class PAAData:
    """People Also Ask data structure"""
    query: str
    questions: List[str] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    related_topics: List[str] = field(default_factory=list)
    intent_categories: List[str] = field(default_factory=list)
    collection_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_question_answer_pairs(self) -> List[Dict[str, Any]]:
        """Get structured question-answer pairs"""
        pairs = []
        
        for i, question in enumerate(self.questions):
            pair = {
                'question': question,
                'answer': self.answers[i] if i < len(self.answers) else "",
                'source': self.sources[i] if i < len(self.sources) else "",
                'intent': self._extract_intent(question)
            }
            pairs.append(pair)
        
        return pairs
    
    def _extract_intent(self, question: str) -> str:
        """Extract intent from question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['how', 'step', 'guide', 'tutorial']):
            return 'procedural'
        elif any(word in question_lower for word in ['what', 'who', 'when', 'where']):
            return 'factual'
        elif any(word in question_lower for word in ['why', 'explain', 'reason']):
            return 'analytical'
        elif any(word in question_lower for word in ['compare', 'vs', 'versus', 'difference']):
            return 'comparative'
        else:
            return 'general'

@dataclass
class RelatedSearchesData:
    """Related searches data structure"""
    query: str
    related_terms: List[str] = field(default_factory=list)
    search_volumes: Dict[str, int] = field(default_factory=dict)
    competition_scores: Dict[str, float] = field(default_factory=dict)
    trend_data: Dict[str, List[float]] = field(default_factory=dict)
    semantic_clusters: List[List[str]] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    collection_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_keyword_insights(self) -> Dict[str, Any]:
        """Get comprehensive keyword insights"""
        return {
            'total_keywords': len(self.related_terms),
            'high_volume_keywords': [
                term for term in self.related_terms
                if self.search_volumes.get(term, 0) > 1000
            ],
            'low_competition_keywords': [
                term for term in self.related_terms
                if self.competition_scores.get(term, 1.0) < 0.3
            ],
            'trending_keywords': [
                term for term in self.related_terms
                if self._is_trending(term)
            ],
            'semantic_groups': len(self.semantic_clusters),
            'long_tail_count': len(self.long_tail_keywords)
        }
    
    def _is_trending(self, term: str) -> bool:
        """Check if keyword is trending upward"""
        trend = self.trend_data.get(term, [])
        if len(trend) < 2:
            return False
        
        # Simple trend detection: last value > average of previous values
        return trend[-1] > sum(trend[:-1]) / len(trend[:-1])

@dataclass
class CompetitorPage:
    """Individual competitor page data"""
    url: str
    title: str
    content_length: int
    headings: Dict[str, List[str]] = field(default_factory=dict)  # h1, h2, h3, etc.
    meta_description: str = ""
    keywords: List[str] = field(default_factory=list)
    content_type: ContentType = ContentType.ARTICLE
    quality_score: float = 0.0
    authority_score: float = 0.0
    social_signals: Dict[str, int] = field(default_factory=dict)
    technical_metrics: Dict[str, Any] = field(default_factory=dict)
    collection_timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CompetitorContentData:
    """Competitor content analysis data"""
    query: str
    analyzed_pages: List[CompetitorPage] = field(default_factory=list)
    content_gaps: List[str] = field(default_factory=list)
    common_topics: List[str] = field(default_factory=list)
    average_content_length: int = 0
    top_performing_formats: List[str] = field(default_factory=list)
    keyword_opportunities: List[str] = field(default_factory=list)
    collection_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def get_content_insights(self) -> Dict[str, Any]:
        """Get comprehensive content analysis insights"""
        if not self.analyzed_pages:
            return {'error': 'No pages analyzed'}
        
        # Calculate content metrics
        content_lengths = [page.content_length for page in self.analyzed_pages]
        quality_scores = [page.quality_score for page in self.analyzed_pages]
        
        # Analyze heading structures
        heading_analysis = self._analyze_heading_patterns()
        
        return {
            'pages_analyzed': len(self.analyzed_pages),
            'content_metrics': {
                'average_length': sum(content_lengths) / len(content_lengths),
                'min_length': min(content_lengths),
                'max_length': max(content_lengths),
                'average_quality': sum(quality_scores) / len(quality_scores) if quality_scores else 0
            },
            'content_gaps': self.content_gaps,
            'common_topics': self.common_topics,
            'heading_patterns': heading_analysis,
            'keyword_opportunities': len(self.keyword_opportunities),
            'top_formats': self.top_performing_formats
        }
    
    def _analyze_heading_patterns(self) -> Dict[str, Any]:
        """Analyze heading structure patterns across pages"""
        heading_counts = {'h1': 0, 'h2': 0, 'h3': 0, 'h4': 0, 'h5': 0, 'h6': 0}
        total_pages = len(self.analyzed_pages)
        
        for page in self.analyzed_pages:
            for level, headings in page.headings.items():
                heading_counts[level] += len(headings)
        
        return {
            'average_headings_per_page': {
                level: count / total_pages if total_pages > 0 else 0
                for level, count in heading_counts.items()
            },
            'most_common_h2_topics': self._extract_common_topics('h2'),
            'heading_hierarchy_score': self._calculate_hierarchy_score()
        }
    
    def _extract_common_topics(self, heading_level: str) -> List[str]:
        """Extract most common topics from specific heading level"""
        all_headings = []
        for page in self.analyzed_pages:
            all_headings.extend(page.headings.get(heading_level, []))
        
        # Simple frequency analysis (would be more sophisticated in production)
        from collections import Counter
        heading_words = []
        for heading in all_headings:
            heading_words.extend(heading.lower().split())
        
        common_words = Counter(heading_words).most_common(10)
        return [word for word, count in common_words if len(word) > 3]
    
    def _calculate_hierarchy_score(self) -> float:
        """Calculate heading hierarchy quality score"""
        if not self.analyzed_pages:
            return 0.0
        
        scores = []
        for page in self.analyzed_pages:
            # Simple scoring: prefer pages with good h1->h2->h3 structure
            h1_count = len(page.headings.get('h1', []))
            h2_count = len(page.headings.get('h2', []))
            h3_count = len(page.headings.get('h3', []))
            
            if h1_count == 1 and h2_count > 0:  # Good structure
                score = min(1.0, (h2_count + h3_count) / 10)
            else:
                score = 0.3  # Basic score for any structure
            
            scores.append(score)
        
        return sum(scores) / len(scores)

# =============================================================================
# Aggregation Models
# =============================================================================

@dataclass
class AggregatedData:
    """Aggregated data from multiple sources"""
    query: str
    primary_suggestions: List[str] = field(default_factory=list)
    related_questions: List[Dict[str, Any]] = field(default_factory=list)
    keyword_clusters: List[List[str]] = field(default_factory=list)
    content_insights: Dict[str, Any] = field(default_factory=dict)
    search_intent: str = "informational"
    difficulty_score: float = 0.5
    opportunity_score: float = 0.5
    data_sources_used: List[DataSourceType] = field(default_factory=list)
    aggregation_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_completeness(self) -> float:
        """Calculate data completeness score"""
        completeness_factors = [
            0.25 if self.primary_suggestions else 0,
            0.25 if self.related_questions else 0,
            0.25 if self.keyword_clusters else 0,
            0.25 if self.content_insights else 0
        ]
        
        return sum(completeness_factors)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'query': self.query,
            'primary_suggestions': self.primary_suggestions,
            'related_questions': self.related_questions,
            'keyword_clusters': self.keyword_clusters,
            'content_insights': self.content_insights,
            'search_intent': self.search_intent,
            'difficulty_score': self.difficulty_score,
            'opportunity_score': self.opportunity_score,
            'data_sources_used': [ds.value for ds in self.data_sources_used],
            'completeness_score': self.calculate_completeness(),
            'aggregation_timestamp': self.aggregation_timestamp.isoformat()
        }
    
    def get_blueprint_data(self) -> Dict[str, Any]:
        """Format data for blueprint generation integration"""
        return {
            'primary_keyword': self.query,
            'related_keywords': self.primary_suggestions[:20],
            'content_questions': [q.get('question', '') for q in self.related_questions[:15]],
            'topic_clusters': self.keyword_clusters,
            'search_intent': self.search_intent,
            'content_difficulty': self.difficulty_score,
            'content_opportunity': self.opportunity_score,
            'competitor_insights': self.content_insights.get('competitor_analysis', {}),
            'suggested_content_length': self.content_insights.get('recommended_length', 1500),
            'content_format_suggestions': self.content_insights.get('format_recommendations', [])
        }

# =============================================================================
# Metrics Models
# =============================================================================

@dataclass
class SourceMetrics:
    """Performance metrics for individual data sources"""
    source_type: DataSourceType
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    cache_hit_rate: float = 0.0
    quality_score_average: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.total_requests
        return self.successful_requests / total if total > 0 else 0.0
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate"""
        return 1.0 - self.success_rate

@dataclass
class PipelineMetrics:
    """Overall pipeline performance metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    partial_requests: int = 0
    failed_requests: int = 0
    timeout_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    cache_hit_rate: float = 0.0
    source_metrics: Dict[DataSourceType, SourceMetrics] = field(default_factory=dict)
    
    def update_source_metrics(self, source_type: DataSourceType, success: bool, response_time: float, quality_score: float):
        """Update metrics for a specific source"""
        if source_type not in self.source_metrics:
            self.source_metrics[source_type] = SourceMetrics(source_type=source_type)
        
        metrics = self.source_metrics[source_type]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            metrics.last_success_time = datetime.utcnow()
        else:
            metrics.failed_requests += 1
            metrics.last_failure_time = datetime.utcnow()
        
        # Update rolling averages
        metrics.average_response_time = (
            (metrics.average_response_time * (metrics.total_requests - 1) + response_time) / 
            metrics.total_requests
        )
        
        if success and quality_score > 0:
            successful_count = metrics.successful_requests
            metrics.quality_score_average = (
                (metrics.quality_score_average * (successful_count - 1) + quality_score) / 
                successful_count
            )

# =============================================================================
# Utility Functions
# =============================================================================

def validate_query(query: str) -> bool:
    """Validate query string"""
    if not query or not query.strip():
        return False
    
    # Check for minimum length
    if len(query.strip()) < 2:
        return False
    
    # Check for maximum length
    if len(query) > 1000:
        return False
    
    return True

def sanitize_query(query: str) -> str:
    """Sanitize query string for safe processing"""
    if not query:
        return ""
    
    # Remove excessive whitespace
    query = ' '.join(query.split())
    
    # Remove potentially harmful characters
    dangerous_chars = ['<', '>', '&', '"', "'", ';', '--']
    for char in dangerous_chars:
        query = query.replace(char, '')
    
    return query.strip()[:500]  # Limit length

def generate_request_id() -> str:
    """Generate unique request ID"""
    timestamp = int(time.time() * 1000000)
    return f"req_{timestamp}"

def calculate_data_freshness(timestamp: datetime) -> float:
    """Calculate data freshness score (0.0 to 1.0)"""
    age_hours = (datetime.utcnow() - timestamp).total_seconds() / 3600
    
    if age_hours < 1:
        return 1.0
    elif age_hours < 24:
        return 0.8
    elif age_hours < 168:  # 1 week
        return 0.6
    elif age_hours < 720:  # 1 month
        return 0.4
    else:
        return 0.2