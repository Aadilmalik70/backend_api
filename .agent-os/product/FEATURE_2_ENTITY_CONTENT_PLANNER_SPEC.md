# 🏗️ Feature 2: Entity-Based Content Planner - Technical Specification

**Feature Name**: Entity-Based Content Planner  
**Version**: 1.0  
**Status**: Ready for Development  
**Priority**: P0 (Core Feature)  
**Estimated Effort**: 100 hours  

---

## 📋 Feature Overview

### **Purpose**
The Entity-Based Content Planner moves beyond traditional keywords to identify the core concepts, people, products, places, and entities that comprehensive content must cover to establish topical authority and compete effectively in search results.

### **Business Value**
- **Content Quality**: +50% improvement in content comprehensiveness
- **Search Rankings**: +35% improvement through topical authority signals
- **User Engagement**: +45% increase in time-on-page through comprehensive coverage
- **Competitive Advantage**: First-to-market with entity-driven content planning
- **Revenue Impact**: +25% conversion through better-targeted content

### **Success Criteria**
- Extract 50+ relevant entities per topic analysis
- Achieve 90%+ precision in entity relevance scoring
- Process competitor analysis in <45 seconds
- Support entity relationship mapping for 1000+ entities
- Deliver 85%+ user satisfaction with entity recommendations

---

## 🏗️ Technical Architecture

### **System Integration**
```python
# Integration with existing SERPStrategists architecture
class EntityBasedContentPlannerService:
    """
    Integrates with existing content analysis pipeline
    """
    def __init__(self, 
                 google_nl_client: GoogleNaturalLanguageClient,
                 knowledge_graph_client: KnowledgeGraphClient,
                 cache_manager: AdvancedCacheManager,
                 websocket_service: WebSocketService):
        self.google_nl_client = google_nl_client
        self.knowledge_graph_client = knowledge_graph_client
        self.cache_manager = cache_manager
        self.websocket_service = websocket_service
```

### **Architecture Diagram**
```mermaid
graph TB
    A[API Request] --> B[EntityContentPlannerService]
    B --> C[ContentAcquisitionEngine]
    B --> D[EntityExtractionEngine]
    B --> E[EntityAnalysisEngine]
    B --> F[RelationshipMappingEngine]
    B --> G[AuthorityScoreEngine]
    
    C --> H[SERP Results Scraper]
    C --> I[Competitor URL Analyzer]
    C --> J[Content Extractor]
    
    D --> K[Google Natural Language API]
    D --> L[spaCy NER Model]
    D --> M[Custom Entity Models]
    
    E --> N[Google Knowledge Graph API]
    E --> O[Wikidata Integration]
    E --> P[Entity Frequency Analysis]
    
    F --> Q[Graph Database (Neo4j)]
    F --> R[Relationship Scoring]
    F --> S[Network Analysis]
    
    G --> T[TF-IDF Authority Scoring]
    G --> U[PageRank Algorithm]
    G --> V[Content Gap Analysis]
    
    X[Cache Layer L1/L2/L3] --> B
    Y[WebSocket Updates] --> B
    Z[Database Storage] --> B
```

### **Data Flow Pipeline**
```yaml
Input Processing:
  1. Receive topic and optional competitor URLs
  2. Validate and sanitize input parameters
  3. Check cache for existing entity analysis
  4. Initialize WebSocket session for progress tracking

Content Acquisition:
  1. Scrape top 20 SERP results for target topic
  2. Extract content from provided competitor URLs
  3. Clean and preprocess text content
  4. Store raw content for entity extraction

Entity Extraction:
  1. Apply multiple NER models to extracted content
  2. Use Google Natural Language API for entity recognition
  3. Apply custom domain-specific entity models
  4. Merge and deduplicate extracted entities

Entity Enhancement:
  1. Query Google Knowledge Graph for entity context
  2. Retrieve entity descriptions and relationships
  3. Calculate entity importance and relevance scores
  4. Map entities to semantic categories

Relationship Mapping:
  1. Identify co-occurrence patterns between entities
  2. Calculate relationship strength scores
  3. Build entity relationship graph
  4. Identify entity clusters and themes

Authority Analysis:
  1. Calculate entity authority scores across content
  2. Identify content gaps and missing entities
  3. Generate entity coverage recommendations
  4. Score topical authority potential

Result Compilation:
  1. Organize entities by importance and category
  2. Generate relationship visualizations
  3. Create content planning recommendations
  4. Store results in database and cache
```

---

## 💻 Implementation Specification

