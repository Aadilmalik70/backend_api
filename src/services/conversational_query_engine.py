"""
Conversational Query Engine - Intelligent natural language query processing

Advanced conversational AI system for SERP Strategist that processes natural language queries
and converts them into actionable search intents with context-aware understanding.

Features:
- Natural language intent recognition with spaCy and transformers
- Context-aware query understanding with conversation history
- Parallel processing of query components with AI Manager integration
- Semantic search intent classification and parameter extraction
- Real-time query enhancement using Knowledge Graph entities
- Advanced caching for rapid query processing
- Multi-turn conversation memory and context retention

Designed for production deployment with P0 priority requirements.
"""

import asyncio
import hashlib
import logging
import time
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from enum import Enum
import re

# Import AI infrastructure dependencies
from services.ai.ai_manager import ai_manager
from services.nlp_processor import NLPProcessor
from utils.google_apis.knowledge_graph_client import get_knowledge_graph_client
from utils.advanced_cache_manager import get_global_cache_manager, ultra_cache

logger = logging.getLogger(__name__)

class QueryIntent(Enum):
    """Enumeration of supported query intents"""
    KEYWORD_RESEARCH = "keyword_research"
    COMPETITOR_ANALYSIS = "competitor_analysis" 
    CONTENT_STRATEGY = "content_strategy"
    SEO_OPTIMIZATION = "seo_optimization"
    MARKET_ANALYSIS = "market_analysis"
    BLUEPRINT_GENERATION = "blueprint_generation"
    ENTITY_RESEARCH = "entity_research"
    TREND_ANALYSIS = "trend_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    UNKNOWN = "unknown"

class QueryContext(Enum):
    """Query context types for conversation flow"""
    NEW_SESSION = "new_session"
    FOLLOW_UP = "follow_up"
    CLARIFICATION = "clarification"
    REFINEMENT = "refinement"
    EXPANSION = "expansion"

@dataclass
class ConversationTurn:
    """Individual conversation turn with query and response"""
    turn_id: str
    user_query: str
    intent: QueryIntent
    context: QueryContext
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ConversationSession:
    """Complete conversation session with history and context"""
    session_id: str
    user_id: Optional[str] = None
    turns: List[ConversationTurn] = field(default_factory=list)
    active_context: Dict[str, Any] = field(default_factory=dict)
    session_intent: Optional[QueryIntent] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def add_turn(self, turn: ConversationTurn):
        """Add a new turn to the conversation"""
        self.turns.append(turn)
        self.last_activity = datetime.utcnow()
        
        # Update session context
        if turn.intent != QueryIntent.UNKNOWN:
            self.session_intent = turn.intent
        
        # Maintain active context from latest turns
        if turn.extracted_entities:
            self.active_context['entities'] = turn.extracted_entities
        if turn.parameters:
            self.active_context.update(turn.parameters)

@dataclass 
class QueryProcessingResult:
    """Complete query processing result"""
    intent: QueryIntent
    context: QueryContext
    confidence_score: float
    extracted_entities: List[Dict[str, Any]]
    parameters: Dict[str, Any]
    suggested_actions: List[str]
    enhanced_query: str
    processing_metrics: Dict[str, Any]
    conversation_context: Optional[Dict[str, Any]] = None

