#!/usr/bin/env python3
"""
Quick syntax check for content_analyzer_enhanced_real.py
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🔍 Checking syntax of content_analyzer_enhanced_real.py...")
    
    # Import the file to check for syntax errors
    from content_analyzer_enhanced_real import ContentAnalyzerEnhancedReal
    
    print("✅ Content analyzer syntax is correct!")
    
    # Try to initialize it
    print("🔧 Testing initialization...")
    analyzer = ContentAnalyzerEnhancedReal()
    print("✅ Content analyzer initialized successfully!")
    
    # Check client status
    print("📊 Checking client status...")
    status = analyzer.get_client_status()
    print(f"✅ Client status retrieved: {len(status)} clients")
    
    print("\n🎉 All syntax checks passed!")
    
except SyntaxError as e:
    print(f"❌ Syntax error in content_analyzer_enhanced_real.py:")
    print(f"   Line {e.lineno}: {e.text}")
    print(f"   Error: {e.msg}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
