#!/usr/bin/env python
"""
Launcher script for the Financial Document Analysis application.
This script creates a proper Flask app instance if needed and adds routes to serve the React frontend.
"""
import os
import sys
from flask import Flask, send_from_directory

# Try to set up the correct app instance
try:
    # First try to import the app directly
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app import app
    print("Successfully imported app from app.py")
except (ImportError, NameError) as e:
    print(f"Could not import app directly: {e}")
    print("Creating a new Flask app instance")

    # Create a new Flask app instance
    app = Flask(__name__,
                static_folder='frontend/build',
                static_url_path='')

    # Try to import configurations and blueprints
    try:
        from routes.document import document_api
        app.register_blueprint(document_api, url_prefix='/api') # Note: Original app.py used /api/document
        print("Registered document_api blueprint")
    except ImportError as e:
        print(f"Could not import document_api: {e}")

    # Example: Try importing api_blueprint if it exists
    try:
        from routes.api import api_blueprint
        app.register_blueprint(api_blueprint, url_prefix='/api') # This might conflict with document_api if both use /api
        print("Registered api_blueprint blueprint")
    except ImportError as e:
        print(f"Could not import api_blueprint: {e}")

# Add route to serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = app.static_folder or 'frontend/build' # Use app's static folder
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    else:
        # Ensure index.html exists before serving
        index_path = os.path.join(static_folder, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder, 'index.html')
        else:
            return "index.html not found in static folder.", 404

# Configure CORS if needed
try:
    from flask_cors import CORS
    CORS(app) # Apply CORS broadly
    print("Enabled CORS support")
except ImportError:
    print("flask_cors not available, CORS support not enabled")

if __name__ == '__main__':
    port = 5001
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass # Keep default port if argument is invalid

    print(f"Starting server on port {port}")
    print(f"The application should be available at http://localhost:{port}")
    # Use debug=True for development, consider waitress/gunicorn for production
    app.run(host='0.0.0.0', port=port, debug=True)