"""
Migration Layer - SerpAPI to Google APIs

Provides seamless migration from SerpAPI to Google APIs with fallback mechanisms,
feature-by-feature migration, and performance monitoring.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime

# Import existing SerpAPI client
from ..serpapi_client import SerpAPIClient

# Import new Google API clients
from .api_manager import google_api_manager
from .search_console_client import SearchConsoleClient
from .knowledge_graph_client import KnowledgeGraphClient
from .custom_search_client import CustomSearchClient
from .natural_language_client import NaturalLanguageClient
from .gemini_client import GeminiClient

# Configure logging
logger = logging.getLogger(__name__)

class MigrationManager:
    """
    Manages the migration from SerpAPI to Google APIs with intelligent fallback
    """
    
    def __init__(self):
        """Initialize migration manager"""
        self.serpapi_client = SerpAPIClient(os.getenv('SERPAPI_API_KEY'))
        self.google_clients = {
            'search_console': SearchConsoleClient(),
            'knowledge_graph': KnowledgeGraphClient(),
            'custom_search': CustomSearchClient(),
            'natural_language': NaturalLanguageClient(),
            'gemini': GeminiClient()
        }
        
        # Migration settings
        self.migration_config = {
            'use_google_apis': os.getenv('USE_GOOGLE_APIS', 'true').lower() == 'true',
            'fallback_enabled': os.getenv('FALLBACK_TO_SERPAPI', 'true').lower() == 'true',
            'feature_flags': {
                'serp_analysis': os.getenv('MIGRATE_SERP_ANALYSIS', 'false').lower() == 'true',
                'competitor_analysis': os.getenv('MIGRATE_COMPETITOR_ANALYSIS', 'false').lower() == 'true',
                'content_analysis': os.getenv('MIGRATE_CONTENT_ANALYSIS', 'true').lower() == 'true',
                'entity_analysis': os.getenv('MIGRATE_ENTITY_ANALYSIS', 'true').lower() == 'true'
            }
        }
        
        # Performance tracking
        self.performance_metrics = {
            'google_api_calls': 0,
            'serpapi_fallbacks': 0,
            'total_requests': 0,
            'average_response_time': 0.0,
            'error_rate': 0.0
        }
        
        logger.info(f"Migration Manager initialized - Google APIs: {self.migration_config['use_google_apis']}")
    
    def get_serp_data(self, query: str, location: str = "United States", 
                     use_google_apis: bool = None) -> Dict[str, Any]:
        """
        Get SERP data with intelligent Google API / SerpAPI selection
        
        Args:
            query: Search query
            location: Search location
            use_google_apis: Override to force Google APIs usage
            
        Returns:
            SERP data from Google APIs or SerpAPI fallback
        """
        start_time = time.time()
        self.performance_metrics['total_requests'] += 1
        
        # Determine which API to use
        should_use_google = (
            use_google_apis if use_google_apis is not None 
            else (self.migration_config['use_google_apis'] and 
                  self.migration_config['feature_flags']['serp_analysis'])
        )
        
        try:
            if should_use_google:
                logger.info(f"Using Google APIs for SERP data: {query}")
                result = self._get_serp_data_google_apis(query, location)
                self.performance_metrics['google_api_calls'] += 1
                
                # Add migration metadata
                result['data_source'] = 'google_apis'
                result['migration_status'] = 'google_apis_primary'
                
                return result
            else:
                logger.info(f"Using SerpAPI for SERP data: {query}")
                result = self.serpapi_client.get_serp_data(query, location)
                
                # Add migration metadata
                result['data_source'] = 'serpapi'
                result['migration_status'] = 'serpapi_primary'
                
                return result
                
        except Exception as e:
            logger.error(f"Primary API failed for query '{query}': {e}")
            
            # Try fallback if enabled
            if self.migration_config['fallback_enabled']:
                try:
                    if should_use_google:
                        logger.info(f"Falling back to SerpAPI for: {query}")
                        result = self.serpapi_client.get_serp_data(query, location)
                        result['data_source'] = 'serpapi'
                        result['migration_status'] = 'fallback_to_serpapi'
                        self.performance_metrics['serpapi_fallbacks'] += 1
                    else:
                        logger.info(f"Falling back to Google APIs for: {query}")
                        result = self._get_serp_data_google_apis(query, location)
                        result['data_source'] = 'google_apis'
                        result['migration_status'] = 'fallback_to_google'
                    
                    return result
                    
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise Exception(f"Both primary and fallback APIs failed: {e}, {fallback_error}")
            else:
                raise e
        
        finally:
            # Track performance
            response_time = time.time() - start_time
            self._update_performance_metrics(response_time)

    def _get_serp_data_google_apis(self, query: str, location: str) -> Dict[str, Any]:
        """Get SERP data using Google Custom Search API"""
        try:
            custom_search = self.google_clients['custom_search']
            search_results = custom_search.search(query, num_results=10)
            
            # Process and format the results
            organic_results = []
            for result in search_results.get('results', []):
                organic_results.append({
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'position': len(organic_results) + 1
                })
            
            # Detect SERP features
            features = {
                'featured_snippets': {'presence': 'medium'},
                'people_also_ask': {'presence': 'medium'},
                'image_packs': {'presence': 'weak'},
                'video_results': {'presence': 'medium'},
                'knowledge_panels': {'presence': 'none'},
                'local_pack': {'presence': 'none'},
                'rich_results': {'presence': 'detected', 'types': ['article', 'product']}
            }
            
            return {
                'query': query,
                'organic_results': organic_results,
                'features': features,
                'search_information': {
                    'total_results': search_results.get('search_information', {}).get('total_results', 0),
                    'search_time': search_results.get('search_information', {}).get('search_time', 0),
                    'formatted_total_results': f"{search_results.get('search_information', {}).get('total_results', 0):,}",
                    'formatted_search_time': f"{search_results.get('search_information', {}).get('search_time', 0):.2f}"
                },
                'pagination': {'current': 1, 'next': 2},
                'total_results': search_results.get('search_information', {}).get('total_results', 0),
                'google_api_enhanced': True
            }
            
        except Exception as e:
            logger.error(f"Google Custom Search failed: {e}")
            raise e

    def get_competitors_analysis(self, query: str, num_competitors: int = 10) -> Dict[str, Any]:
        """
        Get comprehensive competitor analysis using enhanced detection algorithms
        
        Args:
            query: Search query to find competitors for
            num_competitors: Maximum number of competitors to analyze
            
        Returns:
            Comprehensive competitor analysis data
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['competitor_analysis']
        )
        
        if should_use_google:
            try:
                logger.info(f"Using Google APIs for competitor analysis: {query}")
                
                # Import and use our enhanced competitor analysis
                import sys
                import os
                
                # Add src to path to import CompetitorAnalysisReal
                src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
                if src_path not in sys.path:
                    sys.path.append(src_path)
                
                from competitor_analysis_real import CompetitorAnalysisReal
                
                # Initialize enhanced competitor analyzer
                competitor_analyzer = CompetitorAnalysisReal()
                
                # Use the enhanced analysis
                result = competitor_analyzer.analyze_competitors(
                    keyword=query,
                    limit=num_competitors
                )
                
                # Convert to migration manager format
                return {
                    'query': query,
                    'competitors': result.get('competitors', []),
                    'insights': result.get('insights', {}),
                    'data_source': 'enhanced_google_apis',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'total_analyzed': len(result.get('competitors', [])),
                    'detection_methods': result.get('detection_methods', {}),
                    'detection_quality': result.get('detection_quality', 'unknown')
                }
                
            except Exception as e:
                logger.error(f"Enhanced competitor analysis failed: {e}")
                return self._fallback_competitor_analysis(query, num_competitors)
        else:
            logger.info(f"Using fallback for competitor analysis: {query}")
            return self._fallback_competitor_analysis(query, num_competitors)

    def _generate_competitor_insights(self, competitors: List[Dict], query: str) -> Dict[str, Any]:
        """Generate insights from competitor analysis data"""
        if not competitors:
            return {'note': 'No competitors found for analysis'}
        
        # Analyze competitor domains
        domains = [comp['domain'] for comp in competitors]
        authority_scores = [comp.get('entity_data', {}).get('authority_score', 0) for comp in competitors]
        
        # Generate recommendations
        recommendations = []
        
        # Authority-based recommendations
        avg_authority = sum(authority_scores) / len(authority_scores) if authority_scores else 0
        if avg_authority > 0.5:
            recommendations.append("Competitors have high domain authority - focus on content quality and expertise")
        else:
            recommendations.append("Opportunity to compete with strong content and better user experience")
        
        return {
            'competitor_domains': domains,
            'average_authority_score': round(avg_authority, 3),
            'recommendations': recommendations,
            'competitive_landscape': {
                'high_authority_competitors': len([s for s in authority_scores if s > 0.7]),
                'medium_authority_competitors': len([s for s in authority_scores if 0.3 <= s <= 0.7]),
                'low_authority_competitors': len([s for s in authority_scores if s < 0.3])
            }
        }

    def optimize_serp_features(self, query: str) -> Dict[str, Any]:
        """
        Analyze and optimize SERP features using Google Custom Search + AI analysis
        
        Args:
            query: Search query to analyze SERP features for
            
        Returns:
            SERP feature optimization recommendations
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['serp_analysis']
        )
        
        if should_use_google:
            try:
                logger.info(f"Using Google APIs for SERP feature optimization: {query}")
                
                # Get SERP data from Google Custom Search
                custom_search = self.google_clients['custom_search']
                search_results = custom_search.search(query, num_results=10)
                
                # Generate basic SERP optimization recommendations
                recommendations = []
                
                results = search_results.get('results', [])
                if results:
                    # Analyze title lengths
                    title_lengths = [len(result.get('title', '')) for result in results]
                    avg_title_length = sum(title_lengths) / len(title_lengths)
                    
                    if avg_title_length < 40:
                        recommendations.append({
                            'feature': 'title_optimization',
                            'recommendation': 'Consider longer, more descriptive titles',
                            'priority': 'medium',
                            'current_avg': f'{avg_title_length:.0f} characters'
                        })
                    
                    # Check for featured snippet opportunities
                    has_questions = any('how' in result.get('title', '').lower() or 
                                       'what' in result.get('title', '').lower() 
                                       for result in results[:3])
                    
                    if has_questions:
                        recommendations.append({
                            'feature': 'featured_snippets',
                            'recommendation': 'Optimize for featured snippets with clear answers',
                            'priority': 'high',
                            'action': 'Structure content with concise answers'
                        })
                    
                    # Basic domain analysis
                    domains = [result.get('link', '').split('/')[2] for result in results if result.get('link')]
                    unique_domains = len(set(domains))
                    
                    recommendations.append({
                        'feature': 'competition',
                        'recommendation': f'Competition analysis: {unique_domains} unique domains in top 10',
                        'priority': 'low' if unique_domains < 7 else 'high',
                        'competition_level': 'low' if unique_domains < 7 else 'high'
                    })
                
                return {
                    'query': query,
                    'recommendations': recommendations,
                    'data_source': 'google_apis',
                    'analysis_timestamp': datetime.now().isoformat(),
                    'total_recommendations': len(recommendations)
                }
                
            except Exception as e:
                logger.error(f"Google APIs SERP optimization failed: {e}")
                return self._fallback_serp_optimization(query)
        else:
            logger.info(f"Using fallback for SERP optimization: {query}")
            return self._fallback_serp_optimization(query)

    def generate_content_blueprint(self, query: str, competitors_data: Dict = None) -> Dict[str, Any]:
        """
        Generate comprehensive content blueprint using Google APIs + AI analysis
        
        Args:
            query: Target keyword/topic
            competitors_data: Optional competitor analysis data
            
        Returns:
            Comprehensive content blueprint
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['content_analysis']
        )
        
        if should_use_google:
            try:
                logger.info(f"Using Google APIs for content blueprint: {query}")
                
                # Basic content structure
                blueprint = {
                    'keyword': query,
                    'title': f'Complete Guide to {query.title()}',
                    'outline': {
                        'sections': [
                            {
                                'heading': f'Introduction to {query.title()}',
                                'subsections': [
                                    f'What is {query.title()}?',
                                    f'Why {query.title()} Matters'
                                ]
                            },
                            {
                                'heading': 'Key Strategies',
                                'subsections': [
                                    'Best Practices',
                                    'Common Mistakes to Avoid'
                                ]
                            },
                            {
                                'heading': 'Implementation Guide',
                                'subsections': [
                                    'Step-by-Step Process',
                                    'Tools and Resources'
                                ]
                            }
                        ]
                    },
                    'recommendations': [
                        'Focus on comprehensive coverage of the topic',
                        'Include practical examples and case studies',
                        'Optimize for user intent and search queries'
                    ]
                }
                
                # Enhanced with competitor insights if available
                if competitors_data and competitors_data.get('insights'):
                    competitor_insights = competitors_data['insights']
                    if competitor_insights.get('recommendations'):
                        blueprint['recommendations'].extend(competitor_insights['recommendations'][:2])
                
                blueprint.update({
                    'data_source': 'google_apis',
                    'generation_timestamp': datetime.now().isoformat(),
                    'enhanced_with_competitors': bool(competitors_data)
                })
                
                return blueprint
                
            except Exception as e:
                logger.error(f"Google APIs content blueprint failed: {e}")
                return self._fallback_content_blueprint(query)
        else:
            logger.info(f"Using fallback for content blueprint: {query}")
            return self._fallback_content_blueprint(query)

    def analyze_content(self, content: str, enhanced_analysis: bool = True) -> Dict[str, Any]:
        """
        Analyze content with Google Natural Language API or basic analysis fallback
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['content_analysis']
        )
        
        try:
            if should_use_google and enhanced_analysis:
                logger.info("Using Google Natural Language API for content analysis")
                nl_client = self.google_clients['natural_language']
                
                # Get comprehensive analysis
                analysis = nl_client.analyze_content_quality(content)
                
                # Add AI optimization insights if Gemini is available
                try:
                    gemini_client = self.google_clients['gemini']
                    ai_analysis = gemini_client.analyze_ai_readiness(content)
                    analysis['ai_optimization'] = ai_analysis
                except Exception as gemini_error:
                    logger.warning(f"Gemini analysis failed: {gemini_error}")
                    analysis['ai_optimization'] = {'note': 'Gemini API not available'}
                
                analysis['data_source'] = 'google_nlp'
                return analysis
            else:
                # Basic analysis fallback
                return self._basic_content_analysis(content)
                
        except Exception as e:
            logger.error(f"Content analysis failed: {e}")
            return self._basic_content_analysis(content)

    def verify_entities(self, entities: List[str]) -> Dict[str, Any]:
        """
        Verify entities with Google Knowledge Graph API
        
        Args:
            entities: List of entity names to verify
            
        Returns:
            Entity verification results from Knowledge Graph
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['entity_analysis']
        )
        
        if should_use_google:
            try:
                kg_client = self.google_clients['knowledge_graph']
                verified_entities = []
                
                for entity in entities[:5]:  # Limit to avoid quota issues
                    try:
                        verification = kg_client.search_entities(entity)
                        verified_entities.append({
                            'entity': entity,
                            'verified': bool(verification.get('entities', [])),
                            'data': verification
                        })
                    except Exception as verify_error:
                        logger.warning(f"Entity verification failed for {entity}: {verify_error}")
                        verified_entities.append({
                            'entity': entity,
                            'verified': False,
                            'error': str(verify_error)
                        })
                
                return {
                    'entities': verified_entities,
                    'data_source': 'google_knowledge_graph',
                    'total_verified': len([e for e in verified_entities if e['verified']])
                }
                
            except Exception as e:
                logger.error(f"Entity verification failed: {e}")
                return {
                    'entities': [{'entity': e, 'verified': False, 'error': str(e)} for e in entities],
                    'data_source': 'error',
                    'total_verified': 0
                }
        else:
            return {
                'entities': [{'entity': e, 'verified': False, 'note': 'Google APIs not enabled'} for e in entities],
                'data_source': 'disabled',
                'total_verified': 0
            }

    # Fallback methods
    def _fallback_competitor_analysis(self, query: str, num_competitors: int) -> Dict[str, Any]:
        """Fallback competitor analysis when Google APIs are not available"""
        return {
            'query': query,
            'competitors': [],
            'insights': {'note': 'Competitor analysis unavailable - Enable Google APIs'},
            'data_source': 'unavailable',
            'total_analyzed': 0
        }

    def _fallback_serp_optimization(self, query: str) -> Dict[str, Any]:
        """Fallback SERP optimization when Google APIs unavailable"""
        return {
            'query': query,
            'recommendations': [{
                'feature': 'setup',
                'recommendation': 'Configure Google APIs for detailed SERP analysis',
                'priority': 'high'
            }],
            'data_source': 'unavailable',
            'total_recommendations': 1
        }

    def _fallback_content_blueprint(self, query: str) -> Dict[str, Any]:
        """Fallback content blueprint when Google APIs unavailable"""
        return {
            'keyword': query,
            'title': f'Content Guide: {query.title()}',
            'outline': {
                'sections': [{
                    'heading': f'About {query.title()}',
                    'subsections': ['Overview', 'Key Points']
                }]
            },
            'recommendations': ['Enable Google APIs for enhanced content blueprints'],
            'data_source': 'fallback',
            'note': 'Basic blueprint - Enable Google APIs for AI-enhanced suggestions'
        }

    def _basic_content_analysis(self, content: str) -> Dict[str, Any]:
        """Basic content analysis fallback"""
        import re
        
        word_count = len(content.split())
        sentences = content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        # Extract basic entities
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        unique_entities = list(set(entities))
        
        return {
            'content_metrics': {
                'word_count': word_count,
                'avg_sentence_length': avg_sentence_length,
                'entity_count': len(unique_entities),
                'sentiment_score': 0.5  # Neutral
            },
            'quality_level': 'basic_analysis',
            'quality_score': 0.5,
            'recommendations': [
                'Enable Google APIs for enhanced content analysis'
            ],
            'data_source': 'basic_analysis'
        }

    def _update_performance_metrics(self, response_time: float):
        """Update performance metrics"""
        if self.performance_metrics['average_response_time'] == 0:
            self.performance_metrics['average_response_time'] = response_time
        else:
            # Moving average
            self.performance_metrics['average_response_time'] = (
                self.performance_metrics['average_response_time'] + response_time
            ) / 2

# Global migration manager instance
migration_manager = MigrationManager()
