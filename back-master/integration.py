# integration.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import logging
from werkzeug.utils import secure_filename

# Import your PDF processor components
from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
from pdf_processor.tables.table_extractor import TableExtractor

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize components
text_extractor = PDFTextExtractor()
financial_analyzer = FinancialAnalyzer()
table_extractor = TableExtractor()

# Simple in-memory storage for documents (replace with database in production)
documents = []

@app.route('/api/document/upload', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            # Generate a unique ID
            document_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, f"{document_id}_{filename}")
            file.save(file_path)
            
            # Process the document
            logger.info(f"Processing document: {filename}")
            
            # Extract text
            document_content = text_extractor.extract_document(file_path)
            
            # Extract tables
            tables = table_extractor.extract_tables(file_path, None)
            
            # Check if document is financial
            is_financial = any(
                text_extractor.is_potentially_financial(page_data['text']) 
                for page_data in document_content.values()
            )
            
            # Extract financial metrics if applicable
            financial_metrics = {}
            if is_financial:
                for page_num, page_data in document_content.items():
                    metrics = financial_analyzer.extract_financial_metrics(page_data['text'])
                    if metrics:
                        financial_metrics[f"page_{page_num}"] = metrics
            
            # Store document metadata
            doc_info = {
                'id': document_id,
                'filename': filename,
                'path': file_path,
                'upload_date': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path),
                'page_count': len(document_content),
                'is_financial': is_financial,
                'has_tables': bool(tables),
                'status': 'processed'
            }
            documents.append(doc_info)
            
            return jsonify({
                'message': 'Document processed successfully',
                'document_id': document_id,
                'is_financial': is_financial,
                'financial_metrics': financial_metrics,
                'page_count': len(document_content),
                'has_tables': bool(tables)
            }), 200
            
        except Exception as e:
            logger.exception(f"Error processing document: {str(e)}")
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500
    
    return jsonify({'error': 'Unknown error'}), 500

@app.route('/api/document/list', methods=['GET'])
def list_documents():
    return jsonify(documents), 200

@app.route('/api/document/<document_id>', methods=['GET'])
def get_document(document_id):
    doc = next((d for d in documents if d['id'] == document_id), None)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(doc), 200

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "System is operational"}), 200

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    return send_from_directory('frontend/build', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)