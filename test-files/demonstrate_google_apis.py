#!/usr/bin/env python3
"""
Demonstration script for Google APIs integration
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demonstrate_google_apis():
    """Demonstrate Google APIs integration"""
    print("🎭 Google APIs Integration Demonstration")
    print("=" * 60)
    
    # Import the main application
    sys.path.append('src')
    
    try:
        from main import app
        
        # Run demonstration in app context
        with app.app_context():
            # Show configuration
            print("\n📋 Configuration Status:")
            print("-" * 30)
            
            google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
            google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
            
            print(f"Google APIs Enabled: {'✅ Yes' if google_apis_enabled else '❌ No'}")
            print(f"Available Clients: {len(google_apis_clients)}")
            
            if google_apis_clients:
                for client_name, client in google_apis_clients.items():
                    print(f"  • {client_name}: {type(client).__name__}")
            
            # Demonstrate API functionality
            print("\n🔬 API Functionality Demonstration:")
            print("-" * 40)
            
            # Test Custom Search
            if 'custom_search' in google_apis_clients:
                print("\n🔍 Testing Custom Search API...")
                try:
                    client = google_apis_clients['custom_search']
                    result = client.search('python seo tools', num_results=3)
                    
                    if result and 'results' in result:
                        print(f"✅ Found {len(result['results'])} results")
                        for i, item in enumerate(result['results'][:2], 1):
                            print(f"   {i}. {item.get('title', 'No title')}")
                    else:
                        print("⚠️  No results returned")
                        
                except Exception as e:
                    print(f"❌ Custom Search test failed: {e}")
            
            # Test Knowledge Graph
            if 'knowledge_graph' in google_apis_clients:
                print("\n🧠 Testing Knowledge Graph API...")
                try:
                    client = google_apis_clients['knowledge_graph']
                    result = client.search_entities('Google')
                    
                    if result and 'entities' in result:
                        print(f"✅ Found {len(result['entities'])} entities")
                        for entity in result['entities'][:2]:
                            print(f"   • {entity.get('name', 'Unknown')}")
                    else:
                        print("⚠️  No entities returned")
                        
                except Exception as e:
                    print(f"❌ Knowledge Graph test failed: {e}")
            
            # Test Natural Language
            if 'natural_language' in google_apis_clients:
                print("\n📝 Testing Natural Language API...")
                try:
                    client = google_apis_clients['natural_language']
                    result = client.analyze_content('This is a test sentence about SEO optimization.')
                    
                    if result and 'entities' in result:
                        print(f"✅ Found {len(result['entities'])} entities")
                        for entity in result['entities'][:2]:
                            print(f"   • {entity.get('name', 'Unknown')}: {entity.get('type', 'Unknown')}")
                    else:
                        print("⚠️  No entities returned")
                        
                except Exception as e:
                    print(f"❌ Natural Language test failed: {e}")
            
            # Test Gemini
            if 'gemini' in google_apis_clients:
                print("\n🤖 Testing Gemini API...")
                try:
                    client = google_apis_clients['gemini']
                    result = client.analyze_ai_readiness('This is test content for AI analysis.')
                    
                    if result and 'overall_ai_readiness' in result:
                        score = result['overall_ai_readiness']
                        print(f"✅ AI readiness score: {score:.2f}")
                        if 'category_scores' in result:
                            for category, score in result['category_scores'].items():
                                print(f"   • {category}: {score:.2f}")
                    else:
                        print("⚠️  No analysis returned")
                        
                except Exception as e:
                    print(f"❌ Gemini test failed: {e}")
            
            # Test Migration Manager
            if 'migration_manager' in google_apis_clients:
                print("\n🔄 Testing Migration Manager...")
                try:
                    client = google_apis_clients['migration_manager']
                    
                    # Test SERP data migration
                    serp_result = client.get_serp_data('test query')
                    if serp_result:
                        print("✅ SERP data migration working")
                        print(f"   Using: {serp_result.get('data_source', 'Unknown')}")
                    
                    # Test content analysis migration
                    content_result = client.analyze_content('Test content')
                    if content_result:
                        print("✅ Content analysis migration working")
                        print(f"   Entities found: {len(content_result.get('entities', []))}")
                        
                except Exception as e:
                    print(f"❌ Migration Manager test failed: {e}")
            
            # Performance comparison
            print("\n⚡ Performance Comparison:")
            print("-" * 30)
            
            # Simulate API calls and measure time
            if google_apis_enabled:
                start_time = time.time()
                
                # Test a simple workflow
                try:
                    if 'custom_search' in google_apis_clients:
                        google_apis_clients['custom_search'].search('test', num_results=1)
                    
                    if 'knowledge_graph' in google_apis_clients:
                        google_apis_clients['knowledge_graph'].search_entities('test')
                    
                    end_time = time.time()
                    google_apis_time = end_time - start_time
                    
                    print(f"✅ Google APIs workflow: {google_apis_time:.2f}s")
                    print(f"   Estimated cost: ~$0.007 per 1K requests")
                    print(f"   vs SerpAPI: ~$0.050 per 1K requests")
                    print(f"   💰 Cost savings: ~86%")
                    
                except Exception as e:
                    print(f"❌ Performance test failed: {e}")
            
            # Show next steps
            print("\n🚀 Next Steps:")
            print("-" * 20)
            print("1. Start the application: python src/main.py")
            print("2. Test the API endpoints:")
            print("   • GET  http://localhost:5000/")
            print("   • GET  http://localhost:5000/api/google-apis/status")
            print("   • GET  http://localhost:5000/api/health")
            print("   • POST http://localhost:5000/api/process")
            print("3. Monitor performance and costs")
            print("4. Continue with remaining integration tasks")
            
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your .env file configuration")
        print("2. Run: python validate_google_apis_environment.py")
        print("3. Verify Google Cloud project setup")
        print("4. Check API keys and permissions")
    
    print("\n" + "=" * 60)
    print("🎯 Demonstration Complete")
    print("=" * 60)

if __name__ == "__main__":
    demonstrate_google_apis()
