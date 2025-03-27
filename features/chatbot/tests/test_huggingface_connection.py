"""
Test the connection to the Hugging Face API

This script verifies that:
1. The HUGGINGFACE_API_KEY environment variable is set
2. We can connect to the Hugging Face API
3. We can successfully generate embeddings

Run this test with:
    python -m features.chatbot.tests.test_huggingface_connection
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_huggingface_connection():
    """Test connection to Hugging Face API"""
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.error("❌ HUGGINGFACE_API_KEY not found in environment variables")
        logger.error("Please make sure it's set in your .env file or in your environment")
        return False
    
    logger.info(f"✅ Found Hugging Face API key: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Try importing the necessary components
        # Removed redundant inner try block
        # Use the standard import path
        from langchain_huggingface import HuggingFaceEmbeddings # Corrected indentation
        logger.info("✅ Successfully imported langchain_huggingface") # Corrected indentation

        # Set the token environment variable for the library to pick up
        # (Ideally, this should be set globally before running the script, e.g., via .env)
        if api_key: # Corrected indentation
             os.environ["HUGGINGFACE_HUB_TOKEN"] = api_key # Corrected indentation
             logger.info("Temporarily set HUGGINGFACE_HUB_TOKEN environment variable.") # Corrected indentation

        # Initialize embeddings (should pick up token from environment)
        logger.info("Initializing embeddings with model: sentence-transformers/all-MiniLM-L6-v2") # Corrected indentation
        embeddings = HuggingFaceEmbeddings( # Corrected indentation
            model_name="sentence-transformers/all-MiniLM-L6-v2" # Corrected indentation
            # Removed explicit token passing
        ) # Corrected indentation

        # Test the embeddings with a simple text
        test_text = "This is a test to verify Hugging Face API connection" # Corrected indentation
        logger.info(f"Generating embeddings for text: '{test_text}'") # Corrected indentation
        
        embedding_vector = embeddings.embed_query(test_text) # Corrected indentation
        
        # If we get here without errors, the connection is working
        logger.info(f"✅ Successfully generated embeddings with {len(embedding_vector)} dimensions") # Corrected indentation
        logger.info("✅ Hugging Face API connection is working correctly!") # Corrected indentation
        
        # Show a sample of the embedding vector
        logger.info(f"Sample of embedding vector: {embedding_vector[:5]}...") # Corrected indentation
        
        return True # Corrected indentation
        
    except Exception as e:
        logger.error(f"❌ Error connecting to Hugging Face API: {str(e)}")
        logger.error("Please check your API key and internet connection")
        return False

if __name__ == "__main__":
    logger.info("=== Testing Hugging Face API Connection ===")
    success = test_huggingface_connection()
    logger.info(f"Test {'passed' if success else 'failed'}")
