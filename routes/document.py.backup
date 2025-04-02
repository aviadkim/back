from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
import logging
from pathlib import Path
from pymongo import MongoClient
import datetime

# Import document processor
from pdf_processor import DocumentProcessor
# Import configuration (assuming MONGO_URI is defined there)
# If MONGO_URI is not in document_processor_config, import it from the main config
from config.configuration import document_processor_config, MONGO_URI, UPLOAD_FOLDER, MAX_FILE_SIZE

# Create blueprint for document API
document_api = Blueprint('document_api', __name__)
logger = logging.getLogger(__name__)

# Helper functions for response standardization
def success_response(data=None, message=None):
    """Standard success response format."""
    response = {
        'status': 'success',
        'message': message,
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)

def error_response(message, status_code=400):
    """Standard error response format."""
    response = {
        'status': 'error',
        'message': message
    }
    return jsonify(response), status_code

# MongoDB connection (consider moving to a shared db module or using Flask-PyMongo)
_mongo_client = None
def get_db():
    global _mongo_client
    if _mongo_client is None:
        try:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) # Add timeout
            # The ismaster command is cheap and does not require auth.
            _mongo_client.admin.command('ping')
            logger.info("MongoDB connection successful.")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            _mongo_client = None # Reset client on failure
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
    # Use the default database name from the URI if not specified, or a specific one
    db_name = MongoClient(MONGO_URI).get_database().name
    return _mongo_client[db_name]

