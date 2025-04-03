import requests
import json
import os
import sys
import time
import unittest

BASE_URL = "http://localhost:5001"

class APITests(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.document_id = None
        
        # Check if the server is running
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code != 200:
                self.skipTest("API server not responding to health check")
        except:
            self.skipTest("API server not running")
        
        # Find an existing document or upload a new one
        try:
            response = requests.get(f"{BASE_URL}/api/documents")
            documents = response.json().get('documents', [])
            if documents:
                self.document_id = documents[0]['document_id']
                print(f"Using existing document: {self.document_id}")
            else:
                # Find a PDF to upload
                pdf_paths = [
                    './test_documents/sample.pdf',
                    './tests/fixtures/sample.pdf',
                    './uploads/2._Messos_28.02.2025.pdf'
                ]
                
                for path in pdf_paths:
                    if os.path.exists(path):
                        files = {'file': open(path, 'rb')}
                        data = {'language': 'heb+eng'}
                        response = requests.post(f"{BASE_URL}/api/documents/upload", 
                                                files=files, data=data)
                        if response.status_code == 200:
                            self.document_id = response.json().get('document_id')
                            print(f"Uploaded new document: {self.document_id}")
                            break
                
                if not self.document_id:
                    self.skipTest("No document available and couldn't upload one")
        except Exception as e:
            self.skipTest(f"Error setting up test: {e}")
    
    def test_health_endpoint(self):
        """Test the health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
    
    def test_document_list(self):
        """Test document listing"""
        response = requests.get(f"{BASE_URL}/api/documents")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('documents', data)
        self.assertIsInstance(data['documents'], list)
    
    def test_document_details(self):
        """Test document details retrieval"""
        if not self.document_id:
            self.skipTest("No document available")
        
        response = requests.get(f"{BASE_URL}/api/documents/{self.document_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['document_id'], self.document_id)
    
    def test_document_content(self):
        """Test document content retrieval"""
        if not self.document_id:
            self.skipTest("No document available")
        
        response = requests.get(f"{BASE_URL}/api/documents/{self.document_id}/content")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('content', data)
    
    def test_document_financial(self):
        """Test financial data retrieval"""
        if not self.document_id:
            self.skipTest("No document available")
        
        response = requests.get(f"{BASE_URL}/api/documents/{self.document_id}/financial")
        self.assertEqual(response.status_code, 200)
    
    def test_document_tables(self):
        """Test table extraction"""
        if not self.document_id:
            self.skipTest("No document available")
        
        response = requests.get(f"{BASE_URL}/api/documents/{self.document_id}/tables")
        self.assertEqual(response.status_code, 200)
    
    def test_advanced_analysis(self):
        """Test advanced analysis"""
        if not self.document_id:
            self.skipTest("No document available")
        
        response = requests.get(f"{BASE_URL}/api/documents/{self.document_id}/advanced_analysis")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('analysis', data)
    
    def test_qa_system(self):
        """Test question answering"""
        if not self.document_id:
            self.skipTest("No document available")
        
        data = {
            "document_id": self.document_id,
            "question": "What ISINs are mentioned in the document?"
        }
        response = requests.post(f"{BASE_URL}/api/qa/ask", json=data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)

if __name__ == "__main__":
    unittest.main(verbosity=2)
