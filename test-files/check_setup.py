#!/usr/bin/env python3
"""
SERP Strategist Setup Checker

This script checks if your environment is properly configured for the SERP Strategist API.
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking SERP Strategist API Setup...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Required variables
    required_vars = {
        'SERPAPI_KEY': {
            'description': 'SerpAPI for search results',
            'url': 'https://serpapi.com/',
            'critical': False
        },
        'GEMINI_API_KEY': {
            'description': 'Google Gemini AI for content analysis',
            'url': 'https://aistudio.google.com/',
            'critical': True
        },
        'GOOGLE_API_KEY': {
            'description': 'Google APIs (Custom Search, etc.)',
            'url': 'https://console.cloud.google.com/',
            'critical': False
        }
    }
    
    # Optional variables
    optional_vars = {
        'GOOGLE_ADS_CLIENT_ID': 'Google Ads API client ID',
        'GOOGLE_ADS_CLIENT_SECRET': 'Google Ads API client secret',
        'GOOGLE_ADS_DEVELOPER_TOKEN': 'Google Ads API developer token',
        'GOOGLE_ADS_REFRESH_TOKEN': 'Google Ads API refresh token',
        'GOOGLE_ADS_LOGIN_CUSTOMER_ID': 'Google Ads API customer ID',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID': 'Google Custom Search Engine ID'
    }
    
    missing_critical = []
    missing_optional = []
    configured = []
    
    print("📋 Required API Keys:")
    for var, info in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Configured")
            configured.append(var)
        else:
            print(f"  ❌ {var}: Missing")
            print(f"     Description: {info['description']}")
            print(f"     Get it from: {info['url']}")
            if info['critical']:
                missing_critical.append(var)
            else:
                missing_optional.append(var)
    
    print("\n📋 Optional API Keys:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: Configured")
            configured.append(var)
        else:
            print(f"  ⚠️  {var}: Not configured")
            print(f"     Description: {description}")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"  ✅ Configured: {len(configured)} API keys")
    print(f"  ❌ Missing Critical: {len(missing_critical)} API keys")
    print(f"  ⚠️  Missing Optional: {len(missing_optional)} API keys")
    
    if missing_critical:
        print("\n🚨 CRITICAL ISSUES:")
        for var in missing_critical:
            print(f"  - {var} is required for basic functionality")
        print("\n💡 The API will not work properly without these keys.")
        return False
    
    if missing_optional:
        print("\n⚠️  OPTIONAL IMPROVEMENTS:")
        for var in missing_optional:
            print(f"  - {var} would enable enhanced features")
        print("\n💡 The API will work with fallback/mock data for these features.")
    
    if not missing_critical and not missing_optional:
        print("\n🎉 Perfect! All API keys are configured.")
        return True
    
    print("\n📝 How to fix:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your API keys to the .env file")
    print("  3. Restart the API server")
    print("  4. Run this script again to verify")
    
    return len(missing_critical) == 0

def check_dependencies():
    """Check if required Python packages are installed."""
    print("\n🔍 Checking Python Dependencies...")
    print("=" * 50)
    
    required_packages = [
        'flask',
        'requests',
        'beautifulsoup4',
        'google-generativeai',
        'python-dotenv',
        'sqlalchemy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}: Installed")
        except ImportError:
            print(f"  ❌ {package}: Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🚨 Missing packages: {', '.join(missing_packages)}")
        print("💡 Install them with: pip install -r requirements.txt")
        return False
    
    print("\n🎉 All required packages are installed!")
    return True

def test_api_connection():
    """Test basic API functionality."""
    print("\n🔍 Testing API Connection...")
    print("=" * 50)
    
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("  ✅ API server is running and responding")
            data = response.json()
            print(f"  📊 Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"  ❌ API server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ Cannot connect to API server")
        print("  💡 Make sure the server is running: python src/main.py")
        return False
    except Exception as e:
        print(f"  ❌ Error testing API: {e}")
        return False

def main():
    """Main setup checker function."""
    print("🚀 SERP Strategist API Setup Checker")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check environment
    env_ok = check_environment()
    
    # Test API if server is running
    if deps_ok and env_ok:
        api_ok = test_api_connection()
    else:
        api_ok = False
    
    print("\n" + "=" * 50)
    print("🎯 Final Status:")
    
    if deps_ok and env_ok and api_ok:
        print("🎉 Everything is working perfectly!")
        print("✅ Dependencies: OK")
        print("✅ Environment: OK") 
        print("✅ API Connection: OK")
        print("\n🚀 Ready to use SERP Strategist API!")
    elif deps_ok and env_ok:
        print("⚠️  Setup is mostly complete!")
        print("✅ Dependencies: OK")
        print("✅ Environment: OK")
        print("❌ API Connection: Failed")
        print("\n💡 Start the API server: python src/main.py")
    else:
        print("❌ Setup needs attention!")
        print(f"{'✅' if deps_ok else '❌'} Dependencies: {'OK' if deps_ok else 'Missing packages'}")
        print(f"{'✅' if env_ok else '❌'} Environment: {'OK' if env_ok else 'Missing API keys'}")
        print("❌ API Connection: Not tested")
        print("\n💡 Fix the issues above and try again.")

if __name__ == "__main__":
    main()
