@echo off
REM Environment Variables Check Script for Windows
REM This script helps verify that all required API keys are properly configured

echo 🔍 Checking Environment Variables Configuration...
echo ================================================

set missing_required=0

echo.
echo 🔑 API Keys:
echo ------------

REM Check SerpAPI Key
if defined SERPAPI_KEY (
    echo ✅ SERPAPI_KEY: Set ^(SerpAPI for search results^)
) else if defined SERPAPI_API_KEY (
    echo ✅ SERPAPI_API_KEY: Set ^(SerpAPI alternative name^)
) else (
    echo ❌ SERPAPI_KEY: NOT SET ^(SerpAPI for search results^) - REQUIRED
    set missing_required=1
)

REM Check Gemini API Key
if defined GEMINI_API_KEY (
    echo ✅ GEMINI_API_KEY: Set ^(Google Gemini AI^)
) else if defined GOOGLE_API_KEY (
    echo ✅ GOOGLE_API_KEY: Set ^(Google API alternative name^)
) else (
    echo ❌ GEMINI_API_KEY: NOT SET ^(Google Gemini AI^) - REQUIRED
    set missing_required=1
)

echo.
echo 🎯 Google Ads Credentials ^(Optional^):
echo ------------------------------------

if defined GOOGLE_ADS_DEVELOPER_TOKEN (
    echo ✅ GOOGLE_ADS_DEVELOPER_TOKEN: Set ^(Google Ads API developer token^)
) else (
    echo ⚠️  GOOGLE_ADS_DEVELOPER_TOKEN: NOT SET ^(Google Ads API developer token^) - Optional
)

if defined GOOGLE_ADS_CLIENT_ID (
    echo ✅ GOOGLE_ADS_CLIENT_ID: Set ^(Google Ads OAuth client ID^)
) else (
    echo ⚠️  GOOGLE_ADS_CLIENT_ID: NOT SET ^(Google Ads OAuth client ID^) - Optional
)

if defined GOOGLE_ADS_CLIENT_SECRET (
    echo ✅ GOOGLE_ADS_CLIENT_SECRET: Set ^(Google Ads OAuth client secret^)
) else (
    echo ⚠️  GOOGLE_ADS_CLIENT_SECRET: NOT SET ^(Google Ads OAuth client secret^) - Optional
)

if defined GOOGLE_ADS_REFRESH_TOKEN (
    echo ✅ GOOGLE_ADS_REFRESH_TOKEN: Set ^(Google Ads OAuth refresh token^)
) else (
    echo ⚠️  GOOGLE_ADS_REFRESH_TOKEN: NOT SET ^(Google Ads OAuth refresh token^) - Optional
)

if defined GOOGLE_ADS_LOGIN_CUSTOMER_ID (
    echo ✅ GOOGLE_ADS_LOGIN_CUSTOMER_ID: Set ^(Google Ads login customer ID^)
) else (
    echo ⚠️  GOOGLE_ADS_LOGIN_CUSTOMER_ID: NOT SET ^(Google Ads login customer ID^) - Optional
)

echo.
echo 📊 Summary:
echo ----------

if %missing_required%==0 (
    echo ✅ All required environment variables are configured!
    echo.
    echo 🚀 You can now start the application with:
    echo    python src/app_real.py
) else (
    echo ❌ Some required environment variables are missing!
    echo.
    echo 🛠️  To fix this, create a .env file with the following:
    echo.
    echo # Required API Keys
    echo SERPAPI_KEY=your_serpapi_key_here
    echo GEMINI_API_KEY=your_gemini_api_key_here
    echo.
    echo # Optional Google Ads Credentials
    echo GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
    echo GOOGLE_ADS_CLIENT_ID=your_client_id
    echo GOOGLE_ADS_CLIENT_SECRET=your_client_secret
    echo GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
    echo GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id
    echo.
    echo 📚 Get your API keys from:
    echo    • SerpAPI: https://serpapi.com/
    echo    • Gemini: https://makersuite.google.com/app/apikey
    echo    • Google Ads: https://developers.google.com/google-ads/api
)

echo.
pause
