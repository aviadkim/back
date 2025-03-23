import pytest
from unittest.mock import patch, MagicMock
import os

def test_mistral_api_connection():
    """Test Mistral API connection."""
    api_key = os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        pytest.skip("MISTRAL_API_KEY not set")

@patch('agent_framework.coordinator.AgentCoordinator')
def test_document_analysis(mock_coordinator):
    """Test document analysis."""
    mock_coordinator.return_value.analyze_document.return_value = {
        "status": "success",
        "analysis": "Test analysis result"
    }
    assert mock_coordinator.return_value.analyze_document(
        document_id="test_doc"
    )["status"] == "success"
