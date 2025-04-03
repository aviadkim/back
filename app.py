from services.auth_service import AuthService
import requests

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
from config import Config  # Import the Config class
from tasks import process_document_task # Import the Celery task
import database # Add this
from database import ( # Add these specific imports
    add_document_record,
    update_document_status,
    get_document_by_id,
    list_all_documents,
    close_db_connection # For teardown
)
from celery.result import AsyncResult
from celery_worker import celery_app # Ensure celery_app is imported
from enhanced_financial_extractor import EnhancedFinancialExtractor



# Import enhanced endpoints
from services.payment_service import PaymentService
from services.auth_service import AuthService


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
app.config.from_object(Config)  # Load config from Config object

# Register enhanced endpoints
# Note: Ensure register_enhanced_endpoints doesn't override config if it also loads config
app = register_enhanced_endpoints(app)

# Ensure upload directory exists using the loaded config
# Note: Consider if UPLOAD_FOLDER should be absolute or relative, and handle creation appropriately
# For now, assume it's relative to the app root as before.
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

# Utility function (keep allowed_file, remove others)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

            # Secure the filename and determine save path
            original_filename = secure_filename(file.filename)
            filename = f"{document_id}_{original_filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # --- DB INSERTION START ---
            logger.info(f"Attempting to add document record to DB for {document_id}")
            db_id = add_document_record(
                document_id=document_id,
                filename=original_filename,
                language=language
                # user_id=... # Add user ID here when auth is implemented
            )
            if not db_id:
                 logger.error(f"Failed to create database record for {document_id}")
                 # Decide if we should still save the file or return error
                 return jsonify({"error": "Failed to create document record in database"}), 500
            logger.info(f"Successfully added document record to DB for {document_id}")
            # --- DB INSERTION END ---

            # Save the file (consider moving this after DB record creation)
            file.save(file_path)
            logger.info(f"Document saved locally: {file_path} (ID: {document_id})")

            # Queue the processing task to run in the background
            logger.info(f"Queueing document processing task for: {document_id}")
            try:
                # Pass the file_path for now, assuming shared filesystem access for worker
                task = process_document_task.delay(file_path, document_id, original_filename, language)
                logger.info(f"Task {task.id} queued for document {document_id}")

                # --- DB UPDATE START ---
                # Update DB record with task_id and initial file_path
                update_success = update_document_status(
                    document_id=document_id,
                    status="queued",
                    task_id=task.id,
                    file_path=file_path # Store the initial path
                )
                if not update_success:
                     logger.warning(f"Failed to update DB status to 'queued' for {document_id}")
                # --- DB UPDATE END ---


                # Return response indicating processing has started
                return jsonify({
                    "message": "Document uploaded successfully. Processing started in background.",
                    "document_id": document_id,
                    "filename": original_filename,
                    "task_id": task.id,
                    "status": "queued" # Status from DB perspective
                }), 202
            except Exception as e:
                 logger.error(f"Error queueing task for document {document_id}: {str(e)}")
                 # --- DB UPDATE ON QUEUE FAIL START ---
                 update_document_status(
                     document_id=document_id,
                     status="queue_failed",
                     error_message=f"Failed to queue task: {str(e)}"
                 )
                 # --- DB UPDATE ON QUEUE FAIL END ---
                 # Consider deleting the uploaded file if queuing fails
                 # os.remove(file_path) # Optional cleanup
                 return jsonify({
                     "message": "Document uploaded but failed to queue processing task.",
                     "document_id": document_id,
                     "filename": original_filename,
                     "error": str(e),
                     "status": "queue_failed"
                 }), 500
        
        return jsonify({"error": "Invalid file type"}), 400
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get document details and status from DB"""
    try:
        document_record = get_document_by_id(document_id)

        if not document_record:
            return jsonify({"error": "Document not found"}), 404

        # Prepare response based on DB record
        response = {
            "document_id": document_record["_id"],
            "filename": document_record.get("filename"),
            "status": document_record.get("status"),
            "upload_time": document_record.get("upload_time"),
            "last_update_time": document_record.get("last_update_time"),
            "language": document_record.get("language"),
            "error_message": document_record.get("error_message"),
            # Add other relevant fields from the DB record as needed
            # e.g., page_count, isin_count could be added after processing
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/content', methods=['GET'])
def get_document_content(document_id):
    """Get the extracted content of a document using path from DB"""
    try:
        document_record = get_document_by_id(document_id)
        if not document_record:
            return jsonify({"error": "Document not found"}), 404

        ocr_path = document_record.get("ocr_path")
        if not ocr_path or not os.path.exists(ocr_path):
             # Check status as well
             status = document_record.get("status")
             if status == "processing" or status == "queued":
                 return jsonify({"error": "Document content is still being processed."}), 202 # Accepted
             else:
                 return jsonify({"error": "Document content not available or processing failed."}), 404

        # Load the extracted data from the path stored in DB
        with open(ocr_path, 'r', encoding='utf-8') as f:
            document_content = json.load(f)
        
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
            "page_count": len(document_content), # Get count from loaded data
            "content": filtered_document
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting document content for {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/financial', methods=['GET'])
def get_document_financial(document_id):
    """Get the financial data extracted from a document using path from DB"""
    try:
        document_record = get_document_by_id(document_id)
        if not document_record:
            return jsonify({"error": "Document not found"}), 404

        financial_path = document_record.get("financial_path")
        if not financial_path or not os.path.exists(financial_path):
             status = document_record.get("status")
             if status == "processing" or status == "queued":
                 return jsonify({"error": "Financial data is still being processed."}), 202 # Accepted
             else:
                 return jsonify({"error": "Financial data not available or processing failed."}), 404

        # Load the financial data from the path stored in DB
        with open(financial_path, 'r', encoding='utf-8') as f:
            financial_data = json.load(f)
        
        return jsonify({
            "document_id": document_id,
            "isin_count": len(financial_data), # Get count from loaded data
            "financial_data": financial_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting financial data for {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents/<document_id>/tables', methods=['GET'])
def get_document_tables(document_id):
    """Get tables extracted from a document using path from DB"""
    try:
        document_record = get_document_by_id(document_id)
        if not document_record:
            return jsonify({"error": "Document not found"}), 404

        tables_path = document_record.get("tables_path")
        tables = []
        table_count = 0

        if tables_path and os.path.exists(tables_path):
            try:
                with open(tables_path, 'r', encoding='utf-8') as f:
                    tables = json.load(f) # Assuming tables are stored as a list directly
                table_count = len(tables)
                logger.info(f"Loaded {table_count} tables from {tables_path}")
            except Exception as e:
                logger.error(f"Error reading tables file {tables_path}: {e}")
                # Decide how to handle: return error or empty list?
                return jsonify({"error": f"Failed to read table data: {str(e)}"}), 500
        else:
            status = document_record.get("status")
            if status == "processing" or status == "queued":
                 logger.info(f"Table data for {document_id} is still processing.")
                 # Return empty list or indicate processing? Let's return empty for now.
            elif status == "completed":
                 logger.info(f"No tables file found or path not set for completed document {document_id}.")
            else: # Failed or other status
                 logger.warning(f"Table data not available for document {document_id} (status: {status})")


        # Return tables (empty list if none found or processing)
        return jsonify({
            "document_id": document_id,
            "tables": tables,
            "table_count": table_count
        })
    except Exception as e:
        logger.error(f"Error getting tables for {document_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/qa/ask', methods=['POST'])
def ask_question():
    """Ask a question about a document"""
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

        # Get document record from DB
        document_record = get_document_by_id(document_id)
        if not document_record:
            return jsonify({"error": "Document not found"}), 404

        # Determine which path to use for QA
        ocr_path = document_record.get("ocr_path")
        original_file_path = document_record.get("file_path") # Path to original PDF

        if ocr_path and os.path.exists(ocr_path):
            # Use pre-extracted text if available
            logger.info(f"Using pre-extracted OCR data for QA: {ocr_path}")
            with open(ocr_path, 'r', encoding='utf-8') as f:
                extracted_text_data = json.load(f)
            qa_system = OCRQuestionAnswering(extracted_text=extracted_text_data)
        elif original_file_path and os.path.exists(original_file_path):
             # Fallback to processing original PDF if OCR data missing (might be slow)
             logger.warning(f"OCR data path not found for {document_id}. Falling back to processing PDF: {original_file_path}")
             qa_system = OCRQuestionAnswering(pdf_path=original_file_path)
        else:
             logger.error(f"Neither OCR data nor original file path found for document {document_id}")
             return jsonify({"error": "Required document data not found for Q&A."}), 404
        
        # Ask the question
        answer = qa_system.ask(question)
        
        return jsonify({
            "document_id": document_id,
            "question": question,
            "answer": answer,
            "confidence": 0.8  # This is a placeholder - you would compute this properly
        }), 200

@app.route('/api/qa/deepseek', methods=['POST'])
def ask_deepseek():
    """Temporary test endpoint for DeepSeek Q&A via OpenRouter"""
    from config import Config
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    if not Config.OPENROUTER_API_KEY:
        return jsonify({"error": "OpenRouter API key not configured"}), 500

    try:
        # Call OpenRouter API for DeepSeek model
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",  # Update with your site URL
            "X-Title": "Financial Analysis API"       # Update with your site name
        }
        payload = {
            "model": "deepseek/deepseek-chat-v3-0324:free",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        answer = response.json()['choices'][0]['message']['content']
        
        return jsonify({
            "question": question,
            "answer": answer,
            "model": "deepseek-chat-v3",
            "provider": "OpenRouter"
        }), 200

    except requests.exceptions.RequestException as e:
        logger.error(f"DeepSeek API request failed: {str(e)}")
        return jsonify({"error": f"API request failed: {str(e)}"}), 502
    except KeyError as e:
        logger.error(f"Invalid DeepSeek API response format: {str(e)}")
        return jsonify({"error": "Invalid API response format"}), 502
    except Exception as e:
        logger.error(f"Unexpected error processing DeepSeek response: {str(e)}")
        return jsonify({"error": "Unexpected error processing response"}), 500
        

@app.route('/api/documents', methods=['GET'])
def list_documents():
    """List all documents from DB"""
    try:
        # Fetch documents from database
        # Add user_id filtering later when auth is implemented
        documents_from_db = list_all_documents() # Limit can be added here

        # Format response (convert datetime, etc. if needed)
        response_documents = []
        for doc in documents_from_db:
            response_documents.append({
                "document_id": doc["_id"],
                "filename": doc.get("filename"),
                "upload_date": doc.get("upload_time").isoformat() if doc.get("upload_time") else None,
                "status": doc.get("status"),
                "language": doc.get("language")
                # Add other fields as needed
            })

        return jsonify({"documents": response_documents}), 200

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


@app.route('/api/tasks/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """Check the status of a Celery task."""
    try:
        task_result = AsyncResult(task_id, app=celery_app)

        status = task_result.status
        result = None

        if task_result.successful():
            result = task_result.get() # Get the return value of the task
            status = 'completed' # Explicitly set completed status
        elif task_result.failed():
            # Get the exception details
            result = str(task_result.info) if task_result.info else 'Task failed without specific error info.'
            status = 'failed'
        elif status == 'PENDING':
             # Task is waiting to be executed or unknown task_id
             result = 'Task is pending or task ID is invalid.'
        elif status == 'STARTED':
             result = 'Task has started processing.'
        elif status == 'RETRY':
             result = 'Task is being retried.'
        # Add other Celery states if needed (e.g., REVOKED)

        response = {
            'task_id': task_id,
            'status': status,
            'result': result
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error checking task status for {task_id}: {str(e)}")
        return jsonify({"error": f"Failed to get task status: {str(e)}"}), 500

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


@app.teardown_appcontext
def teardown_db(exception):
    close_db_connection()


# Service initializations
payment_service = PaymentService()
auth_service = AuthService()

# Payment routes

@app.route('/api/subscribe', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    try:
        data = request.json
        user_id = data.get('user_id')
        plan_id = data.get('plan_id')
        
        if not user_id or not plan_id:
            return jsonify({"error": "Missing user_id or plan_id"}), 400
            
        # In production, verify user auth here
        subscription = payment_service.create_subscription(user_id, plan_id)
        
        return jsonify({
            "message": "Subscription created",
            "subscription_id": subscription['id']
        }), 201
    except Exception as e:
        logger.error(f"Error processing payment webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
            
        # Check if user exists
        if database.get_user_by_email(email):
            return jsonify({"error": "User already exists"}), 400
            
        # Hash password and create user
        password_hash = auth_service.hash_password(password)
        user_id = database.add_user(email, password_hash)
        
        if not user_id:
            return jsonify({"error": "Failed to create user"}), 500
            
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login existing user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
            
        # Get user from database
        user = database.get_user_by_email(email)
        if not user or not auth_service.verify_password(user['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401
            
        # Generate JWT token
        token = auth_service.generate_token(str(user['_id']))
        
        return jsonify({
            "message": "Login successful",
            "token": token,
            "user_id": str(user['_id'])
        }), 200
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Auth middleware
def auth_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Authorization token missing"}), 401
            
        user_id = auth_service.verify_token(token)
        if not user_id or isinstance(user_id, str) and 'error' in user_id:
            return jsonify({"error": "Invalid token"}), 401
            
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated

# Protect payment routes
@app.route('/api/subscribe', methods=['POST'])
@auth_required
def create_subscription():
    """Create a new subscription (protected)"""
    try:
        data = request.json
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({"error": "Plan ID required"}), 400
            
        # Get user from request (added by auth middleware)
        user_id = request.user_id
        subscription = payment_service.create_subscription(user_id, plan_id)
        
        return jsonify({
            "message": "Subscription created",
            "subscription_id": subscription['id']
        }), 201
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({"error": str(e)}), 500
        logger.error(f"Error creating subscription: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/payment/webhook', methods=['POST'])
@payment_service.webhook_handler

# Authentication routes

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
            
        # Check if user exists (implementation needed in database.py)
        # Hash password
        hashed_password = auth_service.hash_password(password)
        
        # Create user (implementation needed in database.py)
        user_id = "generated_user_id"  # Replace with actual user creation
        
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Login existing user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
            
        # Get user from DB (implementation needed in database.py)
        user = {"id": "user_id", "password_hash": "hashed_password"}  # Replace with actual user lookup
        
        if not auth_service.verify_password(user['password_hash'], password):
            return jsonify({"error": "Invalid credentials"}), 401
            
        token = auth_service.generate_token(user['id'])
        
        return jsonify({
            "message": "Login successful",
            "token": token
        }), 200
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": str(e)}), 500

def auth_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Authorization token missing"}), 401
            
        user_id = auth_service.verify_token(token)
        if isinstance(user_id, str):
            request.user_id = user_id
            return f(*args, **kwargs)
        else:
            return jsonify({"error": user_id}), 401
    return decorated

def payment_webhook():
    """Handle Paddle payment webhooks"""
    try:
        event = request.json
        # Process different webhook events
        if event['alert_name'] == 'subscription_created':
            # Handle new subscription
            pass
        elif event['alert_name'] == 'subscription_cancelled':
            # Handle cancelled subscription
            pass
            
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500
