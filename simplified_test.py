import os
import sys
import subprocess
import time
import json

def run_app_in_background():
    # Check if Python modules are installed
    try:
        # Start the application in background
        print("Starting Flask application in background...")
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print(f"Error starting application: {e}")
        return None

def test_with_curl():
    print("\n=== TESTING WITH CURL ===")
    # Allow some time for the server to start
    time.sleep(5)
    
    # Test health endpoint
    print("\nTesting health endpoint...")
    health_result = os.system("curl -s http://localhost:5000/health")
    print(f"Health endpoint test result: {health_result}")
    
    # Test PDF upload endpoint
    if os.path.exists("test_files/test_invoice.pdf"):
        print("\nTesting PDF upload...")
        upload_result = os.system(
            "curl -s -F 'file=@test_files/test_invoice.pdf' -F 'language=he' http://localhost:5000/api/pdf/upload"
        )
        print(f"Upload endpoint test result: {upload_result}")
    else:
        print("Test PDF file not found, skipping upload test")

def main():
    print("=== SIMPLIFIED TEST SCRIPT ===")
    print("Testing basic Flask app functionality...")
    
    # First, check if .env file exists
    if not os.path.exists(".env"):
        print("Creating .env file from example...")
        if os.path.exists(".env.example"):
            os.system("cp .env.example .env")
            print("Created .env file from example. You'll need to edit it with your API keys.")
        else:
            print("No .env.example file found to create .env from")
    
    # Create required directories
    print("\nCreating required directories...")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    print("Directories created successfully")
    
    # Test MongoDB connection
    print("\nTesting MongoDB connection...")
    mongo_test = """
import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')

try:
    print(f"Attempting to connect to MongoDB at {mongo_uri}")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # Will throw exception if cannot connect
    print("MongoDB connection successful!")
except errors.ServerSelectionTimeoutError as e:
    print(f"MongoDB connection failed: {e}")
    print("MongoDB may not be running. You'll need to start it separately.")
except Exception as e:
    print(f"Unexpected error with MongoDB: {e}")
    """
    
    with open("test_mongo.py", "w") as f:
        f.write(mongo_test)
    
    os.system("python test_mongo.py")
    
    # Start the application and test endpoints
    app_process = run_app_in_background()
    
    if app_process:
        try:
            test_with_curl()
        finally:
            print("\nStopping Flask application...")
            app_process.terminate()
    
    print("\n=== TEST SUMMARY ===")
    print("Basic testing completed. Check the output above for results.")
    print("\nTo run the application manually, use:")
    print("python app.py")
    
    print("\nTo deploy to AWS:")
    print("1. Ensure your AWS credentials are set as GitHub secrets")
    print("2. Push to the master branch or manually trigger the workflow in GitHub Actions")

if __name__ == "__main__":
    main()
