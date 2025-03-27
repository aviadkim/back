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
    
    def __init__(self):
        """Initialize the PDF processor"""
        # Configure pytesseract path if needed
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def process_pdf(self, file_path, language='he'):
        """
        Process a PDF file and extract text content
        
        Args:
            file_path (str): Path to the PDF file
            language (str): Language code for OCR (default: 'he')
            
        Returns:
            tuple: (extracted_text, metadata, page_count)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        try:
            # Extract text using PyPDF2
            extracted_text, metadata, page_count = self._extract_text_with_pypdf(file_path)
            
            # Check if significant text was extracted
            if not self._has_significant_text(extracted_text, page_count):
                logger.info(f"PDF has insufficient text, using OCR for: {file_path}")
                # Use OCR if PDF has insufficient text
                extracted_text = self._extract_text_with_ocr(file_path, language)
                
            # Extract additional metadata
            metadata = self._extract_metadata(file_path, extracted_text, metadata)
                
            return extracted_text, metadata, page_count
            
        except Exception as e:
            logger.exception(f"Error processing PDF: {str(e)}")
            raise
    
    def _extract_text_with_pypdf(self, file_path):
        """
        Extract text from PDF using pypdf
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            tuple: (extracted_text, metadata, page_count)
        """
        try:
            pdf_reader = PdfReader(file_path)
            page_count = len(pdf_reader.pages)
            
            # Extract metadata
            metadata = {}
            if pdf_reader.metadata:
                # Use attribute access for metadata (PyPDF2 >= 3.0.0)
                metadata = {
                    'title': pdf_reader.metadata.title if pdf_reader.metadata.title else '',
                    'author': pdf_reader.metadata.author if pdf_reader.metadata.author else '',
                    'creator': pdf_reader.metadata.creator if pdf_reader.metadata.creator else '',
                    'producer': pdf_reader.metadata.producer if pdf_reader.metadata.producer else '',
                    # CreationDate might still need dictionary access or specific handling
                    'created_date': pdf_reader.metadata.creation_date.isoformat() if pdf_reader.metadata.creation_date else '',
                }
            
            # Extract text from each page
            full_text = ""
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text() or ""
                full_text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
            return full_text, metadata, page_count
            
        except Exception as e:
            logger.exception(f"Error extracting text with pypdf: {str(e)}")
            raise
    
    def _extract_text_with_ocr(self, file_path, language='he'):
        """
        Extract text from PDF using OCR
        
        Args:
            file_path (str): Path to the PDF file
            language (str): Language code for OCR
            
        Returns:
            str: Extracted text
        """
        try:
            # Map language code to Tesseract language
            ocr_language = 'heb' if language == 'he' else 'eng'
            
            # Convert PDF to images
            images = convert_from_path(file_path)
            
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
    
    def _extract_metadata(self, file_path, text, existing_metadata):
        """
        Extract additional metadata from the text content
        
        Args:
            file_path (str): Path to the PDF file
            text (str): Extracted text
            existing_metadata (dict): Existing metadata
            
        Returns:
            dict: Enhanced metadata
        """
        metadata = existing_metadata.copy()
        
        # Try to detect document type from content
        metadata['detected_document_type'] = self._detect_document_type(text)
        
        # Extract dates
        dates = self._extract_dates(text)
        if dates:
            metadata['extracted_dates'] = dates
            # Use the first date as the document date
            metadata['document_date'] = dates[0]
        
        # Extract financial entities
        financial_entities = self._extract_financial_entities(text)
        if financial_entities:
            metadata['financial_entities'] = financial_entities
        
        return metadata
    
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
        
        return entities
