#!/bin/bash

# Environment Variables Check Script
# This script helps verify that all required API keys are properly configured

echo "🔍 Checking Environment Variables Configuration..."
echo "================================================"

# Function to check if an environment variable is set
check_env_var() {
    local var_name=$1
    local description=$2
    local is_required=$3
    
    if [ -n "${!var_name}" ]; then
        echo "✅ $var_name: Set (${description})"
        return 0
    else
        if [ "$is_required" = "required" ]; then
            echo "❌ $var_name: NOT SET (${description}) - REQUIRED"
            return 1
        else
            echo "⚠️  $var_name: NOT SET (${description}) - Optional"
            return 0
        fi
    fi
}

# Track if any required variables are missing
missing_required=0

echo ""
echo "🔑 API Keys:"
echo "------------"

# SerpAPI Key
if ! check_env_var "SERPAPI_KEY" "SerpAPI for search results" "required" && \
   ! check_env_var "SERPAPI_API_KEY" "SerpAPI alternative name" "optional"; then
    missing_required=1
fi

# Gemini API Key
if ! check_env_var "GEMINI_API_KEY" "Google Gemini AI" "required" && \
   ! check_env_var "GOOGLE_API_KEY" "Google API alternative name" "optional"; then
    missing_required=1
fi

echo ""
echo "🎯 Google Ads Credentials (Optional):"
echo "------------------------------------"

check_env_var "GOOGLE_ADS_DEVELOPER_TOKEN" "Google Ads API developer token" "optional"
check_env_var "GOOGLE_ADS_CLIENT_ID" "Google Ads OAuth client ID" "optional"
check_env_var "GOOGLE_ADS_CLIENT_SECRET" "Google Ads OAuth client secret" "optional"
check_env_var "GOOGLE_ADS_REFRESH_TOKEN" "Google Ads OAuth refresh token" "optional"
check_env_var "GOOGLE_ADS_LOGIN_CUSTOMER_ID" "Google Ads login customer ID" "optional"

echo ""
echo "📊 Summary:"
echo "----------"

if [ $missing_required -eq 0 ]; then
    echo "✅ All required environment variables are configured!"
    echo ""
    echo "🚀 You can now start the application with:"
    echo "   python src/app_real.py"
else
    echo "❌ Some required environment variables are missing!"
    echo ""
    echo "🛠️  To fix this, create a .env file with the following:"
    echo ""
    echo "# Required API Keys"
    echo "SERPAPI_KEY=your_serpapi_key_here"
    echo "GEMINI_API_KEY=your_gemini_api_key_here"
    echo ""
    echo "# Optional Google Ads Credentials"
    echo "GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token"
    echo "GOOGLE_ADS_CLIENT_ID=your_client_id"
    echo "GOOGLE_ADS_CLIENT_SECRET=your_client_secret"
    echo "GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token"
    echo "GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id"
    echo ""
    echo "📚 Get your API keys from:"
    echo "   • SerpAPI: https://serpapi.com/"
    echo "   • Gemini: https://makersuite.google.com/app/apikey"
    echo "   • Google Ads: https://developers.google.com/google-ads/api"
fi

echo ""