### **Core Service Class**
```python
"""
src/services/entity_content_planner.py
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
import json
import hashlib
import re
from collections import defaultdict, Counter

import spacy
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
from bs4 import BeautifulSoup
import aiohttp

from src.utils.google_apis.natural_language_client import GoogleNaturalLanguageClient
from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
from src.utils.advanced_cache_manager import AdvancedCacheManager
from src.services.websocket_service import WebSocketService
from src.utils.rate_limiter import RateLimiter
from src.models.entity_analysis import EntityAnalysis, EntityAnalysisStorage

logger = logging.getLogger(__name__)

class EntityBasedContentPlannerService:
    """
    Service for analyzing entities and creating comprehensive content plans
    """
    
    def __init__(self, 
                 google_nl_client: GoogleNaturalLanguageClient,
                 knowledge_graph_client: KnowledgeGraphClient,
                 cache_manager: AdvancedCacheManager,
                 websocket_service: WebSocketService):
        """
        Initialize the Entity-Based Content Planner service
        
        Args:
            google_nl_client: Google Natural Language API client
            knowledge_graph_client: Google Knowledge Graph API client
            cache_manager: Advanced cache manager instance
            websocket_service: WebSocket service for real-time updates
        """
        self.google_nl_client = google_nl_client
        self.knowledge_graph_client = knowledge_graph_client
        self.cache_manager = cache_manager
        self.websocket_service = websocket_service
        self.rate_limiter = RateLimiter()
        
        # Initialize NLP models
        try:
            self.nlp_model = spacy.load("en_core_web_lg")
        except OSError:
            logger.warning("Large spaCy model not found, using medium model")
            self.nlp_model = spacy.load("en_core_web_md")
        
        # Initialize TF-IDF for authority scoring
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.8
        )
        
        # Configuration
        self.config = {
            'max_competitor_urls': 20,
            'max_content_length': 50000,  # chars
            'min_entity_confidence': 0.7,
            'min_relationship_strength': 0.3,
            'cache_ttl': 43200,  # 12 hours
            'max_processing_time': 300,  # 5 minutes
            'entity_categories': {
                'PERSON': 'People',
                'ORG': 'Organizations', 
                'PRODUCT': 'Products',
                'EVENT': 'Events',
                'WORK_OF_ART': 'Content',
                'GPE': 'Places',
                'NORP': 'Groups',
                'FACILITY': 'Facilities',
                'LANGUAGE': 'Languages',
                'DATE': 'Dates',
                'MONEY': 'Financial',
                'PERCENT': 'Statistics',
                'CARDINAL': 'Numbers'
            }
        }
    
    async def analyze_entities_for_topic(self, topic: str, user_id: str,
                                       competitor_urls: Optional[List[str]] = None,
                                       options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main method to analyze entities for comprehensive content planning
        
        Args:
            topic: Target topic for entity analysis
            user_id: User ID for personalization and caching
            competitor_urls: Optional list of competitor URLs to analyze
            options: Additional options for customization
            
        Returns:
            Dictionary containing entity analysis and content recommendations
        """
        start_time = datetime.utcnow()
        session_id = self._generate_session_id(topic, user_id)
        
        try:
            # Initialize WebSocket session
            if self.websocket_service:
                await self._start_websocket_session(session_id, topic, user_id)
            
            # Check cache first
            cache_key = self._generate_cache_key(topic, competitor_urls, options)
            cached_result = self.cache_manager.get('entity_analysis', cache_key)
            
            if cached_result:
                logger.info(f"Cache hit for entity analysis: {topic}")
                await self._complete_websocket_session(session_id, cached_result, cache_hit=True)
                return cached_result
            
            # Step 1: Content Acquisition
            await self._update_progress(session_id, 1, "Content Acquisition", 
                                      "Gathering content from top-ranking pages")
            
            content_data = await self._acquire_content_data(topic, competitor_urls)
            
            # Step 2: Entity Extraction
            await self._update_progress(session_id, 2, "Entity Extraction", 
                                      "Extracting entities using advanced NLP models")
            
            extracted_entities = await self._extract_entities_from_content(content_data)
            
            # Step 3: Entity Enhancement
            await self._update_progress(session_id, 3, "Entity Enhancement", 
                                      "Enriching entities with knowledge graph data")
            
            enhanced_entities = await self._enhance_entities_with_knowledge_graph(extracted_entities)
            
            # Step 4: Relationship Mapping
            await self._update_progress(session_id, 4, "Relationship Mapping", 
                                      "Mapping relationships between entities")
            
            entity_relationships = await self._map_entity_relationships(enhanced_entities, content_data)
            
            # Step 5: Authority Analysis
            await self._update_progress(session_id, 5, "Authority Analysis", 
                                      "Calculating topical authority and content gaps")
            
            authority_analysis = await self._analyze_topical_authority(enhanced_entities, entity_relationships, content_data)
            
            # Step 6: Result Compilation
            await self._update_progress(session_id, 6, "Result Compilation", 
                                      "Generating content planning recommendations")
            
            final_result = await self._compile_entity_analysis_results(
                topic, enhanced_entities, entity_relationships, authority_analysis, 
                content_data, start_time, user_id
            )
            
            # Cache the results
            self.cache_manager.set('entity_analysis', cache_key, 
                                 final_result, ttl=self.config['cache_ttl'])
            
            # Complete WebSocket session
            await self._complete_websocket_session(session_id, final_result)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in entity content planning: {str(e)}")
            if self.websocket_service:
                await self._fail_websocket_session(session_id, str(e))
            raise
    
    async def _acquire_content_data(self, topic: str, 
                                  competitor_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Acquire content from SERP results and competitor URLs
        
        Args:
            topic: Target topic for content acquisition
            competitor_urls: Optional list of competitor URLs
            
        Returns:
            Dictionary containing scraped content data
        """
        content_data = {
            'serp_content': [],
            'competitor_content': [],
            'all_content': [],
            'metadata': {
                'sources_processed': 0,
                'total_content_length': 0,
                'successful_scrapes': 0,
                'failed_scrapes': 0
            }
        }
        
        # Get SERP results for the topic
        serp_urls = await self._get_serp_urls_for_topic(topic)
        
        # Combine SERP URLs with competitor URLs
        all_urls = serp_urls[:self.config['max_competitor_urls']]
        if competitor_urls:
            all_urls.extend(competitor_urls[:10])  # Limit competitor URLs
        
        # Remove duplicates
        all_urls = list(dict.fromkeys(all_urls))
        
        # Scrape content from all URLs
        scraping_tasks = [self._scrape_url_content(url) for url in all_urls]
        scraping_results = await asyncio.gather(*scraping_tasks, return_exceptions=True)
        
        for idx, result in enumerate(scraping_results):
            url = all_urls[idx]
            content_data['metadata']['sources_processed'] += 1
            
            if isinstance(result, Exception):
                logger.warning(f"Failed to scrape {url}: {str(result)}")
                content_data['metadata']['failed_scrapes'] += 1
                continue
            
            if result and len(result.get('text', '')) > 100:
                content_item = {
                    'url': url,
                    'text': result['text'][:self.config['max_content_length']],
                    'title': result.get('title', ''),
                    'meta_description': result.get('meta_description', ''),
                    'headings': result.get('headings', []),
                    'content_length': len(result['text'])
                }
                
                # Categorize content
                if idx < len(serp_urls):
                    content_data['serp_content'].append(content_item)
                else:
                    content_data['competitor_content'].append(content_item)
                
                content_data['all_content'].append(content_item)
                content_data['metadata']['total_content_length'] += content_item['content_length']
                content_data['metadata']['successful_scrapes'] += 1
        
        logger.info(f"Acquired content from {content_data['metadata']['successful_scrapes']} sources")
        return content_data
    
    async def _get_serp_urls_for_topic(self, topic: str) -> List[str]:
        """
        Get SERP URLs for the given topic using Google Custom Search
        """
        try:
            self.rate_limiter.wait_if_needed('google_apis')
            
            search_results = await self.google_nl_client.search_client.search(
                query=topic,
                num_results=self.config['max_competitor_urls']
            )
            
            urls = []
            if 'items' in search_results:
                for item in search_results['items']:
                    if 'link' in item:
                        urls.append(item['link'])
            
            return urls
            
        except Exception as e:
            logger.warning(f"Failed to get SERP URLs for topic '{topic}': {str(e)}")
            return []
    
    async def _scrape_url_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape content from a single URL
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped content or None if failed
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, 
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; SERPStrategists/1.0; +https://serpstrategists.com)'
                    }
                ) as response:
                    if response.status != 200:
                        return None
                    
                    html_content = await response.text()
                    return self._extract_content_from_html(html_content, url)
        
        except Exception as e:
            logger.warning(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_content_from_html(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract structured content from HTML
        
        Args:
            html: Raw HTML content
            url: Source URL
            
        Returns:
            Dictionary containing extracted content elements
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else ''
        
        # Extract meta description
        meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_desc_tag.get('content', '').strip() if meta_desc_tag else ''
        
        # Extract headings
        headings = []
        for heading_tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(heading_tag.name[1]),
                'text': heading_tag.get_text().strip()
            })
        
        # Extract main content
        # Try to find main content areas
        main_content_selectors = [
            'main', 'article', '.content', '.post', '.entry', 
            '[role="main"]', '.main-content'
        ]
        
        main_content = None
        for selector in main_content_selectors:
            main_element = soup.select_one(selector)
            if main_element:
                main_content = main_element
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text content
        text_content = main_content.get_text(separator=' ', strip=True)
        
        # Clean up text
        text_content = re.sub(r'\s+', ' ', text_content)
        text_content = text_content.strip()
        
        return {
            'url': url,
            'title': title,
            'meta_description': meta_description,
            'headings': headings,
            'text': text_content
        }
    
    async def _extract_entities_from_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from all content using multiple NER approaches
        
        Args:
            content_data: Content data from acquisition step
            
        Returns:
            Dictionary containing extracted entities
        """
        all_entities = defaultdict(list)
        entity_sources = defaultdict(set)
        entity_contexts = defaultdict(list)
        
        # Process each piece of content
        for content_item in content_data['all_content']:
            text = content_item['text']
            url = content_item['url']
            
            # Extract entities using spaCy
            spacy_entities = await self._extract_entities_with_spacy(text)
            
            # Extract entities using Google Natural Language API
            google_entities = await self._extract_entities_with_google_nl(text)
            
            # Merge entities from both sources
            merged_entities = self._merge_entity_results(spacy_entities, google_entities)
            
            # Add entities to collections
            for entity in merged_entities:
                entity_text = entity['text'].lower()
                entity_type = entity['type']
                confidence = entity['confidence']
                
                if confidence >= self.config['min_entity_confidence']:
                    all_entities[entity_type].append({
                        'text': entity_text,
                        'display_text': entity['text'],
                        'confidence': confidence,
                        'salience': entity.get('salience', 0),
                        'mentions': entity.get('mentions', 1)
                    })
                    
                    entity_sources[entity_text].add(url)
                    entity_contexts[entity_text].append({
                        'url': url,
                        'context': self._extract_entity_context(text, entity['text']),
                        'title': content_item.get('title', '')
                    })
        
        # Aggregate and score entities
        aggregated_entities = self._aggregate_entities(all_entities, entity_sources, entity_contexts)
        
        return {
            'entities_by_type': aggregated_entities,
            'total_entities': sum(len(entities) for entities in aggregated_entities.values()),
            'entity_sources': dict(entity_sources),
            'entity_contexts': dict(entity_contexts)
        }
    
    async def _extract_entities_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using spaCy NER model
        """
        try:
            # Process text with spaCy
            doc = self.nlp_model(text[:1000000])  # Limit text length for processing
            
            entities = []
            for ent in doc.ents:
                if len(ent.text.strip()) > 1 and ent.label_ in self.config['entity_categories']:
                    entities.append({
                        'text': ent.text,
                        'type': ent.label_,
                        'confidence': 0.8,  # spaCy doesn't provide confidence scores
                        'start': ent.start_char,
                        'end': ent.end_char,
                        'mentions': 1
                    })
            
            return entities
            
        except Exception as e:
            logger.warning(f"spaCy entity extraction error: {str(e)}")
            return []
    
    async def _extract_entities_with_google_nl(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities using Google Natural Language API
        """
        try:
            self.rate_limiter.wait_if_needed('google_apis')
            
            # Limit text length for API call
            text_sample = text[:5000] if len(text) > 5000 else text
            
            response = await self.google_nl_client.analyze_entities(text_sample)
            
            entities = []
            if 'entities' in response:
                for entity in response['entities']:
                    entity_type = entity.get('type', 'OTHER')
                    confidence = entity.get('salience', 0.5)  # Use salience as confidence
                    
                    if entity_type in self.config['entity_categories'] or entity_type == 'OTHER':
                        entities.append({
                            'text': entity['name'],
                            'type': entity_type,
                            'confidence': confidence,
                            'salience': entity.get('salience', 0),
                            'mentions': len(entity.get('mentions', [])),
                            'wikipedia_url': entity.get('metadata', {}).get('wikipedia_url'),
                            'mid': entity.get('metadata', {}).get('mid')
                        })
            
            return entities
            
        except Exception as e:
            logger.warning(f"Google NL entity extraction error: {str(e)}")
            return []
    
    def _merge_entity_results(self, spacy_entities: List[Dict[str, Any]], 
                            google_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge entity results from different NER sources
        """
        merged_entities = {}
        
        # Add spaCy entities
        for entity in spacy_entities:
            key = entity['text'].lower()
            merged_entities[key] = entity
        
        # Add or merge Google entities
        for entity in google_entities:
            key = entity['text'].lower()
            if key in merged_entities:
                # Merge with existing entity
                existing = merged_entities[key]
                existing['confidence'] = max(existing['confidence'], entity['confidence'])
                existing['salience'] = entity.get('salience', existing.get('salience', 0))
                existing['mentions'] += entity.get('mentions', 1)
                if 'wikipedia_url' in entity:
                    existing['wikipedia_url'] = entity['wikipedia_url']
                if 'mid' in entity:
                    existing['mid'] = entity['mid']
            else:
                # Add new entity
                merged_entities[key] = entity
        
        return list(merged_entities.values())
    
    def _extract_entity_context(self, text: str, entity_text: str, context_window: int = 100) -> str:
        """
        Extract context around an entity mention
        """
        # Find entity in text (case insensitive)
        text_lower = text.lower()
        entity_lower = entity_text.lower()
        
        start_pos = text_lower.find(entity_lower)
        if start_pos == -1:
            return ""
        
        # Extract context window
        context_start = max(0, start_pos - context_window)
        context_end = min(len(text), start_pos + len(entity_text) + context_window)
        
        context = text[context_start:context_end]
        return context.strip()
    
    def _aggregate_entities(self, all_entities: Dict[str, List[Dict[str, Any]]], 
                          entity_sources: Dict[str, Set[str]], 
                          entity_contexts: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Aggregate entities by frequency and importance
        """
        aggregated = {}
        
        for entity_type, entities in all_entities.items():
            # Group entities by text
            entity_groups = defaultdict(list)
            for entity in entities:
                entity_groups[entity['text']].append(entity)
            
            # Aggregate each group
            type_entities = []
            for entity_text, group in entity_groups.items():
                if len(group) >= 1:  # Only include entities mentioned at least once
                    aggregated_entity = {
                        'text': entity_text,
                        'display_text': group[0]['display_text'],
                        'type': entity_type,
                        'category': self.config['entity_categories'].get(entity_type, 'Other'),
                        'frequency': len(group),
                        'avg_confidence': sum(e['confidence'] for e in group) / len(group),
                        'avg_salience': sum(e.get('salience', 0) for e in group) / len(group),
                        'total_mentions': sum(e.get('mentions', 1) for e in group),
                        'source_count': len(entity_sources.get(entity_text, set())),
                        'sources': list(entity_sources.get(entity_text, set())),
                        'contexts': entity_contexts.get(entity_text, [])[:3],  # Top 3 contexts
                        'authority_score': self._calculate_entity_authority_score(
                            len(group), 
                            len(entity_sources.get(entity_text, set())), 
                            sum(e.get('salience', 0) for e in group) / len(group)
                        )
                    }
                    
                    # Add Wikipedia info if available
                    if any('wikipedia_url' in e for e in group):
                        wikipedia_entity = next(e for e in group if 'wikipedia_url' in e)
                        aggregated_entity['wikipedia_url'] = wikipedia_entity['wikipedia_url']
                    
                    if any('mid' in e for e in group):
                        mid_entity = next(e for e in group if 'mid' in e)
                        aggregated_entity['knowledge_graph_id'] = mid_entity['mid']
                    
                    type_entities.append(aggregated_entity)
            
            # Sort by authority score
            type_entities.sort(key=lambda x: x['authority_score'], reverse=True)
            aggregated[entity_type] = type_entities
        
        return aggregated
    
    def _calculate_entity_authority_score(self, frequency: int, source_count: int, salience: float) -> float:
        """
        Calculate authority score for an entity based on multiple factors
        """
        # Normalize frequency (log scale to prevent domination)
        freq_score = min(1.0, np.log(frequency + 1) / np.log(10))
        
        # Source diversity score
        source_score = min(1.0, source_count / 10)
        
        # Salience score (already normalized 0-1)
        salience_score = min(1.0, salience)
        
        # Weighted combination
        authority_score = (
            freq_score * 0.4 +
            source_score * 0.4 + 
            salience_score * 0.2
        )
        
        return round(authority_score, 3)
    
    async def _enhance_entities_with_knowledge_graph(self, extracted_entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance entities with Knowledge Graph data
        """
        enhanced_entities = extracted_entities.copy()
        
        # Get top entities for Knowledge Graph enhancement
        top_entities = []
        for entity_type, entities in extracted_entities['entities_by_type'].items():
            top_entities.extend(entities[:5])  # Top 5 per type
        
        # Sort by authority score and take top 20
        top_entities.sort(key=lambda x: x['authority_score'], reverse=True)
        top_entities = top_entities[:20]
        
        # Enhance with Knowledge Graph data
        for entity in top_entities:
            try:
                kg_data = await self._get_knowledge_graph_data(entity['text'])
                if kg_data:
                    entity.update({
                        'description': kg_data.get('description', ''),
                        'types': kg_data.get('types', []),
                        'properties': kg_data.get('properties', {}),
                        'related_entities': kg_data.get('related_entities', [])[:5]
                    })
            except Exception as e:
                logger.warning(f"Knowledge Graph enhancement failed for '{entity['text']}': {str(e)}")
                continue
        
        return enhanced_entities
    
    async def _get_knowledge_graph_data(self, entity_name: str) -> Optional[Dict[str, Any]]:
        """
        Get entity data from Google Knowledge Graph
        """
        try:
            self.rate_limiter.wait_if_needed('google_apis')
            
            kg_data = await self.knowledge_graph_client.search_entities(entity_name, limit=1)
            
            if kg_data and 'itemListElement' in kg_data and kg_data['itemListElement']:
                entity_data = kg_data['itemListElement'][0]['result']
                
                return {
                    'id': entity_data.get('@id'),
                    'description': entity_data.get('description', ''),
                    'detailed_description': entity_data.get('detailedDescription', {}).get('articleBody', ''),
                    'types': entity_data.get('@type', []),
                    'properties': {
                        k: v for k, v in entity_data.items() 
                        if not k.startswith('@') and k not in ['description', 'detailedDescription']
                    },
                    'url': entity_data.get('url'),
                    'image': entity_data.get('image', {}).get('contentUrl') if entity_data.get('image') else None
                }
                
        except Exception as e:
            logger.warning(f"Knowledge Graph API error for '{entity_name}': {str(e)}")
        
        return None
    
    async def _map_entity_relationships(self, enhanced_entities: Dict[str, Any], 
                                      content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map relationships between entities based on co-occurrence and semantic similarity
        """
        # Get all entities as a flat list
        all_entities = []
        for entity_type, entities in enhanced_entities['entities_by_type'].items():
            all_entities.extend(entities)
        
        # Create entity co-occurrence matrix
        cooccurrence_matrix = self._calculate_entity_cooccurrence(all_entities, content_data)
        
        # Build relationship graph
        relationship_graph = self._build_entity_relationship_graph(all_entities, cooccurrence_matrix)
        
        # Identify entity clusters/themes
        entity_clusters = self._identify_entity_clusters(relationship_graph, all_entities)
        
        return {
            'cooccurrence_matrix': cooccurrence_matrix,
            'relationship_graph': relationship_graph,
            'entity_clusters': entity_clusters,
            'total_relationships': len(relationship_graph['edges']),
            'avg_relationship_strength': np.mean([edge['weight'] for edge in relationship_graph['edges']]) if relationship_graph['edges'] else 0
        }
    
    def _calculate_entity_cooccurrence(self, entities: List[Dict[str, Any]], 
                                     content_data: Dict[str, Any]]) -> Dict[Tuple[str, str], float]:
        """
        Calculate co-occurrence strength between entities
        """
        cooccurrence = defaultdict(int)
        entity_names = [entity['text'].lower() for entity in entities]
        
        # Check co-occurrence in each content piece
        for content_item in content_data['all_content']:
            text = content_item['text'].lower()
            
            # Find which entities appear in this content
            present_entities = [name for name in entity_names if name in text]
            
            # Count co-occurrences
            for i, entity1 in enumerate(present_entities):
                for entity2 in present_entities[i+1:]:
                    pair = tuple(sorted([entity1, entity2]))
                    cooccurrence[pair] += 1
        
        # Normalize co-occurrence scores
        max_cooccurrence = max(cooccurrence.values()) if cooccurrence else 1
        normalized_cooccurrence = {
            pair: count / max_cooccurrence 
            for pair, count in cooccurrence.items()
            if count / max_cooccurrence >= self.config['min_relationship_strength']
        }
        
        return normalized_cooccurrence
    
    def _build_entity_relationship_graph(self, entities: List[Dict[str, Any]], 
                                       cooccurrence_matrix: Dict[Tuple[str, str], float]) -> Dict[str, Any]:
        """
        Build a graph of entity relationships
        """
        # Create NetworkX graph
        G = nx.Graph()
        
        # Add nodes (entities)
        entity_map = {entity['text'].lower(): entity for entity in entities}
        for entity in entities:
            G.add_node(entity['text'].lower(), 
                      authority_score=entity['authority_score'],
                      category=entity.get('category', 'Other'),
                      frequency=entity['frequency'])
        
        # Add edges (relationships)
        edges = []
        for (entity1, entity2), weight in cooccurrence_matrix.items():
            G.add_edge(entity1, entity2, weight=weight)
            edges.append({
                'source': entity1,
                'target': entity2,
                'weight': weight,
                'relationship_type': self._determine_relationship_type(
                    entity_map.get(entity1), entity_map.get(entity2)
                )
            })
        
        # Calculate graph metrics
        try:
            centrality = nx.betweenness_centrality(G, weight='weight')
            pagerank = nx.pagerank(G, weight='weight')
        except:
            centrality = {node: 0 for node in G.nodes()}
            pagerank = {node: 1/len(G.nodes()) for node in G.nodes()}
        
        # Update entity scores with graph metrics
        for entity in entities:
            entity_key = entity['text'].lower()
            entity['centrality_score'] = centrality.get(entity_key, 0)
            entity['pagerank_score'] = pagerank.get(entity_key, 0)
            entity['combined_authority'] = (
                entity['authority_score'] * 0.5 +
                centrality.get(entity_key, 0) * 0.3 +
                pagerank.get(entity_key, 0) * 0.2
            )
        
        return {
            'nodes': [
                {
                    'id': node,
                    'entity_data': entity_map.get(node, {}),
                    'centrality': centrality.get(node, 0),
                    'pagerank': pagerank.get(node, 0)
                }
                for node in G.nodes()
            ],
            'edges': edges,
            'graph_density': nx.density(G),
            'connected_components': nx.number_connected_components(G)
        }
    
    def _determine_relationship_type(self, entity1: Optional[Dict[str, Any]], 
                                   entity2: Optional[Dict[str, Any]]) -> str:
        """
        Determine the type of relationship between two entities
        """
        if not entity1 or not entity2:
            return 'general'
        
        cat1 = entity1.get('category', '').lower()
        cat2 = entity2.get('category', '').lower()
        
        relationship_types = {
            ('people', 'organizations'): 'works_for',
            ('people', 'places'): 'located_in',
            ('products', 'organizations'): 'made_by',
            ('events', 'places'): 'located_in',
            ('events', 'people'): 'involves',
            ('organizations', 'places'): 'based_in'
        }
        
        # Check both directions
        relationship = relationship_types.get((cat1, cat2)) or relationship_types.get((cat2, cat1))
        return relationship or 'related_to'
    
    def _identify_entity_clusters(self, relationship_graph: Dict[str, Any], 
                                entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify clusters of related entities
        """
        # Create NetworkX graph from relationship data
        G = nx.Graph()
        
        for node in relationship_graph['nodes']:
            G.add_node(node['id'])
        
        for edge in relationship_graph['edges']:
            G.add_edge(edge['source'], edge['target'], weight=edge['weight'])
        
        # Find communities using Louvain algorithm
        try:
            import community
            communities = community.best_partition(G)
        except ImportError:
            # Fallback to connected components if community detection not available
            communities = {}
            for i, component in enumerate(nx.connected_components(G)):
                for node in component:
                    communities[node] = i
        
        # Group entities by community
        clusters = defaultdict(list)
        entity_map = {entity['text'].lower(): entity for entity in entities}
        
        for entity_name, cluster_id in communities.items():
            if entity_name in entity_map:
                clusters[cluster_id].append(entity_map[entity_name])
        
        # Format cluster results
        cluster_results = []
        for cluster_id, cluster_entities in clusters.items():
            if len(cluster_entities) >= 2:  # Only include clusters with 2+ entities
                # Calculate cluster metrics
                avg_authority = sum(e['authority_score'] for e in cluster_entities) / len(cluster_entities)
                total_frequency = sum(e['frequency'] for e in cluster_entities)
                
                # Determine cluster theme
                categories = [e.get('category', 'Other') for e in cluster_entities]
                dominant_category = max(set(categories), key=categories.count)
                
                cluster_results.append({
                    'cluster_id': cluster_id,
                    'theme': dominant_category,
                    'entities': sorted(cluster_entities, key=lambda x: x['authority_score'], reverse=True),
                    'size': len(cluster_entities),
                    'avg_authority': avg_authority,
                    'total_frequency': total_frequency,
                    'cohesion_score': self._calculate_cluster_cohesion(cluster_entities, relationship_graph)
                })
        
        # Sort clusters by importance
        cluster_results.sort(key=lambda x: (x['avg_authority'], x['size']), reverse=True)
        
        return cluster_results
    
    def _calculate_cluster_cohesion(self, cluster_entities: List[Dict[str, Any]], 
                                  relationship_graph: Dict[str, Any]]) -> float:
        """
        Calculate how cohesive a cluster is based on internal connections
        """
        entity_names = [e['text'].lower() for e in cluster_entities]
        
        # Count internal edges
        internal_edges = 0
        total_possible = len(entity_names) * (len(entity_names) - 1) // 2
        
        for edge in relationship_graph['edges']:
            if edge['source'] in entity_names and edge['target'] in entity_names:
                internal_edges += 1
        
        return internal_edges / total_possible if total_possible > 0 else 0
    
    async def _analyze_topical_authority(self, enhanced_entities: Dict[str, Any], 
                                       entity_relationships: Dict[str, Any], 
                                       content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze topical authority and identify content gaps
        """
        # Get top entities by authority
        all_entities = []
        for entity_type, entities in enhanced_entities['entities_by_type'].items():
            all_entities.extend(entities)
        
        all_entities.sort(key=lambda x: x.get('combined_authority', x['authority_score']), reverse=True)
        
        # Identify must-have entities (high authority, high centrality)
        must_have_entities = [
            e for e in all_entities[:20] 
            if e.get('combined_authority', e['authority_score']) > 0.7
        ]
        
        # Identify supporting entities
        supporting_entities = [
            e for e in all_entities[20:50]
            if e.get('combined_authority', e['authority_score']) > 0.4
        ]
        
        # Analyze content gaps
        content_gaps = self._identify_content_gaps(all_entities, content_data)
        
        # Calculate overall authority score
        authority_score = self._calculate_overall_authority_score(
            must_have_entities, supporting_entities, entity_relationships
        )
        
        return {
            'must_have_entities': must_have_entities,
            'supporting_entities': supporting_entities,
            'content_gaps': content_gaps,
            'authority_score': authority_score,
            'entity_coverage': {
                'total_entities_found': len(all_entities),
                'high_authority_entities': len(must_have_entities),
                'supporting_entities': len(supporting_entities),
                'entity_diversity': len(set(e.get('category', 'Other') for e in all_entities))
            }
        }
    
    def _identify_content_gaps(self, entities: List[Dict[str, Any]], 
                             content_data: Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify entities that are underrepresented in content
        """
        gaps = []
        
        for entity in entities[:30]:  # Check top 30 entities
            # Calculate expected vs actual coverage
            authority_score = entity.get('combined_authority', entity['authority_score'])
            source_coverage = entity['source_count'] / len(content_data['all_content'])
            
            # If high authority but low coverage, it's a gap
            if authority_score > 0.6 and source_coverage < 0.3:
                gaps.append({
                    'entity': entity,
                    'gap_severity': 'high' if authority_score > 0.8 else 'medium',
                    'current_coverage': source_coverage,
                    'expected_coverage': authority_score,
                    'recommendation': f"Include more content about '{entity['display_text']}' to improve topical authority"
                })
        
        return sorted(gaps, key=lambda x: x['expected_coverage'] - x['current_coverage'], reverse=True)
    
    def _calculate_overall_authority_score(self, must_have_entities: List[Dict[str, Any]], 
                                         supporting_entities: List[Dict[str, Any]], 
                                         entity_relationships: Dict[str, Any]) -> float:
        """
        Calculate overall topical authority score
        """
        # Entity coverage score (0-1)
        coverage_score = min(1.0, (len(must_have_entities) + len(supporting_entities) * 0.5) / 20)
        
        # Entity quality score (average authority of top entities)
        if must_have_entities:
            quality_score = sum(e.get('combined_authority', e['authority_score']) 
                              for e in must_have_entities[:10]) / min(10, len(must_have_entities))
        else:
            quality_score = 0
        
        # Relationship richness score
        relationship_score = min(1.0, entity_relationships['total_relationships'] / 50)
        
        # Combined authority score
        authority_score = (
            coverage_score * 0.4 +
            quality_score * 0.4 +
            relationship_score * 0.2
        )
        
        return round(authority_score, 3)
    
    async def _compile_entity_analysis_results(self, topic: str, enhanced_entities: Dict[str, Any],
                                             entity_relationships: Dict[str, Any], 
                                             authority_analysis: Dict[str, Any],
                                             content_data: Dict[str, Any], 
                                             start_time: datetime, user_id: str) -> Dict[str, Any]:
        """
        Compile final entity analysis results
        """
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Generate content recommendations
        content_recommendations = self._generate_content_recommendations(
            authority_analysis['must_have_entities'],
            authority_analysis['supporting_entities'],
            authority_analysis['content_gaps'],
            entity_relationships['entity_clusters']
        )
        
        result = {
            'analysis_id': self._generate_session_id(topic, user_id),
            'topic': topic,
            'entities_by_category': self._organize_entities_by_category(enhanced_entities['entities_by_type']),
            'must_have_entities': authority_analysis['must_have_entities'][:15],
            'supporting_entities': authority_analysis['supporting_entities'][:20],
            'entity_relationships': {
                'clusters': entity_relationships['entity_clusters'][:10],
                'key_relationships': sorted(entity_relationships['relationship_graph']['edges'], 
                                          key=lambda x: x['weight'], reverse=True)[:20]
            },
            'content_gaps': authority_analysis['content_gaps'][:10],
            'authority_analysis': {
                'overall_score': authority_analysis['authority_score'],
                'entity_coverage': authority_analysis['entity_coverage'],
                'recommendations': content_recommendations
            },
            'insights': {
                'total_entities_discovered': enhanced_entities['total_entities'],
                'entity_diversity': len(enhanced_entities['entities_by_type']),
                'relationship_density': entity_relationships['relationship_graph']['graph_density'],
                'content_sources_analyzed': content_data['metadata']['successful_scrapes'],
                'processing_efficiency': content_data['metadata']['successful_scrapes'] / content_data['metadata']['sources_processed'] if content_data['metadata']['sources_processed'] > 0 else 0
            },
            'metadata': {
                'processing_time_seconds': processing_time,
                'content_sources_processed': content_data['metadata']['sources_processed'],
                'successful_scrapes': content_data['metadata']['successful_scrapes'],
                'total_content_analyzed': content_data['metadata']['total_content_length'],
                'cache_status': 'miss',
                'created_at': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'version': '1.0'
            }
        }
        
        # Store in database for historical analysis
        await self._store_result_in_database(result, user_id)
        
        return result
    
    def _organize_entities_by_category(self, entities_by_type: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize entities by semantic categories rather than NER types
        """
        categories = {
            'People & Organizations': [],
            'Products & Services': [],
            'Places & Locations': [],
            'Concepts & Topics': [],
            'Events & Dates': [],
            'Other': []
        }
        
        category_mapping = {
            'PERSON': 'People & Organizations',
            'ORG': 'People & Organizations',
            'PRODUCT': 'Products & Services',
            'GPE': 'Places & Locations',
            'FACILITY': 'Places & Locations',
            'EVENT': 'Events & Dates',
            'DATE': 'Events & Dates',
            'WORK_OF_ART': 'Concepts & Topics',
            'LANGUAGE': 'Concepts & Topics',
            'NORP': 'Concepts & Topics'
        }
        
        for entity_type, entities in entities_by_type.items():
            category = category_mapping.get(entity_type, 'Other')
            categories[category].extend(entities)
        
        # Sort entities within each category by authority score
        for category in categories:
            categories[category].sort(key=lambda x: x.get('combined_authority', x['authority_score']), reverse=True)
        
        return categories
    
    def _generate_content_recommendations(self, must_have_entities: List[Dict[str, Any]],
                                        supporting_entities: List[Dict[str, Any]],
                                        content_gaps: List[Dict[str, Any]],
                                        entity_clusters: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate actionable content recommendations
        """
        recommendations = []
        
        # Must-have entity recommendations
        if must_have_entities:
            recommendations.append({
                'type': 'primary_entities',
                'priority': 'high',
                'title': 'Include Primary Entities',
                'description': f"Ensure your content covers these {len(must_have_entities)} essential entities: " + 
                              ', '.join([e['display_text'] for e in must_have_entities[:5]]) + 
                              (f" and {len(must_have_entities) - 5} more" if len(must_have_entities) > 5 else "")
            })
        
        # Content gap recommendations
        high_priority_gaps = [gap for gap in content_gaps if gap['gap_severity'] == 'high']
        if high_priority_gaps:
            recommendations.append({
                'type': 'content_gaps',
                'priority': 'high',
                'title': 'Address Critical Content Gaps',
                'description': f"Your content lacks coverage of important topics: " + 
                              ', '.join([gap['entity']['display_text'] for gap in high_priority_gaps[:3]])
            })
        
        # Entity cluster recommendations
        top_clusters = entity_clusters[:3]
        for cluster in top_clusters:
            recommendations.append({
                'type': 'entity_cluster',
                'priority': 'medium',
                'title': f'Develop {cluster["theme"]} Section',
                'description': f"Create comprehensive content covering {cluster['theme'].lower()}: " + 
                              ', '.join([e['display_text'] for e in cluster['entities'][:4]])
            })
        
        # Supporting entities recommendation
        if supporting_entities:
            recommendations.append({
                'type': 'supporting_entities',
                'priority': 'medium',
                'title': 'Include Supporting Topics',
                'description': f"Enhance your content with these supporting topics: " + 
                              ', '.join([e['display_text'] for e in supporting_entities[:5]])
            })
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    async def _store_result_in_database(self, result: Dict[str, Any], user_id: str) -> None:
        """
        Store entity analysis result in database
        """
        try:
            storage = EntityAnalysisStorage()
            await storage.save_entity_analysis(
                analysis_id=result['analysis_id'],
                topic=result['topic'],
                user_id=user_id,
                entities_by_category=result['entities_by_category'],
                must_have_entities=result['must_have_entities'],
                supporting_entities=result['supporting_entities'],
                entity_relationships=result['entity_relationships'],
                content_gaps=result['content_gaps'],
                authority_analysis=result['authority_analysis'],
                metadata=result['metadata']
            )
        except Exception as e:
            logger.warning(f"Failed to store entity analysis result: {str(e)}")
    
    # WebSocket helper methods (similar to query finder)
    async def _start_websocket_session(self, session_id: str, topic: str, user_id: str) -> None:
        if self.websocket_service:
            self.websocket_service.start_blueprint_session(
                blueprint_id=session_id,
                user_id=user_id,
                total_steps=6
            )
    
    async def _update_progress(self, session_id: str, step: int, step_name: str, message: str) -> None:
        if self.websocket_service:
            self.websocket_service.update_progress(
                blueprint_id=session_id,
                step=step,
                step_name=step_name,
                message=message
            )
    
    async def _complete_websocket_session(self, session_id: str, result: Dict[str, Any], cache_hit: bool = False) -> None:
        if self.websocket_service:
            processing_time = result['metadata']['processing_time_seconds'] if not cache_hit else 0.5
            self.websocket_service.complete_generation(
                blueprint_id=session_id,
                blueprint_data=result,
                generation_time=int(processing_time)
            )
    
    async def _fail_websocket_session(self, session_id: str, error_message: str) -> None:
        if self.websocket_service:
            self.websocket_service.fail_generation(
                blueprint_id=session_id,
                error_message=error_message
            )
    
    # Utility methods
    def _generate_session_id(self, topic: str, user_id: str) -> str:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        content = f"{topic}_{user_id}_{timestamp}"
        return f"entity_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _generate_cache_key(self, topic: str, competitor_urls: Optional[List[str]] = None, 
                          options: Optional[Dict[str, Any]] = None) -> str:
        content = topic
        if competitor_urls:
            content += "_".join(sorted(competitor_urls))
        if options:
            content += json.dumps(options, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def validate_input(self, topic: str, competitor_urls: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate input parameters
        """
        if not topic or not topic.strip():
            return False, "Topic is required"
        
        if len(topic) > 200:
            return False, "Topic must be less than 200 characters"
        
        if competitor_urls:
            if len(competitor_urls) > 20:
                return False, "Maximum 20 competitor URLs allowed"
            
            # Basic URL validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            for url in competitor_urls:
                if not url_pattern.match(url):
                    return False, f"Invalid URL format: {url}"
        
        return True, None
```

