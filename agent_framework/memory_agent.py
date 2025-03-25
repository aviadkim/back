import os
import json
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

class MemoryAgent:
    """
    Agent responsible for managing document memory
    
    This agent maintains a memory of documents for quick access and retrieval
    during chat and analysis.
    """
    
    def __init__(self):
        """Initialize the memory agent"""
        # Document memory
        self.documents = {}
        
    def add_document(self, document_id: str, analysis_path: str) -> bool:
        """
        Add a document to memory
        
        Args:
            document_id (str): Document ID
            analysis_path (str): Path to document analysis JSON
            
        Returns:
            bool: Success status
        """
        try:
            # Check if file exists
            if not os.path.exists(analysis_path):
                logger.error(f"Analysis file not found: {analysis_path}")
                return False
                
            # Load analysis data
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
                
            # Extract key document info
            document_info = {
                'id': document_id,
                'title': analysis_data.get('file_name', 'Unknown Document'),
                'language': analysis_data.get('language', 'he'),
                'content': analysis_data.get('text_content', ''),
                'metadata': analysis_data.get('metadata', {}),
                'tables': analysis_data.get('tables', []),
                'entities': analysis_data.get('entities', []),
                'financial_data': analysis_data.get('financial_data', {}),
                'chunks': self._create_chunks(analysis_data.get('text_content', ''), 1000, 200),
                'analysis_path': analysis_path
            }
            
            # Add to memory
            self.documents[document_id] = document_info
            logger.info(f"Document {document_id} added to memory")
            return True
            
        except Exception as e:
            logger.exception(f"Error adding document {document_id} to memory: {str(e)}")
            return False
            
    def forget_document(self, document_id: str) -> bool:
        """
        Remove a document from memory
        
        Args:
            document_id (str): Document ID
            
        Returns:
            bool: Success status
        """
        try:
            if document_id in self.documents:
                del self.documents[document_id]
                logger.info(f"Document {document_id} removed from memory")
                return True
            else:
                logger.warning(f"Document {document_id} not found in memory")
                return False
                
        except Exception as e:
            logger.exception(f"Error removing document {document_id} from memory: {str(e)}")
            return False
            
    def get_document_context(self, document_id: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Get relevant context from document based on query
        
        Args:
            document_id (str): Document ID
            query (str): User query
            
        Returns:
            Optional[Dict]: Document context
        """
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found in memory")
                return None
                
            document = self.documents[document_id]
            
            # Find relevant chunks based on simple keyword matching
            # In a production system, this would use vector similarity
            relevant_chunks = self._find_relevant_chunks(document['chunks'], query)
            
            # Create context
            context = {
                'id': document_id,
                'title': document.get('title', 'Unknown Document'),
                'content': '\n\n'.join(relevant_chunks),
                'metadata': document.get('metadata', {}),
                'language': document.get('language', 'he')
            }
            
            # If no relevant chunks found, use beginning of document
            if not relevant_chunks and document.get('content'):
                context['content'] = document['content'][:5000]  # Use first 5000 chars
                
            return context
            
        except Exception as e:
            logger.exception(f"Error getting context for document {document_id}: {str(e)}")
            return None
            
    def get_document_full_content(self, document_id: str) -> Optional[str]:
        """
        Get full document content
        
        Args:
            document_id (str): Document ID
            
        Returns:
            Optional[str]: Document content
        """
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found in memory")
                return None
                
            document = self.documents[document_id]
            return document.get('content', '')
            
        except Exception as e:
            logger.exception(f"Error getting content for document {document_id}: {str(e)}")
            return None
            
    def get_document_financial_data(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get financial data from document
        
        Args:
            document_id (str): Document ID
            
        Returns:
            Optional[Dict]: Financial data
        """
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found in memory")
                return None
                
            document = self.documents[document_id]
            return document.get('financial_data', {})
            
        except Exception as e:
            logger.exception(f"Error getting financial data for document {document_id}: {str(e)}")
            return None
            
    def get_document_tables(self, document_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get tables from document
        
        Args:
            document_id (str): Document ID
            
        Returns:
            Optional[List[Dict]]: Document tables
        """
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found in memory")
                return None
                
            document = self.documents[document_id]
            return document.get('tables', [])
            
        except Exception as e:
            logger.exception(f"Error getting tables for document {document_id}: {str(e)}")
            return None
            
    def update_document(self, document_id: str, analysis_path: str) -> bool:
        """
        Update document in memory
        
        Args:
            document_id (str): Document ID
            analysis_path (str): Path to document analysis JSON
            
        Returns:
            bool: Success status
        """
        # Just re-add the document with the updated analysis
        return self.add_document(document_id, analysis_path)
        
    def _create_chunks(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Create overlapping chunks from text
        
        Args:
            text (str): Text to chunk
            chunk_size (int): Size of each chunk
            overlap (int): Overlap between chunks
            
        Returns:
            List[str]: List of text chunks
        """
        if not text:
            return []
            
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Adjust chunk to end at sentence boundary if possible
            if end < len(text):
                sentence_end = self._find_sentence_end(chunk)
                if sentence_end > 0:
                    chunk = chunk[:sentence_end]
                    end = start + sentence_end
            
            chunks.append(chunk)
            
            # Move start position for next chunk
            start = end - overlap
            
        return chunks
        
    def _find_sentence_end(self, text: str) -> int:
        """
        Find the end of the last complete sentence in text
        
        Args:
            text (str): Text to search
            
        Returns:
            int: Position of sentence end
        """
        # Look for the last sentence-ending punctuation
        for i in range(len(text) - 1, 0, -1):
            if text[i] in ['.', '!', '?', ':', ';', '\n'] and i < len(text) - 1:
                return i + 1
                
        # If no sentence boundary found, look for the last word boundary
        for i in range(len(text) - 1, 0, -1):
            if text[i].isspace() and i < len(text) - 1:
                return i + 1
                
        # If no boundaries found, return the entire chunk
        return -1
        
    def _find_relevant_chunks(self, chunks: List[str], query: str) -> List[str]:
        """
        Find chunks relevant to the query
        
        Args:
            chunks (List[str]): Text chunks
            query (str): Query string
            
        Returns:
            List[str]: Relevant chunks
        """
        if not chunks or not query:
            return []
            
        # Simple keyword matching
        # In a production system, this would use vector similarity
        
        # Get keywords from query
        keywords = [
            word.lower() for word in query.split() 
            if len(word) > 3 and word.lower() not in ['what', 'where', 'when', 'which', 'who', 'how', 'the', 'and', 'that', 'this', 'for', 'from', 'with']
        ]
        
        # Score each chunk
        chunk_scores = []
        for i, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = 0
            
            for keyword in keywords:
                if keyword in chunk_lower:
                    score += chunk_lower.count(keyword)
                    
            chunk_scores.append((i, score))
            
        # Sort chunks by score
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get top chunks (up to 5)
        relevant_chunks = []
        for i, score in chunk_scores:
            if score > 0 and len(relevant_chunks) < 5:
                relevant_chunks.append(chunks[i])
                
        return relevant_chunks
