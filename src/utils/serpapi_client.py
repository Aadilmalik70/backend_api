"""
SerpAPI Integration Module

This module provides integration with SerpAPI for SERP data retrieval.
"""

import logging
import time
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
        self.last_request_time = 0
        self.min_request_interval = 3.0  # Increased to 3 seconds between requests
        
        # Try to initialize the client if API key is provided
        if api_key:
            try:
                # Try new serpapi package first
                try:
                    import serpapi
                    self.client = serpapi
                    self.use_new_api = True
                    logger.info("SerpAPI client initialized successfully (new API)")
                except ImportError:
                    # Fall back to old google-search-results package
                    from serpapi import GoogleSearch
                    self.client = GoogleSearch
                    self.use_new_api = False
                    logger.info("SerpAPI client initialized successfully (legacy API)")
            except Exception as e:
                logger.error(f"Error initializing SerpAPI client: {str(e)}")
                logger.error("Please install either 'pip install serpapi' or 'pip install google-search-results'")
                self.client = None
        else:
            logger.warning("SerpAPI client initialized without API key")
    
    def _rate_limit(self):
        """Implement aggressive rate limiting to avoid hitting API limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_serp_data(self, query: str, location: str = "United States") -> Dict[str, Any]:
        """
        Get SERP data for a query.
        
        Args:
            query: Search query
            location: Search location
            
        Returns:
            Dictionary containing SERP data
            
        Raises:
            Exception: If API is not available or request fails
        """
        logger.info(f"Getting SERP data for query: {query}")
        
        # Check if client is initialized and API key is provided
        if not self.client or not self.api_key:
            raise Exception("SerpAPI client not properly initialized. Please provide a valid API key.")
        
        # Apply rate limiting
        self._rate_limit()
        
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
            
            # Execute search based on API version
            if hasattr(self, 'use_new_api') and self.use_new_api:
                # New API
                results = self.client.search(params)
            else:
                # Legacy API
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
            # Check if it's a rate limit error and wait longer
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning(f"Rate limit hit for query '{query}', waiting 10 seconds...")
                time.sleep(10)
            # Re-raise the exception instead of falling back to mock data
            raise Exception(f"Failed to get SERP data for query '{query}': {str(e)}")
    
    def get_competitors(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get competitors for a query.
        
        Args:
            query: Search query
            limit: Maximum number of competitors to return
            
        Returns:
            List of competitor data
            
        Raises:
            Exception: If API request fails
        """
        logger.info(f"Getting competitors for query: {query}")
        
        try:
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
            
            return competitors
            
        except Exception as e:
            logger.error(f"Error getting competitors: {str(e)}")
            raise Exception(f"Failed to get competitors for query '{query}': {str(e)}")
    
    def get_serp_features(self, query: str) -> Dict[str, Any]:
        """
        Get SERP features for a query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of SERP features
            
        Raises:
            Exception: If API request fails
        """
        logger.info(f"Getting SERP features for query: {query}")
        
        try:
            # Get SERP data
            serp_data = self.get_serp_data(query)
            
            # Extract features
            features = serp_data.get("features", {})
            
            logger.info(f"Analyzing SERP for query: {query}")
            return features
            
        except Exception as e:
            logger.error(f"Error getting SERP features: {str(e)}")
            raise Exception(f"Failed to get SERP features for query '{query}': {str(e)}")
    
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
