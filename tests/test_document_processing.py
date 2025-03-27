import pytest
import os
from models.document_models import Document
def test_document_creation():
    """Test document model creation."""
    doc = Document(
        filename="test.pdf",
        original_name="test.pdf",
        file_path="/tmp/test.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    assert doc.filename == "test.pdf"
    assert not doc.is_processed