### **Database Model**
```python
"""
src/models/entity_analysis.py
"""

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone
import uuid
import json
from typing import Dict, List, Any, Optional

from src.models.blueprint import Base

class EntityAnalysis(Base):
    """
    Database model for storing entity-based content analysis
    """
    __tablename__ = 'entity_analyses'
    
    # Primary fields
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String(500), nullable=False)
    user_id = Column(String(36), nullable=False)
    
    # Entity data (stored as JSON)
    entities_by_category = Column(JSON, nullable=False)
    must_have_entities = Column(JSON, nullable=False)
    supporting_entities = Column(JSON, nullable=False)
    entity_relationships = Column(JSON, nullable=False)
    content_gaps = Column(JSON, nullable=True)
    
    # Analysis results
    authority_analysis = Column(JSON, nullable=True)
    insights = Column(JSON, nullable=True)
    
    # Metadata
    authority_score = Column(Float, nullable=True)
    total_entities = Column(Integer, nullable=True)
    processing_time = Column(Float, nullable=True)
    sources_analyzed = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True)
    
    # Database indexes
    __table_args__ = (
        Index('idx_user_topic', 'user_id', 'topic'),
        Index('idx_authority_score', 'authority_score'),
        Index('idx_created_at', 'created_at'),
        Index('idx_expires_at', 'expires_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'topic': self.topic,
            'user_id': self.user_id,
            'entities_by_category': self.entities_by_category,
            'must_have_entities': self.must_have_entities,
            'supporting_entities': self.supporting_entities,
            'entity_relationships': self.entity_relationships,
            'content_gaps': self.content_gaps,
            'authority_analysis': self.authority_analysis,
            'insights': self.insights,
            'authority_score': self.authority_score,
            'total_entities': self.total_entities,
            'processing_time': self.processing_time,
            'sources_analyzed': self.sources_analyzed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class EntityAnalysisStorage:
    """
    Storage service for entity analyses
    """
    
    def __init__(self, db_session=None):
        self.db_session = db_session
    
    async def save_entity_analysis(self, analysis_id: str, topic: str, user_id: str,
                                 entities_by_category: Dict[str, List[Dict[str, Any]]],
                                 must_have_entities: List[Dict[str, Any]],
                                 supporting_entities: List[Dict[str, Any]],
                                 entity_relationships: Dict[str, Any],
                                 content_gaps: List[Dict[str, Any]],
                                 authority_analysis: Dict[str, Any],
                                 metadata: Dict[str, Any]) -> str:
        """
        Save entity analysis to database
        """
        try:
            # Calculate expiration (12 hours from now)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=12)
            
            entity_analysis = EntityAnalysis(
                id=analysis_id,
                topic=topic,
                user_id=user_id,
                entities_by_category=entities_by_category,
                must_have_entities=must_have_entities,
                supporting_entities=supporting_entities,
                entity_relationships=entity_relationships,
                content_gaps=content_gaps,
                authority_analysis=authority_analysis,
                insights=metadata.get('insights', {}),
                authority_score=authority_analysis.get('overall_score'),
                total_entities=sum(len(entities) for entities in entities_by_category.values()),
                processing_time=metadata.get('processing_time_seconds'),
                sources_analyzed=metadata.get('successful_scrapes'),
                expires_at=expires_at
            )
            
            if self.db_session:
                self.db_session.add(entity_analysis)
                self.db_session.commit()
            
            return analysis_id
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            raise Exception(f"Failed to save entity analysis: {str(e)}")
    
    async def get_entity_analysis(self, analysis_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve entity analysis by ID
        """
        if not self.db_session:
            return None
        
        analysis = self.db_session.query(EntityAnalysis).filter(
            EntityAnalysis.id == analysis_id,
            EntityAnalysis.user_id == user_id,
            EntityAnalysis.expires_at > datetime.now(timezone.utc)
        ).first()
        
        return analysis.to_dict() if analysis else None
    
    async def list_user_entity_analyses(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List entity analyses for a user
        """
        if not self.db_session:
            return []
        
        analyses = self.db_session.query(EntityAnalysis).filter(
            EntityAnalysis.user_id == user_id,
            EntityAnalysis.expires_at > datetime.now(timezone.utc)
        ).order_by(EntityAnalysis.created_at.desc()).offset(offset).limit(limit).all()
        
        return [analysis.to_dict() for analysis in analyses]
```

