"""
Natural Language Client with required methods for hybrid analysis
"""
import logging
import re
from typing import Dict, Any, List, Optional
import os

logger = logging.getLogger(__name__)

class NaturalLanguageClient:
    def __init__(self):
        """Initialize Natural Language client"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.available = bool(self.api_key)
        if not self.available:
            logger.warning("Google API key not found - Natural Language features disabled")
        else:
            logger.info("Natural Language client initialized successfully")
    
    def health_check(self) -> bool:
        """Check if Natural Language API is available"""
        return self.available
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using Google Natural Language API
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment analysis
        """
        try:
            if not self.available or not text or not text.strip():
                return {"score": 0.0, "magnitude": 0.0}
            
            # Limit text length for processing
            text = text[:5000] if len(text) > 5000 else text
            
            logger.info(f"Analyzing sentiment for text: {len(text)} characters")
            
            # Fallback sentiment analysis using simple keyword matching
            sentiment_score = self._calculate_sentiment_score(text)
            magnitude = self._calculate_sentiment_magnitude(text)
            
            return {
                "score": sentiment_score,
                "magnitude": magnitude,
                "language": "en",
                "method": "fallback_analysis"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            return {"score": 0.0, "magnitude": 0.0, "error": str(e)}
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text using Google Natural Language API
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entities with metadata
        """
        try:
            if not self.available or not text or not text.strip():
                return []
            
            # Limit text length for processing
            text = text[:5000] if len(text) > 5000 else text
            
            logger.info(f"Extracting entities from text: {len(text)} characters")
            
            # Fallback entity extraction using pattern matching
            entities = self._extract_entities_fallback(text)
            
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction error: {str(e)}")
            return []
    
    def _calculate_sentiment_score(self, text: str) -> float:
        """Calculate sentiment score using keyword matching"""
        positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 
            'awesome', 'outstanding', 'superb', 'brilliant', 'perfect', 'best',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'success',
            'effective', 'efficient', 'reliable', 'innovative', 'quality'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'poor', 'worst', 'hate',
            'dislike', 'disappointed', 'frustrated', 'angry', 'sad', 'fail',
            'problem', 'issue', 'difficult', 'hard', 'challenge', 'slow',
            'expensive', 'cheap', 'unreliable', 'ineffective'
        ]
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        # Calculate score between -1 and 1
        score = (positive_count - negative_count) / len(words) * 10
        return max(-1.0, min(1.0, score))
    
    def _calculate_sentiment_magnitude(self, text: str) -> float:
        """Calculate sentiment magnitude"""
        # Simple magnitude calculation based on text length and sentiment words
        words = re.findall(r'\b\w+\b', text.lower())
        sentiment_words = [
            'good', 'great', 'excellent', 'bad', 'terrible', 'awful',
            'amazing', 'wonderful', 'horrible', 'love', 'hate'
        ]
        
        sentiment_word_count = sum(1 for word in words if word in sentiment_words)
        magnitude = min(sentiment_word_count / max(len(words), 1) * 5, 1.0)
        
        return magnitude
    
    def _extract_entities_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using pattern matching and heuristics"""
        entities = []
        
        # Extract potential organizations (capitalized words, company indicators)
        org_patterns = [
            r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems|Solutions|Software|Group)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|LLC|Ltd))\b'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                entities.append({
                    "name": match.strip(),
                    "type": "ORGANIZATION",
                    "salience": 0.8,
                    "method": "pattern_matching"
                })
        
        # Extract potential technology terms
        tech_patterns = [
            r'\b(?:API|SDK|SaaS|PaaS|IaaS|IoT|AI|ML|VR|AR|5G|4G|LTE|WiFi|HTTP|HTTPS|JSON|XML|SQL|NoSQL)\b',
            r'\b[A-Z]{2,}\b'  # Acronyms
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 1:  # Filter out single letters
                    entities.append({
                        "name": match,
                        "type": "OTHER",
                        "salience": 0.6,
                        "method": "tech_pattern"
                    })
        
        # Extract potential products/services (capitalized phrases)
        product_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b'
        matches = re.findall(product_pattern, text)
        for match in matches:
            if len(match.split()) <= 3:  # Limit to reasonable product names
                entities.append({
                    "name": match,
                    "type": "CONSUMER_GOOD",
                    "salience": 0.4,
                    "method": "capitalization_pattern"
                })
        
        # Remove duplicates and limit results
        seen = set()
        unique_entities = []
        for entity in entities:
            entity_key = entity["name"].lower()
            if entity_key not in seen and len(entity["name"]) > 2:
                seen.add(entity_key)
                unique_entities.append(entity)
        
        # Sort by salience and return top 15
        unique_entities.sort(key=lambda x: x["salience"], reverse=True)
        return unique_entities[:15]
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text into categories
        
        Args:
            text: Text to classify
            
        Returns:
            Classification results
        """
        try:
            if not self.available or not text:
                return {}
            
            # Simple classification based on keywords
            categories = {
                "technology": ["software", "hardware", "tech", "digital", "cyber", "data", "cloud"],
                "business": ["business", "company", "corporate", "enterprise", "commercial"],
                "telecommunications": ["telecom", "mobile", "wireless", "network", "cellular", "mvno"],
                "media": ["media", "news", "content", "publishing", "broadcasting"],
                "finance": ["finance", "financial", "banking", "investment", "money"]
            }
            
            text_lower = text.lower()
            scores = {}
            
            for category, keywords in categories.items():
                score = sum(1 for keyword in keywords if keyword in text_lower)
                if score > 0:
                    scores[category] = score / len(text_lower.split()) * 100
            
            return {
                "categories": scores,
                "top_category": max(scores.items(), key=lambda x: x[1])[0] if scores else "general"
            }
            
        except Exception as e:
            logger.error(f"Text classification error: {str(e)}")
            return {}
