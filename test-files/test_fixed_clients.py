#!/usr/bin/env python3
"""
Test Fixed Google APIs Clients
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Force reload environment
from dotenv import load_dotenv
load_dotenv(override=True)

from src.utils.google_apis.custom_search_client import CustomSearchClient
from src.utils.google_apis.knowledge_graph_client import KnowledgeGraphClient
from src.utils.google_apis.gemini_client import GeminiClient

def test_fixed_clients():
    """Test the fixed Google APIs clients"""
    print("🔧 Testing Fixed Google APIs Clients")
    print("=" * 50)
    
    # Test Custom Search
    print("\n📊 Testing Custom Search Client...")
    search_client = CustomSearchClient()
    result = search_client.search("SEO tools", num_results=3)
    
    print(f"Result keys: {list(result.keys())}")
    print(f"Items found: {len(result.get('items', []))}")
    print(f"Data source: {result.get('data_source', 'unknown')}")
    
    if result.get('items'):
        print(f"Sample item title: {result['items'][0].get('title', 'No title')}")
    
    # Test Knowledge Graph
    print("\n🧠 Testing Knowledge Graph Client...")
    kg_client = KnowledgeGraphClient()
    kg_result = kg_client.search_entities("Google", limit=2)
    
    print(f"Result keys: {list(kg_result.keys())}")
    print(f"ItemListElement found: {len(kg_result.get('itemListElement', []))}")
    print(f"Entities found: {len(kg_result.get('entities', []))}")
    print(f"Data source: {kg_result.get('data_source', 'unknown')}")
    
    # Test Gemini
    print("\n🤖 Testing Gemini Client...")
    gemini_client = GeminiClient()
    
    if hasattr(gemini_client, 'generate_content'):
        print("✅ generate_content method exists")
        gemini_result = gemini_client.generate_content("What is SEO?")
        print(f"Result keys: {list(gemini_result.keys())}")
        print(f"Content generated: {bool(gemini_result.get('content'))}")
        print(f"Data source: {gemini_result.get('data_source', 'unknown')}")
    else:
        print("❌ generate_content method missing")
    
    print("\n🎯 Test Summary:")
    print(f"Custom Search working: {len(result.get('items', [])) > 0}")
    print(f"Knowledge Graph working: {len(kg_result.get('itemListElement', [])) > 0}")
    print(f"Gemini working: {bool(gemini_result.get('content')) if 'gemini_result' in locals() else False}")

if __name__ == "__main__":
    test_fixed_clients()
