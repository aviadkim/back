import requests
import threading
import time
import sys
from app import app

def run_flask_app():
    app.run(host='127.0.0.1', port=5000)

if __name__ == "__main__":
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Give the server a moment to start
    time.sleep(2)
    
    # Test health endpoint
    try:
        response = requests.get('http://127.0.0.1:5000/health')
        if response.status_code == 200:
            print(f"✅ Health endpoint working: {response.json()}")
        else:
            print(f"❌ Health endpoint returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to health endpoint: {e}")
    
    # Test upload endpoint (without actually uploading)
    try:
        response = requests.post('http://127.0.0.1:5000/api/upload')
        if response.status_code in [400, 405]:
            print("✅ Upload endpoint exists (returns expected error without file)")
        else:
            print(f"❓ Upload endpoint returned unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to upload endpoint: {e}")
    
    sys.exit(0)  # Exit the script (and kill the Flask thread)
