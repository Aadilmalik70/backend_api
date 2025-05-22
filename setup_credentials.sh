#!/bin/bash

# Configuration script for API credentials
# This script creates a .env file with the necessary API credentials

echo "Setting up API credentials for backend_api"
echo "----------------------------------------"

# Create .env file
echo "Creating .env file..."
ENV_FILE="/home/ubuntu/backend_api/.env"

# Check if file exists and ask for confirmation to overwrite
if [ -f "$ENV_FILE" ]; then
    echo "Warning: .env file already exists. This will overwrite existing credentials."
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Prompt for SerpAPI key
echo
echo "Enter your SerpAPI key:"
read SERPAPI_KEY

# Prompt for Google Ads API credentials
echo
echo "Enter your Google Ads API credentials (press Enter to skip if not available):"
echo "Client ID:"
read GOOGLE_ADS_CLIENT_ID
echo "Client Secret:"
read GOOGLE_ADS_CLIENT_SECRET
echo "Developer Token:"
read GOOGLE_ADS_DEVELOPER_TOKEN
echo "Refresh Token:"
read GOOGLE_ADS_REFRESH_TOKEN
echo "Login Customer ID:"
read GOOGLE_ADS_LOGIN_CUSTOMER_ID

# Prompt for Google Cloud credentials file path
echo
echo "Enter the path to your Google Cloud credentials JSON file (press Enter to skip if not available):"
read GOOGLE_APPLICATION_CREDENTIALS

# Create .env file
cat > "$ENV_FILE" << EOL
# API Credentials for backend_api
# Generated on $(date)

# SerpAPI Key
SERPAPI_KEY=${SERPAPI_KEY}

# Google Ads API Credentials
GOOGLE_ADS_CLIENT_ID=${GOOGLE_ADS_CLIENT_ID}
GOOGLE_ADS_CLIENT_SECRET=${GOOGLE_ADS_CLIENT_SECRET}
GOOGLE_ADS_DEVELOPER_TOKEN=${GOOGLE_ADS_DEVELOPER_TOKEN}
GOOGLE_ADS_REFRESH_TOKEN=${GOOGLE_ADS_REFRESH_TOKEN}
GOOGLE_ADS_LOGIN_CUSTOMER_ID=${GOOGLE_ADS_LOGIN_CUSTOMER_ID}

# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
EOL

echo
echo "Credentials saved to $ENV_FILE"
echo
echo "To run the application with these credentials:"
echo "1. Install required dependencies: pip install -r src/utils/requirements.txt"
echo "2. Run the application: python src/main_real.py"
echo
echo "To run tests with these credentials:"
echo "python test_real_implementation.py"
echo
echo "Setup complete!"
