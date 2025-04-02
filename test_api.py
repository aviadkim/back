import requests
import json

def test_api():
    try:
        # Test documents endpoint
        response = requests.get('http://localhost:5001/api/documents')
        print("Status code:", response.status_code)
        print("Response headers:", response.headers)
        
        # Try to parse the JSON
        try:
            data = response.json()
            print("Documents API response (parsed):", json.dumps(data, indent=2))
        except Exception as e:
            print("Error parsing JSON:", e)
            print("Raw response:", response.text)
            
        print("\n" + "-"*50 + "\n")
        
        # Test upload endpoint with minimal data
        response = requests.post('http://localhost:5001/api/documents/upload', data={'language': 'heb+eng'})
        print("Upload endpoint status code:", response.status_code)
        print("Upload response text:", response.text)
        
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_api()
