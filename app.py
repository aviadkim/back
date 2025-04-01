import os
from flask import Flask, jsonify, send_from_directory
from flask import send_from_directory
import os
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Import configuration
from config.configuration import (
    SECRET_KEY, DEBUG, PORT, UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH, MONGO_URI
)

# Import routes
from routes.api import api_blueprint
from routes.document import document_api

# Configure logging (Ensure logging is set up, possibly via configuration.py)
# If configuration.py handles basicConfig, this might not be needed here.
# However, getting the logger instance is fine.
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

# Apply configuration from imported variables
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['MONGO_URI'] = MONGO_URI

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Fix for proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app)

# Configure CORS (allow all origins for simplicity in dev)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(document_api, url_prefix='/api/document')

# Health check route
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "System is operational"})

# Serve React frontend for any other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    static_folder = app.static_folder or 'frontend/build' # Use app's static folder
    if path != "" and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    # Check if build directory exists
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build")
    if not os.path.exists(frontend_path):
        return jsonify({"error": "Frontend not built. Please run npm run build in the frontend directory."}), 404
    # If path doesn't exist in static folder, serve index.html for client-side routing
    index_path = os.path.join(static_folder, 'index.html')
    if os.path.exists(index_path):
         return send_from_directory(static_folder, 'index.html')
    else:
         # Fallback if index.html is missing
         logger.error(f"index.html not found in static folder: {static_folder}")
         return "Frontend not found.", 404


if __name__ == '__main__':
    # Use PORT from imported config
    logger.info(f"Starting application in {os.getenv('FLASK_ENV', 'development')} mode on port {PORT}")
    # Use DEBUG from imported config
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)

