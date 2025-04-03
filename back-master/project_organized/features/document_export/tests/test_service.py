"""Tests for document export service"""
import os
import pytest
import sys
from unittest.mock import MagicMock, patch

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath('../../../'))
from project_organized.features.document_export.service import DocumentExportService

class TestDocumentExportService:
    """Test cases for document export service"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.extraction_dir = 'test_extractions'
        self.export_dir = 'test_exports'
        
        # Create the service with patched ExcelExporter
        with patch('project_organized.features.document_export.service.ExcelExporter') as mock_excel:
            self.service = DocumentExportService(
                extraction_dir=self.extraction_dir,
                export_dir=self.export_dir
            )
            self.mock_excel_exporter = self.service.excel_exporter
    
    def teardown_method(self):
        """Clean up after each test"""
        # Remove test directories if they exist
        import shutil
        for dir_path in [self.extraction_dir, self.export_dir]:
            if os.path.exists(dir_path) and dir_path.startswith('test_'):
                shutil.rmtree(dir_path)
    
    def test_get_available_formats(self):
        """Test getting available export formats"""
        # Service was initialized with mock ExcelExporter, so Excel should be available
        formats = self.service.get_available_formats()
        assert 'json' in formats
        assert 'excel' in formats
    
    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('builtins.open')
    def test_export_document_to_excel(self, mock_open, mock_listdir, mock_exists):
        """Test exporting a document to Excel"""
        # Set up mocks
        document_id = 'doc_test123'
        mock_exists.return_value = True
        mock_listdir.return_value = [f"{document_id}_extraction.json"]
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_file.read.return_value = '{"content": "test content"}'
        
        self.mock_excel_exporter.export_financial_data.return_value = f"{self.export_dir}/{document_id}_export.xlsx"
        
        # Call the service function
        result = self.service.export_document_to_excel(document_id)
        
        # Check results
        assert result == f"{self.export_dir}/{document_id}_export.xlsx"
        self.mock_excel_exporter.export_financial_data.assert_called_once()
