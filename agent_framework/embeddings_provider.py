"""
Embeddings provider for the agent framework

This module provides a standardized way to access embeddings across the agent framework,
handling different library versions and configuration options.
"""

import os
import logging
from typing import List, Any

logger = logging.getLogger(__name__)

class EmbeddingsProvider:
    """
    Provider for embeddings that handles different library versions and configurations
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embeddings provider
        
        Args:
            model_name: The name of the embedding model to use
        """
        self.model_name = model_name
        self._embeddings = None
        
        # Set the API key in the environment if it exists
        api_key = os.environ.get("HUGGINGFACE_API_KEY")
        if api_key:
            os.environ["HUGGINGFACE_HUB_TOKEN"] = api_key
            
    def get_embeddings(self):
        """
        Get the embeddings model, initializing it if necessary
        
        Returns:
            The embeddings model
        """
        if self._embeddings is None:
            try:
                # Try the newer import first
                from langchain_huggingface import HuggingFaceEmbeddings
                logger.info(f"Initializing HuggingFaceEmbeddings from langchain_huggingface with model {self.model_name}")
                
                # Initialize without explicitly passing the token (uses environment variable)
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=self.model_name
                )
            except Exception as e:
                logger.warning(f"Error initializing embeddings with newer version: {str(e)}")
                
                # Fall back to older version if needed
                try:
                    from langchain.embeddings import HuggingFaceEmbeddings
                    logger.info(f"Falling back to older langchain.embeddings with model {self.model_name}")
                    
                    # Get the API key
                    api_key = os.environ.get("HUGGINGFACE_API_KEY")
                    
                    # Initialize with explicit token if available
                    if api_key:
                        self._embeddings = HuggingFaceEmbeddings(
                            model_name=self.model_name,
                            huggingfacehub_api_token=api_key
                        )
                    else:
                        # Try without token (may use environment variable)
                        self._embeddings = HuggingFaceEmbeddings(
                            model_name=self.model_name
                        )
                except Exception as e2:
                    logger.error(f"Failed to initialize embeddings: {str(e2)}")
                    raise RuntimeError("Could not initialize embeddings provider") from e2
        
        return self._embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embeddings for a query text
        
        Args:
            text: The text to embed
            
        Returns:
            The embedding vector
        """
        embeddings = self.get_embeddings()
        return embeddings.embed_query(text)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of documents
        
        Args:
            documents: The documents to embed
            
        Returns:
            A list of embedding vectors
        """
        embeddings = self.get_embeddings()
        return embeddings.embed_documents(documents)
