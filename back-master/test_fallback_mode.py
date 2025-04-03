#!/usr/bin/env python3
"""
Test the fallback mode for document Q&A without using external AI APIs.
"""
import os
import sys
import json
import logging

# Add project root to path
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FallbackTest")

def create_test_document():
    """Create a test document for testing fallback mode"""
    extraction_dir = os.path.join(project_dir, 'extractions')
    os.makedirs(extraction_dir, exist_ok=True)
    
    test_doc_id = "doc_fallback_test"
    test_doc_path = os.path.join(extraction_dir, f"{test_doc_id}_extraction.json")
    
    test_doc_content = """
PORTFOLIO STATEMENT

Client: John Smith
Account Number: 12345678
Statement Date: March 31, 2025
Valuation Date: March 30, 2025

Total Portfolio Value: $1,567,432.18

ASSET ALLOCATION:
Stocks: 65%
Bonds: 25% 
Cash: 10%

HOLDINGS:
1. Apple Inc. (ISIN US0378331005)
   Quantity: 500
   Price per share: $175.25
   Value: $87,625.00

2. Microsoft Corp. (ISIN US5949181045)
   Quantity: 320
   Price per share: $380.50
   Value: $121,760.00

3. Amazon.com Inc. (ISIN US0231351067)
   Quantity: 150
   Price per share: $178.35
   Value: $26,752.50

4. Tesla Inc. (ISIN US88160R1014)
   Quantity: 200
   Price per share: $173.80
   Value: $34,760.00

5. U.S. Treasury Bond 3.5% 2035 (ISIN US912810SP45)
   Face Value: $200,000
   Price: 96.75
   Value: $193,500.00

Currency Allocation:
USD: 85%
EUR: 10%
GBP: 5%
"""
    
    # Create document if it doesn't exist
    if not os.path.exists(test_doc_path):
        logger.info(f"Creating test document: {test_doc_path}")
        test_doc = {
            "document_id": test_doc_id,
            "filename": "portfolio_statement.pdf",
            "page_count": 3,
            "content": test_doc_content
        }
        
        with open(test_doc_path, 'w') as f:
            json.dump(test_doc, f, indent=2)
        
        logger.info("Test document created successfully")
    else:
        logger.info("Test document already exists")
    
    return test_doc_id

def test_fallback_mode():
    """Test the fallback mode for document Q&A"""
    # Create test document
    test_doc_id = create_test_document()
    
    # Import the AI service
    try:
        from project_organized.shared.ai.service import AIService
        ai_service = AIService()
        
        # Show AI service info
        logger.info(f"Default model: {ai_service.default_model}")
        logger.info(f"Using fallback mode: {ai_service.default_model == 'fallback'}")
        
        # Test questions
        test_questions = [
            "What is the portfolio value?",
            "What is the valuation date?",
            "How much is invested in Apple?",
            "What is the asset allocation?",
            "How many shares of Tesla are in the portfolio?",
            "What is the ISIN for Amazon?",
            "What is the currency allocation?"
        ]
        
        # Get document content
        extraction_dir = os.path.join(project_dir, 'extractions')
        doc_path = os.path.join(extraction_dir, f"{test_doc_id}_extraction.json")
        with open(doc_path, 'r') as f:
            doc_data = json.load(f)
            context = doc_data.get('content', '')
        
        # Test each question
        for question in test_questions:
            logger.info(f"\nQuestion: {question}")
            answer = ai_service.generate_response(question, context, model="fallback")
            logger.info(f"Answer: {answer}")
        
    except ImportError as e:
        logger.error(f"Error importing AI service: {e}")

if __name__ == "__main__":
    logger.info("===== Testing Fallback Mode =====")
    test_fallback_mode()
