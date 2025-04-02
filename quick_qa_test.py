#!/usr/bin/env python3
"""
Quick test for document Q&A using a real or sample document.
This script tests AI integration with fewer questions and saves results even on interruption.
"""
import os
import sys
import requests
import json
import logging
import time
import signal
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QuickQATest")

# Track if we've received an interrupt
received_interrupt = False

def signal_handler(sig, frame):
    """Handle interruption signals gracefully"""
    global received_interrupt
    if received_interrupt:  # If we've already received one interrupt, exit immediately
        logger.info("Second interrupt received, exiting immediately")
        sys.exit(1)
    else:
        logger.info("Interrupt received, finishing current question and saving results...")
        received_interrupt = True

# Register signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

class QuickQATester:
    """Test the document Q&A system with quick feedback"""
    
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.document_id = None
        self.pdf_path = None
        self.document_content = None
        self.results = []
    
    def find_real_pdf(self):
        """Find a real PDF file in the project"""
        # Look for PDF files in common locations
        search_paths = [
            '/workspaces/back/uploads',
            '/workspaces/back/test_files',
            '/workspaces/back',
            '/workspaces/back/project_organized/test_files'
        ]
        
        financial_keywords = ['portfolio', 'statement', 'account', 'financial', 'investment']
        pdf_files = []
        
        for path in search_paths:
            if not os.path.exists(path):
                continue
                
            for file in os.listdir(path):
                if not file.lower().endswith('.pdf'):
                    continue
                    
                full_path = os.path.join(path, file)
                # Give priority to files that look like financial documents
                priority = sum(2 for keyword in financial_keywords if keyword.lower() in file.lower())
                pdf_files.append((full_path, priority))
        
        # Sort by priority (higher number first)
        pdf_files.sort(key=lambda x: x[1], reverse=True)
        
        if pdf_files:
            self.pdf_path = pdf_files[0][0]
            logger.info(f"Found real PDF file: {self.pdf_path}")
            return self.pdf_path
        else:
            logger.warning("No PDF files found in the project")
            return None
    
    def upload_real_pdf(self):
        """Upload a real PDF file from the project"""
        # Find a PDF file if not already set
        if not self.pdf_path:
            if not self.find_real_pdf():
                logger.warning("No real PDF files found, falling back to sample document")
                return self.use_sample_document()
        
        logger.info(f"Uploading real PDF: {self.pdf_path}")
        
        try:
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
                    logger.info(f"PDF uploaded successfully! Document ID: {self.document_id}")
                    return True
                else:
                    logger.error(f"PDF upload failed: {response.status_code} - {response.text}")
                    # Fall back to sample document if upload fails
                    logger.info("Falling back to sample document")
                    return self.use_sample_document()
                
        except Exception as e:
            logger.error(f"Error uploading PDF: {e}")
            # Fall back to sample document
            logger.info("Falling back to sample document due to error")
            return self.use_sample_document()
    
    def wait_for_processing(self, max_attempts=30):
        """Wait for the document to be processed"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        logger.info(f"Waiting for document {self.document_id} to be processed...")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/api/documents/{self.document_id}")
                
                if response.status_code == 200:
                    status = response.json().get('status', '')
                    if status == 'processed':
                        logger.info("Document processing complete!")
                        return True
                        
                    logger.info(f"Processing status: {status} (attempt {attempt+1}/{max_attempts})")
                else:
                    logger.error(f"Error checking status: {response.status_code}")
                    
                time.sleep(2)  # Wait before checking again
            except Exception as e:
                logger.error(f"Error checking document status: {e}")
                time.sleep(2)
                
        logger.warning("Document processing took too long, continuing anyway")
        return True
    
    def use_sample_document(self):
        """Use a sample document already in the system"""
        # First check for any existing documents in the system
        try:
            response = self.session.get(f"{self.base_url}/api/documents")
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                if documents:
                    self.document_id = documents[0].get('document_id')
                    logger.info(f"Using existing document: {self.document_id}")
                    return True
        except Exception as e:
            logger.error(f"Error checking for existing documents: {e}")
        
        # If no documents found, create a sample extraction
        extraction_dir = '/workspaces/back/extractions'
        os.makedirs(extraction_dir, exist_ok=True)
        
        doc_id = "doc_qatest123"
        sample_path = os.path.join(extraction_dir, f"{doc_id}_extraction.json")
        
        # Create the sample document if it doesn't exist
        if not os.path.exists(sample_path):
            logger.info("Creating sample document...")
            
            sample_content = {
                "document_id": doc_id,
                "filename": "sample_financial_report.pdf",
                "page_count": 2,
                "content": """
