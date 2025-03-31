import os
import tempfile
import logging
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path

logger = logging.getLogger(__name__)

class EnhancedOCR:
    """Enhanced OCR with support for multiple languages and image preprocessing."""
    
    def __init__(self, config=None):
        """Initialize the OCR processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.engine = self.config.get('ocr_engine', 'tesseract')
        
        # Language settings
        self.default_language = self.config.get('default_language', 'eng')
        self.additional_languages = self.config.get('additional_languages', ['heb'])
        
        # Specify tesseract configuration
        self.tesseract_config = '--psm 6'  # Assume a single uniform block of text
        
        # Initialize loggers
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized EnhancedOCR with engine: {self.engine}")
        
    def process_image(self, image, language=None):
        """Process an image with OCR.
        
        Args:
            image: PIL Image object or path to image
            language: Language code (e.g., 'eng', 'heb', 'auto')
            
        Returns:
            Extracted text
        """
        if language is None:
            language = self.default_language
            
        # Convert path to image if necessary
        if isinstance(image, str) or isinstance(image, Path):
            image = Image.open(image)
            
        # Apply image preprocessing
        preprocessed_image = self._preprocess_image(image)
        
        # Select language
        if language == 'auto':
            lang_param = f"{self.default_language}+{'+'.join(self.additional_languages)}"
        else:
            lang_param = language
            
        try:
            # Run OCR
            text = pytesseract.image_to_string(
                preprocessed_image,
                lang=lang_param,
                config=self.tesseract_config
            )
            
            # Post-process the text if it contains Hebrew
            if 'heb' in lang_param or self._contains_hebrew(text):
                text = self._post_process_hebrew(text)
                
            return text
        except Exception as e:
            self.logger.error(f"OCR error: {str(e)}")
            return ""
    
    def process_pdf_page(self, pdf_path, page_number, language=None):
        """Process a specific page from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number (0-based)
            language: Language code (e.g., 'eng', 'heb', 'auto')
            
        Returns:
            Extracted text
        """
        try:
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path,
                first_page=page_number + 1,
                last_page=page_number + 1
            )
            
            if not images:
                self.logger.warning(f"Failed to convert PDF page {page_number} to image")
                return ""
                
            # Process the image
            return self.process_image(images[0], language)
        except Exception as e:
            self.logger.error(f"Error processing PDF page {page_number}: {str(e)}")
            return ""
    
    def _preprocess_image(self, image):
        """Preprocess image to improve OCR accuracy.
        
        Args:
            image: PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert PIL image to OpenCV format
        img = np.array(image)
        
        # Convert to grayscale if the image is color
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
            
        # Apply adaptive thresholding
        binary = cv2.adaptiveThreshold(
            gray, 
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, h=10)
        
        # Convert back to PIL Image
        return Image.fromarray(denoised)
    
    def _contains_hebrew(self, text):
        """Check if text contains Hebrew characters."""
        # Hebrew Unicode range: 0x0590-0x05FF
        for char in text:
            if '\u0590' <= char <= '\u05FF':
                return True
        return False
    
    def _post_process_hebrew(self, text):
        """Post-process text containing Hebrew characters.
        
        This handles RTL text and fixes common OCR issues with Hebrew.
        """
        # Add RTL mark at the beginning of lines with Hebrew
        rtl_mark = '\u200F'  # Right-to-Left Mark
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            if self._contains_hebrew(line):
                # Add RTL mark to beginning of line
                processed_lines.append(rtl_mark + line)
            else:
                processed_lines.append(line)
        
        # Join lines and return
        return '\n'.join(processed_lines)