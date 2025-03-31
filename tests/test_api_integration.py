import pytest
import os
# Remove direct app import: from app import app
import json
from io import BytesIO

# The test_client fixture is now provided by conftest.py
# We can use it directly in tests.
# If we need to modify the app config per test, we might need a different fixture setup,
# but let's use the module-scoped one for now.
# The tmpdir fixture is function-scoped, while test_client is module-scoped.
# For simplicity, let's assume the UPLOAD_FOLDER set in conftest is sufficient for now.
# If tests need isolated upload folders, conftest.py fixtures need adjustment.

# Use test_client directly instead of creating api_client fixture
# @pytest.fixture
# def api_client(test_client):
#     return test_client

def test_document_upload_flow(test_client): # Use test_client directly
    """Test complete document upload and processing flow."""
    pdf_content = b"%PDF-1.4\nTest PDF content"
    data = {
        'file': (BytesIO(pdf_content), 'test.pdf', 'application/pdf')
    }
    # Use the correct endpoint defined in routes/document.py
    response = test_client.post('/api/document/upload',
                              data=data,
                              content_type='multipart/form-data')
    assert response.status_code in [200, 201]
    
    if response.status_code in [200, 201]:
        response_data = response.get_json()
        assert response_data['status'] == 'success'
        assert 'data' in response_data
        assert 'document_id' in response_data['data']

def test_api_error_handling(test_client): # Use test_client directly
    """Test API error handling for unsupported file type."""
    data = {
        'file': (BytesIO(b'Invalid content'), 'test.txt', 'text/plain')
    }
    # Use the correct endpoint
    response = test_client.post(
        '/api/document/upload',
        data=data,
        content_type='multipart/form-data'
    )
    assert response.status_code == 400
