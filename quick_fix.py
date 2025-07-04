#!/usr/bin/env python3
"""
Quick Fix Script for Content Analyzer Syntax Error

This script will fix the unmatched '}' error in content_analyzer_enhanced_real.py
"""
import os

def quick_fix():
    """Quick fix for the syntax error"""
    
    print("🔧 Quick Fix for Content Analyzer Syntax Error")
    print("=" * 50)
    
    # Navigate to the project directory
    project_dir = "C:/Users/oj/Desktop/project/backend_api"
    os.chdir(project_dir)
    
    file_path = "src/content_analyzer_enhanced_real.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Original file: {len(content)} characters")
        
        # Clean up the content
        content = content.rstrip()
        
        # Count braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"📊 Braces: {open_braces} open, {close_braces} close")
        
        # Fix the brace mismatch
        if close_braces > open_braces:
            print("🔧 Fixing extra closing braces...")
            
            # Remove extra closing braces from the end
            while content.endswith('}') and content.count('}') > content.count('{'):
                content = content[:-1].rstrip()
            
            # Ensure it ends with exactly one closing brace
            if not content.endswith('}'):
                content += '}'
        
        elif open_braces > close_braces:
            print("🔧 Adding missing closing braces...")
            missing = open_braces - close_braces
            content += '}' * missing
        
        # Final check
        if content.count('{') == content.count('}'):
            print("✅ Braces are now balanced")
        else:
            print("❌ Still unbalanced braces")
            return False
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed file saved: {len(content)} characters")
        
        # Test the syntax
        try:
            compile(content, file_path, 'exec')
            print("✅ Syntax is now valid")
            return True
        except SyntaxError as e:
            print(f"❌ Still has syntax error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if quick_fix():
        print("\n🎉 Content Analyzer has been fixed!")
        print("You can now run: python src/main.py")
        print("\nOr run the Phase 2.2 test: python test_phase_2_2_content_analyzer.py")
    else:
        print("\n❌ Failed to fix the content analyzer")
        print("Please check the file manually for syntax errors")
