import pytest
import os
from models.document_models import Document
from utils.pdf_processor import extract_text_from_pdf

@pytest.fixture
def sample_pdf():
    # Create a test PDF file
    pdf_path = "tests/fixtures/sample.pdf"
    return pdf_path

def test_pdf_text_extraction(sample_pdf):
    """Test PDF text extraction functionality."""
    text = extract_text_from_pdf(sample_pdf)
    assert text is not None
    assert len(text) > 0

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
