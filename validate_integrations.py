"""
Integration Test for All Real Data Modules

This script tests the integration of all real data modules to ensure
they work correctly with actual API credentials and browser automation.
"""

import os
import json
import logging
from dotenv import load_dotenv
from src.utils.keyword_planner_api import GoogleKeywordPlannerAPI
from src.utils.serpapi_client import SerpApiClient
from src.utils.gemini_nlp_client import GeminiNLPClient
from src.utils.browser_content_scraper import BrowserContentScraper
from src.keyword_processor_enhanced_real import KeywordProcessorEnhanced
from src.serp_feature_optimizer_real import SerpFeatureOptimizerReal
from src.content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
from src.competitor_analysis_real import CompetitorAnalysisReal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_all_integrations():
    """Validate all real data integrations."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
        "SERPAPI_KEY",
        "GEMINI_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in a .env file or in your environment.")
        return False
    
    # Test each integration
    success = True
    
    # Test keyword planner API
    if not test_keyword_planner_api():
        success = False
    
    # Test SerpAPI
    if not test_serpapi():
        success = False
    
    # Test Gemini API
    if not test_gemini_api():
        success = False
    
    # Test browser scraper
    if not test_browser_scraper():
        success = False
    
    # Test enhanced modules
    if not test_enhanced_modules():
        success = False
    
    return success

def test_keyword_planner_api():
    """Test the Google Keyword Planner API integration."""
    logger.info("Testing Google Keyword Planner API integration...")
    
    try:
        # Initialize the API client
        print("KeywordPlannerAPI")
        api = GoogleKeywordPlannerAPI()
        
        # Test keyword ideas
        test_keywords = ["content marketing"]
        logger.info(f"Testing get_keyword_ideas with keywords: {test_keywords}")
        
        keyword_ideas = api.get_keyword_ideas(test_keywords)
        
        # Verify the response
        if not keyword_ideas:
            logger.error("No keyword ideas returned")
            return False
        
        logger.info(f"Successfully retrieved {len(keyword_ideas)} keyword ideas")
        logger.info("Google Keyword Planner API integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Google Keyword Planner API: {str(e)}")
        return False

def test_serpapi():
    """Test the SerpAPI integration."""
    logger.info("Testing SerpAPI integration...")
    
    try:
        # Initialize the API client
        api = SerpApiClient()
        
        # Test SERP analysis
        test_query = "content marketing"
        logger.info(f"Testing analyze_serp with query: {test_query}")
        
        serp_data = api.analyze_serp(test_query)
        
        # Verify the response
        if not serp_data:
            logger.error("No SERP data returned")
            return False
        
        logger.info("Successfully retrieved SERP data")
        logger.info("SerpAPI integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing SerpAPI: {str(e)}")
        return False

def test_gemini_api():
    """Test the Gemini API integration."""
    logger.info("Testing Gemini API integration...")
    
    try:
        # Initialize the API client
        api_key = os.environ.get("GEMINI_API_KEY")
        api = GeminiNLPClient(api_key=api_key)
        
        # Test content analysis
        test_text = "Google Gemini API is a powerful tool for content analysis and natural language processing."
        logger.info(f"Testing analyze_content with text: {test_text}")
        
        nlp_analysis = api.analyze_content(test_text)
        
        # Verify the response
        if not nlp_analysis:
            logger.error("No NLP analysis returned")
            return False
        
        logger.info("Successfully retrieved NLP analysis")
        logger.info("Gemini API integration test passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Gemini API: {str(e)}")
        return False

def test_browser_scraper():
    """Test the browser content scraper."""
    logger.info("Testing browser content scraper...")
    
    try:
        # Initialize the browser scraper
        with BrowserContentScraper() as scraper:
            # Test content scraping
            test_url = "https://www.example.com"
            logger.info(f"Testing scrape_content with URL: {test_url}")
            
            scraped_content = scraper.scrape_content(test_url)
            
            # Verify the response
            if not scraped_content:
                logger.error("No scraped content returned")
                return False
            
            logger.info("Successfully scraped content")
            logger.info("Browser content scraper test passed!")
            return True
        
    except Exception as e:
        logger.error(f"Error testing browser content scraper: {str(e)}")
        return False

def test_enhanced_modules():
    """Test the enhanced modules with real data."""
    logger.info("Testing enhanced modules with real data...")
    
    try:
        # Test keyword processor
        logger.info("Testing KeywordProcessorEnhanced...")
        keyword_processor = KeywordProcessorEnhanced()
        keyword_results = keyword_processor.process_keywords("content marketing")
        
        if not keyword_results:
            logger.error("No keyword processing results returned")
            return False
        
        logger.info("Successfully processed keywords")
        
        # Test SERP feature optimizer
        logger.info("Testing SerpFeatureOptimizerReal...")
        serp_optimizer = SerpFeatureOptimizerReal()
        serp_results = serp_optimizer.generate_recommendations("content marketing")
        
        if not serp_results:
            logger.error("No SERP optimization recommendations returned")
            return False
        
        logger.info("Successfully generated SERP recommendations")
        
        # Test content analyzer (limited test to avoid long execution)
        logger.info("Testing ContentAnalyzerEnhancedReal...")
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        content_analyzer = ContentAnalyzerEnhancedReal(gemini_api_key=gemini_api_key)
        content_results = content_analyzer.analyze_url("https://www.example.com")
        
        if not content_results:
            logger.error("No content analysis results returned")
            return False
        
        logger.info("Successfully analyzed content")
        
        # Test competitor analysis (limited test to avoid long execution)
        logger.info("Testing CompetitorAnalysisReal...")
        competitor_analyzer = CompetitorAnalysisReal(gemini_api_key=gemini_api_key)
        # Use a very small limit for testing
        competitor_results = competitor_analyzer.analyze_competitors("content marketing", limit=2)
        
        if not competitor_results:
            logger.error("No competitor analysis results returned")
            return False
        
        logger.info("Successfully analyzed competitors")
        
        logger.info("All enhanced modules tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing enhanced modules: {str(e)}")
        return False

if __name__ == "__main__":
    success = validate_all_integrations()
    print(f"Integration validation {'succeeded' if success else 'failed'}")
