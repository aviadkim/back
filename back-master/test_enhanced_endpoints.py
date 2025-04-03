import os
import pytest
import requests
import sys
import json
from enhanced_pdf_processor import EnhancedPDFProcessor

# Add a conftest.py fixture to avoid import error
if not os.path.exists('tests'):
    os.makedirs('tests', exist_ok=True)
    with open('tests/conftest.py', 'w') as f:
        f.write("""
import pytest
import os

@pytest.fixture
def test_pdf_path():
    test_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    if not os.path.exists(test_dir):
        os.makedirs(test_dir, exist_ok=True)
    return os.path.join(test_dir, 'sample.pdf')
""")

def test_document_processing(test_pdf_path):
    processor = EnhancedPDFProcessor()
    doc_id = "doc_test"
    
    # Ensure extractions directory exists
    os.makedirs('extractions', exist_ok=True)
    
    # Process document
    result = processor.process_document(test_pdf_path, doc_id)
    
    # Check extraction file exists
    filename = os.path.basename(test_pdf_path)
    expected_path = os.path.join(
        'extractions',
        f"{doc_id}_{filename.replace('.pdf', '_extraction.json')}"
    )
    assert os.path.exists(expected_path), f"Extraction file not found at {expected_path}"

def test_enhanced_endpoints(document_id, base_url="http://localhost:5001"):
    """Test the enhanced API endpoints"""
    print(f"Testing enhanced endpoints for document: {document_id}")
    
    # Test the advanced analysis endpoint
    print("\n1. Testing advanced analysis endpoint...")
    try:
        response = requests.get(f"{base_url}/api/documents/{document_id}/advanced_analysis")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Analysis results summary:")
            print(f"  Total value: {result['analysis'].get('total_value', 'N/A')}")
            print(f"  Security count: {result['analysis'].get('security_count', 'N/A')}")
            print(f"  Top holdings: {len(result['analysis'].get('top_holdings', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request error: {e}")
    
    # Test the custom table endpoint
    print("\n2. Testing custom table endpoint...")
    try:
        table_spec = {
            "columns": ["isin", "name", "currency"],
            "sort_by": "isin",
            "sort_order": "asc"
        }
        
        response = requests.post(
            f"{base_url}/api/documents/{document_id}/custom_table",
            json=table_spec
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Custom table results:")
            print(f"  Columns: {result['table'].get('columns', [])}")
            print(f"  Rows: {len(result['table'].get('data', []))}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_enhanced_endpoints.py <document_id>")
        print("Example: python test_enhanced_endpoints.py doc_c343d4cc")
        sys.exit(1)
    
    document_id = sys.argv[1]
    test_enhanced_endpoints(document_id)
