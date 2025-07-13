"""
Trend Analyzer Module

This module handles trend analysis for keywords.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Handles trend analysis for keywords.
    """
    
    def __init__(self):
        """Initialize the trend analyzer."""
        pass
    
    def generate_trend_analysis(self, keyword_metrics: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
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
            
            try:
                # Get trend data from keyword metrics if available
                trend_direction = keyword_data.get("trend_direction", "stable")
                trend_strength = keyword_data.get("trend_strength", "moderate")
                seasonal_pattern = keyword_data.get("seasonal_pattern", "steady")
                year_over_year_change = keyword_data.get("year_over_year_change", "0%")
                
                trend_analysis[keyword] = {
                    "trend_direction": trend_direction,
                    "trend_strength": trend_strength,
                    "seasonal_pattern": seasonal_pattern,
                    "year_over_year_change": year_over_year_change,
                    "trend_score": self._calculate_trend_score(
                        trend_direction, trend_strength, seasonal_pattern
                    )
                }
                
            except Exception as e:
                logger.error(f"Error analyzing trends for keyword '{keyword}': {str(e)}")
                trend_analysis[keyword] = {
                    "trend_direction": "stable",
                    "trend_strength": "moderate", 
                    "seasonal_pattern": "steady",
                    "year_over_year_change": "0%",
                    "trend_score": 0.5,
                    "error": str(e)
                }
        
        return trend_analysis
    
    def _calculate_trend_score(self, direction: str, strength: str, pattern: str) -> float:
        """
        Calculate a numerical trend score based on trend characteristics.
        
        Args:
            direction: Trend direction (up/down/stable)
            strength: Trend strength (weak/moderate/strong)
            pattern: Seasonal pattern (steady/seasonal/volatile)
            
        Returns:
            Trend score (0.0 to 1.0)
        """
        try:
            # Base score
            score = 0.5
            
            # Direction factor
            if direction == "up":
                score += 0.3
            elif direction == "down":
                score -= 0.3
            # stable keeps the base score
            
            # Strength factor
            strength_multiplier = {
                "weak": 0.3,
                "moderate": 0.6, 
                "strong": 1.0
            }
            score *= strength_multiplier.get(strength, 0.6)
            
            # Pattern factor (steady is preferred for predictability)
            if pattern == "steady":
                score *= 1.1
            elif pattern == "seasonal":
                score *= 1.0
            elif pattern == "volatile":
                score *= 0.8
            
            # Ensure score is within bounds
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating trend score: {str(e)}")
            return 0.5
    
    def analyze_seasonal_patterns(self, keyword_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze seasonal patterns for a keyword.
        
        Args:
            keyword_data: Keyword data dictionary
            
        Returns:
            Seasonal analysis results
        """
        try:
            keyword = keyword_data.get("keyword", "")
            
            # Simple seasonal pattern detection based on keyword characteristics
            seasonal_indicators = {
                "holiday": ["christmas", "halloween", "valentine", "easter", "thanksgiving"],
                "summer": ["summer", "beach", "vacation", "pool", "sunscreen"],
                "winter": ["winter", "snow", "coat", "heating", "holiday"],
                "back_to_school": ["school", "college", "university", "student", "education"],
                "tax_season": ["tax", "refund", "irs", "accounting", "filing"]
            }
            
            keyword_lower = keyword.lower()
            detected_patterns = []
            
            for season, indicators in seasonal_indicators.items():
                if any(indicator in keyword_lower for indicator in indicators):
                    detected_patterns.append(season)
            
            if detected_patterns:
                pattern_type = "seasonal"
                primary_season = detected_patterns[0]
                confidence = 0.8
            else:
                pattern_type = "steady"
                primary_season = None
                confidence = 0.6
            
            return {
                "pattern_type": pattern_type,
                "primary_season": primary_season,
                "detected_patterns": detected_patterns,
                "confidence": confidence,
                "recommendations": self._get_seasonal_recommendations(pattern_type, primary_season)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {str(e)}")
            return {
                "pattern_type": "steady",
                "primary_season": None,
                "detected_patterns": [],
                "confidence": 0.5,
                "error": str(e)
            }
    
    def _get_seasonal_recommendations(self, pattern_type: str, primary_season: str) -> List[str]:
        """
        Get recommendations based on seasonal patterns.
        
        Args:
            pattern_type: Type of seasonal pattern
            primary_season: Primary season if seasonal
            
        Returns:
            List of recommendations
        """
        if pattern_type == "steady":
            return [
                "Maintain consistent content calendar",
                "Focus on evergreen content optimization",
                "Monitor for emerging trends"
            ]
        
        recommendations = [
            f"Plan content calendar around {primary_season} seasonality",
            "Increase budget during peak season",
            "Prepare content in advance of seasonal trends"
        ]
        
        if primary_season == "holiday":
            recommendations.extend([
                "Start campaigns 6-8 weeks before major holidays",
                "Create gift guides and seasonal content",
                "Monitor competitor holiday strategies"
            ])
        elif primary_season == "back_to_school":
            recommendations.extend([
                "Peak season is July-September",
                "Target parents and students separately",
                "Focus on educational and productivity themes"
            ])
        elif primary_season in ["summer", "winter"]:
            recommendations.extend([
                "Plan 2-3 months ahead of season",
                "Consider weather-dependent variations",
                "Adjust geographic targeting by climate"
            ])
        
        return recommendations
