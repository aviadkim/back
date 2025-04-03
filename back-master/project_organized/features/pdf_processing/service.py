"""Service layer for PDF processing feature."""
import os
import logging
from .processor import EnhancedPDFProcessor

logger = logging.getLogger(__name__)

class PDFProcessingService:
    """Service for processing PDF documents"""
    
    def __init__(self, extraction_dir='extractions'):
        self.processor = EnhancedPDFProcessor()
        self.extraction_dir = extraction_dir
        os.makedirs(extraction_dir, exist_ok=True)
    
    def process_document(self, file_path, document_id=None):
        """Process a document and return extraction results
        
        Args:
            file_path: Path to the PDF file
            document_id: Optional document ID
            
        Returns:
            Dict with extraction results
        """
        logger.info(f"Processing document: {file_path}")
        
        extraction_path = self.processor.process_document(file_path, document_id)
        
        if not extraction_path:
            logger.error("Document processing failed")
            return None
            
        # Read the extraction results
        try:
            with open(extraction_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            return {
                'document_id': document_id,
                'extraction_path': extraction_path,
                'content_length': len(content),
                'status': 'completed'
            }
        except Exception as e:
            logger.error(f"Error reading extraction results: {e}")
            return None
