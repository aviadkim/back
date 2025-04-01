import pypdf # Keep PyPDF2 for now as per the provided code
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
            # Check if file exists
            if not os.path.exists(pdf_path):
                self.logger.error(f"PDF file not found: {pdf_path}")
                return {"error": f"File not found: {pdf_path}"}

            # First try direct text extraction with PyPDF2
            with open(pdf_path, 'rb') as file:
                try:
                    reader = PdfReader(file)
                    page_count = len(reader.pages)

                    for page_num in range(page_count):
                        try:
                            page = reader.pages[page_num]
                            text = page.extract_text()

                            # If text extraction yields little or no text, use OCR
                            if not text or len(text.strip()) < 50:
                                document.update(self._process_page_with_ocr(pdf_path, page_num))
                                continue

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
                        except Exception as e:
                            self.logger.warning(f"Error processing page {page_num}: {str(e)}")
                            # Try OCR fallback for this page
                            document.update(self._process_page_with_ocr(pdf_path, page_num))

                except Exception as e:
                    self.logger.error(f"PyPDF2 failed to read {pdf_path}: {str(e)}")
                    # Fall back to full OCR processing
                    return self._process_with_ocr_fallback(pdf_path)

            return document
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            return {
                "error": str(e),
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "processing_status": "failed"
                }
            }

    def _process_page_with_ocr(self, pdf_path: str, page_num: int) -> Dict[int, Dict[str, Any]]:
        """Process a single page with OCR when direct extraction fails."""
        try:
            # Convert PDF page to image
            images = pdf2image.convert_from_path(
                pdf_path,
                first_page=page_num+1,
                last_page=page_num+1
            )

            if not images:
                return {page_num: {"text": "", "blocks": [], "images": [], "dimensions": {"width": 0, "height": 0}}}

            image = images[0]

            # Run OCR
            text = pytesseract.image_to_string(
                image,
                lang=self.language
            )

            # Process text into blocks
            blocks = self._process_text_to_blocks(text)

            return {page_num: {
                "text": text,
                "blocks": blocks,
                "images": [],
                "dimensions": {
                    "width": image.width,
                    "height": image.height
                }
            }}
        except Exception as e:
            self.logger.warning(f"OCR fallback failed for page {page_num}: {str(e)}")
            return {page_num: {"text": "", "blocks": [], "images": [], "dimensions": {"width": 0, "height": 0}}}

    def _process_with_ocr_fallback(self, pdf_path: str) -> Dict[int, Dict[str, Any]]:
        """Process the entire document with OCR when direct extraction fails."""
        document = {}
        try:
            # Convert all pages to images
            images = pdf2image.convert_from_path(pdf_path)

            for page_num, image in enumerate(images):
                try:
                    # Process each page as an image
                    text = pytesseract.image_to_string(image, lang=self.language)

                    # Process text into blocks
                    blocks = self._process_text_to_blocks(text)

                    # Store results
                    document[page_num] = {
                        "text": text,
                        "blocks": blocks,
                        "images": [],
                        "dimensions": {
                            "width": image.width,
                            "height": image.height
                        }
                    }
                except Exception as e:
                    self.logger.warning(f"Error processing page {page_num} with OCR: {str(e)}")
                    document[page_num] = {
                        "text": "",
                        "blocks": [],
                        "images": [],
                        "dimensions": {"width": 0, "height": 0}
                    }

            return document
        except Exception as e:
            self.logger.error(f"OCR fallback failed for {pdf_path}: {str(e)}")
            return {
                "error": f"OCR processing failed: {str(e)}",
                "metadata": {
                    "filename": os.path.basename(pdf_path),
                    "processing_status": "failed"
                }
            }

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