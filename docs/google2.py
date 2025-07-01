# Google APIs Integration - Complete Implementation
# Replace SerpAPI with Google's native APIs for AI-era SEO

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import language_v1
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSearchConsoleClient:
    """Google Search Console API client for performance data and indexing status."""
    
    def __init__(self, credentials_path: str, site_url: str):
        self.site_url = site_url
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/webmasters.readonly']
        )
        self.service = build('searchconsole', 'v1', credentials=self.credentials)
    
    def get_search_performance(self, query: str, days: int = 30) -> Dict[str, Any]:
        """Get search performance data for specific queries."""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            request = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['query', 'page'],
                'dimensionFilterGroups': [{
                    'filters': [{
                        'dimension': 'query',
                        'operator': 'contains',
                        'expression': query
                    }]
                }],
                'rowLimit': 100
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url, body=request
            ).execute()
            
            return {
                'performance_data': response.get('rows', []),
                'total_clicks': sum(row.get('clicks', 0) for row in response.get('rows', [])),
                'total_impressions': sum(row.get('impressions', 0) for row in response.get('rows', [])),
                'average_ctr': sum(row.get('ctr', 0) for row in response.get('rows', [])) / len(response.get('rows', [])) if response.get('rows') else 0,
                'average_position': sum(row.get('position', 0) for row in response.get('rows', [])) / len(response.get('rows', [])) if response.get('rows') else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting search performance: {str(e)}")
            return {'error': str(e)}
    
    def get_ai_overview_performance(self) -> Dict[str, Any]:
        """Track performance in AI Overviews and rich results."""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            request = {
                'startDate': start_date.isoformat(),
                'endDate': end_date.isoformat(),
                'dimensions': ['searchAppearance'],
                'rowLimit': 100
            }
            
            response = self.service.searchanalytics().query(
                siteUrl=self.site_url, body=request
            ).execute()
            
            ai_features = {}
            for row in response.get('rows', []):
                appearance = row['keys'][0]
                if 'AI' in appearance.upper() or 'RICH' in appearance.upper():
                    ai_features[appearance] = {
                        'clicks': row.get('clicks', 0),
                        'impressions': row.get('impressions', 0),
                        'ctr': row.get('ctr', 0),
                        'position': row.get('position', 0)
                    }
            
            return {'ai_features': ai_features}
            
        except Exception as e:
            logger.error(f"Error getting AI overview performance: {str(e)}")
            return {'error': str(e)}

class GoogleKnowledgeGraphClient:
    """Google Knowledge Graph Search API client for entity verification."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://kgsearch.googleapis.com/v1/entities:search"
    
    def search_entities(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search for entities in Google Knowledge Graph."""
        try:
            params = {
                'query': query,
                'key': self.api_key,
                'limit': limit,
                'indent': True
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            entities = []
            
            for item in data.get('itemListElement', []):
                result = item.get('result', {})
                entities.append({
                    'name': result.get('name', ''),
                    'description': result.get('description', ''),
                    'types': result.get('@type', []),
                    'detailed_description': result.get('detailedDescription', {}).get('articleBody', ''),
                    'url': result.get('url', ''),
                    'score': item.get('resultScore', 0)
                })
            
            return {
                'entities': entities,
                'primary_entity': entities[0] if entities else None,
                'related_entities': entities[1:5] if len(entities) > 1 else []
            }
            
        except Exception as e:
            logger.error(f"Error searching Knowledge Graph: {str(e)}")
            return {'error': str(e)}
    
    def verify_entity(self, entity_name: str) -> Dict[str, Any]:
        """Verify if an entity exists in Google's Knowledge Graph."""
        result = self.search_entities(entity_name, limit=1)
        
        if result.get('entities'):
            entity = result['entities'][0]
            return {
                'verified': True,
                'confidence_score': entity.get('score', 0),
                'entity_data': entity
            }
        
        return {'verified': False, 'confidence_score': 0}

class GoogleNaturalLanguageClient:
    """Google Natural Language API client for content analysis."""
    
    def __init__(self, credentials_path: str):
        self.client = language_v1.LanguageServiceClient.from_service_account_json(credentials_path)
    
    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Comprehensive content analysis using Google NLP."""
        try:
            document = language_v1.Document(
                content=content,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            # Entity analysis
            entities_response = self.client.analyze_entities(
                request={'document': document}
            )
            
            # Sentiment analysis
            sentiment_response = self.client.analyze_sentiment(
                request={'document': document}
            )
            
            # Syntax analysis
            syntax_response = self.client.analyze_syntax(
                request={'document': document}
            )
            
            # Extract entities with confidence scores
            entities = []
            for entity in entities_response.entities:
                entities.append({
                    'name': entity.name,
                    'type': entity.type_.name,
                    'salience': entity.salience,
                    'sentiment_score': entity.sentiment.score if hasattr(entity, 'sentiment') else 0,
                    'mentions': [mention.text.content for mention in entity.mentions]
                })
            
            return {
                'entities': entities,
                'sentiment': {
                    'score': sentiment_response.document_sentiment.score,
                    'magnitude': sentiment_response.document_sentiment.magnitude
                },
                'key_phrases': [token.text.content for token in syntax_response.tokens 
                              if token.part_of_speech.tag.name in ['NOUN', 'ADJ']],
                'readability_score': self._calculate_readability(content),
                'content_structure': self._analyze_structure(content)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score."""
        sentences = content.split('.')
        words = content.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        # Simplified readability calculation
        readability = max(0, min(100, 100 - (avg_sentence_length * 2)))
        return readability
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure for AI optimization."""
        lines = content.split('\n')
        return {
            'has_headings': any(line.startswith('#') for line in lines),
            'has_lists': any(line.strip().startswith(('-', '*', '1.')) for line in lines),
            'paragraph_count': len([line for line in lines if line.strip() and not line.startswith('#')]),
            'word_count': len(content.split()),
            'question_count': content.count('?')
        }

class GoogleCustomSearchClient:
    """Google Custom Search API client for SERP monitoring."""
    
    def __init__(self, api_key: str, search_engine_id: str):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform custom search and analyze results."""
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'display_link': item.get('displayLink', ''),
                    'formatted_url': item.get('formattedUrl', '')
                })
            
            return {
                'results': results,
                'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
                'search_time': data.get('searchInformation', {}).get('searchTime', 0),
                'ai_overview_detected': self._detect_ai_overview(data),
                'featured_snippets': self._extract_featured_snippets(data),
                'knowledge_panel': self._extract_knowledge_panel(data)
            }
            
        except Exception as e:
            logger.error(f"Error performing custom search: {str(e)}")
            return {'error': str(e)}
    
    def _detect_ai_overview(self, search_data: Dict) -> bool:
        """Detect if AI Overview is present in search results."""
        # Check for AI Overview indicators in search results
        for item in search_data.get('items', []):
            if 'ai overview' in item.get('title', '').lower():
                return True
        return False
    
    def _extract_featured_snippets(self, search_data: Dict) -> List[Dict]:
        """Extract featured snippet information."""
        snippets = []
        for item in search_data.get('items', []):
            if item.get('pagemap', {}).get('metatags'):
                snippets.append({
                    'content': item.get('snippet', ''),
                    'source': item.get('displayLink', ''),
                    'url': item.get('link', '')
                })
        return snippets
    
    def _extract_knowledge_panel(self, search_data: Dict) -> Optional[Dict]:
        """Extract knowledge panel information if present."""
        # Knowledge panel data extraction logic
        knowledge_graph = search_data.get('knowledgeGraph', {})
        if knowledge_graph:
            return {
                'title': knowledge_graph.get('title', ''),
                'description': knowledge_graph.get('description', ''),
                'type': knowledge_graph.get('@type', ''),
                'url': knowledge_graph.get('url', '')
            }
        return None

