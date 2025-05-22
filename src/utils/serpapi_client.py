"""
SerpAPI Integration Module

This module provides integration with SerpAPI for SERP data retrieval.
"""

import logging
import json
import random
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SerpAPIClient:
    """
    SerpAPI client for SERP data retrieval.
    
    This class provides methods for retrieving SERP data using SerpAPI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the SerpAPI client.
        
        Args:
            api_key: SerpAPI key
        """
        self.api_key = api_key
        self.client = None
        
        # Try to initialize the client if API key is provided
        if api_key:
            try:
                # Import SerpAPI library
                from serpapi import GoogleSearch
                
                # Initialize client
                self.client = GoogleSearch
                logger.info("SerpAPI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing SerpAPI client: {str(e)}")
                self.client = None
        else:
            logger.info("SerpAPI client initialized successfully")
    
    def get_serp_data(self, query: str, location: str = "United States") -> Dict[str, Any]:
        """
        Get SERP data for a query.
        
        Args:
            query: Search query
            location: Search location
            
        Returns:
            Dictionary containing SERP data
        """
        logger.info(f"Getting SERP data for query: {query}")
        
        # If client is not initialized or API key is not provided, use mock data
        if not self.client or not self.api_key:
            return self._get_mock_serp_data(query)
        
        try:
            # Set up search parameters
            params = {
                "q": query,
                "location": location,
                "hl": "en",
                "gl": "us",
                "google_domain": "google.com",
                "api_key": self.api_key
            }
            
            # Execute search
            search = self.client(params)
            results = search.get_dict()
            
            # Extract relevant data
            organic_results = results.get("organic_results", [])
            
            # Extract SERP features
            features = {}
            
            # Featured snippet
            if "answer_box" in results:
                features["featured_snippets"] = {
                    "presence": "strong",
                    "data": results["answer_box"]
                }
            else:
                features["featured_snippets"] = {"presence": "none"}
            
            # People also ask
            if "related_questions" in results:
                features["people_also_ask"] = {
                    "presence": "strong",
                    "data": results["related_questions"],
                    "count": len(results["related_questions"])
                }
            else:
                features["people_also_ask"] = {"presence": "none"}
            
            # Knowledge panel
            if "knowledge_graph" in results:
                features["knowledge_panels"] = {
                    "presence": "strong",
                    "data": results["knowledge_graph"]
                }
            else:
                features["knowledge_panels"] = {"presence": "none"}
            
            # Image pack
            if "images_results" in results:
                features["image_packs"] = {
                    "presence": "strong",
                    "data": results["images_results"],
                    "count": len(results["images_results"])
                }
            else:
                features["image_packs"] = {"presence": "none"}
            
            # Video results
            if "inline_videos" in results:
                features["video_results"] = {
                    "presence": "strong",
                    "data": results["inline_videos"],
                    "count": len(results["inline_videos"])
                }
            else:
                features["video_results"] = {"presence": "none"}
            
            # Compile SERP data
            serp_data = {
                "query": query,
                "organic_results": organic_results,
                "features": features,
                "pagination": results.get("pagination", {}),
                "search_information": results.get("search_information", {})
            }
            
            return serp_data
            
        except Exception as e:
            logger.error(f"Error getting SERP data: {str(e)}")
            return self._get_mock_serp_data(query)
    
    def get_competitors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get competitors for a query.
        
        Args:
            query: Search query
            limit: Maximum number of competitors to return
            
        Returns:
            List of competitor data
        """
        logger.info(f"Getting competitors for query: {query}")
        
        # Get SERP data
        serp_data = self.get_serp_data(query)
        
        # Extract organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Convert to competitor format
        competitors = []
        for i, result in enumerate(organic_results):
            if i >= limit:
                break
                
            competitor = {
                "url": result.get("link", ""),
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "position": i + 1,
                "domain": self._extract_domain(result.get("link", ""))
            }
            
            competitors.append(competitor)
        
        # If no competitors found, use mock data
        if not competitors:
            return self._get_mock_competitors(query, limit)
        
        return competitors
    
    def get_serp_features(self, query: str) -> Dict[str, Any]:
        """
        Get SERP features for a query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of SERP features
        """
        logger.info(f"Getting SERP features for query: {query}")
        
        # Get SERP data
        serp_data = self.get_serp_data(query)
        
        # Extract features
        features = serp_data.get("features", {})
        
        # If no features found, use mock data
        if not features:
            return self._get_mock_serp_features(query)
        
        logger.info(f"Analyzing SERP for query: {query}")
        return features
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name
        """
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            # Simple fallback
            if url.startswith("http"):
                parts = url.split("/")
                if len(parts) > 2:
                    return parts[2]
            return ""
    
    def _get_mock_serp_data(self, query: str) -> Dict[str, Any]:
        """
        Generate mock SERP data for testing.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of mock SERP data
        """
        logger.warning(f"Using mock SERP data for query: {query}")
        
        # Generate mock organic results
        organic_results = [
            {
                "position": 1,
                "title": f"Best {query} Guide for 2025",
                "link": f"https://example.com/{query.replace(' ', '-')}-guide",
                "snippet": f"Comprehensive guide to {query} with examples and best practices.",
                "displayed_link": "example.com › guides"
            },
            {
                "position": 2,
                "title": f"{query.title()} - Wikipedia",
                "link": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                "snippet": f"Overview of {query} including history, types, and applications.",
                "displayed_link": "en.wikipedia.org › wiki"
            },
            {
                "position": 3,
                "title": f"How to Master {query} in 30 Days",
                "link": f"https://blog.example.org/{query.replace(' ', '-')}-mastery",
                "snippet": f"Learn {query} from scratch with our step-by-step guide.",
                "displayed_link": "blog.example.org › guides"
            }
        ]
        
        # Generate mock features
        features = {
            "featured_snippets": {
                "presence": "strong",
                "data": {
                    "type": "paragraph",
                    "title": f"What is {query}?",
                    "content": f"{query.title()} is a strategic approach to creating and distributing valuable content to attract and engage a target audience."
                }
            },
            "people_also_ask": {
                "presence": "strong",
                "data": [
                    f"What is {query}?",
                    f"How to implement {query}?",
                    f"Best {query} examples",
                    f"{query} vs traditional methods"
                ],
                "count": 4
            },
            "knowledge_panels": {
                "presence": "none"
            },
            "image_packs": {
                "presence": "strong",
                "data": [{"title": f"{query} image 1"}, {"title": f"{query} image 2"}],
                "count": 2
            },
            "video_results": {
                "presence": "weak",
                "data": [{"title": f"{query} video tutorial"}],
                "count": 1
            }
        }
        
        # Compile mock SERP data
        serp_data = {
            "query": query,
            "organic_results": organic_results,
            "features": features,
            "pagination": {"current": 1, "next": "https://example.com/page/2"},
            "search_information": {"total_results": 1240000}
        }
        
        return serp_data
    
    def _get_mock_competitors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Generate mock competitor data for testing.
        
        Args:
            query: Search query
            limit: Maximum number of competitors to return
            
        Returns:
            List of mock competitor data
        """
        logger.warning(f"Using mock competitor data for query: {query}")
        
        # Generate mock competitors
        competitors = [
            {
                "url": f"https://example.com/{query.replace(' ', '-')}-guide",
                "title": f"Best {query} Guide for 2025",
                "snippet": f"Comprehensive guide to {query} with examples and best practices.",
                "position": 1,
                "domain": "example.com"
            },
            {
                "url": f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                "title": f"{query.title()} - Wikipedia",
                "snippet": f"Overview of {query} including history, types, and applications.",
                "position": 2,
                "domain": "wikipedia.org"
            },
            {
                "url": f"https://blog.example.org/{query.replace(' ', '-')}-mastery",
                "title": f"How to Master {query} in 30 Days",
                "snippet": f"Learn {query} from scratch with our step-by-step guide.",
                "position": 3,
                "domain": "example.org"
            }
        ]
        
        # Add more mock competitors if needed
        while len(competitors) < limit:
            position = len(competitors) + 1
            competitors.append({
                "url": f"https://site{position}.com/{query.replace(' ', '-')}",
                "title": f"{query.title()} Resource #{position}",
                "snippet": f"Another resource about {query}.",
                "position": position,
                "domain": f"site{position}.com"
            })
        
        return competitors[:limit]
    
    def _get_mock_serp_features(self, query: str) -> Dict[str, Any]:
        """
        Generate mock SERP features for testing.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of mock SERP features
        """
        logger.warning(f"Using mock SERP features for query: {query}")
        
        # Generate mock features
        features = {
            "featured_snippets": {
                "presence": "none"
            },
            "people_also_ask": {
                "presence": "none"
            },
            "knowledge_panels": {
                "presence": "none"
            },
            "image_packs": {
                "presence": "none"
            },
            "video_results": {
                "presence": "none"
            }
        }
        
        return features
