import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from bson import ObjectId # Needed for converting string IDs if stored as ObjectId
from pymongo.errors import ConnectionFailure # To handle DB connection errors
from config.configuration import (
    SECRET_KEY, JWT_SECRET, LOCAL_STORAGE_PATH, MAX_FILE_SIZE, PORT, DEBUG, UPLOAD_FOLDER
) # Import specific constants
from services.database_service import get_collection, get_document_by_id # Import DB helpers

# Logging is configured in config/configuration.py
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# Apply configurations from config/configuration.py
app.config['SECRET_KEY'] = SECRET_KEY
app.config['JWT_SECRET_KEY'] = JWT_SECRET # Flask-JWT uses JWT_SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Use the constant directly
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE * 1024 * 1024 # Convert MB to bytes

# Ensure upload folder exists (using the configured path)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Setup CORS based on config
# CORS setup removed as enable_cors/cors_origins are not in configuration.py
# If needed, add flask_cors import and CORS(app) call here.

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
    """Get all documents from the database"""
    logger.info("Documents list requested")
    
    try:
        collection = get_collection('documents')
        if not collection:
            logger.error("Database connection not available for getting documents.")
            return jsonify({"error": "Database connection error"}), 500

        # Fetch documents, projecting only necessary fields for the list view
        # Assuming documents have 'filename', 'upload_date', 'status', etc.
        # Convert ObjectId to string for JSON serialization
        documents_cursor = collection.find({}, {
            '_id': 1, 
            'filename': 1, 
            'upload_date': 1, 
            'status': 1, 
            'page_count': 1, 
            'language': 1, 
            'type': 1 
        })
        
        documents_list = []
        for doc in documents_cursor:
            doc['id'] = str(doc['_id']) # Convert ObjectId to string and use 'id'
            del doc['_id'] # Remove the original '_id' field
            # Add default values if fields are missing (optional, based on data model)
            doc.setdefault('upload_date', 'N/A')
            doc.setdefault('status', 'N/A')
            doc.setdefault('page_count', 0)
            doc.setdefault('language', 'N/A')
            doc.setdefault('type', 'N/A')
            documents_list.append(doc)

        logger.info(f"Returning {len(documents_list)} documents from database")
        return jsonify(documents_list)

    except ConnectionFailure as e:
        logger.error(f"Database connection failed: {e}")
        return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        logger.error(f"Error fetching documents: {e}")
        return jsonify({"error": "An error occurred while fetching documents"}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details by ID from the database"""
    logger.info(f"Document details requested: {document_id}")
    
    try:
        # Attempt to convert string ID to ObjectId if your IDs are stored as such
        # If your IDs are stored as strings, you can skip the ObjectId conversion
        try:
            obj_id = ObjectId(document_id)
        except Exception:
            # Handle cases where the ID might not be a valid ObjectId format
            # Or if you store IDs as simple strings (e.g., filenames)
            obj_id = document_id # Use the ID as is if not ObjectId

        document = get_document_by_id(obj_id)

        if document:
            # Convert ObjectId back to string for JSON response
            document['id'] = str(document['_id'])
            del document['_id']
            logger.info(f"Returning document details for: {document_id}")
            return jsonify(document)
        else:
            logger.warning(f"Document not found: {document_id}")
            return jsonify({"error": "Document not found"}), 404

    except ConnectionFailure as e:
        logger.error(f"Database connection failed while fetching document {document_id}: {e}")
        return jsonify({"error": "Database connection failed"}), 500
    except Exception as e:
        logger.error(f"Error fetching document {document_id}: {e}")
        return jsonify({"error": "An error occurred while fetching the document"}), 500

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
    logger.info(f"Starting application on port {PORT} with debug={DEBUG}")
    # Note: app.run is for development. Use Gunicorn/WSGI server in production.
    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
