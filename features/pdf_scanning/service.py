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
from services.database_service import save_document_results, get_document_by_id as db_get_doc_by_id, get_collection # Import DB functions
from config.configuration import document_processor_config # Import the config for the processor
from bson import ObjectId # For handling MongoDB ObjectIds

logger = logging.getLogger(__name__)

# In-memory document storage (in a real app, this would be in a database)
# documents = {} # Remove in-memory storage

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
    
    # Generate a unique document ID (UUID)
    file_name = os.path.basename(file_path)
    document_id = str(uuid.uuid4()) # Use string representation of UUID

    try:
        # Use the unified DocumentProcessor
        result = document_processor.process_document(file_path)

        if 'error' in result:
            # Processing failed
            logger.error(f"DocumentProcessor failed for {file_path}: {result['error']}")
            # Prepare failure data for DB
            db_data = {
                'file_path': file_path,
                'file_name': file_name,
                'uploaded_at': datetime.now().isoformat(),
                'processing_result': {'error': result.get('error', 'Unknown processing error'), 'details': result.get('details')},
                'metadata': result.get('metadata', {'processing_status': 'failed'}) # Ensure status is failed
            }
            # Save failure info to DB
            save_document_results(document_id, db_data)
            return {
                'document_id': document_id,
                'status': 'error',
                'message': f"Error processing document: {result['error']}",
                'metadata': result.get('metadata', {})
            }
        else:
            # Processing succeeded
            logger.info(f"DocumentProcessor succeeded for {file_path}")
            # Prepare success data for DB
            db_data = {
                'file_path': file_path,
                'file_name': file_name,
                'uploaded_at': datetime.now().isoformat(),
                'processing_result': result, # Store the detailed result
                'metadata': result.get('metadata', {}) # Extract top-level metadata
            }
            # Save success info to DB
            save_document_results(document_id, db_data)
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
        db_data = {
            'file_path': file_path,
            'file_name': file_name,
            'uploaded_at': datetime.now().isoformat(),
            'processing_result': {'error': str(e)},
            'metadata': {'processing_status': 'failed'}
        }
        # Save failure info to DB
        save_document_results(document_id, db_data)
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
    logger.info("Fetching all documents from database")
    collection = get_collection('documents')
    if not collection:
        logger.error("Database connection not available for get_all_documents.")
        return []

    try:
        # Fetch only necessary fields for the list view
        documents_cursor = collection.find({}, {
            '_id': 1,
            'file_name': 1,
            'uploaded_at': 1,
            'metadata': 1
        })

        documents_list = []
        for doc in documents_cursor:
            doc_info = {
                'id': str(doc['_id']), # Convert ObjectId to string
                'file_name': doc.get('file_name', 'N/A'),
                'uploaded_at': doc.get('uploaded_at', 'N/A'),
                'metadata': doc.get('metadata', {})
            }
            documents_list.append(doc_info)

        logger.info(f"Retrieved {len(documents_list)} documents.")
        return documents_list
    except Exception as e:
        logger.exception(f"Error fetching documents from database: {e}")
        return []

def get_document_by_id(document_id):
    """
    Get a document by ID
    
    Args:
        document_id: Document ID
        
    Returns:
        dict: Document info or None if not found
    """
    logger.info(f"Fetching document by ID: {document_id}")
    try:
        # Attempt to convert to ObjectId if your IDs are stored as such
        # If you store IDs as strings (like UUIDs), use the ID directly
        # obj_id = ObjectId(document_id) # Uncomment if using ObjectIds
        obj_id = document_id # Assuming document_id is the string UUID used in save_document_results

        document = db_get_doc_by_id(obj_id) # Use the imported DB function

        if document:
            # Convert ObjectId back to string if present
            if '_id' in document and isinstance(document['_id'], ObjectId):
                 document['id'] = str(document['_id'])
                 del document['_id']
            else:
                 document['id'] = obj_id # Ensure 'id' field exists
            logger.info(f"Document found: {document_id}")
            return document
        else:
            logger.warning(f"Document not found in database: {document_id}")
            return None
    except Exception as e:
        # Handle potential ObjectId conversion errors or DB errors
        logger.exception(f"Error fetching document {document_id} from database: {e}")
        return None

def delete_document(document_id):
    """
    Delete a document
    
    Args:
        document_id: Document ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    logger.info(f"Attempting to delete document: {document_id}")
    collection = get_collection('documents')
    if not collection:
        logger.error("Database connection not available for delete_document.")
        return False

    try:
        # First, find the document to get the file path
        # obj_id = ObjectId(document_id) # Uncomment if using ObjectIds
        obj_id = document_id # Assuming string UUID
        document = collection.find_one({'_id': obj_id}, {'file_path': 1})

        if not document:
            logger.warning(f"Document not found for deletion: {document_id}")
            return False

        # Delete the document record from the database
        delete_result = collection.delete_one({'_id': obj_id})

        if delete_result.deleted_count == 1:
            logger.info(f"Successfully deleted document record from DB: {document_id}")
            # Delete the associated file from the filesystem
            try:
                file_path = document.get('file_path')
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Successfully deleted document file: {file_path}")
                elif file_path:
                    logger.warning(f"Document file path found but file does not exist: {file_path}")
            except Exception as file_err:
                logger.error(f"Error deleting document file {file_path}: {file_err}")
            return True
        else:
            logger.warning(f"Document {document_id} found but failed to delete from DB.")
            return False

    except Exception as e:
        logger.exception(f"Error deleting document {document_id}: {e}")
        return False

    # --- Old in-memory logic ---
    # if document_id in documents:
        # Delete the file if it exists
        # try:
        #     file_path = documents[document_id]['file_path']
        #     if os.path.exists(file_path):
        #         os.remove(file_path)
        # except Exception as e:
        #     logger.error(f"Error deleting document file: {e}")
        
        # Remove from memory
        # del documents[document_id]
        # return True
    
    # return False
