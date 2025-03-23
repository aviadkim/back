import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert 'status' in response.json
    assert response.json['status'] == 'healthy'

def test_file_upload_no_file(client):
    """Test file upload without file."""
    response = client.post('/api/documents/upload')
    assert response.status_code == 400
