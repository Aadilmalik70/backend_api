"""
Competitor Content Acquisition Client - Advanced competitor analysis and content intelligence

Comprehensive competitor content analysis system for the data acquisition pipeline,
providing deep insights into competitor strategies, content structures, and optimization opportunities.

Features:
- Multi-source competitor identification (SERP results, domain analysis)
- Advanced web scraping with content extraction and analysis
- Content quality scoring and competitive gap analysis
- Heading structure analysis and content optimization insights
- Social signals and technical performance metrics
- Content format identification and recommendation engine
- Rate limiting and intelligent caching for performance

Data Sources:
- Google SERP results for competitor identification
- Direct competitor page analysis with content extraction
- Technical performance metrics and SEO analysis
- Social media signals and engagement metrics
- Content structure and heading hierarchy analysis

Performance: <10s response time, intelligent rate limiting, comprehensive caching
"""

import asyncio
import logging
import json
import time
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple, Union
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup, Tag
import aiohttp
from collections import Counter, defaultdict
from enum import Enum

from .async_request_manager import AsyncRequestManager, RequestConfig, RequestMethod
from .data_models import CompetitorContentData, CompetitorPage, DataSourceType, ContentType
from .rate_limiter import RateLimiter, RateLimitStrategy

# Import existing Google APIs and SERP infrastructure
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from utils.serpapi_utils import SerpAPIClient
    from utils.google_apis.api_manager import GoogleAPIManager
    from services.migration_manager import MigrationManager
    SERP_APIS_AVAILABLE = True
except ImportError:
    SERP_APIS_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CompetitorConfig:
    """Configuration for competitor content client"""
    # Competitor identification
    max_competitors: int = 20
    min_competitor_score: float = 0.3
    include_local_results: bool = True
    include_featured_snippets: bool = True
    
    # Content analysis
    max_content_length: int = 50000  # Characters
    extract_images: bool = True
    analyze_social_signals: bool = True
    technical_analysis: bool = True
    
    # Performance settings
    request_timeout: float = 15.0
    max_retries: int = 2
    concurrent_requests: int = 5
    cache_duration: int = 3600  # 1 hour
    
    # Rate limiting
    requests_per_minute: int = 120  # Conservative for web scraping
    burst_limit: int = 30

