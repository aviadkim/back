#!/usr/bin/env python3
"""
Test AI models with direct API calls to help diagnose issues.
"""
import os
import sys
import requests
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AIModelTest")

def test_huggingface_api():
    """Test direct connection to HuggingFace API"""
    logger.info("Testing HuggingFace API directly")
    
    # Get API key
    load_dotenv()
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not api_key:
        logger.error("No HuggingFace API key found in .env file")
        return False
    
    # Try to connect to a simple model
    model = "google/flan-t5-small"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "What is the capital of France?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7
        }
    }
    
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        logger.info(f"Making request to {api_url}")
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        # Print complete response for debugging
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Success! Response: {result}")
            return True
        else:
            logger.error(f"Error: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error connecting to HuggingFace API: {e}")
        return False

def test_gemini_api():
    """Test direct connection to Gemini API"""
    logger.info("Testing Gemini API directly")
    
    # Get API key
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("No Gemini API key found in .env file")
        return False
    
    # Clean up the key if it has spaces
    if " " in api_key:
        api_key = api_key.split()[-1]
    
    # Try to install and use the Google Generative AI library
    try:
        try:
            import google.generativeai as genai
            logger.info("Using google.generativeai library")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("What is the capital of France?")
            
            logger.info(f"Success! Response: {response.text}")
            return True
        except ImportError:
            # Fall back to direct API call
            logger.info("google.generativeai not available, using direct API call")
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "What is the capital of France?"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100
                }
            }
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            logger.info(f"Making request to Gemini API")
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            
            # Print complete response for debugging
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Success! Response: {json.dumps(result, indent=2)}")
                return True
            else:
                logger.error(f"Error: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error connecting to Gemini API: {e}")
        return False

def main():
    """Run the tests"""
    logger.info("===== Testing AI Models =====")
    
    hf_result = test_huggingface_api()
    gemini_result = test_gemini_api()
    
    logger.info("\n===== Test Results =====")
    logger.info(f"HuggingFace API: {'✅ Working' if hf_result else '❌ Not Working'}")
    logger.info(f"Gemini API: {'✅ Working' if gemini_result else '❌ Not Working'}")
    
    if not hf_result and not gemini_result:
        logger.info("\nTroubleshooting tips:")
        logger.info("1. Check your API keys in the .env file")
        logger.info("2. Ensure you have an active internet connection")
        logger.info("3. Check if the API services are available")
        logger.info("4. Try installing the Google Generative AI library: pip install google-generativeai")

if __name__ == "__main__":
    main()
