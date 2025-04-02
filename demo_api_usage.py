#!/usr/bin/env python3
"""Demonstration of how to use the Financial Document Processing System API"""

import os
import sys
import json
import requests
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"  # Change if your server is running on a different port
SAMPLE_PDF_PATH = "uploads/test_document.pdf"  # Update this path to point to a valid PDF

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def json_print(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))

def check_health():
    """Check if the API is running"""
    print_header("CHECKING API HEALTH")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status code: {response.status_code}")
        json_print(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def upload_document(file_path):
    """Upload a document to the API"""
    print_header("UPLOADING DOCUMENT")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return None
        
    try:
        files = {'file': open(file_path, 'rb')}
        data = {'language': 'eng'}
        
        response = requests.post(
            f"{API_BASE_URL}/api/documents/upload",
            files=files,
            data=data
        )
        
        print(f"Status code: {response.status_code}")
        result = response.json()
        json_print(result)
        
        if response.status_code == 200:
            return result.get('document_id')
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def list_documents():
    """List all documents"""
    print_header("LISTING DOCUMENTS")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/")
        print(f"Status code: {response.status_code}")
        json_print(response.json())
    except Exception as e:
        print(f"Error: {e}")

def get_document(document_id):
    """Get document details"""
    print_header(f"GETTING DOCUMENT DETAILS: {document_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/{document_id}")
        print(f"Status code: {response.status_code}")
        json_print(response.json())
    except Exception as e:
        print(f"Error: {e}")

def ask_question(document_id, question):
    """Ask a question about a document"""
    print_header(f"ASKING QUESTION: '{question}'")
    
    try:
        data = {
            "document_id": document_id,
            "question": question
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/qa/ask",
            json=data
        )
        
        print(f"Status code: {response.status_code}")
        result = response.json()
        json_print(result)
        
        return result.get('answer')
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_financial_analysis(document_id):
    """Get financial analysis for a document"""
    print_header(f"GETTING FINANCIAL ANALYSIS: {document_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/financial/analyze/{document_id}")
        print(f"Status code: {response.status_code}")
        json_print(response.json())
    except Exception as e:
        print(f"Error: {e}")

def generate_custom_table(document_id):
    """Generate a custom table from the document"""
    print_header(f"GENERATING CUSTOM TABLE: {document_id}")
    
    try:
        spec = {
            "columns": ["name", "isin", "value", "currency"],
            "sort_by": "value",
            "sort_order": "desc"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/documents/{document_id}/custom_table",
            json=spec
        )
        
        print(f"Status code: {response.status_code}")
        json_print(response.json())
    except Exception as e:
        print(f"Error: {e}")

def run_demo():
    """Run a complete demo of the API"""
    print_header("STARTING FINANCIAL DOCUMENT PROCESSING API DEMO")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Check if API is running
    if not check_health():
        print("Error: API is not running")
        return
    
    # Step 2: List existing documents
    list_documents()
    
    # Step 3: Upload a document (if sample exists)
    document_id = None
    if os.path.exists(SAMPLE_PDF_PATH):
        document_id = upload_document(SAMPLE_PDF_PATH)
        
        if document_id:
            print(f"Successfully uploaded document with ID: {document_id}")
        else:
            print("Could not upload document")
    else:
        # If no sample PDF exists, try to find an existing document
        print(f"Sample PDF not found at {SAMPLE_PDF_PATH}")
        print("Trying to find an existing document ID...")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/documents/")
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                if documents:
                    document_id = documents[0].get('document_id')
                    print(f"Using existing document with ID: {document_id}")
        except:
            pass
    
    # If we have a document ID, continue with demo
    if document_id:
        # Wait for document processing
        print("Waiting for document processing...")
        time.sleep(2)
        
        # Get document details
        get_document(document_id)
        
        # Get financial analysis
        get_financial_analysis(document_id)
        
        # Generate a custom table
        generate_custom_table(document_id)
        
        # Ask questions about the document
        questions = [
            "What is this document about?",
            "What is the total portfolio value?",
            "Which companies are mentioned in the document?",
            "What is the date of the document?"
        ]
        
        for question in questions:
            ask_question(document_id, question)
            time.sleep(1)  # Small pause between questions
    else:
        print("Error: No document ID available. Demo cannot continue.")
        
    print_header("DEMO COMPLETED")
    print("You can now explore the API further using the endpoints documented in README.md")
    print("To monitor document processing: python document_dashboard.py")

if __name__ == "__main__":
    run_demo()
