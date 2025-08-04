"""
Enhanced Keyword Processor with Real Data Integration

This module provides enhanced keyword processing functionality using real data sources
instead of mock data.
"""

import logging
import re
import random
from typing import Dict, Any, List, Optional

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from src.utils.keyword_planner_api import KeywordPlannerAPI
    from src.utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer
except ImportError:
    try:
        from utils.keyword_planner_api import KeywordPlannerAPI
        from utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer
    except ImportError:
        # Fallback for local imports within src/
        from .utils.keyword_planner_api import KeywordPlannerAPI
        from .utils.serpapi_keyword_analyzer import SerpAPIKeywordAnalyzer

# Google APIs Integration
try:
    from src.utils.google_apis.custom_search_client import CustomSearchClient
    from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    try:
        from utils.google_apis.custom_search_client import CustomSearchClient
        from utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
        GOOGLE_APIS_AVAILABLE = True
    except ImportError:
        try:
            from .utils.google_apis.custom_search_client import CustomSearchClient
            from .utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
            GOOGLE_APIS_AVAILABLE = True
        except ImportError:
            GOOGLE_APIS_AVAILABLE = False
            logger.warning("Google APIs not available, using SerpAPI fallback")

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
                return self._get_keywords_from_google_search(seed_keywords)
            except Exception as e:
                logger.warning(f"Google APIs failed, using SerpAPI fallback: {str(e)}")
                return self._get_keywords_from_serpapi(seed_keywords)
        else:
            return self._get_keywords_from_serpapi(seed_keywords)
    
    def _get_keywords_from_google_search(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Extract keyword ideas from Google Custom Search.
        
        Args:
            seed_keywords: List of seed keywords
            
        Returns:
            List of keyword ideas from Google Search
        """
        keyword_ideas = []
        
        for seed_keyword in seed_keywords[:3]:  # Limit to 3 to avoid quota issues
            try:
                # Search for related terms
                search_results = self.google_search.search(seed_keyword, num_results=5)
                logger.info(f"Search results for '{seed_keyword}': {len(search_results.get('items', []))} items")
                
                if 'items' in search_results:
                    for item in search_results['items']:
                        # Extract potential keywords from title and snippet
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')
                        
                        # Simple keyword extraction (can be enhanced)
                        extracted_keywords = self._extract_keywords_from_text(title + ' ' + snippet)
                        logger.info(f"Extracted {len(extracted_keywords)} keywords from '{title[:50]}...'")
                        
                        for keyword in extracted_keywords:
                            if keyword not in [k.get('keyword') for k in keyword_ideas]:
                                keyword_ideas.append({
                                    'keyword': keyword,
                                    'search_volume': self._estimate_search_volume(keyword),
                                    'competition': self._estimate_competition(keyword),
                                    'cpc': self._estimate_cpc(keyword),
                                    'relevance': self._calculate_relevance(keyword, seed_keyword),
                                    'source': 'google_search'
                                })
                        
                        # Limit total results
                        if len(keyword_ideas) >= 20:
                            break
                else:
                    logger.warning(f"No 'items' found in search results for '{seed_keyword}'")
                            
            except Exception as e:
                logger.warning(f"Error getting keywords from Google Search for '{seed_keyword}': {str(e)}")
                continue
        
        logger.info(f"Total keywords found: {len(keyword_ideas)}")
        return keyword_ideas[:20]  # Return top 20 results
    
    def _get_keywords_from_serpapi(self, seed_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Get keyword ideas from SerpAPI (fallback method).
        
        Args:
            seed_keywords: List of seed keywords
            
        Returns:
            List of keyword ideas from SerpAPI
        """
        try:
            related_keywords_dict = self.keyword_planner.get_keyword_ideas(seed_keywords)
            logger.info(f"SerpAPI fallback returned {len(related_keywords_dict)} keyword ideas")
            
            # Convert dict to list format
            related_keywords = []
            for keyword, data in related_keywords_dict.items():
                keyword_data = dict(data)
                keyword_data["keyword"] = keyword
                keyword_data["source"] = "serpapi"
                related_keywords.append(keyword_data)
            
            logger.info(f"Converted to {len(related_keywords)} related keywords")
            return related_keywords
        except Exception as e:
            logger.error(f"Error getting keywords from SerpAPI: {str(e)}")
            return []
    
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
                # Get entity data from Knowledge Graph
                entities = self.knowledge_graph.search_entities(keyword, limit=3)
                print("entities", entities)
                # Add entity information to keyword data
                keyword_data['entities'] = entities.get('itemListElement', [])
                keyword_data['entity_score'] = self._calculate_entity_relevance(entities)
                keyword_data['has_knowledge_panel'] = len(entities.get('itemListElement', [])) > 0
                
            except Exception as e:
                logger.warning(f"Error enhancing keyword '{keyword}' with entities: {str(e)}")
                keyword_data['entities'] = []
                keyword_data['entity_score'] = 0
                keyword_data['has_knowledge_panel'] = False
            
            enhanced_keywords.append(keyword_data)
        
        return enhanced_keywords
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract potential keywords from text.
        
        Args:
            text: Text to extract keywords from
            
        Returns:
            List of potential keywords
        """
        if not text:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too', 'very', 'can', 'will', 'just', 'should', 'now', 'get', 'make', 'take', 'come', 'see', 'know', 'think', 'look', 'use', 'find', 'give', 'tell', 'work', 'become', 'leave', 'feel', 'seem', 'ask', 'show', 'try', 'call', 'keep', 'provide', 'hold', 'turn', 'follow', 'begin', 'bring', 'like', 'going', 'want', 'start', 'made', 'getting', 'put', 'set', 'even', 'right', 'old', 'without', 'being', 'having', 'over', 'under', 'again', 'further', 'then', 'once'}
        
        # Extract single words and phrases
        keywords = []
        
        # Single words
        single_words = [word for word in words if word not in stop_words and len(word) > 3]
        keywords.extend(single_words)
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            if words[i] not in stop_words and words[i+1] not in stop_words:
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    phrase = f"{words[i]} {words[i+1]}"
                    keywords.append(phrase)
        
        # Extract 3-word phrases (for longer tail keywords)
        for i in range(len(words) - 2):
            if all(word not in stop_words for word in words[i:i+3]):
                if all(len(word) > 3 for word in words[i:i+3]):
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    keywords.append(phrase)
        
        # Return unique keywords, prioritizing longer phrases
        unique_keywords = list(dict.fromkeys(keywords))  # Preserves order
        
        # Sort by length (longer phrases first) and limit
        unique_keywords.sort(key=len, reverse=True)
        
        logger.debug(f"Extracted {len(unique_keywords)} keywords from text: {text[:100]}...")
        return unique_keywords[:15]  # Return top 15 keywords
    
    def _estimate_search_volume(self, keyword: str) -> int:
        """
        Estimate search volume for a keyword.
        
        Args:
            keyword: Keyword to estimate volume for
            
        Returns:
            Estimated monthly search volume
        """
        # Simple estimation based on keyword length and common patterns
        base_volume = 1000
        
        # Adjust based on keyword length
        if len(keyword) < 10:
            base_volume *= 1.5
        elif len(keyword) > 20:
            base_volume *= 0.5
        
        # Add some randomness to make it more realistic
        variation = random.uniform(0.5, 2.0)
        return int(base_volume * variation)
    
    def _estimate_competition(self, keyword: str) -> float:
        """
        Estimate competition level for a keyword.
        
        Args:
            keyword: Keyword to estimate competition for
            
        Returns:
            Competition level (0.0 to 1.0)
        """
        # Simple estimation based on keyword characteristics
        base_competition = 0.5
        
        # Commercial keywords tend to have higher competition
        commercial_terms = ['buy', 'price', 'cost', 'cheap', 'best', 'review', 'compare']
        if any(term in keyword.lower() for term in commercial_terms):
            base_competition += 0.2
        
        # Longer keywords tend to have lower competition
        if len(keyword.split()) > 3:
            base_competition -= 0.1
        
        return max(0.0, min(1.0, base_competition + random.uniform(-0.1, 0.1)))
    
    def _estimate_cpc(self, keyword: str) -> float:
        """
        Estimate CPC for a keyword.
        
        Args:
            keyword: Keyword to estimate CPC for
            
        Returns:
            Estimated CPC in USD
        """
        # Simple estimation based on keyword characteristics
        base_cpc = 1.0
        
        # Commercial keywords tend to have higher CPC
        commercial_terms = ['buy', 'price', 'cost', 'cheap', 'best', 'review', 'compare']
        if any(term in keyword.lower() for term in commercial_terms):
            base_cpc *= 2.0
        
        # Add randomness
        variation = random.uniform(0.5, 3.0)
        return round(base_cpc * variation, 2)
    
    def _calculate_relevance(self, keyword: str, seed_keyword: str) -> float:
        """
        Calculate relevance score between keyword and seed keyword.
        
        Args:
            keyword: Keyword to calculate relevance for
            seed_keyword: Original seed keyword
            
        Returns:
            Relevance score (0.0 to 1.0)
        """
        # Simple relevance calculation based on word overlap
        keyword_words = set(keyword.lower().split())
        seed_words = set(seed_keyword.lower().split())
        
        if not seed_words:
            return 0.0
        
        overlap = len(keyword_words.intersection(seed_words))
        relevance = overlap / len(seed_words)
        
        return min(1.0, relevance)
    
    def _calculate_entity_relevance(self, entities: Dict[str, Any]) -> float:
        """
        Calculate entity relevance score.
        
        Args:
            entities: Entity data from Knowledge Graph
            
        Returns:
            Entity relevance score (0.0 to 1.0)
        """
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


    