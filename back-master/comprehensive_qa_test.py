#!/usr/bin/env python3
"""
Comprehensive test for document Q&A using a real PDF from the project.
This script will find an existing PDF, upload it (or use an existing upload),
and ask 20 detailed questions to thoroughly test the AI integration.
"""
import os
import sys
import requests
import json
import logging
import time
import signal
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ComprehensiveQATest")

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

class ComprehensiveQATester:
    """Test the document Q&A system with real PDFs from the project"""
    
    def __init__(self, base_url="http://localhost:5003"):
        self.base_url = base_url
        self.session = requests.Session()
        self.document_id = None
        self.pdf_path = None
        self.document_content = None
        self.results = []
        
        # Create results directory
        self.results_dir = os.path.join(os.getcwd(), "qa_test_results")
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Set up result saving paths
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.results_file = os.path.join(self.results_dir, f"comprehensive_qa_test_{timestamp}.json")
        self.results_text_file = os.path.join(self.results_dir, f"comprehensive_qa_test_{timestamp}.txt")
    
    def find_real_pdf(self):
        """Find a real PDF file in the project"""
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
                pdf_files.append((full_path, 0))
                
                priority = sum(2 for keyword in financial_keywords if keyword.lower() in file.lower())
                if priority > 0:
                    pdf_files[-1] = (full_path, priority)
        
        pdf_files.sort(key=lambda x: x[1], reverse=True)
        
        if pdf_files:
            self.pdf_path = pdf_files[0][0]
            logger.info(f"Found PDF file: {self.pdf_path}")
            return self.pdf_path
        else:
            logger.warning("No PDF files found in the project")
            return None
    
    def check_existing_documents(self):
        """Check for existing processed documents"""
        try:
            response = self.session.get(f"{self.base_url}/api/documents")
            
            if response.status_code == 200:
                documents = response.json().get('documents', [])
                
                if documents:
                    self.document_id = documents[0].get('document_id')
                    logger.info(f"Using existing document: {self.document_id}")
                    return self.document_id
            
            return None
        except Exception as e:
            logger.error(f"Error checking existing documents: {e}")
            return None
    
    def upload_document(self):
        """Upload the PDF file if not using an existing one"""
        if self.check_existing_documents():
            return True
            
        if not self.pdf_path:
            if not self.find_real_pdf():
                logger.error("No PDF file available for upload")
                return False
            
        logger.info(f"Uploading document: {self.pdf_path}")
        
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
                    logger.info(f"Document uploaded successfully: {self.document_id}")
                    return True
                else:
                    logger.error(f"Document upload failed: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return False
    
    def wait_for_processing(self, max_attempts=30):
        """Wait for the document to be processed"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
            
        logger.info(f"Waiting for document {self.document_id} to be processed")
        
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/api/documents/{self.document_id}")
                
                if response.status_code == 200:
                    doc_info = response.json()
                    status = doc_info.get('status', '')
                    
                    if status == 'processed':
                        logger.info("Document processing complete")
                        
                        try:
                            extractions_dir = os.path.join('/workspaces/back/extractions')
                            extraction_file = os.path.join(extractions_dir, f"{self.document_id}_extraction.json")
                            
                            if os.path.exists(extraction_file):
                                with open(extraction_file, 'r') as f:
                                    extraction_data = json.load(f)
                                    self.document_content = extraction_data.get('content', '')
                                    logger.info(f"Cached document content: {len(self.document_content)} characters")
                        except Exception as e:
                            logger.warning(f"Couldn't cache document content: {e}")
                            
                        return True
                    
                    logger.info(f"Document status: {status} (attempt {attempt+1}/{max_attempts})")
                else:
                    logger.error(f"Error checking document status: {response.status_code}")
                    
                time.sleep(2)
            except Exception as e:
                logger.error(f"Error checking document status: {e}")
                time.sleep(2)
                
        logger.warning("Document processing took too long")
        return True
    
    def generate_questions_based_on_content(self, num_questions=5):
        """Generate questions based on document content"""
        if not self.document_content:
            logger.warning("No document content available for question generation")
            return []
            
        templates = [
            "What is {entity}?",
            "How much is {entity} worth?",
            "When was {entity} reported?",
            "What is the allocation of {entity}?",
            "How many {entity} are there?",
            "What percentage is {entity}?",
            "What is the ISIN for {entity}?",
            "What is the relationship between {entity} and {entity2}?",
            "Compare {entity} and {entity2}.",
            "Summarize the information about {entity}."
        ]
        
        content = self.document_content.lower()
        
        potential_entities = []
        lines = content.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ":" in line:
                key = line.split(":")[0].strip()
                if len(key) > 3 and not key.isdigit():
                    potential_entities.append(key)
            
            if "inc" in line or "corp" in line or "ltd" in line or "fund" in line or "portfolio" in line:
                words = line.split()
                for i, word in enumerate(words):
                    if word in ["inc", "corp", "ltd", "llc"]:
                        company = " ".join(words[max(0, i-3):i+1])
                        potential_entities.append(company)
            
            if any(m in line for m in ["january", "february", "march", "april", "may", "june", "july",
                                      "august", "september", "october", "november", "december"]):
                potential_entities.append("date")
                
            if "$" in line or "%" in line or any(c in line for c in "0123456789"):
                if "total" in line or "value" in line or "worth" in line or "sum" in line:
                    potential_entities.append("total value")
                elif "allocation" in line:
                    potential_entities.append("allocation")
                
        general_entities = ["portfolio", "statement", "report", "total value", "allocation", 
                           "shares", "securities", "bonds", "stocks", "cash"]
        
        all_entities = list(set(potential_entities + general_entities))
        
        questions = []
        pairs = [(e1, e2) for i, e1 in enumerate(all_entities) 
                          for e2 in all_entities[i+1:]]
        
        for entity in all_entities[:10]:
            for template in templates[:6]:
                if "{entity}" in template and "{entity2}" not in template:
                    questions.append(template.format(entity=entity))
                    if len(questions) >= num_questions * 2:
                        break
        
        for entity, entity2 in pairs[:5]:
            for template in templates[6:]:
                if "{entity}" in template and "{entity2}" in template:
                    questions.append(template.format(entity=entity, entity2=entity2))
                    if len(questions) >= num_questions * 3:
                        break
        
        key_questions = [
            "What is the total portfolio value?",
            "What is the asset allocation?",
            "When was this statement dated?",
            "What companies are included in this portfolio?",
            "What is the largest holding in the portfolio?",
            "What is the percentage of cash in the portfolio?",
            "Summarize this financial document in one paragraph.",
            "Are there any bonds in this portfolio?",
            "What currencies are used in this document?",
            "Are there any foreign securities in this portfolio?"
        ]
        
        all_questions = list(set(questions + key_questions))
        return all_questions[:num_questions]
    
    def ask_questions(self, questions=None):
        """Ask questions about the document"""
        if not self.document_id:
            logger.error("No document ID available")
            return False
        
        if not questions:
            questions = [
                "What is the total portfolio value?",
                "What is the asset allocation in this portfolio?",
                "When was this document created or dated?",
                "What companies or securities are mentioned in this document?",
                "What is the largest holding in the portfolio?",
            ]
            
            if self.document_content:
                generated_questions = self.generate_questions_based_on_content(5)
                all_questions = questions + [q for q in generated_questions if q not in questions]
                questions = all_questions[:20]
            
        logger.info("\n===== Testing Document Q&A with Comprehensive Questions =====")
        
        with open(self.results_text_file, 'w') as f:
            f.write(f"Comprehensive Q&A Test Results\n")
            f.write(f"Document ID: {self.document_id}\n")
            f.write(f"Document Path: {self.pdf_path or 'N/A'}\n")
            f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {os.getenv('DEFAULT_MODEL', 'unknown')}\n")
            f.write(f"----------------------------------------\n\n")
        
        for i, question in enumerate(questions, 1):
            if received_interrupt:
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
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', 'No answer provided')
                    logger.info(f"A: {answer}")
                    
                    self.results.append({
                        "question_number": i,
                        "question": question,
                        "answer": answer,
                        "success": True,
                        "time": time.strftime("%H:%M:%S")
                    })
                    
                    with open(self.results_text_file, 'a') as f:
                        f.write(f"Q{i}: {question}\n")
                        f.write(f"A: {answer}\n\n")
                else:
                    error_text = f"Question failed: {response.status_code} - {response.text}"
                    logger.error(error_text)
                    
                    self.results.append({
                        "question_number": i,
                        "question": question,
                        "answer": f"Error: {response.status_code}",
                        "success": False,
                        "time": time.strftime("%H:%M:%S")
                    })
                    
                    with open(self.results_text_file, 'a') as f:
                        f.write(f"Q{i}: {question}\n")
                        f.write(f"A: Error - {response.status_code}\n\n")
            except Exception as e:
                logger.error(f"Error asking question: {e}")
                
                self.results.append({
                    "question_number": i,
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "success": False,
                    "time": time.strftime("%H:%M:%S")
                })
                
                with open(self.results_text_file, 'a') as f:
                    f.write(f"Q{i}: {question}\n")
                    f.write(f"A: Error - {str(e)}\n\n")
        
        self.save_results()
            
        logger.info(f"\nResults saved to: {self.results_text_file}")
        logger.info(f"Detailed JSON results: {self.results_file}")
        return True
    
    def save_results(self):
        """Save test results to a file"""
        if not self.results:
            logger.warning("No results to save")
            return False
        
        document_info = {
            "document_id": self.document_id,
            "document_path": self.pdf_path,
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model": os.getenv("DEFAULT_MODEL", "unknown")
        }
        
        result_data = {
            "document_info": document_info,
            "results": self.results,
            "summary": {
                "total_questions": len(self.results),
                "successful_responses": sum(1 for r in self.results if r.get("success", False))
            }
        }
        
        try:
            with open(self.results_file, 'w') as f:
                json.dump(result_data, f, indent=2)
                
            logger.info(f"Results saved to {self.results_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def run_comprehensive_test(self, custom_questions=None):
        """Run the comprehensive document QA test"""
        try:
            health_response = self.session.get(f"{self.base_url}/health", timeout=2)
            if health_response.status_code != 200:
                logger.error(f"Application is not running or not healthy. Please start the application.")
                return False
        except:
            logger.error(f"Could not connect to application at {self.base_url}. Please start the application.")
            return False
        
        success = self.upload_document()
        if not success:
            return False
            
        success = self.wait_for_processing()
        if not success:
            return False
            
        return self.ask_questions(custom_questions)

def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Run comprehensive document Q&A test')
    parser.add_argument('--url', default='http://localhost:5003', help='Base URL of the API')
    parser.add_argument('--pdf', default=None, help='Path to a specific PDF file to test')
    args = parser.parse_args()
    
    tester = ComprehensiveQATester(args.url)
    
    if args.pdf:
        if os.path.exists(args.pdf):
            tester.pdf_path = args.pdf
        else:
            logger.error(f"Specified PDF file not found: {args.pdf}")
            return 1
    
    tester.run_comprehensive_test()
    return 0

if __name__ == "__main__":
    load_dotenv()
    sys.exit(main())
