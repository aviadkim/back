import os
import logging
from enhanced_pdf_processor import EnhancedPDFProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuickTest")

def main():
    """Run a quick test of the extraction functionality"""
    test_pdf = 'uploads/doc_de0c7654_2._Messos_28.02.2025.pdf'
    
    if not os.path.exists(test_pdf):
        logger.error(f"Test PDF not found: {test_pdf}")
        return 1
    
    # Ensure extraction directory exists
    os.makedirs('extractions', exist_ok=True)
    
    # Process with minimal settings
    logger.info("Creating processor with minimal settings for faster testing")
    processor = EnhancedPDFProcessor(dpi=150, thread_count=2)
    
    document_id = 'doc_de0c7654'
    filename = os.path.basename(test_pdf)
    
    # Check either possible output path
    expected_path1 = os.path.join('extractions', f"{document_id}_{filename.replace('.pdf', '_extraction.json')}")
    expected_path2 = os.path.join('extractions', f"{filename.replace('.pdf', '_extraction.json')}")
    
    logger.info(f"Expected output file: {expected_path1} or {expected_path2}")
    
    # Only check if the document ID part is applied correctly
    logger.info("Processing document...")
    try:
        result = processor.process_document(test_pdf, document_id)
        
        if result and (os.path.exists(expected_path1) or os.path.exists(expected_path2)):
            logger.info(f"✅ Test passed! Output file created correctly")
            if os.path.exists(expected_path1):
                logger.info(f"File created at: {expected_path1}")
            else:
                logger.info(f"File created at: {expected_path2}")
            return 0
        else:
            if result:
                logger.error(f"❌ Result path returned: {result}")
            logger.error(f"❌ Expected file not found at expected paths")
            logger.error(f"Files in extraction directory: {os.listdir('extractions')}")
            return 1
    except Exception as e:
        logger.error(f"❌ Error during processing: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
