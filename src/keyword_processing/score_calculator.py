"""
Score Calculator Module

This module handles the calculation of difficulty and opportunity scores for keywords.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ScoreCalculator:
    """
    Handles calculation of keyword difficulty and opportunity scores.
    """
    
    def __init__(self):
        """Initialize the score calculator."""
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
    
    def calculate_difficulty(self, keyword_data: Dict[str, Any]) -> int:
        """
        Calculate keyword difficulty score (0-100).
        
        Args:
            keyword_data: Keyword data dictionary
            
        Returns:
            Difficulty score (0-100)
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error calculating difficulty score: {str(e)}")
            return 50  # Default moderate difficulty
    
    def calculate_opportunity(self, keyword_data: Dict[str, Any]) -> int:
        """
        Calculate keyword opportunity score (0-100).
        
        Args:
            keyword_data: Keyword data dictionary
            
        Returns:
            Opportunity score (0-100)
        """
        try:
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
            
        except Exception as e:
            logger.error(f"Error calculating opportunity score: {str(e)}")
            return 50  # Default moderate opportunity
    
    def calculate_entity_relevance(self, entities: Dict[str, Any]) -> float:
        """
        Calculate entity relevance score.
        
        Args:
            entities: Entity data from Knowledge Graph
            
        Returns:
            Entity relevance score (0.0 to 1.0)
        """
        try:
            if not entities or 'itemListElement' not in entities:
                return 0.0
            
            entity_list = entities['itemListElement']
            if not entity_list:
                return 0.0
            
            # Calculate score based on number of entities and their result scores
            total_score = 0.0
            for entity in entity_list:
                result_score = entity.get('resultScore', 0)
                # Normalize the score (typical range is 0-1000+)
                normalized_score = min(1.0, result_score / 1000.0)
                total_score += normalized_score
            
            # Average score across all entities
            return min(1.0, total_score / len(entity_list))
            
        except Exception as e:
            logger.error(f"Error calculating entity relevance: {str(e)}")
            return 0.0
