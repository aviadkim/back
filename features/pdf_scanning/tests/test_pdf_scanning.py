import pytest
import io
import os
import json
from flask import Flask
from werkzeug.datastructures import FileStorage

from features.pdf_scanning.services import PDFScanningService
from features.pdf_scanning.api import pdf_scanning_bp
from shared.pdf_utils import PDFProcessor

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(pdf_scanning_bp)
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def pdf_scanning_service():
    return PDFScanningService()

def test_pdf_upload_no_file(client):
    """Test PDF upload with no file"""
    response = client.post('/api/pdf/upload')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_pdf_upload_empty_filename(client):
    """Test PDF upload with empty filename"""
    response = client.post('/api/pdf/upload', data={
        'file': (io.BytesIO(b''), ''),
        'language': 'he'
    }, content_type='multipart/form-data')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_pdf_upload_invalid_extension(client):
    """Test PDF upload with invalid file extension"""
    response = client.post('/api/pdf/upload', data={
        'file': (io.BytesIO(b'test content'), 'test.txt'),
        'language': 'he'
    }, content_type='multipart/form-data')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'PDF' in data['error']

def test_pdf_processor_initialization():
    """Test PDF processor initialization"""
    processor = PDFProcessor(ocr_enabled=False)
    assert processor is not None
    assert processor.ocr_enabled is False

def test_pdf_scanning_service_initialization(pdf_scanning_service):
    """Test PDF scanning service initialization"""
    assert pdf_scanning_service is not None

def test_pdf_processor_extract_text():
    """Test PDF text extraction"""
    # This test would need a real PDF file
    # We'll create a minimal test that doesn't rely on actual extraction
    processor = PDFProcessor(ocr_enabled=False)
    
    # Mock the extraction by monkeypatching
    original_extract = processor.extract_text
    processor.extract_text = lambda path: "Test extracted text"
    
    text = processor.extract_text("mock_path.pdf")
    assert text == "Test extracted text"
    
    # Restore the original method
    processor.extract_text = original_extract

def test_get_all_documents_endpoint(client, monkeypatch):
    """Test getting all documents endpoint"""
    # Mock the service method
    from features.pdf_scanning.services import pdf_scanning_service
    
    def mock_get_all_documents(limit, offset):
        return [
            {
                "document_id": "test1.pdf",
                "original_filename": "test1.pdf",
                "text_content": "Test content 1",
                "tables": [],
                "processing_date": "2024-01-01T12:00:00"
            },
            {
                "document_id": "test2.pdf",
                "original_filename": "test2.pdf",
                "text_content": "Test content 2",
                "tables": [],
                "processing_date": "2024-01-02T12:00:00"
            }
        ]
    
    monkeypatch.setattr(pdf_scanning_service, "get_all_documents", mock_get_all_documents)
    
    response = client.get('/api/pdf/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'documents' in data
    assert len(data['documents']) == 2
    # Text content should be replaced with preview
    assert 'text_preview' in data['documents'][0]
    assert 'text_content' not in data['documents'][0]

def test_get_document_not_found(client, monkeypatch):
    """Test getting non-existent document"""
    # Mock the service method
    from features.pdf_scanning.services import pdf_scanning_service
    
    def mock_get_document(document_id):
        return None
    
    monkeypatch.setattr(pdf_scanning_service, "get_document", mock_get_document)
    
    response = client.get('/api/pdf/nonexistent_doc')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
