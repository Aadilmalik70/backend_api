#!/usr/bin/env python3
"""
Application Startup Script - Google APIs Integration

This script starts the main application and provides real-time status monitoring
for the Google APIs integration.
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

def print_banner():
    """Print application startup banner"""
    print("🚀 Starting SEO Tool with Google APIs Integration")
    print("=" * 60)
    print("📊 Project Status: 50% Complete (6/13 major tasks)")
    print("✅ Phase 1: Core Infrastructure (100% complete)")
    print("✅ Phase 2.1: API Routes Integration (100% complete)")
    print("✅ Phase 2.2: Content Analyzer Integration (100% complete)")
    print("✅ Phase 2.3: Competitor Analysis Integration (100% complete)")
    print("=" * 60)
    print()

def check_environment():
    """Check if the environment is properly set up"""
    print("🔍 Checking Environment...")
    
    # Check if we're in the right directory
    if not os.path.exists("src/main.py"):
        print("❌ Error: src/main.py not found. Please run from the project root directory.")
        return False
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected. Consider activating your venv.")
    else:
        print("✅ Virtual environment is active")
    
    # Check for key files
    key_files = [
        "src/content_analyzer_enhanced_real.py",
        "src/competitor_analysis_real.py",
        "src/routes/api.py"
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    print("✅ Environment check passed!")
    print()
    return True

def start_application():
    """Start the main application"""
    print("🔄 Starting Application...")
    print("📝 Application logs will appear below:")
    print("-" * 60)
    
    try:
        # Change to project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start the application
        process = subprocess.Popen(
            [sys.executable, "src/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Real-time output monitoring
        def monitor_output():
            for line in iter(process.stdout.readline, ''):
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] {line.rstrip()}")
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Wait a bit to see if the application starts successfully
        time.sleep(5)
        
        if process.poll() is None:
            # Application is still running
            print()
            print("🎉 Application started successfully!")
            print("🌐 The application should be available at: http://localhost:5000")
            print()
            print("📋 Available Endpoints:")
            print("   🏠 Main: http://localhost:5000")
            print("   📊 Health: http://localhost:5000/api/health")
            print("   🔍 Google APIs Status: http://localhost:5000/api/google-apis/status")
            print("   🧪 Google APIs Test: http://localhost:5000/api/google-apis/test")
            print("   📈 Performance: http://localhost:5000/api/google-apis/performance")
            print()
            print("🔧 Enhanced Features Available:")
            print("   ✅ Content Analysis with Google Natural Language API")
            print("   ✅ Competitor Analysis with Google Custom Search & Knowledge Graph")
            print("   ✅ AI-powered insights with Google Gemini API")
            print("   ✅ Intelligent fallback mechanisms")
            print()
            print("⌨️  Press Ctrl+C to stop the application")
            print("-" * 60)
            
            # Keep the script running and monitoring
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping application...")
                process.terminate()
                process.wait()
                print("✅ Application stopped successfully")
        else:
            # Application failed to start
            print("❌ Application failed to start")
            print("Exit code:", process.returncode)
            return False
            
    except FileNotFoundError:
        print("❌ Python interpreter not found")
        return False
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True

def show_usage_tips():
    """Show usage tips for testing the application"""
    print()
    print("🔥 How to Test the Enhanced Features:")
    print("=" * 50)
    print()
    print("1. 📊 **Test Google APIs Status**")
    print("   Visit: http://localhost:5000/api/google-apis/status")
    print("   See real-time status of all Google APIs")
    print()
    print("2. 🧪 **Test Enhanced Content Analysis**")
    print("   Use the /api/process endpoint with a URL")
    print("   Example: POST to /api/process with {'url': 'https://example.com'}")
    print()
    print("3. 🔍 **Test Competitor Analysis**")
    print("   Use the competitor analysis endpoints")
    print("   Enhanced with Google Custom Search and Knowledge Graph")
    print()
    print("4. 📈 **Monitor Performance**")
    print("   Visit: http://localhost:5000/api/google-apis/performance")
    print("   Track API usage and response times")
    print()
    print("5. 🏥 **Health Check**")
    print("   Visit: http://localhost:5000/api/health")
    print("   Overall system health including Google APIs")
    print()

def main():
    """Main function"""
    print_banner()
    
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        return
    
    show_usage_tips()
    
    print("🚀 Starting the application now...")
    print()
    
    if start_application():
        print("✅ Application session completed")
    else:
        print("❌ Application failed to start properly")

if __name__ == "__main__":
    main()