# Document upload endpoint
@document_api.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document."""
    temp_path = None
    temp_dir = None
    try:
        # Check if document was provided
        if 'file' not in request.files:
            return error_response('No file part in the request', 400)

        file = request.files['file']
        if file.filename == '':
            return error_response('No file selected', 400)

        # Get language preference (default to auto-detection)
        language_preference = request.form.get('language', 'auto')

        # Create secure filename and save to temporary location
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        # Debugging: Log the detected extension
        print(f"Initial detected extension: {file_ext} for file {filename}")

        # If extension is missing, try to determine from MIME type
        if not file_ext:
            print(f"No extension found, checking MIME type: {file.content_type}")
            if file.content_type == 'application/pdf':
                file_ext = '.pdf'
            elif file.content_type in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
                file_ext = '.xlsx'
            elif file.content_type == 'text/csv':
                file_ext = '.csv'
            print(f"Extension determined from MIME type: {file_ext}")

        # Validate file extension (after potentially getting it from MIME type)
        allowed_extensions = {'.pdf', '.xlsx', '.xls', '.csv'}
        if file_ext not in allowed_extensions:
            return error_response(
                f'File type not supported. Allowed types: {", ".join(allowed_extensions)}',
                400
            )

        # Generate unique ID for this document
        document_id = str(uuid.uuid4())

        # Save file to temporary location
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        logger.info(f"Document saved to temporary location: {temp_path}")

        # Initialize document processor with configuration
        processor_config = document_processor_config.copy()
        processor_config['language'] = language_preference
        processor = DocumentProcessor(config=processor_config)

        # Process document
        processing_result = processor.process_document(temp_path)

        # Check for processing errors before proceeding
        if "error" in processing_result:
             logger.error(f"Document processing failed for {filename}: {processing_result['error']}")
             return error_response(f"Processing failed: {processing_result['error']}", 500)


        # Save file to permanent location (using configured UPLOAD_FOLDER)
        # Ensure UPLOAD_FOLDER is correctly imported or accessed via app.config
        upload_dir = UPLOAD_FOLDER # Use imported UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        permanent_path = os.path.join(upload_dir, f"{document_id}{file_ext}")

        # Copy file from temp to permanent location
        try:
            # Use shutil for potentially more robust copy
            import shutil
            shutil.copy2(temp_path, permanent_path)
            logger.info(f"Copied temp file {temp_path} to {permanent_path}")

            # Add file path to result metadata
            if 'metadata' not in processing_result:
                 processing_result['metadata'] = {}
            processing_result['metadata']['file_path'] = permanent_path # Store relative path? Or absolute? Decide convention.
            processing_result['metadata']['file_size_bytes'] = os.path.getsize(permanent_path)

        except Exception as e:
            logger.error(f"Error saving file to permanent location {permanent_path}: {str(e)}")
            # Decide if this is a critical error or if we can proceed without the permanent file
            return error_response(f"Could not save file permanently: {str(e)}", 500)


        # Add document ID and metadata
        processing_result['_id'] = document_id # Use generated UUID as MongoDB _id
        processing_result['metadata']['upload_date'] = datetime.datetime.now(datetime.timezone.utc).isoformat() # Use UTC
        processing_result['metadata']['original_filename'] = filename

        # Save results to database
        try:
            db = get_db()
            db.documents.insert_one(processing_result)
            logger.info(f"Processing results for document {document_id} saved to database.")
        except Exception as e:
            logger.error(f"Error saving to database for document {document_id}: {str(e)}")
            # Consider if we should delete the permanent file if DB save fails
            return error_response(f"Failed to save document metadata to database: {str(e)}", 500)

        # Return success response with document ID and key metadata
        return success_response(
            data={
                'document_id': document_id,
                'filename': filename,
                'page_count': processing_result.get('metadata', {}).get('page_count', 0),
                # Ensure tables_data exists and is iterable before calculating count
                'tables_count': sum(len(tables) for tables in processing_result.get('tables', {}).values() if isinstance(tables, list)),
                'language': processing_result.get('metadata', {}).get('language', 'unknown')
            },
            message='Document processed and saved successfully'
        )

    except Exception as e:
        logger.exception(f"Unhandled error during document upload: {str(e)}") # Use logger.exception for traceback
        return error_response(f"An unexpected error occurred during upload: {str(e)}", 500)
    finally:
        # Clean up temporary file and directory
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file {temp_path}: {str(e)}")
        if temp_dir and os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")


# Document retrieval endpoint
@document_api.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Retrieve processed document data."""
    try:
        # Get document from database
        db = get_db()
        # Exclude large fields like full text unless specifically requested?
        document = db.documents.find_one({"_id": document_id}) # Consider projection

        if not document:
            return error_response('Document not found', 404)

        # Convert ObjectId to string for JSON serialization - _id is already string here
        # if '_id' in document and not isinstance(document['_id'], str):
        #     document['_id'] = str(document['_id'])

        return success_response(
            data=document,
            message='Document retrieved successfully'
        )

    except ConnectionError as e:
         logger.error(f"Database connection error retrieving document {document_id}: {str(e)}")
         return error_response(f"Database connection error: {str(e)}", 503) # Service Unavailable
    except Exception as e:
        logger.exception(f"Error retrieving document {document_id}: {str(e)}")
        return error_response(f"Error retrieving document: {str(e)}", 500)

# Documents listing endpoint
# Added 's' to the route as per frontend api client
@document_api.route('/s', methods=['GET'])
def get_documents():
    """Get all documents."""
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit

        # Query database
        db = get_db()
        # Project only necessary fields for listing
        documents = list(db.documents.find({}, {
            "_id": 1,
            "metadata.original_filename": 1,
            "metadata.upload_date": 1,
            "metadata.page_count": 1,
            "metadata.language": 1,
            "metadata.processing_status": 1
        }).sort("metadata.upload_date", -1).skip(skip).limit(limit))

        # Format data for response (extract metadata)
        formatted_docs = []
        for doc in documents:
             # Ensure metadata exists before accessing
             metadata = doc.get('metadata', {})
             formatted_docs.append({
                 "id": doc['_id'], # Use _id as id
                 "filename": metadata.get('original_filename', 'N/A'),
                 "upload_date": metadata.get('upload_date', 'N/A'),
                 "page_count": metadata.get('page_count', 0),
                 "language": metadata.get('language', 'unknown'),
                 "status": metadata.get('processing_status', 'unknown')
             })


        # Get total count for pagination info (optional)
        total_documents = db.documents.count_documents({})

        return success_response(
            data={
                "documents": formatted_docs,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_documents,
                    "pages": (total_documents + limit - 1) // limit # Calculate total pages
                }
            },
            message='Documents retrieved successfully'
        )

    except ConnectionError as e:
         logger.error(f"Database connection error retrieving documents: {str(e)}")
         return error_response(f"Database connection error: {str(e)}", 503)
    except Exception as e:
        logger.exception(f"Error retrieving documents: {str(e)}")
        return error_response(f"Error retrieving documents: {str(e)}", 500)

