# file: app.py

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
import uuid
import logging
from werkzeug.utils import secure_filename
from datetime import datetime
import tempfile
import shutil
from enhanced_financial_extractor import EnhancedFinancialExtractor



# Import enhanced endpoints
from enhanced_api_endpoints import register_enhanced_endpoints
# Import our processing modules
from ocr_text_extractor import extract_text_with_ocr, OCRQuestionAnswering
from financial_data_extractor import (
    extract_isin_numbers, 
    find_associated_data,
    extract_tables_from_text,
    convert_tables_to_dataframes
)

# Configure app
app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

# Register enhanced endpoints
app = register_enhanced_endpoints(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app")

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_document_path(document_id):
    """Get the path to the document file and its extracted data"""
    # In a real app, you would look up the file path in a database
    # For simplicity, we'll just look in the uploads directory
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if document_id in filename:
            return os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return None

def get_extraction_path(document_id):
    """Get the path to the extracted data for a document"""
    base_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_ocr.json")
    if os.path.exists(base_path):
        return base_path
    return None

# Routes
@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "message": "System is operational"
    })

@app.route('/api/documents/upload', methods=['POST'])
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
        
        if file and allowed_file(file.filename):
            # Get language parameter with default
            language = request.form.get('language', 'heb+eng')
            
            # Generate unique ID for the document
            document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Secure the filename and save the file
            original_filename = secure_filename(file.filename)
            filename = f"{document_id}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            logger.info(f"Document uploaded: {original_filename} (ID: {document_id})")
            
            # Start processing in the background
            # In a production system, you would queue this for async processing
            # For simplicity, we'll process it synchronously here
            try:
                logger.info(f"Starting OCR processing: {document_id}")
                document = extract_text_with_ocr(file_path, language=language)
                
                if document:
                    # Save extracted text
                    extraction_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_ocr.json")
                    with open(extraction_path, 'w', encoding='utf-8') as f:
                        json.dump(document, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"OCR processing completed: {document_id}")
                    
                    # Extract financial data
                    all_text = ""
                    for page_num, page_data in document.items():
                        all_text += page_data.get("text", "") + "\n\n"
                    
                    # Extract ISIN numbers
                    isin_numbers = extract_isin_numbers(all_text)
                    
                    # Extract associated data for each ISIN
                    financial_data = []
                    for isin in isin_numbers:
                        data = find_associated_data(all_text, isin, document)
                        if data:
                            financial_data.append(data)
                    
                    # Save financial data
                    financial_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_financial.json")
                    with open(financial_path, 'w', encoding='utf-8') as f:
                        json.dump(financial_data, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"Financial data extraction completed: {document_id}")
                    
                    # Extract tables
                    tables = extract_tables_from_text(all_text)
                    
                    # Save tables
                    if tables:
                        tables_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_tables.json")
                        with open(tables_path, 'w', encoding='utf-8') as f:
                            json.dump(tables, f, indent=2, ensure_ascii=False)
                        
                        logger.info(f"Table extraction completed: {document_id} ({len(tables)} tables)")
                
                return jsonify({
                    "message": "Document uploaded and processed successfully",
                    "document_id": document_id,
                    "filename": original_filename,
                    "language": language,
                    "page_count": len(document) if document else 0,
                    "isin_count": len(isin_numbers) if 'isin_numbers' in locals() else 0,
                    "table_count": len(tables) if 'tables' in locals() else 0,
                    "status": "completed"
                }), 200
                
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {str(e)}")
                return jsonify({
                    "message": "Document uploaded but processing failed",
                    "document_id": document_id,
                    "filename": original_filename,
                    "error": str(e),
                    "status": "failed"
                }), 200
        
        return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details and status"""
    try:
        # Look for the document file
        document_path = get_document_path(document_id)
        if not document_path:
            return jsonify({"error": "Document not found"}), 404
        
        # Check for extracted data
        extraction_path = get_extraction_path(document_id)
        
        if extraction_path:
            # Load the extracted data
            with open(extraction_path, 'r', encoding='utf-8') as f:
                document = json.load(f)
            
            # Load financial data if available
            financial_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_financial.json")
            financial_data = None
            if os.path.exists(financial_path):
                with open(financial_path, 'r', encoding='utf-8') as f:
                    financial_data = json.load(f)
            
            return jsonify({
                "document_id": document_id,
                "filename": os.path.basename(document_path),
                "page_count": len(document),
                "financial_data_available": financial_data is not None,
                "isin_count": len(financial_data) if financial_data else 0,
                "status": "completed"
            }), 200
        else:
            # Document exists but no extracted data yet
            return jsonify({
                "document_id": document_id,
                "filename": os.path.basename(document_path),
                "status": "processing"
            }), 200
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/content', methods=['GET'])
def get_document_content(document_id):
    """Get the extracted content of a document"""
    try:
        # Check for extracted data
        extraction_path = get_extraction_path(document_id)
        
        if not extraction_path:
            return jsonify({"error": "Document content not found"}), 404
        
        # Load the extracted data
        with open(extraction_path, 'r', encoding='utf-8') as f:
            document = json.load(f)
        
        # Get the requested page range
        start_page = request.args.get('start_page', default=0, type=int)
        end_page = request.args.get('end_page', default=999, type=int)
        
        # Filter pages by the requested range
        filtered_document = {}
        for page_num, page_data in document.items():
            page_index = int(page_num)
            if start_page <= page_index <= end_page:
                filtered_document[page_num] = page_data
        
        return jsonify({
            "document_id": document_id,
            "page_count": len(document),
            "content": filtered_document
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting document content for {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/financial', methods=['GET'])
def get_document_financial(document_id):
    """Get the financial data extracted from a document"""
    try:
        # Check for financial data
        financial_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_financial.json")
        
        if not os.path.exists(financial_path):
            return jsonify({"error": "Financial data not found"}), 404
        
        # Load the financial data
        with open(financial_path, 'r', encoding='utf-8') as f:
            financial_data = json.load(f)
        
        return jsonify({
            "document_id": document_id,
            "isin_count": len(financial_data),
            "financial_data": financial_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting financial data for {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/tables', methods=['GET'])
def get_document_tables(document_id):
    """Get tables extracted from a document"""
    # Get the extraction path
    extraction_path = get_extraction_path(document_id)
    
    # Check if the document exists
    document_path = get_document_path(document_id)
    if not os.path.exists(document_path):
        return jsonify({"error": "Document not found"}), 404
    
    # If extraction file exists, read tables from it
    tables = []
    
    if os.path.exists(extraction_path):
        try:
            with open(extraction_path, 'r') as f:
                extraction_data = json.load(f)
                tables = extraction_data.get('tables', [])
        except Exception as e:
            app.logger.error(f"Error reading extraction data: {e}")
    
    # Return tables (empty list if none found)
    return jsonify({
        "tables": tables,
        "document_id": document_id,
        "table_count": len(tables)
    })
@app.route('/api/qa/ask', methods=['POST'])
def ask_question():
    """Ask a question about a document"""
    try:
        # Get request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id:
            return jsonify({"error": "No document_id provided"}), 400
            
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # Get document path
        document_path = get_document_path(document_id)
        if not document_path:
            return jsonify({"error": "Document not found"}), 404
        
        # Check if we have extracted data
        extraction_path = get_extraction_path(document_id)
        
        if extraction_path:
            # Load extracted data
            with open(extraction_path, 'r', encoding='utf-8') as f:
                extracted_text = json.load(f)
            
            # Use the QA system with pre-extracted text
            qa_system = OCRQuestionAnswering(extracted_text=extracted_text)
        else:
            # Use the QA system with the document path
            qa_system = OCRQuestionAnswering(pdf_path=document_path)
        
        # Ask the question
        answer = qa_system.ask(question)
        
        return jsonify({
            "document_id": document_id,
            "question": question,
            "answer": answer,
            "confidence": 0.8  # This is a placeholder - you would compute this properly
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents"""
    try:
        documents = []
        
        # In a real app, you would query a database
        # For simplicity, we'll just look in the uploads directory
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith('doc_') and not filename.endswith('.json'):
                document_id = filename.split('_')[1].split('.')[0]
                
                # Check for extracted data to determine status
                extraction_path = os.path.join(app.config['UPLOAD_FOLDER'], f"doc_{document_id}_ocr.json")
                status = "completed" if os.path.exists(extraction_path) else "processing"
                
                documents.append({
                    "document_id": f"doc_{document_id}",
                    "filename": filename,
                    "upload_date": datetime.fromtimestamp(os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], filename))).isoformat(),
                    "status": status
                })
        
        return jsonify({"documents": documents}), 200
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve the React frontend"""
    static_folder = app.static_folder or 'frontend/build'
    if not os.path.exists(static_folder):
        return jsonify({"error": "Frontend not built"}), 404
    
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    return send_from_directory(static_folder, 'index.html')

@app.route('/api/documents/<document_id>/enhanced')
def get_document_enhanced(document_id):
    """Get enhanced financial extraction for a document"""
    # Check if the document exists
    document_path = get_document_path(document_id)
    if not os.path.exists(document_path):
        return jsonify({"error": "Document not found"}), 404
    
    # Check if enhanced extraction already exists
    enhanced_path = f"enhanced_extractions/{document_id}_enhanced.json"
    if os.path.exists(enhanced_path):
        try:
            with open(enhanced_path, 'r') as f:
                enhanced_data = json.load(f)
            return jsonify({
                "document_id": document_id,
                "enhanced_data": enhanced_data
            })
        except Exception as e:
            app.logger.error(f"Error reading enhanced extraction: {e}")
    
    # Perform enhanced extraction
    try:
        extractor = EnhancedFinancialExtractor()
        result = extractor.process_document(document_id)
        if result:
            return jsonify({
                "document_id": document_id,
                "enhanced_data": result
            })
        else:
            return jsonify({"error": "Enhanced extraction failed"}), 500
    except Exception as e:
        app.logger.error(f"Error during enhanced extraction: {e}")
        return jsonify({"error": f"Enhanced extraction error: {str(e)}"}), 500
