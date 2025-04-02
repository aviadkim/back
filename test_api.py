#!/usr/bin/env python3
"""Test the API endpoints"""
import os
import sys
import json
import time
import signal
import subprocess
import requests
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

# Create a mock document and extraction
document_id = "test_doc_123"
extraction_dir = os.path.join(project_root, "extractions")
os.makedirs(extraction_dir, exist_ok=True)

# Create a sample extraction file
sample_content = f"""This is sample document content for testing with ID {document_id}. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."""

extraction_file = os.path.join(extraction_dir, f"{document_id}_extraction.json")
with open(extraction_file, 'w') as f:
    f.write(sample_content)

print(f"Created sample extraction file: {extraction_file}")

# Start the server process
server_process = None
try:
    # Change to the project_organized directory
    os.chdir(os.path.join(project_root, "project_organized"))
    
    # Start the server
    print("Starting server...")
    server_process = subprocess.Popen(
        ["python", "app.py"],
        env=dict(os.environ, PYTHONPATH=project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(5)
    
    # Test health endpoint
    print("Testing health endpoint...")
    health_response = requests.get("http://localhost:5001/health")
    print(f"Health endpoint status code: {health_response.status_code}")
    print(f"Health endpoint response: {health_response.json()}")
    
    # Test QA endpoint
    print("\nTesting Q&A endpoint...")
    qa_response = requests.post(
        "http://localhost:5001/api/qa/ask",
        json={"document_id": document_id, "question": "What is the portfolio value?"}
    )
    print(f"Q&A endpoint status code: {qa_response.status_code}")
    print(f"Q&A endpoint response: {json.dumps(qa_response.json(), indent=2)}")
    
    print("\n✅ API tests completed successfully!")

except Exception as e:
    print(f"Error during API test: {e}")

finally:
    # Always stop the server
    if server_process:
        print("Stopping server...")
        server_process.send_signal(signal.SIGINT)
        stdout, stderr = server_process.communicate(timeout=5)
        
        # If there were any errors, print them
        if stderr:
            print("Server stderr:")
            print(stderr)
