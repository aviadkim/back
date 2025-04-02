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
        
        # Configure pytesseract
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def process_document(self, file_path, output_dir='extractions'):
        """Process a PDF document and extract all text, tables, and metadata
        
        Args:
            file_path: Path to the PDF file
            output_dir: Directory to save extracted data
            
        Returns:
            Dict with document extraction data
        """
        logger.info(f"Processing document: {file_path}")
        
        # Create document ID from filename
        filename = os.path.basename(file_path)
        document_id = filename.split('_')[0] if '_' in filename else os.path.splitext(filename)[0]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract text with hybrid approach (PyPDF2 + OCR)
        extraction_result = self._extract_text_hybrid(file_path)
        
        # Save extraction result
        output_path = os.path.join(output_dir, f"{document_id}_extraction.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Extraction completed and saved to {output_path}")
        
        return extraction_result
    
    def _extract_text_hybrid(self, file_path):
        """Extract text using both PyPDF2 and OCR for optimal results"""
        # First try to extract text with PyPDF2
        pdf_text = self._extract_text_pypdf2(file_path)
        
        # Then extract with OCR
        ocr_text, ocr_pages = self._extract_text_ocr(file_path)
        
        # Merge results - use PyPDF2 text if it has meaningful content, else OCR
        merged_pages = []
        pdf_reader = PyPDF2.PdfReader(open(file_path, 'rb'))
        page_count = len(pdf_reader.pages)
        
        for i in range(page_count):
            # Get text from both methods
            pdf_page_text = pdf_text.get(i, "").strip()
            ocr_page_text = ocr_pages[i] if i < len(ocr_pages) else ""
            
            # Use PyPDF2 text if it has reasonable length and content
            if len(pdf_page_text) > 100 and not self._is_garbage_text(pdf_page_text):
                page_text = pdf_page_text
                source = "pypdf2"
            else:
                page_text = ocr_page_text
                source = "ocr"
            
            merged_pages.append({
                "page_num": i + 1,
                "text": page_text,
                "source": source
            })
        
        # Combine all text
        full_text = "\n\n".join([page["text"] for page in merged_pages])
        
        # Extract tables from text
        tables = self._detect_tables(full_text, merged_pages)
        
        return {
            "document_id": os.path.splitext(os.path.basename(file_path))[0],
            "filename": os.path.basename(file_path),
            "page_count": page_count,
            "language": self.language,
            "content": full_text,
            "pages": merged_pages,
            "tables": tables
        }
    
    def _extract_text_pypdf2(self, file_path):
        """Extract text using PyPDF2"""
        logger.info(f"Extracting text with PyPDF2: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                pages_text = {}
                for i in range(page_count):
                    page = pdf_reader.pages[i]
                    pages_text[i] = page.extract_text()
                
                return pages_text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return {}
    
    def _extract_text_ocr(self, file_path):
        """Extract text using OCR"""
        logger.info(f"Extracting text with OCR: {file_path}")
        
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=self.dpi)
            
            # Process images in parallel
            all_text = ""
            pages_text = []
            
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
                        # Ensure pages are added in correct order
                        while len(pages_text) <= page_idx:
                            pages_text.append("")
                        pages_text[page_idx] = page_text
                        all_text += page_text + "\n\n"
                    except Exception as e:
                        logger.error(f"Error processing page {page_idx}: {e}")
            
            return all_text, pages_text
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return "", []
    
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
    
    def _is_garbage_text(self, text):
        """Check if text appears to be garbage/encoded"""
        # Define potential indicators of garbage text
        garbage_indicators = [
            # High ratio of special characters
            len(re.findall(r'[^\w\s\.,;:\-\'\"()]', text)) / max(len(text), 1) > 0.2,
            # Extremely long "words" (likely garbage)
            any(len(word) > 25 for word in text.split()),
            # Very few spaces in a long text (likely encoding issue)
            len(text) > 100 and text.count(' ') < len(text) / 50
        ]
        
        return any(garbage_indicators)
    
    def _detect_tables(self, text, pages):
        """Detect and extract tables from text"""
        tables = []
        
        # Look for table patterns in each page
        for page in pages:
            page_text = page["text"]
            page_num = page["page_num"]
            
            # Method 1: Look for consistent spacing patterns (potential table rows)
            rows = self._detect_aligned_text_rows(page_text)
            if rows and len(rows) >= 3:  # At least 3 rows to consider it a table
                table = {
                    "page": page_num,
                    "rows": rows,
                    "detection_method": "aligned_text"
                }
                
                # Try to identify headers
                if len(rows) > 0:
                    table["headers"] = rows[0]
                
                tables.append(table)
            
            # Method 2: Look for potential CSV/TSV-like data
            csv_rows = self._detect_csv_like_data(page_text)
            if csv_rows and len(csv_rows) >= 3:
                table = {
                    "page": page_num,
                    "rows": csv_rows,
                    "detection_method": "csv_like"
                }
                
                # Try to identify headers
                if len(csv_rows) > 0:
                    table["headers"] = csv_rows[0]
                
                tables.append(table)
        
        # Filter duplicates
        unique_tables = self._filter_duplicate_tables(tables)
        
        return unique_tables
    
    def _detect_aligned_text_rows(self, text):
        """Detect text that's aligned in columns (potential table)"""
        lines = text.split('\n')
        aligned_rows = []
        
        # Look for lines with similar spacing patterns
        for line in lines:
            # Skip short lines or lines with excessive spaces
            if len(line.strip()) < 10 or line.count('  ') > 10:
                continue
            
            # Look for multiple spaces as column separators
            if '  ' in line:
                # Split by multiple spaces
                columns = re.split(r'\s{2,}', line.strip())
                if len(columns) >= 2:  # At least 2 columns
                    aligned_rows.append(columns)
        
        # Check if we have consistent number of columns
        if aligned_rows:
            column_counts = [len(row) for row in aligned_rows]
            most_common_count = max(set(column_counts), key=column_counts.count)
            
            # Filter to keep only rows with consistent column count
            aligned_rows = [row for row in aligned_rows if len(row) == most_common_count]
        
        return aligned_rows
    
    def _detect_csv_like_data(self, text):
        """Detect CSV-like data in text"""
        lines = text.split('\n')
        csv_rows = []
        
        # Look for lines with consistent delimiter patterns
        for line in lines:
            # Skip short lines
            if len(line.strip()) < 10:
                continue
            
            # Check common delimiters (comma, tab, semicolon, pipe)
            for delimiter in [',', '\t', ';', '|']:
                if delimiter in line and line.count(delimiter) >= 2:
                    columns = [col.strip() for col in line.split(delimiter)]
                    if all(columns) and len(columns) >= 3:  # Non-empty columns
                        csv_rows.append(columns)
                        break
        
        # Check if we have consistent number of columns
        if csv_rows:
            column_counts = [len(row) for row in csv_rows]
            most_common_count = max(set(column_counts), key=column_counts.count)
            
            # Filter to keep only rows with consistent column count
            csv_rows = [row for row in csv_rows if len(row) == most_common_count]
        
        return csv_rows
    
    def _filter_duplicate_tables(self, tables):
        """Filter duplicate tables"""
        if not tables:
            return []
        
        unique_tables = []
        for table in tables:
            # Check if this table is a duplicate
            is_duplicate = False
            for unique_table in unique_tables:
                # Compare first few rows
                if (unique_table["page"] == table["page"] and
                    len(unique_table["rows"]) > 0 and
                    len(table["rows"]) > 0 and
                    unique_table["rows"][0] == table["rows"][0]):
                    
                    # If first row matches, likely duplicate
                    is_duplicate = True
                    
                    # Keep the one with more rows
                    if len(table["rows"]) > len(unique_table["rows"]):
                        unique_tables.remove(unique_table)
                        unique_tables.append(table)
                    
                    break
            
            if not is_duplicate:
                unique_tables.append(table)
        
        return unique_tables

# Usage example
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_pdf_processor.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    processor = EnhancedPDFProcessor()
    result = processor.process_document(pdf_path)
    
    print(f"Processed {result['filename']}")
    print(f"Page count: {result['page_count']}")
    print(f"Extracted {len(result['content'])} characters of text")
    print(f"Detected {len(result['tables'])} potential tables")
