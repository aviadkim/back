import os
import sys
import pytest
from flask import Flask, json
from io import BytesIO
import shutil

# Add the parent directory to the path to import modules from the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app and various modules for testing
from vertical_slice_app import app as flask_app

@pytest.fixture
def app():
    """
    Create a Flask app fixture for testing
    """
    flask_app.config.update({
        "TESTING": True,
    })
    
    # Create test upload folder if it doesn't exist
    test_upload_folder = 'test_uploads'
    os.makedirs(test_upload_folder, exist_ok=True)
    flask_app.config['UPLOAD_FOLDER'] = test_upload_folder
    
    yield flask_app

@pytest.fixture
def client(app):
    """
    Create a test client for the Flask app
    """
    return app.test_client()

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Setup test environment
    test_upload_folder = 'test_uploads'
    os.makedirs(test_upload_folder, exist_ok=True)
    
    yield
    
    # Cleanup after test
    if os.path.exists(test_upload_folder):
        shutil.rmtree(test_upload_folder)

def test_health_check(client):
    """
    Test the health check endpoint
    """
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "ok"
    assert "version" in data

def test_get_documents_empty(client):
    """
    Test getting documents when there are none
    """
    response = client.get('/api/documents')
    assert response.status_code == 200
    data = json.loads(response.data)
    # Should return at least the demo document
    assert len(data) >= 1

def test_file_upload_no_file(client):
    """Test file upload without providing a file"""
    response = client.post('/api/upload', data={})
    assert response.status_code == 400
    assert response.json['error'] == "No file provided"

def test_file_upload_empty_filename(client):
    """Test file upload with empty filename"""
    data = {
        'file': (BytesIO(b''), ''),
        'language': 'he'
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['error'] == "No file selected"

def test_file_upload_invalid_extension(client):
    """Test file upload with invalid extension"""
    data = {
        'file': (BytesIO(b'test content'), 'test.txt'),
        'language': 'he'
    }
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['error'] == "File type not allowed"

def test_file_upload_success(client):
    """
    Test successful file upload
    """
    data = {
        'file': (BytesIO(b'Test PDF content'), 'test.pdf'),
        'language': 'he'
    }
    
    response = client.post('/api/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 201

def test_pdf_scanning_feature(client):
    """
    Test the PDF scanning feature
    """
    # Test the API endpoint for the PDF scanning feature
    response = client.get('/api/tables/document/test_document')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "tables" in data

def test_document_chat_feature_suggestions(client):
    """
    Test the document chat feature - suggested questions
    """
    # Test the API endpoint for getting suggested questions
    response = client.get('/api/chat/documents/test_document/suggestions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "suggestions" in data

def test_frontend_serving(client):
    """
    Test that the frontend is being served correctly
    """
    response = client.get('/')
    assert response.status_code == 200
    # Check if response contains HTML
    assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data
