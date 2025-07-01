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
    
    def get_competitors(self, query: str, limit: int = 10, exclude_domain: str = None) -> List[Dict[str, Any]]:
        """
        Get competitor analysis with Google APIs or SerpAPI fallback
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['competitor_analysis']
        )
        
        try:
            if should_use_google:
                logger.info(f"Using Google Custom Search for competitors: {query}")
                custom_search = self.google_clients['custom_search']
                return custom_search.get_competitors(query, exclude_domain, limit)
            else:
                logger.info(f"Using SerpAPI for competitors: {query}")
                return self.serpapi_client.get_competitors(query, limit)
                
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            
            # Try fallback
            if self.migration_config['fallback_enabled']:
                try:
                    if should_use_google:
                        return self.serpapi_client.get_competitors(query, limit)
                    else:
                        custom_search = self.google_clients['custom_search']
                        return custom_search.get_competitors(query, exclude_domain, limit)
                except Exception as fallback_error:
                    logger.error(f"Competitor analysis fallback failed: {fallback_error}")
                    return []
            else:
                return []
    
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
    
    def extract_and_verify_entities(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract entities and verify them with Knowledge Graph
        """
        should_use_google = (
            self.migration_config['use_google_apis'] and 
            self.migration_config['feature_flags']['entity_analysis']
        )
        
        if should_use_google:
            try:
                # Extract entities with Natural Language API
                nl_client = self.google_clients['natural_language']
                entities = nl_client.extract_entities(content)
                
                # Verify entities with Knowledge Graph
                kg_client = self.google_clients['knowledge_graph']
                verified_entities = []
                
                for entity in entities[:5]:  # Limit to avoid quota issues
                    try:
                        verification = kg_client.verify_entity(entity['name'], entity['type'])
                        entity.update(verification)
                        verified_entities.append(entity)
                    except Exception as verify_error:
                        logger.warning(f"Entity verification failed for {entity['name']}: {verify_error}")
                        entity['verified'] = False
                        verified_entities.append(entity)
                
                return verified_entities
                
            except Exception as e:
                logger.error(f"Entity analysis failed: {e}")
                return self._basic_entity_extraction(content)
        else:
            return self._basic_entity_extraction(content)
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get comprehensive migration status and performance metrics
        """
        # Health check all Google API clients
        google_api_health = {}
        for api_name, client in self.google_clients.items():
            try:
                if hasattr(client, 'health_check'):
                    google_api_health[api_name] = client.health_check()
                else:
                    google_api_health[api_name] = True  # Assume healthy if no health check
            except Exception as e:
                google_api_health[api_name] = False
                logger.error(f"Health check failed for {api_name}: {e}")
        
        # Calculate success rates
        total_requests = max(self.performance_metrics['total_requests'], 1)
        google_success_rate = (self.performance_metrics['google_api_calls'] / total_requests) * 100
        fallback_rate = (self.performance_metrics['serpapi_fallbacks'] / total_requests) * 100
        
        return {
            'migration_config': self.migration_config,
            'google_api_health': google_api_health,
            'performance_metrics': {
                **self.performance_metrics,
                'google_success_rate': google_success_rate,
                'fallback_rate': fallback_rate
            },
            'recommendations': self._generate_migration_recommendations(google_api_health),
            'next_steps': self._get_next_migration_steps(),
            'cost_analysis': self._estimate_cost_savings()
        }
    
    def enable_feature_migration(self, feature: str, enabled: bool = True) -> Dict[str, Any]:
        """
        Enable or disable migration for specific features
        
        Args:
            feature: Feature name (serp_analysis, competitor_analysis, etc.)
            enabled: Whether to enable Google APIs for this feature
        """
        if feature in self.migration_config['feature_flags']:
            old_value = self.migration_config['feature_flags'][feature]
            self.migration_config['feature_flags'][feature] = enabled
            
            logger.info(f"Feature migration {feature}: {old_value} -> {enabled}")
            
            return {
                'feature': feature,
                'previous_state': old_value,
                'new_state': enabled,
                'migration_config': self.migration_config['feature_flags']
            }
        else:
            raise ValueError(f"Unknown feature: {feature}")
    
    def _get_serp_data_google_apis(self, query: str, location: str) -> Dict[str, Any]:
        """
        Get SERP data using Google APIs (Custom Search + additional analysis)
        """
        custom_search = self.google_clients['custom_search']
        
        # Get basic search results
        search_results = custom_search.search(query, num_results=10)
        
        # Analyze SERP features
        serp_features = custom_search.analyze_serp_features(query)
        
        # Convert to SerpAPI-compatible format
        serp_data = {
            'query': query,
            'organic_results': search_results.get('results', []),
            'features': serp_features.get('features', {}),
            'search_information': search_results.get('search_information', {}),
            'pagination': {'current': 1, 'next': 2},  # Simplified
            'google_api_enhanced': True,
            'total_results': search_results.get('search_information', {}).get('total_results', 0)
        }
        
        return serp_data
    
    def _basic_content_analysis(self, content: str) -> Dict[str, Any]:
        """
        Basic content analysis fallback when Google APIs are not available
        """
        word_count = len(content.split())
        char_count = len(content)
        
        # Simple readability estimation
        sentences = content.count('.') + content.count('!') + content.count('?')
        avg_sentence_length = word_count / max(sentences, 1)
        
        # Basic entity extraction (simplified)
        import re
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        unique_entities = list(set(entities))
        
        return {
            'quality_score': 0.6,  # Default medium quality
            'quality_level': 'fair',
            'content_metrics': {
                'word_count': word_count,
                'char_count': char_count,
                'entity_count': len(unique_entities),
                'avg_sentence_length': avg_sentence_length
            },
            'entities': [{'name': e, 'type': 'UNKNOWN', 'verified': False} for e in unique_entities[:5]],
            'recommendations': [
                'Enable Google Natural Language API for detailed analysis',
                'Consider expanding content if under 300 words',
                'Add more structured headings'
            ],
            'data_source': 'basic_analysis',
            'note': 'Basic analysis - Enable Google APIs for comprehensive insights'
        }
    
    def _basic_entity_extraction(self, content: str) -> List[Dict[str, Any]]:
        """
        Basic entity extraction fallback
        """
        import re
        
        # Extract capitalized words/phrases as potential entities
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        unique_entities = list(set(entities))
        
        return [
            {
                'name': entity,
                'type': 'UNKNOWN',
                'salience': 0.1,
                'verified': False,
                'mentions': [{'text': entity, 'type': 'PROPER'}],
                'note': 'Basic extraction - Enable Google APIs for verification'
            }
            for entity in unique_entities[:10]
        ]
    
    def _update_performance_metrics(self, response_time: float):
        """Update performance metrics"""
        if self.performance_metrics['average_response_time'] == 0:
            self.performance_metrics['average_response_time'] = response_time
        else:
            # Moving average
            self.performance_metrics['average_response_time'] = (
                self.performance_metrics['average_response_time'] + response_time
            ) / 2
    
    def _generate_migration_recommendations(self, health_status: Dict[str, bool]) -> List[str]:
        """Generate migration recommendations based on current status"""
        recommendations = []
        
        # Check Google API health
        unhealthy_apis = [api for api, healthy in health_status.items() if not healthy]
        if unhealthy_apis:
            recommendations.append(f"Fix configuration for: {', '.join(unhealthy_apis)}")
        
        # Check feature migration status
        disabled_features = [
            feature for feature, enabled in self.migration_config['feature_flags'].items() 
            if not enabled
        ]
        if disabled_features:
            recommendations.append(f"Consider enabling migration for: {', '.join(disabled_features)}")
        
        # Performance recommendations
        fallback_rate = self.performance_metrics['serpapi_fallbacks'] / max(self.performance_metrics['total_requests'], 1)
        if fallback_rate > 0.3:
            recommendations.append("High fallback rate detected - check Google API quotas and configuration")
        
        if not recommendations:
            recommendations.append("Migration is performing well - consider enabling more features")
        
        return recommendations
    
    def _get_next_migration_steps(self) -> List[str]:
        """Get suggested next steps for migration"""
        steps = []
        
        # Check current migration status
        if not self.migration_config['feature_flags']['serp_analysis']:
            steps.append("Enable SERP analysis migration (set MIGRATE_SERP_ANALYSIS=true)")
        
        if not self.migration_config['feature_flags']['competitor_analysis']:
            steps.append("Enable competitor analysis migration (set MIGRATE_COMPETITOR_ANALYSIS=true)")
        
        if all(self.migration_config['feature_flags'].values()):
            steps.append("All features migrated - monitor performance and consider disabling SerpAPI")
        
        return steps
    
    def _estimate_cost_savings(self) -> Dict[str, Any]:
        """Estimate cost savings from migration"""
        # Simplified cost estimation
        google_calls = self.performance_metrics['google_api_calls']
        serpapi_calls = self.performance_metrics['total_requests'] - google_calls
        
        # Estimated costs (simplified)
        serpapi_cost_per_call = 0.01  # Estimate
        google_cost_per_call = 0.004  # Estimate (mixed APIs)
        
        current_serpapi_cost = serpapi_calls * serpapi_cost_per_call
        google_cost = google_calls * google_cost_per_call
        
        if self.performance_metrics['total_requests'] > 0:
            projected_monthly_savings = (serpapi_cost_per_call - google_cost_per_call) * self.performance_metrics['total_requests'] * 30
        else:
            projected_monthly_savings = 0
        
        return {
            'current_period': {
                'serpapi_cost': current_serpapi_cost,
                'google_api_cost': google_cost,
                'total_cost': current_serpapi_cost + google_cost
            },
            'projected_monthly_savings': projected_monthly_savings,
            'cost_reduction_percentage': 60,  # Estimated
            'note': 'Cost estimates are approximate - actual savings may vary'
        }

# Global migration manager instance
migration_manager = MigrationManager()