class AIOptimizedContentBlueprint:
    """Enhanced content blueprint generator for AI-era SEO."""
    
    def __init__(self, gemini_api_key: str, knowledge_graph_client: GoogleKnowledgeGraphClient, 
                 nlp_client: GoogleNaturalLanguageClient):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.kg_client = knowledge_graph_client
        self.nlp_client = nlp_client
    
    def generate_ai_optimized_blueprint(self, keyword: str, target_audience: str = "general") -> Dict[str, Any]:
        """Generate content blueprint optimized for AI Overviews and Knowledge Graph."""
        try:
            # Step 1: Entity verification and enhancement
            entity_data = self.kg_client.search_entities(keyword)
            
            # Step 2: Generate AI-optimized content structure
            prompt = f"""
            Create a comprehensive content blueprint for the keyword "{keyword}" that is optimized for:
            1. Google AI Overviews (formerly Bard/SGE)
            2. Featured snippets
            3. Knowledge Graph integration
            4. Entity-based search optimization
            
            Target audience: {target_audience}
            
            Verified entities: {entity_data.get('entities', [])[:3] if entity_data.get('entities') else 'None'}
            
            Provide:
            1. Content structure with H1-H6 headings
            2. Key entities to emphasize
            3. Structured data recommendations
            4. Answer-focused content sections
            5. FAQ section for voice search optimization
            6. Related entity connections
            7. Factual accuracy requirements
            
            Format as JSON with clear sections.
            """
            
            response = self.model.generate_content(prompt)
            ai_blueprint = json.loads(response.text.strip('```json\n').strip('```'))
            
            # Step 3: Entity enhancement recommendations
            entity_enhancements = self._generate_entity_enhancements(entity_data)
            
            # Step 4: Schema markup recommendations
            schema_recommendations = self._generate_schema_recommendations(keyword, entity_data)
            
            # Step 5: AI Overview optimization
            ai_overview_optimization = self._generate_ai_overview_optimization(keyword)
            
            return {
                'blueprint': ai_blueprint,
                'entity_enhancements': entity_enhancements,
                'schema_recommendations': schema_recommendations,
                'ai_overview_optimization': ai_overview_optimization,
                'verified_entities': entity_data.get('entities', []),
                'optimization_score': self._calculate_optimization_score(ai_blueprint, entity_data)
            }
            
        except Exception as e:
            logger.error(f"Error generating AI-optimized blueprint: {str(e)}")
            return {'error': str(e)}
    
    def _generate_entity_enhancements(self, entity_data: Dict) -> List[Dict]:
        """Generate entity enhancement recommendations."""
        enhancements = []
        
        for entity in entity_data.get('entities', [])[:5]:
            enhancements.append({
                'entity': entity.get('name', ''),
                'enhancement_strategy': f"Emphasize {entity.get('name')} as a key entity",
                'context_integration': f"Include {entity.get('description', '')} context",
                'related_entities': entity_data.get('related_entities', []),
                'schema_type': self._determine_schema_type(entity.get('types', []))
            })
        
        return enhancements
    
    def _generate_schema_recommendations(self, keyword: str, entity_data: Dict) -> Dict[str, Any]:
        """Generate structured data recommendations."""
        primary_entity = entity_data.get('primary_entity')
        
        if not primary_entity:
            return {'error': 'No primary entity found'}
        
        schema_type = self._determine_schema_type(primary_entity.get('types', []))
        
        return {
            'primary_schema': schema_type,
            'recommended_properties': self._get_schema_properties(schema_type),
            'entity_markup': {
                'name': primary_entity.get('name', ''),
                'description': primary_entity.get('description', ''),
                'url': primary_entity.get('url', ''),
                'sameAs': [primary_entity.get('url', '')]
            }
        }
    
    def _generate_ai_overview_optimization(self, keyword: str) -> Dict[str, Any]:
        """Generate specific optimizations for AI Overviews."""
        try:
            prompt = f"""
            Provide specific optimization strategies for the keyword "{keyword}" to appear in Google AI Overviews:
            
            1. Content formatting recommendations
            2. Answer structure optimization
            3. Factual accuracy requirements
            4. Citation and source requirements
            5. Entity relationship mapping
            6. Context and comprehensiveness needs
            
            Focus on what AI systems look for when creating summaries.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'ai_overview_strategy': response.text,
                'key_factors': [
                    'Authoritative sources and citations',
                    'Clear, direct answers to questions',
                    'Comprehensive entity coverage',
                    'Factual accuracy and verification',
                    'Structured content hierarchy',
                    'Related topic coverage'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating AI overview optimization: {str(e)}")
            return {'error': str(e)}
    
    def _determine_schema_type(self, entity_types: List[str]) -> str:
        """Determine appropriate schema.org type for entity."""
        schema_mapping = {
            'Person': 'Person',
            'Organization': 'Organization',
            'Place': 'Place',
            'Product': 'Product',
            'Event': 'Event',
            'Article': 'Article',
            'WebPage': 'WebPage'
        }
        
        for entity_type in entity_types:
            if entity_type in schema_mapping:
                return schema_mapping[entity_type]
        
        return 'Thing'  # Default schema type
    
    def _get_schema_properties(self, schema_type: str) -> List[str]:
        """Get recommended properties for schema type."""
        property_mapping = {
            'Person': ['name', 'description', 'url', 'sameAs', 'jobTitle', 'worksFor'],
            'Organization': ['name', 'description', 'url', 'sameAs', 'address', 'telephone'],
            'Place': ['name', 'description', 'address', 'geo', 'telephone'],
            'Product': ['name', 'description', 'brand', 'offers', 'review'],
            'Article': ['headline', 'author', 'datePublished', 'description', 'mainEntityOfPage']
        }
        
        return property_mapping.get(schema_type, ['name', 'description', 'url'])
    
    def _calculate_optimization_score(self, blueprint: Dict, entity_data: Dict) -> float:
        """Calculate optimization score for AI-era SEO."""
        score = 0
        
        # Entity verification score (30%)
        if entity_data.get('entities'):
            score += 30
        
        # Content structure score (25%)
        if blueprint.get('content_structure'):
            score += 25
        
        # Schema recommendations score (25%)
        if blueprint.get('schema_recommendations'):
            score += 25
        
        # AI optimization score (20%)
        if blueprint.get('ai_overview_optimization'):
            score += 20
        
        return min(100, score)

class GoogleAPIsMigrationManager:
    """Manages migration from SerpAPI to Google APIs."""
    
    def __init__(self, google_clients: Dict[str, Any]):
        self.search_console = google_clients.get('search_console')
        self.knowledge_graph = google_clients.get('knowledge_graph')
        self.natural_language = google_clients.get('natural_language')
        self.custom_search = google_clients.get('custom_search')
        self.blueprint_generator = google_clients.get('blueprint_generator')
    
    def replace_serpapi_competitor_analysis(self, keyword: str) -> Dict[str, Any]:
        """Replace SerpAPI competitor analysis with Google APIs."""
        try:
            # Use Custom Search API instead of SerpAPI
            search_results = self.custom_search.search(keyword, num_results=10)
            
            competitors = []
            for result in search_results.get('results', []):
                # Analyze competitor content using NLP API
                if result.get('snippet'):
                    content_analysis = self.natural_language.analyze_content(result['snippet'])
                    
                    competitors.append({
                        'url': result['url'],
                        'title': result['title'],
                        'snippet': result['snippet'],
                        'domain': result['display_link'],
                        'content_analysis': content_analysis,
                        'entities': content_analysis.get('entities', []),
                        'sentiment': content_analysis.get('sentiment', {}),
                        'readability': content_analysis.get('readability_score', 0)
                    })
            
            return {
                'competitors': competitors,
                'total_found': len(competitors),
                'featured_snippets': search_results.get('featured_snippets', []),
                'knowledge_panel': search_results.get('knowledge_panel'),
                'ai_overview_present': search_results.get('ai_overview_detected', False)
            }
            
        except Exception as e:
            logger.error(f"Error in competitor analysis migration: {str(e)}")
            return {'error': str(e)}
    
    def replace_serpapi_keyword_analysis(self, keyword: str) -> Dict[str, Any]:
        """Replace SerpAPI keyword analysis with Google APIs."""
        try:
            # Entity verification using Knowledge Graph
            entity_data = self.knowledge_graph.search_entities(keyword)
            
            # Search performance data from Search Console
            performance_data = {}
            if self.search_console:
                performance_data = self.search_console.get_search_performance(keyword)
            
            # SERP features from Custom Search
            serp_data = self.custom_search.search(keyword, num_results=5)
            
            return {
                'keyword': keyword,
                'entities': entity_data.get('entities', []),
                'primary_entity': entity_data.get('primary_entity'),
                'performance_metrics': performance_data,
                'serp_features': {
                    'featured_snippets': serp_data.get('featured_snippets', []),
                    'knowledge_panel': serp_data.get('knowledge_panel'),
                    'ai_overview': serp_data.get('ai_overview_detected', False)
                },
                'optimization_opportunities': self._identify_optimization_opportunities(entity_data, serp_data)
            }
            
        except Exception as e:
            logger.error(f"Error in keyword analysis migration: {str(e)}")
            return {'error': str(e)}
    
    def _identify_optimization_opportunities(self, entity_data: Dict, serp_data: Dict) -> List[Dict]:
        """Identify optimization opportunities based on Google APIs data."""
        opportunities = []
        
        # Entity-based opportunities
        if entity_data.get('entities'):
            opportunities.append({
                'type': 'entity_optimization',
                'description': 'Optimize content around verified entities',
                'entities': [e.get('name') for e in entity_data['entities'][:3]],
                'priority': 'high'
            })
        
        # Knowledge panel opportunity
        if not serp_data.get('knowledge_panel'):
            opportunities.append({
                'type': 'knowledge_panel',
                'description': 'Opportunity to capture knowledge panel',
                'action': 'Enhance entity markup and authority signals',
                'priority': 'medium'
            })
        
        # AI Overview opportunity
        if not serp_data.get('ai_overview_detected'):
            opportunities.append({
                'type': 'ai_overview',
                'description': 'Opportunity to appear in AI Overview',
                'action': 'Create comprehensive, well-structured content',
                'priority': 'high'
            })
        
        return opportunities

class StructuredDataGenerator:
    """Generate schema markup for AI optimization."""
    
    def __init__(self, knowledge_graph_client: GoogleKnowledgeGraphClient):
        self.kg_client = knowledge_graph_client
    
    def generate_entity_schema(self, entity_name: str, content_type: str = "Article") -> Dict[str, Any]:
        """Generate schema markup for entities."""
        try:
            # Verify entity in Knowledge Graph
            entity_verification = self.kg_client.verify_entity(entity_name)
            
            if not entity_verification.get('verified'):
                logger.warning(f"Entity {entity_name} not verified in Knowledge Graph")
            
            entity_data = entity_verification.get('entity_data', {})
            
            # Base schema structure
            schema = {
                "@context": "https://schema.org",
                "@type": content_type,
                "name": entity_name,
                "description": entity_data.get('description', ''),
                "url": entity_data.get('url', ''),
                "mainEntity": {
                    "@type": self._determine_entity_type(entity_data.get('types', [])),
                    "name": entity_name,
                    "description": entity_data.get('detailed_description', ''),
                    "sameAs": [entity_data.get('url', '')] if entity_data.get('url') else []
                }
            }
            
            # Add specific properties based on entity type
            entity_type = self._determine_entity_type(entity_data.get('types', []))
            schema = self._enhance_schema_by_type(schema, entity_type, entity_data)
            
            return {
                'schema': schema,
                'entity_verified': entity_verification.get('verified', False),
                'confidence_score': entity_verification.get('confidence_score', 0),
                'validation_url': f"https://search.google.com/test/rich-results?url={entity_data.get('url', '')}"
            }
            
        except Exception as e:
            logger.error(f"Error generating entity schema: {str(e)}")
            return {'error': str(e)}
    
    def generate_faq_schema(self, questions_answers: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate FAQ schema for voice search and AI optimization."""
        try:
            faq_items = []
            
            for qa in questions_answers:
                faq_items.append({
                    "@type": "Question",
                    "name": qa.get('question', ''),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": qa.get('answer', '')
                    }
                })
            
            schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_items
            }
            
            return {'schema': schema, 'item_count': len(faq_items)}
            
        except Exception as e:
            logger.error(f"Error generating FAQ schema: {str(e)}")
            return {'error': str(e)}
    
    def generate_article_schema(self, title: str, author: str, content: str, 
                              publish_date: str, entities: List[str]) -> Dict[str, Any]:
        """Generate comprehensive article schema with entity markup."""
        try:
            # Verify main entities
            verified_entities = []
            for entity in entities[:5]:  # Limit to top 5 entities
                verification = self.kg_client.verify_entity(entity)
                if verification.get('verified'):
                    verified_entities.append({
                        "name": entity,
                        "url": verification['entity_data'].get('url', ''),
                        "description": verification['entity_data'].get('description', '')
                    })
            
            schema = {
                "@context": "https://schema.org",
                "@type": "Article",
                "headline": title,
                "author": {
                    "@type": "Person",
                    "name": author
                },
                "datePublished": publish_date,
                "articleBody": content[:500] + "..." if len(content) > 500 else content,
                "mainEntity": verified_entities[0] if verified_entities else None,
                "mentions": [
                    {
                        "@type": "Thing",
                        "name": entity["name"],
                        "url": entity["url"],
                        "description": entity["description"]
                    } for entity in verified_entities
                ]
            }
            
            return {
                'schema': schema,
                'verified_entities': len(verified_entities),
                'total_entities': len(entities)
            }
            
        except Exception as e:
            logger.error(f"Error generating article schema: {str(e)}")
            return {'error': str(e)}
    
    def _determine_entity_type(self, types: List[str]) -> str:
        """Determine schema.org type from Knowledge Graph types."""
        type_mapping = {
            'Person': 'Person',
            'Organization': 'Organization',
            'Place': 'Place',
            'Product': 'Product',
            'Event': 'Event',
            'CreativeWork': 'CreativeWork',
            'WebPage': 'WebPage'
        }
        
        for entity_type in types:
            if entity_type in type_mapping:
                return type_mapping[entity_type]
        
        return 'Thing'
    
    def _enhance_schema_by_type(self, schema: Dict, entity_type: str, entity_data: Dict) -> Dict:
        """Enhance schema with type-specific properties."""
        if entity_type == 'Person':
            if 'mainEntity' in schema:
                schema['mainEntity'].update({
                    "jobTitle": entity_data.get('jobTitle', ''),
                    "worksFor": entity_data.get('worksFor', ''),
                    "knowsAbout": entity_data.get('knowsAbout', [])
                })
        
        elif entity_type == 'Organization':
            if 'mainEntity' in schema:
                schema['mainEntity'].update({
                    "foundingDate": entity_data.get('foundingDate', ''),
                    "founder": entity_data.get('founder', ''),
                    "address": entity_data.get('address', '')
                })
        
        return schema

