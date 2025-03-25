#!/usr/bin/env python

"""
Updated test script to check Hugging Face API key compatibility with current library versions.
Run this script from the root directory of the repository:

python test_api_key_fixed.py
"""

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test Hugging Face API key with different methods"""
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.error("❌ HUGGINGFACE_API_KEY not found in environment variables")
        logger.error("Please make sure it's set in your .env file or in your environment")
        return False
    
    logger.info(f"✅ Found Hugging Face API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Set the API key in the environment (some libraries use this directly)
    os.environ["HUGGINGFACE_HUB_TOKEN"] = api_key
    logger.info("Set HUGGINGFACE_HUB_TOKEN from HUGGINGFACE_API_KEY")
    
    # Try different ways to initialize embeddings
    try:
        # Method 1: Try the langchain-huggingface package
        try:
            logger.info("\nAttempting method 1: Using langchain_huggingface...")
            from langchain_huggingface import HuggingFaceEmbeddings
            
            # Try initializing without explicitly passing the token
            # (it may use HUGGINGFACE_HUB_TOKEN from environment)
            logger.info("Initializing embeddings without explicit token...")
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Test the embeddings
            test_text = "This is a test to verify Hugging Face API connection"
            logger.info(f"Generating embeddings for text: '{test_text}'")
            embedding_vector = embeddings.embed_query(test_text)
            logger.info(f"✅ Success! Generated embeddings with {len(embedding_vector)} dimensions")
            logger.info(f"Sample: {embedding_vector[:3]}...")
            return True
            
        except Exception as e1:
            logger.error(f"Method 1 failed: {str(e1)}")
            
            # Method 2: Try with different parameter name
            try:
                logger.info("\nAttempting method 2: Using different parameter name...")
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    api_key=api_key  # Try this parameter name instead
                )
                
                # Test the embeddings
                test_text = "This is a test to verify Hugging Face API connection"
                logger.info(f"Generating embeddings for text: '{test_text}'")
                embedding_vector = embeddings.embed_query(test_text)
                logger.info(f"✅ Success! Generated embeddings with {len(embedding_vector)} dimensions")
                logger.info(f"Sample: {embedding_vector[:3]}...")
                return True
                
            except Exception as e2:
                logger.error(f"Method 2 failed: {str(e2)}")
                
                # Method 3: Try the older langchain package
                try:
                    logger.info("\nAttempting method 3: Using older langchain package...")
                    from langchain.embeddings import HuggingFaceEmbeddings as OldHuggingFaceEmbeddings
                    
                    embeddings = OldHuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        huggingfacehub_api_token=api_key
                    )
                    
                    # Test the embeddings
                    test_text = "This is a test to verify Hugging Face API connection"
                    logger.info(f"Generating embeddings for text: '{test_text}'")
                    embedding_vector = embeddings.embed_query(test_text)
                    logger.info(f"✅ Success! Generated embeddings with {len(embedding_vector)} dimensions")
                    logger.info(f"Sample: {embedding_vector[:3]}...")
                    return True
                    
                except Exception as e3:
                    logger.error(f"Method 3 failed: {str(e3)}")
                    
                    # Method 4: Try using huggingface_hub directly
                    try:
                        logger.info("\nAttempting method 4: Using huggingface_hub directly...")
                        from huggingface_hub import HfApi
                        
                        api = HfApi(token=api_key)
                        models = api.list_models(limit=1)
                        logger.info(f"✅ Success! Connected to Hugging Face. Sample model: {models[0].id if models else 'None'}")
                        return True
                        
                    except Exception as e4:
                        logger.error(f"Method 4 failed: {str(e4)}")
                        
                        # All methods failed
                        logger.error("\n❌ All connection methods failed.")
                        logger.error("This might be due to a version incompatibility or network issue.")
                        logger.error("Try installing specific versions of the libraries:")
                        logger.error("pip install langchain==0.0.267 langchain-huggingface==0.0.5 huggingface-hub==0.16.4")
                        return False
    
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("=== Testing Hugging Face API Connection ===")
    success = main()
    logger.info(f"\nFinal result: Test {'passed ✓' if success else 'failed ✗'}")
