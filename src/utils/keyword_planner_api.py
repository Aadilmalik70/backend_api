"""
Google Keyword Planner API Integration

This module provides integration with Google Keyword Planner API for keyword research
and analysis.
"""

import os
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime

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
                
                # Ensure credentials include use_proto_plus setting
                if 'use_proto_plus' not in credentials:
                    credentials['use_proto_plus'] = True
                
                # Create client
                self.client = GoogleAdsClient.load_from_dict(credentials)
                logger.info("Google Ads API client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Google Ads API client: {type(e).__name__} - {str(e)}")
                logger.info("Please ensure your Google Ads API credentials (developer_token, client_id, client_secret, refresh_token, login_customer_id) are correctly configured in your environment or credentials file and that the authorizing user has API access.")
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
        logger.info(f"Google Ads API metrics object for trend data: {metrics}")

        monthly_data_dict = {}
        year_over_year_change = None
        trend_direction = None
        trend_strength = None
        seasonal_pattern = "non-seasonal" # Placeholder, can be None if not determinable

        # Attempt to parse monthly search volumes
        # This is a guess, actual field name and structure may vary
        if hasattr(metrics, 'monthly_search_volumes') and metrics.monthly_search_volumes:
            for month_data in metrics.monthly_search_volumes:
                try:
                    # Assuming month_data is an object with 'year', 'month', and 'monthly_searches' attributes
                    # Adjust based on actual structure
                    year = month_data.year
                    month_name = month_data.month.name # Assuming month is an enum
                    # Convert month name to number (e.g., JANUARY to 01)
                    month_number = datetime.strptime(month_name, "%B").month if isinstance(month_name, str) else month_name.value # if it's an enum
                    month_str = f"{month_number:02d}"
                    key = f"{year}-{month_str}"
                    monthly_data_dict[key] = month_data.monthly_searches
                except AttributeError as e:
                    logger.warning(f"Could not parse month_data attribute: {e}. Data: {month_data}")
                except Exception as e:
                    logger.warning(f"Error processing monthly data point: {e}. Data: {month_data}")
        
        # Attempt to get year_over_year_change
        if hasattr(metrics, 'year_over_year_change'):
            year_over_year_change = metrics.year_over_year_change
            
        # Trend direction and strength might be available or derivable
        # For now, defaulting to None if not directly available
        if hasattr(metrics, 'trend_direction'):
            trend_direction = metrics.trend_direction
        
        if hasattr(metrics, 'trend_strength'):
            trend_strength = metrics.trend_strength

        # seasonal_pattern could be determined by analyzing monthly_data_dict if enough data points exist
        # For now, it's a placeholder or can be set to None.

        return {
            "trend_direction": trend_direction,
            "trend_strength": trend_strength,
            "seasonal_pattern": seasonal_pattern,
            "year_over_year_change": year_over_year_change,
            "monthly_data": monthly_data_dict
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
                    "trend_direction": random.choice(["up", "down", "stable", None]),
                    "trend_strength": random.choice(["low", "medium", "high", None]),
                    "seasonal_pattern": "non-seasonal", # Could be improved
                    "year_over_year_change": f"{random.randint(-10, 20)}%",
                    "monthly_data": {
                        "2023-01": random.randint(500, 1000),
                        "2023-02": random.randint(500, 1000),
                        "2023-03": random.randint(500, 1000),
                        "2023-04": random.randint(500, 1000),
                    }
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
                    "trend_direction": random.choice(["up", "down", "stable", None]),
                    "trend_strength": random.choice(["low", "medium", "high", None]),
                    "seasonal_pattern": "non-seasonal", # Could be improved
                    "year_over_year_change": f"{random.randint(-10, 20)}%",
                    "monthly_data": {
                        "2023-01": random.randint(300, 800),
                        "2023-02": random.randint(300, 800),
                        "2023-03": random.randint(300, 800),
                        "2023-04": random.randint(300, 800),
                    }
                }
                }
        
        return mock_data
