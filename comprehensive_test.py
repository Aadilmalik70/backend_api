#!/usr/bin/env python3
"""
Comprehensive test to identify and fix the import issue
"""
import sys
import os
import ast

def check_python_syntax(file_path):
    """Check Python syntax of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        return True, "Syntax is correct"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    print("🔍 Comprehensive syntax and import check")
    print("=" * 50)
    
    # Check content analyzer syntax
    content_analyzer_path = "C:/Users/oj/Desktop/project/backend_api/src/content_analyzer_enhanced_real.py"
    
    print(f"📝 Checking: {content_analyzer_path}")
    
    if os.path.exists(content_analyzer_path):
        is_valid, message = check_python_syntax(content_analyzer_path)
        if is_valid:
            print("✅ Content analyzer syntax is valid")
        else:
            print(f"❌ Content analyzer syntax error: {message}")
            return
    else:
        print(f"❌ File not found: {content_analyzer_path}")
        return
    
    # Check if we can import the module
    try:
        # Add src to path
        src_path = "C:/Users/oj/Desktop/project/backend_api/src"
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        print("🔧 Testing import...")
        from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
        print("✅ Import successful!")
        
        # Test initialization
        print("🚀 Testing initialization...")
        analyzer = ContentAnalyzerEnhancedReal()
        print("✅ Initialization successful!")
        
        # Test methods
        print("🧪 Testing methods...")
        status = analyzer.get_client_status()
        print(f"✅ Methods working - {len(status)} clients status retrieved")
        
        print("\n🎉 All checks passed! The content analyzer is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
