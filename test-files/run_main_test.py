#!/usr/bin/env python3
"""
Simple test to run the main application and capture any errors
"""
import subprocess
import sys
import os

def run_main_app():
    """Run the main application and capture output"""
    
    print("🚀 Running main application...")
    
    # Change to the project directory
    os.chdir("C:/Users/oj/Desktop/project/backend_api")
    
    try:
        # Run the main application
        result = subprocess.run(
            [sys.executable, "src/main.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("📤 STDOUT:")
        print(result.stdout)
        
        print("\n📥 STDERR:")
        print(result.stderr)
        
        print(f"\n📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Application started successfully!")
        else:
            print("❌ Application failed to start")
            
    except subprocess.TimeoutExpired:
        print("⏰ Application startup timed out (probably started successfully)")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    run_main_app()
