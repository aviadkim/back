import os
import pytest
from pdf_processor import DocumentProcessor # Import the new unified processor

# Define the path to the test PDF provided by the user
# Assuming it's relative to the project root /workspaces/back
SAMPLE_PDF_PATH = "test_documents/2. Messos 28.02.2025.pdf"

# Check if the sample PDF exists, skip tests if not
SAMPLE_PDF_EXISTS = os.path.exists(SAMPLE_PDF_PATH)

@pytest.fixture
def pdf_processor():
    """Provides a DocumentProcessor instance for tests."""
    # Instantiate with default config for now
    # Test-specific config could be passed if needed
    return DocumentProcessor()

@pytest.mark.skipif(not SAMPLE_PDF_EXISTS, reason=f"Sample PDF not found at {SAMPLE_PDF_PATH}")
def test_process_pdf_basic_extraction(pdf_processor):
    """
    Tests basic PDF processing, assuming the sample PDF has extractable text.
    Verifies that text is extracted, metadata is returned, and page count is positive.
    """
    try:
        # Call the new process_document method
        result = pdf_processor.process_document(SAMPLE_PDF_PATH)

        # Check the structure of the result dictionary
        assert isinstance(result, dict)
        assert 'error' not in result, f"Processing failed with error: {result.get('error')}"

        assert 'document_text' in result
        assert isinstance(result['document_text'], dict) # Expects dict of page_num: page_data

        assert 'tables' in result
        assert isinstance(result['tables'], dict) # Expects dict of page_num: list_of_tables

        assert 'financial_data' in result
        assert isinstance(result['financial_data'], dict)

        assert 'metadata' in result
        assert isinstance(result['metadata'], dict)
        assert result['metadata'].get('processing_status') == 'completed'
        assert result['metadata'].get('page_count', 0) > 0, "Page count should be positive."
        assert result['metadata'].get('filename') == os.path.basename(SAMPLE_PDF_PATH)

        # Basic check on extracted text (assuming page 0 exists)
        assert 0 in result['document_text'], "Page 0 text not found in results."
        page_0_text = result['document_text'][0].get('text', '')
        assert isinstance(page_0_text, str)
        assert len(page_0_text) > 50, "Extracted text for page 0 seems too short or empty." # Adjusted threshold

    except FileNotFoundError:
        pytest.fail(f"Test failed because sample PDF was not found: {SAMPLE_PDF_PATH}")
    except Exception as e:
        pytest.fail(f"process_document raised an unexpected exception: {e}")

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

    # Instantiate processor specifically for this test if needed, e.g., forcing OCR engine
    # ocr_processor = DocumentProcessor(config={'ocr_engine': 'local', 'language': 'eng'})
    # result = ocr_processor.process_document(ocr_pdf_path)
    result = pdf_processor.process_document(ocr_pdf_path) # Using default processor for now

    assert isinstance(result, dict)
    assert 'error' not in result
    assert 'document_text' in result
    # Add more specific assertions based on the expected OCR output of the sample file
    # Example: Check text from the first page
    page_0_text = result.get('document_text', {}).get(0, {}).get('text', '')
    assert "Expected OCR Text Snippet" in page_0_text
    assert result.get('metadata', {}).get('page_count', 0) > 0

# TODO: Add tests for _extract_metadata details (dates, financial entities) using specific samples
# TODO: Add tests for _detect_document_type with different document types
# TODO: Add tests for error handling (e.g., corrupted PDF)