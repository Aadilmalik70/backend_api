"""
Test script for the real data implementation with Gemini API integration.

This script tests the functionality of the backend API with real data sources
and Gemini API integration for NLP tasks.
"""

import os
import sys
import json
import logging
import unittest
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import modules to test
from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal
from src.serp_feature_optimizer_real import SerpFeatureOptimizerReal
from src.content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
from src.competitor_analysis_real import CompetitorAnalysisReal
from src.utils.gemini_nlp_client import GeminiNLPClient

class RealDataImplementationTest(unittest.TestCase):
    """Test case for the real data implementation."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Get API keys from environment variables
        self.serpapi_key = os.getenv('SERPAPI_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize modules with API keys
        self.keyword_processor = KeywordProcessorEnhancedReal()
        self.serp_optimizer = SerpFeatureOptimizerReal(serpapi_key=self.serpapi_key)
        self.content_analyzer = ContentAnalyzerEnhancedReal(gemini_api_key=self.gemini_api_key)
        self.competitor_analyzer = CompetitorAnalysisReal(
            gemini_api_key=self.gemini_api_key,
            serpapi_key=self.serpapi_key
        )
    
    def test_gemini_nlp_client(self):
        """Test the Gemini NLP client."""
        logger.info("Testing Gemini NLP client")
        
        # Initialize client
        nlp_client = GeminiNLPClient(api_key=self.gemini_api_key)
        
        # Test text analysis
        text = "Google is a technology company based in Mountain View, California. It specializes in Internet-related services and products."
        analysis = nlp_client.analyze_text(text)
        
        # Verify analysis structure
        self.assertIsInstance(analysis, dict)
        self.assertIn("entities", analysis)
        self.assertIn("sentiment", analysis)
        self.assertIn("categories", analysis)
        
        # Test entity extraction
        entities = nlp_client.analyze_entities(text)
        self.assertIsInstance(entities, dict)
        self.assertIn("entities", entities)
        
        # Test sentiment analysis
        sentiment = nlp_client.analyze_sentiment(text)
        self.assertIsInstance(sentiment, dict)
        self.assertIn("sentiment", sentiment)
        
        # Test content analysis
        content = nlp_client.analyze_content(text)
        self.assertIsInstance(content, dict)
        
        logger.info("Gemini NLP client test passed")
    
    def test_keyword_processor(self):
        """Test the keyword processor with real data."""
        logger.info("Testing keyword processor with real data")
        
        # Process keywords
        keyword = "content marketing strategies"
        result = self.keyword_processor.process_keywords(keyword)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("seed_keywords", result)
        self.assertIn("related_keywords", result)
        self.assertIn("keyword_metrics", result)
        
        # Verify seed keywords
        self.assertIsInstance(result["seed_keywords"], list)
        self.assertGreater(len(result["seed_keywords"]), 0)
        
        # Verify related keywords
        self.assertIsInstance(result["related_keywords"], list)
        
        # Verify keyword metrics
        self.assertIsInstance(result["keyword_metrics"], list)
        
        logger.info("Keyword processor test passed")
    
    def test_serp_feature_optimizer(self):
        """Test the SERP feature optimizer with real data."""
        logger.info("Testing SERP feature optimizer with real data")
        
        # Generate SERP feature recommendations
        keyword = "content marketing strategies"
        result = self.serp_optimizer.generate_recommendations(keyword)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("keyword", result)
        self.assertIn("serp_features", result)
        self.assertIn("recommendations", result)
        
        # Verify keyword
        self.assertEqual(result["keyword"], keyword)
        
        # Verify SERP features
        self.assertIsInstance(result["serp_features"], list)
        
        # Verify recommendations
        self.assertIsInstance(result["recommendations"], list)
        
        logger.info("SERP feature optimizer test passed")
    
    def test_content_analyzer(self):
        """Test the content analyzer with real data."""
        logger.info("Testing content analyzer with real data")
        
        # Analyze URL
        url = "https://www.example.com"
        result = self.content_analyzer.analyze_url(url)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("url", result)
        self.assertIn("title", result)
        self.assertIn("word_count", result)
        self.assertIn("readability", result)
        self.assertIn("content_structure", result)
        self.assertIn("content_analysis", result)
        self.assertIn("content_quality", result)
        self.assertIn("seo_analysis", result)
        self.assertIn("recommendations", result)
        
        # Verify URL
        self.assertEqual(result["url"], url)
        
        # Verify content analysis
        self.assertIsInstance(result["content_analysis"], dict)
        self.assertIn("entities", result["content_analysis"])
        self.assertIn("sentiment", result["content_analysis"])
        self.assertIn("categories", result["content_analysis"])
        
        logger.info("Content analyzer test passed")
    
    def test_competitor_analyzer(self):
        """Test the competitor analyzer with real data."""
        logger.info("Testing competitor analyzer with real data")
        
        # Analyze competitors
        keyword = "content marketing strategies"
        result = self.competitor_analyzer.analyze_competitors(keyword, num_competitors=2)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("keyword", result)
        self.assertIn("competitors", result)
        self.assertIn("insights", result)
        
        # Verify keyword
        self.assertEqual(result["keyword"], keyword)
        
        # Verify competitors
        self.assertIsInstance(result["competitors"], list)
        
        # Verify insights
        self.assertIsInstance(result["insights"], dict)
        self.assertIn("content_length", result["insights"])
        self.assertIn("content_structure", result["insights"])
        self.assertIn("common_entities", result["insights"])
        self.assertIn("sentiment_trend", result["insights"])
        self.assertIn("topic_clusters", result["insights"])
        
        logger.info("Competitor analyzer test passed")
    
    def test_content_blueprint_generation(self):
        """Test content blueprint generation with real data."""
        logger.info("Testing content blueprint generation with real data")
        
        # Generate content blueprint
        keyword = "content marketing strategies"
        result = self.competitor_analyzer.generate_content_blueprint(keyword, num_competitors=2)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("keyword", result)
        self.assertIn("outline", result)
        self.assertIn("recommendations", result)
        self.assertIn("competitor_insights", result)
        
        # Verify keyword
        self.assertEqual(result["keyword"], keyword)
        
        # Verify outline
        self.assertIsInstance(result["outline"], dict)
        self.assertIn("title", result["outline"])
        self.assertIn("sections", result["outline"])
        
        # Verify recommendations
        self.assertIsInstance(result["recommendations"], list)
        
        logger.info("Content blueprint generation test passed")
    
    def test_api_process_endpoint(self):
        """Test the /api/process endpoint with real data."""
        logger.info("Testing /api/process endpoint with real data")
        
        # Create a test client
        from src.app_real import app
        from flask.testing import FlaskClient
        
        with app.test_client() as client:
            # Test data
            data = {
                "keyword": "content marketing strategies",
                "url": "https://www.example.com"
            }
            
            # Make request
            response = client.post('/api/process', json=data)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Parse response
            result = json.loads(response.data)
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("keyword_analysis", result)
            self.assertIn("serp_features", result)
            self.assertIn("content_analysis", result)
            self.assertIn("competitor_analysis", result)
            
            logger.info("API endpoint test passed")
    
    def test_api_blueprint_endpoint(self):
        """Test the /api/blueprint endpoint with real data."""
        logger.info("Testing /api/blueprint endpoint with real data")
        
        # Create a test client
        from src.app_real import app
        from flask.testing import FlaskClient
        
        with app.test_client() as client:
            # Test data
            data = {
                "keyword": "content marketing strategies"
            }
            
            # Make request
            response = client.post('/api/blueprint', json=data)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Parse response
            result = json.loads(response.data)
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("keyword", result)
            self.assertIn("outline", result)
            self.assertIn("recommendations", result)
            
            logger.info("API blueprint endpoint test passed")

if __name__ == '__main__':
    unittest.main()
