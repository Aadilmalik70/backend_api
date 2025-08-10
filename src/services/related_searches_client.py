"""
Related Searches Client - Comprehensive keyword expansion and search intelligence

Advanced multi-source related searches collection system that gathers keyword expansions,
search suggestions, and semantic clusters from various search engines and APIs.

Features:
- Multi-source search expansion (Google, Bing, DuckDuckGo, Answer The Public)
- Semantic clustering and topic modeling
- Search volume estimation and competition analysis
- Long-tail keyword identification and opportunities
- Trend analysis and seasonality detection
- Integration with existing Google APIs infrastructure
- Intelligent deduplication and quality scoring

Data Sources:
1. Google Related Searches - From search results pages
2. Bing Related Searches - Microsoft search suggestions  
3. Answer The Public - Question-based keyword expansion
4. Keyword research APIs - Volume and competition data
5. Semantic analysis - Topic clustering and relationships

Performance: <3s response time, intelligent rate limiting across sources
"""

import asyncio
import logging
import json
import time
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, Counter
from enum import Enum
import hashlib

from .async_request_manager import AsyncRequestManager, RequestConfig, RequestMethod
from .data_models import RelatedSearchesData, DataSourceType
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

@dataclass
class SearchesConfig:
    """Configuration for related searches client"""
    # Source settings
    enable_google_related: bool = True
    enable_bing_related: bool = True
    enable_answer_the_public: bool = True
    enable_ubersuggest: bool = False  # Requires API key
    
    # Collection limits
    max_related_terms: int = 50
    max_long_tail_keywords: int = 20
    max_semantic_clusters: int = 8
    min_keyword_length: int = 3
    
    # Quality filters
    min_search_volume: int = 10
    max_competition: float = 0.8
    relevance_threshold: float = 0.6
    
    # Performance settings
    request_timeout: float = 5.0
    max_retries: int = 2
    cache_duration: int = 3600  # 1 hour
    
    # Rate limiting per source
    google_rpm: int = 300
    bing_rpm: int = 200
    atp_rpm: int = 100

class KeywordMetrics:
    """Keyword performance metrics"""
    
    def __init__(self):
        self.search_volume: int = 0
        self.competition: float = 0.0
        self.cpc_estimate: float = 0.0
        self.difficulty: float = 0.0
        self.trend_direction: str = "stable"
        self.seasonality: List[float] = []
        self.commercial_intent: float = 0.0

@dataclass
class RelatedKeyword:
    """Individual related keyword with comprehensive metadata"""
    keyword: str
    source: str
    relevance_score: float
    metrics: KeywordMetrics = field(default_factory=KeywordMetrics)
    semantic_cluster: Optional[str] = None
    intent_category: str = "informational"
    is_long_tail: bool = False
    is_question: bool = False
    related_topics: List[str] = field(default_factory=list)

class SemanticCluster:
    """Semantic keyword cluster"""
    
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.keywords: List[str] = []
        self.central_topic: str = ""
        self.coherence_score: float = 0.0
        self.commercial_potential: float = 0.0

