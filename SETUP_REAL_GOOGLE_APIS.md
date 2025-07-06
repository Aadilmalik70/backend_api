# Google APIs Setup Guide for Real Data Testing

## 🎯 **Goal**: Test Phase 2.4 with Real Google APIs (No Fallback Data)

To test the keyword processor with real Google APIs instead of mock/fallback data, you need to set up the following APIs:

---

## 📋 **Required Setup Steps**

### **1. Google Cloud Project Setup**

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one
   - Note your Project ID

2. **Enable Required APIs**:
   ```
   ✅ Custom Search API
   ✅ Knowledge Graph Search API
   ✅ Cloud Natural Language API (optional)
   ✅ Generative Language API (Gemini)
   ```

3. **Create API Key**:
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Copy the API key (keep it secure!)

### **2. Custom Search Engine Setup**

1. **Create Custom Search Engine**:
   - Go to https://cse.google.com/
   - Click "Add" to create new search engine
   - Configure to search "Entire web"
   - Copy the Search Engine ID

### **3. Environment Configuration**

Update your `.env` file with real values:

```bash
# REQUIRED FOR REAL DATA
GOOGLE_API_KEY=your_actual_google_api_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here
GEMINI_API_KEY=your_actual_google_api_key_here

# DISABLE FALLBACK FOR TESTING
USE_GOOGLE_APIS=true
FALLBACK_TO_SERPAPI=false  # Set to false to force real API usage

# OPTIONAL: Clear these to prevent fallback
SERPAPI_API_KEY=
SERPAPI_KEY=
```

---

## 🧪 **Testing Commands**

### **1. Test Google APIs Connection**
```bash
python test_google_apis_connection.py
```

### **2. Test Keyword Processor with Real Data**
```bash
python test_phase_2_4_keyword_processor.py
```

### **3. Test Specific Google Search**
```bash
python test_real_google_search.py
```

---

## 🔧 **Testing Scripts**

Let me create specific testing scripts for real data:

### **Script 1: Test Google APIs Connection**
```python
# test_google_apis_connection.py
import os
from src.utils.google_apis.custom_search_client import CustomSearchClient
from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient

def test_connection():
    print("🔍 Testing Google APIs Connection...")
    
    # Test Custom Search
    search_client = CustomSearchClient()
    if search_client.api_key and search_client.search_engine_id:
        try:
            result = search_client.search("test query", num_results=1)
            if 'items' in result:
                print("✅ Custom Search API: Working")
            else:
                print("❌ Custom Search API: No results")
        except Exception as e:
            print(f"❌ Custom Search API: Error - {e}")
    else:
        print("❌ Custom Search API: Not configured")
    
    # Test Knowledge Graph
    kg_client = KnowledgeGraphClient()
    if kg_client.api_key:
        try:
            result = kg_client.search_entities("Google", limit=1)
            if 'itemListElement' in result:
                print("✅ Knowledge Graph API: Working")
            else:
                print("❌ Knowledge Graph API: No entities")
        except Exception as e:
            print(f"❌ Knowledge Graph API: Error - {e}")
    else:
        print("❌ Knowledge Graph API: Not configured")

if __name__ == "__main__":
    test_connection()
```

### **Script 2: Test Real Keyword Processing**
```python
# test_real_keyword_processing.py
import os
from src.keyword_processor_enhanced_real import KeywordProcessorEnhancedReal

def test_real_keywords():
    print("🔍 Testing Real Keyword Processing...")
    
    # Disable fallback for testing
    os.environ['FALLBACK_TO_SERPAPI'] = 'false'
    
    processor = KeywordProcessorEnhancedReal()
    
    print(f"Google APIs enabled: {processor.google_apis_enabled}")
    print(f"Google Search client configured: {processor.google_search.api_key is not None}")
    print(f"Knowledge Graph client configured: {processor.knowledge_graph.api_key is not None}")
    
    # Test with real data
    test_keywords = ["SEO tools", "digital marketing"]
    
    for keyword in test_keywords:
        print(f"\n📊 Testing keyword: '{keyword}'")
        try:
            # Test Google Search method directly
            results = processor._get_keywords_from_google_search([keyword])
            print(f"✅ Found {len(results)} related keywords")
            
            for i, kw in enumerate(results[:3]):
                print(f"  {i+1}. {kw['keyword']} (volume: {kw['search_volume']})")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_real_keywords()
```

---

## 💰 **Cost Considerations**

### **Google APIs Pricing (Much Cheaper than SerpAPI)**:
- **Custom Search**: $5 per 1,000 queries (first 100/day FREE)
- **Knowledge Graph**: $1 per 1,000 calls (first 100,000/day FREE)
- **Natural Language**: $1 per 1,000 units (first 5,000/month FREE)
- **Gemini**: Pay per use (generous free tier)

### **For Testing**:
- You can test extensively within the free tiers
- Cost for 1,000 keyword research queries: ~$7 (vs ~$50 with SerpAPI)

---

## 🎯 **What You'll See with Real Data**

✅ **Real Google search results** instead of mock data  
✅ **Actual search volumes** and competition data  
✅ **Real entities** from Google's Knowledge Graph  
✅ **Authentic keyword suggestions** from actual search results  
✅ **True performance metrics** and response times  

---

## 🔧 **Quick Setup Commands**

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your real API keys
nano .env

# 3. Test the connection
python test_google_apis_connection.py

# 4. Test keyword processing with real data
python test_phase_2_4_keyword_processor.py
```

---

## ⚠️ **Troubleshooting**

| Issue | Solution |
|-------|----------|
| "API Key not found" | Add `GOOGLE_API_KEY` to `.env` file |
| "Search Engine ID not found" | Add `GOOGLE_CUSTOM_SEARCH_ENGINE_ID` to `.env` |
| "API not enabled" | Enable APIs in Google Cloud Console |
| "Quota exceeded" | Check API quotas in Google Cloud Console |
| "Mock data still showing" | Set `FALLBACK_TO_SERPAPI=false` |

---

## 🎉 **Expected Results**

Once configured, you should see:
- ✅ Real keyword suggestions from Google search results
- ✅ Actual search volume estimates
- ✅ Real entity data from Knowledge Graph
- ✅ Authentic competition analysis
- ✅ True performance metrics

**Ready to set up real Google APIs testing!**
