import requests
import sys
import os

def test_upload_endpoint(file_path, base_url="http://localhost:5001"):
    """Test the upload endpoint with a file"""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return
    
    print(f"Testing upload endpoint with file: {file_path}")
    
    # Prepare form data
    files = {'file': open(file_path, 'rb')}
    data = {'language': 'heb+eng'}
    
    try:
        # Make the request
        response = requests.post(f"{base_url}/api/documents/upload", files=files, data=data)
        
        print(f"Status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        # Try to get the response as text
        response_text = response.text
        print(f"Response text: {response_text}")
        
        # Try to parse as JSON if possible
        try:
            result = response.json()
            print(f"Parsed JSON: {result}")
        except Exception as e:
            print(f"Error parsing JSON: {e}")
        
    except Exception as e:
        print(f"Request error: {e}")
    finally:
        files['file'].close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_upload_endpoint.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_upload_endpoint(file_path)
