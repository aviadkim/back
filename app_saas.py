import os
from flask import Flask, jsonify, request, send_from_directory
import logging
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Load configurations
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['EXTRACTION_FOLDER'] = os.getenv('EXTRACTION_FOLDER', 'extractions')
app.config['ENHANCED_FOLDER'] = os.getenv('ENHANCED_FOLDER', 'enhanced_extractions')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development_secret_key')
app.config['JWT_EXPIRATION_HOURS'] = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXTRACTION_FOLDER'], exist_ok=True)
os.makedirs(app.config['ENHANCED_FOLDER'], exist_ok=True)

# Import MongoDB connection
from mongodb.connection import get_db_collections
db, collections = get_db_collections()

# Import authentication
from auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Import enhanced financial extractor
from enhanced_financial_extractor import EnhancedFinancialExtractor

# Utility functions
def get_document_path(document_id):
    """Get path to a document file"""
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.startswith(f"{document_id}_") or filename == f"{document_id}.pdf":
            return os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return None

def get_extraction_path(document_id):
    """Get path to an extraction file"""
    extraction_path = os.path.join(app.config['EXTRACTION_FOLDER'], f"{document_id}_extraction.json")
    return extraction_path

def get_enhanced_path(document_id):
    """Get path to an enhanced extraction file"""
    enhanced_path = os.path.join(app.config['ENHANCED_FOLDER'], f"{document_id}_enhanced.json")
    return enhanced_path

# API Routes
@app.route('/health')
def health_check():
    """Check system health"""
    return jsonify({
        'status': 'ok',
        'message': 'System is operational'
    })

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """Upload and process a document"""
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get language
    language = request.form.get('language', 'heb+eng')
    
    # Generate unique ID
    from uuid import uuid4
    document_id = f"doc_{uuid4().hex[:8]}"
    
    # Save file
    filename = f"{document_id}_{file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    # Create document record in MongoDB
    document = {
        'document_id': document_id,
        'filename': filename,
        'upload_date': datetime.now(),
        'status': 'processing',
        'language': language,
        'user_id': 'system',  # Will be replaced with actual user ID in authenticated version
        'file_path': file_path,
        'extraction_path': '',
        'page_count': 0,
        'content': '',
        'metadata': {}
    }
    
    collections['documents'].insert_one(document)
    
    # Process document (this would be moved to a background task in production)
    try:
        # Import document processing here to avoid circular imports
        from document_processor import process_document
        result = process_document(document_id, file_path, language)
        
        # Update document record
        collections['documents'].update_one(
            {'document_id': document_id},
            {'$set': {
                'status': 'completed',
                'extraction_path': get_extraction_path(document_id),
                'page_count': result.get('page_count', 0),
                'content': result.get('content', '')[:1000],  # Store first 1000 chars of content
            }}
        )
        
        # Extract financial data
        extractor = EnhancedFinancialExtractor()
        financial_data = extractor.process_document(document_id)
        
        if financial_data:
            # Store in MongoDB
            financial_data['document_id'] = document_id
            financial_data['extracted_at'] = datetime.now()
            collections['financial_data'].insert_one(financial_data)
        
        return jsonify({
            'document_id': document_id,
            'filename': filename,
            'status': 'completed',
            'language': language,
            'page_count': result.get('page_count', 0),
            'isin_count': len(financial_data.get('isins', [])) if financial_data else 0,
            'table_count': len(financial_data.get('tables', [])) if financial_data else 0,
            'message': 'Document uploaded and processed successfully'
        })
    
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        
        # Update document status to error
        collections['documents'].update_one(
            {'document_id': document_id},
            {'$set': {'status': 'error'}}
        )
        
        return jsonify({
            'document_id': document_id,
            'filename': filename,
            'status': 'error',
            'error': str(e),
            'message': 'Document upload failed during processing'
        }), 500

