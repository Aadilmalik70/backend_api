#!/usr/bin/env python3
"""
Test the main application startup to identify any remaining issues
"""
import sys
import os
import traceback

# Add the project root to the path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def test_main_imports():
    """Test if we can import all the main components"""
    
    print("🔍 Testing main application imports...")
    
    try:
        # Test content analyzer import
        print("   📝 Testing content analyzer import...")
        sys.path.insert(0, os.path.join(project_root, 'src'))
        from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
        print("   ✅ Content analyzer imported successfully")
        
        # Test routes import
        print("   🛣️  Testing routes import...")
        from routes.api import api_bp
        print("   ✅ Routes imported successfully")
        
        # Test the main app startup
        print("   🚀 Testing main app startup...")
        from src.main import app
        print("   ✅ Main app imported successfully")
        
        print("\n🎉 All imports successful! The application should start correctly.")
        
    except Exception as e:
        print(f"\n❌ Error during import testing: {e}")
        traceback.print_exc()
        
        # Try to identify the specific issue
        print("\n🔍 Debugging information:")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Project root: {project_root}")

if __name__ == "__main__":
    test_main_imports()