---

## 🔌 API Specification

### **Endpoint Definition**
```yaml
Method: POST
Path: /api/content/entity-analysis
Authentication: JWT Token Required
Rate Limits:
  - Free Tier: 10 requests/hour
  - Pro Tier: 50 requests/hour
  - Enterprise: Unlimited

Content-Type: application/json
```

### **Request Schema**
```json
{
  "type": "object",
  "required": ["topic"],
  "properties": {
    "topic": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "Target topic for entity analysis"
    },
    "competitor_urls": {
      "type": "array",
      "items": {
        "type": "string",
        "format": "uri"
      },
      "maxItems": 20,
      "description": "Optional competitor URLs to analyze"
    },
    "options": {
      "type": "object",
      "properties": {
        "max_entities": {
          "type": "integer",
          "minimum": 10,
          "maximum": 100,
          "default": 50,
          "description": "Maximum number of entities to return"
        },
        "include_relationships": {
          "type": "boolean",
          "default": true,
          "description": "Include entity relationship mapping"
        },
        "authority_threshold": {
          "type": "number",
          "minimum": 0.1,
          "maximum": 1.0,
          "default": 0.5,
          "description": "Minimum authority score for entity inclusion"
        },
        "focus_categories": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["People & Organizations", "Products & Services", "Places & Locations", "Concepts & Topics", "Events & Dates"]
          },
          "description": "Focus on specific entity categories"
        }
      }
    }
  }
}
```

