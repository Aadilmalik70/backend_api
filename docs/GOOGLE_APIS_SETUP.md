# Google APIs Integration Setup Guide

## 🚀 Quick Start - Get Real Data (No More Mock Data!)

Your current code returns mock/sample data because the APIs aren't properly configured. Follow this guide to get real data.

## 1. Install Required Dependencies

```bash
pip install google-cloud-language==2.12.0
pip install google-api-python-client==2.108.0
pip install google-auth==2.23.4
pip install google-generativeai==0.3.2
pip install requests==2.31.0
```

## 2. Google Cloud Project Setup

### A. Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create new project: "seo-google-apis"
3. Note your PROJECT_ID

### B. Enable Required APIs
```bash
# Install gcloud CLI first: https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable searchconsole.googleapis.com
gcloud services enable customsearch.googleapis.com
gcloud services enable kgsearch.googleapis.com
gcloud services enable language.googleapis.com
```

### C. Create Service Account
```bash
# Create service account
gcloud iam service-accounts create google-apis-seo \
    --description="Service account for SEO Google APIs" \
    --display-name="Google APIs SEO"

# Create key file
gcloud iam service-accounts keys create ./credentials/google-apis-credentials.json \
    --iam-account=google-apis-seo@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## 3. Get API Keys

### A. Google API Key (Custom Search & Knowledge Graph)
1. Go to https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "API Key"
3. Restrict key to specific APIs:
   - Custom Search API
   - Knowledge Graph Search API
4. Copy the API key

### B. Gemini API Key
1. Go to https://makersuite.google.com/app/apikey
2. Create new API key
3. Copy the key

## 4. Configure Search Console

### A. Verify Your Domain
1. Go to https://search.google.com/search-console
2. Add property (your domain)
3. Verify ownership

### B. Grant Service Account Access
1. In Search Console → Settings → Users and permissions
2. Add user: `google-apis-seo@YOUR_PROJECT_ID.iam.gserviceaccount.com`
3. Grant "View" permission

## 5. Setup Custom Search Engine

### A. Create Search Engine
1. Go to https://programmablesearchengine.google.com
2. Click "Add" → Create new search engine
3. Choose "Search the entire web"
4. Get Search Engine ID (format: `017576662512468239146:omuauf_lfve`)

## 6. Environment Configuration

Create/update your `.env` file with these variables:

```env
# Google Cloud Credentials (absolute path)
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\oj\Desktop\project\backend_api\credentials\google-apis-credentials.json

# Google API Key
GOOGLE_API_KEY=AIzaSyD...your_api_key_here

# Custom Search Engine ID
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=017576662512468239146:your_search_engine_id

# Search Console Site URL
SEARCH_CONSOLE_SITE_URL=https://yourdomain.com

# Gemini API Key
GEMINI_API_KEY=AIzaSyA...your_gemini_key_here

# Migration Settings (set to true for real data)
USE_GOOGLE_APIS=true
FALLBACK_TO_SERPAPI=true
MIGRATE_SERP_ANALYSIS=true
MIGRATE_COMPETITOR_ANALYSIS=true
MIGRATE_CONTENT_ANALYSIS=true
MIGRATE_ENTITY_ANALYSIS=true

# Your existing SerpAPI key (fallback)
SERPAPI_API_KEY=your_existing_serpapi_key
```

## 7. Test Your Setup

Run the verification script (created in next step) to test all APIs.

## 📋 Checklist

- [ ] Google Cloud project created
- [ ] APIs enabled in Google Cloud
- [ ] Service account created and key downloaded
- [ ] API keys obtained
- [ ] Domain verified in Search Console
- [ ] Service account added to Search Console
- [ ] Custom Search Engine created
- [ ] Environment variables configured
- [ ] Dependencies installed
- [ ] Verification script run successfully

## 🔧 Troubleshooting

### Mock Data Still Appearing?
- Check environment variables are loaded correctly
- Verify credentials file path exists
- Run health check script
- Check API quotas in Google Cloud Console

### API Errors?
- Verify APIs are enabled in Google Cloud
- Check service account permissions
- Verify API keys are not restricted incorrectly
- Check quotas and billing

### Search Console No Data?
- Domain must be verified and have data
- Service account needs "View" permission
- Wait 24-48 hours for data to appear after setup
