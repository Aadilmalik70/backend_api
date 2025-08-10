"""
Enhanced Knowledge Graph Client with Google Knowledge Graph API and Natural Language API integration
Features: batch processing, rate limiting, entity enrichment, intelligent caching
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import hashlib

# Google Cloud imports with graceful fallbacks
try:
    import google.cloud.language_v1 as language
    from google.cloud import language as language_client
    from google.oauth2 import service_account
    import requests
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    language = None
    language_client = None
    service_account = None
    requests = None

logger = logging.getLogger(__name__)

@dataclass
class RateLimiter:
    """Simple rate limiter for API calls"""
    requests_per_minute: int = 100
    requests_per_day: int = 1000
    
    def __post_init__(self):
        self.minute_calls = []
        self.daily_calls = 0
        self.daily_reset = datetime.now() + timedelta(days=1)
    
    def can_make_request(self) -> bool:
        """Check if request can be made within rate limits"""
        now = datetime.now()
        
        # Reset daily counter if needed
        if now > self.daily_reset:
            self.daily_calls = 0
            self.daily_reset = now + timedelta(days=1)
        
        # Check daily limit
        if self.daily_calls >= self.requests_per_day:
            return False
        
        # Clean old minute calls
        one_minute_ago = now - timedelta(minutes=1)
        self.minute_calls = [call_time for call_time in self.minute_calls if call_time > one_minute_ago]
        
        # Check minute limit
        if len(self.minute_calls) >= self.requests_per_minute:
            return False
        
        return True
    
    def record_request(self):
        """Record a request for rate limiting"""
        now = datetime.now()
        self.minute_calls.append(now)
        self.daily_calls += 1

@dataclass
class EntityResult:
    """Enhanced entity result with enriched data"""
    name: str
    entity_id: Optional[str] = None
    description: Optional[str] = None
    types: List[str] = None
    url: Optional[str] = None
    industry: Optional[str] = None
    confidence_score: float = 0.0
    nlp_analysis: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.types is None:
            self.types = []

class KnowledgeGraphClient:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced Knowledge Graph client with Google APIs integration"""
        self.config = config or {}
        
        # API credentials setup
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        # Initialize Google Cloud clients
        self.knowledge_graph_available = bool(self.api_key) and GOOGLE_CLOUD_AVAILABLE
        self.natural_language_client = None
        
        # Rate limiting
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.get('requests_per_minute', 100),
            requests_per_day=self.config.get('requests_per_day', 1000)
        )
        
        # Caching
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl_hours', 24) * 3600
        
        # Batch processing
        self.max_batch_size = self.config.get('max_batch_size', 10)
        
        # Initialize Natural Language client
        if self.knowledge_graph_available and self.credentials_path:
            try:
                if os.path.exists(self.credentials_path):
                    credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                    self.natural_language_client = language.LanguageServiceClient(credentials=credentials)
                    logger.info("✅ Natural Language API client initialized")
                else:
                    # Try default credentials
                    self.natural_language_client = language.LanguageServiceClient()
                    logger.info("✅ Natural Language API client initialized with default credentials")
            except Exception as e:
                logger.warning(f"⚠️ Natural Language API initialization failed: {e}")
                self.natural_language_client = None
        
        # Log initialization status
        if self.knowledge_graph_available:
            logger.info("✅ Enhanced Knowledge Graph client initialized")
            logger.info(f"   - Knowledge Graph API: {'Available' if self.api_key else 'Not Available'}")
            logger.info(f"   - Natural Language API: {'Available' if self.natural_language_client else 'Not Available'}")
            logger.info(f"   - Rate limiting: {self.rate_limiter.requests_per_minute}/min, {self.rate_limiter.requests_per_day}/day")
            logger.info(f"   - Batch processing: Max {self.max_batch_size} items")
        else:
            logger.warning("⚠️ Knowledge Graph client initialized in fallback mode")
    
    @property
    def available(self) -> bool:
        """Check if Knowledge Graph services are available"""
        return self.knowledge_graph_available
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all services"""
        health_status = {
            'status': 'healthy',
            'services': {
                'knowledge_graph': {'available': bool(self.api_key), 'status': 'healthy'},
                'natural_language': {'available': bool(self.natural_language_client), 'status': 'healthy'}
            },
            'rate_limiting': {
                'can_make_request': self.rate_limiter.can_make_request(),
                'daily_calls_made': self.rate_limiter.daily_calls,
                'daily_limit': self.rate_limiter.requests_per_day,
                'minute_calls': len(self.rate_limiter.minute_calls),
                'minute_limit': self.rate_limiter.requests_per_minute
            },
            'cache': {
                'entries': len(self.cache),
                'ttl_hours': self.cache_ttl / 3600
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Test Knowledge Graph API if available
        if self.api_key:
            try:
                # Simple test query
                test_result = await self._make_kg_request('google', limit=1)
                if test_result.get('itemListElement'):
                    health_status['services']['knowledge_graph']['status'] = 'healthy'
                else:
                    health_status['services']['knowledge_graph']['status'] = 'warning'
            except Exception as e:
                health_status['services']['knowledge_graph']['status'] = 'unhealthy'
                health_status['services']['knowledge_graph']['error'] = str(e)
                health_status['status'] = 'warning'
        
        # Test Natural Language API if available
        if self.natural_language_client:
            try:
                # Simple test analysis
                document = language.Document(content="Test", type_=language.Document.Type.PLAIN_TEXT)
                await asyncio.get_event_loop().run_in_executor(
                    None, self.natural_language_client.analyze_entities, document
                )
                health_status['services']['natural_language']['status'] = 'healthy'
            except Exception as e:
                health_status['services']['natural_language']['status'] = 'unhealthy'
                health_status['services']['natural_language']['error'] = str(e)
                health_status['status'] = 'warning'
        
        # Overall status
        unhealthy_services = sum(1 for service in health_status['services'].values() 
                               if service['status'] == 'unhealthy')
        if unhealthy_services > 0:
            health_status['status'] = 'unhealthy' if unhealthy_services == len(health_status['services']) else 'warning'
        
        return health_status
    
    async def get_entity_info(self, query: str, enrich_with_nlp: bool = True) -> EntityResult:
        """
        Get enhanced entity information from Knowledge Graph API with Natural Language enrichment
        
        Args:
            query: Entity query (domain, company name, or entity)
            enrich_with_nlp: Whether to enrich with Natural Language API analysis
            
        Returns:
            EntityResult with comprehensive entity information
        """
        try:
            if not query or not query.strip():
                return EntityResult(name="", confidence_score=0.0)
            
            # Clean the query
            clean_query = self._clean_query(query)
            logger.debug(f"🔍 Knowledge Graph query for: {clean_query}")
            
            # Check cache first
            cache_key = self._get_cache_key(f"entity_{clean_query}_{enrich_with_nlp}")
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug(f"📦 Cache hit for entity: {clean_query}")
                return EntityResult(**cached_result)
            
            # Rate limiting check
            if not self.rate_limiter.can_make_request():
                logger.warning(f"⚠️ Rate limit reached for query: {clean_query}")
                return self._create_fallback_entity(clean_query)
            
            # Make Knowledge Graph API request
            entity_result = None
            if self.knowledge_graph_available:
                try:
                    kg_response = await self._make_kg_request(clean_query, limit=1)
                    self.rate_limiter.record_request()
                    
                    if kg_response.get('itemListElement'):
                        item = kg_response['itemListElement'][0]
                        result_data = item.get('result', {})
                        
                        entity_result = EntityResult(
                            name=result_data.get('name', clean_query),
                            entity_id=result_data.get('@id'),
                            description=self._extract_description(result_data),
                            types=result_data.get('@type', []),
                            url=result_data.get('url'),
                            confidence_score=item.get('resultScore', 100.0) / 1000.0,  # Normalize to 0-1
                            industry=self._extract_industry(result_data)
                        )
                        
                        logger.info(f"✅ Knowledge Graph entity found: {entity_result.name}")
                    else:
                        logger.debug(f"🔍 No Knowledge Graph results for: {clean_query}")
                        
                except Exception as kg_error:
                    logger.error(f"❌ Knowledge Graph API error: {kg_error}")
            
            # Fallback to inferred entity if no KG result
            if not entity_result:
                entity_result = self._create_fallback_entity(clean_query)
            
            # Enrich with Natural Language API if requested and available
            if enrich_with_nlp and self.natural_language_client and entity_result.description:
                try:
                    nlp_analysis = await self._analyze_entity_with_nlp(entity_result.description)
                    entity_result.nlp_analysis = nlp_analysis
                    
                    # Update industry based on NLP analysis if not already set
                    if not entity_result.industry and nlp_analysis:
                        entity_result.industry = self._extract_industry_from_nlp(nlp_analysis)
                    
                    logger.debug(f"🧠 NLP enrichment completed for: {entity_result.name}")
                    
                except Exception as nlp_error:
                    logger.warning(f"⚠️ NLP enrichment failed: {nlp_error}")
            
            # Cache the result
            self._cache_result(cache_key, entity_result.__dict__)
            
            return entity_result
            
        except Exception as e:
            logger.error(f"❌ Entity info retrieval failed for '{query}': {e}")
            return EntityResult(name=query, confidence_score=0.0)
    
    async def get_entities_batch(self, queries: List[str], enrich_with_nlp: bool = True) -> List[EntityResult]:
        """
        Process multiple entity queries in batch with intelligent rate limiting
        
        Args:
            queries: List of entity queries to process
            enrich_with_nlp: Whether to enrich results with Natural Language API
            
        Returns:
            List of EntityResult objects
        """
        if not queries:
            return []
        
        # Limit batch size
        if len(queries) > self.max_batch_size:
            logger.warning(f"⚠️ Batch size {len(queries)} exceeds limit {self.max_batch_size}, processing first {self.max_batch_size}")
            queries = queries[:self.max_batch_size]
        
        logger.info(f"🚀 Processing batch of {len(queries)} entity queries")
        
        results = []
        
        # Process queries with rate limiting
        for i, query in enumerate(queries):
            try:
                # Check rate limits before each request
                if not self.rate_limiter.can_make_request():
                    logger.warning(f"⚠️ Rate limit reached at query {i+1}/{len(queries)}")
                    # Add remaining queries as fallback entities
                    for remaining_query in queries[i:]:
                        results.append(self._create_fallback_entity(self._clean_query(remaining_query)))
                    break
                
                # Process individual entity
                entity_result = await self.get_entity_info(query, enrich_with_nlp=enrich_with_nlp)
                results.append(entity_result)
                
                # Small delay between requests to be respectful to the API
                if i < len(queries) - 1:  # Don't delay after the last request
                    await asyncio.sleep(0.1)  # 100ms delay
                
            except Exception as e:
                logger.error(f"❌ Batch processing error for query '{query}': {e}")
                results.append(EntityResult(name=query, confidence_score=0.0))
        
        logger.info(f"✅ Batch processing completed: {len(results)} results")
        return results
    
    async def search_entities(self, query: str, limit: int = 10, enrich_with_nlp: bool = False) -> Dict[str, Any]:
        """
        Search for multiple entities in Knowledge Graph with enhanced results
        
        Args:
            query: Search query
            limit: Maximum number of results (capped at 20)
            enrich_with_nlp: Whether to enrich results with Natural Language analysis
            
        Returns:
            Dictionary with enhanced entity search results
        """
        try:
            if not query or not query.strip():
                return {'itemListElement': [], 'query': query, 'total_results': 0}
            
            # Limit the number of results
            limit = min(limit, 20)
            clean_query = self._clean_query(query)
            
            logger.debug(f"🔍 Entity search for: '{clean_query}' (limit: {limit})")
            
            # Check cache
            cache_key = self._get_cache_key(f"search_{clean_query}_{limit}_{enrich_with_nlp}")
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.debug(f"📦 Cache hit for search: {clean_query}")
                return cached_result
            
            # Rate limiting check
            if not self.rate_limiter.can_make_request():
                logger.warning(f"⚠️ Rate limit reached for search: {clean_query}")
                return self._create_fallback_search_result(clean_query)
            
            entities = []
            
            if self.knowledge_graph_available:
                try:
                    # Make Knowledge Graph API request
                    kg_response = await self._make_kg_request(clean_query, limit=limit)
                    self.rate_limiter.record_request()
                    
                    if kg_response.get('itemListElement'):
                        # Process each entity result
                        for item in kg_response['itemListElement']:
                            result_data = item.get('result', {})
                            
                            entity_result = {
                                'result': {
                                    '@type': result_data.get('@type', []),
                                    'name': result_data.get('name', ''),
                                    'description': self._extract_description(result_data),
                                    'url': result_data.get('url'),
                                    'entity_id': result_data.get('@id'),
                                    'industry': self._extract_industry(result_data)
                                },
                                'resultScore': item.get('resultScore', 0)
                            }
                            
                            # NLP enrichment if requested
                            if enrich_with_nlp and self.natural_language_client and entity_result['result']['description']:
                                try:
                                    nlp_analysis = await self._analyze_entity_with_nlp(entity_result['result']['description'])
                                    entity_result['result']['nlp_analysis'] = nlp_analysis
                                except Exception as nlp_error:
                                    logger.warning(f"⚠️ NLP enrichment failed for entity: {nlp_error}")
                            
                            entities.append(entity_result)
                        
                        logger.info(f"✅ Found {len(entities)} entities for: {clean_query}")
                    else:
                        logger.debug(f"🔍 No entities found for: {clean_query}")
                        
                except Exception as kg_error:
                    logger.error(f"❌ Knowledge Graph search error: {kg_error}")
            
            # Fallback result if no KG results
            if not entities:
                entities = [self._create_fallback_search_item(clean_query)]
            
            # Prepare response
            search_result = {
                'itemListElement': entities,
                'query': query,
                'clean_query': clean_query,
                'total_results': len(entities),
                'enriched_with_nlp': enrich_with_nlp,
                'timestamp': datetime.utcnow().isoformat(),
                '@context': {
                    '@vocab': 'http://schema.org/',
                    'goog': 'http://schema.googleapis.com/',
                    'resultScore': 'goog:resultScore',
                    'detailedDescription': 'goog:detailedDescription',
                    'EntitySearchResult': 'goog:EntitySearchResult',
                    'kg': 'http://g.co/kg'
                }
            }
            
            # Cache the result
            self._cache_result(cache_key, search_result)
            
            return search_result
            
        except Exception as e:
            logger.error(f"❌ Entity search failed for '{query}': {e}")
            return {'itemListElement': [], 'query': query, 'error': str(e)}
    
    def search_entities_sync(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Synchronous wrapper for search_entities - backward compatibility
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Fallback for running in async context
                return self._create_fallback_search_result(self._clean_query(query))
            else:
                return loop.run_until_complete(self.search_entities(query, limit, enrich_with_nlp=False))
        except Exception as e:
            logger.error(f"❌ Sync search failed: {e}")
            return {'itemListElement': []}
    
    def _create_fallback_entity(self, query: str) -> EntityResult:
        """Create a fallback entity result when APIs are unavailable"""
        return EntityResult(
            name=query,
            description=f"Business entity: {query}",
            types=["Organization", "Corporation"],
            url=f"https://{query}" if '.' in query else None,
            industry=self._infer_industry_from_domain(query),
            confidence_score=0.3  # Low confidence for fallback
        )
    
    def _create_fallback_search_result(self, query: str) -> Dict[str, Any]:
        """Create fallback search result when rate limited or API unavailable"""
        fallback_item = self._create_fallback_search_item(query)
        
        return {
            'itemListElement': [fallback_item],
            'query': query,
            'total_results': 1,
            'fallback': True,
            'reason': 'rate_limited_or_api_unavailable'
        }
    
    def _create_fallback_search_item(self, query: str) -> Dict[str, Any]:
        """Create fallback search item structure"""
        entity_data = {
            '@type': ["Organization", "Corporation"],
            'name': query,
            'description': f"Business entity: {query}",
            'url': f"https://{query}" if '.' in query else None,
            'industry': self._infer_industry_from_domain(query)
        }
        
        return {
            'result': entity_data,
            'resultScore': self._calculate_result_score(entity_data)
        }
    
    # Helper methods for API integration
    
    async def _make_kg_request(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Make a request to Google Knowledge Graph API
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            API response dictionary
        """
        if not self.api_key or not GOOGLE_CLOUD_AVAILABLE:
            raise Exception("Knowledge Graph API not available")
        
        url = "https://kgsearch.googleapis.com/v1/entities:search"
        params = {
            'query': query,
            'key': self.api_key,
            'limit': limit,
            'indent': True
        }
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.get(url, params=params, timeout=30)
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Knowledge Graph API error: {response.status_code} - {response.text}")
    
    async def _analyze_entity_with_nlp(self, text: str) -> Dict[str, Any]:
        """
        Analyze text with Google Natural Language API
        
        Args:
            text: Text to analyze
            
        Returns:
            NLP analysis results
        """
        if not self.natural_language_client:
            return {}
        
        try:
            document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)
            
            # Run entity analysis in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Analyze entities
            entity_response = await loop.run_in_executor(
                None,
                self.natural_language_client.analyze_entities,
                document
            )
            
            # Analyze sentiment
            sentiment_response = await loop.run_in_executor(
                None,
                self.natural_language_client.analyze_sentiment,
                document
            )
            
            # Process results
            entities = []
            for entity in entity_response.entities:
                entities.append({
                    'name': entity.name,
                    'type': entity.type_.name,
                    'salience': entity.salience,
                    'mentions': [{
                        'text': mention.text.content,
                        'type': mention.type_.name
                    } for mention in entity.mentions[:3]]  # Limit mentions
                })
            
            return {
                'entities': entities,
                'sentiment': {
                    'score': sentiment_response.document_sentiment.score,
                    'magnitude': sentiment_response.document_sentiment.magnitude
                },
                'language': entity_response.language
            }
            
        except Exception as e:
            logger.error(f"❌ Natural Language analysis failed: {e}")
            return {}
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize query string"""
        if not query:
            return ""
        
        # Remove protocols and www
        clean_query = query.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Remove path from URLs
        if '/' in clean_query:
            clean_query = clean_query.split('/')[0]
        
        return clean_query.strip()
    
    def _get_cache_key(self, identifier: str) -> str:
        """Generate cache key for given identifier"""
        return hashlib.md5(identifier.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve item from cache if not expired"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                return cached_item['data']
            else:
                # Remove expired item
                del self.cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, data: Any):
        """Store result in cache with timestamp"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Simple cache cleanup - remove oldest items if cache gets too large
        if len(self.cache) > 1000:
            # Remove 20% of oldest items
            items_to_remove = sorted(self.cache.items(), key=lambda x: x[1]['timestamp'])[:200]
            for key, _ in items_to_remove:
                del self.cache[key]
    
    def _extract_description(self, result_data: Dict[str, Any]) -> str:
        """Extract description from Knowledge Graph result"""
        description = result_data.get('description', '')
        
        # Try detailed description if basic description not available
        if not description and 'detailedDescription' in result_data:
            detailed = result_data['detailedDescription']
            if isinstance(detailed, dict):
                description = detailed.get('articleBody', '')
        
        return description or f"Entity: {result_data.get('name', 'Unknown')}"
    
    def _extract_industry(self, result_data: Dict[str, Any]) -> str:
        """Extract industry from Knowledge Graph result"""
        types = result_data.get('@type', [])
        
        # Map Knowledge Graph types to industries
        industry_mapping = {
            'Corporation': 'business',
            'Organization': 'organization',
            'Company': 'business',
            'TechCompany': 'technology',
            'SoftwareApplication': 'technology',
            'WebSite': 'technology',
            'MediaObject': 'media',
            'NewsMediaOrganization': 'media'
        }
        
        for entity_type in types:
            if entity_type in industry_mapping:
                return industry_mapping[entity_type]
        
        # Fallback to domain-based inference
        name = result_data.get('name', '')
        url = result_data.get('url', '')
        domain = url if url else name
        
        return self._infer_industry_from_domain(domain)
    
    def _extract_industry_from_nlp(self, nlp_analysis: Dict[str, Any]) -> str:
        """Extract industry from NLP analysis results"""
        entities = nlp_analysis.get('entities', [])
        
        # Look for organization or commercial entities
        for entity in entities:
            if entity.get('type') == 'ORGANIZATION' and entity.get('salience', 0) > 0.3:
                return 'organization'
            elif entity.get('type') == 'COMMERCIAL' and entity.get('salience', 0) > 0.2:
                return 'business'
        
        return 'unknown'
    
    def _infer_industry_from_domain(self, domain: str) -> str:
        """Infer industry from domain name - enhanced version"""
        if not domain:
            return "unknown"
        
        domain_lower = domain.lower()
        
        # Enhanced industry detection patterns
        industry_patterns = {
            'technology': ['tech', 'soft', 'ware', 'sys', 'data', 'cloud', 'api', 'dev', 'code', 'cyber', 'digital', 'ai', 'ml'],
            'telecommunications': ['telecom', 'mobile', 'wireless', 'mvno', 'cellular', 'broadband', 'fiber', 'network'],
            'professional_services': ['consult', 'service', 'solution', 'partner', 'advisory', 'strategy', 'manage'],
            'media': ['media', 'news', 'publish', 'content', 'blog', 'journal', 'press', 'broadcast'],
            'research': ['research', 'analytics', 'insights', 'study', 'survey', 'analysis', 'data'],
            'finance': ['bank', 'finance', 'invest', 'capital', 'fund', 'credit', 'loan', 'payment'],
            'healthcare': ['health', 'medical', 'pharma', 'clinic', 'hospital', 'care', 'wellness'],
            'education': ['edu', 'school', 'university', 'college', 'learn', 'training', 'course'],
            'retail': ['shop', 'store', 'retail', 'ecommerce', 'marketplace', 'buy', 'sell'],
            'manufacturing': ['manufacturing', 'industrial', 'factory', 'production', 'supply']
        }
        
        for industry, keywords in industry_patterns.items():
            if any(keyword in domain_lower for keyword in keywords):
                return industry
        
        return "business_services"
    
    def _calculate_result_score(self, entity_info: Dict[str, Any]) -> float:
        """
        Calculate a result score for the entity based on available information
        
        Args:
            entity_info: Entity information dictionary
            
        Returns:
            Score between 0 and 1000 (typical Knowledge Graph range)
        """
        score = 100.0  # Base score
        
        # Increase score based on available information
        if entity_info.get('description'):
            score += 200
        if entity_info.get('url'):
            score += 150
        if entity_info.get('industry'):
            score += 100
        if entity_info.get('@type'):
            score += 50
        if entity_info.get('entity_id'):  # Has official Knowledge Graph ID
            score += 300
        if entity_info.get('nlp_analysis'):  # Has NLP enrichment
            score += 100
        
        return min(score, 1000.0)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'cache_ttl_hours': self.cache_ttl / 3600,
            'cache_size_estimate_kb': len(str(self.cache)) / 1024
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("🧽 Cache cleared")
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limiting status"""
        return {
            'can_make_request': self.rate_limiter.can_make_request(),
            'daily_calls_made': self.rate_limiter.daily_calls,
            'daily_limit': self.rate_limiter.requests_per_day,
            'daily_remaining': self.rate_limiter.requests_per_day - self.rate_limiter.daily_calls,
            'minute_calls': len(self.rate_limiter.minute_calls),
            'minute_limit': self.rate_limiter.requests_per_minute,
            'minute_remaining': self.rate_limiter.requests_per_minute - len(self.rate_limiter.minute_calls),
            'daily_reset': self.rate_limiter.daily_reset.isoformat()
        }

# Backward compatibility methods (keep existing interface)
# These methods wrap the new async methods to maintain compatibility

    def get_entity_info_sync(self, query: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for backward compatibility
        Returns entity info in the original format
        """
        try:
            # Run the async method
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, we can't use run()
                # Return a basic result for now
                return self._create_fallback_entity(self._clean_query(query)).__dict__
            else:
                entity_result = loop.run_until_complete(self.get_entity_info(query, enrich_with_nlp=False))
                # Convert EntityResult to dict format
                return {
                    "@type": entity_result.types,
                    "name": entity_result.name,
                    "description": entity_result.description,
                    "url": entity_result.url,
                    "industry": entity_result.industry
                }
        except Exception as e:
            logger.error(f"❌ Sync entity info failed: {e}")
            return {}


# Global instance (singleton pattern)
_knowledge_graph_client = None

def get_knowledge_graph_client(config: Optional[Dict[str, Any]] = None) -> KnowledgeGraphClient:
    """Get the global Knowledge Graph client instance"""
    global _knowledge_graph_client
    
    if _knowledge_graph_client is None:
        _knowledge_graph_client = KnowledgeGraphClient(config)
    
    return _knowledge_graph_client
