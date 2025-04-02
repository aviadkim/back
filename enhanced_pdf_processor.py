import os
import re
import json
import logging
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import PyPDF2
from PyPDF2 import PdfReader
import tempfile
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedPDFProcessor:
    """Advanced PDF processor with multi-language support and table detection"""
    
    def __init__(self, language='heb+eng', dpi=300, thread_count=4):
        """Initialize the PDF processor
        
        Args:
            language: OCR language(s), default 'heb+eng' for Hebrew and English
            dpi: Image DPI for OCR, higher values give better results but slower processing
            thread_count: Number of parallel threads for processing
        """
        self.language = language
        self.dpi = dpi
        self.thread_count = thread_count
        self.extraction_dir = 'extractions'
        os.makedirs(self.extraction_dir, exist_ok=True)  # Fixed missing parenthesis here
        
        # Configure pytesseract
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def process_document(self, file_path, document_id=None):
        """Process a PDF document and extract all text, tables, and metadata
        
        Args:
            file_path: Path to the PDF file
            document_id: Optional document ID
            
        Returns:
            Dict with document extraction data
        """
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Get filename from document path
            filename = os.path.basename(file_path)
            if not document_id:
                document_id = filename.split('_')[0] if '_' in filename else os.path.splitext(filename)[0]
            
            # בדיקה אם שם הקובץ כבר מכיל את מזהה המסמך
            if filename.startswith(document_id):
                extraction_path = os.path.join(
                    self.extraction_dir,
                    f"{filename.replace('.pdf', '_extraction.json')}"
                )
            else:
                extraction_path = os.path.join(
                    self.extraction_dir,
                    f"{document_id}_{filename.replace('.pdf', '_extraction.json')}"
                )
            
            # Try PyPDF2 first
            try:
                logger.info(f"Extracting text with PyPDF2: {file_path}")
                reader = PdfReader(file_path)
                if len(reader.pages) > 0:
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    return self._save_extraction(extraction_path, text)
            except Exception as e:
                logger.error(f"Error extracting text with PyPDF2: {str(e)}")
            
            # Fallback to OCR
            logger.info(f"Extracting text with OCR: {file_path}")
            return self._ocr_extract(file_path, extraction_path)
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return None
    
    def _save_extraction(self, path, content):
        """Save extracted content to a file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Extraction completed and saved to {path}")
            return path
        except Exception as e:
            logger.error(f"Failed to save extraction: {str(e)}")
            return None
    
    def _ocr_extract(self, file_path, extraction_path):
        """Fallback OCR extraction"""
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=self.dpi)
            
            # Process images in parallel
            all_text = ""
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_count) as executor:
                # Submit OCR tasks
                future_to_page = {
                    executor.submit(self._process_image, img, i): i 
                    for i, img in enumerate(images)
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(future_to_page):
                    page_idx = future_to_page[future]
                    try:
                        page_text = future.result()
                        all_text += page_text + "\n\n"
                    except Exception as e:
                        logger.error(f"Error processing page {page_idx}: {e}")
            
            return self._save_extraction(extraction_path, all_text)
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return None
    
    def _process_image(self, image, page_idx):
        """Process a single image with OCR"""
        logger.info(f"OCR processing page {page_idx+1}")
        
        try:
            # Apply image preprocessing for better OCR results
            preprocessed = self._preprocess_image(image)
            
            # Run OCR
            text = pytesseract.image_to_string(preprocessed, lang=self.language)
            
            # Clean up text
            text = self._clean_text(text)
            
            return text
        except Exception as e:
            logger.error(f"Error in OCR processing for page {page_idx+1}: {e}")
            return ""
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Optional: Apply additional preprocessing techniques
        # Experiment with these options to see what works best for your documents
        # - Thresholding: gray = gray.point(lambda x: 0 if x < 150 else 255)
        # - Noise reduction: Use PIL's ImageFilter
        
        return gray
    
    def _clean_text(self, text):
        """Clean up OCR text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Pipe to I
        
        return text.strip()

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_pdf_processor.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    processor = EnhancedPDFProcessor()
    result = processor.process_document(pdf_path)
    
    print(f"Processed {result}")