### **Response Schema**
```json
{
  "type": "object",
  "properties": {
    "analysis_id": {
      "type": "string",
      "description": "Unique identifier for this analysis"
    },
    "topic": {
      "type": "string",
      "description": "Original topic analyzed"
    },
    "entities_by_category": {
      "type": "object",
      "properties": {
        "People & Organizations": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "Products & Services": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "Places & Locations": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "Concepts & Topics": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "Events & Dates": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "Other": {"type": "array", "items": {"$ref": "#/definitions/Entity"}}
      }
    },
    "must_have_entities": {
      "type": "array",
      "items": {"$ref": "#/definitions/Entity"},
      "description": "High-authority entities that must be covered"
    },
    "supporting_entities": {
      "type": "array", 
      "items": {"$ref": "#/definitions/Entity"},
      "description": "Supporting entities for comprehensive coverage"
    },
    "entity_relationships": {
      "type": "object",
      "properties": {
        "clusters": {"type": "array", "items": {"$ref": "#/definitions/EntityCluster"}},
        "key_relationships": {"type": "array", "items": {"$ref": "#/definitions/EntityRelationship"}}
      }
    },
    "content_gaps": {
      "type": "array",
      "items": {"$ref": "#/definitions/ContentGap"}
    },
    "authority_analysis": {
      "type": "object",
      "properties": {
        "overall_score": {"type": "number"},
        "entity_coverage": {"type": "object"},
        "recommendations": {"type": "array", "items": {"$ref": "#/definitions/Recommendation"}}
      }
    },
    "insights": {
      "type": "object",
      "properties": {
        "total_entities_discovered": {"type": "integer"},
        "entity_diversity": {"type": "integer"},
        "relationship_density": {"type": "number"},
        "content_sources_analyzed": {"type": "integer"},
        "processing_efficiency": {"type": "number"}
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "processing_time_seconds": {"type": "number"},
        "content_sources_processed": {"type": "integer"},
        "successful_scrapes": {"type": "integer"},
        "total_content_analyzed": {"type": "integer"},
        "cache_status": {"type": "string", "enum": ["hit", "miss"]},
        "created_at": {"type": "string", "format": "date-time"},
        "user_id": {"type": "string"},
        "version": {"type": "string"}
      }
    }
  },
  "definitions": {
    "Entity": {
      "type": "object",
      "properties": {
        "text": {"type": "string"},
        "display_text": {"type": "string"},
        "type": {"type": "string"},
        "category": {"type": "string"},
        "frequency": {"type": "integer"},
        "authority_score": {"type": "number"},
        "combined_authority": {"type": "number"},
        "source_count": {"type": "integer"},
        "description": {"type": "string"},
        "wikipedia_url": {"type": "string"},
        "related_entities": {"type": "array", "items": {"type": "string"}}
      }
    },
    "EntityCluster": {
      "type": "object", 
      "properties": {
        "cluster_id": {"type": "integer"},
        "theme": {"type": "string"},
        "entities": {"type": "array", "items": {"$ref": "#/definitions/Entity"}},
        "size": {"type": "integer"},
        "avg_authority": {"type": "number"},
        "cohesion_score": {"type": "number"}
      }
    },
    "EntityRelationship": {
      "type": "object",
      "properties": {
        "source": {"type": "string"},
        "target": {"type": "string"},
        "weight": {"type": "number"},
        "relationship_type": {"type": "string"}
      }
    },
    "ContentGap": {
      "type": "object",
      "properties": {
        "entity": {"$ref": "#/definitions/Entity"},
        "gap_severity": {"type": "string", "enum": ["high", "medium", "low"]},
        "current_coverage": {"type": "number"},
        "expected_coverage": {"type": "number"},
        "recommendation": {"type": "string"}
      }
    },
    "Recommendation": {
      "type": "object",
      "properties": {
        "type": {"type": "string"},
        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
        "title": {"type": "string"},
        "description": {"type": "string"}
      }
    }
  }
}
```

