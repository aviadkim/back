#!/usr/bin/env python
import os
import sys
import subprocess
import time
import json
import requests
import threading
import webbrowser
from urllib.parse import urljoin

def check_environment():
    """Check if all required environment variables and directories exist"""
    print("\n=== CHECKING ENVIRONMENT ===")
    
    # Check directories
    required_dirs = ["uploads", "data", "data/embeddings", "logs"]
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory exists: {directory}")
    
    # Check .env file
    if not os.path.exists(".env"):
        print("Creating .env file from example...")
        if os.path.exists(".env.example"):
            os.system("cp .env.example .env")
            print("Created .env file from example.")
        else:
            print("Warning: No .env.example file found")
            return False
    else:
        print(".env file exists")
    
    return True

def check_mongodb():
    """Check MongoDB connection and start if needed"""
    print("\n=== CHECKING MONGODB ===")
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        info = client.server_info()
        print(f"MongoDB is running (version: {info.get('version', 'unknown')})")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Attempting to start MongoDB via docker-compose...")
        try:
            subprocess.run(["docker-compose", "up", "-d", "mongodb"], check=True)
            print("Waiting for MongoDB to start...")
            time.sleep(5)
            
            # Try connecting again
            try:
                client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
                client.server_info()
                print("MongoDB is now running")
                return True
            except Exception as retry_e:
                print(f"Still couldn't connect to MongoDB: {retry_e}")
                return False
        except Exception as docker_e:
            print(f"Failed to start MongoDB with docker-compose: {docker_e}")
            return False

def create_test_document():
    """Create a test document for upload testing"""
    print("\n=== CREATING TEST DOCUMENT ===")
    test_file_path = "test_files/test_invoice.pdf"
    
    if os.path.exists(test_file_path):
        print(f"Test document already exists: {test_file_path}")
        return test_file_path
    
    # Ensure directory exists
    os.makedirs("test_files", exist_ok=True)
    
    # Try to create a PDF with fpdf
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="TEST INVOICE", ln=True, align='C')
        pdf.cell(200, 10, txt="Invoice #: TEST-2025-001", ln=True)
        pdf.cell(200, 10, txt="Date: March 30, 2025", ln=True)
        pdf.cell(200, 10, txt="Amount: 1,000 NIS", ln=True)
        pdf.output(test_file_path)
        print(f"Created test PDF: {test_file_path}")
        return test_file_path
    except Exception as e:
        print(f"Error creating PDF: {e}")
        # Create a simple text file as fallback
        fallback_path = "test_files/test_document.txt"
        with open(fallback_path, "w") as f:
            f.write("TEST INVOICE\nInvoice #: TEST-2025-001\nDate: March 30, 2025\nAmount: 1,000 NIS")
        print(f"Created fallback test document: {fallback_path}")
        return fallback_path

def run_flask_app():
    """Run the Flask app in a separate thread"""
    try:
        from app import app
        
        # Configure the app to run on port 5000
        app.config['SERVER_NAME'] = 'localhost:5000'
        
        # Start the app in a separate thread
        threading.Thread(target=app.run, kwargs={'debug': False, 'threaded': True}).start()
        print("Flask app started on http://localhost:5000")
        return True
    except Exception as e:
        print(f"Failed to start Flask app: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n=== TESTING API ENDPOINTS ===")
    base_url = "http://localhost:5000"
    endpoints = [
        {"path": "/health", "method": "GET", "expected_status": 200},
    ]
    
    # Wait for the server to start
    print("Waiting for server to start...")
    for _ in range(5):
        try:
            response = requests.get(urljoin(base_url, "/health"))
            if response.status_code == 200:
                print("Server is up!")
                break
        except requests.exceptions.ConnectionError:
            print(".", end="", flush=True)
            time.sleep(1)
    print()
    
    # Test each endpoint
    results = []
    for endpoint in endpoints:
        path = endpoint["path"]
        method = endpoint["method"]
        expected_status = endpoint["expected_status"]
        
        try:
            if method == "GET":
                response = requests.get(urljoin(base_url, path))
            elif method == "POST":
                response = requests.post(urljoin(base_url, path))
            
            if response.status_code == expected_status:
                status = "PASSED"
            else:
                status = f"FAILED (Status: {response.status_code}, Expected: {expected_status})"
            
            results.append({
                "endpoint": path,
                "method": method,
                "status": status,
                "response": response.json() if response.status_code == 200 else None
            })
        except Exception as e:
            results.append({
                "endpoint": path,
                "method": method,
                "status": f"ERROR: {str(e)}",
                "response": None
            })
    
    # Print results
    for result in results:
        print(f"{result['method']} {result['endpoint']}: {result['status']}")
        if result['response']:
            print(f"  Response: {json.dumps(result['response'], indent=2)}")
    
    # Return True if all tests passed
    return all(result["status"] == "PASSED" for result in results)

def open_browser():
    """Open the browser to view the app"""
    time.sleep(2)  # Wait for the app to start
    webbrowser.open("http://localhost:5000")
    print("\nOpened browser to view the application.")
    print("Press Ctrl+C to exit when finished.")

def main():
    """Main function to run all tests"""
    print("=== COMPREHENSIVE SYSTEM TEST ===")
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("Environment setup has issues. Please fix them before continuing.")
    
    # Check MongoDB
    mongo_ok = check_mongodb()
    if not mongo_ok:
        print("MongoDB is not running. Please start it manually with 'docker-compose up -d'.")
    
    # Create test document
    test_doc_path = create_test_document()
    
    # Start the Flask app
    app_started = run_flask_app()
    if not app_started:
        print("Failed to start the Flask app. Please check the errors and fix them.")
        return
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    # Open browser
    open_browser()
    
    # Keep the script running until interrupted
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest completed. Shutting down...")

if __name__ == "__main__":
    main()
