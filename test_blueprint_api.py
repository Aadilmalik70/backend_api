import requests
import json

def test_blueprint_generation():
    """Test the main blueprint generation endpoint"""
    print("[TEST] Testing blueprint generation API")
    print("=" * 50)
    
    # Test the main blueprint endpoint
    blueprint_url = "http://localhost:5000/api/blueprints/generate"
    
    test_data = {
        "keyword": "python machine learning tutorial",
        "num_competitors": 5
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-User-ID": "test-user-123"  # Based on the authentication note
    }
    
    try:
        print(f"[REQUEST] POST {blueprint_url}")
        print(f"[DATA] {json.dumps(test_data, indent=2)}")
        print(f"[HEADERS] {json.dumps(headers, indent=2)}")
        
        response = requests.post(
            blueprint_url,
            json=test_data,
            headers=headers,
            timeout=60  # Longer timeout for blueprint generation
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS] Blueprint generation successful!")
            result_data = response.json()
            
            # Display key information
            print(f"\n[RESULTS] Blueprint Generation Results:")
            for key, value in result_data.items():
                if isinstance(value, dict):
                    print(f"   {key}: {len(value)} items" if value else f"   {key}: empty")
                elif isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                else:
                    print(f"   {key}: {str(value)[:100]}...")
            
            # Save result
            with open("blueprint_result.json", "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            print(f"\n[SAVE] Full result saved to blueprint_result.json")
            
            return True
        else:
            print(f"[ERROR] Request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"[ERROR] Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"[ERROR] Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out (60 seconds)")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False

def test_legacy_process():
    """Test the legacy process endpoint with correct parameters"""
    print("\n[TEST] Testing legacy process endpoint")
    print("=" * 40)
    
    process_url = "http://localhost:5000/api/process"
    
    # Based on the code, it expects 'input' parameter
    test_data = {
        "input": "python machine learning tutorial",
        "domain": "education"
    }
    
    try:
        response = requests.post(
            process_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"[RESPONSE] Status: {response.status_code}")
        
        if response.status_code == 200:
            print("[SUCCESS] Legacy process successful!")
            result_data = response.json()
            print(f"[INFO] Processing method: {result_data.get('processing_method')}")
            print(f"[INFO] Available components: {list(result_data.keys())}")
            return True
        else:
            print(f"[ERROR] Legacy process failed: {response.status_code}")
            print(f"[ERROR] Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Legacy process error: {e}")
        return False

if __name__ == "__main__":
    print("[SUITE] Blueprint API Test Suite")
    print("=" * 50)
    
    # Test health first
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("[OK] Server is healthy")
        else:
            print(f"[WARN] Health check returned {health_response.status_code}")
    except:
        print("[ERROR] Health check failed - server might not be running")
        exit(1)
    
    # Test main blueprint generation
    blueprint_success = test_blueprint_generation()
    
    # Test legacy endpoint
    legacy_success = test_legacy_process()
    
    if blueprint_success or legacy_success:
        print("\n[SUCCESS] At least one API endpoint is working!")
    else:
        print("\n[FAIL] All API tests failed")