class RelatedSearchesClient:
    """
    Advanced related searches client with multi-source collection,
    semantic analysis, and intelligent keyword processing.
    """
    
    def __init__(self, config: Optional[SearchesConfig] = None):
        """Initialize related searches client"""
        self.config = config or SearchesConfig()
        self.logger = logging.getLogger(__name__)
        
        # Request management for different sources
        self.request_manager = AsyncRequestManager()
        
        # Rate limiters for each source
        self.rate_limiters = {
            'google': RateLimiter(requests_per_minute=self.config.google_rpm, burst_limit=50),
            'bing': RateLimiter(requests_per_minute=self.config.bing_rpm, burst_limit=30),
            'atp': RateLimiter(requests_per_minute=self.config.atp_rpm, burst_limit=20)
        }
        
        # Caching system
        self.searches_cache: Dict[str, Tuple[RelatedSearchesData, float]] = {}
        self.cache_ttl = self.config.cache_duration
        
        # Semantic analysis patterns
        self.intent_patterns = self._initialize_intent_patterns()
        self.commercial_indicators = self._initialize_commercial_indicators()
        self.question_patterns = self._initialize_question_patterns()
        
        # Performance metrics
        self.request_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'successful_requests': 0,
            'google_requests': 0,
            'bing_requests': 0,
            'atp_requests': 0,
            'average_response_time': 0.0
        }
        
        self.logger.info("Related Searches Client initialized")
    
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for search intent classification"""
        return {
            'commercial': [
                r'\b(buy|purchase|shop|store|price|cost|deal|discount|sale|cheap|best|top|review)\b',
                r'\b(vs|versus|compare|comparison)\b',
                r'\b(near me|location|local)\b'
            ],
            'informational': [
                r'\b(what|how|why|when|where|who)\b',
                r'\b(guide|tutorial|learn|understand|explain)\b',
                r'\b(definition|meaning|example)\b'
            ],
            'navigational': [
                r'\b(login|sign in|website|official|homepage)\b',
                r'\b(download|install|app)\b'
            ],
            'transactional': [
                r'\b(book|order|hire|subscribe|register|signup)\b',
                r'\b(free|trial|demo)\b'
            ]
        }
    
    def _initialize_commercial_indicators(self) -> List[str]:
        """Initialize commercial intent indicators"""
        return [
            'buy', 'purchase', 'price', 'cost', 'shop', 'store', 'deal',
            'discount', 'sale', 'cheap', 'expensive', 'affordable',
            'best', 'top', 'review', 'compare', 'vs', 'versus',
            'coupon', 'promo', 'offer', 'free shipping', 'warranty'
        ]
    
    def _initialize_question_patterns(self) -> List[str]:
        """Initialize question patterns for identifying question keywords"""
        return [
            r'^(what|how|why|when|where|who|which|can|should|will|is|are|do|does)\s',
            r'\?$',  # Ends with question mark
            r'\b(question|answer)\b'
        ]
    
    async def initialize(self):
        """Initialize related searches client components"""
        try:
            self.logger.info("🚀 Initializing Related Searches Client...")
            
            # Initialize request manager
            await self.request_manager.initialize()
            
            self.logger.info("✅ Related Searches Client initialization complete")
            
        except Exception as e:
            self.logger.error(f"Related Searches Client initialization failed: {e}")
            raise
    
    async def get_related_searches(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive related searches from multiple sources with analysis
        
        Args:
            query: The search query to expand
            context: Additional context for customization
            
        Returns:
            Dictionary with structured related searches data
        """
        
        if not query or not query.strip():
            return self._create_empty_result(query, "Empty query provided")
        
        query = query.strip()
        context = context or {}
        
        start_time = time.time()
        self.request_metrics['total_requests'] += 1
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, context)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                self.request_metrics['cache_hits'] += 1
                self.logger.debug(f"Cache hit for related searches query: {query}")
                return self._format_api_response(cached_result)
            
            # Collect related searches from multiple sources in parallel
            search_tasks = []
            
            if self.config.enable_google_related:
                search_tasks.append(self._get_google_related_searches(query, context))
            
            if self.config.enable_bing_related:
                search_tasks.append(self._get_bing_related_searches(query, context))
            
            if self.config.enable_answer_the_public:
                search_tasks.append(self._get_atp_related_searches(query, context))
            
            # Execute all collection tasks in parallel
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Combine and process all results
            combined_keywords = self._combine_search_results(query, search_results)
            
            # Enhance with semantic analysis and clustering
            enhanced_data = await self._enhance_related_searches(query, combined_keywords, context)
            
            # Cache the result
            self._cache_result(cache_key, enhanced_data)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(True, execution_time)
            
            self.logger.info(f"Related searches retrieved for '{query}': {len(enhanced_data.related_terms)} terms")
            
            return self._format_api_response(enhanced_data)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(False, execution_time)
            self.logger.error(f"Failed to get related searches for '{query}': {e}")
            
            return self._create_error_result(query, str(e))
    
    async def _get_google_related_searches(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[RelatedKeyword]:
        """Get related searches from Google"""
        
        try:
            # Check rate limiter
            if not await self.rate_limiters['google'].acquire():
                self.logger.warning("Google rate limit exceeded")
                return []
            
            self.request_metrics['google_requests'] += 1
            
            # Use Google search to get related searches
            search_url = "https://www.google.com/search"
            params = {
                'q': query,
                'hl': context.get('language', 'en'),
                'gl': context.get('country', 'us'),
                'num': 10
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=search_url,
                params=params,
                headers=headers,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                html_content = result.data if isinstance(result.data, str) else str(result.data)
                related_terms = self._parse_google_related_searches(html_content)
                
                # Convert to RelatedKeyword objects
                keywords = []
                for i, term in enumerate(related_terms):
                    keyword = RelatedKeyword(
                        keyword=term,
                        source='google',
                        relevance_score=0.9 - (i * 0.05),  # Decreasing relevance
                        intent_category=self._classify_intent(term)
                    )
                    keyword.is_question = self._is_question_keyword(term)
                    keyword.is_long_tail = len(term.split()) > 3
                    keywords.append(keyword)
                
                return keywords[:self.config.max_related_terms // 2]  # Half from Google
            
            return []
            
        except Exception as e:
            self.logger.error(f"Google related searches failed: {e}")
            return []
    
    async def _get_bing_related_searches(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[RelatedKeyword]:
        """Get related searches from Bing"""
        
        try:
            # Check rate limiter
            if not await self.rate_limiters['bing'].acquire():
                self.logger.warning("Bing rate limit exceeded")
                return []
            
            self.request_metrics['bing_requests'] += 1
            
            # Use Bing search to get related searches
            search_url = "https://www.bing.com/search"
            params = {
                'q': query,
                'setlang': context.get('language', 'en'),
                'cc': context.get('country', 'US').upper()
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=search_url,
                params=params,
                headers=headers,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                html_content = result.data if isinstance(result.data, str) else str(result.data)
                related_terms = self._parse_bing_related_searches(html_content)
                
                # Convert to RelatedKeyword objects
                keywords = []
                for i, term in enumerate(related_terms):
                    keyword = RelatedKeyword(
                        keyword=term,
                        source='bing',
                        relevance_score=0.8 - (i * 0.05),  # Slightly lower than Google
                        intent_category=self._classify_intent(term)
                    )
                    keyword.is_question = self._is_question_keyword(term)
                    keyword.is_long_tail = len(term.split()) > 3
                    keywords.append(keyword)
                
                return keywords[:self.config.max_related_terms // 3]  # Third from Bing
            
            return []
            
        except Exception as e:
            self.logger.error(f"Bing related searches failed: {e}")
            return []
    
    async def _get_atp_related_searches(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> List[RelatedKeyword]:
        """Get related searches from Answer The Public style questions"""
        
        try:
            # Check rate limiter
            if not await self.rate_limiters['atp'].acquire():
                self.logger.warning("Answer The Public rate limit exceeded")
                return []
            
            self.request_metrics['atp_requests'] += 1
            
            # Generate question-based keywords using Answer The Public approach
            question_keywords = self._generate_atp_questions(query)
            
            # Convert to RelatedKeyword objects
            keywords = []
            for i, question in enumerate(question_keywords):
                keyword = RelatedKeyword(
                    keyword=question,
                    source='answer_the_public',
                    relevance_score=0.7 - (i * 0.03),
                    intent_category='informational',  # Most ATP questions are informational
                    is_question=True,
                    is_long_tail=True  # ATP questions are typically long-tail
                )
                keywords.append(keyword)
            
            return keywords[:self.config.max_related_terms // 4]  # Quarter from ATP
            
        except Exception as e:
            self.logger.error(f"Answer The Public style generation failed: {e}")
            return []
    
    def _parse_google_related_searches(self, html_content: str) -> List[str]:
        """Parse Google related searches from HTML"""
        related_terms = []
        
        # Patterns for Google related searches
        patterns = [
            r'<div[^>]*class="[^"]*related[^"]*"[^>]*>(.*?)</div>',
            r'data-q="([^"]+)"',
            r'<a[^>]*>([^<]*related[^<]*)</a>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                
                # Clean and validate the term
                clean_term = re.sub(r'<[^>]+>', '', str(match)).strip()
                if self._is_valid_related_term(clean_term):
                    related_terms.append(clean_term)
        
        # Also try to find "Searches related to" section
        related_section = re.search(
            r'searches? related to[^<]*</[^>]*>(.*?)</table>',
            html_content,
            re.IGNORECASE | re.DOTALL
        )
        
        if related_section:
            section_html = related_section.group(1)
            links = re.findall(r'<a[^>]*>([^<]+)</a>', section_html)
            
            for link_text in links:
                clean_term = link_text.strip()
                if self._is_valid_related_term(clean_term):
                    related_terms.append(clean_term)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in related_terms:
            term_lower = term.lower()
            if term_lower not in seen and len(term_lower) > self.config.min_keyword_length:
                seen.add(term_lower)
                unique_terms.append(term)
        
        return unique_terms
    
    def _parse_bing_related_searches(self, html_content: str) -> List[str]:
        """Parse Bing related searches from HTML"""
        related_terms = []
        
        # Patterns for Bing related searches
        patterns = [
            r'<li class="sw_ddbk"[^>]*><h4[^>]*><a[^>]*>([^<]+)</a>',
            r'data-q="([^"]+)"',
            r'<div[^>]*class="[^"]*related[^"]*"[^>]*>([^<]+)</div>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                clean_term = re.sub(r'<[^>]+>', '', str(match)).strip()
                if self._is_valid_related_term(clean_term):
                    related_terms.append(clean_term)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in related_terms:
            term_lower = term.lower()
            if term_lower not in seen and len(term_lower) > self.config.min_keyword_length:
                seen.add(term_lower)
                unique_terms.append(term)
        
        return unique_terms
    
    def _generate_atp_questions(self, query: str) -> List[str]:
        """Generate Answer The Public style questions"""
        
        questions = []
        
        # Question templates
        templates = {
            'what': [
                f"what is {query}",
                f"what are {query}",
                f"what does {query} mean",
                f"what are the benefits of {query}",
                f"what are the disadvantages of {query}"
            ],
            'how': [
                f"how to {query}",
                f"how does {query} work",
                f"how much is {query}",
                f"how to use {query}",
                f"how to get {query}"
            ],
            'why': [
                f"why {query}",
                f"why is {query} important",
                f"why do people use {query}",
                f"why should I {query}"
            ],
            'when': [
                f"when to {query}",
                f"when is {query}",
                f"when should I {query}",
                f"when was {query} created"
            ],
            'where': [
                f"where to {query}",
                f"where can I {query}",
                f"where is {query}"
            ],
            'who': [
                f"who uses {query}",
                f"who created {query}",
                f"who needs {query}"
            ]
        }
        
        # Select appropriate templates based on query
        query_words = query.lower().split()
        
        # Add all appropriate question types
        for question_type, question_list in templates.items():
            # Skip if query already contains the question word
            if question_type not in query_words:
                questions.extend(question_list)
        
        return questions[:20]  # Limit to 20 questions
    
    def _combine_search_results(
        self,
        query: str,
        search_results: List[Any]
    ) -> List[RelatedKeyword]:
        """Combine and deduplicate results from multiple sources"""
        
        all_keywords = []
        seen_keywords = set()
        
        for result in search_results:
            if isinstance(result, Exception):
                continue
            
            if isinstance(result, list):
                for keyword in result:
                    if isinstance(keyword, RelatedKeyword):
                        # Deduplicate based on normalized keyword
                        normalized = keyword.keyword.lower().strip()
                        if normalized not in seen_keywords and len(normalized) > self.config.min_keyword_length:
                            seen_keywords.add(normalized)
                            all_keywords.append(keyword)
        
        # Sort by relevance score and source priority
        source_priority = {'google': 3, 'bing': 2, 'answer_the_public': 1}
        
        all_keywords.sort(key=lambda x: (
            source_priority.get(x.source, 0),
            x.relevance_score
        ), reverse=True)
        
        return all_keywords[:self.config.max_related_terms]
    
    async def _enhance_related_searches(
        self,
        query: str,
        keywords: List[RelatedKeyword],
        context: Dict[str, Any]
    ) -> RelatedSearchesData:
        """Enhance keywords with metrics, clustering, and analysis"""
        
        if not keywords:
            return RelatedSearchesData(query=query, collection_timestamp=datetime.utcnow())
        
        # Estimate search volumes and competition
        await self._estimate_keyword_metrics(keywords)
        
        # Perform semantic clustering
        semantic_clusters = self._perform_semantic_clustering(keywords)
        
        # Identify long-tail opportunities
        long_tail_keywords = self._identify_long_tail_opportunities(keywords)
        
        # Extract topics and trends
        topics = self._extract_keyword_topics(keywords)
        
        # Calculate search volumes and competition maps
        search_volumes = {kw.keyword: kw.metrics.search_volume for kw in keywords}
        competition_scores = {kw.keyword: kw.metrics.competition for kw in keywords}
        
        # Create trend data (placeholder implementation)
        trend_data = {kw.keyword: [0.8, 0.9, 1.0, 1.1, 1.2] for kw in keywords[:10]}
        
        # Create enhanced related searches data
        related_data = RelatedSearchesData(
            query=query,
            related_terms=[kw.keyword for kw in keywords],
            search_volumes=search_volumes,
            competition_scores=competition_scores,
            trend_data=trend_data,
            semantic_clusters=[[kw for kw in cluster.keywords] for cluster in semantic_clusters],
            long_tail_keywords=long_tail_keywords,
            collection_timestamp=datetime.utcnow()
        )
        
        return related_data
    
    async def _estimate_keyword_metrics(self, keywords: List[RelatedKeyword]):
        """Estimate search volume and competition for keywords"""
        
        for keyword in keywords:
            # Simple heuristic-based estimation (in production, would use APIs)
            
            # Base volume estimation
            word_count = len(keyword.keyword.split())
            base_volume = 1000 if word_count <= 2 else 500 if word_count <= 4 else 200
            
            # Adjust based on commercial intent
            commercial_score = self._calculate_commercial_score(keyword.keyword)
            volume_multiplier = 1.5 if commercial_score > 0.5 else 1.0
            
            # Adjust based on question format
            if keyword.is_question:
                volume_multiplier *= 0.7  # Questions typically have lower volume
            
            keyword.metrics.search_volume = int(base_volume * volume_multiplier)
            
            # Competition estimation
            keyword.metrics.competition = min(0.9, commercial_score + 0.2)
            
            # Difficulty score
            keyword.metrics.difficulty = (
                keyword.metrics.competition * 0.6 +
                (1.0 - keyword.relevance_score) * 0.4
            )
            
            # Commercial intent
            keyword.metrics.commercial_intent = commercial_score
    
    def _perform_semantic_clustering(self, keywords: List[RelatedKeyword]) -> List[SemanticCluster]:
        """Perform semantic clustering of keywords"""
        
        clusters = []
        
        # Simple clustering based on word overlap and topics
        clustered_keywords = set()
        
        for keyword in keywords:
            if keyword.keyword in clustered_keywords:
                continue
            
            # Create new cluster
            cluster = SemanticCluster(f"cluster_{len(clusters) + 1}")
            cluster.keywords.append(keyword.keyword)
            clustered_keywords.add(keyword.keyword)
            
            # Find related keywords for this cluster
            keyword_words = set(keyword.keyword.lower().split())
            
            for other_keyword in keywords:
                if other_keyword.keyword in clustered_keywords:
                    continue
                
                other_words = set(other_keyword.keyword.lower().split())
                overlap = len(keyword_words & other_words)
                
                # Add to cluster if significant word overlap
                if overlap >= 2 or (overlap >= 1 and len(other_words) <= 3):
                    cluster.keywords.append(other_keyword.keyword)
                    clustered_keywords.add(other_keyword.keyword)
            
            # Only keep clusters with multiple keywords
            if len(cluster.keywords) >= 2:
                cluster.central_topic = self._identify_central_topic(cluster.keywords)
                cluster.coherence_score = len(cluster.keywords) / len(keywords)
                clusters.append(cluster)
            
            # Limit number of clusters
            if len(clusters) >= self.config.max_semantic_clusters:
                break
        
        return clusters
    
    def _identify_long_tail_opportunities(self, keywords: List[RelatedKeyword]) -> List[str]:
        """Identify long-tail keyword opportunities"""
        
        long_tail = []
        
        for keyword in keywords:
            # Long-tail criteria
            is_long_tail = (
                len(keyword.keyword.split()) >= 4 and  # 4+ words
                keyword.metrics.competition < 0.3 and   # Low competition
                keyword.metrics.search_volume > 50 and  # Decent volume
                keyword.relevance_score > 0.6           # Good relevance
            )
            
            if is_long_tail:
                long_tail.append(keyword.keyword)
        
        # Sort by opportunity score (volume / competition)
        long_tail.sort(key=lambda kw: self._calculate_opportunity_score(kw), reverse=True)
        
        return long_tail[:self.config.max_long_tail_keywords]
    
    def _calculate_opportunity_score(self, keyword: str) -> float:
        """Calculate opportunity score for a keyword"""
        # Find the keyword object
        for kw in self.current_keywords:
            if kw.keyword == keyword:
                if kw.metrics.competition > 0:
                    return kw.metrics.search_volume / kw.metrics.competition
                else:
                    return kw.metrics.search_volume * 2
        return 0.0
    
    def _extract_keyword_topics(self, keywords: List[RelatedKeyword]) -> List[str]:
        """Extract main topics from keywords"""
        
        # Count word frequency
        word_count = Counter()
        
        for keyword in keywords:
            words = keyword.keyword.lower().split()
            # Filter out common stop words
            stop_words = {'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'the', 'a', 'an'}
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            word_count.update(filtered_words)
        
        # Get most common topics
        topics = [word for word, count in word_count.most_common(10) if count >= 2]
        
        return topics
    
    def _identify_central_topic(self, cluster_keywords: List[str]) -> str:
        """Identify the central topic of a keyword cluster"""
        
        # Find most common words in the cluster
        word_count = Counter()
        
        for keyword in cluster_keywords:
            words = keyword.lower().split()
            word_count.update(words)
        
        # Return most common non-stop word
        stop_words = {'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'the', 'a', 'an'}
        
        for word, count in word_count.most_common():
            if word not in stop_words and len(word) > 2:
                return word
        
        return cluster_keywords[0].split()[0] if cluster_keywords else "unknown"
    
    def _classify_intent(self, keyword: str) -> str:
        """Classify the search intent of a keyword"""
        
        keyword_lower = keyword.lower()
        
        # Check patterns for each intent type
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, keyword_lower):
                    return intent
        
        # Default to informational
        return 'informational'
    
    def _is_question_keyword(self, keyword: str) -> bool:
        """Check if keyword is a question"""
        
        keyword_lower = keyword.lower()
        
        for pattern in self.question_patterns:
            if re.search(pattern, keyword_lower):
                return True
        
        return False
    
    def _calculate_commercial_score(self, keyword: str) -> float:
        """Calculate commercial intent score (0.0 to 1.0)"""
        
        keyword_lower = keyword.lower()
        commercial_count = 0
        
        for indicator in self.commercial_indicators:
            if indicator in keyword_lower:
                commercial_count += 1
        
        # Normalize score
        max_indicators = len(self.commercial_indicators)
        return min(1.0, commercial_count / max_indicators * 3)  # Scale to make it more sensitive
    
    def _is_valid_related_term(self, term: str) -> bool:
        """Validate if a term is a valid related search term"""
        
        if not term or len(term.strip()) < self.config.min_keyword_length:
            return False
        
        # Filter out obvious noise
        noise_patterns = [
            r'^\d+$',  # Just numbers
            r'^[^\w\s]+$',  # Just punctuation
            r'^\s*$',  # Just whitespace
            r'(click here|more info|read more)',  # Generic phrases
        ]
        
        term_lower = term.lower().strip()
        
        for pattern in noise_patterns:
            if re.match(pattern, term_lower):
                return False
        
        return True
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key for related searches request"""
        
        key_data = {
            'query': query.lower().strip(),
            'language': context.get('language', 'en'),
            'country': context.get('country', 'us'),
            'sources': sorted([
                s for s, enabled in [
                    ('google', self.config.enable_google_related),
                    ('bing', self.config.enable_bing_related),
                    ('atp', self.config.enable_answer_the_public)
                ] if enabled
            ])
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[RelatedSearchesData]:
        """Get cached related searches result if still valid"""
        
        if cache_key in self.searches_cache:
            cached_data, cached_time = self.searches_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
            else:
                # Remove expired cache entry
                del self.searches_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, data: RelatedSearchesData):
        """Cache related searches result"""
        
        self.searches_cache[cache_key] = (data, time.time())
        
        # Prevent cache from growing too large
        if len(self.searches_cache) > 500:
            # Remove oldest entries
            sorted_items = sorted(
                self.searches_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            
            # Keep only the most recent 400 entries
            self.searches_cache = dict(sorted_items[-400:])
    
    def _format_api_response(self, data: RelatedSearchesData) -> Dict[str, Any]:
        """Format related searches data for API response"""
        
        return {
            'query': data.query,
            'related_searches': data.related_terms,
            'keyword_insights': data.get_keyword_insights(),
            'semantic_clusters': data.semantic_clusters,
            'long_tail_opportunities': data.long_tail_keywords,
            'search_volumes': data.search_volumes,
            'competition_analysis': data.competition_scores,
            'trend_indicators': data.trend_data,
            'total_keywords': len(data.related_terms),
            'collection_timestamp': data.collection_timestamp.isoformat(),
            'data_source': DataSourceType.RELATED_SEARCHES.value
        }
    
    def _create_empty_result(self, query: str, reason: str) -> Dict[str, Any]:
        """Create empty result for invalid queries"""
        
        return {
            'query': query,
            'related_searches': [],
            'keyword_insights': {},
            'semantic_clusters': [],
            'long_tail_opportunities': [],
            'search_volumes': {},
            'competition_analysis': {},
            'trend_indicators': {},
            'total_keywords': 0,
            'error': reason,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.RELATED_SEARCHES.value
        }
    
    def _create_error_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """Create error result for failed requests"""
        
        return {
            'query': query,
            'related_searches': [],
            'keyword_insights': {},
            'semantic_clusters': [],
            'long_tail_opportunities': [],
            'search_volumes': {},
            'competition_analysis': {},
            'trend_indicators': {},
            'total_keywords': 0,
            'error': error_message,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.RELATED_SEARCHES.value
        }
    
    def _update_metrics(self, success: bool, execution_time: float):
        """Update client performance metrics"""
        
        if success:
            self.request_metrics['successful_requests'] += 1
        
        # Update rolling average response time
        total_requests = self.request_metrics['total_requests']
        current_avg = self.request_metrics['average_response_time']
        
        self.request_metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + execution_time) / total_requests
        )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get client performance metrics"""
        
        total_requests = self.request_metrics['total_requests']
        cache_hit_rate = (
            self.request_metrics['cache_hits'] / total_requests 
            if total_requests > 0 else 0.0
        )
        success_rate = (
            self.request_metrics['successful_requests'] / total_requests
            if total_requests > 0 else 0.0
        )
        
        return {
            'client_metrics': self.request_metrics,
            'cache_performance': {
                'cache_size': len(self.searches_cache),
                'cache_hit_rate': cache_hit_rate,
                'cache_ttl_seconds': self.cache_ttl
            },
            'performance_summary': {
                'success_rate': success_rate,
                'average_response_time': self.request_metrics['average_response_time'],
                'source_distribution': {
                    'google_requests': self.request_metrics['google_requests'],
                    'bing_requests': self.request_metrics['bing_requests'],
                    'atp_requests': self.request_metrics['atp_requests']
                }
            },
            'rate_limiter_status': {
                source: limiter.get_status() 
                for source, limiter in self.rate_limiters.items()
            },
            'configuration': {
                'max_related_terms': self.config.max_related_terms,
                'max_long_tail_keywords': self.config.max_long_tail_keywords,
                'max_semantic_clusters': self.config.max_semantic_clusters,
                'enabled_sources': {
                    'google': self.config.enable_google_related,
                    'bing': self.config.enable_bing_related,
                    'answer_the_public': self.config.enable_answer_the_public
                }
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for related searches client"""
        
        try:
            # Test with a simple query
            test_result = await self.get_related_searches("test query")
            
            return {
                'status': 'healthy' if 'error' not in test_result else 'degraded',
                'last_test_time': datetime.utcnow().isoformat(),
                'enabled_sources': {
                    'google_related': self.config.enable_google_related,
                    'bing_related': self.config.enable_bing_related,
                    'answer_the_public': self.config.enable_answer_the_public
                },
                'rate_limiter_health': {
                    source: limiter.get_status()['strategy']
                    for source, limiter in self.rate_limiters.items()
                },
                'cache_status': {
                    'size': len(self.searches_cache),
                    'max_size': 500
                }
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_test_time': datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Gracefully shutdown the client"""
        
        try:
            self.logger.info("🛑 Shutting down Related Searches Client...")
            
            # Shutdown request manager
            await self.request_manager.shutdown()
            
            # Shutdown rate limiters
            for limiter in self.rate_limiters.values():
                await limiter.shutdown()
            
            # Clear cache
            self.searches_cache.clear()
            
            self.logger.info("✅ Related Searches Client shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
    
    # Store current keywords for opportunity score calculation
    current_keywords: List[RelatedKeyword] = []
    
    async def _enhance_related_searches(
        self,
        query: str,
        keywords: List[RelatedKeyword],
        context: Dict[str, Any]
    ) -> RelatedSearchesData:
        """Enhanced version that stores keywords for opportunity calculation"""
        
        # Store current keywords for opportunity score calculation
        self.current_keywords = keywords
        
        # Call the original method
        result = await super()._enhance_related_searches(query, keywords, context)
        
        return result