import requests
import json
import sys

def test_authentication(base_url="http://localhost:5001"):
    """Test authentication endpoints"""
    print("Testing authentication...")
    
    # Register a test user
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        # Register
        print("\nTesting registration...")
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 201 and "already" not in response.text:
            print("Registration failed!")
            return False
        
        # Login
        print("\nTesting login...")
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Login failed!")
            return False
        
        # Extract token
        token = response.json().get('token')
        if not token:
            print("No token received!")
            return False
        
        print("Successfully received token!")
        
        # Test profile access
        print("\nTesting profile access...")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(f"{base_url}/api/auth/profile", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Profile access failed!")
            return False
        
        print("Successfully accessed profile!")
        print(json.dumps(response.json(), indent=2))
        
        return True
    
    except Exception as e:
        print(f"Error during authentication test: {e}")
        return False

if __name__ == "__main__":
    success = test_authentication()
    sys.exit(0 if success else 1)
