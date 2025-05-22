#!/bin/bash

# Create .env file for testing
echo "# Environment variables for testing
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id
SERPAPI_KEY=your_serpapi_key
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
" > .env

# Install Python dotenv package for loading environment variables
pip install python-dotenv

# Run the test suite
python test_real_implementation.py

# Exit with the test result status
exit $?
