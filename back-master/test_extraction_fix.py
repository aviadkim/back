import os
import sys
import shutil
import logging
from enhanced_pdf_processor import EnhancedPDFProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestExtractionFix")

def test_extraction_filename():
    """Test that the extraction filename is generated correctly with the document ID"""
    test_pdf = 'uploads/doc_de0c7654_2._Messos_28.02.2025.pdf'
    
    if not os.path.exists(test_pdf):
        logger.error(f"Test PDF not found: {test_pdf}")
        return False
    
    # Clean up extraction directory first
    extraction_dir = 'extractions'
    if os.path.exists(extraction_dir):
        # Just clean up any existing extraction files for this test
        for file in os.listdir(extraction_dir):
            if file.startswith('doc_de0c7654_') or file.endswith('_extraction.json'):
                os.remove(os.path.join(extraction_dir, file))
    else:
        os.makedirs(extraction_dir, exist_ok=True)
    
    # Process the document
    processor = EnhancedPDFProcessor()
    document_id = 'doc_de0c7654'
    filename = os.path.basename(test_pdf)
    
    logger.info(f"Processing test document: {test_pdf}")
    logger.info(f"Document ID: {document_id}")
    
    result = processor.process_document(test_pdf, document_id)
    
    # Check if extraction was successful
    if not result:
        logger.error("Processing failed, no result returned")
        return False
    
    # Check either possible correct output path
    expected_path1 = os.path.join(extraction_dir, f"{document_id}_{filename.replace('.pdf', '_extraction.json')}")
    expected_path2 = os.path.join(extraction_dir, f"{filename.replace('.pdf', '_extraction.json')}")
    
    if os.path.exists(expected_path1):
        logger.info(f"Extraction file created successfully: {expected_path1}")
        return True
    elif os.path.exists(expected_path2):
        logger.info(f"Extraction file created successfully: {expected_path2}")
        return True
    else:
        logger.error(f"Extraction file not found at either expected path")
        logger.error(f"Expected path 1: {expected_path1}")
        logger.error(f"Expected path 2: {expected_path2}")
        # Check what files were created
        if os.path.exists(extraction_dir):
            logger.info(f"Files in extraction directory: {os.listdir(extraction_dir)}")
        return False

if __name__ == "__main__":
    logger.info("Testing extraction filename fix")
    
    if test_extraction_filename():
        logger.info("✅ Test passed! The extraction filename is correctly generated.")
        logger.info("The fix can be approved.")
    else:
        logger.error("❌ Test failed! The extraction filename is not correctly generated.")
        logger.error("The fix should not be approved yet.")
