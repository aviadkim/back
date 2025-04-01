import requests
import os
import sys
import json

def test_health_endpoint(base_url):
    """Test if the application is up and responding to requests."""
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health endpoint is working")
            print(f"Response: {response.json()}")
            return True
        else:
            print("❌ Health endpoint returned non-200 status code")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing health endpoint: {str(e)}")
        return False

def test_api_endpoint(base_url, endpoint):
    """Test if an API endpoint is accessible."""
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"API endpoint {endpoint} status: {response.status_code}")
        if response.status_code in [200, 404]:  # 404 is okay if endpoint requires parameters
            print(f"✅ API endpoint {endpoint} is accessible")
            return True
        else:
            print(f"❌ API endpoint {endpoint} returned unexpected status code")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error accessing API endpoint {endpoint}: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        base_url = "http://localhost:5001"
        print(f"No base URL provided, using default: {base_url}")
    else:
        base_url = sys.argv[1]
    
    print(f"Testing API at {base_url}...")
    
    # Test health endpoint
    health_ok = test_health_endpoint(base_url)
    
    # Test API endpoints
    api_endpoints = [
        "/api/documents",
        "/api/documents/upload"
    ]
    
    api_status = []
    for endpoint in api_endpoints:
        status = test_api_endpoint(base_url, endpoint)
        api_status.append((endpoint, status))
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Health Endpoint: {'✅ OK' if health_ok else '❌ Failed'}")
    print("API Endpoints:")
    for endpoint, status in api_status:
        print(f"  {endpoint}: {'✅ OK' if status else '❌ Failed'}")
    
    overall_status = health_ok and all(status for _, status in api_status)
    print(f"\nOverall Status: {'✅ OK' if overall_status else '❌ Issues Found'}")

if __name__ == "__main__":
    main()
