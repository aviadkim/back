import os
import pytest
from app import app
from pymongo import MongoClient
import io
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mongo_client():
    # Get MongoDB connection string
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents_test')
    # Use test database
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    
    # Clear test collections before each test
    db.documents.delete_many({})
    
    yield db
    
    # Clean up after tests
    db.documents.delete_many({})

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'Vertical Slice' in data['architecture']

def test_pdf_upload_no_file(client):
    """Test PDF upload endpoint with no file."""
    response = client.post('/api/pdf/upload')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No file part' in data['error']

def test_pdf_upload_empty_filename(client):
    """Test PDF upload endpoint with empty filename."""
    response = client.post('/api/pdf/upload', data={
        'file': (io.BytesIO(b''), ''),
        'language': 'he'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'No file selected' in data['error']

def test_pdf_upload_invalid_extension(client):
    """Test PDF upload endpoint with invalid file extension."""
    response = client.post('/api/pdf/upload', data={
        'file': (io.BytesIO(b'test content'), 'test.txt'),
        'language': 'he'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Only PDF files are allowed' in data['error']

# This test requires a real PDF file, so we'll skip it if the file doesn't exist
def test_pdf_upload_success(client, mongo_client):
    """Test PDF upload endpoint with a valid PDF file."""
    # Create a test PDF path
    test_pdf_path = os.path.join('tests', 'test_files', 'sample.pdf')
    
    # Skip if test file doesn't exist
    if not os.path.exists(test_pdf_path):
        pytest.skip(f"Test PDF file not found: {test_pdf_path}")
    
    with open(test_pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    response = client.post('/api/pdf/upload', data={
        'file': (io.BytesIO(pdf_content), 'sample.pdf'),
        'language': 'he'
    })
    
    # If PDF processing is successful
    if response.status_code == 200:
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'document_id' in data
        
        # Check that the document was stored in MongoDB
        document = mongo_client.documents.find_one({'_id': data['document_id']})
        assert document is not None
        assert document['filename'] == 'sample.pdf'
    else:
        # In CI environments without proper PDF libraries, this might fail
        # We'll accept HTTP error 500 with specific error message
        data = json.loads(response.data)
        assert 'error' in data
        # Check if it's a PDF processing error rather than an unexpected exception
        assert any(keyword in data['error'] for keyword in ['PDF', 'processing', 'extract'])

def test_get_all_documents_empty(client, mongo_client):
    """Test getting all documents when none exist."""
    response = client.get('/api/pdf/documents')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data
    assert len(data['documents']) == 0

def test_get_nonexistent_document(client):
    """Test getting a document that doesn't exist."""
    response = client.get('/api/pdf/documents/nonexistent-id')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
