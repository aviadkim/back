import fitz  # PyMuPDF
import re
import logging
from typing import Dict, List, Tuple, Any, Optional

class PDFTextExtractor:
    """Extract and structure text content from PDF documents.
    
    This module handles the extraction of text while preserving
    document structure, formatting, and layout information.
    """
    
    def __init__(self, language="eng"):
        """Initialize the text extractor.
        
        Args:
            language: OCR language to use if needed
        """
        self.language = language
        self.logger = logging.getLogger(__name__)
    
    def extract_document(self, pdf_path: str) -> Dict[int, Dict[str, Any]]:
        """Extract all text and metadata from a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with page numbers as keys and page content as values
        """
        document = {}
        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                page_data = self._process_page(page)
                document[page_num] = page_data
            return document
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            raise
    
    def _process_page(self, page: fitz.Page) -> Dict[str, Any]:
        """Process a single page from the PDF.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Dictionary containing page content and metadata
        """
        # Extract text blocks with their positions
        text_blocks = page.get_text("blocks")
        
        # Get page dimensions
        page_width, page_height = page.rect.width, page.rect.height
        
        # Extract images if present
        images = self._extract_images(page)
        
        # Format as structured data
        return {
            "text": page.get_text(),
            "blocks": [
                {
                    "text": block[4],
                    "bbox": block[:4],
                    "block_type": "text"
                }
                for block in text_blocks
            ],
            "images": images,
            "dimensions": {
                "width": page_width,
                "height": page_height
            }
        }
    
    def _extract_images(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract images from the page with their positions.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            List of dictionaries containing image metadata
        """
        images = []
        img_list = page.get_images(full=True)
        
        for img_index, img in enumerate(img_list):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            if base_image:
                images.append({
                    "index": img_index,
                    "bbox": img[1:5],
                    "size": (base_image["width"], base_image["height"]),
                    "format": base_image["ext"]
                })
                
        return images
    
    def is_potentially_financial(self, text: str) -> bool:
        """Determine if text likely contains financial information.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Boolean indicating if text contains financial indicators
        """
        # Financial indicators: dollar signs, percentages, numbers with commas
        financial_patterns = [
            r'\$[\d,]+\.?\d*',  # Dollar amounts
            r'\d+\.\d+%',        # Percentages
            r'(?:revenue|profit|income|balance|assets|liabilities|equity|cash flow)',
            r'(?:fiscal|quarter|annual|year)',
            r'(?:statement|report|audit)'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
