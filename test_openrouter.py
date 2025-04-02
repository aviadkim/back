#!/usr/bin/env python3
"""
Test the OpenRouter API integration.
"""
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Add project root to path
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OpenRouterTest")

def test_openrouter_direct():
    """Test OpenRouter API directly using requests"""
    import requests
    
    # Load API key from .env
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    if not api_key or not api_key.startswith("sk-or-"):
        logger.error("No valid OpenRouter API key found. Please check your .env file")
        return False
    
    logger.info("Testing OpenRouter API directly")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://financial-document-processor.dev",
        "X-Title": "Financial Document Processor"
    }
    
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            logger.info(f"OpenRouter API works! Response: {content}")
            return True
        else:
            logger.error(f"Error from OpenRouter API: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error connecting to OpenRouter API: {e}")
        return False

def test_ai_service():
    """Test OpenRouter integration through the AI service"""
    try:
        from project_organized.shared.ai.service import AIService
        
        ai_service = AIService()
        
        # Check available APIs
        logger.info("Checking available AI services:")
        if ai_service.has_valid_openrouter_key:
            logger.info("✅ OpenRouter API key found")
            
            # Test OpenRouter model
            logger.info("Testing OpenRouter model...")
            test_prompt = "What is the capital of France in one sentence?"
            response = ai_service.generate_response(test_prompt, model="openrouter")
            logger.info(f"Response: {response}")
            
            # Test with context
            logger.info("Testing with financial context...")
            context = """This is a financial report for XYZ Corp.
            
The company has assets worth $1,500,000 as of December 31, 2024.
The portfolio includes holdings in Apple Inc. (ISIN US0378331005) worth $250,000,
Microsoft Corp. (ISIN US5949181045) worth $300,000, and Tesla Inc. (ISIN US88160R1014) worth $150,000.

The portfolio allocation is:
- Stocks: 75%
- Bonds: 15%
- Cash: 10%

The valuation date of this report is March 15, 2025."""
            
            test_question = "What is the total portfolio value and when is the valuation date?"
            response = ai_service.generate_response(test_question, context, model="openrouter")
            logger.info(f"Response with context: {response}")
            return True
        else:
            logger.error("No valid OpenRouter API key found")
            return False
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error in AI service test: {e}")
        return False

if __name__ == "__main__":
    logger.info("===== Testing OpenRouter Integration =====")
    
    # First test direct API access
    direct_result = test_openrouter_direct()
    
    # Then test through our AI service
    if direct_result:
        logger.info("\n===== Testing AI Service with OpenRouter =====")
        ai_service_result = test_ai_service()
    
    # Print summary
    logger.info("\n===== Test Results =====")
    logger.info(f"OpenRouter Direct API: {'✅ Working' if direct_result else '❌ Not Working'}")
    if direct_result:
        logger.info(f"AI Service Integration: {'✅ Working' if ai_service_result else '❌ Not Working'}")
    
    if not direct_result:
        logger.info("\nTo fix OpenRouter integration:")
        logger.info("1. Get an API key from https://openrouter.ai/")
        logger.info("2. Add it to your .env file as OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
        logger.info("3. Set DEFAULT_MODEL=openrouter in your .env file")
    elif not ai_service_result:
        logger.info("\nDirect API works but the integration has issues.")
        logger.info("Check error messages above and fix the AI service implementation.")