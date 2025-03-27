import os
import pytest
from utils.pdf_processor import PDFProcessor

# Define the path to the test PDF provided by the user
# Assuming it's relative to the project root /workspaces/back
SAMPLE_PDF_PATH = "test_documents/2. Messos 28.02.2025.pdf"

# Check if the sample PDF exists, skip tests if not
SAMPLE_PDF_EXISTS = os.path.exists(SAMPLE_PDF_PATH)

@pytest.fixture
def pdf_processor():
    """Provides a PDFProcessor instance for tests."""
    return PDFProcessor()

@pytest.mark.skipif(not SAMPLE_PDF_EXISTS, reason=f"Sample PDF not found at {SAMPLE_PDF_PATH}")
def test_process_pdf_basic_extraction(pdf_processor):
    """
    Tests basic PDF processing, assuming the sample PDF has extractable text.
    Verifies that text is extracted, metadata is returned, and page count is positive.
    """
    try:
        extracted_text, metadata, page_count = pdf_processor.process_pdf(SAMPLE_PDF_PATH, language='he')

        assert isinstance(extracted_text, str)
        # Basic check: Does it seem like text was extracted? (Adjust threshold if needed)
        assert len(extracted_text) > 100, "Extracted text seems too short or empty."

        assert isinstance(metadata, dict)
        # Check for some expected metadata keys (can be expanded)
        assert "title" in metadata
        assert "detected_document_type" in metadata

        assert isinstance(page_count, int)
        assert page_count > 0, "Page count should be positive."

    except FileNotFoundError:
        pytest.fail(f"Test failed because sample PDF was not found: {SAMPLE_PDF_PATH}")
    except Exception as e:
        pytest.fail(f"process_pdf raised an unexpected exception: {e}")

# Placeholder for OCR test - requires a suitable image-based PDF
@pytest.mark.skip(reason="Requires an image-based or low-text PDF sample for OCR testing")
def test_process_pdf_ocr_fallback(pdf_processor):
    """
    Tests if the processor correctly falls back to OCR when text extraction yields little content.
    Requires a specific sample PDF designed for this purpose.
    """
    # TODO: Replace with actual path to an image-based PDF
    ocr_pdf_path = "path/to/image_based_sample.pdf"
    if not os.path.exists(ocr_pdf_path):
         pytest.skip(f"OCR test PDF not found at {ocr_pdf_path}")

    extracted_text, metadata, page_count = pdf_processor.process_pdf(ocr_pdf_path, language='eng') # Assuming English OCR test file

    assert isinstance(extracted_text, str)
    # Add more specific assertions based on the expected OCR output of the sample file
    assert "Expected OCR Text Snippet" in extracted_text
    assert page_count > 0

# TODO: Add tests for _extract_metadata details (dates, financial entities) using specific samples
# TODO: Add tests for _detect_document_type with different document types
# TODO: Add tests for error handling (e.g., corrupted PDF)