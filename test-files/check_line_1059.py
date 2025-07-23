#!/usr/bin/env python3
"""
Check the exact content around line 1059
"""
import os

def check_line_1059():
    """Check the exact content around line 1059"""
    
    file_path = "C:/Users/oj/Desktop/project/backend_api/src/content_analyzer_enhanced_real.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"Total lines in file: {len(lines)}")
        
        # Check around line 1059
        if len(lines) >= 1059:
            print("Content around line 1059:")
            for i in range(max(0, 1056), min(len(lines), 1062)):
                line_num = i + 1
                content = lines[i].rstrip('\n\r')
                print(f"Line {line_num}: {repr(content)}")
        else:
            print("File has fewer than 1059 lines")
            print("Last 10 lines:")
            for i in range(max(0, len(lines)-10), len(lines)):
                line_num = i + 1
                content = lines[i].rstrip('\n\r')
                print(f"Line {line_num}: {repr(content)}")
        
        # Check for unmatched braces
        content = ''.join(lines)
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"\nBrace count: {open_braces} open, {close_braces} close")
        
        # Try to compile
        try:
            compile(content, file_path, 'exec')
            print("✅ File compiles successfully")
        except SyntaxError as e:
            print(f"❌ Syntax error: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            print(f"   Error: {e.msg}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_line_1059()
