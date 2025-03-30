#!/usr/bin/env python
"""
Script to run the application serving the frontend properly.
This ensures the frontend build is served from the correct directory.
"""
import os
import sys
import time
import webbrowser
import threading
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("data/embeddings", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Set environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_DYNAMODB'] = 'false'  # Disable DynamoDB in development
os.environ['SKIP_VECTOR_SEARCH'] = 'true'
os.environ['DISABLE_AWS_SERVICES'] = 'true'

# Dummy AWS credentials to avoid errors
if 'AWS_ACCESS_KEY_ID' not in os.environ:
    os.environ['AWS_ACCESS_KEY_ID'] = 'codespace_dummy_key'
    
if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'codespace_dummy_secret'
    
if 'AWS_REGION' not in os.environ:
    os.environ['AWS_REGION'] = 'us-east-1'

# Function to open the browser
def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:5000')
    print('\nOpened browser - you should see the frontend now')

# Start browser thread
def start_app_with_browser():
    threading.Thread(target=open_browser).start()
    
    try:
        # Import and run the main app
        from app import app
        print("Starting the application with the frontend...")
        app.run(debug=True, port=5000)
    except ImportError:
        # If app.py can't be imported, create a minimal app to serve the frontend
        print("Could not import the main app. Using a minimal app to serve the frontend.")
        
        app = Flask(__name__, static_folder='frontend/build', static_url_path='')
        CORS(app)
        
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve(path):
            if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')
        
        @app.route('/health')
        def health():
            return jsonify({"status": "ok", "message": "System is operational"})
        
        # Simple document API stub
        documents = []
        
        @app.route('/api/pdf/documents', methods=['GET'])
        def get_documents():
            return jsonify({"documents": documents})
        
        @app.route('/api/pdf/upload', methods=['POST'])
        def upload_document():
            file = request.files.get('file')
            if not file:
                return jsonify({"error": "No file provided"}), 400
                
            # Save file
            os.makedirs('uploads', exist_ok=True)
            file_path = os.path.join('uploads', file.filename)
            file.save(file_path)
            
            # Create document record
            doc_id = f"doc_{int(time.time())}"
            documents.append({
                "_id": doc_id,
                "filename": file.filename,
                "path": file_path,
                "language": request.form.get('language', 'he')
            })
            
            return jsonify({
                "success": True,
                "document_id": doc_id,
                "filename": file.filename
            })
            
        @app.route('/api/copilot/route', methods=['POST'])
        def chat():
            data = request.json
            message = data.get('message', '')
            language = data.get('language', 'he')
            
            # Simple response
            response = {
                "response": "אני מזהה שאתה שואל על המסמך. זוהי גרסת הדגמה שמציגה את הממשק, אך אינה מחוברת למודל השפה האמיתי.",
                "suggested_questions": [
                    "מהו סכום החשבונית?",
                    "מה תאריך החשבונית?",
                    "מי הספק בחשבונית זו?"
                ]
            }
            
            if language != 'he':
                response = {
                    "response": "I see you're asking about the document. This is a demo version showing the interface, but it's not connected to the real language model.",
                    "suggested_questions": [
                        "What is the invoice amount?",
                        "What is the invoice date?",
                        "Who is the vendor in this invoice?"
                    ]
                }
                
            return jsonify(response)
            
        app.run(debug=True, port=5000)

if __name__ == "__main__":
    start_app_with_browser()
