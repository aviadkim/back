from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import os
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
document_api = Blueprint('document_api', __name__, url_prefix='/api/documents')

@document_api.route('', methods=['GET'])
def list_documents():
    """List all documents"""
    try:
        # In a real app, this would fetch from a database
        return jsonify({
            "documents": [
                {"id": "doc_1", "name": "Example Document 1", "status": "completed"},
                {"id": "doc_2", "name": "Example Document 2", "status": "processing"}
            ]
        })
    except Exception as e:
        logger.exception(f"Error listing documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

@document_api.route('/upload', methods=['POST'])
def upload_document():
    """Upload a document for processing"""
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            # Get language parameter with default
            language = request.form.get('language', 'eng')
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            # Generate unique document ID
            document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Document uploaded successfully: {filename}, ID: {document_id}")
            
            # Return success response
            return jsonify({
                "message": "Document uploaded successfully",
                "document_id": document_id,
                "filename": filename,
                "language": language,
                "status": "pending"
            }), 200
    except Exception as e:
        logger.exception(f"Error processing upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@document_api.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details and status"""
    try:
        # In a real application, you would fetch this from a database
        # For demo purposes, just return a mock response
        return jsonify({
            "document_id": document_id,
            "status": "completed",
            "filename": f"{document_id}.pdf",
            "upload_date": "2025-04-01T12:00:00Z",
            "pages": 5,
            "language": "heb+eng"
        }), 200
    except Exception as e:
        logger.exception(f"Error getting document: {str(e)}")
        return jsonify({"error": str(e)}), 500
