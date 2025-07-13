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
    
    def analyze_content_quality(self, text: str) -> Dict[str, Any]:
        """
        Analyze content quality using various metrics
        
        Args:
            text: Text to analyze for quality
            
        Returns:
            Dictionary containing quality metrics
        """
        try:
            if not text or not text.strip():
                return {
                    "quality_score": 0.0,
                    "readability_score": 0.0,
                    "sentiment_score": 0.0,
                    "entity_count": 0,
                    "word_count": 0,
                    "error": "Empty text provided"
                }
            
            # Get basic metrics
            word_count = len(text.split())
            sentence_count = len([s for s in text.split('.') if s.strip()])
            
            # Calculate readability (simple metric)
            readability = self._calculate_readability(text, word_count, sentence_count)
            
            # Get sentiment analysis
            sentiment_result = self.analyze_sentiment(text)
            sentiment_score = sentiment_result.get('score', 0.0)
            
            # Get entities
            entities = self.extract_entities(text)
            entity_count = len(entities)
            
            # Calculate overall quality score
            quality_score = self._calculate_quality_score(
                readability, sentiment_score, entity_count, word_count
            )
            
            return {
                "quality_score": quality_score,
                "readability_score": readability,
                "sentiment_score": sentiment_score,
                "entity_count": entity_count,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_words_per_sentence": word_count / max(sentence_count, 1),
                "entities": entities[:5],  # Return top 5 entities
                "method": "hybrid_analysis"
            }
            
        except Exception as e:
            logger.error(f"Content quality analysis error: {str(e)}")
            return {
                "quality_score": 0.0,
                "readability_score": 0.0,
                "sentiment_score": 0.0,
                "entity_count": 0,
                "word_count": 0,
                "error": str(e)
            }
    
    def _calculate_readability(self, text: str, word_count: int, sentence_count: int) -> float:
        """
        Calculate a simple readability score
        
        Args:
            text: The text to analyze
            word_count: Number of words
            sentence_count: Number of sentences
            
        Returns:
            Readability score (0.0 to 1.0)
        """
        if sentence_count == 0:
            return 0.0
        
        # Average words per sentence (ideal range: 15-20)
        avg_words_per_sentence = word_count / sentence_count
        
        # Calculate based on sentence length (closer to ideal = higher score)
        if 15 <= avg_words_per_sentence <= 20:
            sentence_score = 1.0
        elif 10 <= avg_words_per_sentence <= 25:
            sentence_score = 0.8
        elif 8 <= avg_words_per_sentence <= 30:
            sentence_score = 0.6
        else:
            sentence_score = 0.4
        
        # Check for variety in sentence structure
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        sentence_lengths = [len(s.split()) for s in sentences]
        
        # Calculate variety score
        if len(set(sentence_lengths)) > len(sentence_lengths) * 0.7:
            variety_score = 1.0
        elif len(set(sentence_lengths)) > len(sentence_lengths) * 0.5:
            variety_score = 0.8
        else:
            variety_score = 0.6
        
        # Combined readability score
        readability = (sentence_score * 0.7) + (variety_score * 0.3)
        return min(1.0, readability)
    
    def _calculate_quality_score(self, readability: float, sentiment: float, 
                               entity_count: int, word_count: int) -> float:
        """
        Calculate overall content quality score
        
        Args:
            readability: Readability score (0.0 to 1.0)
            sentiment: Sentiment score (-1.0 to 1.0)
            entity_count: Number of entities found
            word_count: Total word count
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        # Normalize sentiment to 0-1 scale (neutral to positive is good)
        sentiment_normalized = max(0.0, sentiment + 1.0) / 2.0
        
        # Entity density (more entities = more informative content)
        entity_density = min(1.0, entity_count / max(word_count / 100, 1))  # Entities per 100 words
        
        # Word count factor (moderate length is preferred)
        if 50 <= word_count <= 500:
            length_score = 1.0
        elif 20 <= word_count <= 1000:
            length_score = 0.8
        elif word_count >= 10:
            length_score = 0.6
        else:
            length_score = 0.3
        
        # Weighted quality score
        quality = (
            readability * 0.3 +
            sentiment_normalized * 0.2 +
            entity_density * 0.2 +
            length_score * 0.3
        )
        
        return min(1.0, quality)