---

## 🧪 Testing Specification

### **Unit Tests**
```python
"""
tests/test_entity_content_planner.py
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.services.entity_content_planner import EntityBasedContentPlannerService

class TestEntityBasedContentPlannerService:
    
    @pytest.fixture
    def service(self):
        google_nl_client = Mock()
        knowledge_graph_client = Mock()
        cache_manager = Mock()
        websocket_service = Mock()
        
        service = EntityBasedContentPlannerService(
            google_nl_client=google_nl_client,
            knowledge_graph_client=knowledge_graph_client,
            cache_manager=cache_manager,
            websocket_service=websocket_service
        )
        return service
    
    @pytest.mark.asyncio
    async def test_analyze_entities_success(self, service):
        """Test successful entity analysis"""
        service.cache_manager.get.return_value = None
        
        with patch.object(service, '_acquire_content_data') as mock_acquire:
            mock_acquire.return_value = {
                'all_content': [
                    {'text': 'Content marketing involves creating valuable content', 'url': 'test.com', 'title': 'Test'}
                ],
                'metadata': {'successful_scrapes': 1, 'sources_processed': 1, 'total_content_length': 100}
            }
            
            with patch.object(service, '_extract_entities_from_content') as mock_extract:
                mock_extract.return_value = {
                    'entities_by_type': {
                        'PRODUCT': [{'text': 'content marketing', 'authority_score': 0.8, 'frequency': 5}]
                    },
                    'total_entities': 1
                }
                
                result = await service.analyze_entities_for_topic("content marketing", "user123")
        
        assert result['topic'] == "content marketing"
        assert 'entities_by_category' in result
        assert 'must_have_entities' in result
        assert 'authority_analysis' in result
    
    def test_calculate_entity_authority_score(self, service):
        """Test entity authority scoring"""
        score = service._calculate_entity_authority_score(
            frequency=10, source_count=5, salience=0.8
        )
        assert 0 <= score <= 1
        assert isinstance(score, float)
    
    def test_determine_relationship_type(self, service):
        """Test relationship type determination"""
        entity1 = {'category': 'People'}
        entity2 = {'category': 'Organizations'}
        
        rel_type = service._determine_relationship_type(entity1, entity2)
        assert rel_type in ['works_for', 'related_to']
    
    def test_validate_input(self, service):
        """Test input validation"""
        # Valid input
        is_valid, error = service.validate_input("machine learning")
        assert is_valid == True
        assert error is None
        
        # Invalid - empty topic
        is_valid, error = service.validate_input("")
        assert is_valid == False
        assert "required" in error
        
        # Invalid - too long
        is_valid, error = service.validate_input("a" * 201)
        assert is_valid == False
        assert "200 characters" in error
        
        # Invalid URLs
        is_valid, error = service.validate_input("test", ["not-a-url"])
        assert is_valid == False
        assert "Invalid URL" in error
```

