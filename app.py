import os
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Import configuration
from config.configuration import config, CORS_ORIGINS, SECRET_KEY, DEBUG, PORT

# Import routes
from routes.api import api_blueprint
from routes.document import document_api

# Configure logging
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

    # Apply configuration
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = DEBUG

    # Fix for proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Configure CORS
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})

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
        return app.send_static_file('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting application in {config['flask_env']} mode on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
