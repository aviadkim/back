import PyPDF2
import pdf2image
import pytesseract
import re
import logging
import os
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
            # First try direct text extraction with PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                
                for page_num in range(page_count):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    # If text extraction yields little or no text, use OCR
                    if not text or len(text.strip()) < 50:
                        # Convert PDF page to image and use OCR
                        page_images = pdf2image.convert_from_path(
                            pdf_path, 
                            first_page=page_num+1, 
                            last_page=page_num+1
                        )
                        if page_images:
                            text = pytesseract.image_to_string(
                                page_images[0], 
                                lang=self.language
                            )
                    
                    # Extract page dimensions
                    page_box = page.mediabox
                    width = float(page_box.width)
                    height = float(page_box.height)
                    
                    # Process text into blocks (simplified)
                    blocks = self._process_text_to_blocks(text)
                    
                    document[page_num] = {
                        "text": text,
                        "blocks": blocks,
                        "images": [],  # Placeholder for image extraction
                        "dimensions": {
                            "width": width,
                            "height": height
                        }
                    }
                
            return document
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            raise
    
    def _process_text_to_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Process a text string into blocks based on paragraphs.
        
        Args:
            text: Text content to process
            
        Returns:
            List of dictionaries containing block data
        """
        blocks = []
        if not text:
            return blocks
            
        # Split text into paragraphs by double newlines
        paragraphs = text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                blocks.append({
                    "text": paragraph.strip(),
                    "bbox": [0, i*50, 500, (i+1)*50],  # Placeholder coordinates
                    "block_type": "text"
                })
                
        return blocks
    
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
