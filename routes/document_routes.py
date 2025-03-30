from flask import Blueprint, request, jsonify, current_app, send_file
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import json

# Assuming models.document_models only defines the structure conceptually now
# from models.document_models import Document
from shared.database import db  # Import DynamoDB connector
# Assuming these services are adapted or will be adapted for DynamoDB interaction if needed
from services.document_service import process_document, analyze_document
# Utils and agents likely don't interact directly with db object
from utils.pdf_processor import PDFProcessor
from agent_framework.memory_agent import MemoryAgent
from agent_framework.coordinator import AgentCoordinator

# Create the blueprint
# Note: Renamed blueprint variable to avoid conflict with imported 'document_routes' if run as script
document_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

# Create agent instances (assuming these don't need db passed in)
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'csv'}

# --- Helper Function ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@document_bp.route('', methods=['GET'])
def get_documents():
    """Get all documents from DynamoDB."""
    try:
        # Use the appropriate method from your DynamoDB connector
        # Assuming db.list_documents() scans/queries the table and returns a list of dicts
        documents = db.list_documents("financial_documents") # Assuming table name is 'financial_documents'

        # Format the result for the frontend
        result = []
        for doc in documents:
            result.append({
                'id': doc.get('id'), # Use .get() for safety
                'title': doc.get('title', 'Untitled'),
                'file_name': doc.get('file_name', ''),
                'document_type': doc.get('document_type', 'other'),
                'status': doc.get('status', 'unknown'),
                'file_size': doc.get('file_size', 0),
                'page_count': doc.get('page_count'), # Allow None if not set
                'language': doc.get('language', 'en'),
                'created_at': doc.get('created_at', datetime.utcnow().isoformat()),
                'updated_at': doc.get('updated_at'), # Allow None
            })

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error getting documents: {str(e)}")
        # Consider more specific error handling based on db connector exceptions
        return jsonify({'error': 'Failed to retrieve documents'}), 500

@document_bp.route('', methods=['POST'])
def upload_document():
    """Upload a new document and store metadata in DynamoDB."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

        # Get form data
        title = request.form.get('title', file.filename)
        document_type = request.form.get('documentType', 'other')
        language = request.form.get('language', 'he') # Default to Hebrew based on previous context
        processing_mode = request.form.get('processingMode', 'standard')

        # Generate unique ID and prepare file info
        document_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower()

        # Ensure UPLOAD_FOLDER is configured in Flask app config
        if 'UPLOAD_FOLDER' not in current_app.config:
             current_app.logger.error("UPLOAD_FOLDER not configured in Flask app.")
             return jsonify({'error': 'Server configuration error: Upload folder not set'}), 500

        uploads_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, f"{document_id}.{file_extension}")

        # Save the file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        # Create document item for DynamoDB
        document_item = {
            'id': document_id, # Primary key
            'title': title,
            'file_name': filename,
            'file_path': file_path, # Store path where file is saved
            'file_type': file_extension,
            'file_size': file_size,
            'document_type': document_type,
            'language': language,
            'status': 'uploaded', # Initial status before processing task starts
            'created_at': datetime.now().isoformat(), # Use ISO format string
            'updated_at': datetime.now().isoformat()
            # Add other relevant fields like user_id if available
        }

        # Store metadata in DynamoDB
        # Assuming table name is 'financial_documents'
        stored_id = db.store_document("financial_documents", document_item)
        if not stored_id:
             # Attempt to clean up saved file if DB store fails
             try: os.remove(file_path)
             except OSError: pass
             return jsonify({'error': 'Failed to store document metadata'}), 500

        # Update status after storing, before starting task
        db.update_document("financial_documents", {"id": document_id}, {"status": "processing"})

        # Trigger background processing task (ensure current_app has 'tasks' configured)
        if hasattr(current_app, 'tasks') and callable(getattr(current_app.tasks, 'add_task', None)):
            current_app.tasks.add_task(
                process_document, # The function to run
                document_id=document_id,
                file_path=file_path,
                language=language,
                processing_mode=processing_mode
            )
            current_app.logger.info(f"Background task added for document {document_id}")
        else:
             current_app.logger.warning("Background task runner not configured on current_app. Skipping processing task.")
             # Optionally update status back to 'uploaded' or 'pending_manual_processing'
             db.update_document("financial_documents", {"id": document_id}, {"status": "pending_processing"})


        # Return essential info about the created document record
        return jsonify({
            'id': document_item['id'],
            'title': document_item['title'],
            'file_name': document_item['file_name'],
            'document_type': document_item['document_type'],
            'status': 'processing', # Reflect the status after triggering the task
            'file_size': document_item['file_size'],
            'language': document_item['language'],
            'created_at': document_item['created_at'],
        }), 201 # 201 Created is appropriate

    except Exception as e:
        current_app.logger.exception(f"Error uploading document: {str(e)}") # Log full traceback
        return jsonify({'error': 'An unexpected error occurred during upload'}), 500

@document_bp.route('/<string:document_id>', methods=['GET'])
def get_document(document_id):
    """Get a document by ID from DynamoDB."""
    try:
        # Use DynamoDB find_document
        # Assuming table name is 'financial_documents' and key is {'id': document_id}
        document = db.find_document("financial_documents", {'id': document_id})

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        # Load analysis data if path exists (assuming analysis is stored separately)
        analysis = None
        analysis_path = document.get('analysis_path')
        if analysis_path and os.path.exists(analysis_path):
            try:
                with open(analysis_path, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
            except Exception as json_e:
                 current_app.logger.error(f"Error loading analysis file {analysis_path}: {json_e}")
                 analysis = {"error": "Failed to load analysis data"}


        # Format result for frontend
        result = {
            'id': document.get('id'),
            'title': document.get('title', 'Untitled'),
            'file_name': document.get('file_name', ''),
            'document_type': document.get('document_type', 'other'),
            'status': document.get('status', 'unknown'),
            'file_size': document.get('file_size', 0),
            'page_count': document.get('page_count'),
            'language': document.get('language', 'en'),
            'created_at': document.get('created_at', ''),
            'updated_at': document.get('updated_at'),
            'analysis': analysis # Include loaded analysis data or error
            # Add other fields as needed by the frontend
        }

        return jsonify(result), 200

    except Exception as e:
        current_app.logger.exception(f"Error getting document {document_id}: {str(e)}")
        return jsonify({'error': 'Failed to retrieve document'}), 500

@document_bp.route('/<string:document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a document from DynamoDB and associated files."""
    try:
        # Check if document exists before attempting deletion
        # Assuming table name is 'financial_documents' and key is {'id': document_id}
        document = db.find_document("financial_documents", {'id': document_id})

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        # Delete the physical file(s) first
        file_path = document.get('file_path')
        analysis_path = document.get('analysis_path')

        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                current_app.logger.info(f"Deleted file: {file_path}")
            except OSError as file_e:
                 current_app.logger.error(f"Error deleting file {file_path}: {file_e}")
                 # Decide if this should prevent DB deletion - maybe not?

        if analysis_path and os.path.exists(analysis_path):
            try:
                os.remove(analysis_path)
                current_app.logger.info(f"Deleted analysis file: {analysis_path}")
            except OSError as analysis_e:
                 current_app.logger.error(f"Error deleting analysis file {analysis_path}: {analysis_e}")

        # Delete metadata from DynamoDB
        # Assuming table name is 'financial_documents' and key is {'id': document_id}
        deleted = db.delete_document("financial_documents", {'id': document_id})

        if not deleted:
             # This might happen if the delete operation itself failed, even if the item existed
             current_app.logger.warning(f"DynamoDB delete operation reported failure for document {document_id}, though item might be gone.")
             # Return success anyway as the item is likely gone or inaccessible
             # return jsonify({'error': 'Failed to delete document metadata from database'}), 500

        # Remove from memory agent (if applicable)
        if memory_agent:
             memory_agent.forget_document(document_id)

        return jsonify({'success': True, 'message': 'Document deleted successfully'}), 200

    except Exception as e:
        current_app.logger.exception(f"Error deleting document {document_id}: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during deletion'}), 500

@document_bp.route('/<string:document_id>/download', methods=['GET'])
def download_document(document_id):
    """Download the original document file."""
    try:
        # Use DynamoDB find_document
        # Assuming table name is 'financial_documents' and key is {'id': document_id}
        document = db.find_document("financial_documents", {'id': document_id})

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        file_path = document.get('file_path')
        if not file_path or not os.path.exists(file_path):
            current_app.logger.error(f"Document file path not found or file missing for ID {document_id}. Path: {file_path}")
            return jsonify({'error': 'Document file not found on server'}), 404

        download_name = document.get('file_name', f"document_{document_id}") # Use original filename if available

        return send_file(
            file_path,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        current_app.logger.exception(f"Error downloading document {document_id}: {str(e)}")
        return jsonify({'error': 'Failed to download document'}), 500

@document_bp.route('/<string:document_id>/analyze', methods=['POST'])
def analyze_document_endpoint(document_id):
    """Trigger document analysis (potentially background task)."""
    try:
        # Use DynamoDB find_document
        # Assuming table name is 'financial_documents' and key is {'id': document_id}
        document = db.find_document("financial_documents", {'id': document_id})

        if not document:
            return jsonify({'error': 'Document not found'}), 404

        data = request.json or {}
        force = data.get('force', False)

        # Check if analysis already exists (e.g., based on status or analysis_path)
        # This logic might need refinement based on how 'analyze_document' service works
        analysis_path = document.get('analysis_path')
        current_status = document.get('status')

        if analysis_path and os.path.exists(analysis_path) and not force and current_status == 'completed':
             try:
                 with open(analysis_path, 'r', encoding='utf-8') as f:
                     analysis = json.load(f)
                 return jsonify(analysis), 200 # Return existing analysis
             except Exception as json_e:
                  current_app.logger.error(f"Error reading existing analysis file {analysis_path}: {json_e}")
                  # Proceed to re-analyze if reading fails? Or return error? For now, proceed.

        # Update status to indicate analysis is starting/queued
        update_payload = {
            'status': 'processing',
            'updated_at': datetime.now().isoformat()
        }
        updated = db.update_document("financial_documents", {'id': document_id}, update_payload)

        if not updated:
             current_app.logger.error(f"Failed to update document status to 'processing' for ID {document_id}")
             # Decide if we should still queue the task
             # return jsonify({'error': 'Failed to update document status before analysis'}), 500

        # Trigger background analysis task
        if hasattr(current_app, 'tasks') and callable(getattr(current_app.tasks, 'add_task', None)):
            current_app.tasks.add_task(
                analyze_document, # The function to run
                document_id=document_id,
                force=force
            )
            message = 'Document analysis started'
            status_code = 202 # Accepted
        else:
             current_app.logger.warning("Background task runner not configured. Cannot start analysis task.")
             message = 'Analysis task cannot be started (server configuration)'
             status_code = 501 # Not Implemented (or 503 Service Unavailable)
             # Optionally revert status update if task cannot be queued
             # db.update_document("financial_documents", {'id': document_id}, {'status': document.get('status', 'uploaded')})


        return jsonify({'success': status_code == 202, 'message': message}), status_code

    except Exception as e:
        current_app.logger.exception(f"Error analyzing document {document_id}: {str(e)}")
        # Attempt to set status to failed if possible
        try:
             db.update_document("financial_documents", {'id': document_id}, {'status': 'failed'})
        except Exception as db_e:
             current_app.logger.error(f"Failed to set status to 'failed' after analysis error for {document_id}: {db_e}")
        return jsonify({'error': 'An unexpected error occurred during analysis trigger'}), 500

# Note: Ensure the blueprint is registered in your main app.py:
# from routes.document_routes import document_bp
# app.register_blueprint(document_bp)
