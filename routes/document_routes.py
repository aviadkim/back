from flask import Blueprint, request, jsonify, current_app, send_file
import os
from werkzeug.utils import secure_filename
from services.document_service import DocumentService

document_bp = Blueprint('document', __name__, url_prefix='/api')
document_service = DocumentService()

@document_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    Endpoint for uploading a document
    Returns 400 if no file is provided
    """
    # Validate request has files
    if not request.files:
        return jsonify({"error": "No file provided"}), 400
        
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    
    # Validate filename
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    
    # Validate file extension
    allowed_extensions = {'pdf', 'doc', 'docx', 'xlsx', 'xls'}
    if '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "File type not allowed"}), 400
    
    language = request.form.get('language', os.environ.get('DEFAULT_LANGUAGE', 'he'))
    
    try:
        result = document_service.process_document(file, language)
        return jsonify(result), 201
    except Exception as e:
        current_app.logger.error(f"Error processing document: {str(e)}")
        return jsonify({"error": "Failed to process document"}), 500

@document_bp.route('/documents', methods=['GET'])
def get_documents():
    """
    Endpoint for retrieving all documents
    """
    try:
        documents = document_service.get_all_documents()
        return jsonify({"documents": documents}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document with extracted data"""
    try:
        document = document_service.get_document(document_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
            
        # Include extracted data and text content
        document.update({
            'extractedData': document_service.get_extracted_data(document_id),
            'text_content': document_service.get_document_text_content(document_id)
        })
        return jsonify(document), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@document_bp.route('/documents/<document_id>/file', methods=['GET'])
def get_document_file(document_id):
    """Get the original document file"""
    try:
        file_path = document_service.get_document_file_path(document_id)
        return send_file(file_path)
    except Exception as e:
        current_app.logger.error(f"Error retrieving document file: {str(e)}")
        return jsonify({"error": "Failed to retrieve document file"}), 500

@document_bp.route('/documents/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download the original document file"""
    try:
        file_path = document_service.get_document_file_path(document_id)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Error downloading document: {str(e)}")
        return jsonify({"error": "Failed to download document"}), 500

@document_bp.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        document_service.delete_document(document_id)
        return jsonify({"message": "Document deleted successfully"}), 200
    except Exception as e:
        current_app.logger.error(f"Error deleting document: {str(e)}")
        return jsonify({"error": "Failed to delete document"}), 500

@document_bp.route('/documents/<document_id>/raw', methods=['GET'])
def get_document_raw_text(document_id):
    """Get raw text content of document"""
    try:
        text_content = document_service.get_document_text_content(document_id)
        return jsonify({"text_content": text_content}), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving document text: {str(e)}")
        return jsonify({"error": "Failed to retrieve document text"}), 500
