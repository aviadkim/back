"""Tests for document QA service"""
import os
import pytest
import sys
from unittest.mock import MagicMock, patch

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath('../../../'))
from project_organized.features.document_qa.service import DocumentQAService

class TestDocumentQAService:
    """Test cases for document QA service"""
    
    def setup_method(self):
        """Set up test environment before each test"""
        self.service = DocumentQAService()
        
        # Mock the underlying QA components
        self.service.simple_qa = MagicMock()
        self.service.financial_qa = MagicMock()
        
        # Set default return values
        self.service.simple_qa.answer.return_value = "Simple answer"
        self.service.financial_qa.answer.return_value = "Financial answer"
    
    @patch('project_organized.features.document_qa.service.DocumentQAService._get_document_content')
    @patch('project_organized.features.document_qa.service.DocumentQAService._is_financial_question')
    def test_answer_financial_question(self, mock_is_financial, mock_get_content):
        """Test answering a financial question"""
        # Set up mocks
        document_id = 'doc_test123'
        question = "What is the value of Apple stock?"
        document_content = "This is a document about stocks"
        
        mock_get_content.return_value = document_content
        mock_is_financial.return_value = True
        
        # Call the service function
        answer = self.service.answer_question(document_id, question)
        
        # Check results
        mock_get_content.assert_called_once_with(document_id)
        mock_is_financial.assert_called_once_with(question)
        self.service.financial_qa.answer.assert_called_once_with(question, document_content, document_id)
        assert answer == "Financial answer"
    
    @patch('project_organized.features.document_qa.service.DocumentQAService._get_document_content')
    @patch('project_organized.features.document_qa.service.DocumentQAService._is_financial_question')
    def test_answer_general_question(self, mock_is_financial, mock_get_content):
        """Test answering a general question"""
        # Set up mocks
        document_id = 'doc_test123'
        question = "How many pages is this document?"
        document_content = "This is a document about stocks"
        
        mock_get_content.return_value = document_content
        mock_is_financial.return_value = False
        
        # Call the service function
        answer = self.service.answer_question(document_id, question)
        
        # Check results
        self.service.simple_qa.answer.assert_called_once_with(question, document_content)
        assert answer == "Simple answer"
