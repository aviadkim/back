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
        try:
            # Try the new import first (recommended)
            from langchain_huggingface import HuggingFaceEmbeddings
            logger.info("✅ Successfully imported langchain_huggingface")
        except ImportError:
            # Fall back to deprecated import for compatibility
            logger.warning("⚠️ langchain_huggingface not found, falling back to deprecated import")
            from langchain.embeddings import HuggingFaceEmbeddings
        
        # Initialize embeddings with the API key
        logger.info("Initializing embeddings with model: sentence-transformers/all-MiniLM-L6-v2")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            huggingfacehub_api_token=api_key
        )
        
        # Test the embeddings with a simple text
        test_text = "This is a test to verify Hugging Face API connection"
        logger.info(f"Generating embeddings for text: '{test_text}'")
        
        embedding_vector = embeddings.embed_query(test_text)
        
        # If we get here without errors, the connection is working
        logger.info(f"✅ Successfully generated embeddings with {len(embedding_vector)} dimensions")
        logger.info("✅ Hugging Face API connection is working correctly!")
        
        # Show a sample of the embedding vector
        logger.info(f"Sample of embedding vector: {embedding_vector[:5]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error connecting to Hugging Face API: {str(e)}")
        logger.error("Please check your API key and internet connection")
        return False

if __name__ == "__main__":
    logger.info("=== Testing Hugging Face API Connection ===")
    success = test_huggingface_connection()
    logger.info(f"Test {'passed' if success else 'failed'}")
