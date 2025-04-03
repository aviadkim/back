"""Service layer for document export feature."""
import os
import logging
import json
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DocumentExportService:
    """Service for exporting document data"""
    
    def __init__(self, extraction_dir='extractions', export_dir='exports'):
        # Use absolute paths to avoid permission issues
        self.extraction_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', extraction_dir))
        self.export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', export_dir))
        
        # Create directories with proper error handling
        try:
            os.makedirs(self.export_dir, exist_ok=True)
            os.makedirs(self.extraction_dir, exist_ok=True)
        except PermissionError:
            logger.error(f"Permission denied while creating {self.export_dir} or {self.extraction_dir}")
            logger.info(f"Using temporary directory instead")
            import tempfile
            self.export_dir = tempfile.gettempdir()
            self.extraction_dir = tempfile.gettempdir()
        
        # Try to import ExcelExporter from multiple locations for backward compatibility
        try:
            from .excel_exporter import ExcelExporter
            self.excel_exporter = ExcelExporter(export_dir=self.export_dir)
            self._excel_available = True
        except ImportError:
            try:
                # Try old location
                import sys
                sys.path.append('../..')
                from excel_exporter import ExcelExporter
                self.excel_exporter = ExcelExporter(export_dir=self.export_dir)
                self._excel_available = True
            except ImportError:
                logger.warning("Excel export functionality not available")
                self._excel_available = False
    
    def export_document_to_excel(self, document_id):
        """Export document data to Excel
        
        Args:
            document_id: Document ID
            
        Returns:
            Path to generated Excel file or None if export failed
        """
        if not self._excel_available:
            logger.error("Excel export not available")
            return None
            
        # Get financial data for document
        financial_data = self._get_financial_data(document_id)
        if not financial_data:
            logger.error(f"No financial data found for document {document_id}")
            return None
        
        # Export to Excel
        filename = f"{document_id}_export.xlsx"
        excel_path = self.excel_exporter.export_financial_data(
            data=financial_data,
            filename=filename,
            document_id=document_id
        )
        
        return excel_path
        
    def get_available_formats(self):
        """Get available export formats
        
        Returns:
            List of available export formats
        """
        formats = ['json']
        if self._excel_available:
            formats.append('excel')
        return formats
        
    def _get_financial_data(self, document_id):
        """Get financial data for a document
        
        Args:
            document_id: Document ID
            
        Returns:
            List of financial data entries or None if not found
        """
        # Look for extraction file
        extraction_files = [f for f in os.listdir(self.extraction_dir) 
                           if f.startswith(document_id) and f.endswith('_extraction.json')]
        
        if not extraction_files:
            logger.error(f"No extraction file found for document {document_id}")
            return None
        
        # Get extraction data
        extraction_path = os.path.join(self.extraction_dir, extraction_files[0])
        try:
            with open(extraction_path, 'r', encoding='utf-8') as f:
                extraction_data = json.load(f)
            
            # Extract financial data from extraction data
            # This is just a simple example - in real code, you would parse the data
            return [
                {
                    'isin': 'US0378331005',
                    'name': 'Apple Inc.',
                    'quantity': 100,
                    'price': 145.86,
                    'currency': 'USD',
                    'value': 14586.00
                },
                {
                    'isin': 'US02079K1079',
                    'name': 'Alphabet Inc.',
                    'quantity': 50,
                    'price': 2321.34,
                    'currency': 'USD',
                    'value': 116067.00
                }
            ]
        except Exception as e:
            logger.error(f"Error reading extraction data: {e}")
            return None
