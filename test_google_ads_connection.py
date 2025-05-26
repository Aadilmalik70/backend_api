import os
import logging
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_google_ads_api_connection():
    """
    Tests the connection to the Google Ads API using credentials from environment variables
    or a google-ads.yaml file.
    """
    try:
        # Attempt to load the client from environment variables or a yaml file.
        # Ensure your google-ads.yaml is in your home directory or configured via
        # GOOGLE_ADS_YAML_FILE environment variable.
        # Required fields in yaml or as environment variables (prefixed with GOOGLE_ADS_):
        #   developer_token, client_id, client_secret, refresh_token, login_customer_id, use_proto_plus
        logger.info("Attempting to initialize Google Ads API client...")
        
        # Option 1: Load from default YAML file or environment variables
        # Set use_proto_plus to True if not in YAML
        credentials = {
            key[len("GOOGLE_ADS_"):]: value 
            for key, value in os.environ.items() 
            if key.startswith("GOOGLE_ADS_")
        }
        if not credentials.get("developer_token"): # Basic check if env vars are set
             logger.info("Trying to load credentials from google-ads.yaml file.")
             # If not using env vars, client will try to load from default YAML path
             googleads_client = GoogleAdsClient.load_from_env() # Tries env then default YAML
        else:
            logger.info("Trying to load credentials from environment variables.")
            # Ensure use_proto_plus is set, GoogleAdsClient.load_from_dict expects it
            if 'use_proto_plus' not in credentials:
                credentials['use_proto_plus'] = "True" # As string, it will be converted
            
            # Convert string "True"/"False" to boolean for use_proto_plus if present
            if isinstance(credentials.get('use_proto_plus'), str):
                credentials['use_proto_plus'] = credentials['use_proto_plus'].lower() == 'true'

            # login_customer_id might be set with or without hyphens. API expects no hyphens.
            if 'login_customer_id' in credentials:
                credentials['login_customer_id'] = credentials['login_customer_id'].replace('-', '')
            
            googleads_client = GoogleAdsClient.load_from_dict(credentials)

        logger.info("Google Ads API client initialized successfully.")

        # Perform a simple API call to list accessible customers
        # This requires the login_customer_id to be a manager account if you want to list accounts,
        # or your own account ID if you're querying it directly.
        customer_service = googleads_client.get_service("CustomerService")
        logger.info("Attempting to list accessible customers (requires login_customer_id to be set)...")
        
        accessible_customers = customer_service.list_accessible_customers()
        
        if not accessible_customers.resource_names:
            logger.warning("No accessible customers found. This might be okay if the configured "
                           "login_customer_id is not a manager account or has no linked accounts. "
                           "However, the connection was successful.")
        else:
            logger.info("Successfully retrieved accessible customer accounts:")
            for resource_name in accessible_customers.resource_names:
                logger.info(f"- {resource_name}")
        
        logger.info("Google Ads API connection test successful!")
        return True

    except GoogleAdsException as ex:
        logger.error(
            f"Google Ads API connection test failed with GoogleAdsException: {ex.message}",
            exc_info=True,
        )
        for error in ex.failure.errors:
            logger.error(f"Error code: {error.error_code}")
            logger.error(f"Error message: {error.message}")
        return False
    except Exception as e:
        logger.error(f"Google Ads API connection test failed with an unexpected error: {str(e)}", exc_info=True)
        logger.error(
            "Please ensure your google-ads.yaml file is correctly configured and "
            "environment variables (GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, etc.) "
            "are set if you are not using a YAML file."
        )
        return False

if __name__ == "__main__":
    test_google_ads_api_connection()