@app.route('/api/documents')
def list_documents():
    """List all documents"""
    documents = []
    
    for doc in collections['documents'].find():
        documents.append({
            'document_id': doc['document_id'],
            'filename': doc['filename'],
            'status': doc['status'],
            'upload_date': doc['upload_date'].isoformat() if isinstance(doc['upload_date'], datetime) else doc['upload_date']
        })
    
    return jsonify({'documents': documents})

@app.route('/api/documents/<document_id>')
def get_document(document_id):
    """Get document details"""
    document = collections['documents'].find_one({'document_id': document_id})
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify({
        'document_id': document['document_id'],
        'filename': document['filename'],
        'status': document['status'],
        'language': document['language'],
        'upload_date': document['upload_date'].isoformat() if isinstance(document['upload_date'], datetime) else document['upload_date'],
        'page_count': document['page_count']
    })

@app.route('/api/documents/<document_id>/content')
def get_document_content(document_id):
    """Get document content"""
    document = collections['documents'].find_one({'document_id': document_id})
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Get content from extraction file
    extraction_path = document.get('extraction_path') or get_extraction_path(document_id)
    
    if not os.path.exists(extraction_path):
        return jsonify({'error': 'Content not found'}), 404
    
    try:
        with open(extraction_path, 'r') as f:
            extraction_data = json.load(f)
            content = extraction_data.get('content', '')
            pages = extraction_data.get('pages', [])
    except Exception as e:
        logger.error(f"Error reading extraction data: {e}")
        return jsonify({'error': 'Error reading content'}), 500
    
    return jsonify({
        'document_id': document_id,
        'content': content,
        'pages': pages
    })

@app.route('/api/documents/<document_id>/financial')
def get_document_financial(document_id):
    """Get financial data extracted from a document"""
    financial_data = collections['financial_data'].find_one({'document_id': document_id})
    
    if not financial_data:
        # Try to get from file
        enhanced_path = get_enhanced_path(document_id)
        
        if os.path.exists(enhanced_path):
            try:
                with open(enhanced_path, 'r') as f:
                    financial_data = json.load(f)
            except Exception as e:
                logger.error(f"Error reading enhanced extraction: {e}")
        
        if not financial_data:
            return jsonify({'error': 'Financial data not found'}), 404
    
    # Remove MongoDB _id if present
    if '_id' in financial_data:
        financial_data.pop('_id')
    
    return jsonify(financial_data)

@app.route('/api/documents/<document_id>/tables')
def get_document_tables(document_id):
    """Get tables extracted from a document"""
    financial_data = collections['financial_data'].find_one({'document_id': document_id})
    
    if not financial_data:
        # Try to get from file
        enhanced_path = get_enhanced_path(document_id)
        
        if os.path.exists(enhanced_path):
            try:
                with open(enhanced_path, 'r') as f:
                    financial_data = json.load(f)
            except Exception as e:
                logger.error(f"Error reading enhanced extraction: {e}")
        
        if not financial_data:
            return jsonify({
                'tables': [],
                'document_id': document_id,
                'table_count': 0
            })
    
    tables = financial_data.get('tables', [])
    
    return jsonify({
        'tables': tables,
        'document_id': document_id,
        'table_count': len(tables)
    })

@app.route('/api/documents/<document_id>/advanced_analysis')
def get_document_advanced_analysis(document_id):
    """Get advanced analysis for a document"""
    # Check if analysis exists in MongoDB
    analysis = collections['analytics'].find_one({
        'document_id': document_id,
        'type': 'portfolio_analysis'
    })
    
    if not analysis:
        # Generate analysis
        from enhanced_financial_extractor import analyze_portfolio
        
        analysis_result = analyze_portfolio(document_id)
        
        # Store in MongoDB
        analysis = {
            'document_id': document_id,
            'user_id': 'system',
            'type': 'portfolio_analysis',
            'parameters': {},
            'results': analysis_result,
            'created_at': datetime.now()
        }
        
        collections['analytics'].insert_one(analysis)
        
        analysis_result = analysis['results']
    else:
        analysis_result = analysis['results']
    
    return jsonify({
        'document_id': document_id,
        'analysis': analysis_result
    })

