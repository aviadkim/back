"""
Routes for PDF Scanning Feature
"""

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from . import pdf_scanning_bp
from .service import process_pdf_document, get_all_documents, get_document_by_id, delete_document

@pdf_scanning_bp.route('/api/pdf/upload', methods=['POST'])
def upload_pdf():
    """Upload and process a PDF document"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file part'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No selected file'
            }), 400
            
        if file and file.filename.lower().endswith('.pdf'):
            filename = secure_filename(file.filename)
            upload_folder = os.environ.get('UPLOAD_FOLDER', 'uploads')
            
            # Ensure the upload folder exists
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Process the PDF
            result = process_pdf_document(file_path)
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded and processed successfully',
                'document_id': result['document_id'],
                'filename': filename,
                'details': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'File must be a PDF'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@pdf_scanning_bp.route('/api/pdf/documents', methods=['GET'])
def get_documents():
    """Get all documents"""
    try:
        documents = get_all_documents()
        
        return jsonify({
            'status': 'success',
            'documents': documents
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@pdf_scanning_bp.route('/api/pdf/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a specific document"""
    try:
        document = get_document_by_id(document_id)
        
        if not document:
            return jsonify({
                'status': 'error',
                'message': 'Document not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'document': document
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@pdf_scanning_bp.route('/api/pdf/documents/<document_id>', methods=['DELETE'])
def remove_document(document_id):
    """Delete a document"""
    try:
        result = delete_document(document_id)
        
        if not result:
            return jsonify({
                'status': 'error',
                'message': 'Document not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Document deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
