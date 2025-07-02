"""
Quick Fix Script for Google APIs Setup Issues
Addresses the specific problems found in your verification
"""

import os
import sys
from pathlib import Path

def fix_credentials_path():
    """Fix the corrupted credentials path in .env file"""
    print("🔧 Fixing credentials path...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read current .env content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Fix the corrupted path
    old_path = "C:\\Users\\oj\\Desktop\\projecackend_api"
    new_path = "C:\\Users\\oj\\Desktop\\project\\backend_api\\credentials\\google-apis-credentials.json"
    
    if old_path in content:
        content = content.replace(old_path, new_path)
        
        # Write back to .env file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed credentials path to: {new_path}")
        return True
    else:
        print("⚠️ Corrupted path not found in .env file")
        print("Current GOOGLE_APPLICATION_CREDENTIALS value:")
        
        # Show current value
        for line in content.split('\n'):
            if line.startswith('GOOGLE_APPLICATION_CREDENTIALS='):
                print(f"   {line}")
                break
        
        return False

def create_credentials_directory():
    """Ensure credentials directory exists"""
    print("📁 Creating credentials directory...")
    
    creds_dir = Path('credentials')
    creds_dir.mkdir(exist_ok=True)
    
    print("✅ Credentials directory ready")
    return True

def check_credentials_file():
    """Check if the credentials file exists"""
    creds_path = Path('credentials/google-apis-credentials.json')
    
    if creds_path.exists():
        print("✅ Service account credentials file found")
        return True
    else:
        print("❌ Service account credentials file NOT found")
        print(f"Expected location: {creds_path.absolute()}")
        print("\n📋 To get your credentials file:")
        print("1. Go to https://console.cloud.google.com")
        print("2. Select your project")
        print("3. Go to IAM & Admin > Service Accounts")
        print("4. Create service account (or use existing)")
        print("5. Click on service account > Keys > Add Key > Create New Key > JSON")
        print("6. Download the JSON file")
        print("7. Save it as: credentials/google-apis-credentials.json")
        return False

def install_missing_dependencies():
    """Install missing dependencies"""
    print("📦 Installing missing dependencies...")
    
    try:
        import subprocess
        
        # Install serpapi for fallback functionality
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'google-search-results'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SerpAPI package installed successfully")
        else:
            print("⚠️ Failed to install SerpAPI package")
            print(f"Error: {result.stderr}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_sample_credentials_template():
    """Create a template for credentials file"""
    template_path = Path('credentials/credentials-template.json')
    
    template_content = '''{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project-id.iam.gserviceaccount.com"
}'''
    
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"📝 Created credentials template: {template_path}")
    print("   Replace this template with your actual service account JSON file")

def main():
    """Main fix function"""
    print("🔧 Google APIs Quick Fix")
    print("=" * 40)
    print()
    
    # Step 1: Fix credentials path
    path_fixed = fix_credentials_path()
    
    # Step 2: Create credentials directory
    create_credentials_directory()
    
    # Step 3: Check credentials file
    creds_exists = check_credentials_file()
    
    if not creds_exists:
        create_sample_credentials_template()
    
    # Step 4: Install missing dependencies
    deps_installed = install_missing_dependencies()
    
    print("\n" + "=" * 40)
    print("📊 Fix Summary:")
    print(f"   Credentials path fixed: {'✅' if path_fixed else '❌'}")
    print(f"   Credentials file exists: {'✅' if creds_exists else '❌'}")
    print(f"   Dependencies installed: {'✅' if deps_installed else '❌'}")
    
    if creds_exists and deps_installed:
        print("\n🎉 All issues fixed! Run verification again:")
        print("   python verify_google_apis.py")
    else:
        print("\n⚠️ Additional steps needed:")
        if not creds_exists:
            print("   • Download service account JSON file to credentials/ directory")
        if not deps_installed:
            print("   • Install SerpAPI: pip install google-search-results")
        
        print("\n📖 For detailed setup: See GOOGLE_APIS_SETUP.md")

if __name__ == "__main__":
    main()
