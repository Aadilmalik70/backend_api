#!/usr/bin/env python3
"""
Direct test of the main application to identify the specific issue
"""
import os
import sys

# Set up the environment
os.chdir("C:/Users/oj/Desktop/project/backend_api")

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, "src")

print("🔍 Direct application test")
print("=" * 30)
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}...")

try:
    print("\n1. Testing content analyzer import...")
    from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    print("   ✅ Content analyzer imported successfully")
    
    print("\n2. Testing content analyzer initialization...")
    analyzer = ContentAnalyzerEnhancedReal()
    print("   ✅ Content analyzer initialized successfully")
    
    print("\n3. Testing routes import...")
    from routes.api import api_bp
    print("   ✅ Routes imported successfully")
    
    print("\n4. Testing main app import...")
    import main
    print("   ✅ Main app imported successfully")
    
    print("\n🎉 All tests passed! The application should work correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    # Additional debugging
    print("\n🔍 Additional debugging:")
    if "content_analyzer_enhanced_real" in str(e):
        print("   Issue is with content analyzer file")
        
        # Check if the file exists
        if os.path.exists("src/content_analyzer_enhanced_real.py"):
            print("   ✅ File exists")
            
            # Try to check syntax
            try:
                with open("src/content_analyzer_enhanced_real.py", 'r') as f:
                    content = f.read()
                compile(content, "src/content_analyzer_enhanced_real.py", 'exec')
                print("   ✅ Syntax is valid")
            except SyntaxError as se:
                print(f"   ❌ Syntax error: {se}")
                print(f"   Line {se.lineno}: {se.text}")
        else:
            print("   ❌ File does not exist")
