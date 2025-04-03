#!/usr/bin/env python3
"""
Test the document Q&A system with a real PDF file.
This script uploads a PDF file, processes it, and then asks questions about its content.
"""
import os
import sys
import requests
import json
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PDFQATest")

class DocumentQATester:
    """Test the document Q&A system with a real PDF"""
    
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.document_id = None
        self.pdf_path = None
    
    def find_pdf_file(self):
        """Find a PDF file to test with"""
        # Look for PDF files in common locations
        search_paths = [
            '/workspaces/back/uploads',
            '/workspaces/back/test_files',
            '/workspaces/back'
        ]
        
        pdf_files = []
        for path in search_paths:
            if os.path.exists(path):
                pdf_files.extend([
                    os.path.join(path, f) 
                    for f in os.listdir(path) 
                    if f.lower().endswith('.pdf')
                ])
        
        if not pdf_files:
            # Create a temporary PDF file if none found
            logger.warning("No PDF files found, creating a sample PDF")
            from reportlab.pdfgen import canvas
            
            sample_path = '/workspaces/back/uploads/sample_financial_report.pdf'
            os.makedirs('/workspaces/back/uploads', exist_ok=True)
            
            c = canvas.Canvas(sample_path)
            c.setFont("Helvetica", 12)
            
            # Add some financial content
            c.drawString(100, 800, "XYZ Investment Holdings - Portfolio Statement")
            c.drawString(100, 780, "Client: John Smith")
            c.drawString(100, 760, "Account Number: 12345678")
            c.drawString(100, 740, "Date: March 31, 2025")
            c.drawString(100, 720, "Valuation Date: March 30, 2025")
            c.drawString(100, 700, "-------------------------------------------")
            
            c.drawString(100, 680, "Portfolio Summary:")
            c.drawString(120, 660, "Total Value: $1,745,320.50")
            c.drawString(120, 640, "Stocks: 65% ($1,134,458.33)")
            c.drawString(120, 620, "Bonds: 25% ($436,330.13)")
            c.drawString(120, 600, "Cash: 10% ($174,532.05)")
            
            c.drawString(100, 580, "Holdings:")
            c.drawString(120, 560, "1. Apple Inc. (AAPL) - ISIN US0378331005")
            c.drawString(140, 540, "Shares: 500")
            c.drawString(140, 520, "Price: $175.25")
            c.drawString(140, 500, "Value: $87,625.00")
            
            c.drawString(120, 480, "2. Microsoft Corp (MSFT) - ISIN US5949181045")
            c.drawString(140, 460, "Shares: 320")
            c.drawString(140, 440, "Price: $380.50")
            c.drawString(140, 420, "Value: $121,760.00")
            
            c.drawString(120, 400, "3. Tesla Inc (TSLA) - ISIN US88160R1014")
            c.drawString(140, 380, "Shares: 200")
            c.drawString(140, 360, "Price: $173.80")
            c.drawString(140, 340, "Value: $34,760.00")
            
            c.drawString(100, 320, "Performance Summary:")
            c.drawString(120, 300, "YTD Return: +8.45%")
            c.drawString(120, 280, "1 Year Return: +12.37%")
            c.drawString(120, 260, "3 Year Return: +45.12%")
            
            c.save()
            
            pdf_files = [sample_path]
        
        self.pdf_path = pdf_files[0]
        logger.info(f"Using PDF file: {self.pdf_path}")
        return self.pdf_path
    
    def upload_document(self):
        """Upload the PDF file"""
        if not self.pdf_path:
            self.find_pdf_file()
            
        logger.info(f"Uploading document {self.pdf_path}")
        
        with open(self.pdf_path, 'rb') as file:
            files = {'file': file}
            data = {'language': 'heb+eng'}
            
            response = self.session.post(
                f"{self.base_url}/api/documents/upload", 
                files=files, 
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.document_id = result.get('document_id')
                logger.info(f"Document uploaded successfully: {self.document_id}")
                return True
            else:
                logger.error(f"Document upload failed: {response.status_code} - {response.text}")
                return False
    
    def wait_for_processing(self, max_attempts=10):
        """Wait for the document to be processed"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        logger.info(f"Waiting for document {self.document_id} to be processed")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/api/documents/{self.document_id}")
                
                if response.status_code == 200:
                    status = response.json().get('status', '')
                    if status == 'processed':
                        logger.info("Document processing complete")
                        return True
                        
                logger.info(f"Document still processing (attempt {attempt+1}/{max_attempts})...")
                time.sleep(2)  # Wait 2 seconds between checks
                
            except Exception as e:
                logger.error(f"Error checking document status: {e}")
                
        logger.warning(f"Document processing took too long, continuing anyway")
        return True
    
    def ask_questions(self, questions=None):
        """Ask questions about the document"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        if questions is None:
            # Default questions to ask
            questions = [
                "What is the total portfolio value?",
                "What stocks are in the portfolio?",
                "What is the allocation of stocks, bonds, and cash?",
                "What is the valuation date?",
                "How many shares of Microsoft are in the portfolio?",
                "What is the ISIN for Tesla?",
                "What is the YTD return percentage?",
                "What is the most valuable holding in the portfolio?",
                "What is the price of Apple stock?",
                "Summarize this portfolio statement in a few sentences."
            ]
        
        logger.info("\n===== Testing Document Q&A =====")
        
        for question in questions:
            logger.info(f"\nQ: {question}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/qa/ask",
                    json={
                        'document_id': self.document_id,
                        'question': question
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', 'No answer provided')
                    logger.info(f"A: {answer}")
                else:
                    logger.error(f"Question failed: {response.status_code} - {response.text}")
                
            except Exception as e:
                logger.error(f"Error asking question: {e}")
                
        logger.info("\nDocument Q&A testing complete!")
        return True
    
    def run_full_test(self):
        """Run the full document QA test"""
        success = self.upload_document()
        if not success:
            return False
            
        success = self.wait_for_processing()
        if not success:
            return False
            
        return self.ask_questions()

def main():
    """Main function"""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test document Q&A with a real PDF')
    parser.add_argument('--url', default='http://localhost:5003', help='Base URL of the API')
    parser.add_argument('--pdf', default=None, help='Path to a specific PDF file to test with')
    args = parser.parse_args()
    
    tester = DocumentQATester(args.url)
    
    if args.pdf:
        if os.path.exists(args.pdf):
            tester.pdf_path = args.pdf
        else:
            logger.error(f"Specified PDF file not found: {args.pdf}")
            return 1
    
    tester.run_full_test()
    return 0

if __name__ == "__main__":
    sys.exit(main())
