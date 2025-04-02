#!/usr/bin/env python3

"""
Test script for Vertical Slice Architecture implementation
"""

import os
import json
import requests
import time
import sys

# Default URL
BASE_URL = "http://localhost:5001"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"    {text}")
    print("=" * 80)

def run_test(name, func):
    """Run a test and print the result"""
    print(f"\n> Running test: {name}")
    try:
        result = func()
        print(f"  ✅ PASS: {name}")
        return result
    except Exception as e:
        print(f"  ❌ FAIL: {name}")
        print(f"  Error: {e}")
        return None

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    response.raise_for_status()
    data = response.json()
    assert data["status"] == "ok"
    print(f"  Version: {data.get('version', 'unknown')}")
    return data

def test_document_list():
    """Test getting the document list"""
    response = requests.get(f"{BASE_URL}/api/documents")
    response.raise_for_status()
    data = response.json()
    print(f"  Found {len(data)} documents")
    return data

def test_document_chat():
    """Test the document chat feature"""
    # Create a chat session
    response = requests.post(
        f"{BASE_URL}/api/chat/sessions", 
        json={"userId": "test_user", "documents": ["test_document"]}
    )
    response.raise_for_status()
    data = response.json()
    session_id = data["session_id"]
    print(f"  Created chat session: {session_id}")
    
    # Send a message
    response = requests.post(
        f"{BASE_URL}/api/chat/sessions/{session_id}/messages",
        json={"message": "What is the total assets value?"}
    )
    response.raise_for_status()
    data = response.json()
    print(f"  Bot response: {data['response']['answer'][:50]}...")
    
    # Get session history
    response = requests.get(f"{BASE_URL}/api/chat/sessions/{session_id}/history")
    response.raise_for_status()
    data = response.json()
    print(f"  Session has {len(data['history'])} messages")
    
    return session_id

def test_document_suggestions():
    """Test getting suggested questions for a document"""
    document_id = "test_document"
    response = requests.get(f"{BASE_URL}/api/chat/documents/{document_id}/suggestions")
    response.raise_for_status()
    data = response.json()
    suggestions = data["suggestions"]
    print(f"  Found {len(suggestions)} suggested questions")
    if suggestions:
        print(f"  First suggestion: {suggestions[0]['text']}")
    return suggestions

def test_tables_feature():
    """Test the table extraction feature"""
    document_id = "test_document"
    
    # Get document tables
    response = requests.get(f"{BASE_URL}/api/tables/document/{document_id}")
    response.raise_for_status()
    data = response.json()
    tables = data["tables"]
    print(f"  Found {len(tables)} tables in document")
    
    if not tables:
        return None
    
    # Get a specific table
    table_id = tables[0]["id"]
    response = requests.get(f"{BASE_URL}/api/tables/{table_id}")
    response.raise_for_status()
    data = response.json()
    table = data["table"]
    print(f"  Retrieved table: {table['name']}")
    
    # Generate a table view (summary)
    response = requests.post(
        f"{BASE_URL}/api/tables/generate",
        json={
            "documentId": document_id,
            "tableIds": [table_id],
            "format": "summary"
        }
    )
    response.raise_for_status()
    data = response.json()
    summary = data["table"]
    print(f"  Generated summary view with {len(summary.get('metrics', []))} metrics")
    
    return tables

def test_pdf_scanning():
    """Test the PDF scanning feature if a test file is available"""
    pdf_files = [f for f in os.listdir("uploads") if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print("  No PDF files found in uploads/ directory, skipping test")
        return None
    
    test_file = pdf_files[0]
    print(f"  Testing with PDF file: {test_file}")
    
    with open(os.path.join("uploads", test_file), "rb") as f:
        files = {"file": (test_file, f)}
        response = requests.post(
            f"{BASE_URL}/api/pdf/upload",
            files=files
        )
    
    try:
        response.raise_for_status()
        data = response.json()
        print(f"  Processed document: {data.get('document_id')}")
        return data
    except:
        print(f"  Error response: {response.text}")
        raise

def main():
    """Main test function"""
    print_header("Testing Vertical Slice Architecture Implementation")
    
    # Check if the application is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to {BASE_URL}")
        print("Make sure the application is running with:")
        print("  python vertical_slice_app.py")
        return 1
    
    # Run tests
    run_test("Health Check", test_health_check)
    run_test("Document List", test_document_list)
    run_test("Document Chat", test_document_chat)
    run_test("Document Suggestions", test_document_suggestions)
    run_test("Tables Feature", test_tables_feature)
    
    # Test PDF scanning if we have test files
    if os.path.exists("uploads") and os.listdir("uploads"):
        run_test("PDF Scanning", test_pdf_scanning)
    else:
        print("\n> Skipping PDF Scanning test (no files in uploads/ directory)")
    
    print("\nAll tests completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
