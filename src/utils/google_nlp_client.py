"""
Google NLP Client Module with Fallback

This module provides a client for Google's Natural Language API with fallback
functionality when credentials are not available.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleNLPClient:
    """
    Client for Google's Natural Language API with fallback functionality.
    
    This class provides methods for text analysis using Google's NLP API,
    with graceful fallback to basic analysis when credentials are not available.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Google NLP client.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON file
        """
        self.credentials_path = credentials_path
        self.client = None
        
        # Try to initialize the client if credentials are provided
        if credentials_path and os.path.exists(credentials_path):
            try:
                # Set environment variable for credentials
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
                
                # Import Google Cloud libraries
                from google.cloud import language_v1
                
                # Create client
                self.client = language_v1.LanguageServiceClient()
                logger.info("Google NLP client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Google NLP client: {str(e)}")
                self.client = None
        else:
            logger.warning("Google NLP credentials not provided, using fallback analysis")
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using Google's Natural Language API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing text: {text[:100]}...")
        
        # If client is not initialized, use fallback
        if not self.client:
            logger.warning("Using basic text analysis fallback")
            return self._basic_text_analysis(text)
        
        try:
            # Import Google Cloud libraries
            from google.cloud import language_v1
            
            # Create document
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )
            
            # Analyze entities
            entities = self.client.analyze_entities(document=document).entities
            
            # Analyze sentiment
            sentiment = self.client.analyze_sentiment(document=document).document_sentiment
            
            # Analyze syntax
            syntax = self.client.analyze_syntax(document=document)
            
            # Analyze categories (if available)
            try:
                categories = self.client.classify_text(document=document).categories
                category_results = [
                    {
                        "name": category.name,
                        "confidence": category.confidence
                    }
                    for category in categories
                ]
            except Exception as e:
                logger.warning(f"Error analyzing categories: {str(e)}")
                category_results = []
            
            # Compile results
            result = {
                "entities": [
                    {
                        "name": entity.name,
                        "type": language_v1.Entity.Type(entity.type_).name,
                        "salience": entity.salience,
                        "mentions": len(entity.mentions)
                    }
                    for entity in entities
                ],
                "sentiment": {
                    "score": sentiment.score,
                    "magnitude": sentiment.magnitude
                },
                "language": syntax.language_code,
                "categories": category_results,
                "tokens": len(syntax.tokens)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing text with Google NLP: {str(e)}")
            return self._basic_text_analysis(text)
    
    def _basic_text_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform basic text analysis as a fallback.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing basic analysis results
        """
        # Split text into words and sentences
        words = text.split()
        sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
        
        # Calculate basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / max(1, sentence_count)
        
        # Calculate word frequencies
        word_freq = {}
        stop_words = {'the', 'and', 'a', 'to', 'of', 'in', 'is', 'that', 'it', 'with', 'for', 'as', 'on', 'by', 'this', 'be', 'are', 'an', 'or', 'at', 'from'}
        for word in words:
            word = word.lower().strip('.,;:!?()[]{}"\'-')
            if word and word not in stop_words and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top entities (words) by frequency
        entities = []
        for word, count in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
            entities.append({
                "name": word,
                "type": "COMMON",
                "salience": count / max(1, word_count),
                "mentions": count
            })
        
        # Define simple positive and negative word sets for basic sentiment analysis
        positive_words = {'good', 'great', 'excellent', 'best', 'amazing', 'wonderful', 'fantastic', 'outstanding', 'superb', 'brilliant', 'awesome', 'perfect', 'positive', 'beneficial', 'better', 'success', 'successful', 'happy', 'glad', 'pleased', 'satisfied', 'enjoy', 'enjoyed', 'like', 'liked', 'love', 'loved', 'recommend', 'recommended', 'impressive', 'impressed'}
        
        negative_words = {'bad', 'worst', 'terrible', 'awful', 'horrible', 'poor', 'negative', 'harmful', 'worse', 'failure', 'failed', 'unhappy', 'sad', 'upset', 'dissatisfied', 'hate', 'hated', 'dislike', 'disliked', 'avoid', 'avoided', 'disappointing', 'disappointed', 'disappoints', 'disappoint'}
        
        positive_count = sum(1 for word in words if word.lower().strip('.,;:!?()[]{}"\'-') in positive_words)
        negative_count = sum(1 for word in words if word.lower().strip('.,;:!?()[]{}"\'-') in negative_words)
        
        # Calculate sentiment score (-1 to 1)
        if word_count > 0:
            sentiment_score = (positive_count - negative_count) / word_count
            sentiment_magnitude = (positive_count + negative_count) / word_count
        else:
            sentiment_score = 0
            sentiment_magnitude = 0
        
        # Compile results
        result = {
            "entities": entities,
            "sentiment": {
                "score": sentiment_score,
                "magnitude": sentiment_magnitude
            },
            "language": "en",  # Assume English
            "categories": [],  # Empty categories list for fallback
            "tokens": word_count
        }
        
        return result
    
    def analyze_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing entities analysis
        """
        # Use the full analysis and extract entities
        analysis = self.analyze_text(text)
        # Return as a dictionary, not just the list
        return {"entities": analysis["entities"]}
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing sentiment analysis
        """
        # Use the full analysis and extract sentiment
        analysis = self.analyze_text(text)
        # Return as a dictionary with the sentiment key
        return {"sentiment": analysis["sentiment"]}
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze content of text (alias for analyze_text).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        # This is an alias for analyze_text to maintain compatibility with content analyzer
        return self.analyze_text(text)
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text into categories.
        
        Args:
            text: Text to classify
            
        Returns:
            Dictionary containing categories analysis
        """
        # Use the full analysis and extract categories
        analysis = self.analyze_text(text)
        # Return as a dictionary, not just the list
        return {"categories": analysis["categories"]}
    
    def analyze_syntax(self, text: str) -> Dict[str, Any]:
        """
        Analyze syntax of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing syntax analysis
        """
        # Use the full analysis and extract relevant parts
        analysis = self.analyze_text(text)
        return {
            "language": analysis["language"],
            "tokens": analysis["tokens"]
        }