class ConversationalQueryEngine:
    """
    Advanced conversational query processing engine with AI integration
    
    Processes natural language queries through multiple AI services in parallel,
    extracts intents and entities, and provides contextual understanding for
    multi-turn conversations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the conversational query engine"""
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        
        # Initialize AI components
        self.ai_manager = ai_manager
        self.nlp_processor = None
        self.knowledge_graph_client = get_knowledge_graph_client()
        self.cache_manager = get_global_cache_manager()
        
        # Conversation management
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.session_ttl = timedelta(hours=self.config.get('session_ttl_hours', 24))
        
        # Intent patterns for classification
        self.intent_patterns = self._initialize_intent_patterns()
        
        # Performance metrics
        self.metrics = {
            'total_queries_processed': 0,
            'intent_classification_accuracy': 0.0,
            'avg_processing_time': 0.0,
            'cache_hit_rate': 0.0,
            'conversation_sessions': 0
        }
        
        self.logger.info("Conversational Query Engine initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the query engine"""
        return {
            'max_conversation_turns': 20,
            'session_ttl_hours': 24,
            'intent_confidence_threshold': 0.7,
            'entity_confidence_threshold': 0.6,
            'enable_conversation_memory': True,
            'enable_query_enhancement': True,
            'parallel_processing': True,
            'cache_query_results': True,
            'max_entities_per_query': 10
        }
    
    def _initialize_intent_patterns(self) -> Dict[QueryIntent, List[str]]:
        """Initialize intent classification patterns"""
        return {
            QueryIntent.KEYWORD_RESEARCH: [
                r'\b(keyword|keywords?|search terms?|key phrases?)\b',
                r'\b(find|research|discover).+\b(words?|terms?)\b',
                r'\b(what|which).+\b(keywords?|phrases?)\b'
            ],
            QueryIntent.COMPETITOR_ANALYSIS: [
                r'\b(competitor|competition|rival|competing)\b',
                r'\b(analyze|compare|benchmark).+\b(competitors?|rivals?)\b',
                r'\bwho are?.+\b(competitors?|rivals?)\b'
            ],
            QueryIntent.CONTENT_STRATEGY: [
                r'\b(content|article|blog|post).+\b(strategy|plan|ideas?)\b',
                r'\b(create|write|develop).+\b(content|articles?)\b',
                r'\b(content|editorial).+\b(calendar|planning)\b'
            ],
            QueryIntent.SEO_OPTIMIZATION: [
                r'\b(seo|optimization|optimize|ranking)\b',
                r'\b(improve|boost|increase).+\b(ranking|visibility)\b',
                r'\b(search engine|google).+\b(optimization|ranking)\b'
            ],
            QueryIntent.MARKET_ANALYSIS: [
                r'\b(market|industry|sector).+\b(analysis|research|trends?)\b',
                r'\b(analyze|study).+\b(market|industry)\b',
                r'\bmarket.+\b(size|share|opportunities?)\b'
            ],
            QueryIntent.BLUEPRINT_GENERATION: [
                r'\b(blueprint|template|structure|outline)\b',
                r'\b(generate|create|build).+\b(blueprint|template)\b',
                r'\b(content|article).+\b(blueprint|structure)\b'
            ],
            QueryIntent.ENTITY_RESEARCH: [
                r'\b(company|brand|organization).+\b(information|details?|research)\b',
                r'\btell me about\b.+\b(company|brand)\b',
                r'\bwhat is\b.+\b(company|organization)\b'
            ],
            QueryIntent.TREND_ANALYSIS: [
                r'\b(trend|trending|popular|hot)\b',
                r'\bwhat\'?s.+\b(trending|popular|hot)\b',
                r'\b(current|latest).+\b(trends?|topics?)\b'
            ],
            QueryIntent.PERFORMANCE_ANALYSIS: [
                r'\b(performance|analytics|metrics|stats)\b',
                r'\bhow.+\b(performing|doing)\b',
                r'\b(track|measure|analyze).+\b(performance|results?)\b'
            ]
        }
    
    async def initialize(self) -> bool:
        """Initialize all AI components and services"""
        try:
            self.logger.info("🚀 Initializing Conversational Query Engine components...")
            
            # Initialize AI Manager services
            if not await self.ai_manager.initialize_services():
                self.logger.warning("AI Manager initialization incomplete - some features may be limited")
            
            # Initialize NLP Processor
            try:
                self.nlp_processor = NLPProcessor()
                if hasattr(self.nlp_processor, 'initialize'):
                    await self.nlp_processor.initialize()
                self.logger.info("✅ NLP Processor initialized")
            except Exception as e:
                self.logger.warning(f"NLP Processor initialization failed: {e}")
                self.nlp_processor = None
            
            # Validate Knowledge Graph client
            if self.knowledge_graph_client:
                health = await self.knowledge_graph_client.health_check()
                if health.get('status') in ['healthy', 'warning']:
                    self.logger.info("✅ Knowledge Graph client available")
                else:
                    self.logger.warning("⚠️ Knowledge Graph client has issues")
            
            self.logger.info("✅ Conversational Query Engine initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Initialization failed: {e}")
            return False
    
    async def process_query(
        self,
        user_query: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None
    ) -> QueryProcessingResult:
        """
        Process a conversational query with full AI pipeline
        
        Args:
            user_query: Natural language query from user
            session_id: Conversation session identifier
            user_id: User identifier for personalization
            context_data: Additional context information
            
        Returns:
            Complete query processing result with intent, entities, and actions
        """
        start_time = time.time()
        
        try:
            # Clean and validate input
            if not user_query or not user_query.strip():
                raise ValueError("Empty query provided")
            
            user_query = user_query.strip()
            if len(user_query) > 10000:  # Limit query length
                user_query = user_query[:10000]
            
            self.logger.debug(f"Processing query: '{user_query[:100]}...' (Session: {session_id})")
            
            # Get or create conversation session
            session = await self._get_or_create_session(session_id, user_id)
            
            # Check cache first
            cache_key = self._generate_cache_key(user_query, session.session_id if session else None)
            if self.config.get('cache_query_results', True):
                cached_result = await self._get_cached_result(cache_key)
                if cached_result:
                    self.logger.debug(f"Cache hit for query: {cache_key[:16]}...")
                    self.metrics['cache_hit_rate'] = (self.metrics.get('cache_hit_rate', 0) * 0.9 + 0.1)
                    return QueryProcessingResult(**cached_result)
            
            # Parallel processing of query components
            if self.config.get('parallel_processing', True):
                processing_result = await self._process_query_parallel(
                    user_query, session, context_data
                )
            else:
                processing_result = await self._process_query_sequential(
                    user_query, session, context_data
                )
            
            # Create conversation turn
            turn = ConversationTurn(
                turn_id=self._generate_turn_id(),
                user_query=user_query,
                intent=processing_result.intent,
                context=processing_result.context,
                extracted_entities=processing_result.extracted_entities,
                parameters=processing_result.parameters,
                confidence_score=processing_result.confidence_score,
                processing_time=time.time() - start_time
            )
            
            # Update session
            if session:
                session.add_turn(turn)
                await self._update_session_cache(session)
            
            # Cache result
            if self.config.get('cache_query_results', True):
                await self._cache_result(cache_key, asdict(processing_result))
            
            # Update metrics
            self.metrics['total_queries_processed'] += 1
            self.metrics['avg_processing_time'] = (
                (self.metrics.get('avg_processing_time', 0) * 0.9) + 
                (processing_result.processing_metrics.get('total_time', 0) * 0.1)
            )
            
            self.logger.info(f"Query processed successfully in {time.time() - start_time:.3f}s")
            return processing_result
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            # Return fallback result
            return QueryProcessingResult(
                intent=QueryIntent.UNKNOWN,
                context=QueryContext.NEW_SESSION,
                confidence_score=0.0,
                extracted_entities=[],
                parameters={},
                suggested_actions=["Please rephrase your query"],
                enhanced_query=user_query,
                processing_metrics={'error': str(e), 'total_time': time.time() - start_time}
            )
    
    async def _process_query_parallel(
        self,
        user_query: str,
        session: Optional[ConversationSession],
        context_data: Optional[Dict[str, Any]]
    ) -> QueryProcessingResult:
        """Process query using parallel AI services"""
        
        processing_start = time.time()
        
        # Prepare parallel processing tasks
        tasks = []
        
        # Intent classification task
        tasks.append(('intent', self._classify_intent(user_query, session)))
        
        # Entity extraction task
        if self.nlp_processor:
            tasks.append(('entities', self._extract_entities_nlp(user_query)))
        
        # Context analysis task
        tasks.append(('context', self._analyze_context(user_query, session)))
        
        # Knowledge Graph enhancement task (if entities expected)  
        if self.config.get('enable_query_enhancement', True):
            tasks.append(('kg_enhancement', self._enhance_with_knowledge_graph(user_query)))
        
        # Execute tasks in parallel
        results = {}
        try:
            task_results = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for (task_name, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    self.logger.warning(f"Task {task_name} failed: {result}")
                    results[task_name] = None
                else:
                    results[task_name] = result
                    
        except Exception as e:
            self.logger.error(f"Parallel processing failed: {e}")
            results = {}
        
        # Combine results
        intent_result = results.get('intent', (QueryIntent.UNKNOWN, 0.0))
        entities_result = results.get('entities', [])
        context_result = results.get('context', QueryContext.NEW_SESSION)
        kg_result = results.get('kg_enhancement', {})
        
        # Extract components
        intent, intent_confidence = intent_result if isinstance(intent_result, tuple) else (intent_result, 0.0)
        extracted_entities = entities_result if isinstance(entities_result, list) else []
        
        # Generate parameters and actions
        parameters = await self._extract_parameters(user_query, intent, extracted_entities)
        suggested_actions = await self._generate_suggested_actions(intent, parameters, extracted_entities)
        enhanced_query = await self._enhance_query(user_query, kg_result)
        
        processing_time = time.time() - processing_start
        
        return QueryProcessingResult(
            intent=intent,
            context=context_result,
            confidence_score=intent_confidence,
            extracted_entities=extracted_entities,
            parameters=parameters,
            suggested_actions=suggested_actions,
            enhanced_query=enhanced_query,
            processing_metrics={
                'total_time': processing_time,
                'parallel_tasks': len(tasks),
                'successful_tasks': len([r for r in results.values() if r is not None]),
                'kg_enhancement': kg_result is not None
            },
            conversation_context=session.active_context if session else None
        )
    
    async def _process_query_sequential(
        self,
        user_query: str,
        session: Optional[ConversationSession],
        context_data: Optional[Dict[str, Any]]
    ) -> QueryProcessingResult:
        """Process query using sequential AI services"""
        
        processing_start = time.time()
        
        # Sequential processing
        intent, intent_confidence = await self._classify_intent(user_query, session)
        extracted_entities = await self._extract_entities_nlp(user_query) if self.nlp_processor else []
        context_result = await self._analyze_context(user_query, session)
        
        # Knowledge Graph enhancement
        kg_result = {}
        if self.config.get('enable_query_enhancement', True):
            kg_result = await self._enhance_with_knowledge_graph(user_query)
        
        # Generate parameters and actions
        parameters = await self._extract_parameters(user_query, intent, extracted_entities)
        suggested_actions = await self._generate_suggested_actions(intent, parameters, extracted_entities)
        enhanced_query = await self._enhance_query(user_query, kg_result)
        
        processing_time = time.time() - processing_start
        
        return QueryProcessingResult(
            intent=intent,
            context=context_result,
            confidence_score=intent_confidence,
            extracted_entities=extracted_entities,
            parameters=parameters,
            suggested_actions=suggested_actions,
            enhanced_query=enhanced_query,
            processing_metrics={
                'total_time': processing_time,
                'sequential_processing': True,
                'kg_enhancement': bool(kg_result)
            },
            conversation_context=session.active_context if session else None
        )
    
    async def _classify_intent(
        self, 
        user_query: str, 
        session: Optional[ConversationSession]
    ) -> Tuple[QueryIntent, float]:
        """Classify user query intent using pattern matching and ML"""
        
        try:
            query_lower = user_query.lower()
            intent_scores = {}
            
            # Pattern-based classification
            for intent, patterns in self.intent_patterns.items():
                score = 0.0
                for pattern in patterns:
                    if re.search(pattern, query_lower, re.IGNORECASE):
                        score += 1.0
                
                if score > 0:
                    intent_scores[intent] = score / len(patterns)
            
            # Consider session context
            if session and session.session_intent and session.session_intent != QueryIntent.UNKNOWN:
                # Boost related intents based on conversation history
                context_boost = 0.2
                if session.session_intent in intent_scores:
                    intent_scores[session.session_intent] += context_boost
            
            # Get best intent
            if intent_scores:
                best_intent = max(intent_scores, key=intent_scores.get)
                confidence = min(intent_scores[best_intent], 1.0)
                
                if confidence >= self.config.get('intent_confidence_threshold', 0.7):
                    return best_intent, confidence
            
            return QueryIntent.UNKNOWN, 0.0
            
        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}")
            return QueryIntent.UNKNOWN, 0.0
    
    async def _extract_entities_nlp(self, user_query: str) -> List[Dict[str, Any]]:
        """Extract entities using NLP processor"""
        
        try:
            if not self.nlp_processor:
                return []
            
            # Process with spaCy
            spacy_result = await self.nlp_processor.process_text_spacy(user_query)
            
            entities = []
            if spacy_result and 'entities' in spacy_result:
                for entity in spacy_result['entities'][:self.config.get('max_entities_per_query', 10)]:
                    if entity.get('confidence', 0) >= self.config.get('entity_confidence_threshold', 0.6):
                        entities.append({
                            'text': entity.get('text', ''),
                            'label': entity.get('label', ''),
                            'confidence': entity.get('confidence', 0.0),
                            'start': entity.get('start', 0),
                            'end': entity.get('end', 0),
                            'source': 'spacy'
                        })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}")
            return []
    
    async def _analyze_context(
        self, 
        user_query: str, 
        session: Optional[ConversationSession]
    ) -> QueryContext:
        """Analyze query context based on conversation history"""
        
        try:
            if not session or not session.turns:
                return QueryContext.NEW_SESSION
            
            # Context indicators
            follow_up_indicators = [
                'also', 'additionally', 'furthermore', 'moreover', 'and', 'plus'
            ]
            
            clarification_indicators = [
                'what do you mean', 'can you explain', 'clarify', 'i don\'t understand'
            ]
            
            refinement_indicators = [
                'instead', 'actually', 'rather', 'modify', 'change', 'adjust'
            ]
            
            expansion_indicators = [
                'more details', 'elaborate', 'expand', 'tell me more', 'deeper'
            ]
            
            query_lower = user_query.lower()
            
            # Check for context indicators
            if any(indicator in query_lower for indicator in clarification_indicators):
                return QueryContext.CLARIFICATION
            elif any(indicator in query_lower for indicator in refinement_indicators):
                return QueryContext.REFINEMENT
            elif any(indicator in query_lower for indicator in expansion_indicators):
                return QueryContext.EXPANSION
            elif any(indicator in query_lower for indicator in follow_up_indicators):
                return QueryContext.FOLLOW_UP
            
            # Default to follow-up if there are previous turns
            return QueryContext.FOLLOW_UP
            
        except Exception as e:
            self.logger.error(f"Context analysis failed: {e}")
            return QueryContext.NEW_SESSION
    
    async def _enhance_with_knowledge_graph(self, user_query: str) -> Dict[str, Any]:
        """Enhance query with Knowledge Graph entities"""
        
        try:
            if not self.knowledge_graph_client:
                return {}
            
            # Extract potential entities for KG lookup
            words = user_query.split()
            potential_entities = []
            
            # Look for company names, domains, proper nouns
            for word in words:
                if (len(word) > 3 and 
                    (word[0].isupper() or 
                     '.' in word or 
                     word.lower().endswith('.com'))):
                    potential_entities.append(word)
            
            if not potential_entities:
                return {}
            
            # Batch query KG for entities
            kg_results = await self.knowledge_graph_client.get_entities_batch(
                potential_entities[:5],  # Limit to 5 entities
                enrich_with_nlp=False
            )
            
            enhancement = {
                'kg_entities': [],
                'enriched_terms': []
            }
            
            for result in kg_results:
                if result.confidence_score > 0.3:  # Only include confident results
                    enhancement['kg_entities'].append({
                        'name': result.name,
                        'industry': result.industry,
                        'description': result.description,
                        'confidence': result.confidence_score
                    })
                    
                    if result.industry:
                        enhancement['enriched_terms'].append(result.industry)
            
            return enhancement
            
        except Exception as e:
            self.logger.error(f"Knowledge Graph enhancement failed: {e}")
            return {}
    
    async def _extract_parameters(
        self, 
        user_query: str, 
        intent: QueryIntent, 
        entities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract parameters based on intent and entities"""
        
        parameters = {
            'query': user_query,
            'intent': intent.value,
            'entity_count': len(entities)
        }
        
        # Intent-specific parameter extraction
        if intent == QueryIntent.KEYWORD_RESEARCH:
            parameters.update({
                'target_keywords': [e['text'] for e in entities if e['label'] in ['ORG', 'PRODUCT', 'GPE']],
                'search_volume_required': 'volume' in user_query.lower(),
                'difficulty_analysis': 'difficulty' in user_query.lower()
            })
        
        elif intent == QueryIntent.COMPETITOR_ANALYSIS:
            parameters.update({
                'competitors': [e['text'] for e in entities if e['label'] == 'ORG'],
                'analysis_depth': 'detailed' if 'detailed' in user_query.lower() else 'standard',
                'include_content': 'content' in user_query.lower()
            })
        
        elif intent == QueryIntent.CONTENT_STRATEGY:
            parameters.update({
                'content_type': self._extract_content_type(user_query),
                'target_audience': [e['text'] for e in entities if e['label'] == 'PERSON'],
                'topics': [e['text'] for e in entities if e['label'] in ['ORG', 'PRODUCT']]
            })
        
        elif intent == QueryIntent.BLUEPRINT_GENERATION:
            parameters.update({
                'blueprint_type': 'content',
                'target_keywords': [e['text'] for e in entities],
                'structure_requirements': 'outline' in user_query.lower()
            })
        
        return parameters
    
    def _extract_content_type(self, user_query: str) -> str:
        """Extract content type from query"""
        content_types = {
            'blog': ['blog', 'post', 'article'],
            'video': ['video', 'youtube', 'vlog'],
            'infographic': ['infographic', 'visual', 'graphic'],
            'guide': ['guide', 'tutorial', 'how-to'],
            'whitepaper': ['whitepaper', 'research', 'report']
        }
        
        query_lower = user_query.lower()
        for content_type, keywords in content_types.items():
            if any(keyword in query_lower for keyword in keywords):
                return content_type
        
        return 'article'
    
    async def _generate_suggested_actions(
        self, 
        intent: QueryIntent, 
        parameters: Dict[str, Any], 
        entities: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate suggested actions based on intent and parameters"""
        
        actions = []
        
        if intent == QueryIntent.KEYWORD_RESEARCH:
            actions.extend([
                "Generate keyword research report",
                "Analyze search volume trends",
                "Identify long-tail opportunities"
            ])
            if parameters.get('target_keywords'):
                actions.append(f"Focus on keywords: {', '.join(parameters['target_keywords'][:3])}")
        
        elif intent == QueryIntent.COMPETITOR_ANALYSIS:
            actions.extend([
                "Perform competitor content analysis",
                "Compare SEO strategies",
                "Identify content gaps"
            ])
            if parameters.get('competitors'):
                actions.append(f"Analyze competitors: {', '.join(parameters['competitors'][:3])}")
        
        elif intent == QueryIntent.CONTENT_STRATEGY:
            actions.extend([
                "Create content calendar",
                "Develop topic clusters",
                "Plan content distribution"
            ])
            
        elif intent == QueryIntent.BLUEPRINT_GENERATION:
            actions.extend([
                "Generate content blueprint",
                "Create structured outline",
                "Optimize for search intent"
            ])
        
        elif intent == QueryIntent.SEO_OPTIMIZATION:
            actions.extend([
                "Analyze on-page SEO factors",
                "Review technical SEO elements",
                "Optimize content structure"
            ])
        
        else:
            actions.extend([
                "Clarify your requirements",
                "Provide more specific details",
                "Choose from available options"
            ])
        
        return actions[:5]  # Limit to 5 actions
    
    async def _enhance_query(self, original_query: str, kg_enhancement: Dict[str, Any]) -> str:
        """Enhance query with additional context and entities"""
        
        enhanced_query = original_query
        
        if kg_enhancement and kg_enhancement.get('enriched_terms'):
            enriched_terms = kg_enhancement['enriched_terms']
            # Add industry context if available
            if enriched_terms:
                enhanced_query += f" (Industry context: {', '.join(enriched_terms[:3])})"
        
        return enhanced_query
    
    async def _get_or_create_session(
        self, 
        session_id: Optional[str], 
        user_id: Optional[str]
    ) -> Optional[ConversationSession]:
        """Get existing session or create new one"""
        
        if not self.config.get('enable_conversation_memory', True):
            return None
        
        try:
            # Clean expired sessions
            await self._cleanup_expired_sessions()
            
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.last_activity = datetime.utcnow()
                return session
            
            # Create new session
            if not session_id:
                session_id = self._generate_session_id()
            
            session = ConversationSession(
                session_id=session_id,
                user_id=user_id
            )
            
            self.active_sessions[session_id] = session
            self.metrics['conversation_sessions'] = len(self.active_sessions)
            
            return session
            
        except Exception as e:
            self.logger.error(f"Session management failed: {e}")
            return None
    
    async def _cleanup_expired_sessions(self):
        """Remove expired conversation sessions"""
        
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session in self.active_sessions.items():
                if current_time - session.last_activity > self.session_ttl:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                self.logger.debug(f"Cleaned up {len(expired_sessions)} expired sessions")
                self.metrics['conversation_sessions'] = len(self.active_sessions)
                
        except Exception as e:
            self.logger.error(f"Session cleanup failed: {e}")
    
    async def _update_session_cache(self, session: ConversationSession):
        """Update session in cache"""
        try:
            # Keep only recent turns to limit memory usage
            max_turns = self.config.get('max_conversation_turns', 20)
            if len(session.turns) > max_turns:
                session.turns = session.turns[-max_turns:]
            
            # Cache session data if cache manager available
            if hasattr(self.cache_manager, 'set_with_ttl'):
                await self.cache_manager.set_with_ttl(
                    f"conversation_session:{session.session_id}",
                    asdict(session),
                    ttl_seconds=int(self.session_ttl.total_seconds())
                )
        except Exception as e:
            self.logger.error(f"Session cache update failed: {e}")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import uuid
        return f"conv_{uuid.uuid4().hex[:16]}"
    
    def _generate_turn_id(self) -> str:
        """Generate unique turn ID"""
        import uuid
        return f"turn_{uuid.uuid4().hex[:12]}"
    
    def _generate_cache_key(self, query: str, session_id: Optional[str] = None) -> str:
        """Generate cache key for query result"""
        key_data = f"{query}:{session_id or 'no_session'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query processing result"""
        try:
            if hasattr(self.cache_manager, 'get'):
                # Use the correct cache manager interface
                full_key = f"query_result:{cache_key}"
                return await asyncio.to_thread(self.cache_manager.get, full_key, full_key)
            return None
        except Exception as e:
            self.logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache query processing result"""
        try:
            if hasattr(self.cache_manager, 'set_with_ttl'):
                full_key = f"query_result:{cache_key}"
                await asyncio.to_thread(
                    self.cache_manager.set_with_ttl, 
                    full_key, 
                    result, 
                    ttl_seconds=3600
                )
        except Exception as e:
            self.logger.error(f"Cache storage failed: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            'processing_metrics': self.metrics.copy(),
            'session_metrics': {
                'active_sessions': len(self.active_sessions),
                'session_ttl_hours': self.session_ttl.total_seconds() / 3600
            },
            'ai_integration': {
                'nlp_processor_available': self.nlp_processor is not None,
                'knowledge_graph_available': self.knowledge_graph_client is not None,
                'ai_manager_initialized': self.ai_manager is not None
            },
            'configuration': self.config
        }
    
    async def shutdown(self):
        """Gracefully shutdown the conversational query engine"""
        try:
            self.logger.info("🛑 Shutting down Conversational Query Engine...")
            
            # Clear sessions
            self.active_sessions.clear()
            
            # Update final metrics
            self.metrics['conversation_sessions'] = 0
            
            self.logger.info("✅ Conversational Query Engine shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

# Global instance factory
_conversational_query_engine = None

async def get_conversational_query_engine(config: Optional[Dict[str, Any]] = None) -> ConversationalQueryEngine:
    """Get the global conversational query engine instance"""
    global _conversational_query_engine
    
    if _conversational_query_engine is None:
        _conversational_query_engine = ConversationalQueryEngine(config)
        await _conversational_query_engine.initialize()
    
    return _conversational_query_engine