import pytest
import os
from app import app
import json
from io import BytesIO

@pytest.fixture
def api_client(test_client, tmpdir):
    """Setup test client with temporary upload folder."""
    upload_dir = str(tmpdir.mkdir('uploads'))
    test_client.application.config['UPLOAD_FOLDER'] = upload_dir
    return test_client

def test_document_upload_flow(api_client):
    """Test complete document upload and processing flow."""
    pdf_content = b"%PDF-1.4\nTest PDF content"
    data = {
        'file': (BytesIO(pdf_content), 'test.pdf', 'application/pdf')
    }
    response = api_client.post('/api/documents/upload',
                             data=data,
                             content_type='multipart/form-data')
    assert response.status_code in [200, 201]
    
    if response.status_code in [200, 201]:
        data = response.get_json()
        assert 'document_id' in data

def test_api_error_handling(api_client):
    """Test API error handling."""
    data = {
        'file': (BytesIO(b'Invalid content'), 'test.txt', 'text/plain')
    }
    response = api_client.post(
        '/api/documents/upload',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