@app.route('/api/documents/<document_id>/custom_table')
def generate_document_custom_table(document_id):
    """Generate a custom table from document data"""
    columns = request.args.get('columns', 'isin,name,currency')
    columns = columns.split(',')
    
    # Generate custom table
    from enhanced_financial_extractor import generate_custom_table
    
    table_result = generate_custom_table(document_id, columns)
    
    return jsonify(table_result)

@app.route('/api/qa/ask', methods=['POST'])
def ask_question():
    """Ask a question about a document"""
    data = request.get_json()
    
    if not data or 'document_id' not in data or 'question' not in data:
        return jsonify({'error': 'Missing document_id or question'}), 400
    
    document_id = data['document_id']
    question = data['question']
    
    # Get document
    document = collections['documents'].find_one({'document_id': document_id})
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Get content
    extraction_path = document.get('extraction_path') or get_extraction_path(document_id)
    
    if not os.path.exists(extraction_path):
        return jsonify({'error': 'Document content not found'}), 404
    
    try:
        with open(extraction_path, 'r') as f:
            extraction_data = json.load(f)
            content = extraction_data.get('content', '')
    except Exception as e:
        logger.error(f"Error reading extraction data: {e}")
        return jsonify({'error': 'Error reading document content'}), 500
    
    # Get financial data
    financial_data = collections['financial_data'].find_one({'document_id': document_id})
    
    if not financial_data:
        # Try to get from file
        enhanced_path = get_enhanced_path(document_id)
        
        if os.path.exists(enhanced_path):
            try:
                with open(enhanced_path, 'r') as f:
                    financial_data = json.load(f)
            except Exception as e:
                logger.error(f"Error reading enhanced extraction: {e}")
    
    # Import document QA engine
    from document_qa import DocumentQA
    
    qa_engine = DocumentQA()
    answer = qa_engine.answer_question(question, content, financial_data)
    
    return jsonify({
        'document_id': document_id,
        'question': question,
        'answer': answer
    })

# Serve frontend
@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=''):
    """Serve frontend"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'build')
    
    if path == '':
        return send_from_directory(frontend_path, 'index.html')
    
    # Check if file exists
    file_path = os.path.join(frontend_path, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(frontend_path, path)
    
    # If not found, return index.html for client-side routing
    return send_from_directory(frontend_path, 'index.html')

# Document processor placeholder (to be implemented in a separate file)
class document_processor:
    @staticmethod
    def process_document(document_id, file_path, language):
        """Process document and extract text"""
        logger.info(f"Processing document: {document_id}")
        
        # This is a placeholder for the actual document processing logic
        # In a real implementation, this would use OCR and text extraction
        
        result = {
            'document_id': document_id,
            'file_path': file_path,
            'language': language,
            'page_count': 1,
            'content': f"Sample content for document {document_id}"
        }
        
        # Save extraction result
        extraction_path = get_extraction_path(document_id)
        os.makedirs(os.path.dirname(extraction_path), exist_ok=True)
        
        with open(extraction_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result

# Document QA engine placeholder (to be implemented in a separate file)
class DocumentQA:
    def answer_question(self, question, content, financial_data):
        """Answer a question about a document"""
        # This is a placeholder for the actual QA logic
        # In a real implementation, this would use NLP and context understanding
        
        if "ISIN" in question or "isin" in question:
            isins = financial_data.get('isins', []) if financial_data else []
            if isins:
                return f"I found these potential ISIN numbers: {', '.join(isins[:10])}{' and more' if len(isins) > 10 else ''}"
            else:
                return "I couldn't find any ISIN numbers in the document."
        
        return f"I don't have a specific answer to that question based on the document content."

if __name__ == '__main__':
    # Import datetime for MongoDB documents
    from datetime import datetime
    
    # Run the app
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
