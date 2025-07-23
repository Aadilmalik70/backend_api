#!/usr/bin/env python3
"""
SerpAPI Rate Limit Monitor

This script helps you monitor your SerpAPI usage and avoid rate limits.
"""

import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_serpapi_account():
    """Check SerpAPI account status and usage."""
    print("📊 Checking SerpAPI Account Status")
    print("=" * 50)
    
    api_key = os.getenv('SERPAPI_KEY') or os.getenv('SERPAPI_API_KEY')
    if not api_key:
        print("❌ SerpAPI key not found in environment variables")
        return False
    
    try:
        # Check account status
        account_url = f"https://serpapi.com/account?api_key={api_key}"
        response = requests.get(account_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ API Key: ...{api_key[-8:]}")  # Show last 8 characters
            print(f"📈 Searches this month: {data.get('this_month_usage', 'N/A')}")
            print(f"🎯 Monthly limit: {data.get('plan_searches_left', 'N/A')} remaining")
            print(f"💰 Plan: {data.get('plan', 'N/A')}")
            
            # Calculate rate limit recommendation
            usage = data.get('this_month_usage', 0)
            if usage > 80:  # If more than 80% used
                print("⚠️  High usage detected - recommend 5+ second delays between requests")
            elif usage > 50:  # If more than 50% used
                print("💡 Moderate usage - recommend 3+ second delays between requests")
            else:
                print("✅ Low usage - standard rate limiting should work fine")
            
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_rate_limiting():
    """Test current rate limiting by making controlled requests."""
    print("\n🔬 Testing Rate Limiting")
    print("=" * 50)
    
    api_key = os.getenv('SERPAPI_KEY') or os.getenv('SERPAPI_API_KEY')
    if not api_key:
        print("❌ SerpAPI key not found")
        return False
    
    # Make 3 test requests with timing
    test_queries = ["test query 1", "test query 2", "test query 3"]
    delays = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"Request {i}/3: {query}")
        start_time = time.time()
        
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": api_key,
                "num": 1,
                "hl": "en",
                "gl": "us"
            }
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                print(f"  ✅ Success - {response_time:.2f}s response time")
                delays.append(response_time)
            elif response.status_code == 429:
                print(f"  ⚠️  Rate limited - need longer delays")
                return False
            else:
                print(f"  ❌ Error {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {str(e)}")
            return False
        
        # Wait 3 seconds between requests
        if i < len(test_queries):
            print("  ⏱️  Waiting 3 seconds...")
            time.sleep(3)
    
    if delays:
        avg_delay = sum(delays) / len(delays)
        print(f"\n📊 Average response time: {avg_delay:.2f}s")
        print("✅ Rate limiting test completed successfully")
        print("💡 Your current 3-second delay appears to be working")
    
    return True

def recommend_settings():
    """Provide recommendations for optimal settings."""
    print("\n💡 Recommendations")
    print("=" * 50)
    
    print("🔧 For optimal performance:")
    print("   • Use 3-5 second delays between SerpAPI requests")
    print("   • Limit related keywords to 1-2 to reduce API calls")
    print("   • Monitor your monthly usage regularly")
    print("   • Consider upgrading plan if hitting limits frequently")
    
    print("\n⚙️  Current backend settings:")
    print("   • SerpAPI delay: 3.0 seconds")
    print("   • Related keywords: Limited to 2")
    print("   • Browser scraping delay: 2.0 seconds")
    
    print("\n🚨 If you get rate limited:")
    print("   • Wait 10-15 minutes before trying again")
    print("   • Increase delays in serpapi_keyword_analyzer.py")
    print("   • Reduce the number of keywords analyzed simultaneously")

def main():
    """Run the rate limit monitor."""
    print("🚀 SerpAPI Rate Limit Monitor")
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check account status
    account_ok = check_serpapi_account()
    
    if account_ok:
        # Test rate limiting
        rate_limit_ok = test_rate_limiting()
        
        # Provide recommendations
        recommend_settings()
        
        if rate_limit_ok:
            print("\n🎉 Everything looks good! You can proceed with keyword analysis.")
        else:
            print("\n⚠️  Rate limiting issues detected. Please wait before making more requests.")
    else:
        print("\n❌ Please check your SerpAPI configuration.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
