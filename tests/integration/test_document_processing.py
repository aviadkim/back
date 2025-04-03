import pytest
import os
import io
from werkzeug.datastructures import FileStorage

@pytest.fixture
def sample_pdf():
    """Create a fixture for a sample PDF file"""
    # Look in multiple locations for the sample PDF
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '../../test_samples/sample_financial.pdf'),
        os.path.join(os.path.dirname(__file__), '../fixtures/sample.pdf'),
        './test_samples/sample_financial.pdf',
        './tests/fixtures/sample.pdf'
    ]
    
    # Use the first path that exists
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    pytest.skip("No sample PDF found in any of the expected locations")

def test_document_upload_and_extraction(client, sample_pdf):
    """Test the complete upload and extraction pipeline"""
    # Test file upload
    with open(sample_pdf, 'rb') as f:
        data = {}
        data['file'] = (io.BytesIO(f.read()), os.path.basename(sample_pdf), 'application/pdf')
        data['language'] = 'heb+eng'
        
        response = client.post(
            '/api/documents/upload',
            data=data,
            content_type='multipart/form-data'
        )
    
    assert response.status_code == 200
    result = response.get_json()
    assert 'document_id' in result
    
    document_id = result['document_id']
    
    # Test document retrieval
    response = client.get(f'/api/documents/{document_id}')
    assert response.status_code == 200
    document = response.get_json()
    assert document['document_id'] == document_id
