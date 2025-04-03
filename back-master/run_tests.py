import os
import requests
import json
import sys

BASE_URL = "http://localhost:5001"

def test_health():
    """Test the health endpoint"""
    print("\n--- Testing Health Endpoint ---")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    return response.status_code == 200

def test_list_documents():
    """Test listing documents"""
    print("\n--- Testing Document List ---")
    response = requests.get(f"{BASE_URL}/api/documents")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Document count: {len(data.get('documents', []))}")
    if len(data.get('documents', [])) > 0:
        print(f"First document: {json.dumps(data['documents'][0], indent=2)}")
        return data['documents'][0].get('document_id')
    return None

def test_upload_document(file_path):
    """Test document upload"""
    print(f"\n--- Testing Document Upload: {file_path} ---")
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
    
    files = {'file': open(file_path, 'rb')}
    data = {'language': 'heb+eng'}
    
    response = requests.post(f"{BASE_URL}/api/documents/upload", files=files, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        return result.get('document_id')
    return None

def test_document_analysis(document_id):
    """Test document analysis"""
    if not document_id:
        print("No document ID available for testing")
        return False
    
    print(f"\n--- Testing Document Analysis: {document_id} ---")
    response = requests.get(f"{BASE_URL}/api/documents/{document_id}/advanced_analysis")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
    return response.status_code == 200

def test_qa(document_id):
    """Test question answering"""
    if not document_id:
        print("No document ID available for testing")
        return False
    
    print(f"\n--- Testing QA: {document_id} ---")
    data = {
        "document_id": document_id,
        "question": "What ISINs are mentioned in the document?"
    }
    response = requests.post(f"{BASE_URL}/api/qa/ask", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}..." if len(response.text) > 200 else f"Response: {response.text}")
    return response.status_code == 200

def main():
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    # Run tests
    health_ok = test_health()
    
    # Get existing document or upload new one
    document_id = test_list_documents()
    if not document_id and pdf_path:
        document_id = test_upload_document(pdf_path)
    
    if document_id:
        test_document_analysis(document_id)
        test_qa(document_id)
    else:
        print("\nNo document available for testing. Please provide a PDF path.")

if __name__ == "__main__":
    main()
