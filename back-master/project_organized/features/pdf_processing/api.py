"""API endpoints for PDF processing feature."""
from flask import Blueprint, request, jsonify
from .processor import EnhancedPDFProcessor
import os
import uuid
from werkzeug.utils import secure_filename

# Create blueprint for this feature
pdf_bp = Blueprint('pdf_processing', __name__, url_prefix='/api/pdf')

def register_routes(app):
    """Register all routes for this feature"""
    app.register_blueprint(pdf_bp)

@pdf_bp.route('/process', methods=['POST'])
def process_document():
    """Process a PDF document and extract its text"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    language = request.form.get('language', 'heb+eng')
    
    # Create processor and process the document
    processor = EnhancedPDFProcessor(language=language)
    
    # Save file to temporary location
    upload_dir = os.path.join('..', '..', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    temp_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
    temp_path = os.path.join(upload_dir, temp_filename)
    
    file.save(temp_path)
    
    # Process the document
    try:
        result_path = processor.process_document(temp_path)
        
        if result_path:
            return jsonify({
                'status': 'success',
                'extraction_path': result_path
            })
        else:
            return jsonify({'error': 'Processing failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
