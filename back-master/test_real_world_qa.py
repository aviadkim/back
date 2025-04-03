#!/usr/bin/env python3
"""
Real-world test for the document Q&A system
This script performs a comprehensive test of the document Q&A feature by:
1. Uploading a real-world PDF document
2. Asking questions using different models
3. Benchmarking the quality of responses
"""
import os
import sys
import requests
import json
import logging
import time
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RealWorldQATest")

class DocumentQATest:
    """Test the document Q&A system with real-world documents"""
    
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.document_id = None
        self.document_info = None
        self.results = {}
        
        # Load API key configuration
        load_dotenv()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Create results directory
        self.results_dir = os.path.join(os.getcwd(), "qa_results")
        os.makedirs(self.results_dir, exist_ok=True)
    
    def upload_document(self, pdf_path):
        """Upload a document for testing"""
        logger.info(f"Uploading document: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return False
        
        try:
            with open(pdf_path, 'rb') as file:
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
                    
                    # Wait for processing
                    self._wait_for_processing()
                    
                    # Get document info
                    self._get_document_info()
                    
                    return True
                else:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return False
    
    def _wait_for_processing(self, max_attempts=30):
        """Wait for document processing to complete"""
        if not self.document_id:
            return False
            
        logger.info(f"Waiting for document processing to complete...")
        for i in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/api/documents/{self.document_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status')
                    
                    if status == 'processed':
                        logger.info("Document processing complete")
                        return True
                    
                    logger.info(f"Processing status: {status} (attempt {i+1}/{max_attempts})")
                else:
                    logger.error(f"Error checking status: {response.status_code}")
            
            except Exception as e:
                logger.error(f"Error during processing check: {e}")
                
            time.sleep(2)  # Wait before checking again
            
        logger.warning("Document processing took too long, continuing anyway")
        return False
    
    def _get_document_info(self):
        """Get information about the uploaded document"""
        if not self.document_id:
            return None
            
        try:
            response = self.session.get(f"{self.base_url}/api/documents/{self.document_id}")
            
            if response.status_code == 200:
                self.document_info = response.json()
                logger.info(f"Got document info: {self.document_info.get('filename')}")
                return self.document_info
            else:
                logger.error(f"Failed to get document info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting document info: {e}")
            return None
    
    def test_with_questions(self, questions=None, model="openrouter"):
        """Test document Q&A with specific questions"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        if not questions:
            # Default general questions
            questions = [
                "What type of document is this?",
                "Summarize this document in a few sentences.",
                "What is the total portfolio value?",
                "What companies are mentioned in this document?",
                "What is the asset allocation?",
                "When was this document created or dated?",
                "Are there any ISINs mentioned in the document?",
                "What currencies are mentioned in this document?",
            ]
        
        logger.info(f"\n===== Testing Q&A with model: {model} =====")
        
        results = []
        for question in questions:
            logger.info(f"Q: {question}")
            
            try:
                # Force model via URL parameter to override .env setting
                response = self.session.post(
                    f"{self.base_url}/api/qa/ask?model={model}",
                    json={
                        "document_id": self.document_id,
                        "question": question
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided")
                    logger.info(f"A: {answer}")
                    
                    results.append({
                        "question": question,
                        "answer": answer,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"Question failed: {response.status_code} - {response.text}")
                    results.append({
                        "question": question,
                        "answer": f"Error: {response.status_code}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except Exception as e:
                logger.error(f"Error asking question: {e}")
                results.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Save results
        self.results[model] = results
        return results
    
    def save_results(self):
        """Save test results to a file"""
        if not self.results:
            logger.warning("No results to save")
            return False
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_test_results_{timestamp}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        result_data = {
            "document_id": self.document_id,
            "document_info": self.document_info,
            "test_date": datetime.now().isoformat(),
            "model_results": self.results
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(result_data, f, indent=2)
                
            logger.info(f"Results saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def run_comprehensive_test(self, pdf_path):
        """Run a comprehensive test with all available models"""
        if not self.upload_document(pdf_path):
            return False
        
        # First test with fallback mode
        self.test_with_questions(model="fallback")
        
        # Test with OpenRouter if available
        if self.openrouter_api_key and self.openrouter_api_key.startswith('sk-or-'):
            self.test_with_questions(model="openrouter")
        else:
            logger.warning("Skipping OpenRouter test - no valid API key")
        
        # Test with Gemini if available
        if self.gemini_api_key and not self.gemini_api_key.startswith('YOUR_GEMINI_API_KEY'):
            self.test_with_questions(model="gemini")
        else:
            logger.warning("Skipping Gemini test - no valid API key")
        
        # Test with HuggingFace if available
        if self.huggingface_api_key and not self.huggingface_api_key.startswith('YOUR_HUGGINGFACE_API_KEY'):
            self.test_with_questions(model="huggingface")
        else:
            logger.warning("Skipping HuggingFace test - no valid API key")
        
        # Save all results
        self.save_results()
        
        return True

def find_pdf_files():
    """Find all available PDF files for testing"""
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
    
    return pdf_files

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test document Q&A with real PDFs")
    parser.add_argument("--url", default="http://localhost:5003", help="Base URL of the API")
    parser.add_argument("--pdf", help="Path to a specific PDF file to test")
    parser.add_argument("--model", choices=["fallback", "openrouter", "gemini", "huggingface"],
                      help="Use a specific model for testing")
    args = parser.parse_args()
    
    tester = DocumentQATest(args.url)
    
    if args.pdf:
        # Test with specific PDF
        if os.path.exists(args.pdf):
            if args.model:
                # Test with specific model
                tester.upload_document(args.pdf)
                tester.test_with_questions(model=args.model)
                tester.save_results()
            else:
                # Test with all available models
                tester.run_comprehensive_test(args.pdf)
        else:
            logger.error(f"PDF file not found: {args.pdf}")
            return 1
    else:
        # Find PDF files and test with first one
        pdf_files = find_pdf_files()
        if pdf_files:
            logger.info(f"Found {len(pdf_files)} PDF files")
            tester.run_comprehensive_test(pdf_files[0])
        else:
            logger.error("No PDF files found for testing")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
