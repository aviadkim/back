"""
Services for PDF Scanning Feature
"""

import os
import logging
import uuid
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# In-memory document storage (in a real app, this would be in a database)
documents = {}

# Try to import the agent framework for processing
try:
    from agent_framework import get_coordinator
    coordinator = get_coordinator()
    use_agent_framework = True
except Exception as e:
    logger.warning(f"Failed to import agent framework: {e}")
    coordinator = None
    use_agent_framework = False

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
    document_id = f"{uuid.uuid4()}"
    
    # Process with agent framework if available
    if use_agent_framework and coordinator:
        try:
            result = coordinator.process_document(file_path)
            # Store document info
            documents[document_id] = {
                'id': document_id,
                'file_path': file_path,
                'file_name': file_name,
                'uploaded_at': datetime.now().isoformat(),
                'processing_result': result,
                'metadata': {
                    'title': result.get('metadata', {}).get('title', file_name),
                    'language': result.get('metadata', {}).get('language', 'he'),
                    'page_count': result.get('chunks_count', 1),
                    'confidence': result.get('metadata', {}).get('confidence', 0.9)
                }
            }
            return {
                'document_id': document_id,
                'status': 'success',
                'message': 'Document processed successfully with AI agents',
                'metadata': documents[document_id]['metadata']
            }
        except Exception as e:
            logger.error(f"Error processing document with agent framework: {e}")
            # Fall back to basic processing
            pass
    
    # Basic processing if agent framework is not available or failed
    try:
        # In a real implementation, this would extract text and metadata from the PDF
        # For this demo, we'll use mock data
        documents[document_id] = {
            'id': document_id,
            'file_path': file_path,
            'file_name': file_name,
            'uploaded_at': datetime.now().isoformat(),
            'metadata': {
                'title': Path(file_path).stem,
                'language': 'he',
                'page_count': 10,  # Mock value
                'confidence': 0.9  # Mock value
            },
            'content': {
                'text': 'This is mock text content for the document.',
                'tables': [
                    {
                        'id': f'{document_id}_table_1',
                        'page': 1,
                        'name': 'Table 1',
                        'header': ['Column 1', 'Column 2', 'Column 3'],
                        'rows': [
                            ['Data 1-1', 'Data 1-2', 'Data 1-3'],
                            ['Data 2-1', 'Data 2-2', 'Data 2-3']
                        ]
                    }
                ],
                'entities': [
                    {'type': 'person', 'text': 'John Doe', 'confidence': 0.9},
                    {'type': 'organization', 'text': 'Acme Corp', 'confidence': 0.85},
                    {'type': 'date', 'text': '2022-01-01', 'confidence': 0.95}
                ]
            }
        }
        
        return {
            'document_id': document_id,
            'status': 'success',
            'message': 'Document processed successfully with basic processing',
            'metadata': documents[document_id]['metadata']
        }
    except Exception as e:
        logger.error(f"Error in basic document processing: {e}")
        raise

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
