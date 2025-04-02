"""Tests for document upload service"""
import os
import pytest
import sys
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath('../../../'))
from project_organized.features.document_upload.service import DocumentUploadService

class TestDocumentUploadService:
    """Test cases for document upload service"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.upload_dir = 'test_uploads'
        self.extraction_dir = 'test_extractions'
        self.service = DocumentUploadService(
            upload_dir=self.upload_dir,
            extraction_dir=self.extraction_dir
        )
        
    def teardown_method(self):
        """Clean up after each test"""
        # Remove test directories if they exist
        import shutil
        if os.path.exists(self.upload_dir):
            shutil.rmtree(self.upload_dir)
        if os.path.exists(self.extraction_dir):
            shutil.rmtree(self.extraction_dir)
    
    def test_initialization(self):
        """Test that service initializes correctly"""
        assert self.service is not None
        assert self.service.upload_dir == self.upload_dir
        assert self.service.extraction_dir == self.extraction_dir
        assert os.path.exists(self.upload_dir)
        assert os.path.exists(self.extraction_dir)
    
    @patch('uuid.uuid4')
    def test_handle_upload(self, mock_uuid):
        """Test handling a file upload"""
        # Mock UUID to get consistent document ID
        mock_uuid.return_value.hex = 'abcdef1234567890'
        
        # Create mock file object
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = 'test_document.pdf'
        mock_file.save = MagicMock()
        
        # Call the service function
        result = self.service.handle_upload(mock_file, 'eng')
        
        # Check results
        assert result is not None
        assert result['document_id'] == 'doc_abcdef12'
        assert result['filename'] == 'test_document.pdf'
        assert result['language'] == 'eng'
        
        # Check that save was called with correct path
        expected_path = os.path.join(self.upload_dir, 'doc_abcdef12_test_document.pdf')
        mock_file.save.assert_called_once_with(expected_path)
