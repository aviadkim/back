import PyPDF2
import os
from utils.logger import logger

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file with better error handling."""
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) == 0:
                logger.warning("PDF file is empty")
                return ""
                
            text = []
            for page in reader.pages:
                try:
                    text.append(page.extract_text())
                except Exception as e:
                    logger.warning(f"Error extracting text from page: {str(e)}")
                    text.append("")
                    
            return "\n".join(text)
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise
