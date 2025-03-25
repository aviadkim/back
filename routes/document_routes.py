from flask import Blueprint, request, jsonify, current_app, send_file
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import json

from models.document_models import Document, db
from services.document_service import process_document, analyze_document
from utils.pdf_processor import PDFProcessor
from agent_framework.memory_agent import MemoryAgent
from agent_framework.coordinator import AgentCoordinator

# Create the blueprint
document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

# Create agent instances
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@document_bp.route('', methods=['GET'])
def get_documents():
    """Get all documents"""
    try:
        documents = Document.query.order_by(Document.created_at.desc()).all()
        result = []
        
        for doc in documents:
            result.append({
                'id': doc.id,
                'title': doc.title,
                'file_name': doc.file_name,
                'document_type': doc.document_type,
                'status': doc.status,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'language': doc.language,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
            })
        
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_bp.route('', methods=['POST'])
def upload_document():
    """Upload a new document"""
    try:
        # Check if file is in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        
        # Check if file is empty
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Supported formats: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Get form data
        title = request.form.get('title', file.filename)
        document_type = request.form.get('documentType', 'other')
        language = request.form.get('language', 'he')
        processing_mode = request.form.get('processingMode', 'standard')
        
        # Generate unique ID and save file
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()
        
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file path
        file_path = os.path.join(uploads_dir, f"{document_id}.{file_extension}")
        file.save(file_path)
        
        # Get file size and metadata
        file_size = os.path.getsize(file_path)
        
        # Create document record
        document = Document(
            id=document_id,
            title=title,
            file_name=filename,
            file_path=file_path,
            file_type=file_extension,
            file_size=file_size,
            document_type=document_type,
            language=language,
            status='processing',
        )
        
        db.session.add(document)
        db.session.commit()
        
        # Process document in a background task
        current_app.tasks.add_task(
            process_document,
            document_id=document_id,
            file_path=file_path,
            language=language,
            processing_mode=processing_mode
        )
        
        return jsonify({
            'id': document.id,
            'title': document.title,
            'file_name': document.file_name,
            'document_type': document.document_type,
            'status': document.status,
            'file_size': document.file_size,
            'language': document.language,
            'created_at': document.created_at.isoformat(),
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error uploading document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get a document by ID"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Load analysis data if it exists
        analysis = None
        if document.analysis_path and os.path.exists(document.analysis_path):
            with open(document.analysis_path, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
        
        result = {
            'id': document.id,
            'title': document.title,
            'file_name': document.file_name,
            'document_type': document.document_type,
            'status': document.status,
            'file_size': document.file_size,
            'page_count': document.page_count,
            'language': document.language,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat() if document.updated_at else None,
            'analysis': analysis
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_bp.route('/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Delete the file
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            
        # Delete analysis file if it exists
        if document.analysis_path and os.path.exists(document.analysis_path):
            os.remove(document.analysis_path)
            
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        # Remove from memory agent
        memory_agent.forget_document(document_id)
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_bp.route('/<document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download the original document"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        if not document.file_path or not os.path.exists(document.file_path):
            return jsonify({'error': 'Document file not found'}), 404
            
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.file_name
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_bp.route('/<document_id>/analyze', methods=['POST'])
def analyze_document_endpoint(document_id):
    """Analyze a document"""
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Get request data
        data = request.json or {}
        force = data.get('force', False)
        
        # Check if analysis already exists and force is not true
        if document.analysis_path and os.path.exists(document.analysis_path) and not force:
            with open(document.analysis_path, 'r', encoding='utf-8') as f:
                analysis = json.load(f)
                return jsonify(analysis), 200
        
        # Set document status to processing
        document.status = 'processing'
        db.session.commit()
        
        # Start analysis in a background task
        current_app.tasks.add_task(
            analyze_document,
            document_id=document_id,
            force=force
        )
        
        return jsonify({
            'success': True, 
            'message': 'Document analysis started'
        }), 202
        
    except Exception as e:
        current_app.logger.error(f"Error analyzing document {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
