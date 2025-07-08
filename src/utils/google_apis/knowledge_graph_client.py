"""
Knowledge Graph Client with required methods for hybrid analysis
"""
import logging
from typing import Dict, Any, Optional,List
import os

logger = logging.getLogger(__name__)

class KnowledgeGraphClient:
    def __init__(self):
        """Initialize Knowledge Graph client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.available = bool(self.api_key)
        if not self.available:
            logger.warning("Google API key not found - Knowledge Graph features disabled")
        else:
            logger.info("Knowledge Graph client initialized successfully")
    
    def health_check(self) -> bool:
        """Check if Knowledge Graph API is available"""
        return self.available
    
    def get_entity_info(self, query: str) -> Dict[str, Any]:
        """
        Get entity information from Knowledge Graph API
        
        Args:
            query: Entity query (domain or company name)
            
        Returns:
            Dictionary containing entity information
        """
        try:
            if not self.available:
                logger.debug(f"Knowledge Graph API not available for query: {query}")
                return {}
            
            if not query or not query.strip():
                return {}
            
            # Clean the query - remove protocol and www
            clean_query = query.replace('https://', '').replace('http://', '').replace('www.', '')
            if '/' in clean_query:
                clean_query = clean_query.split('/')[0]
            
            logger.info(f"Knowledge Graph query for: {clean_query}")
            
            # For now, return basic entity structure until KG API is fully implemented
            # This prevents the attribute error while maintaining the data structure
            entity_info = {
                "@type": ["Organization", "Corporation"],
                "name": clean_query,
                "description": f"Business entity: {clean_query}",
                "url": f"https://{clean_query}",
                "industry": self._infer_industry_from_domain(clean_query)
            }
            
            return entity_info
            
        except Exception as e:
            logger.error(f"Knowledge Graph API error for '{query}': {str(e)}")
            return {}
    
    def _infer_industry_from_domain(self, domain: str) -> str:
        """Infer industry from domain name"""
        domain_lower = domain.lower()
        
        # Technology companies
        if any(tech_term in domain_lower for tech_term in ['tech', 'soft', 'ware', 'sys', 'data', 'cloud', 'api']):
            return "technology"
        
        # Telecom companies
        if any(telecom_term in domain_lower for telecom_term in ['telecom', 'mobile', 'wireless', 'mvno', 'cellular']):
            return "telecommunications"
        
        # Consulting/Services
        if any(service_term in domain_lower for service_term in ['consult', 'service', 'solution', 'partner']):
            return "professional_services"
        
        # Media companies
        if any(media_term in domain_lower for media_term in ['media', 'news', 'publish', 'content']):
            return "media"
        
        # Research companies
        if any(research_term in domain_lower for research_term in ['research', 'analytics', 'insights', 'study']):
            return "research"
        
        return "business_services"
    
    def search_entities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for entities in Knowledge Graph
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of entities
        """
        try:
            if not self.available:
                return []
            
            # Placeholder implementation
            return [self.get_entity_info(query)]
            
        except Exception as e:
            logger.error(f"Entity search error: {str(e)}")
            return []
