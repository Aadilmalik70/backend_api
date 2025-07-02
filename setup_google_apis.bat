@echo off
REM Google APIs Setup Script for Windows
REM This script helps you set up Google APIs for your SEO application

echo 🚀 Google APIs Setup Script (Windows)
echo This will help you configure Google APIs to replace SerpAPI
echo ==========================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed
    echo 📥 Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip is required but not installed
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing required dependencies...
pip install -r requirements-google-apis.txt

if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo 📝 Creating .env file template...
    (
        echo # Google Cloud Credentials
        echo GOOGLE_APPLICATION_CREDENTIALS=./credentials/google-apis-credentials.json
        echo.
        echo # Google API Key ^(for Custom Search ^& Knowledge Graph^)
        echo GOOGLE_API_KEY=your_google_api_key_here
        echo.
        echo # Custom Search Engine ID
        echo GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here
        echo.
        echo # Search Console Site URL
        echo SEARCH_CONSOLE_SITE_URL=https://yourdomain.com
        echo.
        echo # Gemini API Key
        echo GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Migration Settings
        echo USE_GOOGLE_APIS=true
        echo FALLBACK_TO_SERPAPI=true
        echo MIGRATE_SERP_ANALYSIS=true
        echo MIGRATE_COMPETITOR_ANALYSIS=true
        echo MIGRATE_CONTENT_ANALYSIS=true
        echo MIGRATE_ENTITY_ANALYSIS=true
        echo.
        echo # Your existing SerpAPI key ^(for fallback^)
        echo SERPAPI_API_KEY=your_existing_serpapi_key
    ) > .env
    echo ✅ .env file created
    echo ⚠️ Please edit .env file with your actual API keys
) else (
    echo ✅ .env file already exists
)

REM Create credentials directory
if not exist credentials (
    echo 📁 Creating credentials directory...
    mkdir credentials
    echo ✅ Credentials directory created
)

REM Check if gcloud is installed
gcloud version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Google Cloud CLI is installed
    echo 📋 Next steps:
    echo    1. Run: gcloud auth login
    echo    2. Run: gcloud config set project YOUR_PROJECT_ID
    echo    3. Enable APIs: gcloud services enable searchconsole.googleapis.com customsearch.googleapis.com language.googleapis.com
) else (
    echo ⚠️ Google Cloud CLI not installed
    echo 📥 Install from: https://cloud.google.com/sdk/docs/install
)

echo.
echo 📖 Next Steps:
echo =============
echo 1. Follow GOOGLE_APIS_SETUP.md for detailed setup
echo 2. Configure your API keys in .env file
echo 3. Download service account credentials to ./credentials/
echo 4. Run: python verify_google_apis.py
echo 5. Test with: python examples/production_integration.py
echo.
echo 🎯 Goal: Replace SerpAPI with Google APIs for better data and lower costs!
echo ✅ Setup script completed!
echo.
pause