class ContentAnalysisEngine:
    """Advanced content analysis and scoring engine"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Content quality indicators
        self.quality_indicators = {
            'readability': ['clear', 'simple', 'easy', 'understand', 'guide'],
            'authority': ['research', 'study', 'expert', 'professional', 'authority'],
            'completeness': ['complete', 'comprehensive', 'detailed', 'thorough', 'extensive'],
            'freshness': ['2024', '2025', 'latest', 'updated', 'recent', 'new']
        }
        
        # Technical SEO factors
        self.technical_factors = [
            'meta_description_length', 'title_length', 'heading_structure',
            'image_alt_text', 'internal_links', 'external_links', 'word_count'
        ]
    
    def analyze_content_quality(self, page: CompetitorPage, html_content: str) -> float:
        """Comprehensive content quality analysis"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            quality_scores = []
            
            # Content structure score
            structure_score = self._analyze_content_structure(soup)
            quality_scores.append(('structure', structure_score, 0.25))
            
            # Readability score
            readability_score = self._analyze_readability(soup)
            quality_scores.append(('readability', readability_score, 0.20))
            
            # Authority signals score
            authority_score = self._analyze_authority_signals(soup, page.title, page.meta_description)
            quality_scores.append(('authority', authority_score, 0.20))
            
            # Technical SEO score
            technical_score = self._analyze_technical_seo(soup, page)
            quality_scores.append(('technical', technical_score, 0.15))
            
            # Content completeness score
            completeness_score = self._analyze_completeness(soup, page.content_length)
            quality_scores.append(('completeness', completeness_score, 0.20))
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in quality_scores)
            
            # Log detailed scoring for debugging
            self.logger.debug(f"Quality analysis for {page.url}: {dict((name, f'{score:.2f}') for name, score, _ in quality_scores)} = {total_score:.2f}")
            
            return min(1.0, max(0.0, total_score))
            
        except Exception as e:
            self.logger.error(f"Content quality analysis failed: {e}")
            return 0.5  # Default score
    
    def _analyze_content_structure(self, soup: BeautifulSoup) -> float:
        """Analyze heading hierarchy and content structure"""
        try:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            if not headings:
                return 0.3  # No headings is poor structure
            
            # Check for proper hierarchy
            heading_levels = [int(h.name[1]) for h in headings]
            
            structure_factors = []
            
            # H1 presence and uniqueness
            h1_count = heading_levels.count(1)
            structure_factors.append(0.9 if h1_count == 1 else (0.7 if h1_count > 0 else 0.3))
            
            # H2-H6 distribution
            h2_h6_count = len([level for level in heading_levels if level > 1])
            structure_factors.append(min(1.0, h2_h6_count / 8.0))  # Good if 8+ subheadings
            
            # Hierarchy logic (no level skipping)
            hierarchy_score = 1.0
            for i in range(1, len(heading_levels)):
                level_diff = heading_levels[i] - heading_levels[i-1]
                if level_diff > 1:  # Skipped a level
                    hierarchy_score *= 0.9
            structure_factors.append(hierarchy_score)
            
            return sum(structure_factors) / len(structure_factors)
            
        except Exception as e:
            self.logger.error(f"Structure analysis error: {e}")
            return 0.5
    
    def _analyze_readability(self, soup: BeautifulSoup) -> float:
        """Analyze content readability factors"""
        try:
            # Get main content text
            content_text = soup.get_text()
            
            # Calculate readability metrics
            sentences = re.split(r'[.!?]+', content_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            words = content_text.split()
            
            if not sentences or not words:
                return 0.3
            
            # Average sentence length (12-20 words is ideal)
            avg_sentence_length = len(words) / len(sentences)
            sentence_score = 1.0 - abs(avg_sentence_length - 16) / 16.0
            sentence_score = max(0.0, min(1.0, sentence_score))
            
            # Paragraph structure
            paragraphs = soup.find_all('p')
            if paragraphs:
                avg_paragraph_length = len(words) / len(paragraphs)
                paragraph_score = 1.0 - abs(avg_paragraph_length - 50) / 50.0  # 50 words ideal
                paragraph_score = max(0.0, min(1.0, paragraph_score))
            else:
                paragraph_score = 0.3
            
            # List usage (improves readability)
            lists = soup.find_all(['ul', 'ol'])
            list_score = min(1.0, len(lists) / 5.0)  # Good if 5+ lists
            
            # Image usage
            images = soup.find_all('img')
            image_score = min(1.0, len(images) / 10.0)  # Good if 10+ images
            
            return (sentence_score * 0.4 + paragraph_score * 0.3 + 
                   list_score * 0.15 + image_score * 0.15)
            
        except Exception as e:
            self.logger.error(f"Readability analysis error: {e}")
            return 0.5
    
    def _analyze_authority_signals(self, soup: BeautifulSoup, title: str, meta_desc: str) -> float:
        """Analyze content authority and credibility signals"""
        try:
            content_text = (title + " " + meta_desc + " " + soup.get_text()).lower()
            authority_factors = []
            
            # Authority keyword presence
            for category, keywords in self.quality_indicators.items():
                if category == 'authority':
                    keyword_matches = sum(1 for keyword in keywords if keyword in content_text)
                    authority_factors.append(min(1.0, keyword_matches / 3.0))
            
            # External link analysis
            external_links = [
                a for a in soup.find_all('a', href=True)
                if 'http' in a['href'] and not any(domain in a['href'] for domain in ['facebook', 'twitter', 'instagram'])
            ]
            external_score = min(1.0, len(external_links) / 10.0)
            authority_factors.append(external_score)
            
            # Citation patterns (numbers, statistics, dates)
            citations = len(re.findall(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?%?\b', content_text))
            citation_score = min(1.0, citations / 20.0)
            authority_factors.append(citation_score)
            
            # Date/freshness indicators
            freshness_indicators = self.quality_indicators['freshness']
            freshness_matches = sum(1 for indicator in freshness_indicators if indicator in content_text)
            freshness_score = min(1.0, freshness_matches / 2.0)
            authority_factors.append(freshness_score)
            
            return sum(authority_factors) / len(authority_factors) if authority_factors else 0.5
            
        except Exception as e:
            self.logger.error(f"Authority analysis error: {e}")
            return 0.5
    
    def _analyze_technical_seo(self, soup: BeautifulSoup, page: CompetitorPage) -> float:
        """Analyze technical SEO factors"""
        try:
            technical_scores = []
            
            # Meta description analysis
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc_length = len(meta_desc['content'])
                meta_score = 1.0 if 120 <= desc_length <= 160 else 0.7 if desc_length > 0 else 0.0
            else:
                meta_score = 0.0
            technical_scores.append(meta_score)
            
            # Title tag analysis
            title_length = len(page.title)
            title_score = 1.0 if 30 <= title_length <= 60 else 0.7 if title_length > 0 else 0.0
            technical_scores.append(title_score)
            
            # Image alt text coverage
            images = soup.find_all('img')
            if images:
                images_with_alt = [img for img in images if img.get('alt')]
                alt_coverage = len(images_with_alt) / len(images)
                technical_scores.append(alt_coverage)
            else:
                technical_scores.append(1.0)  # No images = no problem
            
            # Internal linking
            internal_links = soup.find_all('a', href=True)
            internal_links = [a for a in internal_links if not a['href'].startswith('http')]
            internal_score = min(1.0, len(internal_links) / 20.0)
            technical_scores.append(internal_score)
            
            # Schema markup presence
            schema_scripts = soup.find_all('script', type='application/ld+json')
            schema_score = 1.0 if schema_scripts else 0.5
            technical_scores.append(schema_score)
            
            return sum(technical_scores) / len(technical_scores)
            
        except Exception as e:
            self.logger.error(f"Technical SEO analysis error: {e}")
            return 0.5
    
    def _analyze_completeness(self, soup: BeautifulSoup, content_length: int) -> float:
        """Analyze content completeness and depth"""
        try:
            completeness_factors = []
            
            # Content length analysis (1500-3000 words is often ideal)
            word_count = len(soup.get_text().split())
            if 1500 <= word_count <= 3000:
                length_score = 1.0
            elif 1000 <= word_count <= 5000:
                length_score = 0.8
            elif word_count > 500:
                length_score = 0.6
            else:
                length_score = 0.3
            completeness_factors.append(length_score)
            
            # Section diversity (multiple H2s indicate comprehensive coverage)
            h2_headings = soup.find_all('h2')
            section_score = min(1.0, len(h2_headings) / 8.0)
            completeness_factors.append(section_score)
            
            # Media richness (images, videos, etc.)
            media_elements = soup.find_all(['img', 'video', 'iframe', 'canvas'])
            media_score = min(1.0, len(media_elements) / 15.0)
            completeness_factors.append(media_score)
            
            # List and table presence (structured information)
            structured_elements = soup.find_all(['ul', 'ol', 'table', 'dl'])
            structure_score = min(1.0, len(structured_elements) / 8.0)
            completeness_factors.append(structure_score)
            
            return sum(completeness_factors) / len(completeness_factors)
            
        except Exception as e:
            self.logger.error(f"Completeness analysis error: {e}")
            return 0.5

class CompetitorContentClient:
    """
    Advanced competitor content acquisition and analysis client.
    Provides comprehensive competitor intelligence for content strategy optimization.
    """
    
    def __init__(self, config: Optional[CompetitorConfig] = None):
        """Initialize competitor content client"""
        self.config = config or CompetitorConfig()
        self.logger = logging.getLogger(__name__)
        
        # Request management
        self.request_manager = AsyncRequestManager()
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.requests_per_minute,
            burst_limit=self.config.burst_limit,
            strategy=RateLimitStrategy.ADAPTIVE  # Adaptive for web scraping
        )
        
        # Content analysis engine
        self.content_analyzer = ContentAnalysisEngine()
        
        # SERP APIs integration
        self.serpapi_client = None
        self.google_api_manager = None
        self.migration_manager = None
        
        if SERP_APIS_AVAILABLE:
            try:
                self.serpapi_client = SerpAPIClient()
                self.google_api_manager = GoogleAPIManager()
                self.migration_manager = MigrationManager()
            except Exception as e:
                self.logger.warning(f"SERP APIs not fully available: {e}")
        
        # Caching and performance
        self.competitor_cache: Dict[str, Tuple[CompetitorContentData, float]] = {}
        self.page_cache: Dict[str, Tuple[CompetitorPage, float]] = {}
        self.cache_ttl = self.config.cache_duration
        
        # Performance metrics
        self.request_metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'total_pages_analyzed': 0,
            'average_analysis_time': 0.0
        }
        
        # User agent rotation for web scraping
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        
        self.logger.info("Competitor Content Client initialized")
    
    async def initialize(self):
        """Initialize client components"""
        try:
            self.logger.info("🚀 Initializing Competitor Content Client...")
            
            # Initialize request manager
            await self.request_manager.initialize()
            
            # Initialize SERP APIs if available
            if self.serpapi_client:
                await self.serpapi_client.initialize()
                self.logger.info("✅ SerpAPI integration enabled")
            
            if self.google_api_manager:
                await self.google_api_manager.initialize()
                self.logger.info("✅ Google APIs integration enabled")
            
            if self.migration_manager:
                await self.migration_manager.initialize()
                self.logger.info("✅ Migration manager enabled for fallback")
            
            self.logger.info("✅ Competitor Content Client initialization complete")
            
        except Exception as e:
            self.logger.error(f"Competitor Content Client initialization failed: {e}")
            raise
    
    async def get_competitor_content(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive competitor content analysis
        
        Args:
            query: The search query to analyze competitors for
            context: Additional context for customization
            
        Returns:
            Dictionary with structured competitor content data and insights
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
                self.logger.debug(f"Cache hit for competitor analysis query: {query}")
                return self._format_api_response(cached_result)
            
            # Check rate limiter
            if not await self.rate_limiter.acquire():
                raise Exception("Rate limit exceeded for competitor content analysis")
            
            # Step 1: Identify competitors from SERP results
            competitors = await self._identify_competitors(query, context)
            
            if not competitors:
                self.logger.warning(f"No competitors found for query: {query}")
                return self._create_empty_result(query, "No competitors found in search results")
            
            # Step 2: Analyze competitor pages in parallel
            analyzed_pages = await self._analyze_competitor_pages(competitors, context)
            
            # Step 3: Generate competitive insights
            competitive_data = await self._generate_competitive_insights(query, analyzed_pages, context)
            
            # Cache the result
            self._cache_result(cache_key, competitive_data)
            
            # Update metrics
            execution_time = time.time() - start_time
            self._update_metrics(True, execution_time, len(analyzed_pages))
            
            self.logger.info(f"Competitor analysis completed for '{query}': {len(analyzed_pages)} pages analyzed")
            
            return self._format_api_response(competitive_data)
            
        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(False, execution_time, 0)
            self.logger.error(f"Failed to analyze competitor content for '{query}': {e}")
            
            return self._create_error_result(query, str(e))
    
    async def _identify_competitors(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify competitor URLs from search results"""
        try:
            competitors = []
            
            # Try to get SERP results from available APIs
            if self.serpapi_client:
                serp_results = await self._get_serpapi_competitors(query, context)
                if serp_results:
                    competitors.extend(serp_results)
            
            # Try Google Custom Search as fallback
            if not competitors and self.google_api_manager:
                google_results = await self._get_google_search_competitors(query, context)
                if google_results:
                    competitors.extend(google_results)
            
            # Filter and rank competitors
            competitors = self._filter_and_rank_competitors(competitors, query)
            
            return competitors[:self.config.max_competitors]
            
        except Exception as e:
            self.logger.error(f"Competitor identification failed: {e}")
            return []
    
    async def _get_serpapi_competitors(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get competitors from SerpAPI results"""
        try:
            if not self.serpapi_client:
                return []
            
            # Prepare SerpAPI parameters
            params = {
                'engine': 'google',
                'q': query,
                'location': context.get('location', 'United States'),
                'hl': context.get('language', 'en'),
                'num': 20  # Get more results for better competitor analysis
            }
            
            results = await self.serpapi_client.search(params)
            
            if not results or 'organic_results' not in results:
                return []
            
            competitors = []
            
            for i, result in enumerate(results['organic_results']):
                competitor = {
                    'url': result.get('link', ''),
                    'title': result.get('title', ''),
                    'description': result.get('snippet', ''),
                    'position': i + 1,
                    'source': 'serpapi',
                    'relevance_score': max(0.1, 1.0 - (i * 0.05))  # Decreasing relevance by position
                }
                
                if competitor['url'] and self._is_valid_competitor_url(competitor['url']):
                    competitors.append(competitor)
            
            # Include featured snippets if available
            if self.config.include_featured_snippets and 'featured_snippet' in results:
                snippet = results['featured_snippet']
                competitors.insert(0, {
                    'url': snippet.get('link', ''),
                    'title': snippet.get('title', ''),
                    'description': snippet.get('snippet', ''),
                    'position': 0,  # Featured snippet is position 0
                    'source': 'serpapi_featured',
                    'relevance_score': 1.0,
                    'is_featured': True
                })
            
            return competitors
            
        except Exception as e:
            self.logger.error(f"SerpAPI competitor search failed: {e}")
            return []
    
    async def _get_google_search_competitors(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get competitors from Google Custom Search API"""
        try:
            if not self.google_api_manager:
                return []
            
            search_params = {
                'q': query,
                'num': 10,
                'start': 1
            }
            
            results = await self.google_api_manager.custom_search(search_params)
            
            if not results or 'items' not in results:
                return []
            
            competitors = []
            
            for i, item in enumerate(results['items']):
                competitor = {
                    'url': item.get('link', ''),
                    'title': item.get('title', ''),
                    'description': item.get('snippet', ''),
                    'position': i + 1,
                    'source': 'google_custom_search',
                    'relevance_score': max(0.1, 1.0 - (i * 0.1))
                }
                
                if competitor['url'] and self._is_valid_competitor_url(competitor['url']):
                    competitors.append(competitor)
            
            return competitors
            
        except Exception as e:
            self.logger.error(f"Google Custom Search competitor search failed: {e}")
            return []
    
    def _is_valid_competitor_url(self, url: str) -> bool:
        """Validate if URL is suitable for competitor analysis"""
        if not url or not url.startswith('http'):
            return False
        
        # Parse URL
        parsed = urlparse(url)
        
        # Filter out common non-competitor domains
        excluded_domains = [
            'youtube.com', 'facebook.com', 'twitter.com', 'instagram.com',
            'linkedin.com', 'pinterest.com', 'reddit.com', 'quora.com',
            'amazon.com', 'ebay.com', 'etsy.com',  # E-commerce giants
            'wikipedia.org', 'github.com', 'stackoverflow.com'  # Reference sites
        ]
        
        domain = parsed.netloc.lower()
        if any(excluded in domain for excluded in excluded_domains):
            return False
        
        # Check for valid file extensions (exclude PDFs, docs, etc.)
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        return True
    
    def _filter_and_rank_competitors(self, competitors: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Filter and rank competitors based on relevance and quality"""
        if not competitors:
            return []
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_competitors = []
        
        for competitor in competitors:
            url = competitor.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                unique_competitors.append(competitor)
        
        # Score competitors based on multiple factors
        for competitor in unique_competitors:
            score = competitor.get('relevance_score', 0.5)
            
            # Boost score for featured snippets
            if competitor.get('is_featured'):
                score *= 1.2
            
            # Boost score for title/description relevance
            title = competitor.get('title', '').lower()
            description = competitor.get('description', '').lower()
            query_lower = query.lower()
            
            query_words = query_lower.split()
            title_matches = sum(1 for word in query_words if word in title)
            desc_matches = sum(1 for word in query_words if word in description)
            
            relevance_boost = (title_matches * 0.1) + (desc_matches * 0.05)
            score += relevance_boost
            
            # Penalize very low positions
            position = competitor.get('position', 10)
            if position > 15:
                score *= 0.8
            
            competitor['final_score'] = min(1.0, score)
        
        # Filter by minimum score and sort by final score
        filtered_competitors = [
            c for c in unique_competitors 
            if c.get('final_score', 0) >= self.config.min_competitor_score
        ]
        
        filtered_competitors.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        
        return filtered_competitors
    
    async def _analyze_competitor_pages(
        self, 
        competitors: List[Dict[str, Any]], 
        context: Dict[str, Any]
    ) -> List[CompetitorPage]:
        """Analyze competitor pages in parallel with rate limiting"""
        analyzed_pages = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)
        
        # Create analysis tasks
        tasks = []
        for competitor in competitors:
            task = self._analyze_single_page(competitor, context, semaphore)
            tasks.append(task)
        
        # Execute tasks and collect results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, CompetitorPage):
                analyzed_pages.append(result)
            elif isinstance(result, Exception):
                self.logger.warning(f"Page analysis failed: {result}")
        
        return analyzed_pages
    
    async def _analyze_single_page(
        self, 
        competitor: Dict[str, Any], 
        context: Dict[str, Any],
        semaphore: asyncio.Semaphore
    ) -> Optional[CompetitorPage]:
        """Analyze a single competitor page"""
        async with semaphore:
            try:
                url = competitor.get('url', '')
                if not url:
                    return None
                
                # Check page cache
                page_cache_key = self._generate_page_cache_key(url)
                cached_page = self._get_cached_page(page_cache_key)
                if cached_page:
                    return cached_page
                
                # Rate limiting
                if not await self.rate_limiter.acquire():
                    self.logger.warning(f"Rate limited while analyzing: {url}")
                    return None
                
                # Fetch page content
                html_content = await self._fetch_page_content(url)
                if not html_content:
                    return None
                
                # Parse and analyze content
                page = await self._parse_page_content(url, html_content, competitor)
                
                # Cache the page
                if page:
                    self._cache_page(page_cache_key, page)
                
                return page
                
            except Exception as e:
                self.logger.error(f"Failed to analyze page {competitor.get('url', 'unknown')}: {e}")
                return None
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch HTML content from competitor page"""
        try:
            # Random user agent to avoid blocks
            import random
            user_agent = random.choice(self.user_agents)
            
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            request_config = RequestConfig(
                method=RequestMethod.GET,
                url=url,
                headers=headers,
                timeout=self.config.request_timeout,
                retries=self.config.max_retries,
                follow_redirects=True
            )
            
            result = await self.request_manager.execute_request(request_config)
            
            if result.success and result.data:
                if isinstance(result.data, str):
                    return result.data
                elif hasattr(result.data, 'text'):
                    return await result.data.text()
                else:
                    return str(result.data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to fetch content from {url}: {e}")
            return None
    
    async def _parse_page_content(
        self, 
        url: str, 
        html_content: str, 
        competitor: Dict[str, Any]
    ) -> Optional[CompetitorPage]:
        """Parse and analyze page content structure"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract basic metadata
            title = self._extract_title(soup, competitor.get('title', ''))
            meta_description = self._extract_meta_description(soup)
            content_length = len(soup.get_text().strip())
            
            # Extract headings structure
            headings = self._extract_headings(soup)
            
            # Extract keywords from content
            keywords = self._extract_keywords(soup, title, meta_description)
            
            # Determine content type
            content_type = self._classify_content_type(soup, url, title)
            
            # Calculate quality and authority scores
            quality_score = self.content_analyzer.analyze_content_quality(
                CompetitorPage(url=url, title=title, content_length=content_length),
                html_content
            )
            
            authority_score = self._calculate_authority_score(soup, url)
            
            # Extract technical metrics
            technical_metrics = self._extract_technical_metrics(soup)
            
            # Extract social signals if configured
            social_signals = {}
            if self.config.analyze_social_signals:
                social_signals = await self._extract_social_signals(soup, url)
            
            page = CompetitorPage(
                url=url,
                title=title,
                content_length=content_length,
                headings=headings,
                meta_description=meta_description,
                keywords=keywords,
                content_type=content_type,
                quality_score=quality_score,
                authority_score=authority_score,
                social_signals=social_signals,
                technical_metrics=technical_metrics,
                collection_timestamp=datetime.utcnow()
            )
            
            return page
            
        except Exception as e:
            self.logger.error(f"Failed to parse content from {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, fallback_title: str) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            return title_tag.get_text().strip()[:200]  # Limit length
        
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.get_text().strip():
            return h1_tag.get_text().strip()[:200]
        
        return fallback_title[:200] if fallback_title else "Untitled Page"
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()[:500]
        
        # Fallback to first paragraph
        first_p = soup.find('p')
        if first_p and first_p.get_text().strip():
            return first_p.get_text().strip()[:500]
        
        return ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract heading structure"""
        headings = defaultdict(list)
        
        for level in range(1, 7):
            heading_tags = soup.find_all(f'h{level}')
            for tag in heading_tags:
                text = tag.get_text().strip()
                if text and len(text) <= 200:  # Reasonable heading length
                    headings[f'h{level}'].append(text)
        
        return dict(headings)
    
    def _extract_keywords(self, soup: BeautifulSoup, title: str, meta_description: str) -> List[str]:
        """Extract keywords from content"""
        try:
            # Combine title, meta description, and headings for keyword extraction
            text_sources = [title, meta_description]
            
            # Add heading text
            for level in range(1, 4):  # Focus on h1-h3
                headings = soup.find_all(f'h{level}')
                text_sources.extend([h.get_text() for h in headings])
            
            # Add first few paragraphs
            paragraphs = soup.find_all('p')[:5]
            text_sources.extend([p.get_text() for p in paragraphs])
            
            # Combine and process text
            combined_text = ' '.join(text_sources).lower()
            
            # Simple keyword extraction (would be more sophisticated in production)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', combined_text)
            
            # Filter out common stop words
            stop_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
                'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his',
                'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy',
                'did', 'doesn', 'each', 'few', 'she', 'use', 'your', 'way', 'many'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Get most common keywords
            word_counts = Counter(filtered_words)
            top_keywords = [word for word, count in word_counts.most_common(20) if count > 1]
            
            return top_keywords
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return []
    
    def _classify_content_type(self, soup: BeautifulSoup, url: str, title: str) -> ContentType:
        """Classify the type of content"""
        try:
            # Check URL patterns
            url_lower = url.lower()
            title_lower = title.lower()
            
            # Product page indicators
            if any(indicator in url_lower for indicator in ['/product/', '/item/', 'shop', 'buy']):
                return ContentType.PRODUCT_PAGE
            
            # Blog post indicators
            if any(indicator in url_lower for indicator in ['/blog/', '/post/', '/article/', 'news']):
                return ContentType.BLOG_POST
            
            # FAQ indicators
            if any(indicator in title_lower for indicator in ['faq', 'frequently asked', 'questions']):
                return ContentType.FAQ
            
            # Guide indicators
            if any(indicator in title_lower for indicator in ['guide', 'tutorial', 'how to', 'step by step']):
                return ContentType.GUIDE
            
            # Landing page indicators (short content, CTA focus)
            content_length = len(soup.get_text())
            cta_elements = soup.find_all(['button', 'input'], string=re.compile(r'sign up|subscribe|download|buy now', re.I))
            
            if content_length < 1500 and len(cta_elements) > 2:
                return ContentType.LANDING_PAGE
            
            # Default to article
            return ContentType.ARTICLE
            
        except Exception:
            return ContentType.ARTICLE
    
    def _calculate_authority_score(self, soup: BeautifulSoup, url: str) -> float:
        """Calculate domain authority score (simplified)"""
        try:
            authority_indicators = []
            
            # Domain age indicators (simplified heuristics)
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Well-known authoritative domains get higher scores
            high_authority_domains = ['.edu', '.gov', '.org']
            if any(domain.endswith(suffix) for suffix in high_authority_domains):
                authority_indicators.append(1.0)
            else:
                authority_indicators.append(0.5)
            
            # Content indicators
            external_links = len([a for a in soup.find_all('a', href=True) if 'http' in a['href']])
            authority_indicators.append(min(1.0, external_links / 20.0))
            
            # Contact/about page presence
            nav_links = soup.find_all('a', href=True)
            has_contact = any('contact' in link.get('href', '').lower() for link in nav_links)
            has_about = any('about' in link.get('href', '').lower() for link in nav_links)
            
            contact_about_score = (0.5 if has_contact else 0) + (0.5 if has_about else 0)
            authority_indicators.append(contact_about_score)
            
            # SSL certificate (https)
            ssl_score = 1.0 if url.startswith('https') else 0.3
            authority_indicators.append(ssl_score)
            
            return sum(authority_indicators) / len(authority_indicators)
            
        except Exception as e:
            self.logger.error(f"Authority score calculation failed: {e}")
            return 0.5
    
    def _extract_technical_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract technical SEO metrics"""
        try:
            metrics = {}
            
            # Page structure metrics
            metrics['total_images'] = len(soup.find_all('img'))
            metrics['images_with_alt'] = len([img for img in soup.find_all('img') if img.get('alt')])
            metrics['internal_links'] = len([a for a in soup.find_all('a', href=True) if not a['href'].startswith('http')])
            metrics['external_links'] = len([a for a in soup.find_all('a', href=True) if a['href'].startswith('http')])
            
            # Content metrics
            text_content = soup.get_text()
            metrics['word_count'] = len(text_content.split())
            metrics['character_count'] = len(text_content)
            
            # Heading metrics
            for level in range(1, 7):
                metrics[f'h{level}_count'] = len(soup.find_all(f'h{level}'))
            
            # Schema markup
            metrics['schema_scripts'] = len(soup.find_all('script', type='application/ld+json'))
            
            # Meta tags
            meta_tags = soup.find_all('meta')
            metrics['meta_tags_count'] = len(meta_tags)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Technical metrics extraction failed: {e}")
            return {}
    
    async def _extract_social_signals(self, soup: BeautifulSoup, url: str) -> Dict[str, int]:
        """Extract social media signals (simplified implementation)"""
        try:
            # This is a simplified implementation
            # In production, you'd integrate with social media APIs
            social_signals = {
                'facebook_shares': 0,
                'twitter_shares': 0,
                'linkedin_shares': 0,
                'pinterest_pins': 0
            }
            
            # Look for social share buttons/counts in HTML
            social_elements = soup.find_all(['span', 'div'], class_=re.compile(r'share|social', re.I))
            
            for element in social_elements:
                text = element.get_text().strip()
                if text.isdigit():
                    count = int(text)
                    
                    # Try to determine social platform based on nearby elements
                    if 'facebook' in str(element).lower():
                        social_signals['facebook_shares'] = max(social_signals['facebook_shares'], count)
                    elif 'twitter' in str(element).lower():
                        social_signals['twitter_shares'] = max(social_signals['twitter_shares'], count)
                    elif 'linkedin' in str(element).lower():
                        social_signals['linkedin_shares'] = max(social_signals['linkedin_shares'], count)
                    elif 'pinterest' in str(element).lower():
                        social_signals['pinterest_pins'] = max(social_signals['pinterest_pins'], count)
            
            return social_signals
            
        except Exception as e:
            self.logger.error(f"Social signals extraction failed: {e}")
            return {'facebook_shares': 0, 'twitter_shares': 0, 'linkedin_shares': 0, 'pinterest_pins': 0}
    
    async def _generate_competitive_insights(
        self, 
        query: str, 
        analyzed_pages: List[CompetitorPage], 
        context: Dict[str, Any]
    ) -> CompetitorContentData:
        """Generate comprehensive competitive insights"""
        try:
            if not analyzed_pages:
                return CompetitorContentData(query=query)
            
            # Calculate average content length
            content_lengths = [page.content_length for page in analyzed_pages]
            average_content_length = sum(content_lengths) // len(content_lengths)
            
            # Identify common topics from headings and keywords
            common_topics = self._identify_common_topics(analyzed_pages)
            
            # Identify content gaps
            content_gaps = await self._identify_content_gaps(query, analyzed_pages, context)
            
            # Identify top performing formats
            top_formats = self._identify_top_performing_formats(analyzed_pages)
            
            # Identify keyword opportunities
            keyword_opportunities = self._identify_keyword_opportunities(analyzed_pages, query)
            
            competitive_data = CompetitorContentData(
                query=query,
                analyzed_pages=analyzed_pages,
                content_gaps=content_gaps,
                common_topics=common_topics,
                average_content_length=average_content_length,
                top_performing_formats=top_formats,
                keyword_opportunities=keyword_opportunities,
                collection_timestamp=datetime.utcnow()
            )
            
            return competitive_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate competitive insights: {e}")
            return CompetitorContentData(query=query)
    
    def _identify_common_topics(self, analyzed_pages: List[CompetitorPage]) -> List[str]:
        """Identify topics that appear across multiple competitors"""
        try:
            topic_frequency = defaultdict(int)
            
            # Collect topics from headings and keywords
            for page in analyzed_pages:
                # Process headings
                for level, headings in page.headings.items():
                    for heading in headings:
                        # Extract key words from headings
                        words = re.findall(r'\b[a-zA-Z]{4,}\b', heading.lower())
                        for word in words:
                            topic_frequency[word] += 1
                
                # Process keywords
                for keyword in page.keywords:
                    topic_frequency[keyword] += 1
            
            # Filter topics that appear in multiple pages
            min_frequency = max(2, len(analyzed_pages) // 3)  # At least 1/3 of pages
            common_topics = [
                topic for topic, freq in topic_frequency.items() 
                if freq >= min_frequency
            ]
            
            # Sort by frequency and return top topics
            common_topics.sort(key=lambda x: topic_frequency[x], reverse=True)
            
            return common_topics[:15]  # Top 15 common topics
            
        except Exception as e:
            self.logger.error(f"Common topics identification failed: {e}")
            return []
    
    async def _identify_content_gaps(
        self, 
        query: str, 
        analyzed_pages: List[CompetitorPage], 
        context: Dict[str, Any]
    ) -> List[str]:
        """Identify potential content gaps in competitor coverage"""
        try:
            # This is a simplified implementation
            # In production, this would use more sophisticated analysis
            
            gaps = []
            
            # Common content types that might be missing
            content_type_coverage = defaultdict(int)
            for page in analyzed_pages:
                content_type_coverage[page.content_type] += 1
            
            # Identify missing content types
            all_content_types = [ContentType.ARTICLE, ContentType.GUIDE, ContentType.FAQ, ContentType.BLOG_POST]
            for content_type in all_content_types:
                if content_type_coverage[content_type] < 2:  # Less than 2 pages of this type
                    gaps.append(f"Limited {content_type.value} coverage")
            
            # Analyze heading patterns for gaps
            h2_topics = []
            for page in analyzed_pages:
                h2_topics.extend(page.headings.get('h2', []))
            
            # Common topics that might be missing
            expected_topics = self._generate_expected_topics(query)
            covered_topics = set(topic.lower() for topic in h2_topics)
            
            for expected in expected_topics:
                if not any(expected in covered for covered in covered_topics):
                    gaps.append(f"Missing coverage of '{expected}'")
            
            return gaps[:10]  # Top 10 gaps
            
        except Exception as e:
            self.logger.error(f"Content gap identification failed: {e}")
            return []
    
    def _generate_expected_topics(self, query: str) -> List[str]:
        """Generate expected topics based on query"""
        # This is a simplified implementation
        query_lower = query.lower()
        expected = []
        
        # Common topics for how-to queries
        if any(word in query_lower for word in ['how', 'guide', 'tutorial']):
            expected.extend(['benefits', 'step-by-step', 'common mistakes', 'tips', 'best practices'])
        
        # Common topics for comparison queries
        if any(word in query_lower for word in ['vs', 'versus', 'compare', 'difference']):
            expected.extend(['pros and cons', 'pricing', 'features', 'alternatives'])
        
        # Common topics for product/service queries
        if any(word in query_lower for word in ['best', 'top', 'review']):
            expected.extend(['comparison', 'pricing', 'features', 'customer reviews', 'alternatives'])
        
        # Generic topics that often appear
        expected.extend(['introduction', 'overview', 'conclusion', 'faq', 'resources'])
        
        return expected
    
    def _identify_top_performing_formats(self, analyzed_pages: List[CompetitorPage]) -> List[str]:
        """Identify top performing content formats"""
        try:
            format_scores = defaultdict(list)
            
            # Group pages by content type and calculate average quality
            for page in analyzed_pages:
                format_scores[page.content_type.value].append(page.quality_score)
            
            # Calculate average quality for each format
            format_averages = {}
            for format_type, scores in format_scores.items():
                if scores:
                    format_averages[format_type] = sum(scores) / len(scores)
            
            # Sort by average quality
            sorted_formats = sorted(format_averages.items(), key=lambda x: x[1], reverse=True)
            
            return [format_type for format_type, _ in sorted_formats]
            
        except Exception as e:
            self.logger.error(f"Top performing formats identification failed: {e}")
            return []
    
    def _identify_keyword_opportunities(self, analyzed_pages: List[CompetitorPage], query: str) -> List[str]:
        """Identify keyword opportunities based on competitor analysis"""
        try:
            # Collect all keywords from competitors
            all_keywords = []
            for page in analyzed_pages:
                all_keywords.extend(page.keywords)
            
            # Find keywords that appear in multiple competitors (indicating opportunity)
            keyword_frequency = Counter(all_keywords)
            
            # Filter out the main query terms
            query_words = set(query.lower().split())
            opportunities = [
                keyword for keyword, freq in keyword_frequency.most_common(20)
                if freq >= 2 and keyword not in query_words and len(keyword) > 3
            ]
            
            return opportunities[:15]  # Top 15 opportunities
            
        except Exception as e:
            self.logger.error(f"Keyword opportunities identification failed: {e}")
            return []
    
    def _generate_cache_key(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cache key for competitor analysis"""
        import hashlib
        
        key_data = {
            'query': query.lower().strip(),
            'location': context.get('location', 'default'),
            'language': context.get('language', 'en'),
            'max_competitors': self.config.max_competitors
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _generate_page_cache_key(self, url: str) -> str:
        """Generate cache key for individual page"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[CompetitorContentData]:
        """Get cached competitor analysis result"""
        if cache_key in self.competitor_cache:
            cached_data, cached_time = self.competitor_cache[cache_key]
            
            if time.time() - cached_time < self.cache_ttl:
                return cached_data
            else:
                del self.competitor_cache[cache_key]
        
        return None
    
    def _get_cached_page(self, cache_key: str) -> Optional[CompetitorPage]:
        """Get cached page analysis result"""
        if cache_key in self.page_cache:
            cached_page, cached_time = self.page_cache[cache_key]
            
            if time.time() - cached_time < self.cache_ttl:
                return cached_page
            else:
                del self.page_cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, data: CompetitorContentData):
        """Cache competitor analysis result"""
        self.competitor_cache[cache_key] = (data, time.time())
        
        # Prevent cache from growing too large
        if len(self.competitor_cache) > 200:
            sorted_items = sorted(
                self.competitor_cache.items(),
                key=lambda x: x[1][1]
            )
            self.competitor_cache = dict(sorted_items[-150:])
    
    def _cache_page(self, cache_key: str, page: CompetitorPage):
        """Cache page analysis result"""
        self.page_cache[cache_key] = (page, time.time())
        
        # Prevent cache from growing too large
        if len(self.page_cache) > 1000:
            sorted_items = sorted(
                self.page_cache.items(),
                key=lambda x: x[1][1]
            )
            self.page_cache = dict(sorted_items[-800:])
    
    def _format_api_response(self, data: CompetitorContentData) -> Dict[str, Any]:
        """Format competitor content data for API response"""
        return {
            'query': data.query,
            'competitor_analysis': data.get_content_insights(),
            'analyzed_pages': len(data.analyzed_pages),
            'content_gaps': data.content_gaps,
            'common_topics': data.common_topics,
            'average_content_length': data.average_content_length,
            'top_performing_formats': data.top_performing_formats,
            'keyword_opportunities': data.keyword_opportunities,
            'competitor_details': [
                {
                    'url': page.url,
                    'title': page.title,
                    'content_type': page.content_type.value,
                    'quality_score': round(page.quality_score, 2),
                    'authority_score': round(page.authority_score, 2),
                    'content_length': page.content_length,
                    'heading_counts': {level: len(headings) for level, headings in page.headings.items()},
                    'top_keywords': page.keywords[:10]
                }
                for page in data.analyzed_pages
            ],
            'collection_timestamp': data.collection_timestamp.isoformat(),
            'data_source': DataSourceType.COMPETITOR_CONTENT.value
        }
    
    def _create_empty_result(self, query: str, reason: str) -> Dict[str, Any]:
        """Create empty result for invalid queries"""
        return {
            'query': query,
            'competitor_analysis': {'error': reason},
            'analyzed_pages': 0,
            'content_gaps': [],
            'common_topics': [],
            'average_content_length': 0,
            'top_performing_formats': [],
            'keyword_opportunities': [],
            'competitor_details': [],
            'error': reason,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.COMPETITOR_CONTENT.value
        }
    
    def _create_error_result(self, query: str, error_message: str) -> Dict[str, Any]:
        """Create error result for failed requests"""
        return {
            'query': query,
            'competitor_analysis': {'error': error_message},
            'analyzed_pages': 0,
            'content_gaps': [],
            'common_topics': [],
            'average_content_length': 0,
            'top_performing_formats': [],
            'keyword_opportunities': [],
            'competitor_details': [],
            'error': error_message,
            'collection_timestamp': datetime.utcnow().isoformat(),
            'data_source': DataSourceType.COMPETITOR_CONTENT.value
        }
    
    def _update_metrics(self, success: bool, execution_time: float, pages_analyzed: int):
        """Update client performance metrics"""
        if success:
            self.request_metrics['successful_analyses'] += 1
        else:
            self.request_metrics['failed_analyses'] += 1
        
        self.request_metrics['total_pages_analyzed'] += pages_analyzed
        
        # Update rolling average analysis time
        total_requests = self.request_metrics['total_requests']
        current_avg = self.request_metrics['average_analysis_time']
        
        self.request_metrics['average_analysis_time'] = (
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
            self.request_metrics['successful_analyses'] / total_requests
            if total_requests > 0 else 0.0
        )
        
        return {
            'client_metrics': self.request_metrics,
            'cache_performance': {
                'competitor_cache_size': len(self.competitor_cache),
                'page_cache_size': len(self.page_cache),
                'cache_hit_rate': cache_hit_rate,
                'cache_ttl_seconds': self.cache_ttl
            },
            'performance_summary': {
                'success_rate': success_rate,
                'average_analysis_time': self.request_metrics['average_analysis_time'],
                'average_pages_per_analysis': (
                    self.request_metrics['total_pages_analyzed'] / max(1, self.request_metrics['successful_analyses'])
                )
            },
            'configuration': {
                'max_competitors': self.config.max_competitors,
                'concurrent_requests': self.config.concurrent_requests,
                'request_timeout': self.config.request_timeout,
                'requests_per_minute': self.config.requests_per_minute
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for competitor content client"""
        try:
            # Test with a simple query
            test_result = await self.get_competitor_content("test query")
            
            return {
                'status': 'healthy' if 'error' not in test_result else 'degraded',
                'last_test_time': datetime.utcnow().isoformat(),
                'serpapi_available': self.serpapi_client is not None,
                'google_api_available': self.google_api_manager is not None,
                'request_manager_status': await self.request_manager.health_check(),
                'rate_limiter_status': self.rate_limiter.get_status(),
                'cache_status': {
                    'competitor_cache_size': len(self.competitor_cache),
                    'page_cache_size': len(self.page_cache),
                    'total_cache_items': len(self.competitor_cache) + len(self.page_cache)
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
            self.logger.info("🛑 Shutting down Competitor Content Client...")
            
            # Shutdown request manager
            await self.request_manager.shutdown()
            
            # Shutdown rate limiter
            await self.rate_limiter.shutdown()
            
            # Clear caches
            self.competitor_cache.clear()
            self.page_cache.clear()
            
            self.logger.info("✅ Competitor Content Client shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")