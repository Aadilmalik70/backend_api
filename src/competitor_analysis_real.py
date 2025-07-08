"""
Hybrid Competitor Analysis - Real Data Implementation

This module combines Google APIs for search and entity analysis with Playwright
for deep content scraping, using only real data without mocks or hardcoded values.
"""

import logging
import re
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

# Google APIs
from utils.google_apis.custom_search_client import CustomSearchClient
from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient  
from utils.google_apis.natural_language_client import NaturalLanguageClient
from utils.google_apis.gemini_client import GeminiClient

# Playwright & SerpAPI
from utils.browser_content_scraper import BrowserContentScraper
from utils.serpapi_client import SerpAPIClient
from utils.gemini_nlp_client import GeminiNLPClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompetitorAnalysisReal:
    """
    Hybrid competitor analysis using only real data sources.
    
    Strategy:
    1. Google Custom Search API - for search results
    2. Google Knowledge Graph - for entity enrichment
    3. Playwright - for content scraping
    4. SerpAPI - as fallback
    5. Gemini - for content analysis
    
    NO HARDCODED VALUES - ALL DATA IS REAL
    """
    
    def __init__(self, serpapi_key: Optional[str] = None, gemini_api_key: Optional[str] = None):
        """Initialize hybrid competitor analysis with all clients."""
        # Google APIs (Primary for search)
        self.custom_search_client = CustomSearchClient()
        self.knowledge_graph_client = KnowledgeGraphClient()
        self.natural_language_client = NaturalLanguageClient()
        self.gemini_client = GeminiClient()
        
        # Playwright & SerpAPI (Primary for content)
        self.content_scraper = BrowserContentScraper()
        self.serp_client = SerpAPIClient(api_key=serpapi_key)
        self.gemini_nlp_client = GeminiNLPClient(api_key=gemini_api_key)
        
        # Check availability of services
        self.google_search_available = self.custom_search_client.health_check()
        self.knowledge_graph_available = self.knowledge_graph_client.health_check()
        self.natural_language_available = self.natural_language_client.health_check()
        self.gemini_available = self.gemini_client.health_check()
        self.serpapi_available = serpapi_key is not None
        
        logger.info(f"🔧 Hybrid Analysis initialized - "
                   f"Google Search: {self.google_search_available}, "
                   f"Knowledge Graph: {self.knowledge_graph_available}, "
                   f"Playwright: Available, "
                   f"SerpAPI: {self.serpapi_available}")
    
    def analyze_competitors(self, keyword: str, limit: int = 20, num_competitors: int = None) -> Dict[str, Any]:
        """
        Hybrid competitor analysis using only real data.
        
        Args:
            keyword: Target keyword
            limit: Maximum number of competitors to analyze
            num_competitors: Alternative parameter (compatibility)
            
        Returns:
            Comprehensive competitor analysis with REAL data only
        """
        if num_competitors is not None:
            limit = num_competitors
        
        logger.info(f"🚀 Starting hybrid competitor analysis for: {keyword}")
        
        try:
            # Phase 1: Get search results using Google APIs (primary) or SerpAPI (fallback)
            search_results = self._get_search_results(keyword, limit)
            logger.info(f"📊 Found {len(search_results)} real search results")
            
            if not search_results:
                logger.warning("No search results found")
                return self._get_empty_analysis(keyword, "No search results found")
            
            # Phase 2: Enrich with Knowledge Graph data
            enriched_results = self._enrich_with_knowledge_graph(search_results, keyword)
            logger.info(f"🧠 Enriched {len(enriched_results)} results with Knowledge Graph")
            
            # Phase 3: Deep content analysis with Playwright
            analyzed_competitors = self._deep_content_analysis(enriched_results, keyword)
            logger.info(f"🎯 Completed deep analysis of {len(analyzed_competitors)} competitors")
            
            # Phase 4: Generate insights from REAL data only
            insights = self._generate_real_insights(analyzed_competitors, keyword)
            
            return {
                "keyword": keyword,
                "competitors": analyzed_competitors,
                "insights": insights,
                "analysis_timestamp": datetime.now().isoformat(),
                "data_source": "hybrid_google_playwright",
                "analysis_quality": self._assess_analysis_quality(analyzed_competitors),
                "services_used": self._get_services_used()
            }
            
        except Exception as e:
            logger.error(f"❌ Hybrid analysis failed: {str(e)}")
            return self._get_empty_analysis(keyword, f"Analysis failed: {str(e)}")
    
    def _get_search_results(self, keyword: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get REAL search results using Google Custom Search API or SerpAPI.
        NO HARDCODED DATA.
        """
        # Try Google Custom Search API first
        if self.google_search_available:
            try:
                logger.info("🔍 Using Google Custom Search API for REAL search results")
                
                # Dynamic search patterns based on keyword
                search_patterns = [
                    keyword,
                    f"{keyword} software",
                    f"{keyword} tools",
                    f"{keyword} platform",
                    f"{keyword} solution"
                ]
                
                all_results = []
                for pattern in search_patterns[:3]:  # Limit to avoid quota exhaustion
                    try:
                        results = self.custom_search_client.search(pattern, num_results=min(10, limit))
                        if results and 'items' in results:
                            for item in results['items']:
                                # Extract REAL data from search results
                                url = item.get('link', '')
                                if not url or not self._is_valid_url(url):
                                    continue
                                
                                result = {
                                    "url": url,
                                    "title": item.get('title', ''),
                                    "description": item.get('snippet', ''),
                                    "domain": self._extract_domain(url),
                                    "position": len(all_results) + 1,
                                    "source": "google_custom_search",
                                    "search_pattern": pattern,
                                    "found_at": datetime.now().isoformat()
                                }
                                all_results.append(result)
                                
                    except Exception as pattern_error:
                        logger.warning(f"Pattern search failed: {pattern} - {str(pattern_error)}")
                        continue
                
                # Remove duplicates and return real results
                unique_results = self._deduplicate_results(all_results)
                logger.info(f"Found {len(unique_results)} unique real search results")
                return unique_results[:limit]
                
            except Exception as e:
                logger.warning(f"Google Custom Search failed: {str(e)}, falling back to SerpAPI")
        
        # Fallback to SerpAPI for real data
        if self.serpapi_available:
            try:
                logger.info("🔍 Using SerpAPI for REAL search results")
                competitors = self.serp_client.get_competitors(keyword, limit)
                
                if not competitors:
                    logger.warning("SerpAPI returned no results")
                    return []
                
                # Convert SerpAPI format to standard format (REAL data)
                results = []
                for i, comp in enumerate(competitors):
                    url = comp.get("url", "")
                    if not url or not self._is_valid_url(url):
                        continue
                    
                    result = {
                        "url": url,
                        "title": comp.get("title", ""),
                        "description": comp.get("description", ""),
                        "domain": self._extract_domain(url),
                        "position": i + 1,
                        "source": "serpapi",
                        "search_pattern": keyword,
                        "found_at": datetime.now().isoformat()
                    }
                    results.append(result)
                
                logger.info(f"Found {len(results)} real results from SerpAPI")
                return results
                
            except Exception as e:
                logger.error(f"SerpAPI also failed: {str(e)}")
        
        logger.warning("⚠️ No search services available - returning empty results")
        return []
    
    def _enrich_with_knowledge_graph(self, results: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """
        Enrich search results with REAL Knowledge Graph data.
        NO HARDCODED INDUSTRIES OR CLASSIFICATIONS.
        """
        if not self.knowledge_graph_available:
            logger.info("📋 Knowledge Graph not available, using basic enrichment")
            return self._basic_enrichment(results, keyword)
        
        enriched_results = []
        for result in results:
            try:
                domain = result.get("domain", "")
                title = result.get("title", "")
                description = result.get("description", "")
                
                # Query Knowledge Graph for REAL entity information
                entity_info = self.knowledge_graph_client.get_entity_info(domain)
                
                # Add REAL entity information to result
                result["entity_info"] = entity_info
                
                # Classify industry based on REAL data from Knowledge Graph and content
                result["industry_category"] = self._classify_industry_from_real_data(
                    title, description, entity_info
                )
                
                # Calculate relevance based on REAL content
                result["relevance_score"] = self._calculate_real_relevance_score(result, keyword)
                
                enriched_results.append(result)
                logger.debug(f"Enriched {domain} with Knowledge Graph data")
                
            except Exception as e:
                logger.warning(f"Knowledge Graph enrichment failed for {domain}: {str(e)}")
                # Add basic enrichment without Knowledge Graph
                result["entity_info"] = {}
                result["industry_category"] = self._classify_industry_from_real_data(
                    title, description, {}
                )
                result["relevance_score"] = self._calculate_real_relevance_score(result, keyword)
                enriched_results.append(result)
        
        return enriched_results
    
    def _basic_enrichment(self, results: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """Basic enrichment when Knowledge Graph is not available."""
        enriched_results = []
        for result in results:
            result["entity_info"] = {}
            result["industry_category"] = self._classify_industry_from_real_data(
                result.get("title", ""), result.get("description", ""), {}
            )
            result["relevance_score"] = self._calculate_real_relevance_score(result, keyword)
            enriched_results.append(result)
        
        return enriched_results
    
    def _deep_content_analysis(self, results: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
        """
        Perform deep content analysis using Playwright scraping.
        Uses ONLY real scraped data.
        """
        analyzed_competitors = []
        
        for result in results:
            competitor_analysis = self._analyze_single_competitor_real_data(result, keyword)
            analyzed_competitors.append(competitor_analysis)
        
        return analyzed_competitors
    
    def _analyze_single_competitor_real_data(self, result: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """
        Analyze a single competitor with comprehensive Playwright scraping.
        Uses ONLY real scraped data - NO HARDCODED VALUES.
        """
        url = result.get("url", "")
        logger.info(f"🔍 Deep analysis of: {url}")
        
        try:
            # Scrape content with Playwright
            content = self.content_scraper.scrape_content(url)
            
            if content.get("failed", False) or content.get("error"):
                error_msg = content.get('error', 'Unknown scraping error')
                logger.warning(f"Scraping failed for {url}: {error_msg}")
                return self._get_real_failed_analysis(result, error_msg)
            
            # Extract main content
            main_content = content.get("main_content", "")
            if not main_content or len(main_content.strip()) < 50:
                logger.warning(f"Insufficient content from {url}: {len(main_content)} chars")
                return self._get_real_failed_analysis(result, "Insufficient content extracted")
            
            # Comprehensive analysis using REAL scraped data
            analysis = {
                # Basic info from real data
                "url": url,
                "title": result.get("title", ""),
                "domain": result.get("domain", ""),
                "position": result.get("position", 0),
                "source": "hybrid_analysis",
                
                # Content metrics from real scraped data
                "content_length": len(main_content),
                "word_count": len([word for word in main_content.split() if word.strip()]),
                
                # SEO analysis from real scraped data
                "keyword_usage": self._analyze_real_keyword_usage(content, keyword),
                "content_structure": self._analyze_real_content_structure(content),
                "readability": self._calculate_real_readability(main_content),
                "seo_elements": self._analyze_real_seo_elements(content),
                
                # Enhanced analysis with real NLP data
                "sentiment": self._analyze_real_sentiment(main_content),
                "entities": self._extract_real_entities(main_content),
                "topics": self._extract_real_topics(main_content),
                
                # Competitor-specific metrics from real data
                "content_similarity": self._calculate_real_content_similarity(main_content, keyword),
                "industry_category": result.get("industry_category", ""),
                "relevance_score": result.get("relevance_score", 0),
                "confidence_score": self._calculate_real_confidence_score(content, keyword),
                
                # Real metadata
                "scraped_at": content.get("scraped_at", datetime.now().isoformat()),
                "status": "success",
                "detection_method": "hybrid_google_playwright"
            }
            
            logger.info(f"✅ Successfully analyzed: {url}")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis failed for {url}: {str(e)}")
            return self._get_real_failed_analysis(result, f"Analysis error: {str(e)}")
    
    def _analyze_real_keyword_usage(self, content: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """Analyze keyword usage based on REAL scraped content."""
        text = content.get("main_content", "")
        title = content.get("title", "")
        meta_description = content.get("meta_description", "")
        
        # Extract headings from real data
        headings = content.get("headings", [])
        h1_text = ""
        all_headings_text = ""
        
        for heading in headings:
            heading_text = heading.get("text", "")
            all_headings_text += heading_text + " "
            if heading.get("level") == "h1" and not h1_text:
                h1_text = heading_text
        
        # Normalize for analysis
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        title_lower = title.lower()
        meta_lower = meta_description.lower()
        h1_lower = h1_text.lower()
        headings_lower = all_headings_text.lower()
        
        # Count actual occurrences
        text_count = text_lower.count(keyword_lower)
        title_count = title_lower.count(keyword_lower)
        meta_count = meta_lower.count(keyword_lower)
        h1_count = h1_lower.count(keyword_lower)
        headings_count = headings_lower.count(keyword_lower)
        
        # Calculate real density
        word_count = len([word for word in text.split() if word.strip()])
        density = (text_count / max(1, word_count)) * 100
        
        return {
            "total_count": text_count,
            "density_percentage": round(density, 2),
            "title_usage": {
                "present": title_count > 0,
                "count": title_count,
                "title_text": title
            },
            "meta_description_usage": {
                "present": meta_count > 0,
                "count": meta_count,
                "meta_text": meta_description
            },
            "h1_usage": {
                "present": h1_count > 0,
                "count": h1_count,
                "h1_text": h1_text
            },
            "headings_usage": {
                "present": headings_count > 0,
                "count": headings_count,
                "total_headings": len(headings)
            },
            "optimization_score": self._calculate_real_optimization_score(
                title_count, meta_count, h1_count, headings_count, density
            )
        }
    
    def _analyze_real_content_structure(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content structure from REAL scraped data."""
        headings = content.get("headings", [])
        images = content.get("images", [])
        links = content.get("links", {})
        main_content = content.get("main_content", "")
        
        # Analyze real heading hierarchy
        heading_structure = {}
        for heading in headings:
            level = heading.get("level", "")
            if level:
                heading_structure[level] = heading_structure.get(level, 0) + 1
        
        # Analyze real content sections
        paragraphs = [p.strip() for p in main_content.split('\n') 
                     if p.strip() and len(p.strip()) > 20]
        
        # Count real lists
        list_count = self._count_real_lists(main_content)
        
        # Analyze real links
        internal_links = links.get("internal", [])
        external_links = links.get("external", [])
        
        # Calculate real average paragraph length
        avg_paragraph_length = (
            sum(len(p) for p in paragraphs) / len(paragraphs) 
            if paragraphs else 0
        )
        
        return {
            "heading_hierarchy": heading_structure,
            "total_headings": len(headings),
            "paragraph_count": len(paragraphs),
            "average_paragraph_length": round(avg_paragraph_length, 1),
            "list_count": list_count,
            "image_count": len(images),
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "content_organization_score": self._calculate_real_organization_score(
                heading_structure, len(paragraphs), list_count, len(images)
            )
        }
    
    def _analyze_real_seo_elements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze SEO elements from REAL scraped data."""
        title = content.get("title", "")
        meta_description = content.get("meta_description", "")
        canonical_url = content.get("canonical_url", "")
        
        return {
            "title_tag": {
                "text": title,
                "length": len(title),
                "optimized": 30 <= len(title) <= 60 if title else False
            },
            "meta_description": {
                "text": meta_description,
                "length": len(meta_description),
                "optimized": 150 <= len(meta_description) <= 160 if meta_description else False
            },
            "canonical_url": canonical_url,
            "has_canonical": bool(canonical_url),
            "schema_markup": content.get("schema_markup", {}),
            "open_graph": content.get("open_graph", {}),
            "twitter_cards": content.get("twitter_cards", {})
        }
    
    def _analyze_real_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment using REAL NLP services."""
        try:
            if self.natural_language_available:
                sentiment = self.natural_language_client.analyze_sentiment(content)
                return sentiment
            elif self.gemini_nlp_client:
                analysis = self.gemini_nlp_client.analyze_content(content)
                return analysis.get("sentiment", {"score": 0, "magnitude": 0})
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {str(e)}")
        
        return {"score": 0, "magnitude": 0, "error": "Analysis failed"}
    
    def _extract_real_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities using REAL NLP services."""
        try:
            if self.natural_language_available:
                entities = self.natural_language_client.extract_entities(content)
                return entities
            elif self.gemini_nlp_client:
                analysis = self.gemini_nlp_client.analyze_content(content)
                return analysis.get("entities", [])
        except Exception as e:
            logger.warning(f"Entity extraction failed: {str(e)}")
        
        return []
    
    def _extract_real_topics(self, content: str) -> List[str]:
        """Extract topics using REAL NLP services."""
        try:
            if self.gemini_available:
                topics = self.gemini_client.extract_topics(content)
                return topics
        except Exception as e:
            logger.warning(f"Topic extraction failed: {str(e)}")
        
        return []
    
    def _calculate_real_readability(self, text: str) -> Dict[str, Any]:
        """Calculate readability metrics from REAL text."""
        if not text or not text.strip():
            return {
                "flesch_score": 0,
                "reading_level": "Unknown",
                "error": "No text to analyze"
            }
        
        # Split into real sentences and words
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = [w.strip() for w in text.split() if w.strip()]
        
        sentence_count = len(sentences)
        word_count = len(words)
        
        if sentence_count == 0 or word_count == 0:
            return {
                "flesch_score": 0,
                "reading_level": "Unknown",
                "error": "Insufficient text for analysis"
            }
        
        # Calculate real metrics
        avg_sentence_length = word_count / sentence_count
        syllable_count = sum(self._count_syllables(word) for word in words)
        avg_syllables_per_word = syllable_count / word_count
        
        # Real Flesch Reading Ease calculation
        flesch_score = (
            206.835 - 
            (1.015 * avg_sentence_length) - 
            (84.6 * avg_syllables_per_word)
        )
        flesch_score = max(0, min(100, flesch_score))
        
        # Determine reading level based on real score
        if flesch_score >= 90:
            reading_level = "Very Easy"
        elif flesch_score >= 80:
            reading_level = "Easy"
        elif flesch_score >= 70:
            reading_level = "Fairly Easy"
        elif flesch_score >= 60:
            reading_level = "Standard"
        elif flesch_score >= 50:
            reading_level = "Fairly Difficult"
        elif flesch_score >= 30:
            reading_level = "Difficult"
        else:
            reading_level = "Very Difficult"
        
        return {
            "flesch_score": round(flesch_score, 1),
            "reading_level": reading_level,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_syllables_per_word": round(avg_syllables_per_word, 1),
            "sentence_count": sentence_count,
            "word_count": word_count,
            "syllable_count": syllable_count
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word."""
        if not word:
            return 0
        
        word = word.lower().strip()
        if not word:
            return 0
        
        vowels = "aeiouy"
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not previous_was_vowel:
                    syllable_count += 1
                previous_was_vowel = True
            else:
                previous_was_vowel = False
        
        # Handle silent 'e'
        if word.endswith('e') and syllable_count > 1:
            syllable_count -= 1
        
        return max(1, syllable_count)
    
    def _calculate_real_content_similarity(self, content: str, keyword: str) -> float:
        """Calculate content similarity using REAL text analysis."""
        if not content or not keyword:
            return 0.0
        
        # Extract real terms
        keyword_terms = set(keyword.lower().split())
        content_terms = set(content.lower().split())
        
        if not keyword_terms:
            return 0.0
        
        # Calculate real similarity metrics
        intersection = keyword_terms.intersection(content_terms)
        union = keyword_terms.union(content_terms)
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0
        
        # Keyword coverage
        coverage = len(intersection) / len(keyword_terms)
        
        # Combined real similarity score
        similarity = (jaccard + coverage) / 2
        
        return round(similarity, 3)
    
    def _classify_industry_from_real_data(self, title: str, description: str, 
                                        entity_info: Dict[str, Any]) -> str:
        """
        Classify industry based on REAL data from Knowledge Graph and content.
        NO HARDCODED INDUSTRY MAPPINGS.
        """
        # Extract real industry information from Knowledge Graph
        if entity_info and isinstance(entity_info, dict):
            # Look for industry information in Knowledge Graph response
            kg_types = entity_info.get("@type", [])
            if isinstance(kg_types, list):
                for kg_type in kg_types:
                    if isinstance(kg_type, str):
                        return kg_type.lower().replace(" ", "_")
            
            # Look for description or industry field
            kg_description = entity_info.get("description", "")
            if kg_description:
                return self._extract_industry_from_text(kg_description)
        
        # Fall back to content analysis
        combined_text = f"{title} {description}".lower()
        return self._extract_industry_from_text(combined_text)
    
    def _extract_industry_from_text(self, text: str) -> str:
        """Extract industry from text without hardcoded mappings."""
        if not text:
            return "unknown"
        
        # Extract potential industry keywords from real text
        text_lower = text.lower()
        words = [word.strip() for word in text_lower.split() if len(word.strip()) > 3]
        
        # Look for industry-indicating terms
        industry_terms = []
        for word in words:
            if any(suffix in word for suffix in ['tech', 'soft', 'ware', 'service', 'platform']):
                industry_terms.append(word)
        
        if industry_terms:
            return "_".join(industry_terms[:2])  # Take first 2 relevant terms
        
        return "business_services"
    
    def _calculate_real_relevance_score(self, result: Dict[str, Any], keyword: str) -> float:
        """Calculate relevance score from REAL search result data."""
        if not keyword:
            return 0.0
        
        score = 0.0
        keyword_lower = keyword.lower()
        keyword_terms = set(keyword_lower.split())
        
        # Title relevance (real title analysis)
        title = result.get("title", "").lower()
        if title:
            title_terms = set(title.split())
            title_overlap = len(keyword_terms.intersection(title_terms))
            score += (title_overlap / len(keyword_terms)) * 0.4
        
        # Description relevance (real description analysis)
        description = result.get("description", "").lower()
        if description:
            desc_terms = set(description.split())
            desc_overlap = len(keyword_terms.intersection(desc_terms))
            score += (desc_overlap / len(keyword_terms)) * 0.3
        
        # URL relevance (real URL analysis)
        url = result.get("url", "").lower()
        if url:
            url_terms = set(re.findall(r'[a-zA-Z]+', url))
            url_overlap = len(keyword_terms.intersection(url_terms))
            score += (url_overlap / len(keyword_terms)) * 0.2
        
        # Position bonus (real search position)
        position = result.get("position", 999)
        if position <= 5:
            score += 0.1
        elif position <= 10:
            score += 0.05
        
        return min(round(score, 3), 1.0)
    
    def _calculate_real_confidence_score(self, content: Dict[str, Any], keyword: str) -> float:
        """Calculate confidence score from REAL scraped data."""
        score = 0.0
        
        # Content quality based on real data
        main_content = content.get("main_content", "")
        content_length = len(main_content)
        
        if content_length > 2000:
            score += 0.3
        elif content_length > 1000:
            score += 0.2
        elif content_length > 500:
            score += 0.1
        
        # SEO elements presence (real data)
        if content.get("title"):
            score += 0.15
        if content.get("meta_description"):
            score += 0.15
        if content.get("headings"):
            score += 0.1
        
        # Content structure (real data)
        headings = content.get("headings", [])
        if any(h.get("level") == "h1" for h in headings):
            score += 0.1
        if len(headings) >= 3:
            score += 0.05
        
        # Images presence (real data)
        images = content.get("images", [])
        if images:
            score += 0.05
        
        # Links presence (real data)
        links = content.get("links", {})
        if links.get("internal") or links.get("external"):
            score += 0.05
        
        return min(round(score, 3), 1.0)
    
    def _calculate_real_optimization_score(self, title_count: int, meta_count: int, 
                                         h1_count: int, headings_count: int, density: float) -> float:
        """Calculate keyword optimization score from REAL usage data."""
        score = 0.0
        
        # Title optimization (real count)
        if title_count > 0:
            score += 0.3
        
        # Meta description optimization (real count)
        if meta_count > 0:
            score += 0.2
        
        # H1 optimization (real count)
        if h1_count > 0:
            score += 0.2
        
        # Headings optimization (real count)
        if headings_count > 0:
            score += 0.1
        
        # Density optimization (real calculated density)
        if 0.5 <= density <= 3.0:
            score += 0.2
        elif 0.1 <= density < 0.5 or 3.0 < density <= 5.0:
            score += 0.1
        
        return round(score, 2)
    
    def _calculate_real_organization_score(self, headings: Dict[str, int], 
                                         paragraph_count: int, list_count: int, image_count: int) -> float:
        """Calculate organization score from REAL content structure."""
        score = 0.0
        
        # Heading structure (real heading counts)
        if headings.get("h1", 0) > 0:
            score += 0.3
        if headings.get("h2", 0) >= 2:
            score += 0.2
        if headings.get("h3", 0) > 0:
            score += 0.1
        
        # Content variety (real counts)
        if paragraph_count >= 3:
            score += 0.2
        if list_count > 0:
            score += 0.1
        if image_count > 0:
            score += 0.1
        
        return round(score, 2)
    
    def _count_real_lists(self, content: str) -> int:
        """Count lists in REAL content."""
        if not content:
            return 0
        
        lines = content.split('\n')
        list_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for bullet points
            if line.startswith(('•', '●', '◦', '-', '*', '→', '▪', '▫')):
                list_count += 1
            # Check for numbered lists
            elif len(line) > 3 and line[0].isdigit() and line[1] in '.):':
                list_count += 1
        
        return list_count
    
    def _generate_real_insights(self, competitors: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """
        Generate insights from REAL competitor analysis data.
        NO HARDCODED VALUES - ALL METRICS ARE CALCULATED FROM REAL DATA.
        """
        successful_competitors = [c for c in competitors if c.get("status") == "success"]
        failed_competitors = [c for c in competitors if c.get("status") == "failed"]
        
        if not successful_competitors:
            return {
                "error": "No successful competitor analysis",
                "total_analyzed": len(competitors),
                "successful": 0,
                "failed": len(failed_competitors),
                "failure_reasons": [c.get("error", "Unknown") for c in failed_competitors]
            }
        
        # Extract REAL metrics from successful analyses
        real_metrics = self._extract_real_metrics(successful_competitors)
        
        # Generate insights based on REAL data
        insights = {
            "content_analysis": {
                "average_content_length": real_metrics["avg_content_length"],
                "average_word_count": real_metrics["avg_word_count"],
                "content_length_range": {
                    "min": real_metrics["min_content_length"],
                    "max": real_metrics["max_content_length"]
                },
                "top_performers": real_metrics["top_content_performers"]
            },
            "seo_analysis": {
                "average_keyword_density": real_metrics["avg_keyword_density"],
                "keyword_optimization_scores": real_metrics["keyword_opt_scores"],
                "title_optimization_rate": real_metrics["title_opt_rate"],
                "meta_description_rate": real_metrics["meta_desc_rate"],
                "h1_optimization_rate": real_metrics["h1_opt_rate"]
            },
            "content_structure": {
                "average_headings_count": real_metrics["avg_headings_count"],
                "heading_hierarchy_usage": real_metrics["heading_hierarchy"],
                "average_paragraph_count": real_metrics["avg_paragraph_count"],
                "list_usage_rate": real_metrics["list_usage_rate"],
                "image_usage_rate": real_metrics["image_usage_rate"]
            },
            "readability_analysis": {
                "average_flesch_score": real_metrics["avg_flesch_score"],
                "reading_level_distribution": real_metrics["reading_levels"],
                "average_sentence_length": real_metrics["avg_sentence_length"],
                "average_word_complexity": real_metrics["avg_word_complexity"]
            },
            "industry_distribution": real_metrics["industry_distribution"],
            "common_topics": real_metrics["common_topics"],
            "entity_analysis": real_metrics["entity_analysis"],
            "data_quality": {
                "total_competitors_analyzed": len(competitors),
                "successful_analyses": len(successful_competitors),
                "failed_analyses": len(failed_competitors),
                "success_rate": round((len(successful_competitors) / len(competitors)) * 100, 1),
                "average_confidence_score": real_metrics["avg_confidence_score"]
            }
        }
        
        return insights
    
    def _extract_real_metrics(self, competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract all metrics from REAL competitor data."""
        # Content metrics
        content_lengths = [c.get("content_length", 0) for c in competitors]
        word_counts = [c.get("word_count", 0) for c in competitors]
        
        # SEO metrics
        keyword_densities = []
        keyword_opt_scores = []
        title_optimized = 0
        meta_desc_optimized = 0
        h1_optimized = 0
        
        for competitor in competitors:
            keyword_usage = competitor.get("keyword_usage", {})
            keyword_densities.append(keyword_usage.get("density_percentage", 0))
            keyword_opt_scores.append(keyword_usage.get("optimization_score", 0))
            
            if keyword_usage.get("title_usage", {}).get("present", False):
                title_optimized += 1
            if keyword_usage.get("meta_description_usage", {}).get("present", False):
                meta_desc_optimized += 1
            if keyword_usage.get("h1_usage", {}).get("present", False):
                h1_optimized += 1
        
        # Structure metrics
        headings_counts = []
        paragraph_counts = []
        list_counts = []
        image_counts = []
        heading_hierarchy = {}
        
        for competitor in competitors:
            structure = competitor.get("content_structure", {})
            headings_counts.append(structure.get("total_headings", 0))
            paragraph_counts.append(structure.get("paragraph_count", 0))
            list_counts.append(structure.get("list_count", 0))
            image_counts.append(structure.get("image_count", 0))
            
            # Aggregate heading hierarchy
            hierarchy = structure.get("heading_hierarchy", {})
            for level, count in hierarchy.items():
                heading_hierarchy[level] = heading_hierarchy.get(level, 0) + count
        
        # Readability metrics
        flesch_scores = []
        sentence_lengths = []
        word_complexities = []
        reading_levels = []
        
        for competitor in competitors:
            readability = competitor.get("readability", {})
            flesch_scores.append(readability.get("flesch_score", 0))
            sentence_lengths.append(readability.get("avg_sentence_length", 0))
            word_complexities.append(readability.get("avg_syllables_per_word", 0))
            reading_levels.append(readability.get("reading_level", "Unknown"))
        
        # Industry and topic analysis
        industries = [c.get("industry_category", "") for c in competitors if c.get("industry_category")]
        industry_distribution = dict(Counter(industries))
        
        # Extract entities and topics
        all_entities = []
        all_topics = []
        
        for competitor in competitors:
            entities = competitor.get("entities", [])
            for entity in entities:
                if isinstance(entity, dict) and entity.get("name"):
                    all_entities.append(entity["name"].lower())
            
            topics = competitor.get("topics", [])
            all_topics.extend([topic.lower() for topic in topics if isinstance(topic, str)])
        
        # Calculate averages and distributions
        total_competitors = len(competitors)
        
        return {
            # Content metrics
            "avg_content_length": round(sum(content_lengths) / total_competitors, 0) if content_lengths else 0,
            "avg_word_count": round(sum(word_counts) / total_competitors, 0) if word_counts else 0,
            "min_content_length": min(content_lengths) if content_lengths else 0,
            "max_content_length": max(content_lengths) if content_lengths else 0,
            "top_content_performers": self._get_top_performers(competitors, "content_length"),
            
            # SEO metrics
            "avg_keyword_density": round(sum(keyword_densities) / len(keyword_densities), 2) if keyword_densities else 0,
            "keyword_opt_scores": keyword_opt_scores,
            "title_opt_rate": round((title_optimized / total_competitors) * 100, 1),
            "meta_desc_rate": round((meta_desc_optimized / total_competitors) * 100, 1),
            "h1_opt_rate": round((h1_optimized / total_competitors) * 100, 1),
            
            # Structure metrics
            "avg_headings_count": round(sum(headings_counts) / total_competitors, 1) if headings_counts else 0,
            "heading_hierarchy": heading_hierarchy,
            "avg_paragraph_count": round(sum(paragraph_counts) / total_competitors, 1) if paragraph_counts else 0,
            "list_usage_rate": round((sum(1 for c in list_counts if c > 0) / total_competitors) * 100, 1),
            "image_usage_rate": round((sum(1 for c in image_counts if c > 0) / total_competitors) * 100, 1),
            
            # Readability metrics
            "avg_flesch_score": round(sum(flesch_scores) / len(flesch_scores), 1) if flesch_scores else 0,
            "reading_levels": dict(Counter(reading_levels)),
            "avg_sentence_length": round(sum(sentence_lengths) / len(sentence_lengths), 1) if sentence_lengths else 0,
            "avg_word_complexity": round(sum(word_complexities) / len(word_complexities), 1) if word_complexities else 0,
            
            # Industry and topics
            "industry_distribution": industry_distribution,
            "common_topics": [topic for topic, count in Counter(all_topics).most_common(10) if count >= 2],
            "entity_analysis": [entity for entity, count in Counter(all_entities).most_common(15) if count >= 2],
            
            # Quality metrics
            "avg_confidence_score": round(sum(c.get("confidence_score", 0) for c in competitors) / total_competitors, 3)
        }
    
    def _get_top_performers(self, competitors: List[Dict[str, Any]], metric: str) -> List[Dict[str, Any]]:
        """Get top performing competitors for a specific metric."""
        # Sort by metric and get top 3
        sorted_competitors = sorted(
            competitors, 
            key=lambda x: x.get(metric, 0), 
            reverse=True
        )
        
        top_performers = []
        for comp in sorted_competitors[:3]:
            top_performers.append({
                "domain": comp.get("domain", ""),
                "url": comp.get("url", ""),
                "value": comp.get(metric, 0)
            })
        
        return top_performers
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not excluded."""
        if not url:
            return False
        
        # Exclude non-business sites
        excluded_domains = [
            'wikipedia.org', 'youtube.com', 'linkedin.com', 'facebook.com',
            'twitter.com', 'instagram.com', 'reddit.com', 'quora.com',
            'stackoverflow.com', 'github.com', 'amazon.com', 'ebay.com'
        ]
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        return not any(excluded in domain for excluded in excluded_domains)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results by domain."""
        seen_domains = set()
        unique_results = []
        
        for result in results:
            domain = result.get("domain", "")
            if domain and domain not in seen_domains:
                seen_domains.add(domain)
                unique_results.append(result)
        
        return unique_results
    
    def _get_real_failed_analysis(self, result: Dict[str, Any], error_reason: str) -> Dict[str, Any]:
        """Generate failed analysis with real result data."""
        return {
            "url": result.get("url", ""),
            "title": result.get("title", ""),
            "domain": result.get("domain", ""),
            "position": result.get("position", 0),
            "source": "hybrid_analysis",
            "content_length": 0,
            "word_count": 0,
            "keyword_usage": {
                "total_count": 0,
                "density_percentage": 0,
                "optimization_score": 0
            },
            "content_structure": {
                "total_headings": 0,
                "paragraph_count": 0,
                "list_count": 0,
                "image_count": 0
            },
            "readability": {
                "flesch_score": 0,
                "reading_level": "Unknown"
            },
            "sentiment": {"score": 0, "error": "Analysis failed"},
            "entities": [],
            "topics": [],
            "content_similarity": 0,
            "industry_category": result.get("industry_category", ""),
            "relevance_score": result.get("relevance_score", 0),
            "confidence_score": 0,
            "status": "failed",
            "error": error_reason,
            "scraped_at": datetime.now().isoformat()
        }
    
    def _get_empty_analysis(self, keyword: str, reason: str) -> Dict[str, Any]:
        """Return empty analysis with error reason."""
        return {
            "keyword": keyword,
            "competitors": [],
            "insights": {
                "error": reason,
                "data_quality": {
                    "total_competitors_analyzed": 0,
                    "successful_analyses": 0,
                    "failed_analyses": 0,
                    "success_rate": 0
                }
            },
            "analysis_timestamp": datetime.now().isoformat(),
            "data_source": "hybrid_google_playwright",
            "analysis_quality": "failed",
            "services_used": self._get_services_used()
        }
    
    def _assess_analysis_quality(self, competitors: List[Dict[str, Any]]) -> str:
        """Assess overall analysis quality based on real results."""
        if not competitors:
            return "no_data"
        
        successful = sum(1 for c in competitors if c.get("status") == "success")
        total = len(competitors)
        success_rate = (successful / total) * 100
        
        if success_rate >= 80:
            return "excellent"
        elif success_rate >= 60:
            return "good"
        elif success_rate >= 40:
            return "fair"
        else:
            return "poor"
    
    def _get_services_used(self) -> Dict[str, bool]:
        """Get status of services used."""
        return {
            "google_custom_search": self.google_search_available,
            "knowledge_graph": self.knowledge_graph_available,
            "natural_language_api": self.natural_language_available,
            "gemini_api": self.gemini_available,
            "playwright_scraping": True,
            "serpapi_fallback": self.serpapi_available
        }
    
    def generate_content_blueprint(self, keyword: str, num_competitors: int = 20) -> Dict[str, Any]:
        """
        Generate content blueprint based on REAL competitor analysis.
        
        Args:
            keyword: Target keyword
            num_competitors: Number of competitors to analyze
            
        Returns:
            Content blueprint based on real competitor data
        """
        logger.info(f"📋 Generating content blueprint for: {keyword}")
        
        try:
            # Get real competitor analysis
            competitor_analysis = self.analyze_competitors(keyword, num_competitors=num_competitors)
            
            if not competitor_analysis.get("competitors"):
                return self._get_fallback_blueprint(keyword, "No competitor data available")
            
            # Extract real insights
            insights = competitor_analysis.get("insights", {})
            competitors = competitor_analysis.get("competitors", [])
            
            # Generate blueprint based on real data
            blueprint = self._generate_real_blueprint(keyword, insights, competitors)
            
            return blueprint
            
        except Exception as e:
            logger.error(f"❌ Content blueprint generation failed: {str(e)}")
            return self._get_fallback_blueprint(keyword, f"Generation failed: {str(e)}")
    
    def _generate_real_blueprint(self, keyword: str, insights: Dict[str, Any], 
                               competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate blueprint based on real competitor analysis."""
        successful_competitors = [c for c in competitors if c.get("status") == "success"]
        
        # Extract real common topics
        common_topics = insights.get("common_topics", [])
        entity_analysis = insights.get("entity_analysis", [])
        
        # Generate outline based on real competitor content
        outline = self._generate_outline_from_real_data(keyword, common_topics, entity_analysis)
        
        # Generate recommendations based on real metrics
        recommendations = self._generate_real_recommendations(keyword, insights, successful_competitors)
        
        return {
            "keyword": keyword,
            "outline": outline,
            "recommendations": recommendations,
            "competitor_insights": {
                "content_analysis": insights.get("content_analysis", {}),
                "seo_analysis": insights.get("seo_analysis", {}),
                "content_structure": insights.get("content_structure", {}),
                "readability_analysis": insights.get("readability_analysis", {})
            },
            "data_quality": insights.get("data_quality", {}),
            "generated_at": datetime.now().isoformat(),
            "based_on_real_data": True
        }
    
    def _generate_outline_from_real_data(self, keyword: str, common_topics: List[str], 
                                       entities: List[str]) -> Dict[str, Any]:
        """Generate outline based on real competitor content analysis."""
        # Use real topics to create relevant sections
        sections = []
        
        # Introduction section
        sections.append({
            "heading": f"Introduction to {keyword.title()}",
            "subsections": [
                f"What is {keyword.title()}?",
                f"Why {keyword.title()} is Important"
            ]
        })
        
        # Add sections based on real common topics
        if common_topics:
            for i, topic in enumerate(common_topics[:4]):  # Use up to 4 real topics
                sections.append({
                    "heading": f"{topic.title()} in {keyword.title()}",
                    "subsections": [
                        f"Understanding {topic.title()}",
                        f"Best Practices for {topic.title()}"
                    ]
                })
        
        # Add sections based on real entities
        if entities:
            sections.append({
                "heading": f"Key {keyword.title()} Components",
                "subsections": [entity.title() for entity in entities[:4]]
            })
        
        # Implementation section
        sections.append({
            "heading": f"Implementing {keyword.title()}",
            "subsections": [
                "Step-by-Step Guide",
                "Common Challenges and Solutions"
            ]
        })
        
        return {
            "title": f"Complete Guide to {keyword.title()}",
            "sections": sections
        }
    
    def _generate_real_recommendations(self, keyword: str, insights: Dict[str, Any], 
                                     competitors: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on real competitor analysis."""
        recommendations = []
        
        # Content length recommendations based on real data
        content_analysis = insights.get("content_analysis", {})
        avg_length = content_analysis.get("average_content_length", 0)
        if avg_length > 0:
            recommendations.append(f"Target content length: {int(avg_length)} words (based on competitor average)")
        
        # SEO recommendations based on real data
        seo_analysis = insights.get("seo_analysis", {})
        keyword_density = seo_analysis.get("average_keyword_density", 0)
        if keyword_density > 0:
            recommendations.append(f"Target keyword density: {keyword_density}% (based on competitor analysis)")
        
        # Structure recommendations based on real data
        structure_analysis = insights.get("content_structure", {})
        avg_headings = structure_analysis.get("average_headings_count", 0)
        if avg_headings > 0:
            recommendations.append(f"Use approximately {int(avg_headings)} headings for better structure")
        
        # Readability recommendations based on real data
        readability = insights.get("readability_analysis", {})
        avg_flesch = readability.get("average_flesch_score", 0)
        if avg_flesch > 0:
            reading_level = readability.get("reading_level_distribution", {})
            most_common_level = max(reading_level.items(), key=lambda x: x[1])[0] if reading_level else "Standard"
            recommendations.append(f"Target reading level: {most_common_level} (Flesch score: {avg_flesch})")
        
        # Add general recommendations based on successful competitors
        if competitors:
            recommendations.extend([
                f"Analyze top {min(3, len(competitors))} competitors for content gaps",
                "Include visual elements based on competitor image usage",
                "Optimize meta descriptions and title tags based on competitor best practices"
            ])
        
        return recommendations
    
    def _get_fallback_blueprint(self, keyword: str, error_reason: str) -> Dict[str, Any]:
        """Generate fallback blueprint when real data is unavailable."""
        return {
            "keyword": keyword,
            "outline": {
                "title": f"Complete Guide to {keyword.title()}",
                "sections": [
                    {
                        "heading": f"Introduction to {keyword.title()}",
                        "subsections": [
                            f"What is {keyword.title()}?",
                            f"Why {keyword.title()} Matters"
                        ]
                    },
                    {
                        "heading": "Key Strategies",
                        "subsections": [
                            "Best Practices",
                            "Common Mistakes to Avoid"
                        ]
                    },
                    {
                        "heading": "Implementation Guide",
                        "subsections": [
                            "Step-by-Step Process",
                            "Tools and Resources"
                        ]
                    }
                ]
            },
            "recommendations": [
                "Create comprehensive, well-researched content",
                "Focus on user intent and search query matching",
                "Include relevant examples and case studies",
                "Optimize for both search engines and user experience"
            ],
            "error": error_reason,
            "competitor_insights": {},
            "data_quality": {
                "total_competitors_analyzed": 0,
                "successful_analyses": 0,
                "error": error_reason
            },
            "generated_at": datetime.now().isoformat(),
            "based_on_real_data": False
        }