from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
import logging
from pathlib import Path

# Import configuration
from config.configuration import document_processor_config, MAX_FILE_SIZE

# Import services
from services.document_service import save_document_results, get_document_by_id
from services.table_service import get_tables_by_document
from services.financial_service import get_financial_data_by_document
from services.question_service import process_document_question

# Import processor
from pdf_processor import DocumentProcessor

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

# Document upload endpoint
@document_api.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document."""
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

        # Validate file extension
        allowed_extensions = {'.pdf', '.xlsx', '.xls', '.csv'}
        if file_ext not in allowed_extensions:
            return error_response(
                f'File type not supported. Allowed types: {", ".join(allowed_extensions)}',
                400
            )

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell() / (1024 * 1024)  # in MB
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return error_response(f'File too large. Maximum size is {MAX_FILE_SIZE}MB', 400)

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

        # Save results to database
        db_result = save_document_results(document_id, processing_result)

        # Clean up temporary file
        try:
            os.remove(temp_path)
            os.rmdir(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {str(e)}")

        # Return success response with document ID
        return success_response(
            data={
                'document_id': document_id,
                'filename': filename,
                'page_count': processing_result.get('metadata', {}).get('page_count', 0),
                'tables_count': sum(len(tables) for tables in processing_result.get('tables', {}).values()),
                'language': processing_result.get('metadata', {}).get('language', 'unknown')
            },
            message='Document processed successfully'
        )

    except Exception as e:
        logger.error(f"Error processing document upload: {str(e)}")
        return error_response(f"Error processing document: {str(e)}", 500)

# Document retrieval endpoint
@document_api.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Retrieve processed document data."""
    try:
        # Get document from database
        document = get_document_by_id(document_id)

        if not document:
            return error_response('Document not found', 404)

        return success_response(
            data=document,
            message='Document retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        return error_response(f"Error retrieving document: {str(e)}", 500)

# Table data endpoint
@document_api.route('/<document_id>/tables', methods=['GET'])
def get_document_tables(document_id):
    """Get tables extracted from document."""
    try:
        # Get table data from database
        tables = get_tables_by_document(document_id)

        if not tables:
            return error_response('No tables found for this document', 404)

        return success_response(
            data=tables,
            message='Tables retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error retrieving tables for document {document_id}: {str(e)}")
        return error_response(f"Error retrieving tables: {str(e)}", 500)

# Financial data endpoint
@document_api.route('/<document_id>/financial', methods=['GET'])
def get_financial_data(document_id):
    """Get financial data extracted from document."""
    try:
        # Get financial data from database
        financial_data = get_financial_data_by_document(document_id)

        if not financial_data:
            return error_response('No financial data found for this document', 404)

        return success_response(
            data=financial_data,
            message='Financial data retrieved successfully'
        )

    except Exception as e:
        logger.error(f"Error retrieving financial data for document {document_id}: {str(e)}")
        return error_response(f"Error retrieving financial data: {str(e)}", 500)

# Document question endpoint
@document_api.route('/<document_id>/question', methods=['POST'])
def ask_document_question(document_id):
    """Ask a question about a document."""
    try:
        # Get question from request
        data = request.get_json()
        if not data or 'question' not in data:
            return error_response('No question provided', 400)

        question = data['question']

        # Process question
        answer = process_document_question(document_id, question)

        return success_response(
            data=answer,
            message='Question processed successfully'
        )

    except Exception as e:
        logger.error(f"Error processing question for document {document_id}: {str(e)}")
        return error_response(f"Error processing question: {str(e)}", 500)