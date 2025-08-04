#!/usr/bin/env python3
"""
Health check script for SERP Strategist API
Used by Docker HEALTHCHECK instruction
"""

import sys
import requests
import os
from time import sleep

def check_health():
    """Check if the application is healthy"""
    try:
        # Get the port from environment or use default
        port = os.environ.get('FLASK_PORT', '5000')
        url = f"http://localhost:{port}/api/health"
        
        # Make health check request with timeout
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("Health check passed")
                return True
            else:
                print(f"Health check failed: {data}")
                return False
        else:
            print(f"Health check failed with status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Health check failed with exception: {e}")
        return False
    except Exception as e:
        print(f"Health check failed with unexpected error: {e}")
        return False

def main():
    """Main health check function"""
    # Perform health check
    if check_health():
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()