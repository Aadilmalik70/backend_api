"""
Gemini API Client for NLP tasks

This module provides integration with Google's Gemini API for natural language processing tasks.
"""

import os
import logging
import json
import random
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiNLPClient:
    """
    Gemini API client for NLP tasks.
    
    This class provides methods for natural language processing using Google's Gemini API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini API client.
        
        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        self.client = None
        
        # Try to initialize the client if API key is provided
        if api_key:
            try:
                # Import Gemini API library
                import google.generativeai as genai
                
                # Configure API key
                genai.configure(api_key=api_key)
                
                # Initialize client
                self.client = genai
                logger.info("Gemini API client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Gemini API client: {str(e)}")
                self.client = None
        else:
            logger.warning("Gemini API key not provided, using fallback analysis")
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: Prompt for content generation
            
        Returns:
            Generated content as string
        """
        logger.info(f"Generating content with prompt: {prompt[:50]}...")
        
        # If client is not initialized, use fallback
        if not self.client:
            logger.warning("Using fallback content generation")
            return self._generate_fallback_content(prompt)
        
        try:
            # Generate content using Gemini API
            model = self.client.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                return response.text
            else:
                # Handle different response formats
                return str(response)
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return self._generate_fallback_content(prompt)
    
    def _generate_fallback_content(self, prompt: str) -> str:
        """
        Generate fallback content when API is not available.
        
        Args:
            prompt: Prompt for content generation
            
        Returns:
            Fallback content as string
        """
        logger.warning(f"Using fallback content generation for prompt: {prompt[:50]}...")
        
        # Extract key information from prompt
        prompt_lower = prompt.lower()
        
        # Check if it's an outline request
        if "outline" in prompt_lower or "content blueprint" in prompt_lower:
            return self._generate_outline_fallback(prompt)
        
        # Check if it's a topic clusters request
        if "topic clusters" in prompt_lower:
            return self._generate_topic_clusters_fallback(prompt)
        
        # Default fallback response
        return """
        This is fallback content generated without the Gemini API.
        
        The content is based on general best practices and may not be specifically tailored to your query.
        Please provide a valid Gemini API key for more accurate and customized results.
        
        Key points:
        - This is placeholder content
        - It follows a general structure
        - It includes multiple paragraphs
        - It provides some generic information
        
        For better results, please configure the Gemini API integration.
        """
    
    def _generate_outline_fallback(self, prompt: str) -> str:
        """
        Generate fallback outline when API is not available.
        
        Args:
            prompt: Prompt for outline generation
            
        Returns:
            Fallback outline as string
        """
        # Extract keyword from prompt
        keyword_match = None
        for pattern in ['"(.*?)"', 'about "(.*?)"', 'for "(.*?)"', 'for an article about "(.*?)"']:
            import re
            match = re.search(pattern, prompt)
            if match:
                keyword_match = match.group(1)
                break
        
        keyword = keyword_match or "the topic"
        
        return f"""
        # Comprehensive Guide to {keyword.title()}
        
        ## Introduction to {keyword.title()}
        ### What is {keyword.title()}?
        - Definition and core concepts
        - Historical context and evolution
        - Importance in today's context
        
        ### Why {keyword.title()} Matters
        - Key benefits and advantages
        - Statistical evidence of effectiveness
        - Real-world applications
        
        ## Key Strategies for {keyword.title()}
        ### Strategy 1: Planning and Preparation
        - Step-by-step approach
        - Tools and resources needed
        - Common pitfalls to avoid
        
        ### Strategy 2: Implementation Techniques
        - Best practices for implementation
        - Case studies of successful implementation
        - Measuring effectiveness
        
        ## Advanced {keyword.title()} Techniques
        ### Optimization Methods
        - Fine-tuning your approach
        - Advanced tools and technologies
        - Performance indicators to track
        
        ### Integration with Other Systems
        - Complementary approaches
        - Creating a comprehensive framework
        - Synergy effects and benefits
        
        ## Future Trends in {keyword.title()}
        ### Emerging Technologies
        - Innovations on the horizon
        - Potential game-changers
        - Preparing for future developments
        
        ### Industry Predictions
        - Expert forecasts
        - Market trends and analysis
        - Opportunities for early adopters
        
        ## Conclusion
        ### Key Takeaways
        - Summary of main points
        - Action items for implementation
        - Resources for further learning
        """
    
    def _generate_topic_clusters_fallback(self, prompt: str) -> str:
        """
        Generate fallback topic clusters when API is not available.
        
        Args:
            prompt: Prompt for topic clusters generation
            
        Returns:
            Fallback topic clusters as string
        """
        # Extract keyword from prompt
        keyword_match = None
        for pattern in ['"(.*?)"', 'about "(.*?)"', 'for "(.*?)"']:
            import re
            match = re.search(pattern, prompt)
            if match:
                keyword_match = match.group(1)
                break
        
        keyword = keyword_match or "the topic"
        
        return f"""
        1. Core Concepts and Fundamentals of {keyword}
        2. Strategic Implementation and Best Practices
        3. Tools, Technologies, and Resources
        4. Case Studies and Real-World Applications
        5. Future Trends and Emerging Opportunities
        """
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using Gemini API.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing text: {text[:50]}...")
        
        # If client is not initialized, use fallback
        if not self.client:
            logger.warning("Using fallback analysis")
            return self._analyze_text_fallback(text)
        
        try:
            # Analyze text using Gemini API
            model = self.client.GenerativeModel('gemini-pro')
            
            # Create a structured prompt for analysis
            analysis_prompt = f"""
            Analyze the following text and provide a structured response with these components:
            1. Entities: Extract key entities (people, organizations, concepts, etc.)
            2. Sentiment: Determine overall sentiment (positive, negative, neutral)
            3. Categories: Classify the text into relevant categories
            4. Language: Identify the language
            
            Text to analyze:
            {text}
            
            Format your response as JSON with these keys: entities (array), sentiment (object with score and magnitude), categories (array), language (string).
            """
            
            response = model.generate_content(analysis_prompt)
            
            # Extract text from response
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)
            
            # Try to parse JSON from response
            try:
                # Extract JSON from response (it might be wrapped in markdown code blocks)
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response_text
                
                # Parse JSON
                result = json.loads(json_str)
                
                # Ensure required keys exist
                if "entities" not in result:
                    result["entities"] = []
                if "sentiment" not in result:
                    result["sentiment"] = {"score": 0, "magnitude": 0}
                if "categories" not in result:
                    result["categories"] = []
                if "language" not in result:
                    result["language"] = "en"
                
                return result
                
            except Exception as e:
                logger.error(f"Error parsing Gemini API response: {str(e)}")
                return self._analyze_text_fallback(text)
            
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return self._analyze_text_fallback(text)
    
    def _analyze_text_fallback(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using fallback methods when API is not available.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        logger.warning(f"Using fallback analysis for text: {text[:50]}...")
        
        # Simple text analysis without NLP API
        # Split into sentences and words
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        words = [w for w in text.split() if w.strip()]
        
        # Count words and sentences
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
                "magnitude": sentiment_magnitude,
                "overall": "positive" if sentiment_score > 0.05 else ("negative" if sentiment_score < -0.05 else "neutral")
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
