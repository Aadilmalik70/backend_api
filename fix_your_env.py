"""
Automated fix for your specific .env file issues
This script will fix the problems found in your configuration
"""

import os
import re
from pathlib import Path

def fix_env_file():
    """Fix the specific issues in the .env file"""
    print("🔧 Fixing .env file issues...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    fixes_made = []
    
    # Fix 1: Correct the credentials path
    old_path_pattern = r'GOOGLE_APPLICATION_CREDENTIALS=C:\\Users\\oj\\Desktop\\projecackend_api'
    new_path = 'GOOGLE_APPLICATION_CREDENTIALS=C:\\Users\\oj\\Desktop\\project\\backend_api\\credentials\\google-apis-credentials.json'
    
    if re.search(old_path_pattern, content):
        content = re.sub(old_path_pattern, new_path, content)
        fixes_made.append("✅ Fixed credentials file path")
    
    # Fix 2: Remove duplicate GEMINI_API_KEY line if it exists
    lines = content.split('\n')
    new_lines = []
    gemini_key_found = False
    
    for line in lines:
        if line.startswith('GEMINI_API_KEY='):
            if not gemini_key_found:
                # Keep the first occurrence
                new_lines.append(line)
                gemini_key_found = True
                fixes_made.append("✅ Removed duplicate GEMINI_API_KEY")
            # Skip subsequent occurrences
        else:
            new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # Fix 3: Add warning comment about Custom Search Engine ID
    if 'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="AIzaSy' in content:
        content = content.replace(
            'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="AIzaSyDGBM56i_W4YD8TrAtnSaHAe1uu8oTp4xU"',
            '# WRONG: GOOGLE_CUSTOM_SEARCH_ENGINE_ID="AIzaSyDGBM56i_W4YD8TrAtnSaHAe1uu8oTp4xU"\n' +
            '# The above is an API key, not a Search Engine ID!\n' +
            '# Create your Custom Search Engine at: https://programmablesearchengine.google.com\n' +
            'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="YOUR_SEARCH_ENGINE_ID_HERE"'
        )
        fixes_made.append("✅ Fixed Custom Search Engine ID (needs to be created)")
    
    # Write the fixed content back
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Fixed .env file with {len(fixes_made)} changes:")
    for fix in fixes_made:
        print(f"   {fix}")
    
    return True

def create_service_account_instructions():
    """Create step-by-step instructions for service account"""
    instructions = """
# 🔑 MISSING: Service Account Credentials File

Your .env file points to: credentials/google-apis-credentials.json
But this file doesn't exist yet.

## Step-by-Step to Get Service Account Credentials:

### 1. Go to Google Cloud Console
https://console.cloud.google.com

### 2. Create or Select Project
- Click project dropdown at top
- Create new project OR select existing project
- Note your PROJECT_ID

### 3. Enable Required APIs
- Go to "APIs & Services" > "Library"
- Search and enable these APIs:
  ✅ Custom Search API
  ✅ Knowledge Graph Search API  
  ✅ Google Search Console API
  ✅ Cloud Natural Language API

### 4. Create Service Account
- Go to "IAM & Admin" > "Service Accounts"
- Click "Create Service Account"
- Name: google-apis-seo
- Description: Service account for SEO Google APIs
- Click "Create and Continue"
- Skip roles for now, click "Done"

### 5. Generate JSON Key
- Click on your new service account
- Go to "Keys" tab
- Click "Add Key" > "Create New Key"
- Select "JSON" format
- Click "Create"
- File will download automatically

### 6. Save the File
- Rename downloaded file to: google-apis-credentials.json
- Move it to: C:\\Users\\oj\\Desktop\\project\\backend_api\\credentials\\google-apis-credentials.json

### 7. Add to Search Console
- Go to https://search.google.com/search-console
- Make sure https://www.serpstrategists.com/ is verified
- Go to Settings > Users and permissions
- Add user: [SERVICE_ACCOUNT_EMAIL]@[PROJECT_ID].iam.gserviceaccount.com
- Give "View" permission

## ⚠️ IMPORTANT: Create Custom Search Engine

Your current GOOGLE_CUSTOM_SEARCH_ENGINE_ID is wrong (it's an API key, not Search Engine ID)

### Create Custom Search Engine:
1. Go to: https://programmablesearchengine.google.com
2. Click "Add" to create new search engine
3. Choose "Search the entire web"
4. Create the search engine
5. Get your Search Engine ID (format: 017576662512468239146:omuauf_lfve)
6. Replace YOUR_SEARCH_ENGINE_ID_HERE in .env file

Once you have both files, run: python verify_google_apis.py
"""
    
    with open('SERVICE_ACCOUNT_SETUP.md', 'w') as f:
        f.write(instructions)
    
    print("📝 Created SERVICE_ACCOUNT_SETUP.md with detailed instructions")

def check_current_status():
    """Check what's working and what's not"""
    print("\n📊 Current Status Check:")
    
    # Check environment variables
    env_vars = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID'),
        'GOOGLE_APPLICATION_CREDENTIALS': os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        'SERPAPI_API_KEY': os.getenv('SERPAPI_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
    }
    
    for var, value in env_vars.items():
        if value and value != "YOUR_SEARCH_ENGINE_ID_HERE":
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ❌ {var}: Missing or placeholder")
    
    # Check credentials file
    creds_path = Path('credentials/google-apis-credentials.json')
    if creds_path.exists():
        print("   ✅ Service account file: Found")
    else:
        print("   ❌ Service account file: Missing")
    
    # Check SerpAPI dependency
    try:
        import googleapiclient
        print("   ✅ Google API Client: Installed")
    except ImportError:
        print("   ❌ Google API Client: Not installed")
    
    try:
        from serpapi import GoogleSearch
        print("   ✅ SerpAPI: Installed")
    except ImportError:
        print("   ❌ SerpAPI: Not installed (pip install google-search-results)")

def main():
    """Main fix function"""
    print("🛠️ Automated Fix for Your Google APIs Setup")
    print("=" * 50)
    
    # Fix the .env file
    fix_env_file()
    
    # Create setup instructions
    create_service_account_instructions()
    
    # Check current status
    check_current_status()
    
    print("\n" + "=" * 50)
    print("🎯 Next Steps:")
    print("1. Follow instructions in SERVICE_ACCOUNT_SETUP.md")
    print("2. Download service account JSON file")
    print("3. Create Custom Search Engine")
    print("4. Install missing dependency: pip install google-search-results")
    print("5. Run: python verify_google_apis.py")
    
    print("\n💡 Quick test with what you have:")
    print("   pip install google-search-results")
    print("   python verify_google_apis.py")

if __name__ == "__main__":
    main()
