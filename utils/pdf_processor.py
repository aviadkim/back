import os
import logging
import tempfile
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader # Changed from PyPDF2
import re
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class PDFProcessor:
    """
    Utility class for processing PDF files
    
    This class handles PDF text extraction with OCR if needed.
    """
    
    def __init__(self, file_path=None):
        """Initialize the PDF processor with an optional file path"""
        # Configure pytesseract path if needed
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        
        self.file_path = file_path
    
    def extract_text(self, language='he'):
        """
        Extract text from PDF file
        
        Args:
            language (str): Language code for OCR (default: 'he')
            
        Returns:
            str: Extracted text
        """
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PDF file not found: {self.file_path}")
            
        try:
            logger.info(f"Extracting text from {self.file_path}")
            # Extract text using PyPDF
            pdf_reader = PdfReader(self.file_path)
            page_count = len(pdf_reader.pages)
            
            # Extract text from each page
            full_text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ""
                full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
            # Check if significant text was extracted
            if not self._has_significant_text(full_text, page_count):
                logger.info(f"PDF has insufficient text, using OCR for: {self.file_path}")
                # Use OCR if PDF has insufficient text
                full_text = self._extract_text_with_ocr(language)
                
            return full_text
            
        except Exception as e:
            logger.exception(f"Error extracting text: {str(e)}")
            raise
    
    def extract_metadata(self):
        """
        Extract metadata from PDF file
        
        Returns:
            dict: Metadata dictionary
        """
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError(f"PDF file not found: {self.file_path}")
            
        try:
            logger.info(f"Extracting metadata from {self.file_path}")
            # Use PyPDF to extract metadata
            pdf_reader = PdfReader(self.file_path)
            page_count = len(pdf_reader.pages)
            
            # Extract basic metadata
            metadata = {
                'pages_count': page_count,
                'filename': os.path.basename(self.file_path),
                'filesize': os.path.getsize(self.file_path),
            }
            
            # Extract document metadata if available
            if pdf_reader.metadata:
                # Use attribute access for metadata (PyPDF >= 3.0.0)
                if hasattr(pdf_reader.metadata, 'title') and pdf_reader.metadata.title:
                    metadata['title'] = pdf_reader.metadata.title
                if hasattr(pdf_reader.metadata, 'author') and pdf_reader.metadata.author:
                    metadata['author'] = pdf_reader.metadata.author
                if hasattr(pdf_reader.metadata, 'creator') and pdf_reader.metadata.creator:
                    metadata['creator'] = pdf_reader.metadata.creator
                if hasattr(pdf_reader.metadata, 'producer') and pdf_reader.metadata.producer:
                    metadata['producer'] = pdf_reader.metadata.producer
                # Handle dates carefully
                if hasattr(pdf_reader.metadata, 'creation_date') and pdf_reader.metadata.creation_date:
                    try:
                        metadata['creation_date'] = pdf_reader.metadata.creation_date.isoformat()
                    except:
                        # Fallback if date parsing fails
                        metadata['creation_date'] = str(pdf_reader.metadata.creation_date)
                
                if hasattr(pdf_reader.metadata, 'modification_date') and pdf_reader.metadata.modification_date:
                    try:
                        metadata['modification_date'] = pdf_reader.metadata.modification_date.isoformat()
                    except:
                        # Fallback if date parsing fails
                        metadata['modification_date'] = str(pdf_reader.metadata.modification_date)
            
            # Try to detect document type based on content
            extracted_text = self.extract_text()
            document_type = self._detect_document_type(extracted_text)
            metadata['document_type'] = document_type
            
            # Extract additional metadata
            metadata.update(self._extract_additional_metadata(extracted_text))
            
            return metadata
            
        except Exception as e:
            logger.exception(f"Error extracting metadata: {str(e)}")
            raise
    
    def _extract_text_with_ocr(self, language='he'):
        """
        Extract text from PDF using OCR
        
        Args:
            language (str): Language code for OCR
            
        Returns:
            str: Extracted text
        """
        try:
            # Map language code to Tesseract language
            ocr_language = 'heb' if language == 'he' else 'eng'
            
            # Convert PDF to images
            images = convert_from_path(self.file_path)
            
            full_text = ""
            for i, image in enumerate(images):
                # Use pytesseract to extract text
                page_text = pytesseract.image_to_string(image, lang=ocr_language)
                full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
            return full_text
            
        except Exception as e:
            logger.exception(f"Error extracting text with OCR: {str(e)}")
            raise
    
    def _has_significant_text(self, text, page_count):
        """
        Check if the extracted text has significant content
        
        Args:
            text (str): Extracted text
            page_count (int): Number of pages
            
        Returns:
            bool: True if text is significant, False otherwise
        """
        # Remove whitespace and newlines
        clean_text = text.replace('\n', ' ').replace('\r', ' ').strip()
        
        # Calculate expected minimum characters per page (very rough heuristic)
        min_chars_per_page = 100
        expected_min_chars = page_count * min_chars_per_page
        
        return len(clean_text) >= expected_min_chars
    
    def _detect_document_type(self, text):
        """
        Detect document type from text content
        
        Args:
            text (str): Document text
            
        Returns:
            str: Detected document type
        """
        text_lower = text.lower()
        
        # Bank statement indicators
        bank_indicators = [
            'דף חשבון', 'bank statement', 'תנועות בחשבון', 'יתרה', 'balance',
            'פעולות אחרונות', 'recent transactions', 'מצב חשבון'
        ]
        
        # Investment report indicators
        investment_indicators = [
            'דוח השקעות', 'investment report', 'תיק השקעות', 'portfolio',
            'נכסים פיננסיים', 'financial assets', 'נירות ערך', 'securities'
        ]
        
        # Tax document indicators
        tax_indicators = [
            'דוח מס', 'tax report', 'מס הכנסה', 'income tax',
            'אישור מס', 'tax certificate', 'אישור ניכוי מס', 'tax withholding'
        ]
        
        # Invoice indicators
        invoice_indicators = [
            'חשבונית מס', 'tax invoice', 'חשבונית', 'invoice',
            'מספר חשבונית', 'invoice number', 'פרטי חשבונית'
        ]
        
        # Receipt indicators
        receipt_indicators = [
            'קבלה', 'receipt', 'אישור תשלום', 'payment confirmation',
            'תודה על קנייתך', 'thank you for your purchase'
        ]
        
        # Check for document type indicators
        for indicator in bank_indicators:
            if indicator in text_lower:
                return 'bankStatement'
                
        for indicator in investment_indicators:
            if indicator in text_lower:
                return 'investmentReport'
                
        for indicator in tax_indicators:
            if indicator in text_lower:
                return 'taxDocument'
                
        for indicator in invoice_indicators:
            if indicator in text_lower:
                return 'invoice'
                
        for indicator in receipt_indicators:
            if indicator in text_lower:
                return 'receipt'
                
        # Default to other if no known type is detected
        return 'other'
    
    def _extract_additional_metadata(self, text):
        """
        Extract additional metadata from text content
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Additional metadata
        """
        metadata = {}
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            metadata['extracted_dates'] = dates
        
        # Extract financial entities
        financial_entities = self._extract_financial_entities(text)
        if financial_entities:
            metadata['financial_entities'] = financial_entities
        
        return metadata
    
    def _extract_dates(self, text):
        """
        Extract dates from text
        
        Args:
            text (str): Document text
            
        Returns:
            list: List of extracted dates
        """
        # Patterns for common date formats in Hebrew and English documents
        patterns = [
            # DD/MM/YYYY
            r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})',
            # MM/DD/YYYY (US format)
            r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})',
            # YYYY-MM-DD (ISO format)
            r'(\d{4}[/.-]\d{1,2}[/.-]\d{1,2})',
            # Hebrew date formats with month names
            r'(\d{1,2}\s+(?:ינואר|פברואר|מרץ|מרס|אפריל|מאי|יוני|יולי|אוגוסט|ספטמבר|אוקטובר|נובמבר|דצמבר)\s+\d{4})',
            # English date formats with month names
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})',
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
            
        # Remove duplicates while preserving order
        unique_dates = []
        for date in dates:
            if date not in unique_dates:
                unique_dates.append(date)
                
        return unique_dates
    
    def _extract_financial_entities(self, text):
        """
        Extract financial entities like account numbers, amounts, etc.
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Dictionary of extracted financial entities
        """
        entities = {}
        
        # Extract currency amounts
        currency_pattern = r'₪\s*([\d,.]+)|(\d+(?:,\d+)*(?:\.\d+)?)\s*₪|\$\s*([\d,.]+)|€\s*([\d,.]+)'
        currency_matches = re.findall(currency_pattern, text)
        
        if currency_matches:
            amounts = []
            for match in currency_matches:
                # Each match is a tuple of capture groups
                amount = next((group for group in match if group), None)
                if amount:
                    # Clean up amount (remove commas)
                    amount = amount.replace(',', '')
                    try:
                        amount = float(amount)
                        amounts.append(amount)
                    except ValueError:
                        pass
                        
            if amounts:
                entities['currency_amounts'] = amounts
                
                # Get statistics
                entities['max_amount'] = max(amounts)
                entities['min_amount'] = min(amounts)
                entities['avg_amount'] = sum(amounts) / len(amounts)
        
        # Extract account numbers
        account_pattern = r'חשבון\s*(?:מספר)?\s*:?\s*(\d{3,}[-\s]?\d{4,})|ח-ן\s*:?\s*(\d{3,}[-\s]?\d{4,})|account\s*(?:number)?\s*:?\s*(\d{3,}[-\s]?\d{4,})'
        account_matches = re.findall(account_pattern, text, re.IGNORECASE)
        
        if account_matches:
            account_numbers = []
            for match in account_matches:
                # Each match is a tuple of capture groups
                account = next((group for group in match if group), None)
                if account:
                    account_numbers.append(account.strip())
                    
            if account_numbers:
                entities['account_numbers'] = account_numbers
        
        # Extract IDs (Israeli ID numbers are 9 digits)
        id_pattern = r'ת\.?ז\.?\s*:?\s*(\d{9})|תעודת\s*זהות\s*:?\s*(\d{9})|ID\s*(?:number)?\s*:?\s*(\d{9})'
        id_matches = re.findall(id_pattern, text, re.IGNORECASE)
        
        if id_matches:
            ids = []
            for match in id_matches:
                # Each match is a tuple of capture groups
                id_num = next((group for group in match if group), None)
                if id_num:
                    ids.append(id_num.strip())
                    
            if ids:
                entities['id_numbers'] = ids
                
        # Extract ISIN numbers (International Securities Identification Number)
        isin_pattern = r'([A-Z]{2}[A-Z0-9]{9}\d)'
        isin_matches = re.findall(isin_pattern, text)
        
        if isin_matches:
            entities['isin_numbers'] = list(set(isin_matches))  # Unique ISINs
        
        return entities
