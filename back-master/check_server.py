
import requests
import sys

try:
    response = requests.get('http://localhost:5001/health')
    if response.status_code == 200:
        print("Server is running, can test endpoints")
        sys.exit(0)
    else:
        print(f"Server responded with status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Server not running: {e}")
    sys.exit(1)