# Table data endpoint
@document_api.route('/<document_id>/tables', methods=['GET'])
def get_document_tables(document_id):
    """Get tables extracted from document."""
    try:
        # Get document from database, projecting only the tables field
        db = get_db()
        document = db.documents.find_one({"_id": document_id}, {"tables": 1})

        if not document:
            return error_response('Document not found', 404)

        tables = document.get('tables', {})

        # Check if tables data is empty or indicates errors
        if not tables or all(isinstance(t, dict) and "error" in t for page_tables in tables.values() for t in page_tables):
             # Consider returning success with empty data vs. 404 if no tables were found vs. errors
             return success_response(data={}, message='No valid tables found or table extraction failed for this document')


        return success_response(
            data=tables,
            message='Tables retrieved successfully'
        )

    except ConnectionError as e:
         logger.error(f"Database connection error retrieving tables for {document_id}: {str(e)}")
         return error_response(f"Database connection error: {str(e)}", 503)
    except Exception as e:
        logger.exception(f"Error retrieving tables for document {document_id}: {str(e)}")
        return error_response(f"Error retrieving tables: {str(e)}", 500)

# Financial data endpoint
@document_api.route('/<document_id>/financial', methods=['GET'])
def get_financial_data(document_id):
    """Get financial data extracted from document."""
    try:
        # Get document from database, projecting only financial data
        db = get_db()
        document = db.documents.find_one({"_id": document_id}, {"financial_data": 1})

        if not document:
            return error_response('Document not found', 404)

        financial_data = document.get('financial_data', {})

        if not financial_data or not any(financial_data.values()): # Check if financial data is empty
            return success_response(data={}, message='No financial data extracted for this document')


        return success_response(
            data=financial_data,
            message='Financial data retrieved successfully'
        )

    except ConnectionError as e:
         logger.error(f"Database connection error retrieving financial data for {document_id}: {str(e)}")
         return error_response(f"Database connection error: {str(e)}", 503)
    except Exception as e:
        logger.exception(f"Error retrieving financial data for document {document_id}: {str(e)}")
        return error_response(f"Error retrieving financial data: {str(e)}", 500)

# Document question endpoint
@document_api.route('/<document_id>/question', methods=['POST'])
def ask_document_question(document_id):
    """Ask a question about a document."""
    # Note: This requires a proper QA service implementation
    try:
        # Get question from request
        data = request.get_json()
        if not data or 'question' not in data:
            return error_response('No question provided', 400)

        question = data['question']

        # Placeholder: In a real app, call a QA service here
        # e.g., from services.question_service import process_document_question
        # answer = process_document_question(document_id, question)

        # Simple placeholder response for now
        logger.warning(f"Question endpoint called for doc {document_id}, but QA service is not implemented.")
        answer = {
            "question": question,
            "response": "Placeholder: Advanced question answering is not yet implemented.",
            "sources": []
        }

        return success_response(
            data=answer,
            message='Question received (placeholder response)'
        )

    except Exception as e:
        logger.exception(f"Error processing question for document {document_id}: {str(e)}")
        return error_response(f"Error processing question: {str(e)}", 500)