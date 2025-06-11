"""
Enhanced Keyword Processor with Real Data Integration

This module provides enhanced keyword processing functionality using real data sources
instead of mock data.
"""

import logging
import re
import random
from typing import Dict, Any, List, Optional

from utils.keyword_planner_api import KeywordPlannerAPI
from utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KeywordProcessorEnhancedReal:
    """
    Enhanced keyword processor with real data integration.
    
    This class provides methods for processing keywords using real data sources
    instead of mock data.
    """
    
    def __init__(self, google_ads_credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the enhanced keyword processor.
        
        Args:
            google_ads_credentials: Google Ads API credentials for real data integration
        """
        self.keyword_planner = SerpAPIKeywordAnalyzer()
        
        # Define difficulty factors (weights)
        self.difficulty_factors = {
            "competition": 0.4,
            "search_volume": 0.3,
            "cpc": 0.2,
            "serp_features": 0.1
        }
        
        # Define opportunity factors (weights)
        self.opportunity_factors = {
            "competition": 0.3,
            "search_volume": 0.3,
            "relevance": 0.2,
            "trend": 0.2
        }
    
    def process_keywords(self, input_text: str) -> Dict[str, Any]:
        """
        Process keywords from input text.
        
        Args:
            input_text: Input text containing keywords
            
        Returns:
            Dictionary containing processed keywords and metrics
        """
        logger.info(f"Processing keywords from input: {input_text}")
        
        # Extract seed keywords from input text
        seed_keywords = self._extract_seed_keywords(input_text)
        logger.info(f"Extracted {len(seed_keywords)} seed keywords")
        
        # Get keyword metrics from Keyword Planner API
        keyword_metrics = self.keyword_planner.get_keyword_metrics(seed_keywords)
        logger.info(f"Retrieved metrics for {len(keyword_metrics)} keywords")
        
        # Generate related keywords (limit to reduce API calls)
        related_keywords_dict = self.keyword_planner.get_keyword_ideas(seed_keywords)
        logger.info(f"Generated {len(related_keywords_dict)} related keywords")
        
        # Convert related_keywords from dict to list to match test expectations
        related_keywords = []
        for keyword, data in related_keywords_dict.items():
            # Create a copy of the data and add the keyword
            keyword_data = dict(data)
            keyword_data["keyword"] = keyword
            related_keywords.append(keyword_data)
        
        # Calculate difficulty and opportunity scores
        for keyword in keyword_metrics:
            # Ensure all required fields are present and have proper types
            if "competition" in keyword and not isinstance(keyword["competition"], (int, float)):
                try:
                    keyword["competition"] = float(keyword["competition"])
                except (ValueError, TypeError):
                    keyword["competition"] = 0.5  # Default value if conversion fails
            
            keyword["difficulty"] = self._calculate_difficulty(keyword)
            keyword["opportunity"] = self._calculate_opportunity(keyword)
        
        # Generate trend analysis
        trend_analysis = self._generate_trend_analysis(keyword_metrics)
        
        # Compile result
        result = {
            "seed_keywords": seed_keywords,
            "keyword_metrics": keyword_metrics,
            "related_keywords": related_keywords,  # Now a list instead of a dict
            "trend_analysis": trend_analysis
        }
        
        return result
    
    def _extract_seed_keywords(self, input_text: str) -> List[str]:
        """
        Extract seed keywords from input text.
        
        Args:
            input_text: Input text containing keywords
            
        Returns:
            List of seed keywords
        """
        # Split input text by common separators
        separators = r'[,;|]|\band\b|\bor\b'
        keywords = [kw.strip() for kw in re.split(separators, input_text) if kw.strip()]
        
        # Remove duplicates while preserving order
        unique_keywords = []
        for kw in keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)
        
        return unique_keywords
    
    def _calculate_difficulty(self, keyword_data: Dict[str, Any]) -> int:
        """
        Calculate keyword difficulty score (0-100).
        
        Args:
            keyword_data: Keyword data dictionary
            
        Returns:
            Difficulty score (0-100)
        """
        # Extract metrics and ensure they are numeric
        competition = float(keyword_data.get("competition", 0.5))
        
        # Handle search_volume - ensure it's numeric
        search_volume = keyword_data.get("search_volume", 1000)
        if not isinstance(search_volume, (int, float)):
            try:
                search_volume = float(search_volume)
            except (ValueError, TypeError):
                search_volume = 1000  # Default value
        
        # Handle CPC - ensure it's numeric
        cpc = keyword_data.get("cpc", 1.0)
        if not isinstance(cpc, (int, float)):
            try:
                cpc = float(cpc)
            except (ValueError, TypeError):
                cpc = 1.0  # Default value
        
        # Handle SERP features - ensure it's a list
        serp_features = keyword_data.get("serp_features", [])
        if not isinstance(serp_features, list):
            serp_features = []
        
        # Normalize search volume (higher volume = higher difficulty)
        normalized_volume = min(1.0, search_volume / 10000)
        
        # Normalize CPC (higher CPC = higher difficulty)
        normalized_cpc = min(1.0, cpc / 10.0)
        
        # Calculate SERP features factor (more features = higher difficulty)
        serp_factor = min(1.0, len(serp_features) / 7.0)  # Assuming max 7 features
        
        # Calculate weighted score
        weighted_score = (
            competition * self.difficulty_factors["competition"] +
            normalized_volume * self.difficulty_factors["search_volume"] +
            normalized_cpc * self.difficulty_factors["cpc"] +
            serp_factor * self.difficulty_factors["serp_features"]
        )
        
        # Convert to 0-100 scale
        difficulty = int(weighted_score * 100)
        
        # Ensure score is within 0-100 range
        return max(0, min(100, difficulty))
    
    def _calculate_opportunity(self, keyword_data: Dict[str, Any]) -> int:
        """
        Calculate keyword opportunity score (0-100).
        
        Args:
            keyword_data: Keyword data dictionary
            
        Returns:
            Opportunity score (0-100)
        """
        # Extract metrics and ensure they are numeric
        competition = float(keyword_data.get("competition", 0.5))
        
        # Handle search_volume - ensure it's numeric
        search_volume = keyword_data.get("search_volume", 1000)
        if not isinstance(search_volume, (int, float)):
            try:
                search_volume = float(search_volume)
            except (ValueError, TypeError):
                search_volume = 1000  # Default value
        
        relevance = float(keyword_data.get("relevance", 0.7))  # Default relevance
        trend_direction = keyword_data.get("trend_direction", "stable")
        trend_strength = keyword_data.get("trend_strength", "moderate")
        
        # Normalize search volume (higher volume = higher opportunity)
        normalized_volume = min(1.0, search_volume / 10000)
        
        # Calculate trend factor (up = higher opportunity)
        trend_factor = 0.5  # Default (stable)
        if trend_direction == "up":
            trend_factor = 0.8 if trend_strength == "strong" else 0.7
        elif trend_direction == "down":
            trend_factor = 0.3 if trend_strength == "strong" else 0.4
        
        # Calculate weighted score
        weighted_score = (
            (1 - competition) * self.opportunity_factors["competition"] +  # Invert competition (lower = better)
            normalized_volume * self.opportunity_factors["search_volume"] +
            relevance * self.opportunity_factors["relevance"] +
            trend_factor * self.opportunity_factors["trend"]
        )
        
        # Convert to 0-100 scale
        opportunity = int(weighted_score * 100)
        
        # Ensure score is within 0-100 range
        return max(0, min(100, opportunity))
    
    def _generate_trend_analysis(self, keyword_metrics: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Generate trend analysis for keywords.
        
        Args:
            keyword_metrics: List of keyword metric dictionaries
            
        Returns:
            Dictionary mapping keywords to trend analysis
        """
        trend_analysis = {}
        
        for keyword_data in keyword_metrics:
            keyword = keyword_data.get("keyword", "")
            if not keyword:
                continue
            
            # Get trend data from keyword metrics if available
            trend_direction = keyword_data.get("trend_direction", "stable")
            trend_strength = keyword_data.get("trend_strength", "moderate")
            seasonal_pattern = keyword_data.get("seasonal_pattern", "steady")
            year_over_year_change = keyword_data.get("year_over_year_change", "0%")
            
            trend_analysis[keyword] = {
                "trend_direction": trend_direction,
                "trend_strength": trend_strength,
                "seasonal_pattern": seasonal_pattern,
                "year_over_year_change": year_over_year_change
            }
        
        return trend_analysis


    