import os
from flask import Flask, jsonify, send_from_directory
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

def create_app():
    """Create and configure the Flask application."""
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
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # If path doesn't exist in static folder, serve index.html for client-side routing
        return send_from_directory(app.static_folder, 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    # Use PORT from imported config
    logger.info(f"Starting application in {os.getenv('FLASK_ENV', 'development')} mode on port {PORT}")
    # Use DEBUG from imported config
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