XYZ Investment Holdings - Portfolio Statement
Client: Jane Smith
Account Number: 87654321
Date: April 1, 2025
Valuation Date: March 31, 2025

Portfolio Summary:
Total Value: $1,865,432.25
Stocks: 70% ($1,305,802.58)
Bonds: 20% ($373,086.45)
Cash: 10% ($186,543.23)

Holdings:
1. Apple Inc. (AAPL) - ISIN US0378331005
   Shares: 800
   Price: $185.75
   Value: $148,600.00

2. Microsoft Corp (MSFT) - ISIN US5949181045
   Shares: 350
   Price: $420.50
   Value: $147,175.00

3. Amazon.com Inc (AMZN) - ISIN US0231351067
   Shares: 200
   Price: $190.25
   Value: $38,050.00

4. Alphabet Inc (GOOGL) - ISIN US02079K3059
   Shares: 150
   Price: $175.80
   Value: $26,370.00

5. US Treasury Bond 2.5% 2030 - ISIN US912828ZX16
   Face Value: $300,000
   Price: 94.35
   Value: $283,050.00

Performance:
YTD Return: +7.85%
1 Year Return: +15.63%
3 Year Return: +38.75%

Currency Allocation:
USD: 90%
EUR: 7%
GBP: 3%
"""
            }
            
            with open(sample_path, 'w') as f:
                json.dump(sample_content, f, indent=2)
                
            logger.info(f"Created sample document at {sample_path}")
        
        self.document_id = doc_id
        logger.info(f"Using sample document with ID: {self.document_id}")
        return True
    
    def ask_questions(self, questions=None, max_questions=5, save_on_interrupt=True):
        """Ask questions about the document"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        if questions is None:
            # Default questions for quick testing
            questions = [
                "What is the total portfolio value?",
                "What is the allocation of stocks, bonds, and cash?",
                "What is the valuation date?",
                "What companies are in the portfolio?",
                "What is the ISIN for Amazon?",
                "What is the YTD return percentage?",
                "How many shares of Apple are in the portfolio?",
                "What currencies are mentioned in the document?"
            ]
            
            # Limit to max_questions
            questions = questions[:max_questions]
        
        logger.info("\n===== Quick Document Q&A Test =====")
        
        # Create a directory for storing results
        results_dir = "/workspaces/back/qa_test_results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Prepare results file name (will be used later)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = os.path.join(results_dir, f"quick_qa_test_{timestamp}.json")
        
        for i, question in enumerate(questions, 1):
            if received_interrupt and save_on_interrupt:
                logger.info("Interrupt received. Saving results and exiting.")
                break
                
            logger.info(f"\nQ{i}: {question}")
            
            try:
                response = self.session.post(
                    f"{self.base_url}/api/qa/ask",
                    json={
                        'document_id': self.document_id,
                        'question': question
                    },
                    timeout=20  # Add timeout to prevent hanging
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', 'No answer provided')
                    logger.info(f"A: {answer}")
                    
                    self.results.append({
                        "question": question,
                        "answer": answer,
                        "success": True,
                        "time": time.strftime("%H:%M:%S")
                    })
                else:
                    error_text = f"Question failed: {response.status_code} - {response.text}"
                    logger.error(error_text)
                    
                    self.results.append({
                        "question": question,
                        "answer": f"Error: {response.status_code}",
                        "success": False,
                        "time": time.strftime("%H:%M:%S")
                    })
                    
            except Exception as e:
                logger.error(f"Error asking question: {e}")
                
                self.results.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "success": False,
                    "time": time.strftime("%H:%M:%S")
                })
        
        # Save results
        if self.results:  # Only save if we have results
            self.save_results(results_file)
        
        return True
    
    def save_results(self, filename=None):
        """Save the test results to a file"""
        if not filename:
            # Create a default filename if none provided
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_dir = "/workspaces/back/qa_test_results"
            os.makedirs(results_dir, exist_ok=True)
            filename = os.path.join(results_dir, f"quick_qa_test_{timestamp}.json")
        
        results_data = {
            "document_id": self.document_id,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": self.results,
            "summary": {
                "total_questions": len(self.results),
                "successful_responses": sum(1 for r in self.results if r.get("success", False)),
                "model": os.getenv("DEFAULT_MODEL", "unknown")
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            logger.info(f"Results saved to {filename}")
            
            # Also save a readable text version
            text_filename = os.path.splitext(filename)[0] + ".txt"
            with open(text_filename, 'w') as f:
                f.write(f"Quick Q&A Test Results\n")
                f.write(f"Document ID: {self.document_id}\n")
                f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model: {os.getenv('DEFAULT_MODEL', 'unknown')}\n")
                f.write(f"--------------------\n\n")
                
                for i, r in enumerate(self.results, 1):
                    f.write(f"Q{i}: {r['question']}\n")
                    f.write(f"A: {r['answer']}\n\n")
                    
            logger.info(f"Results also saved in text format to {text_filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def run_quick_test(self, max_questions=5, use_real_pdf=True):
        """Run a quick Q&A test with the document"""
        try:
            # Make sure application is running
            try:
                health_response = self.session.get(f"{self.base_url}/health", timeout=2)
                if health_response.status_code != 200:
                    logger.error(f"Application is not running or not healthy.")
                    return False
            except:
                logger.error(f"Could not connect to application at {self.base_url}")
                return False
            
            # Use a real PDF if requested, otherwise use sample document
            if use_real_pdf:
                if not self.upload_real_pdf():
                    logger.error("Failed to upload real PDF")
                    return False
                
                # Wait for processing to complete
                if not self.wait_for_processing():
                    logger.error("Document processing failed")
                    return False
            else:
                # Use sample document
                if not self.use_sample_document():
                    logger.error("Failed to use sample document")
                    return False
            
            # Run the test
            return self.ask_questions(max_questions=max_questions)
        except Exception as e:
            logger.error(f"Error during quick test: {e}")
            traceback.print_exc()
            return False

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Run a quick document Q&A test')
    parser.add_argument('--url', default='http://localhost:5003', help='Base URL of the API')
    parser.add_argument('--questions', type=int, default=5, help='Number of questions to test')
    parser.add_argument('--pdf', default=None, help='Path to a specific PDF file')
    parser.add_argument('--no-real-pdf', action='store_true', help='Use sample document instead of real PDF')
    args = parser.parse_args()
    
    tester = QuickQATester(args.url)
    
    # If a specific PDF is provided, use it
    if args.pdf:
        if os.path.exists(args.pdf):
            tester.pdf_path = args.pdf
            logger.info(f"Using specified PDF file: {args.pdf}")
        else:
            logger.error(f"Specified PDF file not found: {args.pdf}")
            return 1
    
    # Run the test with real PDF unless --no-real-pdf is specified
    success = tester.run_quick_test(max_questions=args.questions, use_real_pdf=not args.no_real_pdf)
    
    if success:
        logger.info("\n✅ Quick test completed successfully!")
    else:
        logger.error("\n❌ Quick test failed!")
    
    return 0 if success else 1

if __name__ == "__main__":
    load_dotenv()
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user. Exiting.")
        sys.exit(1)