class AIOverviewPerformanceTracker:
    """Track performance in AI Overviews and rich results."""
    
    def __init__(self, search_console_client: GoogleSearchConsoleClient, 
                 custom_search_client: GoogleCustomSearchClient):
        self.search_console = search_console_client
        self.custom_search = custom_search_client
    
    def track_ai_feature_performance(self, keywords: List[str]) -> Dict[str, Any]:
        """Track performance across AI-powered search features."""
        try:
            results = {
                'ai_overview_appearances': {},
                'featured_snippet_performance': {},
                'knowledge_panel_presence': {},
                'overall_ai_visibility': 0
            }
            
            for keyword in keywords:
                # Search Console data for AI features
                ai_performance = self.search_console.get_ai_overview_performance()
                
                # Custom search for current SERP features
                serp_analysis = self.custom_search.search(keyword)
                
                results['ai_overview_appearances'][keyword] = {
                    'detected': serp_analysis.get('ai_overview_detected', False),
                    'performance_data': ai_performance.get('ai_features', {})
                }
                
                results['featured_snippet_performance'][keyword] = {
                    'snippets_found': len(serp_analysis.get('featured_snippets', [])),
                    'snippet_data': serp_analysis.get('featured_snippets', [])
                }
                
                results['knowledge_panel_presence'][keyword] = {
                    'panel_detected': bool(serp_analysis.get('knowledge_panel')),
                    'panel_data': serp_analysis.get('knowledge_panel')
                }
            
            # Calculate overall AI visibility score
            total_features = len(keywords) * 3  # 3 features per keyword
            detected_features = sum([
                1 for keyword in keywords 
                for feature in ['ai_overview_appearances', 'featured_snippet_performance', 'knowledge_panel_presence']
                if results[feature][keyword].get('detected') or 
                   results[feature][keyword].get('snippets_found', 0) > 0 or
                   results[feature][keyword].get('panel_detected', False)
            ])
            
            results['overall_ai_visibility'] = (detected_features / total_features) * 100 if total_features > 0 else 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error tracking AI feature performance: {str(e)}")
            return {'error': str(e)}
    
    def generate_optimization_report(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization recommendations based on AI feature performance."""
        try:
            recommendations = []
            
            # AI Overview optimization
            ai_appearances = performance_data.get('ai_overview_appearances', {})
            low_ai_keywords = [k for k, v in ai_appearances.items() if not v.get('detected')]
            
            if low_ai_keywords:
                recommendations.append({
                    'type': 'ai_overview_optimization',
                    'priority': 'high',
                    'keywords': low_ai_keywords,
                    'action': 'Optimize content structure for AI Overview inclusion',
                    'specific_tactics': [
                        'Create comprehensive, well-structured content',
                        'Include direct answers to questions',
                        'Enhance entity markup and relationships',
                        'Improve content authority and citations'
                    ]
                })
            
            # Featured snippet optimization
            snippet_performance = performance_data.get('featured_snippet_performance', {})
            low_snippet_keywords = [k for k, v in snippet_performance.items() if v.get('snippets_found', 0) == 0]
            
            if low_snippet_keywords:
                recommendations.append({
                    'type': 'featured_snippet_optimization',
                    'priority': 'medium',
                    'keywords': low_snippet_keywords,
                    'action': 'Optimize content for featured snippet capture',
                    'specific_tactics': [
                        'Create concise, direct answers',
                        'Use proper heading structure',
                        'Include numbered lists and tables',
                        'Answer common questions directly'
                    ]
                })
            
            # Knowledge panel optimization
            panel_presence = performance_data.get('knowledge_panel_presence', {})
            no_panel_keywords = [k for k, v in panel_presence.items() if not v.get('panel_detected')]
            
            if no_panel_keywords:
                recommendations.append({
                    'type': 'knowledge_panel_optimization',
                    'priority': 'medium',
                    'keywords': no_panel_keywords,
                    'action': 'Build entity authority for knowledge panel capture',
                    'specific_tactics': [
                        'Enhance entity schema markup',
                        'Build authoritative backlinks',
                        'Create comprehensive entity-focused content',
                        'Verify entity in Knowledge Graph'
                    ]
                })
            
            return {
                'recommendations': recommendations,
                'overall_score': performance_data.get('overall_ai_visibility', 0),
                'priority_actions': [r for r in recommendations if r['priority'] == 'high'],
                'improvement_potential': 100 - performance_data.get('overall_ai_visibility', 0)
            }
            
        except Exception as e:
            logger.error(f"Error generating optimization report: {str(e)}")
            return {'error': str(e)}

# Integration Example - Complete Setup
def setup_google_apis_integration():
    """Complete setup example for Google APIs integration."""
    
    # Initialize all clients
    search_console_client = GoogleSearchConsoleClient(
        credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        site_url=os.getenv('SEARCH_CONSOLE_SITE_URL')
    )
    
    knowledge_graph_client = GoogleKnowledgeGraphClient(
        api_key=os.getenv('GOOGLE_API_KEY')
    )
    
    natural_language_client = GoogleNaturalLanguageClient(
        credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    )
    
    custom_search_client = GoogleCustomSearchClient(
        api_key=os.getenv('GOOGLE_API_KEY'),
        search_engine_id=os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    )
    
    blueprint_generator = AIOptimizedContentBlueprint(
        gemini_api_key=os.getenv('GOOGLE_GEMINI_API_KEY'),
        knowledge_graph_client=knowledge_graph_client,
        nlp_client=natural_language_client
    )
    
    # Create migration manager
    google_clients = {
        'search_console': search_console_client,
        'knowledge_graph': knowledge_graph_client,
        'natural_language': natural_language_client,
        'custom_search': custom_search_client,
        'blueprint_generator': blueprint_generator
    }
    
    migration_manager = GoogleAPIsMigrationManager(google_clients)
    
    # Create structured data generator
    schema_generator = StructuredDataGenerator(knowledge_graph_client)
    
    # Create performance tracker
    performance_tracker = AIOverviewPerformanceTracker(
        search_console_client, custom_search_client
    )
    
    return {
        'migration_manager': migration_manager,
        'schema_generator': schema_generator,
        'performance_tracker': performance_tracker,
        'blueprint_generator': blueprint_generator
    }

# Usage Example
if __name__ == "__main__":
    # Setup integration
    integration = setup_google_apis_integration()
    
    # Example: Generate AI-optimized content blueprint
    blueprint = integration['blueprint_generator'].generate_ai_optimized_blueprint(
        keyword="artificial intelligence marketing",
        target_audience="digital marketers"
    )
    
    print("AI-Optimized Content Blueprint:")
    print(json.dumps(blueprint, indent=2))
    
    # Example: Replace SerpAPI competitor analysis
    competitor_analysis = integration['migration_manager'].replace_serpapi_competitor_analysis(
        keyword="artificial intelligence marketing"
    )
    
    print("\nCompetitor Analysis (Google APIs):")
    print(json.dumps(competitor_analysis, indent=2))
    
    # Example: Generate schema markup
    schema = integration['schema_generator'].generate_entity_schema(
        entity_name="artificial intelligence",
        content_type="Article"
    )
    
    print("\nSchema Markup:")
    print(json.dumps(schema, indent=2))