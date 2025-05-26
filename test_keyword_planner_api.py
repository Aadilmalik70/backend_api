"""
Integration test for Google Keyword Planner API

This script tests the real Google Keyword Planner API integration
to ensure it works correctly with actual API credentials.
"""

import os
import json
import logging
from dotenv import load_dotenv
from src.utils.keyword_planner_api import KeywordPlannerAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_keyword_planner_api():
    """Test the Google Keyword Planner API integration with real credentials."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID"
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in a .env file or in your environment.")
        return False
    
    try:
        # Initialize the API client with environment variables
        api = KeywordPlannerAPI()
        
        # Test keyword ideas
        test_keywords = ["content marketing", "SEO strategy"]
        logger.info(f"Testing get_keyword_ideas with keywords: {test_keywords}")
        
        keyword_ideas = api.get_keyword_ideas(test_keywords)
        
        # Verify the response
        if not keyword_ideas:
            logger.error("No keyword ideas returned")
            return False
        
        logger.info(f"Successfully retrieved {len(keyword_ideas)} keyword ideas")
        
        # Print sample of the results
        sample_keyword = next(iter(keyword_ideas))
        logger.info(f"Sample keyword data for '{sample_keyword}':")
        logger.info(json.dumps(keyword_ideas[sample_keyword], indent=2))
        
        # Test related keywords
        logger.info(f"Testing get_related_keywords with keywords: {test_keywords}")
        
        related_keywords = api.get_related_keywords(test_keywords)
        
        # Verify the response
        if not related_keywords:
            logger.error("No related keywords returned")
            return False
        
        logger.info(f"Successfully retrieved {len(related_keywords)} related keywords")
        logger.info(f"Sample related keywords: {related_keywords[:5]}")
        
        # Test keyword metrics
        specific_keywords = test_keywords + related_keywords[:3]
        logger.info(f"Testing get_keyword_metrics with keywords: {specific_keywords}")
        
        keyword_metrics = api.get_keyword_metrics(specific_keywords)
        
        # Verify the response
        if not keyword_metrics:
            logger.error("No keyword metrics returned")
            return False
        
        logger.info(f"Successfully retrieved metrics for {len(keyword_metrics)} keywords")
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Google Keyword Planner API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_keyword_planner_api()
    print(f"Test {'succeeded' if success else 'failed'}")
