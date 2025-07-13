"""
Keyword Extractor Module

This module handles the extraction and processing of keywords from text input.
"""

import logging
import re
import random
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    Handles keyword extraction and related keyword generation.
    """
    
    def __init__(self):
        """Initialize the keyword extractor."""
        self.stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 
            'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 
            'before', 'after', 'above', 'below', 'between', 'among', 'this', 
            'that', 'these', 'those', 'what', 'which', 'who', 'when', 'where', 
            'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 
            'other', 'some', 'such', 'only', 'own', 'same', 'than', 'too', 
            'very', 'can', 'will', 'just', 'should', 'now', 'get', 'make', 
            'take', 'come', 'see', 'know', 'think', 'look', 'use', 'find', 
            'give', 'tell', 'work', 'become', 'leave', 'feel', 'seem', 'ask', 
            'show', 'try', 'call', 'keep', 'provide', 'hold', 'turn', 'follow', 
            'begin', 'bring', 'like', 'going', 'want', 'start', 'made', 
            'getting', 'put', 'set', 'even', 'right', 'old', 'without', 
            'being', 'having', 'over', 'under', 'again', 'further', 'then', 
            'once'
        }
    
    def extract_seed_keywords(self, input_text: str) -> List[str]:
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
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
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
        
        # Extract single words and phrases
        keywords = []
        
        # Single words
        single_words = [word for word in words if word not in self.stop_words and len(word) > 3]
        keywords.extend(single_words)
        
        # Extract 2-word phrases
        for i in range(len(words) - 1):
            if words[i] not in self.stop_words and words[i+1] not in self.stop_words:
                if len(words[i]) > 3 and len(words[i+1]) > 3:
                    phrase = f"{words[i]} {words[i+1]}"
                    keywords.append(phrase)
        
        # Extract 3-word phrases (for longer tail keywords)
        for i in range(len(words) - 2):
            if all(word not in self.stop_words for word in words[i:i+3]):
                if all(len(word) > 3 for word in words[i:i+3]):
                    phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                    keywords.append(phrase)
        
        # Return unique keywords, prioritizing longer phrases
        unique_keywords = list(dict.fromkeys(keywords))  # Preserves order
        
        # Sort by length (longer phrases first) and limit
        unique_keywords.sort(key=len, reverse=True)
        
        logger.debug(f"Extracted {len(unique_keywords)} keywords from text: {text[:100]}...")
        return unique_keywords[:15]  # Return top 15 keywords
    
    def get_keywords_from_google_search(self, seed_keywords: List[str], google_search_client) -> List[Dict[str, Any]]:
        """
        Extract keyword ideas from Google Custom Search.
        
        Args:
            seed_keywords: List of seed keywords
            google_search_client: Google search client instance
            
        Returns:
            List of keyword ideas from Google Search
        """
        keyword_ideas = []
        
        for seed_keyword in seed_keywords[:3]:  # Limit to 3 to avoid quota issues
            try:
                # Search for related terms
                search_results = google_search_client.search(seed_keyword, num_results=5)
                logger.info(f"Search results for '{seed_keyword}': {len(search_results.get('items', []))} items")
                
                if 'items' in search_results:
                    for item in search_results['items']:
                        # Extract potential keywords from title and snippet
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')
                        
                        # Simple keyword extraction
                        extracted_keywords = self.extract_keywords_from_text(title + ' ' + snippet)
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
    
    def get_keywords_from_serpapi(self, seed_keywords: List[str], serpapi_client) -> List[Dict[str, Any]]:
        """
        Get keyword ideas from SerpAPI (fallback method).
        
        Args:
            seed_keywords: List of seed keywords
            serpapi_client: SerpAPI client instance
            
        Returns:
            List of keyword ideas from SerpAPI
        """
        try:
            related_keywords_dict = serpapi_client.get_keyword_ideas(seed_keywords)
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
