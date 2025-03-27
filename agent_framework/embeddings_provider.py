"""
Embeddings provider for the agent framework

This module provides a standardized way to access embeddings across the agent framework,
handling different library versions and configuration options.
"""

import os
import logging
from typing import List  # Removed unused Any

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
                from langchain_huggingface import HuggingFaceEmbeddings

                logger.info(
                    f"Initializing HuggingFaceEmbeddings with model {self.model_name}"
                )

                # Initialize using langchain_huggingface.
                # It should automatically use HUGGINGFACE_HUB_TOKEN if set in the environment.
                self._embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
            except ImportError:
                logger.error(
                    "`langchain-huggingface` package not found. Please install it."
                )
                raise RuntimeError(
                    "Could not initialize embeddings provider: langchain-huggingface not installed."
                )
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFace embeddings: {str(e)}")
                raise RuntimeError("Could not initialize embeddings provider") from e

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
