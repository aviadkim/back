import pytest
import os
from app import app
import json
from io import BytesIO

@pytest.fixture
def api_client():
    app.config['TESTING'] = True
    app.config['UPLOAD_FOLDER'] = 'tests/fixtures'
    return app.test_client()

def test_document_upload_flow(api_client):
    """Test complete document upload and processing flow."""
    # Create test PDF content
    test_content = b"Test PDF content"
    response = api_client.post(
        '/api/documents/upload',
        data={
            'file': (BytesIO(test_content), 'test.pdf')
        },
        content_type='multipart/form-data'
    )
    assert response.status_code in [200, 201]  # Allow both success codes

def test_api_error_handling(api_client):
    """Test API error handling."""
    # Test invalid file type
    response = api_client.post(
        '/api/documents/upload',
        data={'file': ('test.txt', b'Invalid file')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
