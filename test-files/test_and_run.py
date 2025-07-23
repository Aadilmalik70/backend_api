#!/usr/bin/env python3
"""
Simple script to test and run the main application
"""
import os
import sys
import subprocess

def test_and_run_main():
    """Test and run the main application"""
    
    print("🚀 Testing and Running Main Application")
    print("=" * 40)
    
    # Navigate to the project directory
    project_dir = "C:/Users/oj/Desktop/project/backend_api"
    os.chdir(project_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Test 1: Check if main.py exists
    main_file = "src/main.py"
    if os.path.exists(main_file):
        print("✅ main.py exists")
    else:
        print("❌ main.py not found")
        return
    
    # Test 2: Try to run the main application
    print("\n🔄 Starting main application...")
    
    try:
        # Run the main application
        result = subprocess.run(
            [sys.executable, main_file],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )
        
        print("📤 Application Output:")
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("📥 Error Output:")
            print(result.stderr)
        
        print(f"📊 Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Application started successfully!")
        else:
            print("❌ Application failed to start")
            
            # Try to identify the specific issue
            if "SyntaxError" in result.stderr:
                print("\n🔍 Syntax error detected - attempting to fix...")
                
                # Try to fix the syntax error
                fix_syntax_error(result.stderr)
                
    except subprocess.TimeoutExpired:
        print("⏰ Application startup timed out")
        print("   This might mean the application started successfully and is running")
        print("   You can now try to access it at http://localhost:5000")
        
    except Exception as e:
        print(f"❌ Error running application: {e}")

def fix_syntax_error(stderr_output):
    """Try to fix syntax errors based on the error output"""
    
    if "unmatched '}'" in stderr_output:
        print("🔧 Attempting to fix unmatched brace...")
        
        # Read the content analyzer file
        file_path = "src/content_analyzer_enhanced_real.py"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove any trailing extra braces
            content = content.rstrip()
            
            # Count braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            
            print(f"   Brace count: {open_braces} open, {close_braces} close")
            
            # If there's an extra closing brace, remove it
            if close_braces > open_braces:
                # Find and remove the last extra closing brace
                content = content.rstrip('}').rstrip()
                
                # Make sure it ends with exactly one closing brace
                if not content.endswith('}'):
                    content += '}'
                
                print("   Removed extra closing brace")
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Syntax error fixed - try running the application again")
            
        except Exception as e:
            print(f"❌ Failed to fix syntax error: {e}")

if __name__ == "__main__":
    test_and_run_main()
