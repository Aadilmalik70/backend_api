#!/usr/bin/env python3
"""
Minimal test to isolate the import issue
"""
import sys
import os

# Set up the path properly
project_root = "C:/Users/oj/Desktop/project/backend_api"
os.chdir(project_root)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

print("🔍 Minimal Import Test")
print("=" * 30)
print(f"Working directory: {os.getcwd()}")
print(f"Python path includes: {sys.path[:3]}")

# Test 1: Try to import the content analyzer directly
print("\n1. Testing direct import...")
try:
    import content_analyzer_enhanced_real
    print("✅ Direct module import successful")
    
    # Test class import
    from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    print("✅ Class import successful")
    
    # Test initialization
    analyzer = ContentAnalyzerEnhancedReal()
    print("✅ Initialization successful")
    
except Exception as e:
    print(f"❌ Direct import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Try to import from the routes module
print("\n2. Testing routes import...")
try:
    from routes.api import api_bp
    print("✅ Routes import successful")
except Exception as e:
    print(f"❌ Routes import failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Try to run main.py import
print("\n3. Testing main.py import...")
try:
    import main
    print("✅ Main.py import successful")
except Exception as e:
    print(f"❌ Main.py import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete")