### **Integration Tests**
```python
"""
tests/integration/test_entity_planner_integration.py
"""

@pytest.mark.integration
class TestEntityPlannerIntegration:
    
    @pytest.mark.asyncio
    async def test_real_entity_extraction(self, real_service):
        """Test with real NLP models"""
        content_data = {
            'all_content': [{
                'text': 'Apple Inc. is a technology company founded by Steve Jobs in California.',
                'url': 'example.com',
                'title': 'Test'
            }],
            'metadata': {'successful_scrapes': 1, 'sources_processed': 1}
        }
        
        result = await real_service._extract_entities_from_content(content_data)
        
        assert result['total_entities'] > 0
        assert any('apple' in str(entity).lower() for entities in result['entities_by_type'].values() for entity in entities)
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_integration(self, real_service):
        """Test Knowledge Graph API integration"""
        if not os.getenv('GOOGLE_API_KEY'):
            pytest.skip("Google API key not provided")
        
        kg_data = await real_service._get_knowledge_graph_data("Apple Inc")
        
        if kg_data:  # API might return None for some queries
            assert 'description' in kg_data
            assert isinstance(kg_data['description'], str)
```

---

## 📈 Success Metrics

### **Technical Performance Metrics**
- **Response Time**: <45 seconds for 95% of requests
- **Entity Extraction Accuracy**: >90% precision in entity relevance
- **Relationship Mapping**: >85% accuracy in entity relationships
- **Cache Hit Rate**: >70% for repeat topic analyses
- **Content Processing**: Handle 20+ competitor URLs simultaneously

### **Business Success Metrics**
- **Content Quality Improvement**: +50% comprehensive coverage
- **User Engagement**: +45% time spent with entity planner
- **Content Performance**: +35% improvement in search rankings
- **Feature Adoption**: >70% of users use entity planner within first month

### **Quality Metrics**
- **Entity Relevance**: >90% of entities rated as relevant by users
- **Authority Scoring**: >85% accuracy in identifying must-have entities
- **Relationship Quality**: >80% of mapped relationships confirmed as meaningful
- **Content Gap Detection**: >90% of identified gaps confirmed as valuable

---

**Document Status**: Final Technical Specification  
**Dependencies**: Feature 1 (Query Finder) completion recommended but not required  
**Estimated Development Time**: 100 hours (2.5 weeks with 2 developers)  
**Next Phase**: Ready for development after technical debt resolution

This specification provides complete implementation guidance for the Entity-Based Content Planner, including advanced NLP processing, knowledge graph integration, relationship mapping, and comprehensive testing strategies.