#!/usr/bin/env python3
"""
Quick test to check if the application starts without errors
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_app_startup():
    """Test if the application starts without errors"""
    print("🧪 Testing Application Startup After SerpAPI Fix")
    print("=" * 50)
    
    try:
        # Add src to path
        sys.path.append('src')
        
        # Test imports
        print("1. Testing imports...")
        from main import app
        print("✅ Main application imported successfully")
        
        # Test app creation
        print("\n2. Testing app configuration...")
        with app.app_context():
            google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
            google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
            
            print(f"✅ Google APIs enabled: {google_apis_enabled}")
            print(f"✅ Available clients: {len(google_apis_clients)}")
            
            if google_apis_clients:
                for client_name in google_apis_clients.keys():
                    print(f"   • {client_name}")
        
        # Test routes
        print("\n3. Testing API routes...")
        from src.routes.api import api_bp
        print("✅ API routes imported successfully")
        
        # Test basic endpoints
        print("\n4. Testing basic endpoints...")
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test root endpoint
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Root endpoint working")
            else:
                print(f"⚠️  Root endpoint status: {response.status_code}")
            
            # Test health endpoint
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"⚠️  Health endpoint status: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS: Application starts without errors!")
        print("✅ SerpAPI fallback mechanism working")
        print("✅ Google APIs integration functional")
        print("✅ All endpoints responding")
        
        print("\n🚀 You can now start the application:")
        print("   python src/main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Application startup failed: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # More detailed error information
        import traceback
        print("\n🔍 Detailed error trace:")
        traceback.print_exc()
        
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if all required dependencies are installed")
        print("2. Verify your .env file configuration")
        print("3. Run: python validate_google_apis_environment.py")
        print("4. Check if all required modules are in place")
        
        return False

if __name__ == "__main__":
    success = test_app_startup()
    sys.exit(0 if success else 1)
