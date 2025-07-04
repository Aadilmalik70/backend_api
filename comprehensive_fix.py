#!/usr/bin/env python3
"""
Comprehensive fix for the content analyzer syntax issue
"""
import os
import sys
import ast

def comprehensive_fix():
    """Comprehensive fix for the content analyzer"""
    
    print("🔧 Comprehensive Content Analyzer Fix")
    print("=" * 40)
    
    # Change to the project directory
    os.chdir("C:/Users/oj/Desktop/project/backend_api")
    
    file_path = "src/content_analyzer_enhanced_real.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"📁 Working with: {file_path}")
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 Original file: {len(content)} characters, {len(content.splitlines())} lines")
        
        # Check for syntax errors
        try:
            ast.parse(content)
            print("✅ AST parsing successful - syntax is valid")
        except SyntaxError as e:
            print(f"❌ Syntax error found: {e}")
            print(f"   Line {e.lineno}: {e.text}")
            
            # Try to fix common issues
            print("🔧 Attempting to fix syntax issues...")
            
            # Check for unmatched braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            if open_braces != close_braces:
                print(f"   Brace mismatch: {open_braces} open, {close_braces} close")
                
                # If we have an extra closing brace, remove it
                if close_braces > open_braces:
                    # Remove the last extra closing brace
                    content = content.rstrip()
                    if content.endswith('}'):
                        content = content[:-1]
                    print("   Removed extra closing brace")
        
        # Clean up the file
        content = content.rstrip()
        
        # Ensure the file ends properly (it should end with a closing brace for the last method)
        if not content.endswith('}'):
            content += '}'
            print("   Added missing closing brace")
        
        # Try to parse again
        try:
            ast.parse(content)
            print("✅ Fixed syntax is valid")
        except SyntaxError as e:
            print(f"❌ Still has syntax error: {e}")
            return False
        
        # Save the fixed file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ File saved: {len(content)} characters")
        
        # Test the import
        print("\n🧪 Testing import...")
        sys.path.insert(0, "src")
        
        try:
            # Clear any cached modules
            if 'content_analyzer_enhanced_real' in sys.modules:
                del sys.modules['content_analyzer_enhanced_real']
            
            from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
            print("✅ Import successful")
            
            # Test initialization
            analyzer = ContentAnalyzerEnhancedReal()
            print("✅ Initialization successful")
            
            # Test a method
            status = analyzer.get_client_status()
            print(f"✅ Method test successful: {len(status)} clients")
            
            return True
            
        except Exception as e:
            print(f"❌ Import/initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if comprehensive_fix():
        print("\n🎉 Content analyzer has been successfully fixed!")
        print("   You can now run: python src/main.py")
    else:
        print("\n❌ Failed to fix content analyzer")
