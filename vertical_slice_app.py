import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from config.configuration import config # Import the new config

# Logging is configured in config/configuration.py
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Apply configurations from config/configuration.py
app.config['SECRET_KEY'] = config.get('secret_key', 'default-secret')
app.config['JWT_SECRET_KEY'] = config.get('jwt_secret', 'default-jwt-secret') # Flask-JWT uses JWT_SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.get('local_storage_path', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = config.get('max_file_size', 16) * 1024 * 1024 # Convert MB to bytes

# Ensure upload folder exists (using the configured path)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup CORS based on config
if config.get('enable_cors', False):
    from flask_cors import CORS
    CORS(app, origins=config.get('cors_origins', '*'))

# Register feature blueprints
from features.pdf_scanning import pdf_scanning_bp
from features.document_chat import document_chat_bp
from features.table_extraction import table_extraction_bp

app.register_blueprint(pdf_scanning_bp)
app.register_blueprint(document_chat_bp)
app.register_blueprint(table_extraction_bp)

# Global API routes

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "System is operational",
        "version": "5.0.0"
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint"""
    logger.info("File upload requested")
    
    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"File uploaded: {filename}")
        
        # If PDF, send to PDF processing
        if filename.lower().endswith('.pdf'):
            try:
                from features.pdf_scanning.service import process_pdf_document
                result = process_pdf_document(file_path)
                return jsonify({
                    "status": "success",
                    "message": "File uploaded and processed successfully",
                    "document_id": result["document_id"],
                    "filename": filename,
                    "details": result
                })
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")
                return jsonify({
                    "status": "error",
                    "message": f"Error processing PDF: {str(e)}"
                }), 500
        
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "document_id": filename.replace('.', '_'),
            "filename": filename
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all documents"""
    logger.info("Documents list requested")
    
    documents = []
    
    # If upload folder exists, add files to the list
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
                doc_type = "unknown"
                if filename.lower().endswith('.pdf'):
                    doc_type = "PDF"
                elif filename.lower().endswith(('.xls', '.xlsx')):
                    doc_type = "Excel"
                elif filename.lower().endswith('.csv'):
                    doc_type = "CSV"
                    
                documents.append({
                    "id": filename.replace('.', '_'),
                    "filename": filename,
                    "upload_date": "2025-03-30T00:00:00",
                    "status": "completed",
                    "page_count": 1 if doc_type != "PDF" else 10,
                    "language": "he",
                    "type": doc_type
                })
    
    # If no documents, add a sample document
    if not documents:
        documents.append({
            "id": "demo_document_1",
            "filename": "financial_report_2025.pdf",
            "upload_date": "2025-03-15T10:30:00",
            "status": "completed",
            "page_count": 12,
            "language": "he",
            "type": "PDF"
        })
    
    logger.info(f"Returning {len(documents)} documents")
    return jsonify(documents)

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details by ID"""
    logger.info(f"Document details requested: {document_id}")
    
    # Convert ID back to filename if needed
    if '_' in document_id:
        filename = document_id.replace('_', '.', 1)
    else:
        filename = document_id
    
    # Sample document data for demo
    document = {
        "metadata": {
            "id": document_id,
            "filename": filename,
            "upload_date": "2025-03-30T00:00:00",
            "status": "completed",
            "page_count": 10,
            "language": "he",
            "type": "PDF",
            "size_bytes": 1024000
        },
        "processed_data": {
            "isin_data": [
                {"isin": "US0378331005", "company": "Apple Inc.", "market": "NASDAQ", "type": "מניה"},
                {"isin": "US88160R1014", "company": "Tesla Inc.", "market": "NASDAQ", "type": "מניה"},
                {"isin": "DE000BAY0017", "company": "Bayer AG", "market": "XETRA", "type": "מניה"}
            ],
            "financial_data": {
                "is_financial": True,
                "document_type": "דו\"ח שנתי",
                "metrics": {
                    "assets": [
                        {"name": "סך נכסים", "value": 1200000, "unit": "₪"},
                        {"name": "נכסים נזילים", "value": 550000, "unit": "₪"}
                    ],
                    "returns": [
                        {"name": "תשואה שנתית", "value": 8.7, "unit": "%"},
                        {"name": "תשואה ממוצעת 5 שנים", "value": 7.2, "unit": "%"}
                    ],
                    "ratios": [
                        {"name": "יחס שארפ", "value": 1.3},
                        {"name": "יחס P/E ממוצע", "value": 22.4}
                    ]
                }
            },
            "tables": {
                "1": [
                    {
                        "id": f"{document_id}_table_1",
                        "name": "חלוקת נכסים",
                        "page": 1,
                        "header": ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
                        "rows": [
                            ["מניות", "45%", "450,000"],
                            ["אג\"ח ממשלתי", "30%", "300,000"],
                            ["אג\"ח קונצרני", "15%", "150,000"],
                            ["מזומן", "10%", "100,000"]
                        ]
                    }
                ],
                "2": [
                    {
                        "id": f"{document_id}_table_2",
                        "name": "התפלגות מטבעית",
                        "page": 2,
                        "header": ["מטבע", "אחוז מהתיק", "שווי (₪)"],
                        "rows": [
                            ["שקל (₪)", "60%", "600,000"],
                            ["דולר ($)", "25%", "250,000"],
                            ["אירו (€)", "10%", "100,000"],
                            ["אחר", "5%", "50,000"]
                        ]
                    }
                ]
            }
        }
    }
    
    logger.info(f"Returning document details for: {document_id}")
    return jsonify(document)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Mock agent endpoint
@app.route('/api/agent', methods=['POST'])
def agent_endpoint():
    """Agent API endpoint"""
    data = request.json
    
    # Simulate different models
    model_name = data.get('model', 'gemini').lower()
    prompt = data.get('prompt', '')
    
    response = {
        "model": model_name,
        "status": "success",
        "generated_text": ""
    }
    
    if model_name == 'llama':
        response["generated_text"] = f"תשובה ממודל LLAMA: {prompt[:50]}..."
    elif model_name == 'gemini':
        response["generated_text"] = f"תשובה ממודל Gemini: {prompt[:50]}..."
    elif model_name == 'mistral':
        response["generated_text"] = f"תשובה ממודל Mistral: {prompt[:50]}..."
    else:
        response["generated_text"] = f"תשובה ממודל ברירת מחדל: {prompt[:50]}..."
    
    return jsonify(response)

if __name__ == '__main__':
    # Use settings from the imported config
    port = config.get('port', 5000)
    debug = config.get('debug', False)
    logger.info(f"Starting application on port {port} with debug={debug}")
    # Note: app.run is for development. Use Gunicorn/WSGI server in production.
    app.run(debug=debug, host='0.0.0.0', port=port)
