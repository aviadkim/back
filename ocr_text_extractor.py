# file: ocr_text_extractor.py

import pdf2image
import pytesseract
import os
import json
import sys
import re
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"document_processing_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("document_processor")

def extract_text_with_ocr(pdf_path, language="heb+eng", dpi=300):
    """Extract text from a PDF using OCR with high resolution images for better accuracy"""
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return None
    
    try:
        logger.info(f"Converting PDF to images: {pdf_path}")
        images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
        logger.info(f"PDF has {len(images)} pages")
        
        document = {}
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1}/{len(images)} with OCR...")
            text = pytesseract.image_to_string(image, lang=language)
            
            document[i] = {
                "page_num": i+1,
                "text": text
            }
        
        return document
    
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None

class OCRQuestionAnswering:
    def __init__(self, pdf_path=None, extracted_text=None, language="heb+eng"):
        """Initialize with either a PDF path or pre-extracted text"""
        self.document = None
        self.all_text = ""
        
        if extracted_text:
            self.document = extracted_text
        elif pdf_path:
            self.document = extract_text_with_ocr(pdf_path, language)
        
        # Prepare the document text
        if self.document:
            for page_num, page_data in self.document.items():
                self.all_text += page_data.get("text", "") + "\n\n"
    
    def ask(self, question):
        """Ask a question about the document"""
        if not self.document:
            return "No document loaded"
        
        question = question.lower()
        
        # Answer based on question type
        if "how many pages" in question:
            return f"The document has {len(self.document)} pages."
            
        elif "isin" in question or "international securities identification number" in question:
            # Look for ISIN patterns (12 characters, usually 2 letters followed by numbers)
            isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
            matches = re.findall(isin_pattern, self.all_text)
            if matches:
                return f"I found these potential ISIN numbers: {', '.join(matches)}"
            else:
                return "I couldn't find any ISIN numbers in the document."
        
        elif "ticker" in question or "symbol" in question:
            # Try to extract stock tickers - various patterns
            ticker_patterns = [
                r'\b[A-Z]{1,5}\b',  # Basic US stock pattern (1-5 uppercase letters)
                r'\b[A-Z]{1,4}\.[A-Z]{1,2}\b'  # International pattern like "AAPL.US"
            ]
            all_matches = []
            for pattern in ticker_patterns:
                matches = re.findall(pattern, self.all_text)
                all_matches.extend(matches)
            
            if all_matches:
                # Filter out common words that might match the pattern
                common_words = {'THE', 'AND', 'FOR', 'INC', 'LTD', 'LLC', 'ETF', 'USD', 'EUR', 'GBP', 'CHF'}
                filtered_matches = [m for m in all_matches if m not in common_words]
                if filtered_matches:
                    return f"I found these potential ticker symbols: {', '.join(filtered_matches)}"
            
            return "I couldn't identify any clear ticker symbols in the document."
                
        elif "table" in question:
            # Simple table detection based on whitespace patterns
            potential_tables = []
            lines = self.all_text.split('\n')
            for i, line in enumerate(lines):
                if i < len(lines) - 3:  # Need at least 3 consecutive lines
                    if len(line.strip()) > 20 and '  ' in line:
                        # Check if next lines have similar spacing
                        if '  ' in lines[i+1] and '  ' in lines[i+2]:
                            # This might be a table
                            table_preview = line[:50] + "..."
                            potential_tables.append(table_preview)
            
            if potential_tables:
                return f"I found {len(potential_tables)} potential tables in the document. Here's a preview of one: {potential_tables[0]}"
            else:
                return "I couldn't detect any obvious tables in the text."
                
        else:
            # Split into paragraphs and find relevant ones
            paragraphs = re.split(r'\n\s*\n', self.all_text)
            keywords = [w for w in question.split() if len(w) > 3]
            
            scored_paragraphs = []
            for para in paragraphs:
                if len(para.strip()) < 20:  # Skip short paragraphs
                    continue
                
                score = sum(1 for kw in keywords if kw in para.lower())
                if score > 0:
                    scored_paragraphs.append((para, score))
            
            scored_paragraphs.sort(key=lambda x: x[1], reverse=True)
            
            if scored_paragraphs:
                return f"Based on your question, this might be relevant:\n\n{scored_paragraphs[0][0]}"
            else:
                return "I couldn't find information related to your question."

def main():
    if len(sys.argv) < 2:
        print("Usage: python ocr_text_extractor.py <pdf_path> [question] [language]")
        print("Example: python ocr_text_extractor.py test_documents/sample.pdf 'How many pages?' 'heb+eng'")
        return
    
    pdf_path = sys.argv[1]
    question = sys.argv[2] if len(sys.argv) > 2 else None
    language = sys.argv[3] if len(sys.argv) > 3 else "heb+eng"
    
    if question:
        # Question and answer mode
        qa_system = OCRQuestionAnswering(pdf_path=pdf_path, language=language)
        print(f"Question: {question}")
        answer = qa_system.ask(question)
        print(f"Answer: {answer}")
    else:
        # Just extract text
        document = extract_text_with_ocr(pdf_path, language)
        
        if document:
            print("\n=== Extraction Results ===")
            for page_num, page_data in document.items():
                text = page_data["text"]
                preview = text[:100] + "..." if len(text) > 100 else text
                print(f"Page {page_data['page_num']}: {preview}")
            
            # Save results to file
            output_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_ocr.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(document, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()