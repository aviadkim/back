"""
Run all tests for the chatbot feature

This script runs all the tests for the chatbot feature in sequence 
and provides a summary of results. It includes:

1. Hugging Face API connection test
2. Chatbot capabilities test
3. Chatbot API tests

Run this script with:
    python -m features.chatbot.tests.run_all_tests
"""

import os
import sys
import unittest
import pytest
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/chatbot_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_all_tests():
    """Run all chatbot tests and log results"""
    
    logger.info("=" * 70)
    logger.info("RUNNING ALL CHATBOT TESTS")
    logger.info("=" * 70)
    
    # Keep track of test results
    results = {
        "huggingface_connection": False,
        "chatbot_capabilities": False,
        "chatbot_api": False
    }
    
    # 1. Run Hugging Face API connection test
    logger.info("\n\n" + "=" * 50)
    logger.info("TESTING HUGGING FACE API CONNECTION")
    logger.info("=" * 50)
    
    try:
        from features.chatbot.tests.test_huggingface_connection import test_huggingface_connection
        results["huggingface_connection"] = test_huggingface_connection()
    except Exception as e:
        logger.error(f"Error running Hugging Face connection test: {str(e)}")
    
    # 2. Run Chatbot capabilities test
    logger.info("\n\n" + "=" * 50)
    logger.info("TESTING CHATBOT CAPABILITIES")
    logger.info("=" * 50)
    
    try:
        from features.chatbot.tests.test_chatbot_capabilities import test_chatbot_capabilities
        results["chatbot_capabilities"] = test_chatbot_capabilities()
    except Exception as e:
        logger.error(f"Error running chatbot capabilities test: {str(e)}")
    
    # 3. Run Chatbot API tests
    logger.info("\n\n" + "=" * 50)
    logger.info("TESTING CHATBOT API")
    logger.info("=" * 50)
    
    try:
        # Use pytest to run the API tests
        exit_code = pytest.main(['-v', 'features/chatbot/tests/test_chatbot_api.py'])
        results["chatbot_api"] = exit_code == 0
    except Exception as e:
        logger.error(f"Error running chatbot API tests: {str(e)}")
    
    # Print summary of results
    logger.info("\n\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    overall_result = all(results.values())
    logger.info(f"\nOverall result: {'✅ ALL TESTS PASSED' if overall_result else '❌ SOME TESTS FAILED'}")
    
    return overall_result

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
