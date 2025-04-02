#!/usr/bin/env python

"""
Simple test script to check if the Hugging Face API key is set correctly.
Run this script from the root directory of the repository:

python test_api_key.py
"""

import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found in environment variables")
        print("Please make sure it's set in your .env file or in your environment")
        return False
    
    print(f"✅ Found Hugging Face API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Try to import necessary packages
    try:
        # Use the standard import path
        from langchain_huggingface import HuggingFaceEmbeddings
        print("✅ Successfully imported langchain_huggingface")
        
        # Set the token environment variable for the library to pick up
        # (Ideally, this should be set globally before running the script, e.g., via .env)
        if api_key:
             os.environ["HUGGINGFACE_HUB_TOKEN"] = api_key
             print("Temporarily set HUGGINGFACE_HUB_TOKEN environment variable.")
        
        # Initialize embeddings (should pick up token from environment)
        print("Initializing embeddings with model: sentence-transformers/all-MiniLM-L6-v2")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
            # Removed explicit token passing
        )
        
        # Test the embeddings with a simple text
        test_text = "This is a test to verify Hugging Face API connection"
        print(f"Generating embeddings for text: '{test_text}'")
        
        embedding_vector = embeddings.embed_query(test_text)
        
        # If we get here without errors, the connection is working
        print(f"✅ Successfully generated embeddings with {len(embedding_vector)} dimensions")
        print("✅ Hugging Face API connection is working correctly!")
        
        # Show a sample of the embedding vector
        print(f"Sample of embedding vector: {embedding_vector[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Hugging Face API: {str(e)}")
        print("Please check your API key and internet connection")
        return False

if __name__ == "__main__":
    print("=== Testing Hugging Face API Connection ===")
    success = main()
    print(f"Test {'passed' if success else 'failed'}")
