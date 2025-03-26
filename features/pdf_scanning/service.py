import os
import uuid
import json
import logging
from datetime import datetime
from pymongo import MongoClient
from utils.pdf_processor import PDFProcessor

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
client = MongoClient(MONGO_URI)
db = client.get_database()
documents_collection = db.documents

def process_pdf_document(file_path, language='he'):
    """
    Process a PDF document and extract text and metadata
    
    Args:
        file_path (str): Path to the PDF file
        language (str): Document language (default: 'he' for Hebrew)
        
    Returns:
        tuple: (document_id, document_data) - Document ID and extracted data
    """
    try:
        # Create a document ID
        document_id = str(uuid.uuid4())
        
        # Get filename for storing
        filename = os.path.basename(file_path)
        
        # Process PDF using the utility
        pdf_processor = PDFProcessor(file_path)
        
        # Extract text from PDF
        full_text = pdf_processor.extract_text(language=language)
        
        # Extract metadata
        metadata = pdf_processor.extract_metadata()
        
        # Create document record
        document = {
            '_id': document_id,
            'filename': filename,
            'original_path': file_path,
            'upload_date': datetime.now(),
            'language': language,
            'pages_count': metadata.get('pages_count', 0),
            'title': metadata.get('title', filename),
            'author': metadata.get('author', 'Unknown'),
            'creation_date': metadata.get('creation_date'),
            'modification_date': metadata.get('modification_date'),
            'full_text': full_text,
            'processed': True
        }
        
        # Store document data in MongoDB
        documents_collection.insert_one(document)
        
        logger.info(f"Document {document_id} processed and stored successfully")
        
        # Create document data to return (exclude full text for performance)
        document_data = {k: v for k, v in document.items() if k != 'full_text'}
        document_data['text_length'] = len(full_text)
        document_data['text_preview'] = full_text[:200] + '...' if len(full_text) > 200 else full_text
        
        return document_id, document_data
        
    except Exception as e:
        logger.error(f"Error processing PDF document: {str(e)}")
        raise

def get_all_documents():
    """
    Get all processed documents
    
    Returns:
        list: List of document summaries
    """
    try:
        # Retrieve all documents, but exclude full text for performance
        documents = list(documents_collection.find({}, {
            'full_text': 0
        }))
        
        # Convert MongoDB ObjectId to string for JSON serialization
        for doc in documents:
            if '_id' in doc and not isinstance(doc['_id'], str):
                doc['_id'] = str(doc['_id'])
            
            # Convert datetime objects to strings
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
        
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {str(e)}")
        raise

def get_document_by_id(document_id):
    """
    Get a specific document by ID
    
    Args:
        document_id (str): Document ID
        
    Returns:
        dict: Document data or None if not found
    """
    try:
        document = documents_collection.find_one({'_id': document_id})
        
        if not document:
            return None
        
        # Convert MongoDB ObjectId to string for JSON serialization
        if '_id' in document and not isinstance(document['_id'], str):
            document['_id'] = str(document['_id'])
        
        # Convert datetime objects to strings
        for key, value in document.items():
            if isinstance(value, datetime):
                document[key] = value.isoformat()
        
        return document
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise

def delete_document(document_id):
    """
    Delete a document by ID
    
    Args:
        document_id (str): Document ID
        
    Returns:
        bool: True if document was deleted, False if not found
    """
    try:
        # Find the document first to get the file path
        document = documents_collection.find_one({'_id': document_id})
        
        if not document:
            return False
        
        # Delete the document from MongoDB
        result = documents_collection.delete_one({'_id': document_id})
        
        if result.deleted_count == 0:
            return False
        
        # Try to delete the original file if it exists
        original_path = document.get('original_path')
        if original_path and os.path.exists(original_path):
            try:
                os.remove(original_path)
                logger.info(f"Deleted original file at {original_path}")
            except Exception as e:
                logger.warning(f"Could not delete original file at {original_path}: {str(e)}")
        
        logger.info(f"Document {document_id} deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise
