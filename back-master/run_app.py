#!/usr/bin/env python
"""
Launcher for the Financial Document Analysis System
"""
import os
import sys
from flask import Flask, send_from_directory

# Try to import the app
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import app
    print("Successfully imported app from app.py")
except Exception as e:
    print(f"Error importing app: {e}")
    print("Creating a new Flask app")
    app = Flask(__name__, 
               static_folder='frontend/build',
               static_url_path='')
    
    # Try to import blueprints
    try:
        from routes.document import document_api
        app.register_blueprint(document_api, url_prefix='/api')
        print("Registered document_api blueprint")
    except ImportError as e:
        print(f"Could not import document_api: {e}")

# Add route to serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('frontend/build', path)):
        return send_from_directory('frontend/build', path)
    else:
        return send_from_directory('frontend/build', 'index.html')

if __name__ == '__main__':
    port = 5001
    print(f"Starting server on port {port}")
    print(f"The application will be available at http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
