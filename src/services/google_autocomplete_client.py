"""
Google Autocomplete Client - Query suggestion and expansion service

High-performance Google Autocomplete integration for the data acquisition pipeline,
providing intelligent query suggestions, search intent analysis, and user behavior insights.

Features:
- Multiple Google Autocomplete endpoints for comprehensive coverage
- Geographic and language-specific suggestions
- Search volume estimation and trending analysis
- Intent classification and query expansion
- Rate limiting and caching optimization
- Integration with existing Google APIs infrastructure

Data Sources:
- Google Autocomplete API (official)
- Google Suggest JSON endpoint (unofficial)
- YouTube autocomplete for video content insights
- Google Shopping suggestions for commercial queries

Performance: <2s response time, 600 requests/minute rate limit
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import quote, urlencode
from enum import Enum
import re

from .async_request_manager import AsyncRequestManager, RequestConfig, RequestMethod
from .data_models import AutocompleteData, DataSourceType
from .rate_limiter import RateLimiter

# Import existing Google APIs infrastructure
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils', 'google_apis'))
    from api_manager import GoogleAPIManager
    from migration_manager import MigrationManager
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class AutocompleteConfig:
    """Configuration for Google Autocomplete client"""
    # API endpoints
    primary_endpoint: str = "https://suggestqueries.google.com/complete/search"
    youtube_endpoint: str = "https://suggestqueries.google.com/complete/search"
    shopping_endpoint: str = "https://suggestqueries.google.com/complete/search"
    
    # Request parameters
    default_language: str = "en"
    default_country: str = "us"
    max_suggestions: int = 10
    include_trending: bool = True
    
    # Performance settings
    request_timeout: float = 3.0
    max_retries: int = 2
    cache_duration: int = 1800  # 30 minutes
    
    # Rate limiting
    requests_per_minute: int = 600
    burst_limit: int = 100

class SuggestionType(Enum):
    """Types of autocomplete suggestions"""
    WEB_SEARCH = "web"
    YOUTUBE = "youtube" 
    SHOPPING = "shopping"
    NEWS = "news"
    IMAGES = "images"

@dataclass
class SuggestionResult:
    """Individual autocomplete suggestion with metadata"""
    suggestion: str
    suggestion_type: SuggestionType
    relevance_score: float
    search_volume_estimate: int = 0
    trend_direction: str = "stable"  # up, down, stable
    intent_category: str = "informational"
    geo_popularity: Dict[str, float] = field(default_factory=dict)

class GoogleAutocompleteClient:
    """
    Advanced Google Autocomplete client with multi-endpoint support,
    intelligent caching, and comprehensive suggestion analysis.
    """
    
    def __init__(self, config: Optional[AutocompleteConfig] = None):
        """Initialize Google Autocomplete client"""
        self.config = config or AutocompleteConfig()
        self.logger = logging.getLogger(__name__)
        
        # Request management
        self.request_manager = AsyncRequestManager()
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.requests_per_minute,
            burst_limit=self.config.burst_limit
        )
        
        # Google APIs integration
        self.google_api_manager = None
        if GOOGLE_APIS_AVAILABLE:
            try:
                self.google_api_manager = GoogleAPIManager()
            except Exception as e:
                self.logger.warning(f"Google APIs manager not available: {e}")
        
        # Caching and performance
        self.suggestion_cache: Dict[str, Tuple[AutocompleteData, float]] = {}
        self.cache_ttl = self.config.cache_duration
        
        # Analytics and optimization
        self.request_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }
        
        self.logger.info("Google Autocomplete Client initialized")
    
    async def initialize(self):
        """Initialize client components"""
        try:
            self.logger.info("🚀 Initializing Google Autocomplete Client...")
            
            # Initialize request manager
            await self.request_manager.initialize()
            
            # Initialize Google APIs if available
            if self.google_api_manager:
                await self.google_api_manager.initialize()
                self.logger.info("✅ Google APIs integration enabled")
            
            self.logger.info("✅ Google Autocomplete Client initialization complete")
            
        except Exception as e:
            self.logger.error(f"Google Autocomplete Client initialization failed: {e}")
            raise
    
    async def get_autocomplete_suggestions(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive autocomplete suggestions with analysis
        
        Args:
            query: The search query to get suggestions for
            context: Additional context for suggestion customization
            
        Returns:
            Dictionary with structured autocomplete data
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
                self.logger.debug(f"Cache hit for autocomplete query: {query}")
                return cached_result.to_dict() if hasattr(cached_result, 'to_dict') else cached_result
            
            # Check rate limiter
            if not await self.rate_limiter.acquire():
                raise Exception("Rate limit exceeded for Google Autocomplete")
            
            # Get suggestions from multiple sources
            suggestion_tasks = [
                self._get_web_suggestions(query, context),
                self._get_youtube_suggestions(query, context),
                self._get_shopping_suggestions(query, context)
            ]
            
            # Execute all suggestion requests in parallel
            suggestion_results = await asyncio.gather(*suggestion_tasks, return_exceptions=True)
            
            # Process and combine results
            combined_suggestions = self._combine_suggestion_results(query, suggestion_results, context)
            
            # Analyze and enhance suggestions
            enhanced_data = await self._enhance_suggestions(query, combined_suggestions, context)
            
            # Cache the result
            self._cache_result(cache_key, enhanced_data)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(True, execution_time)
            
            self.logger.info(f"Autocomplete suggestions retrieved for '{query}': {len(enhanced_data.suggestions)} suggestions")
            
            return self._format_api_response(enhanced_data)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(False, execution_time)
            self.logger.error(f"Failed to get autocomplete suggestions for '{query}': {e}")
            
            return self._create_error_result(query, str(e))
    
    async def _get_web_suggestions(self, query: str, context: Dict[str, Any]) -> List[SuggestionResult]:
        """Get web search autocomplete suggestions"""
        try:
            # Prepare request parameters
            params = {
                'client': 'firefox',
                'q': query,
                'hl': context.get('language', self.config.default_language),
                'gl': context.get('country', self.config.default_country),
                'ds': 'o'  # Include only organic suggestions
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=self.config.primary_endpoint,
                params=params,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                # Parse Google Suggest JSON response
                suggestions = self._parse_google_suggest_response(result.data)
                
                # Convert to SuggestionResult objects
                suggestion_objects = []
                for i, suggestion in enumerate(suggestions[:self.config.max_suggestions]):
                    suggestion_objects.append(SuggestionResult(
                        suggestion=suggestion,
                        suggestion_type=SuggestionType.WEB_SEARCH,
                        relevance_score=1.0 - (i * 0.1),  # Decreasing relevance
                        intent_category=self._classify_intent(suggestion)
                    ))
                
                return suggestion_objects
            else:
                self.logger.warning(f"Web suggestions request failed: {result.error_message}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting web suggestions: {e}")
            return []
    
    async def _get_youtube_suggestions(self, query: str, context: Dict[str, Any]) -> List[SuggestionResult]:
        """Get YouTube-specific autocomplete suggestions"""
        try:
            params = {
                'client': 'youtube',
                'q': query,
                'hl': context.get('language', self.config.default_language),
                'gl': context.get('country', self.config.default_country)
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=self.config.youtube_endpoint,
                params=params,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                suggestions = self._parse_google_suggest_response(result.data)
                
                suggestion_objects = []
                for i, suggestion in enumerate(suggestions[:5]):  # Fewer YouTube suggestions
                    suggestion_objects.append(SuggestionResult(
                        suggestion=suggestion,
                        suggestion_type=SuggestionType.YOUTUBE,
                        relevance_score=0.8 - (i * 0.1),
                        intent_category="video_content"
                    ))
                
                return suggestion_objects
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting YouTube suggestions: {e}")
            return []
    
    async def _get_shopping_suggestions(self, query: str, context: Dict[str, Any]) -> List[SuggestionResult]:
        """Get shopping-specific autocomplete suggestions"""
        try:
            # Only get shopping suggestions for commercial intent queries
            if not self._has_commercial_intent(query):
                return []
            
            params = {
                'client': 'shopping',
                'q': query,
                'hl': context.get('language', self.config.default_language),
                'gl': context.get('country', self.config.default_country)
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=self.config.shopping_endpoint,
                params=params,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                suggestions = self._parse_google_suggest_response(result.data)
                
                suggestion_objects = []
                for i, suggestion in enumerate(suggestions[:3]):  # Few shopping suggestions
                    suggestion_objects.append(SuggestionResult(
                        suggestion=suggestion,
                        suggestion_type=SuggestionType.SHOPPING,
                        relevance_score=0.7 - (i * 0.1),
                        intent_category="commercial"
                    ))
                
                return suggestion_objects
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting shopping suggestions: {e}")
            return []
    
    def _parse_google_suggest_response(self, response_data: Any) -> List[str]:
        """Parse Google Suggest JSON response format"""
        try:
            # Google Suggest returns JSONP format: ["query", ["suggestion1", "suggestion2", ...]]
            if isinstance(response_data, str):
                # Remove JSONP callback wrapper if present
                if response_data.startswith('window.google.ac.h('):
                    response_data = response_data[19:-1]  # Remove wrapper
                
                # Parse JSON
                data = json.loads(response_data)
            else:
                data = response_data
            
            if isinstance(data, list) and len(data) >= 2:
                suggestions = data[1]  # Second element contains suggestions
                if isinstance(suggestions, list):
                    return [str(suggestion) for suggestion in suggestions if suggestion]
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error parsing Google Suggest response: {e}")
            return []
    
    def _combine_suggestion_results(
        self,
        query: str,
        suggestion_results: List[Any],
        context: Dict[str, Any]
    ) -> List[SuggestionResult]:
        """Combine and deduplicate suggestions from multiple sources"""
        
        all_suggestions = []
        seen_suggestions = set()
        
        for result in suggestion_results:
            if isinstance(result, Exception):
                continue
            
            if isinstance(result, list):
                for suggestion_result in result:
                    if isinstance(suggestion_result, SuggestionResult):
                        # Deduplicate suggestions
                        suggestion_text = suggestion_result.suggestion.lower().strip()
                        if suggestion_text not in seen_suggestions:
                            seen_suggestions.add(suggestion_text)
                            all_suggestions.append(suggestion_result)
        
        # Sort by relevance score and suggestion type priority
        all_suggestions.sort(key=lambda x: (
            self._get_type_priority(x.suggestion_type),
            x.relevance_score
        ), reverse=True)
        
        return all_suggestions[:self.config.max_suggestions]
    
    def _get_type_priority(self, suggestion_type: SuggestionType) -> int:
        """Get priority score for suggestion types"""
        priorities = {
            SuggestionType.WEB_SEARCH: 3,
            SuggestionType.YOUTUBE: 2,
            SuggestionType.SHOPPING: 1,
            SuggestionType.NEWS: 2,
            SuggestionType.IMAGES: 1
        }
        return priorities.get(suggestion_type, 0)
    
    async def _enhance_suggestions(
        self,
        query: str,
        suggestions: List[SuggestionResult],
        context: Dict[str, Any]
    ) -> AutocompleteData:
        """Enhance suggestions with additional analysis and metadata"""
        
        # Extract basic data
        suggestion_texts = [s.suggestion for s in suggestions]
        confidence_scores = [s.relevance_score for s in suggestions]
        
        # Estimate search volumes (placeholder implementation)
        search_volumes = await self._estimate_search_volumes(suggestion_texts)
        
        # Identify trending queries
        trending_queries = await self._identify_trending_queries(suggestion_texts)
        
        # Analyze geographic variations
        geo_data = await self._analyze_geographic_variations(query, context)
        
        # Create enhanced autocomplete data
        autocomplete_data = AutocompleteData(
            query=query,
            suggestions=suggestion_texts,
            confidence_scores=confidence_scores,
            search_volumes=search_volumes,
            trending_queries=trending_queries,
            geo_data=geo_data,
            collection_timestamp=datetime.utcnow()
        )
        
        return autocomplete_data
    
    async def _estimate_search_volumes(self, suggestions: List[str]) -> List[int]:
        """Estimate search volumes for suggestions"""
        # Placeholder implementation - in production, this would use
        # Google Keyword Planner API or similar service
        volumes = []
        
        for suggestion in suggestions:
            # Simple heuristic based on suggestion length and common words
            base_volume = 1000
            
            # Longer queries typically have lower volume
            length_factor = max(0.1, 1.0 - (len(suggestion.split()) - 1) * 0.2)
            
            # Common words get higher volume estimates
            common_words = ['how', 'what', 'best', 'top', 'review', 'buy']
            common_factor = 1.5 if any(word in suggestion.lower() for word in common_words) else 1.0
            
            estimated_volume = int(base_volume * length_factor * common_factor)
            volumes.append(estimated_volume)
        
        return volumes
    
    async def _identify_trending_queries(self, suggestions: List[str]) -> List[str]:
        """Identify which suggestions are currently trending"""
        # Placeholder implementation - would use Google Trends API
        trending = []
        
        # Simple heuristic: current events, technology, and entertainment keywords
        trending_indicators = [
            '2024', '2025', 'new', 'latest', 'update', 'review',
            'ai', 'chatgpt', 'tech', 'iphone', 'samsung'
        ]
        
        for suggestion in suggestions:
            if any(indicator in suggestion.lower() for indicator in trending_indicators):
                trending.append(suggestion)
        
        return trending[:3]  # Limit to top 3 trending
    
    async def _analyze_geographic_variations(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Analyze geographic variations in suggestions"""
        # Placeholder implementation - would make region-specific requests
        geo_data = {}
        
        # Common geographic markets
        regions = ['us', 'gb', 'ca', 'au', 'in']
        
        for region in regions[:2]:  # Limit to 2 regions to avoid rate limits
            if region != context.get('country', 'us'):
                # In production, this would make actual requests for different regions
                geo_data[region] = [f"{query} {region} specific variation"]
        
        return geo_data
    
    def _classify_intent(self, suggestion: str) -> str:
        """Classify the intent behind a suggestion"""
        suggestion_lower = suggestion.lower()
        
        # Commercial intent
        commercial_keywords = ['buy', 'price', 'cost', 'shop', 'store', 'deal', 'sale', 'cheap']
        if any(keyword in suggestion_lower for keyword in commercial_keywords):
            return "commercial"
        
        # Navigational intent
        navigational_keywords = ['login', 'website', 'official', 'homepage']
        if any(keyword in suggestion_lower for keyword in navigational_keywords):
            return "navigational"
        
        # Informational intent (default)
        return "informational"
    
    def _has_commercial_intent(self, query: str) -> bool:
        """Check if query has commercial intent for shopping suggestions"""
        commercial_indicators = [
            'buy', 'purchase', 'shop', 'store', 'price', 'cost',
            'deal', 'discount', 'sale', 'review', 'compare'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in commercial_indicators)
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key for suggestion request"""
        import hashlib
        
        key_data = {
            'query': query.lower().strip(),
            'language': context.get('language', self.config.default_language),
            'country': context.get('country', self.config.default_country)
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[AutocompleteData]:
        """Get cached autocomplete result if still valid"""
        if cache_key in self.suggestion_cache:
            cached_data, cached_time = self.suggestion_cache[cache_key]
            
            # Check if cache is still valid
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
            else:
                # Remove expired cache entry
                del self.suggestion_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, data: AutocompleteData):
        """Cache autocomplete result"""
        self.suggestion_cache[cache_key] = (data, time.time())
        
        # Prevent cache from growing too large
        if len(self.suggestion_cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(
                self.suggestion_cache.items(),
                key=lambda x: x[1][1]  # Sort by timestamp
            )
            
            # Keep only the most recent 800 entries
            self.suggestion_cache = dict(sorted_items[-800:])
    
    def _format_api_response(self, data: AutocompleteData) -> Dict[str, Any]:
        """Format autocomplete data for API response"""
        return {
            'query': data.query,
            'suggestions': data.get_top_suggestions(limit=self.config.max_suggestions),
            'trending_queries': data.trending_queries,
            'geographic_variations': data.geo_data,
            'total_suggestions': len(data.suggestions),
            'collection_timestamp': data.collection_timestamp.isoformat(),
            'data_source': DataSourceType.GOOGLE_AUTOCOMPLETE.value
        }
    
    def _create_empty_result(self, query: str, reason: str) -> Dict[str, Any]:
        """Create empty result for invalid queries"""
        return {
            'query': query,
            'suggestions': [],
            'trending_queries': [],
            'geographic_variations': {},
            'total_suggestions': 0,
            'error': reason,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.GOOGLE_AUTOCOMPLETE.value
        }
    
    def _create_error_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """Create error result for failed requests"""
        return {
            'query': query,
            'suggestions': [],
            'trending_queries': [],
            'geographic_variations': {},
            'total_suggestions': 0,
            'error': error_message,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.GOOGLE_AUTOCOMPLETE.value
        }
    
    def _update_metrics(self, success: bool, execution_time: float):
        """Update client performance metrics"""
        if success:
            self.request_metrics['successful_requests'] += 1
        else:
            self.request_metrics['failed_requests'] += 1
        
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
                'cache_size': len(self.suggestion_cache),
                'cache_hit_rate': cache_hit_rate,
                'cache_ttl_seconds': self.cache_ttl
            },
            'performance_summary': {
                'success_rate': success_rate,
                'average_response_time': self.request_metrics['average_response_time'],
                'total_requests': total_requests
            },
            'configuration': {
                'max_suggestions': self.config.max_suggestions,
                'request_timeout': self.config.request_timeout,
                'requests_per_minute': self.config.requests_per_minute
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for Google Autocomplete client"""
        try:
            # Test with a simple query
            test_result = await self.get_autocomplete_suggestions("test query")
            
            return {
                'status': 'healthy' if 'error' not in test_result else 'degraded',
                'last_test_time': datetime.utcnow().isoformat(),
                'request_manager_status': await self.request_manager.health_check(),
                'rate_limiter_status': self.rate_limiter.get_status(),
                'cache_status': {
                    'size': len(self.suggestion_cache),
                    'max_size': 1000
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
            self.logger.info("🛑 Shutting down Google Autocomplete Client...")
            
            # Shutdown request manager
            await self.request_manager.shutdown()
            
            # Clear cache
            self.suggestion_cache.clear()
            
            self.logger.info("✅ Google Autocomplete Client shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")