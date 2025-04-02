"""Tests for financial analysis service"""
import os
import pytest
import sys
from unittest.mock import MagicMock, patch

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath('../../../'))
from project_organized.features.financial_analysis.service import FinancialAnalysisService

class TestFinancialAnalysisService:
    """Test cases for financial analysis service"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.service = FinancialAnalysisService()
    
    @patch('project_organized.features.financial_analysis.service.FinancialAnalysisService._find_document_path')
    @patch('project_organized.features.financial_analysis.service.FinancialAnalysisService._get_extraction_results')
    @patch('project_organized.features.financial_analysis.extractors.AdvancedFinancialExtractor.analyze')
    def test_analyze_document(self, mock_analyze, mock_get_extraction, mock_find_path):
        """Test document analysis"""
        # Set up mocks
        document_id = 'doc_test123'
        mock_path = '/path/to/document.pdf'
        mock_extraction = '{"content": "test content"}'
        mock_analysis_result = {'securities': [], 'total_value': 10000}
        
        mock_find_path.return_value = mock_path
        mock_get_extraction.return_value = mock_extraction
        mock_analyze.return_value = mock_analysis_result
        
        # Call the service function
        result = self.service.analyze_document(document_id)
        
        # Check results
        assert result == mock_analysis_result
        mock_find_path.assert_called_once_with(document_id)
        mock_get_extraction.assert_called_once_with(document_id)
        mock_analyze.assert_called_once_with(mock_path, mock_extraction)
