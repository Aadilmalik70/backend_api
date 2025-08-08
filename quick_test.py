import requests
import json

# Test the health endpoint first
try:
    print("Testing health endpoint...")
    health_response = requests.get("http://localhost:5000/api/health", timeout=5)
    print(f"Health Status: {health_response.status_code}")
    if health_response.status_code == 200:
        print(json.dumps(health_response.json(), indent=2))
except Exception as e:
    print(f"Health check failed: {e}")

# Test the process endpoint
try:
    print("\nTesting process endpoint with 'input'...")
    process_response = requests.post(
        "http://localhost:5000/api/process",
        json={"input": "python tutorial", "domain": "education"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    print(f"Process Status: {process_response.status_code}")
    if process_response.status_code != 200:
        print("Response:", process_response.text)
        
        # Try with keyword parameter
        print("\nTesting process endpoint with 'keyword'...")
        process_response = requests.post(
            "http://localhost:5000/api/process",
            json={"keyword": "python tutorial", "domain": "education"},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        print(f"Process Status: {process_response.status_code}")
        print("Response:", process_response.text[:500] + "..." if len(process_response.text) > 500 else process_response.text)
    else:
        response_data = process_response.json()
        print("Success! Key fields:")
        print(f"- Processing method: {response_data.get('processing_method')}")
        print(f"- Components: {list(response_data.keys())}")
        
except Exception as e:
    print(f"Process test failed: {e}")