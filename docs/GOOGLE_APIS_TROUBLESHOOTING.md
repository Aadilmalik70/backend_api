# Google APIs Troubleshooting Guide

## 🎯 **Current Issue**: APIs configured but returning no real data

Based on your test results, the Google APIs are **configured correctly** but not returning real data. Here's how to fix this:

---

## 🔧 **Step-by-Step Fix**

### **Step 1: Test APIs Directly**
```bash
python test_direct_apis.py
```

This will test the APIs directly to see if they're working at all.

### **Step 2: Disable Fallback Completely**
```bash
python disable_fallback.py
```

This forces the system to use only real Google APIs.

### **Step 3: Test Real Data**
```bash
python test_google_apis_connection.py
```

---

## 🐛 **Common Issues & Solutions**

### **Issue 1: Custom Search Engine Configuration**
**Problem**: Search engine returns 0 results
**Solution**: 
1. Go to https://cse.google.com/
2. Edit your search engine
3. Make sure it's set to search "**Entire Web**" not just specific sites
4. In "Setup" → "Basics" → ensure "Image search" and "Safe search" are configured
5. In "Setup" → "Advanced" → make sure "Search the entire web" is checked

### **Issue 2: API Quotas**
**Problem**: APIs have daily/monthly limits
**Solutions**:
- **Custom Search**: 100 searches/day free, then $5/1000 queries
- **Knowledge Graph**: 100,000 requests/day free, then $1/1000 requests
- Check quotas in Google Cloud Console → APIs & Services → Quotas

### **Issue 3: API Permissions**
**Problem**: API key doesn't have proper permissions
**Solution**:
1. Go to Google Cloud Console
2. APIs & Services → Credentials
3. Edit your API key
4. Under "API restrictions" make sure these are allowed:
   - Custom Search API
   - Knowledge Graph Search API
   - Generative Language API

### **Issue 4: Billing Account**
**Problem**: Some APIs require billing enabled
**Solution**:
1. Go to Google Cloud Console → Billing
2. Link a billing account to your project
3. Even with billing enabled, free tiers still apply

---

## 🧪 **Real Data Test Commands**

Run these in order to get real data:

```bash
# 1. Test direct API calls
python test_direct_apis.py

# 2. Disable fallback completely  
python disable_fallback.py

# 3. Test Google APIs connection
python test_google_apis_connection.py

# 4. Test real keyword processing
python test_real_keyword_processing.py

# 5. Test Phase 2.4 with real data
python test_phase_2_4_keyword_processor.py
```

---

## 🎯 **Expected Real Data Results**

When working correctly, you should see:

```
✅ Custom Search API: Working! Found 5 results
✅ Knowledge Graph API: Working! Found 3 entities  
✅ Gemini API: Working!
✅ Found 15 related keywords from Google Search
✅ Enhanced 10/15 keywords with entities
🎯 Real data confidence: 25/30 indicators
✅ Real Google APIs data detected!
```

---

## 🔍 **Debug Information**

From your test output, I can see:
- ✅ **API Keys**: Configured correctly
- ✅ **Search Engine ID**: Configured correctly  
- ❌ **Search Results**: Returning 0 items
- ❌ **Entity Results**: Returning no entities

This suggests the APIs are **connected** but not **configured properly** for real data.

---

## 💡 **Quick Fixes to Try**

### **Fix 1: Update Custom Search Engine**
```bash
# 1. Go to https://cse.google.com/
# 2. Find your search engine (ID: a60466b73e...)
# 3. Click "Setup" → "Basics"
# 4. Change "Sites to search" to "Search the entire web"
# 5. Save and test again
```

### **Fix 2: Test with Different Queries**
```bash
# Try simpler, more common queries
python -c "
from src.utils.google_apis.custom_search_client import CustomSearchClient
client = CustomSearchClient()
result = client.search('python programming', num_results=3)
print('Items found:', len(result.get('items', [])))
"
```

### **Fix 3: Check API Enablement**
1. Go to Google Cloud Console
2. APIs & Services → Enabled APIs
3. Ensure these are enabled:
   - Custom Search API
   - Knowledge Graph Search API
   - Generative Language API

---

## 🎯 **Next Steps**

1. **Run the direct API test**: `python test_direct_apis.py`
2. **Fix Custom Search Engine configuration** if needed
3. **Disable fallback**: `python disable_fallback.py`  
4. **Test again**: `python test_google_apis_connection.py`

Once you get real data from the APIs, Phase 2.4 will show authentic Google search results instead of mock data!

---

## 📞 **Still Need Help?**

If APIs still don't work:
1. Check Google Cloud Console → APIs & Services → Quotas
2. Verify billing account is linked (even for free tier)
3. Try creating a new Custom Search Engine
4. Check API key restrictions in Google Cloud Console

The good news is your implementation is working correctly - we just need to get the APIs configured properly for real data! 🎉
