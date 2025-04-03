import os
import sys
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SystemTest")

class SystemTester:
    """Test the entire financial document processing system"""
    
    def __init__(self, test_pdf_path=None):
        """Initialize the system tester
        
        Args:
            test_pdf_path: Path to a test PDF file
        """
        self.test_pdf_path = test_pdf_path
        
        # Set up directories
        self.dirs = {
            'uploads': 'uploads',
            'extractions': 'extractions',
            'financial_data': 'financial_data',
            'excel_exports': 'excel_exports'
        }
        
        # Create directories if they don't exist
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Track test document ID
        self.document_id = None
    
    def run_full_test(self):
        """Run a complete system test from PDF processing to Excel export"""
        logger.info("Starting full system test")
        
        # Step 1: Test PDF processor
        logger.info("=" * 40)
        logger.info("Step 1: Testing Enhanced PDF Processor")
        pdf_success = self.test_pdf_processor()
        if not pdf_success:
            logger.error("PDF processing test failed. Stopping test.")
            return False
        
        # Step 2: Test financial data extraction
        logger.info("=" * 40)
        logger.info("Step 2: Testing Advanced Financial Extractor")
        extraction_success = self.test_financial_extraction()
        if not extraction_success:
            logger.error("Financial extraction test failed. Stopping test.")
            return False
        
        # Step 3: Test question answering
        logger.info("=" * 40)
        logger.info("Step 3: Testing Document Q&A System")
        qa_success = self.test_qa_system()
        if not qa_success:
            logger.error("Q&A system test failed. Stopping test.")
            return False
        
        # Step 4: Test Excel export
        logger.info("=" * 40)
        logger.info("Step 4: Testing Excel Export")
        export_success = self.test_excel_export()
        if not export_success:
            logger.error("Excel export test failed. Stopping test.")
            return False
        
        logger.info("=" * 40)
        logger.info("All system tests completed successfully!")
        return True
    
    def test_pdf_processor(self):
        """Test the enhanced PDF processor"""
        try:
            from enhanced_pdf_processor import EnhancedPDFProcessor
            
            logger.info("Enhanced PDF processor module imported successfully")
            
            # Check for test file
            if not self.test_pdf_path or not os.path.exists(self.test_pdf_path):
                available_pdfs = []
                # Look for PDFs in uploads directory
                for filename in os.listdir(self.dirs['uploads']):
                    if filename.endswith('.pdf'):
                        available_pdfs.append(os.path.join(self.dirs['uploads'], filename))
                
                if not available_pdfs:
                    logger.error("No test PDF file available")
                    return False
                
                self.test_pdf_path = available_pdfs[0]
                logger.info(f"Using existing PDF for testing: {self.test_pdf_path}")
            
            # Create processor
            processor = EnhancedPDFProcessor()
            
            # Process the PDF
            logger.info(f"Processing PDF: {self.test_pdf_path}")
            result = processor.process_document(self.test_pdf_path, self.dirs['extractions'])
            
            # Check result
            if not result:
                logger.error("PDF processing failed: No result returned")
                return False
            
            self.document_id = result.get('document_id')
            logger.info(f"PDF processed successfully. Document ID: {self.document_id}")
            logger.info(f"Page count: {result.get('page_count')}")
            logger.info(f"Extracted {len(result.get('content', ''))} characters of text")
            
            # Check if extraction file was created
            extraction_path = os.path.join(self.dirs['extractions'], f"{self.document_id}_extraction.json")
            if not os.path.exists(extraction_path):
                logger.error(f"Extraction file not created: {extraction_path}")
                return False
            
            logger.info(f"Extraction file created: {extraction_path}")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import enhanced PDF processor: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in PDF processor test: {e}")
            return False
    
    def test_financial_extraction(self):
        """Test the advanced financial extractor"""
        try:
            from advanced_financial_extractor import AdvancedFinancialExtractor
            
            logger.info("Advanced financial extractor module imported successfully")
            
            # Check if we have a document ID
            if not self.document_id:
                logger.error("No document ID available for financial extraction test")
                return False
            
            # Create extractor
            extractor = AdvancedFinancialExtractor()
            
            # Extract financial data
            logger.info(f"Extracting financial data for document: {self.document_id}")
            result = extractor.extract_from_document(
                self.document_id, 
                self.dirs['extractions'], 
                self.dirs['financial_data']
            )
            
            # Check result
            if not result:
                logger.error("Financial extraction failed: No result returned")
                return False
            
            logger.info(f"Financial data extracted successfully")
            logger.info(f"Found {len(result.get('isins', []))} ISINs")
            logger.info(f"Extracted data for {len(result.get('securities', []))} securities")
            logger.info(f"Detected {len(result.get('tables', []))} tables")
            
            # Check if financial data file was created
            financial_path = os.path.join(self.dirs['financial_data'], f"{self.document_id}_financial.json")
            if not os.path.exists(financial_path):
                logger.error(f"Financial data file not created: {financial_path}")
                return False
            
            logger.info(f"Financial data file created: {financial_path}")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import advanced financial extractor: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in financial extraction test: {e}")
            return False
    
    def test_qa_system(self):
        """Test the document Q&A system"""
        try:
            from financial_document_qa import FinancialDocumentQA
            
            logger.info("Financial document Q&A module imported successfully")
            
            # Check if we have a document ID
            if not self.document_id:
                logger.error("No document ID available for Q&A test")
                return False
            
            # Create Q&A system
            qa_system = FinancialDocumentQA()
            
            # Test questions
            test_questions = [
                "How many ISINs are in this document?",
                "What is the total portfolio value?",
                "What securities are mentioned in the document?"
            ]
            
            # Ask questions
            for question in test_questions:
                logger.info(f"Q: {question}")
                answer = qa_system.answer_question(
                    question, 
                    self.document_id, 
                    self.dirs['extractions'], 
                    self.dirs['financial_data']
                )
                logger.info(f"A: {answer}")
            
            logger.info("Q&A system test completed successfully")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import financial document Q&A: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in Q&A system test: {e}")
            return False
    
    def test_excel_export(self):
        """Test the Excel export functionality"""
        try:
            from excel_exporter import FinancialDataExporter
            
            logger.info("Excel exporter module imported successfully")
            
            # Check if we have a document ID
            if not self.document_id:
                logger.error("No document ID available for Excel export test")
                return False
            
            # Create exporter
            exporter = FinancialDataExporter(self.dirs['excel_exports'])
            
            # Export all document data
            logger.info(f"Exporting all data for document: {self.document_id}")
            excel_path = exporter.export_document_data(
                self.document_id, 
                self.dirs['financial_data'], 
                self.dirs['extractions']
            )
            
            # Check result
            if not excel_path or not os.path.exists(excel_path):
                logger.error("Excel export failed: No file created")
                return False
            
            logger.info(f"Excel file created: {excel_path}")
            
            # Export custom table
            logger.info(f"Exporting custom table for document: {self.document_id}")
            columns = ['isin', 'name', 'quantity', 'price', 'value']
            custom_path = exporter.export_custom_table(
                self.document_id, 
                columns, 
                self.dirs['financial_data']
            )
            
            # Check result
            if not custom_path or not os.path.exists(custom_path):
                logger.error("Custom table export failed: No file created")
                return False
            
            logger.info(f"Custom table exported: {custom_path}")
            return True
            
        except ImportError as e:
            logger.error(f"Failed to import Excel exporter: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in Excel export test: {e}")
            return False

if __name__ == "__main__":
    # Get test PDF path from command line arguments
    test_pdf_path = None
    if len(sys.argv) > 1:
        test_pdf_path = sys.argv[1]
    
    # Run the test
    tester = SystemTester(test_pdf_path)
    success = tester.run_full_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
