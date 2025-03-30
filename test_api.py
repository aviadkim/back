import subprocess
import time
import requests
import os
import sys
import json
import signal
import threading

def run_server():
    try:
        server_process = subprocess.Popen(['python', 'app.py'], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
        return server_process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def test_health_endpoint():
    max_attempts = 20
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5000/health')
            if response.status_code == 200:
                print(f"Health endpoint test: SUCCESS (Status: {response.status_code})")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"Health endpoint returned: {response.status_code}, retrying...")
        except requests.exceptions.ConnectionError:
            print(f"Server not ready, attempt {attempt+1}/{max_attempts}...")
        time.sleep(1)
    
    print("Health endpoint test: FAILED - Server did not become ready")
    return False

def test_upload_endpoint():
    try:
        if not os.path.exists('test_files/test_invoice.pdf'):
            print("Test PDF not found, skipping upload test")
            return False
            
        files = {'file': open('test_files/test_invoice.pdf', 'rb')}
        data = {'language': 'he'}
        response = requests.post('http://localhost:5000/api/pdf/upload', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Upload endpoint test: SUCCESS (Status: {response.status_code})")
            print(f"Document ID: {result.get('document_id')}")
            return result.get('document_id')
        else:
            print(f"Upload endpoint test: FAILED (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Upload endpoint test: ERROR - {str(e)}")
        return None

def test_chat_endpoint(document_id):
    if not document_id:
        print("No document ID available, skipping chat test")
        return False
        
    try:
        data = {
            'message': 'What is the total amount on this invoice?',
            'document_ids': [document_id],
            'language': 'he'
        }
        response = requests.post('http://localhost:5000/api/copilot/route', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Chat endpoint test: SUCCESS (Status: {response.status_code})")
            print(f"Bot response: {result.get('response')}")
            return True
        else:
            print(f"Chat endpoint test: FAILED (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Chat endpoint test: ERROR - {str(e)}")
        return False

def run_tests():
    print("Starting test suite...")
    server_process = run_server()
    
    if not server_process:
        print("Could not start server for testing")
        return
    
    try:
        # Wait for server to start
        server_ready = test_health_endpoint()
        
        if server_ready:
            # Test document upload
            document_id = test_upload_endpoint()
            
            # Test chat functionality
            if document_id:
                test_chat_endpoint(document_id)
    finally:
        print("Tests completed, shutting down server...")
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_tests()
