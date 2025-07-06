#!/usr/bin/env python3
"""
Force Real Google APIs Usage (Disable Fallback)
"""

import os

def disable_fallback():
    """Disable fallback and force real Google APIs usage"""
    print("🔧 Disabling fallback to force real Google APIs usage...")
    
    # Set environment variables for current session
    os.environ['FALLBACK_TO_SERPAPI'] = 'false'
    os.environ['USE_GOOGLE_APIS'] = 'true'
    
    # Update .env file
    env_file = '.env'
    lines = []
    
    # Read existing .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    
    # Update or add the settings
    updated_lines = []
    settings_found = set()
    
    for line in lines:
        if line.strip().startswith('FALLBACK_TO_SERPAPI='):
            updated_lines.append('FALLBACK_TO_SERPAPI=false\\n')
            settings_found.add('FALLBACK_TO_SERPAPI')
        elif line.strip().startswith('USE_GOOGLE_APIS='):
            updated_lines.append('USE_GOOGLE_APIS=true\\n')
            settings_found.add('USE_GOOGLE_APIS')
        else:
            updated_lines.append(line)
    
    # Add missing settings
    if 'FALLBACK_TO_SERPAPI' not in settings_found:
        updated_lines.append('FALLBACK_TO_SERPAPI=false\\n')
    if 'USE_GOOGLE_APIS' not in settings_found:
        updated_lines.append('USE_GOOGLE_APIS=true\\n')
    
    # Write back to .env file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ Fallback disabled successfully")
    print("✅ Google APIs forced as primary")
    print("✅ Updated .env file")
    
    # Show current settings
    print("\\n📋 Current settings:")
    print(f"FALLBACK_TO_SERPAPI={os.environ.get('FALLBACK_TO_SERPAPI', 'not set')}")
    print(f"USE_GOOGLE_APIS={os.environ.get('USE_GOOGLE_APIS', 'not set')}")

if __name__ == "__main__":
    disable_fallback()
    print("\\n🎯 Now run your tests - they will use real Google APIs only!")
    print("Commands to run:")
    print("1. python test_direct_apis.py")
    print("2. python test_google_apis_connection.py")
    print("3. python test_real_keyword_processing.py")
