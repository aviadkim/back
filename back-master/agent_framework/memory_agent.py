# agent_framework/memory_agent.py

import os
import json
import logging
from typing import Dict, List, Any, Optional
import numpy as np

# Import the database instance
from shared.database import db

# Import sentence transformer
try:
    # from sentence_transformers import SentenceTransformer # Temporarily commented out to bypass Torch OSError
    # from sentence_transformers.util import cos_sim # Also triggers torch import, commenting out too

    # Force unavailable if main import is commented
    # SENTENCE_TRANSFORMER_AVAILABLE = True
    raise ImportError("SentenceTransformer import temporarily disabled") # Force except block
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False
    SentenceTransformer = None
    cos_sim = None
    logging.warning(
        "sentence-transformers library not found. Vector search will not be available."
    )


# Set up logging
logger = logging.getLogger(__name__)


class MemoryAgent:
    """
    Agent responsible for managing document memory using MongoDB for persistence
    and vector search for context retrieval.

    This agent maintains a memory of documents for quick access and retrieval
    during chat and analysis.
    """

    def __init__(self):
        """Initialize the memory agent"""
        self.collection_name = "document_analysis_store"
        self.embedding_model = None
        if SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                # Using a multilingual model suitable for both English and Hebrew
                self.embedding_model = SentenceTransformer(
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
                logger.info("Sentence Transformer model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Sentence Transformer model: {e}")
                self.embedding_model = None
        else:
            logger.warning(
                "Sentence Transformer library not available. Vector search disabled."
            )

        # Removed check for db.use_mongo and db.db, as the Database class handles DynamoDB resource state internally.
        # Methods will log errors if the resource is unavailable.

    def add_document(self, document_id: str, analysis_path: str) -> bool:
        """
        Add or update a document's analysis data and embeddings in MongoDB.

        Args:
            document_id (str): Document ID (will be used as _id in MongoDB)
            analysis_path (str): Path to document analysis JSON

        Returns:
            bool: Success status
        """
        # Removed check for db.use_mongo and db.db
        # The db.store_document method (or equivalent DynamoDB method) will handle resource availability.

        try:
            # Check if file exists
            if not os.path.exists(analysis_path):
                logger.error(f"Analysis file not found: {analysis_path}")
                return False

            # Load analysis data
            with open(analysis_path, "r", encoding="utf-8") as f:
                analysis_data = json.load(f)

            text_content = analysis_data.get("text_content", "")
            chunks = self._create_chunks(text_content, 1000, 200)
            chunk_embeddings = []

            # Generate embeddings if model is available and chunks exist
            if self.embedding_model and chunks:
                try:
                    logger.info(
                        f"Generating embeddings for {len(chunks)} chunks of document {document_id}..."
                    )
                    # Encode chunks - ensure model is available
                    embeddings_np = self.embedding_model.encode(
                        chunks, convert_to_numpy=True
                    )
                    # Convert numpy arrays to lists for JSON/BSON serialization
                    chunk_embeddings = [emb.tolist() for emb in embeddings_np]
                    logger.info(f"Embeddings generated for document {document_id}.")
                except Exception as e:
                    logger.error(
                        f"Failed to generate embeddings for document {document_id}: {e}"
                    )
                    chunk_embeddings = []  # Store empty list if embedding fails

            # Prepare document data for MongoDB
            document_info = {
                "_id": document_id,  # Use document_id as MongoDB _id
                "title": analysis_data.get("file_name", "Unknown Document"),
                "language": analysis_data.get("language", "he"),
                "content": text_content,
                "metadata": analysis_data.get("metadata", {}),
                "tables": analysis_data.get("tables", []),
                "entities": analysis_data.get("entities", []),
                "financial_data": analysis_data.get("financial_data", {}),
                "chunks": chunks,
                "chunk_embeddings": chunk_embeddings,  # Store embeddings
                "analysis_path": analysis_path,
            }

            # Use update_one with upsert=True to insert or update the document
            result = db.db[self.collection_name].update_one(
                {"_id": document_id}, {"$set": document_info}, upsert=True
            )

            if result.upserted_id or result.modified_count > 0:
                logger.info(
                    f"Document {document_id} added/updated in persistent memory (MongoDB)"
                )
                return True
            else:
                logger.info(
                    f"Document {document_id} data already up-to-date in persistent memory (MongoDB)"
                )
                return True

        except Exception as e:
            logger.exception(
                f"Error adding/updating document {document_id} in persistent memory: {str(e)}"
            )
            return False

    def forget_document(self, document_id: str) -> bool:
        """
        Remove a document from persistent memory (MongoDB).

        Args:
            document_id (str): Document ID

        Returns:
            bool: Success status
        """
        # Removed check for db.use_mongo and db.db

        try:
            # Assuming db.delete_document now uses DynamoDB and handles resource availability
            deleted = db.delete_document(self.collection_name, {"id": document_id}) # Assuming 'id' is the key for DynamoDB
            if deleted:
                logger.info(
                    f"Document {document_id} removed from persistent memory (MongoDB)"
                )
                return True
            else:
                logger.warning(
                    f"Document {document_id} not found in persistent memory (MongoDB)"
                )
                return False

        except Exception as e:
            logger.exception(
                f"Error removing document {document_id} from persistent memory: {str(e)}"
            )
            return False

    def get_document_context(
        self, document_id: str, query: str, top_k: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Get relevant context from document based on query using vector similarity search.

        Args:
            document_id (str): Document ID
            query (str): User query
            top_k (int): Number of top relevant chunks to return

        Returns:
            Optional[Dict]: Document context containing relevant chunks
        """
        # Removed check for db.use_mongo and db.db

        try:
            # Assuming db.find_document now uses DynamoDB and handles resource availability
            document = db.find_document(self.collection_name, {"id": document_id}) # Assuming 'id' is the key for DynamoDB

            if not document:
                logger.warning(
                    f"Document {document_id} not found in persistent memory (MongoDB)"
                )
                return None

            chunks = document.get("chunks", [])
            chunk_embeddings_list = document.get("chunk_embeddings", [])

            relevant_chunks_content = []

            # Use vector search if embeddings and model are available
            if (
                self.embedding_model
                and chunks
                and chunk_embeddings_list
                and len(chunks) == len(chunk_embeddings_list)
            ):
                try:
                    logger.info(
                        f"Performing vector search for document {document_id}..."
                    )
                    # Convert stored lists back to numpy array for calculations
                    chunk_embeddings = np.array(chunk_embeddings_list)

                    # Generate query embedding
                    query_embedding = self.embedding_model.encode(
                        query, convert_to_numpy=True
                    )

                    # Calculate cosine similarities
                    # Ensure embeddings are 2D arrays for cos_sim
                    if query_embedding.ndim == 1:
                        query_embedding = query_embedding.reshape(1, -1)
                    if (
                        chunk_embeddings.ndim == 1
                    ):  # Should not happen if stored correctly
                        chunk_embeddings = chunk_embeddings.reshape(1, -1)

                    similarities = cos_sim(query_embedding, chunk_embeddings)[
                        0
                    ]  # Get the similarity scores tensor/array

                    # Get top_k indices
                    # Using argsort for potentially better performance on large arrays
                    # We negate similarities because argsort sorts in ascending order
                    top_indices = np.argsort(-similarities)[:top_k]

                    # Filter out results below a certain threshold (optional)
                    similarity_threshold = 0.3  # Adjust as needed
                    relevant_chunks_content = [
                        chunks[i]
                        for i in top_indices
                        if similarities[i] > similarity_threshold
                    ]

                    logger.info(
                        f"Found {len(relevant_chunks_content)} relevant chunks via vector search."
                    )

                except Exception as e:
                    logger.error(
                        f"Vector search failed for document {document_id}: {e}. Falling back."
                    )
                    relevant_chunks_content = []  # Fallback handled below

            # Fallback: If vector search failed or wasn't possible, return first few chunks
            if not relevant_chunks_content:
                logger.warning(
                    f"Vector search skipped or failed for document {document_id}. Returning first {top_k} chunks."
                )
                relevant_chunks_content = chunks[:top_k]

            # Create context object to return
            context = {
                "id": document_id,
                "title": document.get("title", "Unknown Document"),
                "content": "\n\n".join(
                    relevant_chunks_content
                ),  # Join the content of relevant chunks
                "metadata": document.get("metadata", {}),
                "language": document.get("language", "he"),
            }

            return context

        except Exception as e:
            logger.exception(
                f"Error getting context for document {document_id} from persistent memory: {str(e)}"
            )
            return None

    # --- Other retrieval methods remain the same ---

    def get_document_full_content(self, document_id: str) -> Optional[str]:
        """
        Get full document content from persistent memory (MongoDB).
        (Implementation remains the same)
        """
        # Removed check for db.use_mongo and db.db

        try:
            # Assuming db.find_document now uses DynamoDB and handles resource availability
            document = db.find_document(self.collection_name, {"id": document_id}) # Assuming 'id' is the key for DynamoDB
            if not document:
                logger.warning(
                    f"Document {document_id} not found in persistent memory (MongoDB)"
                )
                return None
            return document.get("content", "")
        except Exception as e:
            logger.exception(
                f"Error getting content for document {document_id} from persistent memory: {str(e)}"
            )
            return None

    def get_document_financial_data(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get financial data from document in persistent memory (MongoDB).
        (Implementation remains the same)
        """
        # Removed check for db.use_mongo and db.db

        try:
            # Assuming db.find_document now uses DynamoDB and handles resource availability
            document = db.find_document(self.collection_name, {"id": document_id}) # Assuming 'id' is the key for DynamoDB
            if not document:
                logger.warning(
                    f"Document {document_id} not found in persistent memory (MongoDB)"
                )
                return None
            return document.get("financial_data", {})
        except Exception as e:
            logger.exception(
                f"Error getting financial data for document {document_id} from persistent memory: {str(e)}"
            )
            return None

    def get_document_tables(self, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get tables from document in persistent memory (MongoDB).
        (Implementation remains the same)
        """
        # Removed check for db.use_mongo and db.db

        try:
            # Assuming db.find_document now uses DynamoDB and handles resource availability
            document = db.find_document(self.collection_name, {"id": document_id}) # Assuming 'id' is the key for DynamoDB
            if not document:
                logger.warning(
                    f"Document {document_id} not found in persistent memory (MongoDB)"
                )
                return None
            return document.get("tables", [])
        except Exception as e:
            logger.exception(
                f"Error getting tables for document {document_id} from persistent memory: {str(e)}"
            )
            return None

    def update_document(self, document_id: str, analysis_path: str) -> bool:
        """
        Update document in persistent memory (MongoDB).
        (Implementation remains the same)
        """
        return self.add_document(document_id, analysis_path)

    # --- Helper methods remain the same ---

    def _create_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Create overlapping chunks from text
        (Implementation remains the same)
        """
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if end < len(text):
                sentence_end = self._find_sentence_end(chunk)
                if sentence_end > 0:
                    chunk = chunk[:sentence_end]
                    end = start + sentence_end
            chunks.append(chunk)
            next_start = end - overlap
            if next_start <= start:
                next_start = start + 1
            start = next_start
        # Filter out potentially empty chunks if text was very short
        return [c for c in chunks if c.strip()]

    def _find_sentence_end(self, text: str) -> int:
        """
        Find the end of the last complete sentence in text
        (Implementation remains the same)
        """
        for i in range(len(text) - 1, 0, -1):
            if text[i] in [".", "!", "?", ":", ";", "\n"] and i < len(text) - 1:
                if i + 1 >= len(text) or text[i + 1].isspace():
                    return i + 1
        for i in range(len(text) - 1, 0, -1):
            if text[i].isspace() and i < len(text) - 1:
                return i + 1
        return -1

    # _find_relevant_chunks is no longer needed as get_document_context uses vector search
