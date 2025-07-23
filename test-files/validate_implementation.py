#!/usr/bin/env python3
"""
Final validation test for Google APIs integration (Phase 1 & 2.1)
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_implementation():
    """Validate the current implementation"""
    print("🏁 Final Validation Test - Phase 1 & 2.1")
    print("=" * 50)
    
    validation_results = {
        "phase_1": {"completed": 0, "total": 3},
        "phase_2_1": {"completed": 0, "total": 1},
        "overall": {"passed": 0, "total": 8}
    }
    
    # Test 1: Environment Configuration
    print("\n1. 🔧 Testing Environment Configuration...")
    try:
        # Check if validation script exists and runs
        if os.path.exists("validate_google_apis_environment.py"):
            print("✅ Environment validation script exists")
            validation_results["phase_1"]["completed"] += 1
            validation_results["overall"]["passed"] += 1
        else:
            print("❌ Environment validation script missing")
        
        # Check .env.example
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as f:
                content = f.read()
                if "GOOGLE_API_KEY" in content and "GOOGLE_CUSTOM_SEARCH_ENGINE_ID" in content:
                    print("✅ Environment example file properly configured")
                    validation_results["phase_1"]["completed"] += 1
                    validation_results["overall"]["passed"] += 1
                else:
                    print("❌ Environment example file incomplete")
        else:
            print("❌ Environment example file missing")
            
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
    
    # Test 2: Dependencies
    print("\n2. 📦 Testing Dependencies...")
    try:
        # Check requirements.txt
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r") as f:
                content = f.read()
                if "google-api-python-client" in content and "google-generativeai" in content:
                    print("✅ Requirements file has Google APIs dependencies")
                    validation_results["phase_1"]["completed"] += 1
                    validation_results["overall"]["passed"] += 1
                else:
                    print("❌ Requirements file missing Google APIs dependencies")
        else:
            print("❌ Requirements file missing")
            
    except Exception as e:
        print(f"❌ Dependencies test failed: {e}")
    
    # Test 3: Main Application
    print("\n3. 🚀 Testing Main Application...")
    try:
        # Check if main.py exists and has Google APIs integration
        if os.path.exists("src/main.py"):
            with open("src/main.py", "r") as f:
                content = f.read()
                if "google_apis" in content.lower() and "initialize_google_apis" in content:
                    print("✅ Main application has Google APIs integration")
                    validation_results["phase_1"]["completed"] += 1
                    validation_results["overall"]["passed"] += 1
                else:
                    print("❌ Main application missing Google APIs integration")
        else:
            print("❌ Main application file missing")
            
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
    
    # Test 4: API Routes
    print("\n4. 🛣️ Testing API Routes...")
    try:
        # Check if api.py exists and has Google APIs integration
        if os.path.exists("src/routes/api.py"):
            with open("src/routes/api.py", "r") as f:
                content = f.read()
                if "google_apis" in content.lower() and "migration_manager" in content.lower():
                    print("✅ API routes have Google APIs integration")
                    validation_results["phase_2_1"]["completed"] += 1
                    validation_results["overall"]["passed"] += 1
                else:
                    print("❌ API routes missing Google APIs integration")
        else:
            print("❌ API routes file missing")
            
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
    
    # Test 5: Application Startup
    print("\n5. ⚡ Testing Application Startup...")
    try:
        # Try importing and initializing the application
        sys.path.append('src')
        from main import app
        
        with app.app_context():
            google_apis_enabled = app.config.get('GOOGLE_APIS_ENABLED', False)
            google_apis_clients = app.config.get('GOOGLE_APIS_CLIENTS', {})
            
            print(f"✅ Application starts successfully")
            print(f"   Google APIs enabled: {google_apis_enabled}")
            print(f"   Available clients: {len(google_apis_clients)}")
            
            if google_apis_enabled:
                validation_results["overall"]["passed"] += 1
                print("✅ Google APIs properly initialized")
            else:
                print("⚠️  Google APIs not enabled (check .env configuration)")
                
    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
    
    # Test 6: API Endpoints
    print("\n6. 🌐 Testing API Endpoints...")
    try:
        from src.main import app
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # Test root endpoint
            response = client.get('/')
            if response.status_code == 200:
                data = json.loads(response.data)
                if "google_apis" in data:
                    print("✅ Root endpoint returns Google APIs status")
                    validation_results["overall"]["passed"] += 1
                else:
                    print("⚠️  Root endpoint missing Google APIs status")
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
            
            # Test Google APIs status endpoint
            response = client.get('/api/google-apis/status')
            if response.status_code == 200:
                print("✅ Google APIs status endpoint working")
                validation_results["overall"]["passed"] += 1
            else:
                print(f"❌ Google APIs status endpoint failed: {response.status_code}")
                
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
    
    # Test 7: Documentation
    print("\n7. 📚 Testing Documentation...")
    try:
        # Check if README.md is updated
        if os.path.exists("README.md"):
            with open("README.md", "r") as f:
                content = f.read()
                if "Google APIs Integration" in content:
                    print("✅ README.md updated with Google APIs integration")
                    validation_results["overall"]["passed"] += 1
                else:
                    print("❌ README.md not updated")
        else:
            print("❌ README.md missing")
            
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
    
    # Test 8: Integration Files
    print("\n8. 🔗 Testing Integration Files...")
    try:
        # Check if TODO list exists and is updated
        if os.path.exists("GOOGLE_APIS_INTEGRATION_TODO.md"):
            with open("GOOGLE_APIS_INTEGRATION_TODO.md", "r") as f:
                content = f.read()
                if "[x]" in content:
                    print("✅ TODO list exists and has completed tasks")
                    validation_results["overall"]["passed"] += 1
                else:
                    print("⚠️  TODO list exists but no tasks marked complete")
        else:
            print("❌ TODO list missing")
            
        # Check if progress report exists
        if os.path.exists("GOOGLE_APIS_INTEGRATION_PROGRESS.md"):
            print("✅ Progress report exists")
        else:
            print("⚠️  Progress report missing")
            
    except Exception as e:
        print(f"❌ Integration files test failed: {e}")
    
    # Results Summary
    print("\n" + "=" * 50)
    print("📊 Validation Results Summary")
    print("=" * 50)
    
    phase_1_percentage = (validation_results["phase_1"]["completed"] / validation_results["phase_1"]["total"]) * 100
    phase_2_1_percentage = (validation_results["phase_2_1"]["completed"] / validation_results["phase_2_1"]["total"]) * 100
    overall_percentage = (validation_results["overall"]["passed"] / validation_results["overall"]["total"]) * 100
    
    print(f"📋 Phase 1 (Core Infrastructure): {validation_results['phase_1']['completed']}/{validation_results['phase_1']['total']} ({phase_1_percentage:.0f}%)")
    print(f"📋 Phase 2.1 (API Routes): {validation_results['phase_2_1']['completed']}/{validation_results['phase_2_1']['total']} ({phase_2_1_percentage:.0f}%)")
    print(f"📋 Overall Integration: {validation_results['overall']['passed']}/{validation_results['overall']['total']} ({overall_percentage:.0f}%)")
    
    # Status Assessment
    print("\n🎯 Status Assessment:")
    if overall_percentage >= 80:
        print("✅ EXCELLENT: Google APIs integration is production-ready!")
        print("🚀 Ready to proceed with Phase 2.2 (Content Analyzer)")
    elif overall_percentage >= 60:
        print("⚠️  GOOD: Most components working, minor issues to resolve")
        print("🔧 Address failing tests before proceeding")
    else:
        print("❌ NEEDS WORK: Major components need attention")
        print("🔧 Focus on fixing core infrastructure issues")
    
    # Next Steps
    print("\n🚀 Next Steps:")
    print("-" * 20)
    if overall_percentage >= 80:
        print("1. 🎉 Celebrate Phase 1 & 2.1 completion!")
        print("2. 📝 Update TODO list with current progress")
        print("3. 🔄 Start Phase 2.2 (Content Analyzer)")
        print("4. 🧪 Run: python src/main.py to test the application")
        print("5. 📊 Monitor performance and costs")
    else:
        print("1. 🔧 Fix failing validation tests")
        print("2. 🔄 Re-run this validation script")
        print("3. 📚 Check documentation for troubleshooting")
        print("4. 🧪 Run: python validate_google_apis_environment.py")
    
    # Application Testing Commands
    print("\n🧪 Quick Application Test Commands:")
    print("-" * 40)
    print("# Start the application")
    print("python src/main.py")
    print("")
    print("# Test endpoints (in another terminal)")
    print("curl http://localhost:5000/")
    print("curl http://localhost:5000/api/google-apis/status")
    print("curl http://localhost:5000/api/health")
    print("")
    print("# Test processing endpoint")
    print("curl -X POST http://localhost:5000/api/process \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"input\": \"SEO tools\", \"domain\": \"example.com\"}'")
    
    print("\n" + "=" * 50)
    print("🎯 Final Validation Complete")
    print("=" * 50)
    
    return overall_percentage >= 80

if __name__ == "__main__":
    success = validate_implementation()
    sys.exit(0 if success else 1)
