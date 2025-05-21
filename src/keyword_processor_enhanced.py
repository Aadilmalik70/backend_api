import os
import json
import random
import re
from datetime import datetime

class KeywordProcessor:
    """
    Enhanced class for processing keywords and generating keyword insights.
    """
    
    def __init__(self):
        """Initialize the KeywordProcessor with default settings."""
        self.difficulty_factors = {
            "competition": 0.4,
            "search_volume": 0.3,
            "cpc": 0.2,
            "serp_features": 0.1
        }
        
        self.opportunity_factors = {
            "competition": -0.3,
            "search_volume": 0.4,
            "relevance": 0.2,
            "trend": 0.1
        }
        
        # Mock data for search volumes (would be from API in real implementation)
        self.mock_search_volumes = {
            "ai content strategy": 2400,
            "serp dominance": 1200,
            "ai content optimization": 1800,
            "content strategy tools": 3600,
            "ai for seo": 2900,
            "content gap analysis": 1500,
            "featured snippet optimization": 1100,
            "ai seo tools": 2200,
            "content optimization software": 1900,
            "keyword research tools": 4500,
            "serp features": 1300,
            "content strategy template": 2800,
            "ai writing tools": 3200,
            "seo content strategy": 2600,
            "competitor content analysis": 1400
        }
        
        # Mock data for CPC values (would be from API in real implementation)
        self.mock_cpc_values = {
            "ai content strategy": 4.25,
            "serp dominance": 3.80,
            "ai content optimization": 4.10,
            "content strategy tools": 5.20,
            "ai for seo": 4.75,
            "content gap analysis": 3.50,
            "featured snippet optimization": 3.90,
            "ai seo tools": 4.50,
            "content optimization software": 4.80,
            "keyword research tools": 5.50,
            "serp features": 3.70,
            "content strategy template": 4.30,
            "ai writing tools": 4.90,
            "seo content strategy": 4.60,
            "competitor content analysis": 3.85
        }
        
        # Mock data for competition levels (would be from API in real implementation)
        self.mock_competition_levels = {
            "ai content strategy": 0.75,
            "serp dominance": 0.68,
            "ai content optimization": 0.72,
            "content strategy tools": 0.82,
            "ai for seo": 0.78,
            "content gap analysis": 0.65,
            "featured snippet optimization": 0.70,
            "ai seo tools": 0.76,
            "content optimization software": 0.80,
            "keyword research tools": 0.85,
            "serp features": 0.67,
            "content strategy template": 0.74,
            "ai writing tools": 0.79,
            "seo content strategy": 0.77,
            "competitor content analysis": 0.69
        }
        
        # Mock trend data (would be from API in real implementation)
        self.mock_trend_data = {
            "ai content strategy": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "serp dominance": {"direction": "up", "strength": "moderate", "pattern": "steady"},
            "ai content optimization": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "content strategy tools": {"direction": "up", "strength": "moderate", "pattern": "higher in Q1/Q3"},
            "ai for seo": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "content gap analysis": {"direction": "up", "strength": "moderate", "pattern": "steady"},
            "featured snippet optimization": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "ai seo tools": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "content optimization software": {"direction": "up", "strength": "moderate", "pattern": "higher in Q1"},
            "keyword research tools": {"direction": "stable", "strength": "n/a", "pattern": "seasonal peaks"},
            "serp features": {"direction": "up", "strength": "moderate", "pattern": "steady"},
            "content strategy template": {"direction": "up", "strength": "moderate", "pattern": "higher in Q1/Q3"},
            "ai writing tools": {"direction": "up", "strength": "strong", "pattern": "steady"},
            "seo content strategy": {"direction": "up", "strength": "moderate", "pattern": "steady"},
            "competitor content analysis": {"direction": "up", "strength": "moderate", "pattern": "steady"}
        }
    
    def process(self, input_text):
        """
        Process input text to generate keyword insights.
        
        Args:
            input_text (str): The input text to process
            
        Returns:
            dict: Keyword data and insights
        """
        # In a real implementation, this would use NLP and keyword research APIs
        # For now, we'll generate realistic mock data
        
        # Extract main topic and generate related keywords
        main_topic = self._extract_main_topic(input_text)
        keywords = self._generate_related_keywords(main_topic)
        
        # Calculate keyword scores
        keyword_scores = {}
        for keyword in keywords:
            difficulty = self._calculate_difficulty(keyword)
            opportunity = self._calculate_opportunity(keyword)
            
            keyword_scores[keyword] = {
                "difficulty": difficulty,
                "opportunity": opportunity
            }
        
        # Generate enhanced metrics
        enhanced_metrics = self._generate_enhanced_metrics(keywords)
        
        # Generate trend analysis
        trend_analysis = self._generate_trend_analysis(keywords)
        
        # Compile keyword data
        keyword_data = {
            "main_topic": main_topic,
            "keywords": keywords,
            "keyword_scores": keyword_scores,
            "enhanced_metrics": enhanced_metrics,
            "trend_analysis": trend_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
        return keyword_data
    
    def _extract_main_topic(self, input_text):
        """Extract the main topic from input text."""
        # In a real implementation, this would use NLP to extract the main topic
        # For now, we'll use a simple approach
        
        # Remove common filler words
        cleaned_text = re.sub(r'\b(the|a|an|and|or|for|to|in|on|with|about)\b', '', input_text, flags=re.IGNORECASE)
        
        # If the input contains "content strategy" or similar, use that as the main topic
        if re.search(r'content\s+strategy', input_text, re.IGNORECASE):
            return "content strategy"
        elif re.search(r'serp\s+dominance', input_text, re.IGNORECASE):
            return "serp dominance"
        elif re.search(r'ai\s+content', input_text, re.IGNORECASE):
            return "ai content strategy"
        
        # Default to a generic topic if no specific one is found
        return "ai content strategy for serp dominance"
    
    def _generate_related_keywords(self, main_topic):
        """Generate related keywords based on the main topic."""
        # In a real implementation, this would use keyword research APIs
        # For now, we'll use predefined keywords based on the main topic
        
        main_topic_lower = main_topic.lower()
        
        if "content strategy" in main_topic_lower:
            base_keywords = [
                "ai content strategy",
                "content strategy tools",
                "seo content strategy",
                "content strategy template",
                "content gap analysis",
                "competitor content analysis"
            ]
        elif "serp" in main_topic_lower:
            base_keywords = [
                "serp dominance",
                "serp features",
                "featured snippet optimization",
                "ai for seo",
                "seo content strategy",
                "serp ranking factors"
            ]
        elif "ai" in main_topic_lower:
            base_keywords = [
                "ai content strategy",
                "ai content optimization",
                "ai for seo",
                "ai seo tools",
                "ai writing tools",
                "content optimization software"
            ]
        else:
            # Default keywords
            base_keywords = [
                "ai content strategy",
                "serp dominance",
                "ai content optimization",
                "content strategy tools",
                "ai for seo",
                "content gap analysis",
                "featured snippet optimization"
            ]
        
        # Ensure we have 7-10 keywords
        if len(base_keywords) < 7:
            additional_keywords = [
                "keyword research tools",
                "content optimization software",
                "ai seo tools",
                "content strategy template",
                "ai writing tools",
                "seo content strategy",
                "competitor content analysis"
            ]
            
            # Add additional keywords until we have at least 7
            while len(base_keywords) < 7:
                keyword = additional_keywords.pop(0)
                if keyword not in base_keywords:
                    base_keywords.append(keyword)
        
        # Limit to 10 keywords
        return base_keywords[:10]
    
    def _calculate_difficulty(self, keyword):
        """Calculate keyword difficulty score (0-100)."""
        # In a real implementation, this would use keyword research APIs
        # For now, we'll generate realistic scores based on mock data
        
        # Get mock data for the keyword
        competition = self.mock_competition_levels.get(keyword, random.uniform(0.6, 0.85))
        search_volume = self.mock_search_volumes.get(keyword, random.randint(1000, 5000))
        cpc = self.mock_cpc_values.get(keyword, random.uniform(3.5, 5.5))
        
        # Normalize search volume (higher volume = higher difficulty)
        normalized_volume = min(1.0, search_volume / 5000)
        
        # Normalize CPC (higher CPC = higher difficulty)
        normalized_cpc = min(1.0, cpc / 6.0)
        
        # Calculate weighted score
        weighted_score = (
            competition * self.difficulty_factors["competition"] +
            normalized_volume * self.difficulty_factors["search_volume"] +
            normalized_cpc * self.difficulty_factors["cpc"] +
            random.uniform(0.3, 0.7) * self.difficulty_factors["serp_features"]  # Random SERP features factor
        )
        
        # Convert to 0-100 scale
        difficulty = int(weighted_score * 100)
        
        # Ensure score is within 0-100 range
        return max(0, min(100, difficulty))
    
    def _calculate_opportunity(self, keyword):
        """Calculate keyword opportunity score (0-100)."""
        # In a real implementation, this would use keyword research APIs
        # For now, we'll generate realistic scores based on mock data
        
        # Get mock data for the keyword
        competition = self.mock_competition_levels.get(keyword, random.uniform(0.6, 0.85))
        search_volume = self.mock_search_volumes.get(keyword, random.randint(1000, 5000))
        trend_data = self.mock_trend_data.get(keyword, {"direction": "stable", "strength": "n/a"})
        
        # Normalize search volume (higher volume = higher opportunity)
        normalized_volume = min(1.0, search_volume / 5000)
        
        # Calculate trend factor (up = higher opportunity)
        trend_factor = 0.5  # Default (stable)
        if trend_data["direction"] == "up":
            trend_factor = 0.8 if trend_data["strength"] == "strong" else 0.7
        elif trend_data["direction"] == "down":
            trend_factor = 0.3 if trend_data["strength"] == "strong" else 0.4
        
        # Calculate relevance (random for mock data)
        relevance = random.uniform(0.7, 1.0)
        
        # Calculate weighted score
        weighted_score = (
            (1 - competition) * -self.opportunity_factors["competition"] +  # Invert competition (lower = better)
            normalized_volume * self.opportunity_factors["search_volume"] +
            relevance * self.opportunity_factors["relevance"] +
            trend_factor * self.opportunity_factors["trend"]
        )
        
        # Convert to 0-100 scale
        opportunity = int(weighted_score * 100)
        
        # Ensure score is within 0-100 range
        return max(0, min(100, opportunity))
    
    def _generate_enhanced_metrics(self, keywords):
        """Generate enhanced metrics for keywords."""
        enhanced_metrics = {}
        
        for keyword in keywords:
            enhanced_metrics[keyword] = {
                "search_volume": self.mock_search_volumes.get(keyword, random.randint(1000, 5000)),
                "cpc": self.mock_cpc_values.get(keyword, round(random.uniform(3.5, 5.5), 2)),
                "competition": self.mock_competition_levels.get(keyword, round(random.uniform(0.6, 0.85), 2)),
                "serp_features": self._generate_mock_serp_features()
            }
        
        return enhanced_metrics
    
    def _generate_mock_serp_features(self):
        """Generate mock SERP features presence."""
        features = ["featured_snippet", "people_also_ask", "knowledge_panel", "image_pack", "video_results", "local_pack", "top_stories"]
        present_features = []
        
        # Randomly select which features are present
        for feature in features:
            if random.random() < 0.4:  # 40% chance for each feature
                present_features.append(feature)
        
        return present_features
    
    def _generate_trend_analysis(self, keywords):
        """Generate trend analysis for keywords."""
        trend_analysis = {}
        
        for keyword in keywords:
            mock_trend = self.mock_trend_data.get(keyword, {
                "direction": random.choice(["up", "stable", "down"]),
                "strength": random.choice(["strong", "moderate", "weak"]),
                "pattern": random.choice(["steady", "seasonal", "volatile"])
            })
            
            trend_analysis[keyword] = {
                "trend_direction": mock_trend["direction"],
                "trend_strength": mock_trend["strength"],
                "seasonal_pattern": mock_trend["pattern"],
                "year_over_year_change": self._generate_mock_yoy_change(mock_trend["direction"], mock_trend["strength"])
            }
        
        return trend_analysis
    
    def _generate_mock_yoy_change(self, direction, strength):
        """Generate mock year-over-year change percentage based on trend direction and strength."""
        if direction == "up":
            if strength == "strong":
                return f"+{random.randint(30, 80)}%"
            elif strength == "moderate":
                return f"+{random.randint(15, 29)}%"
            else:  # weak
                return f"+{random.randint(5, 14)}%"
        elif direction == "down":
            if strength == "strong":
                return f"-{random.randint(30, 50)}%"
            elif strength == "moderate":
                return f"-{random.randint(15, 29)}%"
            else:  # weak
                return f"-{random.randint(5, 14)}%"
        else:  # stable
            return f"{random.randint(-4, 4)}%"
