#!/usr/bin/env python3
"""
Fix any encoding or syntax issues in the content analyzer
"""
import os
import re

def fix_content_analyzer():
    """Fix any syntax issues in the content analyzer"""
    
    file_path = "src/content_analyzer_enhanced_real.py"
    
    print("🔧 Fixing content analyzer file...")
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Original file size: {len(content)} characters")
        
        # Remove any trailing whitespace and ensure proper ending
        content = content.rstrip()
        
        # Check if the file ends properly
        if not content.endswith('}'):
            print("❌ File doesn't end with closing brace")
            return False
        
        # Count braces to ensure they're balanced
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"📊 Brace count: {open_braces} open, {close_braces} close")
        
        if open_braces != close_braces:
            print("❌ Unbalanced braces detected")
            return False
        
        # Try to compile the content
        try:
            compile(content, file_path, 'exec')
            print("✅ Content compiles successfully")
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            return False
        
        # Write the cleaned content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ File cleaned and saved successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    os.chdir("C:/Users/oj/Desktop/project/backend_api")
    
    if fix_content_analyzer():
        print("\n🎉 Content analyzer file has been fixed!")
        
        # Test the import
        try:
            import sys
            sys.path.insert(0, "src")
            from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
            print("✅ Import test successful!")
            
            # Test initialization
            analyzer = ContentAnalyzerEnhancedReal()
            print("✅ Initialization test successful!")
            
        except Exception as e:
            print(f"❌ Import/initialization test failed: {e}")
    else:
        print("❌ Failed to fix content analyzer file")
