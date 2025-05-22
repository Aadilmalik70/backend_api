"""
Google Keyword Planner API Integration

This module provides integration with Google Keyword Planner API for keyword research
and analysis.
"""

import os
import logging
import random
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordPlannerAPI:
    """
    Google Keyword Planner API client.
    
    This class provides methods for interacting with Google Keyword Planner API
    to get keyword ideas, metrics, and related keywords.
    """
    
    def __init__(self, credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the Google Keyword Planner API client.
        
        Args:
            credentials: Google Ads API credentials dictionary
        """
        self.credentials = credentials
        self.client = None
        
        # Try to initialize the client if credentials are provided
        if credentials:
            try:
                # Import Google Ads API libraries
                from google.ads.googleads.client import GoogleAdsClient
                
                # Create client
                self.client = GoogleAdsClient.load_from_dict(credentials)
                logger.info("Google Ads API client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Google Ads API client: {str(e)}")
                self.client = None
        else:
            logger.warning("Google Ads API credentials not provided, using mock data")
    
    def get_keyword_ideas(self, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get keyword ideas from Google Keyword Planner.
        
        Args:
            keywords: List of seed keywords
            
        Returns:
            Dictionary mapping keywords to their metrics
        """
        logger.info(f"Getting keyword ideas for: {keywords}")
        
        # If client is not initialized, use mock data
        if not self.client:
            logger.warning("Google Ads API client not initialized, using mock data")
            return self._get_mock_keyword_ideas(keywords)
        
        try:
            # Import Google Ads API libraries
            from google.ads.googleads.client import GoogleAdsClient
            from google.ads.googleads.v14.services.types.keyword_plan_idea_service import (
                GenerateKeywordIdeasRequest,
                KeywordPlanNetworkEnum,
            )
            
            # Get the keyword plan idea service
            keyword_plan_idea_service = self.client.get_service("KeywordPlanIdeaService")
            
            # Create request
            request = GenerateKeywordIdeasRequest(
                customer_id=self.credentials.get("login_customer_id", ""),
                language="en",
                geo_target_constants=["1023191"],  # US
                include_adult_keywords=False,
                keyword_plan_network=KeywordPlanNetworkEnum.KeywordPlanNetwork.GOOGLE_SEARCH_AND_PARTNERS,
                keyword_seed={"keywords": keywords}
            )
            
            # Get keyword ideas
            response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
            
            # Process results
            keyword_ideas = {}
            for result in response.results:
                keyword = result.text.lower()
                
                # Extract metrics
                keyword_ideas[keyword] = {
                    "keyword": keyword,
                    "search_volume": result.keyword_idea_metrics.avg_monthly_searches,
                    "competition": self._get_competition_level(result.keyword_idea_metrics.competition.name),
                    "competition_index": result.keyword_idea_metrics.competition_index,
                    "cpc": result.keyword_idea_metrics.average_cpc_micros / 1000000,  # Convert micros to dollars
                    "trend_data": self._extract_trend_data(result.keyword_idea_metrics)
                }
            
            logger.info(f"Retrieved {len(keyword_ideas)} keyword ideas")
            return keyword_ideas
            
        except Exception as e:
            logger.error(f"Error getting keyword ideas: {str(e)}")
            return self._get_mock_keyword_ideas(keywords)
    
    def get_related_keywords(self, keywords: List[str]) -> List[str]:
        """
        Get related keywords from Google Keyword Planner.
        
        Args:
            keywords: List of seed keywords
            
        Returns:
            List of related keywords
        """
        logger.info(f"Getting related keywords for: {keywords}")
        
        # Get keyword ideas
        keyword_ideas = self.get_keyword_ideas(keywords)
        
        # Extract related keywords
        related_keywords = [k for k in keyword_ideas.keys() if k not in keywords]
        
        logger.info(f"Found {len(related_keywords)} related keywords")
        return related_keywords
    
    def get_keyword_metrics(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Get metrics for specific keywords from Google Keyword Planner.
        
        Args:
            keywords: List of keywords to get metrics for
            
        Returns:
            List of dictionaries containing keyword metrics
        """
        logger.info(f"Getting metrics for {len(keywords)} keywords")
        
        # Get keyword ideas for these keywords
        keyword_data = self.get_keyword_ideas(keywords)
        
        # Convert to list format
        metrics_list = []
        for keyword, data in keyword_data.items():
            metrics_list.append(data)
        
        return metrics_list
    
    def _get_competition_level(self, competition_enum: str) -> str:
        """
        Convert competition enum to string.
        
        Args:
            competition_enum: Competition enum from Google Ads API
            
        Returns:
            Competition level as string
        """
        competition_map = {
            "COMPETITION_UNSPECIFIED": "UNKNOWN",
            "LOW": "LOW",
            "MEDIUM": "MEDIUM",
            "HIGH": "HIGH"
        }
        
        return competition_map.get(competition_enum, "UNKNOWN")
    
    def _extract_trend_data(self, metrics) -> Dict[str, Any]:
        """
        Extract trend data from keyword metrics.
        
        Args:
            metrics: Keyword metrics from Google Ads API
            
        Returns:
            Dictionary containing trend data
        """
        # This would extract monthly search volume data
        # For now, we'll return a simplified version
        
        # Determine trend direction and strength
        trend_direction = "stable"
        trend_strength = "n/a"
        
        # In a real implementation, this would analyze the monthly data
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "seasonal_pattern": "non-seasonal",
            "year_over_year_change": "N/A",
            "monthly_data": {}
        }
    
    def _get_mock_keyword_ideas(self, keywords: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Generate mock keyword ideas for testing.
        
        Args:
            keywords: List of seed keywords
            
        Returns:
            Dictionary mapping keywords to their metrics
        """
        logger.warning("Using mock keyword data")
        
        mock_data = {}
        
        # Add seed keywords
        for keyword in keywords:
            mock_data[keyword] = {
                "keyword": keyword,
                "search_volume": 1000,
                "competition": "MEDIUM",
                "competition_index": 50,
                "cpc": 1.5,
                "trend_data": {
                    "trend_direction": "stable",
                    "trend_strength": "n/a",
                    "seasonal_pattern": "non-seasonal",
                    "year_over_year_change": "N/A",
                    "monthly_data": {}
                }
            }
        
        # Add some related keywords
        related_keywords = [
            f"{keyword} strategy" for keyword in keywords
        ] + [
            f"{keyword} examples" for keyword in keywords
        ] + [
            f"best {keyword}" for keyword in keywords
        ]
        
        for keyword in related_keywords:
            if keyword not in mock_data:
                mock_data[keyword] = {
                    "keyword": keyword,
                    "search_volume": 500,
                    "competition": "MEDIUM",
                    "competition_index": 40,
                    "cpc": 1.2,
                    "trend_data": {
                        "trend_direction": "stable",
                        "trend_strength": "n/a",
                        "seasonal_pattern": "non-seasonal",
                        "year_over_year_change": "N/A",
                        "monthly_data": {}
                    }
                }
        
        return mock_data
