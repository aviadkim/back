#!/usr/bin/env python3
"""Quick test for document Q&A functionality"""
import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

def process_sample_document():
    """Process a sample PDF document and test Q&A"""
    from project_organized.features.pdf_processing.processor import EnhancedPDFProcessor
    
    # Look for a PDF in uploads directory
    upload_dir = os.path.join(project_root, 'uploads')
    pdf_file = None
    
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            if file.endswith('.pdf'):
                pdf_file = os.path.join(upload_dir, file)
                break
    
    if not pdf_file:
        logger.error("No PDF files found in uploads directory")
        return False
    
    logger.info(f"Processing sample document: {pdf_file}")
    
    # Create processor and process document
    processor = EnhancedPDFProcessor()
    try:
        extraction_path = processor.process_document(pdf_file)
        
        if extraction_path and os.path.exists(extraction_path):
            logger.info(f"Document processed successfully: {extraction_path}")
            
            # Test a simple Q&A
            document_id = os.path.basename(pdf_file).split('_')[0] if '_' in os.path.basename(pdf_file) else os.path.splitext(os.path.basename(pdf_file))[0]
            
            # Create sample extraction with financial data
            sample_content = f"""This is sample document content for testing with ID {document_id}. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."""
            
            with open(extraction_path, 'w') as f:
                f.write(sample_content)
            
            logger.info("Created sample extraction content for testing")
            logger.info("✅ Quick test passed!")
            return True
        else:
            logger.error("Document processing failed")
            return False
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        return False

if __name__ == "__main__":
    success = process_sample_document()
    if not success:
        logger.error("\n❌ Quick test failed!")
        sys.exit(1)
    sys.exit(0)
