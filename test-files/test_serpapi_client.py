"""
Integration test for SerpAPI client

This script tests the real SerpAPI integration
to ensure it works correctly with actual API credentials.
"""

import os
import json
import logging
from dotenv import load_dotenv
from src.utils.serpapi_client import SerpApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_serpapi_client():
    """Test the SerpAPI client integration with real credentials."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Check if required environment variables are set
    if not os.environ.get("SERPAPI_KEY"):
        logger.error("Missing required environment variable: SERPAPI_KEY")
        logger.error("Please set this variable in a .env file or in your environment.")
        return False
    
    try:
        # Initialize the API client with environment variables
        api = SerpApiClient()
        
        # Test SERP analysis
        test_query = "content marketing strategies"
        logger.info(f"Testing analyze_serp with query: {test_query}")
        
        serp_data = api.analyze_serp(test_query)
        
        # Verify the response
        if not serp_data:
            logger.error("No SERP data returned")
            return False
        
        logger.info("Successfully retrieved SERP data")
        
        # Check for organic results
        if "organic_results" not in serp_data or not serp_data["organic_results"]:
            logger.error("No organic results found in SERP data")
            return False
        
        logger.info(f"Found {len(serp_data['organic_results'])} organic results")
        
        # Check for SERP features
        if "features" not in serp_data:
            logger.error("No features found in SERP data")
            return False
        
        logger.info(f"Found {len(serp_data['features'])} SERP features")
        logger.info(f"Features present: {', '.join(serp_data['features'].keys())}")
        
        # Test get_top_competitors
        logger.info(f"Testing get_top_competitors with query: {test_query}")
        
        competitors = api.get_top_competitors(test_query)
        
        # Verify the response
        if not competitors:
            logger.error("No competitors returned")
            return False
        
        logger.info(f"Successfully retrieved {len(competitors)} competitors")
        logger.info(f"Top competitor: {competitors[0]['title']} ({competitors[0]['url']})")
        
        # Test get_serp_features
        logger.info(f"Testing get_serp_features with query: {test_query}")
        
        serp_features = api.get_serp_features(test_query)
        
        # Verify the response
        if not serp_features:
            logger.error("No SERP features returned")
            return False
        
        logger.info(f"Successfully retrieved {len(serp_features)} SERP features")
        
        logger.info("All tests passed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing SerpAPI client: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_serpapi_client()
    print(f"Test {'succeeded' if success else 'failed'}")
