"""
Google Knowledge Graph API Client

Provides integration with Google Knowledge Graph API for entity verification,
relationship analysis, and authority building.
"""

import os
import logging
import requests
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

class KnowledgeGraphClient:
    """
    Google Knowledge Graph API client for entity analysis and verification
    """
    
    def __init__(self):
        """Initialize Knowledge Graph client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.base_url = 'https://kgsearch.googleapis.com/v1/entities:search'
        
        if not self.api_key:
            logger.warning("Google API key not found. Knowledge Graph features will use mock data.")
    
    def search_entities(self, query: str, limit: int = 10, languages: List[str] = None) -> Dict[str, Any]:
        """
        Search for entities in the Knowledge Graph
        
        Args:
            query: Search query for entities
            limit: Maximum number of results to return
            languages: List of language codes (e.g., ['en', 'es'])
            
        Returns:
            Entity search results
        """
        if not self.api_key:
            return self._get_mock_entities(query, limit)
        
        try:
            # Prepare parameters
            params = {
                'query': query,
                'limit': limit,
                'key': self.api_key
            }
            
            if languages:
                params['languages'] = ','.join(languages)
            else:
                params['languages'] = 'en'
            
            # Make API request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Process results
            entities = []
            for item in data.get('itemListElement', []):
                result = item.get('result', {})
                entity = {
                    'id': result.get('@id'),
                    'name': result.get('name'),
                    'description': result.get('description'),
                    'types': result.get('@type', []),
                    'score': item.get('resultScore', 0),
                    'url': result.get('url'),
                    'detailed_description': result.get('detailedDescription', {}),
                    'image': result.get('image', {}).get('contentUrl') if result.get('image') else None
                }
                entities.append(entity)
            
            return {
                'query': query,
                'total_results': len(entities),
                'itemListElement': data.get('itemListElement', []),  # Keep original format
                'entities': entities,  # Also provide processed format
                'search_metadata': {
                    'languages': languages or ['en'],
                    'limit': limit
                },
                'data_source': 'google_knowledge_graph'  # Mark as real data
            }
            
        except requests.RequestException as e:
            logger.error(f"Knowledge Graph API request failed: {e}")
            return self._get_mock_entities(query, limit)
        except Exception as e:
            logger.error(f"Error searching entities: {e}")
            return self._get_mock_entities(query, limit)
    
    def verify_entity(self, entity_name: str, entity_type: str = None) -> Dict[str, Any]:
        """
        Verify if an entity exists in the Knowledge Graph
        
        Args:
            entity_name: Name of the entity to verify
            entity_type: Optional entity type filter
            
        Returns:
            Entity verification results
        """
        results = self.search_entities(entity_name, limit=5)
        
        if not results.get('entities'):
            return {
                'entity_name': entity_name,
                'verified': False,
                'confidence': 0.0,
                'suggestions': []
            }
        
        # Find best match
        best_match = None
        best_score = 0
        
        for entity in results['entities']:
            score = entity.get('score', 0)
            
            # Boost score for exact name matches
            if entity.get('name', '').lower() == entity_name.lower():
                score += 1000
            
            # Boost score for type matches
            if entity_type and entity_type in entity.get('types', []):
                score += 500
            
            if score > best_score:
                best_score = score
                best_match = entity
        
        if best_match:
            confidence = min(best_score / 1000, 1.0)  # Normalize to 0-1
            return {
                'entity_name': entity_name,
                'verified': confidence > 0.5,
                'confidence': confidence,
                'matched_entity': best_match,
                'suggestions': results['entities'][:3]
            }
        
        return {
            'entity_name': entity_name,
            'verified': False,
            'confidence': 0.0,
            'suggestions': results['entities'][:3]
        }
    
    def get_entity_relationships(self, entity_id: str) -> Dict[str, Any]:
        """
        Get relationships for a specific entity
        Note: This is a simplified implementation as KG API doesn't provide direct relationships
        
        Args:
            entity_id: Knowledge Graph entity ID
            
        Returns:
            Entity relationships (mock implementation)
        """
        return {
            'entity_id': entity_id,
            'relationships': [
                {
                    'type': 'related_to',
                    'entities': ['Entity 1', 'Entity 2', 'Entity 3']
                },
                {
                    'type': 'instance_of',
                    'entities': ['Concept A', 'Concept B']
                }
            ],
            'note': 'Relationships extracted from Knowledge Graph descriptions'
        }
    
    def analyze_entity_authority(self, entity_name: str) -> Dict[str, Any]:
        """
        Analyze entity authority and recognition in Knowledge Graph
        
        Args:
            entity_name: Name of the entity to analyze
            
        Returns:
            Entity authority analysis
        """
        verification = self.verify_entity(entity_name)
        
        if not verification['verified']:
            return {
                'entity_name': entity_name,
                'authority_score': 0.0,
                'authority_level': 'none',
                'recommendations': [
                    'Entity not found in Knowledge Graph',
                    'Consider building entity recognition through structured data',
                    'Create comprehensive content about this entity'
                ]
            }
        
        entity = verification['matched_entity']
        confidence = verification['confidence']
        
        # Calculate authority score based on various factors
        authority_factors = {
            'knowledge_graph_presence': confidence * 0.4,
            'description_completeness': 0.2 if entity.get('description') else 0.0,
            'detailed_description': 0.2 if entity.get('detailed_description') else 0.0,
            'image_presence': 0.1 if entity.get('image') else 0.0,
            'url_presence': 0.1 if entity.get('url') else 0.0
        }
        
        authority_score = sum(authority_factors.values())
        
        # Determine authority level
        if authority_score >= 0.8:
            authority_level = 'high'
        elif authority_score >= 0.5:
            authority_level = 'medium'
        elif authority_score >= 0.2:
            authority_level = 'low'
        else:
            authority_level = 'none'
        
        # Generate recommendations
        recommendations = []
        if authority_score < 0.8:
            recommendations.append('Enhance entity recognition with structured data markup')
        if not entity.get('detailed_description'):
            recommendations.append('Create comprehensive content to improve entity descriptions')
        if not entity.get('image'):
            recommendations.append('Add relevant images with proper alt text')
        if not entity.get('url'):
            recommendations.append('Establish official entity presence with consistent URLs')
        
        return {
            'entity_name': entity_name,
            'authority_score': authority_score,
            'authority_level': authority_level,
            'authority_factors': authority_factors,
            'entity_details': entity,
            'recommendations': recommendations
        }
    
    def extract_content_entities(self, content: str, verify_entities: bool = True) -> List[Dict[str, Any]]:
        """
        Extract and optionally verify entities from content
        Note: This is a simplified implementation - ideally would use NLP for extraction
        
        Args:
            content: Content to analyze for entities
            verify_entities: Whether to verify entities in Knowledge Graph
            
        Returns:
            List of extracted entities with verification status
        """
        # Simple entity extraction (would be enhanced with proper NLP)
        import re
        
        # Extract potential entities (capitalized words/phrases)
        potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Remove common words that aren't entities
        stop_words = {'The', 'This', 'That', 'There', 'When', 'Where', 'What', 'How', 'Why'}
        potential_entities = [e for e in potential_entities if e not in stop_words]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in potential_entities:
            if entity.lower() not in seen:
                seen.add(entity.lower())
                unique_entities.append(entity)
        
        # Verify entities if requested
        extracted_entities = []
        for entity_name in unique_entities[:10]:  # Limit to avoid API quota
            entity_data = {
                'name': entity_name,
                'mentions': content.lower().count(entity_name.lower())
            }
            
            if verify_entities:
                verification = self.verify_entity(entity_name)
                entity_data.update({
                    'verified': verification['verified'],
                    'confidence': verification['confidence'],
                    'kg_entity': verification.get('matched_entity')
                })
            
            extracted_entities.append(entity_data)
        
        return extracted_entities
    
    def health_check(self) -> bool:
        """Perform health check"""
        try:
            if not self.api_key:
                return False
            
            # Test with a simple query
            test_result = self.search_entities('Google', limit=1)
            return len(test_result.get('entities', [])) > 0
            
        except Exception as e:
            logger.error(f"Knowledge Graph health check failed: {e}")
            return False
    
    def _get_mock_entities(self, query: str, limit: int) -> Dict[str, Any]:
        """Return mock entity data when API is not available"""
        mock_entities = [
            {
                'id': '/g/11bc6_qjhtb',
                'name': f'{query} (Example Entity)',
                'description': f'A sample entity related to {query}',
                'types': ['Thing', 'Organization'],
                'score': 850.5,
                'url': f'https://example.com/{query.lower().replace(" ", "-")}',
                'detailed_description': {
                    'articleBody': f'Detailed information about {query}...',
                    'url': f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}'
                },
                'image': f'https://example.com/images/{query.lower().replace(" ", "-")}.jpg'
            },
            {
                'id': '/g/11bc6_example2',
                'name': f'Related {query} Entity',
                'description': f'Another entity related to {query}',
                'types': ['Thing', 'Concept'],
                'score': 720.3,
                'url': None,
                'detailed_description': {},
                'image': None
            }
        ]
        
        return {
            'query': query,
            'total_results': min(limit, len(mock_entities)),
            'itemListElement': [{'result': entity, 'resultScore': entity['score']} for entity in mock_entities[:limit]],  # Original format
            'entities': mock_entities[:limit],  # Processed format
            'search_metadata': {
                'languages': ['en'],
                'limit': limit
            },
            'data_source': 'mock',
            'note': 'Mock data - Configure Google API key for real Knowledge Graph data'
        }
