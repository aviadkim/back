"""Service layer for financial analysis feature."""
import os
import logging
from .extractors import EnhancedFinancialExtractor, AdvancedFinancialExtractor

logger = logging.getLogger(__name__)

class FinancialAnalysisService:
    """Service for extracting and analyzing financial data from documents"""
    
    def __init__(self):
        self.basic_extractor = EnhancedFinancialExtractor()
        self.advanced_extractor = AdvancedFinancialExtractor()
    
    def analyze_document(self, document_id, document_path=None):
        """Analyze a document and extract financial data
        
        Args:
            document_id: Document ID
            document_path: Path to the document (optional)
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing document {document_id}")
        
        if not document_path:
            # Try to find document path based on ID
            document_path = self._find_document_path(document_id)
            
        if not document_path or not os.path.exists(document_path):
            logger.error(f"Document not found: {document_path}")
            return None
            
        # Get extraction results
        extraction = self._get_extraction_results(document_id)
        if not extraction:
            logger.warning(f"No extraction results found for {document_id}")
            # Could perform extraction here
        
        # Run financial analysis
        try:
            result = self.advanced_extractor.analyze(document_path, extraction)
            return result
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return None
    
    def _find_document_path(self, document_id):
        """Find document path based on ID"""
        # This would normally query a database or file system
        uploads_dir = os.path.join('..', '..', 'uploads')
        for filename in os.listdir(uploads_dir):
            if filename.startswith(document_id) and filename.endswith('.pdf'):
                return os.path.join(uploads_dir, filename)
        return None
    
    def _get_extraction_results(self, document_id):
        """Get extraction results for a document"""
        # This would normally query a database or file system
        extractions_dir = os.path.join('..', '..', 'extractions')
        for filename in os.listdir(extractions_dir):
            if filename.startswith(document_id) and filename.endswith('_extraction.json'):
                path = os.path.join(extractions_dir, filename)
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
        return None
