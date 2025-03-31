"""
Services for PDF Scanning Feature
"""

import os
import logging
import uuid
from datetime import datetime
import json
from pathlib import Path
from pdf_processor import DocumentProcessor # Import the new processor
from config.configuration import document_processor_config # Import the config for the processor

logger = logging.getLogger(__name__)

# In-memory document storage (in a real app, this would be in a database)
documents = {}

# Instantiate the DocumentProcessor (consider making this a singleton or managed instance later)
# Pass the specific configuration section for the processor
document_processor = DocumentProcessor(config=document_processor_config)

def process_pdf_document(file_path):
    """
    Process a PDF document
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        dict: Processing result
    """
    logger.info(f"Processing PDF document: {file_path}")
    
    # Generate document ID from filename
    file_name = os.path.basename(file_path)
    document_id = f"{uuid.uuid4()}" # Generate a unique ID for this processing instance

    try:
        # Use the unified DocumentProcessor
        result = document_processor.process_document(file_path)

        if 'error' in result:
            # Processing failed
            logger.error(f"DocumentProcessor failed for {file_path}: {result['error']}")
            # Store minimal failure info
            documents[document_id] = {
                'id': document_id,
                'file_path': file_path,
                'file_name': file_name,
                'uploaded_at': datetime.now().isoformat(),
                'processing_result': {'error': result['error']},
                'metadata': result.get('metadata', {}) # Include metadata if available
            }
            return {
                'document_id': document_id,
                'status': 'error',
                'message': f"Error processing document: {result['error']}",
                'metadata': result.get('metadata', {})
            }
        else:
            # Processing succeeded
            logger.info(f"DocumentProcessor succeeded for {file_path}")
            # Store the full result
            documents[document_id] = {
                'id': document_id,
                'file_path': file_path,
                'file_name': file_name,
                'uploaded_at': datetime.now().isoformat(),
                'processing_result': result, # Store the detailed result
                'metadata': result.get('metadata', {}) # Extract top-level metadata
            }
            return {
                'document_id': document_id,
                'status': 'success',
                'message': 'Document processed successfully',
                'metadata': result.get('metadata', {}) # Return top-level metadata
            }

    except Exception as e:
        # Catch unexpected errors during the call
        logger.exception(f"Unexpected error calling DocumentProcessor for {file_path}: {e}")
        # Store minimal failure info
        documents[document_id] = {
            'id': document_id,
            'file_path': file_path,
            'file_name': file_name,
            'uploaded_at': datetime.now().isoformat(),
            'processing_result': {'error': str(e)},
            'metadata': {'processing_status': 'failed'}
        }
        return {
            'document_id': document_id,
            'status': 'error',
            'message': f"Unexpected error during processing: {str(e)}",
            'metadata': {'processing_status': 'failed'}
        }

def get_all_documents():
    """
    Get all documents
    
    Returns:
        list: All documents
    """
    return [
        {
            'id': doc_id,
            'file_name': info['file_name'],
            'uploaded_at': info['uploaded_at'],
            'metadata': info['metadata']
        }
        for doc_id, info in documents.items()
    ]

def get_document_by_id(document_id):
    """
    Get a document by ID
    
    Args:
        document_id: Document ID
        
    Returns:
        dict: Document info or None if not found
    """
    if document_id in documents:
        return documents[document_id]
    return None

def delete_document(document_id):
    """
    Delete a document
    
    Args:
        document_id: Document ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    if document_id in documents:
        # Delete the file if it exists
        try:
            file_path = documents[document_id]['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            logger.error(f"Error deleting document file: {e}")
        
        # Remove from memory
        del documents[document_id]
        return True
    
    return False
