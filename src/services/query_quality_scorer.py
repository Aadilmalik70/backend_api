"""
Query Quality Scorer - Multi-dimensional quality assessment system

Provides comprehensive quality scoring for queries and responses across different
question types and business domains with configurable weighting schemes.

Features:
- Multi-dimensional quality metrics (clarity, relevance, completeness, actionability)
- Question-type specific scoring algorithms
- Domain-aware quality assessment
- Performance benchmarking and optimization
- Configurable quality thresholds and weights

Designed for high-performance scoring with <50ms response time per assessment.
"""

import asyncio
import logging
import time
import statistics
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import re
import json

# Import related services
from .question_type_classifier import QuestionType
from .domain_expansion_engine import BusinessDomain

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality assessment dimensions"""
    CLARITY = "clarity"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    ACTIONABILITY = "actionability"
    ACCURACY = "accuracy"
    SPECIFICITY = "specificity"
    COMPLEXITY = "complexity"

@dataclass
class QualityMetric:
    """Individual quality metric assessment"""
    dimension: QualityDimension
    score: float  # 0.0 - 1.0
    reasoning: str
    contributing_factors: List[str] = field(default_factory=list)
    weight: float = 1.0

@dataclass
class QualityAssessment:
    """Complete quality assessment result"""
    overall_score: float  # 0.0 - 1.0
    grade: str  # A, B, C, D, F
    individual_metrics: List[QualityMetric]
    question_type: Optional[QuestionType] = None
    primary_domain: Optional[BusinessDomain] = None
    strengths: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    confidence_level: float = 0.0

@dataclass
class QualityBenchmark:
    """Quality benchmarking data"""
    question_type: QuestionType
    domain: BusinessDomain
    avg_score: float
    score_distribution: Dict[str, int]  # Grade distribution
    common_issues: List[str]
    best_practices: List[str]

class QueryQualityScorer:
    """
    Advanced multi-dimensional quality scoring system for queries and responses.
    
    Provides comprehensive quality assessment with question-type and domain-specific
    scoring algorithms optimized for different use cases.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the query quality scorer"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Quality dimension weights by question type
        self.dimension_weights = self._initialize_dimension_weights()
        
        # Quality assessment patterns and rules
        self.assessment_patterns = self._initialize_assessment_patterns()
        
        # Benchmarking data
        self.quality_benchmarks = {}
        
        # Performance metrics
        self.metrics = {
            'total_assessments': 0,
            'avg_processing_time': 0.0,
            'score_distribution': {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0},
            'dimension_accuracy': {},
            'common_quality_issues': {}
        }
        
        self.logger.info("Query Quality Scorer initialized with multi-dimensional assessment")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for quality scoring"""
        return {
            'grade_thresholds': {
                'A': 0.9,
                'B': 0.8,
                'C': 0.7,
                'D': 0.6,
                'F': 0.0
            },
            'enable_benchmarking': True,
            'enable_improvement_suggestions': True,
            'min_confidence_threshold': 0.6,
            'max_assessment_time_ms': 50,
            'enable_domain_weighting': True
        }
    
    def _initialize_dimension_weights(self) -> Dict[QuestionType, Dict[QualityDimension, float]]:
        """Initialize quality dimension weights by question type"""
        return {
            QuestionType.FACTUAL: {
                QualityDimension.ACCURACY: 0.4,
                QualityDimension.RELEVANCE: 0.3,
                QualityDimension.COMPLETENESS: 0.2,
                QualityDimension.CLARITY: 0.1
            },
            QuestionType.ANALYTICAL: {
                QualityDimension.RELEVANCE: 0.3,
                QualityDimension.COMPLETENESS: 0.3,
                QualityDimension.ACCURACY: 0.2,
                QualityDimension.COMPLEXITY: 0.2
            },
            QuestionType.COMPARATIVE: {
                QualityDimension.RELEVANCE: 0.3,
                QualityDimension.COMPLETENESS: 0.3,
                QualityDimension.ACCURACY: 0.2,
                QualityDimension.CLARITY: 0.2
            },
            QuestionType.PROCEDURAL: {
                QualityDimension.ACTIONABILITY: 0.4,
                QualityDimension.COMPLETENESS: 0.3,
                QualityDimension.CLARITY: 0.2,
                QualityDimension.SPECIFICITY: 0.1
            },
            QuestionType.CREATIVE: {
                QualityDimension.ACTIONABILITY: 0.4,
                QualityDimension.RELEVANCE: 0.3,
                QualityDimension.COMPLETENESS: 0.2,
                QualityDimension.CLARITY: 0.1
            },
            QuestionType.DIAGNOSTIC: {
                QualityDimension.ACTIONABILITY: 0.4,
                QualityDimension.ACCURACY: 0.3,
                QualityDimension.COMPLETENESS: 0.2,
                QualityDimension.SPECIFICITY: 0.1
            },
            QuestionType.UNKNOWN: {
                QualityDimension.RELEVANCE: 0.25,
                QualityDimension.CLARITY: 0.25,
                QualityDimension.COMPLETENESS: 0.25,
                QualityDimension.ACTIONABILITY: 0.25
            }
        }
    
    def _initialize_assessment_patterns(self) -> Dict[QualityDimension, Dict[str, Any]]:
        """Initialize quality assessment patterns"""
        return {
            QualityDimension.CLARITY: {
                'high_indicators': [
                    r'\b(specific|exact|precise|clear|detailed)\b',
                    r'\b(who|what|when|where|why|how)\b',
                    r'\b\d+\b',  # Numbers indicate specificity
                    r'\b(please|help|need|want)\b'  # Clear intent
                ],
                'low_indicators': [
                    r'\b(maybe|possibly|somewhat|kind of|sort of)\b',
                    r'\b(thing|stuff|something|anything)\b',
                    r'^.{0,20}$',  # Very short queries
                    r'\b(um|uh|er|hmm)\b'  # Hesitation words
                ],
                'scoring_factors': {
                    'length_optimal': (10, 100),  # Character range for optimal length
                    'question_words_bonus': 0.2,
                    'vague_penalty': 0.3
                }
            },
            QualityDimension.RELEVANCE: {
                'high_indicators': [
                    r'\b(business|marketing|sales|finance|operations)\b',
                    r'\b(strategy|plan|approach|method)\b',
                    r'\b(improve|optimize|increase|enhance)\b',
                    r'\b(analysis|research|data|insights)\b'
                ],
                'low_indicators': [
                    r'^(hi|hello|test|testing)$',
                    r'\b(random|whatever|anything|nothing)\b',
                    r'^.{0,5}$',  # Very short queries
                    r'^\W+$'  # Only punctuation/symbols
                ],
                'scoring_factors': {
                    'domain_keyword_bonus': 0.3,
                    'generic_penalty': 0.2
                }
            },
            QualityDimension.COMPLETENESS: {
                'high_indicators': [
                    r'\b(complete|comprehensive|detailed|thorough)\b',
                    r'\b(include|considering|with|using)\b',
                    r'\b(step.by.step|detailed|comprehensive)\b',
                    r'\b(all|every|entire|complete)\b'
                ],
                'low_indicators': [
                    r'^.{0,20}$',  # Very short queries
                    r'\b(just|only|simple|basic)\b',
                    r'^\w+\s*\?*$'  # Single word queries
                ],
                'scoring_factors': {
                    'detail_level_bonus': 0.2,
                    'brevity_penalty': 0.1
                }
            },
            QualityDimension.ACTIONABILITY: {
                'high_indicators': [
                    r'\b(how to|guide|steps|process|implement)\b',
                    r'\b(create|build|develop|design|make)\b',
                    r'\b(plan|strategy|approach|method)\b',
                    r'\b(action|execute|do|perform)\b'
                ],
                'low_indicators': [
                    r'\b(what is|who is|when was)\b',  # Pure factual
                    r'\b(theory|concept|idea|thought)\b',  # Abstract concepts
                    r'\b(general|abstract|conceptual)\b'
                ],
                'scoring_factors': {
                    'action_verb_bonus': 0.3,
                    'abstract_penalty': 0.2
                }
            },
            QualityDimension.ACCURACY: {
                'assessment_method': 'contextual',  # Requires context/domain knowledge
                'factors': [
                    'factual_consistency',
                    'domain_appropriateness',  
                    'terminology_correctness',
                    'logical_coherence'
                ]
            },
            QualityDimension.SPECIFICITY: {
                'high_indicators': [
                    r'\b\d+\b',  # Numbers
                    r'\b(specific|exact|particular|precise)\b',
                    r'\b\w+\.\w+\b',  # Domain names, file extensions
                    r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'  # Proper nouns
                ],
                'low_indicators': [
                    r'\b(general|generic|any|all|some)\b',
                    r'\b(thing|stuff|something|anything)\b',
                    r'\b(etc|and so on|among others)\b'
                ],
                'scoring_factors': {
                    'proper_noun_bonus': 0.2,
                    'number_bonus': 0.1,
                    'generic_penalty': 0.3
                }
            },
            QualityDimension.COMPLEXITY: {
                'assessment_method': 'computational',
                'factors': [
                    'sentence_structure',
                    'vocabulary_sophistication',
                    'concept_depth',
                    'multi_part_queries'
                ]
            }
        }
    
    async def assess_query_quality(
        self,
        query: str,
        question_type: Optional[QuestionType] = None,
        domain: Optional[BusinessDomain] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> QualityAssessment:
        """
        Assess the quality of a query across multiple dimensions
        
        Args:
            query: The query to assess
            question_type: Optional question type for type-specific scoring
            domain: Optional domain for domain-aware scoring
            context: Optional context for enhanced assessment
            
        Returns:
            QualityAssessment with scores and recommendations
        """
        start_time = time.time()
        
        try:
            if not query or not query.strip():
                return QualityAssessment(
                    overall_score=0.0,
                    grade='F',
                    individual_metrics=[],
                    processing_time=time.time() - start_time,
                    confidence_level=0.0,
                    improvement_suggestions=["Query is empty or invalid"]
                )
            
            query = query.strip()
            self.logger.debug(f"Assessing query quality: '{query[:50]}...'")
            
            # Determine question type if not provided
            if question_type is None:
                question_type = QuestionType.UNKNOWN
            
            # Get dimension weights for this question type
            weights = self.dimension_weights.get(question_type, self.dimension_weights[QuestionType.UNKNOWN])
            
            # Assess each quality dimension
            individual_metrics = []
            for dimension, weight in weights.items():
                metric = await self._assess_dimension(query, dimension, question_type, domain, context)
                metric.weight = weight
                individual_metrics.append(metric)
            
            # Calculate overall score (weighted average)
            total_weighted_score = sum(metric.score * metric.weight for metric in individual_metrics)
            total_weight = sum(metric.weight for metric in individual_metrics)
            overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
            
            # Determine grade
            grade = self._calculate_grade(overall_score)
            
            # Generate strengths and improvement suggestions
            strengths = await self._identify_strengths(individual_metrics, query)
            improvement_suggestions = await self._generate_improvement_suggestions(individual_metrics, query, question_type)
            
            # Calculate confidence level
            confidence_level = await self._calculate_confidence(individual_metrics, question_type, domain)
            
            # Create assessment result
            processing_time = time.time() - start_time
            assessment = QualityAssessment(
                overall_score=overall_score,
                grade=grade,
                individual_metrics=individual_metrics,
                question_type=question_type,
                primary_domain=domain,
                strengths=strengths,
                improvement_suggestions=improvement_suggestions,
                processing_time=processing_time,
                confidence_level=confidence_level
            )
            
            # Update metrics
            self._update_metrics(assessment)
            
            self.logger.info(f"Quality assessed: {grade} ({overall_score:.3f}) in {processing_time:.3f}s")
            return assessment
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            return QualityAssessment(
                overall_score=0.0,
                grade='F',
                individual_metrics=[],
                processing_time=time.time() - start_time,
                confidence_level=0.0,
                improvement_suggestions=[f"Assessment error: {str(e)}"]
            )
    
    async def _assess_dimension(
        self,
        query: str,
        dimension: QualityDimension,
        question_type: QuestionType,
        domain: Optional[BusinessDomain],
        context: Optional[Dict[str, Any]]
    ) -> QualityMetric:
        """Assess a single quality dimension"""
        
        patterns = self.assessment_patterns.get(dimension, {})
        query_lower = query.lower()
        
        if dimension == QualityDimension.CLARITY:
            score = await self._assess_clarity(query, patterns)
        elif dimension == QualityDimension.RELEVANCE:
            score = await self._assess_relevance(query, patterns, domain)
        elif dimension == QualityDimension.COMPLETENESS:
            score = await self._assess_completeness(query, patterns, question_type)
        elif dimension == QualityDimension.ACTIONABILITY:
            score = await self._assess_actionability(query, patterns, question_type)
        elif dimension == QualityDimension.ACCURACY:
            score = await self._assess_accuracy(query, domain, context)
        elif dimension == QualityDimension.SPECIFICITY:
            score = await self._assess_specificity(query, patterns)
        elif dimension == QualityDimension.COMPLEXITY:
            score = await self._assess_complexity(query, question_type)
        else:
            score = 0.5  # Default neutral score
        
        # Generate reasoning
        reasoning = await self._generate_dimension_reasoning(dimension, score, query)
        
        return QualityMetric(
            dimension=dimension,
            score=score,
            reasoning=reasoning,
            contributing_factors=[]
        )
    
    async def _assess_clarity(self, query: str, patterns: Dict[str, Any]) -> float:
        """Assess query clarity"""
        score = 0.5  # Base score
        
        # Length assessment
        query_length = len(query)
        optimal_min, optimal_max = patterns.get('scoring_factors', {}).get('length_optimal', (10, 100))
        
        if optimal_min <= query_length <= optimal_max:
            score += 0.2
        elif query_length < optimal_min:
            score -= 0.2
        elif query_length > optimal_max * 2:
            score -= 0.1
        
        # High clarity indicators
        high_count = 0
        for pattern in patterns.get('high_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                high_count += 1
        score += min(high_count * 0.1, 0.3)
        
        # Low clarity indicators
        low_count = 0
        for pattern in patterns.get('low_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                low_count += 1
        score -= min(low_count * 0.15, 0.4)
        
        # Question words bonus
        question_words = ['what', 'who', 'when', 'where', 'why', 'how', 'which']
        if any(word in query.lower() for word in question_words):
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _assess_relevance(self, query: str, patterns: Dict[str, Any], domain: Optional[BusinessDomain]) -> float:
        """Assess query relevance"""
        score = 0.5  # Base score
        
        # High relevance indicators
        high_count = 0
        for pattern in patterns.get('high_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                high_count += 1
        score += min(high_count * 0.15, 0.4)
        
        # Low relevance indicators (penalize)
        low_count = 0
        for pattern in patterns.get('low_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                low_count += 1
        score -= min(low_count * 0.2, 0.4)
        
        # Domain-specific relevance boost
        if domain and self.config.get('enable_domain_weighting', True):
            # This would require integration with domain expansion engine
            # For now, give moderate boost for having a detected domain
            score += 0.1
        
        return max(0.0, min(1.0, score))
    
    async def _assess_completeness(self, query: str, patterns: Dict[str, Any], question_type: QuestionType) -> float:
        """Assess query completeness"""
        score = 0.5  # Base score
        
        # Length-based completeness
        query_length = len(query)
        if query_length > 50:
            score += 0.2
        elif query_length < 15:
            score -= 0.3
        
        # High completeness indicators
        high_count = 0
        for pattern in patterns.get('high_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                high_count += 1
        score += min(high_count * 0.1, 0.3)
        
        # Question type specific completeness
        if question_type == QuestionType.PROCEDURAL:
            # Procedural queries should ask for steps/process
            if any(word in query.lower() for word in ['steps', 'process', 'how', 'guide']):
                score += 0.2
        elif question_type == QuestionType.COMPARATIVE:
            # Comparative queries should mention alternatives
            if any(word in query.lower() for word in ['vs', 'versus', 'compare', 'better', 'alternative']):
                score += 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _assess_actionability(self, query: str, patterns: Dict[str, Any], question_type: QuestionType) -> float:
        """Assess query actionability"""
        score = 0.3  # Lower base score as not all queries need to be actionable
        
        # High actionability indicators
        high_count = 0
        for pattern in patterns.get('high_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                high_count += 1
        score += min(high_count * 0.2, 0.5)
        
        # Question type modifiers
        if question_type in [QuestionType.PROCEDURAL, QuestionType.CREATIVE, QuestionType.DIAGNOSTIC]:
            score += 0.2  # These types should be more actionable
        elif question_type == QuestionType.FACTUAL:
            score -= 0.1  # Factual queries are less about action
        
        # Action verbs check
        action_verbs = ['create', 'build', 'implement', 'develop', 'design', 'make', 'generate', 'fix', 'solve']
        if any(verb in query.lower() for verb in action_verbs):
            score += 0.2
        
        return max(0.0, min(1.0, score))
    
    async def _assess_accuracy(self, query: str, domain: Optional[BusinessDomain], context: Optional[Dict[str, Any]]) -> float:
        """Assess query accuracy (contextual assessment)"""
        score = 0.7  # Default good score as accuracy is hard to assess without context
        
        # Basic accuracy indicators
        # Check for obvious inaccuracies or nonsensical combinations
        nonsensical_patterns = [
            r'\b(colorless green ideas sleep furiously)\b',  # Famous nonsensical phrase
            r'\b(square circle|cold fire|dry water)\b',  # Contradictory terms
        ]
        
        for pattern in nonsensical_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score -= 0.4
        
        # Domain consistency check
        if domain and context:
            # Would require more sophisticated domain knowledge validation
            # For now, maintain neutral score
            pass
        
        return max(0.0, min(1.0, score))
    
    async def _assess_specificity(self, query: str, patterns: Dict[str, Any]) -> float:
        """Assess query specificity"""
        score = 0.5  # Base score
        
        # High specificity indicators
        high_count = 0
        for pattern in patterns.get('high_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                high_count += 1
        score += min(high_count * 0.15, 0.4)
        
        # Low specificity indicators
        low_count = 0
        for pattern in patterns.get('low_indicators', []):
            if re.search(pattern, query, re.IGNORECASE):
                low_count += 1
        score -= min(low_count * 0.2, 0.4)
        
        # Count specific elements
        numbers = len(re.findall(r'\b\d+\b', query))
        proper_nouns = len(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query))
        
        score += min(numbers * 0.05, 0.1)
        score += min(proper_nouns * 0.05, 0.2)
        
        return max(0.0, min(1.0, score))
    
    async def _assess_complexity(self, query: str, question_type: QuestionType) -> float:
        """Assess appropriate complexity level"""
        score = 0.5  # Base score
        
        # Sentence structure complexity
        sentences = query.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Moderate complexity is often optimal
        if 10 <= avg_sentence_length <= 25:
            score += 0.2
        elif avg_sentence_length > 30:
            score -= 0.1  # Too complex
        elif avg_sentence_length < 5:
            score -= 0.2  # Too simple
        
        # Vocabulary sophistication (rough measure)
        long_words = len([word for word in query.split() if len(word) > 7])
        if long_words > 0:
            score += min(long_words * 0.05, 0.2)
        
        # Question type appropriateness
        if question_type == QuestionType.ANALYTICAL:
            score += 0.1  # Analytical queries should be somewhat complex
        elif question_type == QuestionType.FACTUAL:
            score -= 0.05  # Factual queries can be simpler
        
        return max(0.0, min(1.0, score))
    
    async def _generate_dimension_reasoning(self, dimension: QualityDimension, score: float, query: str) -> str:
        """Generate reasoning for dimension score"""
        
        if score >= 0.8:
            performance = "excellent"
        elif score >= 0.6:
            performance = "good"
        elif score >= 0.4:
            performance = "fair"
        else:
            performance = "needs improvement"
        
        dimension_name = dimension.value.replace('_', ' ')
        return f"Query shows {performance} {dimension_name} (score: {score:.2f})"
    
    def _calculate_grade(self, overall_score: float) -> str:
        """Calculate letter grade from overall score"""
        thresholds = self.config.get('grade_thresholds', {})
        
        for grade in ['A', 'B', 'C', 'D']:
            if overall_score >= thresholds.get(grade, 0):
                return grade
        
        return 'F'
    
    async def _identify_strengths(self, metrics: List[QualityMetric], query: str) -> List[str]:
        """Identify query strengths"""
        strengths = []
        
        # Find top performing dimensions
        sorted_metrics = sorted(metrics, key=lambda m: m.score, reverse=True)
        
        for metric in sorted_metrics[:3]:  # Top 3 dimensions
            if metric.score >= 0.7:
                dimension_name = metric.dimension.value.replace('_', ' ')
                strengths.append(f"Strong {dimension_name} ({metric.score:.2f})")
        
        # Specific strength patterns
        if len(query) > 50:
            strengths.append("Well-detailed query with sufficient context")
        
        if any(word in query.lower() for word in ['specific', 'detailed', 'comprehensive']):
            strengths.append("Uses specific language indicating clear requirements")
        
        return strengths
    
    async def _generate_improvement_suggestions(
        self, 
        metrics: List[QualityMetric], 
        query: str, 
        question_type: QuestionType
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        if not self.config.get('enable_improvement_suggestions', True):
            return suggestions
        
        # Find lowest performing dimensions
        sorted_metrics = sorted(metrics, key=lambda m: m.score)
        
        for metric in sorted_metrics[:2]:  # Bottom 2 dimensions
            if metric.score < 0.6:
                dimension = metric.dimension
                
                if dimension == QualityDimension.CLARITY:
                    if len(query) < 15:
                        suggestions.append("Consider providing more detail about your specific needs")
                    if any(word in query.lower() for word in ['thing', 'stuff', 'something']):
                        suggestions.append("Replace vague terms with specific descriptions")
                
                elif dimension == QualityDimension.ACTIONABILITY:
                    if question_type in [QuestionType.PROCEDURAL, QuestionType.CREATIVE]:
                        suggestions.append("Include what you want to accomplish or create")
                    else:
                        suggestions.append("Consider what action or outcome you're seeking")
                
                elif dimension == QualityDimension.COMPLETENESS:
                    suggestions.append("Add more context about your situation or constraints")
                    if question_type == QuestionType.COMPARATIVE:
                        suggestions.append("Specify the options you want to compare")
                
                elif dimension == QualityDimension.SPECIFICITY:
                    suggestions.append("Include specific names, numbers, or examples")
                    suggestions.append("Replace generic terms with precise descriptions")
        
        # General suggestions based on query length
        if len(query) < 10:
            suggestions.append("Expand your query with more detail and context")
        elif len(query) > 200:
            suggestions.append("Consider breaking complex queries into focused parts")
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    async def _calculate_confidence(
        self, 
        metrics: List[QualityMetric], 
        question_type: Optional[QuestionType], 
        domain: Optional[BusinessDomain]
    ) -> float:
        """Calculate confidence in the quality assessment"""
        
        # Base confidence from metric consistency
        scores = [m.score for m in metrics]
        if len(scores) > 1:
            score_variance = statistics.variance(scores)
            consistency_confidence = max(0.0, 1.0 - score_variance)
        else:
            consistency_confidence = 0.5
        
        # Question type confidence
        type_confidence = 0.8 if question_type and question_type != QuestionType.UNKNOWN else 0.4
        
        # Domain confidence
        domain_confidence = 0.7 if domain else 0.5
        
        # Combined confidence
        overall_confidence = (consistency_confidence * 0.5 + type_confidence * 0.3 + domain_confidence * 0.2)
        
        return min(overall_confidence, 1.0)
    
    def _update_metrics(self, assessment: QualityAssessment):
        """Update scoring metrics"""
        self.metrics['total_assessments'] += 1
        
        # Update grade distribution
        self.metrics['score_distribution'][assessment.grade] += 1
        
        # Update processing time
        self.metrics['avg_processing_time'] = (
            (self.metrics['avg_processing_time'] * (self.metrics['total_assessments'] - 1) + assessment.processing_time) /
            self.metrics['total_assessments']
        )
    
    async def batch_assess_quality(
        self,
        queries: List[str],
        question_types: Optional[List[QuestionType]] = None,
        domains: Optional[List[BusinessDomain]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[QualityAssessment]:
        """
        Assess quality of multiple queries in batch
        
        Args:
            queries: List of queries to assess
            question_types: Optional list of question types (aligned with queries)
            domains: Optional list of domains (aligned with queries)
            context: Optional shared context
            
        Returns:
            List of QualityAssessment objects
        """
        if not queries:
            return []
        
        self.logger.info(f"Batch assessing quality for {len(queries)} queries")
        
        try:
            # Prepare arguments for parallel processing
            tasks = []
            for i, query in enumerate(queries):
                question_type = question_types[i] if question_types and i < len(question_types) else None
                domain = domains[i] if domains and i < len(domains) else None
                
                tasks.append(self.assess_query_quality(query, question_type, domain, context))
            
            # Process in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch quality assessment failed for query {i}: {result}")
                    processed_results.append(QualityAssessment(
                        overall_score=0.0,
                        grade='F',
                        individual_metrics=[],
                        processing_time=0.0,
                        confidence_level=0.0,
                        improvement_suggestions=[f"Assessment error: {str(result)}"]
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch quality assessment failed: {e}")
            return [QualityAssessment(
                overall_score=0.0,
                grade='F',
                individual_metrics=[],
                processing_time=0.0,
                confidence_level=0.0,
                improvement_suggestions=["Batch processing failed"]
            ) for _ in queries]
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get comprehensive quality scoring metrics"""
        return {
            'total_assessments': self.metrics['total_assessments'],
            'average_processing_time': self.metrics['avg_processing_time'],
            'grade_distribution': dict(self.metrics['score_distribution']),
            'supported_dimensions': [dim.value for dim in QualityDimension],
            'supported_question_types': len(self.dimension_weights),
            'configuration': self.config
        }
    
    def get_dimension_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed definitions of quality dimensions"""
        return {
            'clarity': {
                'description': 'How clear and understandable the query is',
                'factors': ['specificity', 'language clarity', 'intent clarity'],
                'optimal_for': ['all query types']
            },
            'relevance': {
                'description': 'How relevant the query is to the intended domain or purpose',
                'factors': ['domain alignment', 'context appropriateness', 'topic relevance'],
                'optimal_for': ['domain-specific queries']
            },
            'completeness': {
                'description': 'Whether the query contains sufficient information',
                'factors': ['detail level', 'context provision', 'scope coverage'],
                'optimal_for': ['complex analytical queries']
            },
            'actionability': {
                'description': 'Whether the query leads to actionable outcomes',
                'factors': ['action orientation', 'implementation focus', 'practical utility'],
                'optimal_for': ['procedural and creative queries']
            },
            'accuracy': {
                'description': 'Factual correctness and logical consistency',
                'factors': ['factual accuracy', 'logical coherence', 'domain correctness'],
                'optimal_for': ['factual and analytical queries']
            },
            'specificity': {
                'description': 'How specific and precise the query is',
                'factors': ['precision level', 'concrete examples', 'measurable elements'],
                'optimal_for': ['technical and diagnostic queries']
            },
            'complexity': {
                'description': 'Appropriate level of complexity for the query type',
                'factors': ['conceptual depth', 'linguistic complexity', 'scope breadth'],
                'optimal_for': ['analytical and comparative queries']
            }
        }

# Global instance factory
_query_quality_scorer = None

async def get_query_quality_scorer(config: Optional[Dict[str, Any]] = None) -> QueryQualityScorer:
    """Get the global query quality scorer instance"""
    global _query_quality_scorer
    
    if _query_quality_scorer is None:
        _query_quality_scorer = QueryQualityScorer(config)
    
    return _query_quality_scorer