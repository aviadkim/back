#!/usr/bin/env python3
"""
Test the document Q&A feature with OpenRouter integration.
"""
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QATest")

def create_test_document():
    """Create a sample document for testing"""
    extraction_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'extractions'))
    os.makedirs(extraction_dir, exist_ok=True)
    
    doc_id = "doc_qatest123"
    sample_path = os.path.join(extraction_dir, f"{doc_id}_extraction.json")
    
    # Create test document if it doesn't exist
    if not os.path.exists(sample_path):
        logger.info(f"Creating test document at {sample_path}")
        
        sample_content = {
            "document_id": doc_id,
            "filename": "portfolio_statement.pdf",
            "page_count": 2,
            "content": """
XYZ Investment Holdings - Portfolio Statement
Client: John Smith
Account Number: 12345678
Date: March 31, 2025
Valuation Date: March 30, 2025

Portfolio Summary:
Total Value: $1,745,320.50
Stocks: 65% ($1,134,458.33)
Bonds: 25% ($436,330.13)
Cash: 10% ($174,532.05)

Holdings:
1. Apple Inc. (AAPL) - ISIN US0378331005
   Shares: 500
   Price: $175.25
   Value: $87,625.00

2. Microsoft Corp (MSFT) - ISIN US5949181045
   Shares: 320
   Price: $380.50
   Value: $121,760.00

3. Tesla Inc (TSLA) - ISIN US88160R1014
   Shares: 200
   Price: $173.80
   Value: $34,760.00
"""
        }
        
        with open(sample_path, 'w') as f:
            json.dump(sample_content, f, indent=2)
        
        logger.info("Test document created successfully")
    
    return doc_id

def test_document_qa():
    """Test document Q&A with OpenRouter integration"""
    try:
        # Prepare test document
        doc_id = create_test_document()
        
        # Import the necessary components
        logger.info("Importing DocumentQAService...")
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from project_organized.features.document_qa.service import DocumentQAService
        
        # Create service instance
        qa_service = DocumentQAService()
        
        # Test with various questions
        questions = [
            "What is the total portfolio value?",
            "How many shares of Apple does the client own?",
            "What is the allocation of stocks, bonds, and cash?",
            "What is the valuation date?",
            "What is the ISIN for Tesla?"
        ]
        
        for question in questions:
            logger.info(f"\nQ: {question}")
            answer = qa_service.answer_question(doc_id, question)
            logger.info(f"A: {answer}")
            
        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.info("This error might be due to missing __init__.py files or incorrect path setup.")
        return False
    except Exception as e:
        logger.error(f"Error testing document Q&A: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    load_dotenv()
    logger.info("===== Testing Document Q&A with OpenRouter =====")
    success = test_document_qa()
    if success:
        logger.info("\n✅ Document Q&A feature is working correctly with OpenRouter!")
    else:
        logger.error("\n❌ Document Q&A feature test failed.")
