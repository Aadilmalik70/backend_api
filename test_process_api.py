#!/usr/bin/env python3
"""
Test script for the /process API endpoint
Tests both Google APIs and fallback functionality
"""

import requests
import json
import os
import sys
from datetime import datetime

def test_process_api():
    """Test the /process API endpoint"""
    
    # API endpoint
    base_url = "http://localhost:5000"
    process_url = f"{base_url}/api/process"
    health_url = f"{base_url}/api/health"
    
    print("[TEST] Testing /process API endpoint")
    print("=" * 50)
    
    # Test data - try both "input" and "keyword" parameters
    test_data_input = {
        "input": "python machine learning tutorial",
        "domain": "education"
    }
    
    test_data_keyword = {
        "keyword": "python machine learning tutorial",
        "domain": "education"
    }
    
    try:
        # First check if the server is running with health check
        print("[HEALTH] Checking server health...")
        try:
            health_response = requests.get(health_url, timeout=10)
            if health_response.status_code == 200:
                health_data = health_response.json()
                print(f"[OK] Server is healthy: {health_data.get('status', 'unknown')}")
                print(f"[INFO] Google APIs enabled: {health_data.get('google_apis', {}).get('enabled', False)}")
                print(f"[INFO] Fallback APIs available: {health_data.get('fallback_apis', {})}")
            else:
                print(f"[WARN] Health check returned status {health_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Server health check failed: {e}")
            print("[TIP] Make sure the Flask server is running with: python src/main.py")
            return False
        
        print("\n[TEST] Testing /process endpoint...")
        
        # Try with "input" parameter first
        print("[TEST] Trying with 'input' parameter...")
        response = requests.post(
            process_url, 
            json=test_data_input,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 400:
            # Try with "keyword" parameter
            print("[TEST] 'input' failed, trying with 'keyword' parameter...")
            response = requests.post(
                process_url, 
                json=test_data_keyword,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[OK] API request successful!")
            
            # Parse response
            result_data = response.json()
            
            # Display key information
            print(f"\n[RESULTS] Processing Results:")
            print(f"   Input: {result_data.get('input', 'N/A')}")
            print(f"   Domain: {result_data.get('domain', 'N/A')}")
            print(f"   Method: {result_data.get('processing_method', 'N/A')}")
            print(f"   Timestamp: {result_data.get('timestamp', 'N/A')}")
            
            # Check Google APIs status
            google_status = result_data.get('google_apis_status', {})
            print(f"\n[APIS] Google APIs Status:")
            print(f"   Enabled: {google_status.get('enabled', False)}")
            print(f"   APIs Used: {', '.join(google_status.get('apis_used', []))}")
            if 'fallback_available' in google_status:
                print(f"   Fallback Available: {google_status.get('fallback_available', False)}")
            
            # Check which components worked
            print(f"\n[COMPONENTS] Component Results:")
            components = [
                'serp_analysis', 'content_analysis', 'entity_analysis', 
                'competitor_analysis', 'serp_optimization', 'content_blueprint',
                'keyword_data', 'performance_prediction', 'export_options'
            ]
            
            for component in components:
                if component in result_data:
                    component_data = result_data[component]
                    if isinstance(component_data, dict) and 'error' in component_data:
                        print(f"   [ERROR] {component}: {component_data['error']}")
                    else:
                        print(f"   [OK] {component}: Success")
                else:
                    print(f"   [SKIP] {component}: Not present")
            
            # Save full response for inspection
            output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVE] Full response saved to: {output_file}")
            
            return True
            
        else:
            print(f"[ERROR] API request failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out (30 seconds)")
        print("[TIP] The API might be processing or server might be slow")
        return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection failed")
        print("[TIP] Make sure the Flask server is running on http://localhost:5000")
        print("[TIP] Start server with: python src/main.py")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_invalid_requests():
    """Test API with invalid requests"""
    print("\n[TEST] Testing invalid requests...")
    
    base_url = "http://localhost:5000"
    process_url = f"{base_url}/api/process"
    
    # Test empty input
    try:
        response = requests.post(
            process_url,
            json={"input": "", "domain": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Empty input test - Status: {response.status_code}")
        if response.status_code == 400:
            print("[OK] Correctly rejected empty input")
        else:
            print("[WARN] Expected 400 status for empty input")
    except Exception as e:
        print(f"[ERROR] Empty input test failed: {e}")
    
    # Test missing input
    try:
        response = requests.post(
            process_url,
            json={"domain": "test"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"Missing input test - Status: {response.status_code}")
        if response.status_code == 400:
            print("[OK] Correctly rejected missing input")
        else:
            print("[WARN] Expected 400 status for missing input")
    except Exception as e:
        print(f"[ERROR] Missing input test failed: {e}")

if __name__ == "__main__":
    print("[SUITE] API Process Endpoint Test Suite")
    print("=" * 50)
    
    # Test main functionality
    success = test_process_api()
    
    if success:
        # Test error handling
        test_invalid_requests()
        print("\n[SUCCESS] Test suite completed successfully!")
    else:
        print("\n[FAIL] Main test failed - skipping additional tests")
        sys.exit(1)