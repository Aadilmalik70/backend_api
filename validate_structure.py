#!/usr/bin/env python3
"""
Simple script to validate and fix any basic issues in the content analyzer
"""
import sys
import os

def validate_file_structure():
    """Validate the file structure and fix basic issues"""
    
    print("🔍 Validating file structure...")
    
    # Check if the main files exist
    files_to_check = [
        "src/content_analyzer_enhanced_real.py",
        "src/routes/api.py",
        "src/main.py"
    ]
    
    for file_path in files_to_check:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Check the content analyzer file specifically
    content_analyzer_path = os.path.join(os.path.dirname(__file__), "src/content_analyzer_enhanced_real.py")
    
    try:
        with open(content_analyzer_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for basic syntax issues
        print("\n🔍 Checking content analyzer file...")
        
        # Count braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        print(f"   Opening braces: {open_braces}")
        print(f"   Closing braces: {close_braces}")
        
        # Count parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        print(f"   Opening parentheses: {open_parens}")
        print(f"   Closing parentheses: {close_parens}")
        
        # Check for unmatched brackets
        open_brackets = content.count('[')
        close_brackets = content.count(']')
        print(f"   Opening brackets: {open_brackets}")
        print(f"   Closing brackets: {close_brackets}")
        
        # Check the end of the file
        print("\n📄 Last 200 characters of file:")
        print(repr(content[-200:]))
        
        # Try to compile the file
        try:
            compile(content, content_analyzer_path, 'exec')
            print("\n✅ File compiles successfully!")
        except SyntaxError as e:
            print(f"\n❌ Syntax error: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    validate_file_structure()
