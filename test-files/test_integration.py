#!/usr/bin/env python3
"""
Test the updated application with Google APIs integration
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_google_apis_integration():
    """Test the Google APIs integration"""
    print("🧪 Testing Google APIs Integration")
    print("=" * 50)
    
    # Test environment validation
    print("\n1. Testing environment validation...")
    try:
        result = os.system("python validate_google_apis_environment.py")
        if result == 0:
            print("✅ Environment validation passed")
        else:
            print("❌ Environment validation failed")
    except Exception as e:
        print(f"❌ Environment validation error: {e}")
    
    # Test main application startup
    print("\n2. Testing main application startup...")
    try:
        # Import main application
        sys.path.append('src')
        from main import app
        
        # Test app configuration
        with app.app_context():
            google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
            google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
            
            print(f"✅ Google APIs enabled: {google_apis_enabled}")
            print(f"✅ Google APIs clients: {len(google_apis_clients)}")
            
            if google_apis_clients:
                for client_name in google_apis_clients.keys():
                    print(f"   • {client_name}")
            
    except Exception as e:
        print(f"❌ Main application startup error: {e}")
    
    # Test API routes
    print("\n3. Testing API routes...")
    try:
        # Start the Flask app in test mode
        from src.main import app
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test root endpoint
            response = client.get('/')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Root endpoint: {data.get('name', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Google APIs: {data.get('google_apis', {}).get('enabled', False)}")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
            
            # Test Google APIs status
            response = client.get('/api/google-apis/status')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Google APIs status: {data.get('google_apis_enabled', False)}")
                print(f"   Clients available: {data.get('clients_available', 0)}")
            else:
                print(f"❌ Google APIs status failed: {response.status_code}")
            
            # Test health check
            response = client.get('/api/health')
            if response.status_code == 200:
                data = json.loads(response.data)
                print(f"✅ Health check: {data.get('status', 'unknown')}")
                print(f"   Overall status: {data.get('overall_status', 'unknown')}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API routes test error: {e}")
    
    # Test individual Google APIs
    print("\n4. Testing individual Google APIs...")
    try:
        result = os.system("python verify_google_apis.py")
        if result == 0:
            print("✅ Individual Google APIs tests passed")
        else:
            print("❌ Individual Google APIs tests failed")
    except Exception as e:
        print(f"❌ Individual Google APIs test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Summary")
    print("=" * 50)
    
    # Check current status
    google_api_key = os.getenv('GOOGLE_API_KEY')
    use_google_apis = os.getenv('USE_GOOGLE_APIS', 'true').lower() == 'true'
    
    if google_api_key and use_google_apis:
        print("✅ Google APIs integration is ready")
        print("🚀 You can now start using Google APIs in your application")
        print("\n📋 Next steps:")
        print("   1. Run: python src/main.py")
        print("   2. Test endpoints with curl or Postman")
        print("   3. Monitor performance and costs")
    else:
        print("⚠️  Google APIs integration needs configuration")
        print("🔧 Action items:")
        print("   1. Set GOOGLE_API_KEY in .env file")
        print("   2. Set USE_GOOGLE_APIS=true in .env file")
        print("   3. Run: python validate_google_apis_environment.py")

if __name__ == "__main__":
    test_google_apis_integration()
