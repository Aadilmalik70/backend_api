"""
Update your .env file with the correct Custom Search Engine ID
"""

import os
from pathlib import Path

def update_env_with_search_id():
    """Update .env file with the correct Custom Search Engine ID"""
    
    # Your correct Search Engine ID from the screenshot
    correct_search_id = "a60466b73e52647f2"
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the incorrect Custom Search Engine ID
    old_patterns = [
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="AIzaSyDGBM56i_W4YD8TrAtnSaHAe1uu8oTp4xU"',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="YOUR_SEARCH_ENGINE_ID_HERE"',
        'GOOGLE_CUSTOM_SEARCH_ENGINE_ID=YOUR_SEARCH_ENGINE_ID_HERE',
    ]
    
    new_line = f'GOOGLE_CUSTOM_SEARCH_ENGINE_ID="{correct_search_id}"'
    
    updated = False
    for old_pattern in old_patterns:
        if old_pattern in content:
            content = content.replace(old_pattern, new_line)
            updated = True
            print(f"✅ Updated: {old_pattern}")
            break
    
    # If no exact match found, try to find any line with GOOGLE_CUSTOM_SEARCH_ENGINE_ID
    if not updated:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('GOOGLE_CUSTOM_SEARCH_ENGINE_ID=') or line.startswith('# WRONG: GOOGLE_CUSTOM_SEARCH_ENGINE_ID='):
                lines[i] = new_line
                updated = True
                print(f"✅ Updated line: {line}")
                break
        content = '\n'.join(lines)
    
    # If still not found, add it
    if not updated:
        content += f'\n{new_line}\n'
        print("✅ Added new Custom Search Engine ID")
        updated = True
    
    if updated:
        # Write back to file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated .env file with Search Engine ID: {correct_search_id}")
        return True
    else:
        print("❌ Could not update .env file")
        return False

def verify_update():
    """Verify the update was successful"""
    print("\n🔍 Verifying update...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    search_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
    
    if search_id == "a60466b73e52647f2":
        print("✅ Custom Search Engine ID correctly set!")
        return True
    else:
        print(f"❌ Custom Search Engine ID is: {search_id}")
        print("Expected: a60466b73e52647f2")
        return False

def main():
    print("🔧 Updating Custom Search Engine ID")
    print("=" * 40)
    print("From your screenshot, your Search Engine ID is: a60466b73e52647f2")
    print()
    
    # Update the .env file
    if update_env_with_search_id():
        # Verify the update
        if verify_update():
            print("\n🎉 Success! Your Custom Search Engine is now configured correctly.")
            print("\n📋 What's configured now:")
            print("   ✅ Custom Search Engine ID: a60466b73e52647f2")
            print("   ✅ Search Engine Name: serpstrategists.com")
            print("   ✅ Search the entire web: Enabled")
            print("\n🚀 Next steps:")
            print("   1. Install SerpAPI: pip install google-search-results")
            print("   2. Test: python verify_google_apis.py")
            print("   3. If you need Search Console/Natural Language, get service account credentials")
        else:
            print("\n❌ Update failed. Please manually update your .env file:")
            print('   GOOGLE_CUSTOM_SEARCH_ENGINE_ID="a60466b73e52647f2"')
    else:
        print("\n❌ Could not update .env file automatically.")
        print("Please manually add this line to your .env file:")
        print('GOOGLE_CUSTOM_SEARCH_ENGINE_ID="a60466b73e52647f2"')

if __name__ == "__main__":
    main()
