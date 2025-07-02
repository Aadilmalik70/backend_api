#!/bin/bash

# Google APIs Setup Script
# This script helps you set up Google APIs for your SEO application

echo "🚀 Google APIs Setup Script"
echo "This will help you configure Google APIs to replace SerpAPI"
echo "=========================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

# Install dependencies
echo "📦 Installing required dependencies..."
pip3 install -r requirements-google-apis.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOL
# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-apis-credentials.json

# Google API Key (for Custom Search & Knowledge Graph)
GOOGLE_API_KEY=your_google_api_key_here

# Custom Search Engine ID
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here

# Search Console Site URL
SEARCH_CONSOLE_SITE_URL=https://yourdomain.com

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Migration Settings
USE_GOOGLE_APIS=true
FALLBACK_TO_SERPAPI=true
MIGRATE_SERP_ANALYSIS=true
MIGRATE_COMPETITOR_ANALYSIS=true
MIGRATE_CONTENT_ANALYSIS=true
MIGRATE_ENTITY_ANALYSIS=true

# Your existing SerpAPI key (for fallback)
SERPAPI_API_KEY=your_existing_serpapi_key
EOL
    echo "✅ .env file created"
    echo "⚠️ Please edit .env file with your actual API keys"
else
    echo "✅ .env file already exists"
fi

# Create credentials directory
if [ ! -d "credentials" ]; then
    echo "📁 Creating credentials directory..."
    mkdir -p credentials
    echo "✅ Credentials directory created"
fi

# Check if gcloud is installed
if command -v gcloud &> /dev/null; then
    echo "✅ Google Cloud CLI is installed"
    echo "📋 Next steps:"
    echo "   1. Run: gcloud auth login"
    echo "   2. Run: gcloud config set project YOUR_PROJECT_ID"
    echo "   3. Enable APIs: gcloud services enable searchconsole.googleapis.com customsearch.googleapis.com language.googleapis.com"
else
    echo "⚠️ Google Cloud CLI not installed"
    echo "📥 Install from: https://cloud.google.com/sdk/docs/install"
fi

echo ""
echo "📖 Next Steps:"
echo "============="
echo "1. Follow GOOGLE_APIS_SETUP.md for detailed setup"
echo "2. Configure your API keys in .env file"
echo "3. Download service account credentials to ./credentials/"
echo "4. Run: python verify_google_apis.py"
echo "5. Test with: python examples/production_integration.py"
echo ""
echo "🎯 Goal: Replace SerpAPI with Google APIs for better data and lower costs!"
echo "✅ Setup script completed!"
