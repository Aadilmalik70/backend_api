"""
Enhanced Keyword Processor with Real Data Integration

This module provides enhanced keyword processing functionality using real data sources
instead of mock data. Refactored into smaller, focused modules.
"""

import logging
from typing import Dict, Any, List, Optional

from .keyword_extractor import KeywordExtractor
from .score_calculator import ScoreCalculator
from .trend_analyzer import TrendAnalyzer

from ..utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer
from ..utils.keyword_planner_api import KeywordPlannerAPI

# Google APIs Integration
try:
    from ..utils.google_apis.custom_search_client import CustomSearchClient
    from ..utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordProcessorEnhancedReal:
    """
    Enhanced keyword processor with real data integration.
    
    This class provides methods for processing keywords using real data sources
    instead of mock data. Refactored for better maintainability.
    """
    
    def __init__(self, google_ads_credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the enhanced keyword processor.
        
        Args:
            google_ads_credentials: Google Ads API credentials for real data integration
        """
        # Initialize component modules
        self.keyword_extractor = KeywordExtractor()
        self.score_calculator = ScoreCalculator()
        self.trend_analyzer = TrendAnalyzer()
        
        # Multi-tier client architecture: Google APIs -> SerpAPI fallback
        if GOOGLE_APIS_AVAILABLE:
            self.google_search = CustomSearchClient()
            self.knowledge_graph = KnowledgeGraphClient()
            self.google_apis_enabled = True
            logger.info("✅ Google APIs clients initialized")
        else:
            self.google_search = None
            self.knowledge_graph = None
            self.google_apis_enabled = False
            logger.warning("⚠️  Google APIs not available")
        
        # Keep SerpAPI as fallback
        self.keyword_planner = SerpAPIKeywordAnalyzer()
        
        # Initialize Google Ads API if credentials provided
        if google_ads_credentials:
            self.google_ads_api = KeywordPlannerAPI(google_ads_credentials)
        else:
            self.google_ads_api = None
    
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
        seed_keywords = self.keyword_extractor.extract_seed_keywords(input_text)
        logger.info(f"Extracted {len(seed_keywords)} seed keywords")
        
        # Get keyword metrics from Keyword Planner API
        keyword_metrics = self.keyword_planner.get_keyword_metrics(seed_keywords)
        logger.info(f"Retrieved metrics for {len(keyword_metrics)} keywords")
        
        # Generate related keywords using Google APIs or fallback
        related_keywords = self._get_enhanced_keyword_ideas(seed_keywords)
        logger.info(f"Generated {len(related_keywords)} related keywords")
        
        # Enhance keywords with entity analysis if Google APIs available
        if self.google_apis_enabled:
            keyword_metrics = self._enhance_keywords_with_entities(keyword_metrics)
            related_keywords = self._enhance_keywords_with_entities(related_keywords)
        
        # Calculate difficulty and opportunity scores
        for keyword in keyword_metrics:
            # Ensure all required fields are present and have proper types
            if "competition" in keyword and not isinstance(keyword["competition"], (int, float)):
                try:
                    keyword["competition"] = float(keyword["competition"])
                except (ValueError, TypeError):
                    keyword["competition"] = 0.5  # Default value if conversion fails
            
            keyword["difficulty"] = self.score_calculator.calculate_difficulty(keyword)
            keyword["opportunity"] = self.score_calculator.calculate_opportunity(keyword)
        
        # Generate trend analysis
        trend_analysis = self.trend_analyzer.generate_trend_analysis(keyword_metrics)
        
        # Compile result
        result = {
            "seed_keywords": seed_keywords,
            "keyword_metrics": keyword_metrics,
            "related_keywords": related_keywords,
            "trend_analysis": trend_analysis
        }
        
        return result
    
    def _get_enhanced_keyword_ideas(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Get keyword ideas using Google APIs with SerpAPI fallback.
        
        Args:
            seed_keywords: List of seed keywords
            
        Returns:
            List of related keywords with enhanced data
        """
        if self.google_apis_enabled and self.google_search:
            try:
                return self.keyword_extractor.get_keywords_from_google_search(
                    seed_keywords, self.google_search
                )
            except Exception as e:
                logger.warning(f"Google APIs failed, using SerpAPI fallback: {str(e)}")
                return self.keyword_extractor.get_keywords_from_serpapi(
                    seed_keywords, self.keyword_planner
                )
        else:
            return self.keyword_extractor.get_keywords_from_serpapi(
                seed_keywords, self.keyword_planner
            )
    
    def _enhance_keywords_with_entities(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enhance keywords with entity analysis using Knowledge Graph.
        
        Args:
            keywords: List of keyword dictionaries
            
        Returns:
            Enhanced keywords with entity data
        """
        if not self.knowledge_graph:
            return keywords
        
        enhanced_keywords = []
        
        for keyword_data in keywords:
            keyword = keyword_data.get('keyword', '')
            if not keyword:
                enhanced_keywords.append(keyword_data)
                continue
            
            try:
                # Get entity data from Knowledge Graph - Fixed: expecting dict not list
                entities = self.knowledge_graph.search_entities(keyword, limit=3)
                logger.debug(f"Entities for '{keyword}': {entities}")
                
                # Add entity information to keyword data
                keyword_data['entities'] = entities.get('itemListElement', [])
                keyword_data['entity_score'] = self.score_calculator.calculate_entity_relevance(entities)
                keyword_data['has_knowledge_panel'] = len(entities.get('itemListElement', [])) > 0
                
            except Exception as e:
                logger.warning(f"Error enhancing keyword '{keyword}' with entities: {str(e)}")
                keyword_data['entities'] = []
                keyword_data['entity_score'] = 0
                keyword_data['has_knowledge_panel'] = False
            
            enhanced_keywords.append(keyword_data)
        
        return enhanced_keywords
    
    def analyze_keyword_difficulty(self, keyword: str) -> Dict[str, Any]:
        """
        Analyze difficulty for a single keyword.
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Difficulty analysis results
        """
        try:
            # Get keyword metrics
            keyword_metrics = self.keyword_planner.get_keyword_metrics([keyword])
            
            if not keyword_metrics:
                return {
                    "keyword": keyword,
                    "difficulty": 50,
                    "opportunity": 50,
                    "error": "No metrics available"
                }
            
            keyword_data = keyword_metrics[0]
            
            # Calculate scores
            difficulty = self.score_calculator.calculate_difficulty(keyword_data)
            opportunity = self.score_calculator.calculate_opportunity(keyword_data)
            
            # Add entity analysis if available
            if self.google_apis_enabled:
                enhanced_data = self._enhance_keywords_with_entities([keyword_data])
                keyword_data = enhanced_data[0]
            
            # Add trend analysis
            trend_analysis = self.trend_analyzer.generate_trend_analysis([keyword_data])
            seasonal_analysis = self.trend_analyzer.analyze_seasonal_patterns(keyword_data)
            
            return {
                "keyword": keyword,
                "difficulty": difficulty,
                "opportunity": opportunity,
                "metrics": keyword_data,
                "trend_analysis": trend_analysis.get(keyword, {}),
                "seasonal_analysis": seasonal_analysis
            }
            
        except Exception as e:
            logger.error(f"Error analyzing keyword difficulty for '{keyword}': {str(e)}")
            return {
                "keyword": keyword,
                "difficulty": 50,
                "opportunity": 50,
                "error": str(e)
            }
    
    def get_keyword_suggestions(self, seed_keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get keyword suggestions for a seed keyword.
        
        Args:
            seed_keyword: Base keyword for suggestions
            limit: Maximum number of suggestions
            
        Returns:
            List of keyword suggestions with metrics
        """
        try:
            # Get related keywords
            related_keywords = self._get_enhanced_keyword_ideas([seed_keyword])
            
            # Enhance with scoring
            for keyword_data in related_keywords:
                keyword_data["difficulty"] = self.score_calculator.calculate_difficulty(keyword_data)
                keyword_data["opportunity"] = self.score_calculator.calculate_opportunity(keyword_data)
            
            # Sort by opportunity score (descending) and limit results
            related_keywords.sort(key=lambda x: x.get('opportunity', 0), reverse=True)
            
            return related_keywords[:limit]
            
        except Exception as e:
            logger.error(f"Error getting keyword suggestions for '{seed_keyword}': {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of all API connections.
        
        Returns:
            Dictionary with health status of each service
        """
        health_status = {
            "google_apis_available": self.google_apis_enabled,
            "serpapi_available": True,  # Assuming always available
            "services": {}
        }
        
        # Check Google APIs
        if self.google_apis_enabled:
            try:
                health_status["services"]["google_search"] = self.google_search.health_check() if self.google_search else False
                health_status["services"]["knowledge_graph"] = self.knowledge_graph.health_check() if self.knowledge_graph else False
            except Exception as e:
                logger.error(f"Error checking Google APIs health: {str(e)}")
                health_status["services"]["google_apis_error"] = str(e)
        
        # Check SerpAPI (basic check)
        try:
            health_status["services"]["serpapi"] = True
        except Exception as e:
            logger.error(f"Error checking SerpAPI health: {str(e)}")
            health_status["services"]["serpapi"] = False
            health_status["services"]["serpapi_error"] = str(e)
        
        return health_status
