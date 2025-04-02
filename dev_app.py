#!/usr/bin/env python
"""
Simplified version of the app for development without all dependencies.
This runs a minimal version of the app with just the basic endpoints.
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import time
import datetime
import json

# Create the Flask app
app = Flask(__name__, static_folder='frontend/build')
CORS(app)

# Ensure required directories exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('data/embeddings', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Simple in-memory storage for development
documents = []
document_counter = 0

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'System is operational',
        'timestamp': datetime.datetime.now().isoformat(),
        'mode': 'development'
    })

@app.route('/api/pdf/upload', methods=['POST'])
def upload_file():
    global document_counter
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file
    filename = f"doc_{int(time.time())}_{document_counter}.pdf"
    file_path = os.path.join('uploads', filename)
    file.save(file_path)
    
    # Create document record
    document_counter += 1
    document_id = f"doc_{document_counter}"
    
    document_info = {
        'id': document_id,
        'filename': file.filename,
        'path': file_path,
        'upload_time': datetime.datetime.now().isoformat(),
        'status': 'processed'
    }
    
    documents.append(document_info)
    
    return jsonify({
        'success': True,
        'message': 'File uploaded successfully',
        'document_id': document_id,
        'filename': file.filename
    })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({
        'documents': documents,
        'count': len(documents)
    })

@app.route('/api/copilot/route', methods=['POST'])
def copilot_route():
    data = request.json
    
    # Simulate AI response
    return jsonify({
        'response': f"This is a simulated AI response. In development mode, I'll respond to any query without using actual AI services.",
        'metadata': {
            'processed_at': datetime.datetime.now().isoformat(),
            'mode': 'development',
            'query': data.get('message', '')
        }
    })

# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Start the development server
if __name__ == '__main__':
    print("Starting simplified development server...")
    print("This is a streamlined version without AI dependencies")
    print("Visit http://localhost:5000 to view the application")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
