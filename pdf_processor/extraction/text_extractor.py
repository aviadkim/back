import PyPDF2
import pdf2image
import pytesseract
import re
import logging
import os
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any, Optional

class PDFTextExtractor:
    """Extract and structure text content from PDF documents.
    
    This module handles the extraction of text while preserving
    document structure, formatting, and layout information.
    With enhanced support for multilingual documents and financial content.
    """
    
    def __init__(self, language="eng+heb"):
        """Initialize the text extractor.
        
        Args:
            language: OCR language to use if needed. Default supports both English and Hebrew.
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
                    self.logger.debug(f"Processing page {page_num+1} of {page_count}")
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Determine if OCR is needed based on text quality
                    use_ocr = self._should_use_ocr(text)
                    
                    if use_ocr:
                        # Convert PDF page to image and use OCR
                        page_images = pdf2image.convert_from_path(
                            pdf_path, 
                            first_page=page_num+1, 
                            last_page=page_num+1,
                            dpi=300  # Higher DPI for better quality
                        )
                        if page_images:
                            # Use improved OCR settings
                            ocr_config = '--psm 6 --oem 3'  # Assume a uniform block of text
                            text = pytesseract.image_to_string(
                                page_images[0], 
                                lang=self.language,
                                config=ocr_config
                            )
                            
                            # Check for right-to-left language
                            if self._is_rtl_dominant(text):
                                # Additional OCR pass with RTL-specific settings
                                ocr_config = '--psm 6 --oem 3 -c preserve_interword_spaces=1'
                                text = pytesseract.image_to_string(
                                    page_images[0], 
                                    lang=self.language,
                                    config=ocr_config
                                )
                    
                    # Extract page dimensions
                    page_box = page.mediabox
                    width = float(page_box.width)
                    height = float(page_box.height)
                    
                    # Detect text direction
                    text_direction = self._detect_text_direction(text)
                    
                    # Process text into blocks with improved structure recognition
                    blocks = self._process_text_to_blocks(text)
                    
                    document[page_num] = {
                        "text": text,
                        "blocks": blocks,
                        "images": [],  # Placeholder for image extraction
                        "dimensions": {
                            "width": width,
                            "height": height
                        },
                        "text_direction": text_direction,
                        "language": self._detect_language(text)
                    }
                
            return document
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path}: {str(e)}")
            raise
    
    def _should_use_ocr(self, text: str) -> bool:
        """Determine if OCR should be used based on text quality.
        
        Args:
            text: Extracted text to analyze
            
        Returns:
            Boolean indicating if OCR should be used
        """
        # Use OCR if text extraction yields little or no text
        if not text or len(text.strip()) < 50:
            return True
            
        # Check for poor text quality indicators
        if len(text.strip()) < 100 and text.count('\n') < 3:
            return True
            
        # Check for text that appears corrupted
        if '�' in text or '□' in text:
            return True
            
        # Check for common OCR issues like missing spaces between words
        words = text.split()
        if words:
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length > 15:  # Unusually long words suggest missing spaces
                return True
                
        return False
    
    def _process_text_to_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Process a text string into blocks with improved structure recognition.
        
        Args:
            text: Text content to process
            
        Returns:
            List of dictionaries containing block data
        """
        blocks = []
        if not text:
            return blocks
            
        # Split text into meaningful blocks
        if '\n\n' in text:
            # Split by double newlines for paragraphs
            paragraphs = re.split(r'\n\s*\n', text)
        else:
            # If no double newlines, try to intelligently split
            paragraphs = self._intelligently_split_text(text)
        
        y_position = 0
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Determine block type based on content
            block_type = "text"
            if self._appears_to_be_heading(paragraph):
                block_type = "heading"
            elif self._appears_to_be_list(paragraph):
                block_type = "list"
            elif self.is_potentially_financial(paragraph):
                block_type = "financial"
            elif self._appears_to_be_table_row(paragraph):
                block_type = "table"
                
            # Estimate block height based on content
            lines = paragraph.split('\n')
            block_height = max(len(lines) * 20, 20)  # At least 20px height
            
            # Detect language of this specific block
            block_language = self._detect_language(paragraph)
            
            blocks.append({
                "text": paragraph,
                "bbox": [20, y_position, 580, y_position + block_height],  # Estimated coordinates
                "block_type": block_type,
                "language": block_language
            })
            
            y_position += block_height + 10  # Add spacing between blocks
                
        return blocks
    
    def _intelligently_split_text(self, text: str) -> List[str]:
        """Split text into meaningful blocks when standard paragraph breaks aren't available.
        
        Args:
            text: Text to split
            
        Returns:
            List of text blocks
        """
        if not text:
            return []
            
        # Split by newlines first
        lines = text.split('\n')
        
        # Group lines into paragraphs
        paragraphs = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            # Check if this line looks like a paragraph start
            if not current_paragraph:
                current_paragraph.append(line)
            elif not line:
                # Empty line ends paragraph
                if current_paragraph:
                    paragraphs.append('\n'.join(current_paragraph))
                    current_paragraph = []
            elif line.endswith(('.', ':', '?', '!')):
                # Line ends with sentence ending punctuation
                current_paragraph.append(line)
                paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = []
            elif self._appears_to_be_heading(line) or line.isupper():
                # Line appears to be a heading
                if current_paragraph:
                    paragraphs.append('\n'.join(current_paragraph))
                current_paragraph = [line]
            elif self._appears_to_be_table_row(line):
                # Line appears to be a table row
                if current_paragraph and not self._appears_to_be_table_row(current_paragraph[-1]):
                    paragraphs.append('\n'.join(current_paragraph))
                    current_paragraph = [line]
                else:
                    current_paragraph.append(line)
            else:
                current_paragraph.append(line)
        
        # Add the last paragraph if it exists
        if current_paragraph:
            paragraphs.append('\n'.join(current_paragraph))
            
        return paragraphs
    
    def _appears_to_be_heading(self, text: str) -> bool:
        """Determine if text appears to be a heading.
        
        Args:
            text: Text to analyze
            
        Returns:
            Boolean indicating if text is likely a heading
        """
        # Check if single line
        if '\n' not in text.strip():
            text = text.strip()
            
            # Check for all caps
            if text.isupper() and len(text) > 3:
                return True
                
            # Check for numbering patterns typical in headings
            if re.match(r'^[\d\.]+\s+[A-Z]', text):
                return True
                
            # Check for short phrases ending with colon
            if len(text) < 100 and text.endswith(':'):
                return True
                
            # Check for financial statement section headers
            if text in ["INCOME STATEMENT", "BALANCE SHEET", "CASH FLOW STATEMENT", 
                      "דוח רווח והפסד", "מאזן", "דוח תזרים מזומנים"]:
                return True
        
        return False
    
    def _appears_to_be_list(self, text: str) -> bool:
        """Determine if text appears to be a list.
        
        Args:
            text: Text to analyze
            
        Returns:
            Boolean indicating if text is likely a list
        """
        lines = text.split('\n')
        if len(lines) < 2:
            return False
            
        # Check if lines start with bullets, numbers, or similar patterns
        list_markers = 0
        for line in lines:
            line = line.strip()
            if re.match(r'^[\d\.]+\s+', line) or re.match(r'^[•\*\-]\s+', line):
                list_markers += 1
                
        # If more than 50% of lines have list markers, consider it a list
        return list_markers > len(lines) / 2
    
    def _appears_to_be_table_row(self, text: str) -> bool:
        """Determine if a line of text appears to be part of a table.
        
        Args:
            text: Text to analyze
            
        Returns:
            Boolean indicating if text is likely a table row
        """
        # Check for multiple whitespace blocks indicating columns
        if re.search(r'\S+\s{3,}\S+', text):
            return True
            
        # Check for pipe characters often used in tables
        if '|' in text and text.count('|') >= 2:
            return True
            
        # Check for tab characters
        if '\t' in text:
            return True
            
        # Check for repeated numeric data (common in financial tables)
        numbers = re.findall(r'(?:[\$€₪]?\s?\d[\d,\.]*\s?%?)', text)
        if len(numbers) >= 3:  # Multiple numeric values suggest a table row
            return True
            
        # Check for ISIN pattern (common in financial documents)
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        if re.search(isin_pattern, text):
            return True
            
        return False
    
    def _detect_language(self, text: str) -> str:
        """Detect the language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('heb' for Hebrew, 'eng' for English, 'mixed' for both)
        """
        if not text:
            return "unknown"
            
        # Regular expressions for Hebrew and English characters
        hebrew_pattern = r'[\u0590-\u05FF\uFB1D-\uFB4F]+'
        english_pattern = r'[a-zA-Z]+'
        
        # Find all matches
        hebrew_chars = len(re.findall(hebrew_pattern, text))
        english_chars = len(re.findall(english_pattern, text))
        
        # Determine dominant language
        if hebrew_chars > 0 and english_chars == 0:
            return "heb"
        elif english_chars > 0 and hebrew_chars == 0:
            return "eng"
        elif hebrew_chars > 0 and english_chars > 0:
            return "mixed"
        else:
            return "unknown"
    
    def _detect_text_direction(self, text: str) -> str:
        """Detect if text is primarily right-to-left or left-to-right.
        
        Args:
            text: Text to analyze
            
        Returns:
            'rtl' for right-to-left, 'ltr' for left-to-right
        """
        # Check for Hebrew characters (RTL)
        hebrew_pattern = r'[\u0590-\u05FF\uFB1D-\uFB4F]'
        hebrew_chars = len(re.findall(hebrew_pattern, text))
        
        # Check for English characters (LTR)
        english_pattern = r'[a-zA-Z]'
        english_chars = len(re.findall(english_pattern, text))
        
        # If significantly more Hebrew than English, consider it RTL
        if hebrew_chars > english_chars * 1.5:
            return "rtl"
        else:
            return "ltr"
    
    def _is_rtl_dominant(self, text: str) -> bool:
        """Check if right-to-left text is dominant.
        
        Args:
            text: Text to analyze
            
        Returns:
            Boolean indicating if RTL is dominant
        """
        return self._detect_text_direction(text) == "rtl"
    
    def is_potentially_financial(self, text: str) -> bool:
        """Determine if text likely contains financial information.
        
        Args:
            text: Text content to analyze
            
        Returns:
            Boolean indicating if text contains financial indicators
        """
        # Financial indicators: dollar signs, percentages, numbers with commas
        financial_patterns = [
            # English patterns
            r'\$[\d,]+\.?\d*',  # Dollar amounts
            r'[\d,]+\.?\d*\s*[€£₪]',  # Euro, Pound, Shekel amounts
            r'\d+\.\d+%',        # Percentages
            r'(?:revenue|profit|income|balance|assets|liabilities|equity|cash flow)',
            r'(?:fiscal|quarter|annual|year)',
            r'(?:statement|report|audit)',
            r'(?:ISIN|איסין)\s*:?\s*[A-Z0-9]+', # ISIN numbers
            
            # Hebrew patterns
            r'₪[\d,]+\.?\d*',  # Shekel amounts (symbol first)
            r'[\d,]+\.?\d*\s*?ש"ח',  # Shekel amounts (abbreviation)
            r'(?:הכנסות|רווח|הפסד|מאזן|נכסים|התחייבויות|הון|תזרים מזומנים)',
            r'(?:רבעון|שנתי|דו״ח|דוח|תשואה)',
            r'(?:ני"ע|ניירות ערך|אגרות חוב|אג"ח|מניות)'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False

    def extract_document_with_enhanced_ocr(self, pdf_path: str) -> Dict[int, Dict[str, Any]]:
        """Extract text with enhanced OCR processing for difficult documents.
        
        This method applies more aggressive image processing techniques and 
        multiple OCR passes to handle low-quality scans or complex layouts.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with page numbers as keys and page content as values
        """
        document = {}
        try:
            # Convert all pages to images
            images = pdf2image.convert_from_path(pdf_path, dpi=300)
            
            for page_num, img in enumerate(images):
                self.logger.debug(f"Enhanced OCR processing for page {page_num+1}")
                
                # Convert PIL image to OpenCV format
                open_cv_image = np.array(img)
                open_cv_image = open_cv_image[:, :, ::-1].copy()  # RGB to BGR
                
                # Apply image preprocessing
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                
                # Apply threshold to get black and white image
                _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                
                # Apply noise reduction
                denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
                
                # Apply OCR with multiple language settings
                text_eng = pytesseract.image_to_string(
                    denoised, 
                    lang="eng",
                    config='--psm 6 --oem 3'
                )
                
                text_heb = pytesseract.image_to_string(
                    denoised, 
                    lang="heb",
                    config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
                )
                
                text_mixed = pytesseract.image_to_string(
                    denoised, 
                    lang=self.language,
                    config='--psm 6 --oem 3'
                )
                
                # Select the best text based on content
                final_text = self._select_best_ocr_result([text_eng, text_heb, text_mixed])
                
                # Process text into blocks
                blocks = self._process_text_to_blocks(final_text)
                
                # Detect text direction
                text_direction = self._detect_text_direction(final_text)
                
                document[page_num] = {
                    "text": final_text,
                    "blocks": blocks,
                    "images": [],
                    "dimensions": {
                        "width": img.width,
                        "height": img.height
                    },
                    "text_direction": text_direction,
                    "language": self._detect_language(final_text),
                    "extraction_method": "enhanced_ocr"
                }
                
            return document
        except Exception as e:
            self.logger.error(f"Failed to extract text with enhanced OCR from {pdf_path}: {str(e)}")
            raise
            
    def _select_best_ocr_result(self, texts: List[str]) -> str:
        """Select the best OCR result from multiple processing attempts.
        
        Args:
            texts: List of text results from different OCR processes
            
        Returns:
            The best text based on quality heuristics
        """
        if not texts:
            return ""
            
        # Calculate scores for each text
        scores = []
        
        for text in texts:
            score = 0
            
            # Score based on text length (longer is usually better)
            score += len(text) * 0.01
            
            # Score based on word count (more words is usually better)
            words = text.split()
            score += len(words) * 0.5
            
            # Score based on financial indicators (higher for financial documents)
            if self.is_potentially_financial(text):
                score += 10
                
            # Score based on ISIN detection
            isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
            isin_matches = re.findall(isin_pattern, text)
            score += len(isin_matches) * 5
            
            # Score based on recognized numeric values
            numeric_pattern = r'[\d,]+\.?\d*'
            numeric_matches = re.findall(numeric_pattern, text)
            score += len(numeric_matches) * 0.2
            
            scores.append(score)
        
        # Return the text with the highest score
        if scores:
            best_index = scores.index(max(scores))
            return texts[best_index]
        else:
            # Fallback to the first text
            return texts[0] if texts else ""