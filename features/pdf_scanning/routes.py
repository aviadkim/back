from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from . import pdf_scanning_bp
from .service import process_pdf_document, get_all_documents, get_document_by_id, delete_document

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pdf_scanning_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    Upload and process a PDF document
    ---
    post:
      summary: Upload and process a PDF document
      description: Endpoint for uploading PDF documents for processing
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                language:
                  type: string
                  enum: [he, en]
                  default: he
      responses:
        200:
          description: Document uploaded and processed successfully
        400:
          description: Bad request (no file or invalid file)
        500:
          description: Server error
    """
    try:
        # Check if file part exists in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        # Check if a file was selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if the file is a PDF
        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Get language from form data (default to Hebrew)
        language = request.form.get('language', 'he')
        
        # Secure the filename and save the file
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        logger.info(f"PDF file saved to {file_path}")
        
        # Process the PDF
        document_id, document_data = process_pdf_document(file_path, language)
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded and processed successfully',
            'document_id': document_id,
            'filename': filename,
            'data': document_data
        })
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return jsonify({'error': f'Error processing PDF: {str(e)}'}), 500

@pdf_scanning_bp.route('/documents', methods=['GET'])
def list_documents():
    """
    List all processed documents
    ---
    get:
      summary: List all processed documents
      description: Returns a list of all processed documents
      responses:
        200:
          description: List of documents
    """
    try:
        documents = get_all_documents()
        return jsonify({'documents': documents})
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({'error': f'Error listing documents: {str(e)}'}), 500

@pdf_scanning_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    Get a specific document by ID
    ---
    get:
      summary: Get document details
      description: Returns details of a specific document
      parameters:
        - name: document_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Document details
        404:
          description: Document not found
    """
    try:
        document = get_document_by_id(document_id)
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        return jsonify({'document': document})
    except Exception as e:
        logger.error(f"Error retrieving document: {str(e)}")
        return jsonify({'error': f'Error retrieving document: {str(e)}'}), 500

@pdf_scanning_bp.route('/documents/<document_id>', methods=['DELETE'])
def remove_document(document_id):
    """
    Delete a document by ID
    ---
    delete:
      summary: Delete a document
      description: Deletes a document and its associated data
      parameters:
        - name: document_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Document deleted successfully
        404:
          description: Document not found
    """
    try:
        success = delete_document(document_id)
        if not success:
            return jsonify({'error': 'Document not found'}), 404
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': f'Error deleting document: {str(e)}'}), 500
