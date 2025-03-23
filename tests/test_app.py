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
    assert response.json['status'] == 'ok'

def test_api_health_check(client):
    """Test API health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert 'status' in response.json
    assert response.json['status'] in ['ok', 'warning']

def test_file_upload_no_file(client):
    """Test file upload without file."""
    response = client.post('/api/upload')
    assert response.status_code == 400
    assert 'error' in response.json

def test_chat_no_question(client):
    """Test chat endpoint without question."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    assert 'error' in response.json
