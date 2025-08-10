"""
Question Type Classifier - Advanced 6-type classification system

Classifies conversational queries into 6 distinct question types for optimized processing:
- Factual: Direct information requests  
- Analytical: Deep analysis and insights
- Comparative: Comparison-based queries
- Procedural: How-to and process queries
- Creative: Ideation and brainstorming  
- Diagnostic: Problem-solving queries

Designed for high-performance classification with <100ms response time.
"""

import asyncio
import logging
import re
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Enhanced 6-type question classification"""
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"
    CREATIVE = "creative"
    DIAGNOSTIC = "diagnostic"
    UNKNOWN = "unknown"

@dataclass
class ClassificationResult:
    """Result of question type classification"""
    question_type: QuestionType
    confidence_score: float
    reasoning: str
    alternative_types: List[Tuple[QuestionType, float]] = field(default_factory=list)
    processing_time: float = 0.0
    patterns_matched: List[str] = field(default_factory=list)

@dataclass
class ClassificationMetrics:
    """Classification performance metrics"""
    total_classifications: int = 0
    accuracy_by_type: Dict[str, float] = field(default_factory=dict)
    avg_confidence: float = 0.0
    avg_processing_time: float = 0.0
    pattern_effectiveness: Dict[str, float] = field(default_factory=dict)

class QuestionTypeClassifier:
    """
    Advanced 6-type question classification system with high-performance pattern matching.
    
    Uses sophisticated regex patterns, semantic analysis, and confidence scoring to
    classify queries into the optimal question type for processing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the question type classifier"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Classification patterns for each question type
        self.classification_patterns = self._initialize_patterns()
        
        # Performance metrics
        self.metrics = ClassificationMetrics()
        
        # Semantic keywords for enhanced classification
        self.semantic_keywords = self._initialize_semantic_keywords()
        
        self.logger.info("Question Type Classifier initialized with 6-type system")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the classifier"""
        return {
            'confidence_threshold': 0.6,
            'enable_semantic_analysis': True,
            'enable_alternative_ranking': True,
            'max_alternatives': 3,
            'pattern_weights': {
                'primary': 1.0,
                'secondary': 0.7,
                'contextual': 0.5
            }
        }
    
    def _initialize_patterns(self) -> Dict[QuestionType, Dict[str, List[str]]]:
        """Initialize comprehensive classification patterns"""
        return {
            QuestionType.FACTUAL: {
                'primary': [
                    r'\b(what is|what are|what was|what were)\b',
                    r'\b(who is|who are|who was|who were)\b',
                    r'\b(when is|when was|when will|when did)\b',
                    r'\b(where is|where are|where was|where were)\b',
                    r'\b(which is|which are|which was|which were)\b',
                    r'\b(how much|how many|how often)\b'
                ],
                'secondary': [
                    r'\b(define|definition of|meaning of)\b',
                    r'\b(tell me about|information about|details about)\b',
                    r'\b(facts about|data on|statistics)\b',
                    r'\b(list of|examples of|types of)\b'
                ],
                'contextual': [
                    r'\b(company|organization|brand).+\b(founded|established|created)\b',
                    r'\b(price|cost|rate|fee).+\bof\b',
                    r'\b(location|address|headquarters)\b'
                ]
            },
            QuestionType.ANALYTICAL: {
                'primary': [
                    r'\b(why does|why is|why are|why did|why do)\b',
                    r'\b(how does|how is|how are|how did|how do)\b',
                    r'\b(analyze|analysis|examine|investigate)\b',
                    r'\b(implications|impact|effect|consequences)\b',
                    r'\b(trends|patterns|insights|drivers)\b'
                ],
                'secondary': [
                    r'\b(cause|reason|factor|influence|correlation)\b',
                    r'\b(deep dive|in-depth|comprehensive review)\b',
                    r'\b(understand|explain|clarify|breakdown)\b',
                    r'\b(relationship between|connection between)\b'
                ],
                'contextual': [
                    r'\b(market|industry|business).+\b(analysis|research|study)\b',
                    r'\b(performance|metrics|kpi).+\b(analysis|review)\b',
                    r'\b(root cause|underlying|fundamental)\b'
                ]
            },
            QuestionType.COMPARATIVE: {
                'primary': [
                    r'\b(compare|comparison|contrast|versus|vs\.?)\b',
                    r'\b(better|best|worse|worst|superior|inferior)\b',
                    r'\b(difference|differences|similar|similarities)\b',
                    r'\b(alternative|alternatives|option|options)\b',
                    r'\bwhich.+\b(better|best|prefer|choose|recommend)\b'
                ],
                'secondary': [
                    r'\b(pros and cons|advantages|disadvantages|benefits|drawbacks)\b',
                    r'\b(competition|competitive|competitor|rivals)\b',
                    r'\b(benchmark|benchmarking|evaluate|assessment)\b',
                    r'\b(rank|ranking|rate|rating|score|scoring)\b'
                ],
                'contextual': [
                    r'\bA\b.+\b(vs|versus|compared to|against)\b.+\bB\b',
                    r'\b(product|service|solution).+\b(comparison|competitive)\b',
                    r'\b(choose between|decision between|select from)\b'
                ]
            },
            QuestionType.PROCEDURAL: {
                'primary': [
                    r'\b(how to|how do I|how can I|how should I)\b',
                    r'\b(steps|process|procedure|method|approach)\b',
                    r'\b(guide|tutorial|instructions|directions)\b',
                    r'\b(create|build|make|develop|implement)\b',
                    r'\b(setup|configure|install|deploy)\b'
                ],
                'secondary': [
                    r'\b(workflow|framework|methodology|strategy)\b',
                    r'\b(plan|planning|roadmap|timeline)\b',
                    r'\b(best practices|recommendations|guidelines)\b',
                    r'\b(checklist|requirements|prerequisites)\b'
                ],
                'contextual': [
                    r'\b(getting started|begin|start|initiate)\b',
                    r'\b(step-by-step|walkthrough|guide)\b',
                    r'\b(implementation|execution|deployment)\b'
                ]
            },
            QuestionType.CREATIVE: {
                'primary': [
                    r'\b(generate|create|design|develop|build)\b',
                    r'\b(ideas|concepts|suggestions|recommendations)\b',
                    r'\b(brainstorm|ideate|innovate|invent)\b',
                    r'\b(content|copy|text|article|blog)\b',
                    r'\b(creative|original|unique|novel)\b'
                ],
                'secondary': [
                    r'\b(template|format|structure|outline)\b',
                    r'\b(campaign|strategy|plan|concept)\b',
                    r'\b(inspiration|inspire|motivate)\b',
                    r'\b(write|compose|craft|produce)\b'
                ],
                'contextual': [
                    r'\b(marketing|advertising|promotional).+\b(content|campaign)\b',
                    r'\b(social media|blog|website).+\b(content|post)\b',
                    r'\b(creative brief|brand voice|messaging)\b'
                ]
            },
            QuestionType.DIAGNOSTIC: {
                'primary': [
                    r'\b(problem|issue|error|bug|fault)\b',
                    r'\b(fix|solve|repair|resolve|correct)\b',
                    r'\b(troubleshoot|debug|diagnose|identify)\b',
                    r'\b(not working|broken|failing|error)\b',
                    r'\b(why.+not|what.+wrong|how.+fix)\b'
                ],
                'secondary': [
                    r'\b(optimize|improve|enhance|upgrade)\b',
                    r'\b(performance|slow|speed|efficiency)\b',
                    r'\b(warning|alert|notification|message)\b',
                    r'\b(recovery|restore|backup|rollback)\b'
                ],
                'contextual': [
                    r'\b(system|application|website|software).+\b(down|offline|unavailable)\b',
                    r'\b(error message|error code|exception)\b',
                    r'\b(maintenance|monitoring|health check)\b'
                ]
            }
        }
    
    def _initialize_semantic_keywords(self) -> Dict[QuestionType, List[str]]:
        """Initialize semantic keywords for enhanced classification"""
        return {
            QuestionType.FACTUAL: [
                'information', 'data', 'statistics', 'facts', 'details', 'documentation',
                'specification', 'description', 'profile', 'overview', 'summary'
            ],
            QuestionType.ANALYTICAL: [
                'analysis', 'research', 'study', 'investigation', 'examination', 'insight',
                'trend', 'pattern', 'correlation', 'causation', 'hypothesis', 'theory'
            ],
            QuestionType.COMPARATIVE: [
                'comparison', 'evaluation', 'assessment', 'benchmark', 'alternative',
                'competitor', 'option', 'choice', 'selection', 'preference', 'recommendation'
            ],
            QuestionType.PROCEDURAL: [
                'process', 'procedure', 'method', 'approach', 'workflow', 'framework',
                'methodology', 'strategy', 'implementation', 'execution', 'deployment'
            ],
            QuestionType.CREATIVE: [
                'creative', 'original', 'innovative', 'unique', 'novel', 'artistic',
                'design', 'content', 'campaign', 'concept', 'idea', 'inspiration'
            ],
            QuestionType.DIAGNOSTIC: [
                'problem', 'issue', 'error', 'bug', 'troubleshooting', 'debugging',
                'optimization', 'performance', 'maintenance', 'monitoring', 'health'
            ]
        }
    
    async def classify_question(self, query: str, context: Optional[Dict[str, Any]] = None) -> ClassificationResult:
        """
        Classify a query into one of 6 question types
        
        Args:
            query: The natural language query to classify
            context: Optional context information to improve classification
            
        Returns:
            ClassificationResult with type, confidence, and reasoning
        """
        start_time = time.time()
        
        try:
            if not query or not query.strip():
                return ClassificationResult(
                    question_type=QuestionType.UNKNOWN,
                    confidence_score=0.0,
                    reasoning="Empty or invalid query",
                    processing_time=time.time() - start_time
                )
            
            query = query.strip().lower()
            self.logger.debug(f"Classifying query: '{query[:50]}...'")
            
            # Calculate scores for each question type
            type_scores = {}
            matched_patterns = {}
            
            for question_type in QuestionType:
                if question_type == QuestionType.UNKNOWN:
                    continue
                    
                score, patterns = await self._calculate_type_score(query, question_type, context)
                type_scores[question_type] = score
                matched_patterns[question_type] = patterns
            
            # Find best match
            if not type_scores:
                return ClassificationResult(
                    question_type=QuestionType.UNKNOWN,
                    confidence_score=0.0,
                    reasoning="No patterns matched",
                    processing_time=time.time() - start_time
                )
            
            # Sort by score
            sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
            best_type, best_score = sorted_types[0]
            
            # Generate alternatives if requested
            alternatives = []
            if self.config.get('enable_alternative_ranking', True):
                max_alternatives = self.config.get('max_alternatives', 3)
                for question_type, score in sorted_types[1:max_alternatives+1]:
                    if score >= self.config.get('confidence_threshold', 0.6) * 0.8:  # 80% of threshold
                        alternatives.append((question_type, score))
            
            # Generate reasoning
            reasoning = await self._generate_reasoning(query, best_type, best_score, matched_patterns.get(best_type, []))
            
            # Update metrics
            self.metrics.total_classifications += 1
            self.metrics.avg_confidence = (
                (self.metrics.avg_confidence * (self.metrics.total_classifications - 1) + best_score) /
                self.metrics.total_classifications
            )
            
            processing_time = time.time() - start_time
            self.metrics.avg_processing_time = (
                (self.metrics.avg_processing_time * (self.metrics.total_classifications - 1) + processing_time) /
                self.metrics.total_classifications
            )
            
            result = ClassificationResult(
                question_type=best_type,
                confidence_score=best_score,
                reasoning=reasoning,
                alternative_types=alternatives,
                processing_time=processing_time,
                patterns_matched=matched_patterns.get(best_type, [])
            )
            
            self.logger.info(f"Classified as {best_type.value} with confidence {best_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            return ClassificationResult(
                question_type=QuestionType.UNKNOWN,
                confidence_score=0.0,
                reasoning=f"Classification error: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    async def _calculate_type_score(
        self, 
        query: str, 
        question_type: QuestionType, 
        context: Optional[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """Calculate confidence score for a specific question type"""
        
        if question_type not in self.classification_patterns:
            return 0.0, []
        
        patterns = self.classification_patterns[question_type]
        matched_patterns = []
        total_score = 0.0
        
        # Pattern matching with weights
        pattern_weights = self.config.get('pattern_weights', {})
        
        for weight_type, pattern_list in patterns.items():
            weight = pattern_weights.get(weight_type, 1.0)
            
            for pattern in pattern_list:
                try:
                    if re.search(pattern, query, re.IGNORECASE):
                        pattern_score = weight * (1.0 / len(pattern_list))  # Normalize by pattern count
                        total_score += pattern_score
                        matched_patterns.append(f"{weight_type}:{pattern}")
                        
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern {pattern}: {e}")
                    continue
        
        # Semantic keyword analysis
        if self.config.get('enable_semantic_analysis', True):
            semantic_bonus = await self._calculate_semantic_score(query, question_type)
            total_score += semantic_bonus
        
        # Context boost
        if context:
            context_boost = await self._calculate_context_boost(query, question_type, context)
            total_score += context_boost
        
        # Normalize score to 0-1 range
        normalized_score = min(total_score, 1.0)
        
        return normalized_score, matched_patterns
    
    async def _calculate_semantic_score(self, query: str, question_type: QuestionType) -> float:
        """Calculate semantic similarity bonus"""
        if question_type not in self.semantic_keywords:
            return 0.0
        
        keywords = self.semantic_keywords[question_type]
        matches = 0
        
        for keyword in keywords:
            if keyword in query:
                matches += 1
        
        # Semantic bonus: 0.1 per keyword match, max 0.3
        return min(matches * 0.1, 0.3)
    
    async def _calculate_context_boost(
        self, 
        query: str, 
        question_type: QuestionType, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate context-based confidence boost"""
        boost = 0.0
        
        # Previous question type context
        if 'previous_type' in context:
            previous_type = context['previous_type']
            if previous_type == question_type:
                boost += 0.1  # Conversation continuity bonus
        
        # Domain context
        if 'domain' in context:
            domain = context['domain'].lower()
            
            # Domain-specific boosts
            domain_boosts = {
                QuestionType.ANALYTICAL: ['business', 'research', 'analytics'],
                QuestionType.PROCEDURAL: ['technology', 'implementation', 'operations'],
                QuestionType.CREATIVE: ['marketing', 'content', 'design'],
                QuestionType.DIAGNOSTIC: ['technical', 'support', 'troubleshooting']
            }
            
            if question_type in domain_boosts:
                for domain_keyword in domain_boosts[question_type]:
                    if domain_keyword in domain:
                        boost += 0.05
        
        return min(boost, 0.2)  # Max 0.2 context boost
    
    async def _generate_reasoning(
        self, 
        query: str, 
        question_type: QuestionType, 
        confidence: float, 
        patterns: List[str]
    ) -> str:
        """Generate human-readable reasoning for the classification"""
        
        type_descriptions = {
            QuestionType.FACTUAL: "seeking direct information or facts",
            QuestionType.ANALYTICAL: "requiring deep analysis or insights",
            QuestionType.COMPARATIVE: "comparing options or alternatives",
            QuestionType.PROCEDURAL: "asking for step-by-step guidance",
            QuestionType.CREATIVE: "requesting creative content or ideas",
            QuestionType.DIAGNOSTIC: "identifying or solving problems"
        }
        
        base_reason = f"Classified as {question_type.value} ({type_descriptions.get(question_type, 'unknown type')})"
        
        if confidence >= 0.8:
            confidence_level = "high confidence"
        elif confidence >= 0.6:
            confidence_level = "moderate confidence"
        else:
            confidence_level = "low confidence"
        
        if patterns:
            pattern_info = f" based on {len(patterns)} matched patterns"
        else:
            pattern_info = " based on semantic analysis"
        
        return f"{base_reason} with {confidence_level}{pattern_info}."
    
    async def batch_classify(
        self, 
        queries: List[str], 
        context: Optional[Dict[str, Any]] = None
    ) -> List[ClassificationResult]:
        """
        Classify multiple queries in batch for high performance
        
        Args:
            queries: List of queries to classify
            context: Optional shared context for all queries
            
        Returns:
            List of ClassificationResult objects
        """
        start_time = time.time()
        
        try:
            if not queries:
                return []
            
            self.logger.info(f"Batch classifying {len(queries)} queries")
            
            # Process queries in parallel
            tasks = [self.classify_question(query, context) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Batch classification failed for query {i}: {result}")
                    processed_results.append(ClassificationResult(
                        question_type=QuestionType.UNKNOWN,
                        confidence_score=0.0,
                        reasoning=f"Batch processing error: {str(result)}",
                        processing_time=0.0
                    ))
                else:
                    processed_results.append(result)
            
            batch_time = time.time() - start_time
            self.logger.info(f"Batch classification completed in {batch_time:.3f}s")
            
            return processed_results
            
        except Exception as e:
            self.logger.error(f"Batch classification failed: {e}")
            return [ClassificationResult(
                question_type=QuestionType.UNKNOWN,
                confidence_score=0.0,
                reasoning="Batch processing failed",
                processing_time=0.0
            ) for _ in queries]
    
    def get_classification_metrics(self) -> Dict[str, Any]:
        """Get comprehensive classification performance metrics"""
        return {
            'total_classifications': self.metrics.total_classifications,
            'average_confidence': self.metrics.avg_confidence,
            'average_processing_time': self.metrics.avg_processing_time,
            'accuracy_by_type': dict(self.metrics.accuracy_by_type),
            'pattern_effectiveness': dict(self.metrics.pattern_effectiveness),
            'supported_types': [qtype.value for qtype in QuestionType if qtype != QuestionType.UNKNOWN],
            'configuration': self.config
        }
    
    def get_type_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed definitions of all question types"""
        return {
            'factual': {
                'description': 'Direct information requests seeking specific facts, data, or details',
                'examples': [
                    'What is the population of New York?',
                    'When was Microsoft founded?',
                    'Who is the CEO of Tesla?',
                    'How much does this product cost?'
                ],
                'optimal_for': ['data lookup', 'fact verification', 'basic information needs']
            },
            'analytical': {
                'description': 'Deep analysis queries requiring insights, trends, or understanding',
                'examples': [
                    'Why is customer retention decreasing?',
                    'What are the implications of this market trend?',
                    'Analyze the performance of our marketing campaigns',
                    'How does inflation affect consumer behavior?'
                ],
                'optimal_for': ['business intelligence', 'research', 'strategic planning']
            },
            'comparative': {
                'description': 'Comparison-based queries evaluating options, alternatives, or differences',
                'examples': [
                    'Compare React vs Vue for our project',
                    'Which is better: email or social media marketing?',
                    'What are the pros and cons of remote work?',
                    'Evaluate different CRM solutions'
                ],
                'optimal_for': ['decision making', 'vendor selection', 'option evaluation']
            },
            'procedural': {
                'description': 'How-to queries seeking step-by-step guidance or processes',
                'examples': [
                    'How to set up a Google Ads campaign?',
                    'What are the steps to implement SEO?',
                    'Create a workflow for customer onboarding',
                    'Guide me through database migration'
                ],
                'optimal_for': ['implementation', 'training', 'process documentation']
            },
            'creative': {
                'description': 'Creative queries requesting original content, ideas, or designs',
                'examples': [
                    'Generate blog post ideas for our company',
                    'Create a social media campaign concept',
                    'Write product descriptions for our catalog',
                    'Design an email template layout'
                ],
                'optimal_for': ['content creation', 'marketing campaigns', 'brainstorming']
            },
            'diagnostic': {
                'description': 'Problem-solving queries focused on identifying and fixing issues',
                'examples': [
                    'Why is our website loading slowly?',
                    'Fix the email delivery problem',
                    'Troubleshoot database connection issues',
                    'Optimize application performance'
                ],
                'optimal_for': ['technical support', 'optimization', 'problem resolution']
            }
        }

# Global instance factory
_question_type_classifier = None

async def get_question_type_classifier(config: Optional[Dict[str, Any]] = None) -> QuestionTypeClassifier:
    """Get the global question type classifier instance"""
    global _question_type_classifier
    
    if _question_type_classifier is None:
        _question_type_classifier = QuestionTypeClassifier(config)
    
    return _question_type_classifier