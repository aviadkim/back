"""
Main application entry point with vertical slice architecture.
"""
from flask import Flask, jsonify, send_from_directory
import os
import logging
import sys

# Add the parent directory to sys.path to allow importing our features
sys.path.insert(0, os.path.abspath('..'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    # Set the static folder to the frontend build directory with absolute path
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    
    # Configure the app with absolute paths
    app.config.update(
        DEBUG=os.environ.get('FLASK_DEBUG', True),
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-for-testing'),
        UPLOAD_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads')),
        EXTRACTION_FOLDER=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'extractions')),
    )
    
    # Basic routes
    @app.route('/health')
    def health():
        return jsonify({"status": "ok", "message": "Service is healthy"})
    
    # Important: Remove the conflicting routes
    # We will let the feature registry handle the frontend routes
    
    # Try to register features from feature registry
    try:
        from project_organized.features import registry
        registry.register_all_with_app(app)
        logger.info(f"Registered features: {', '.join(registry.list_enabled_features())}")
    except ImportError as e:
        logger.warning(f"Could not import feature registry: {e}")
        
        # Register individual features as fallback
        try:
            from project_organized.features.document_upload.api import register_routes as register_upload_routes
            register_upload_routes(app)
            logger.info("Registered document upload routes")
        except ImportError as e:
            logger.warning(f"Could not register document upload routes: {e}")
        
        try:
            from project_organized.features.pdf_processing.api import register_routes as register_pdf_routes
            register_pdf_routes(app)
            logger.info("Registered PDF processing routes")
        except ImportError as e:
            logger.warning(f"Could not register PDF processing routes: {e}")
        
        try:
            from project_organized.features.financial_analysis.api import register_routes as register_financial_routes
            register_financial_routes(app)
            logger.info("Registered financial analysis routes")
        except ImportError as e:
            logger.warning(f"Could not register financial analysis routes: {e}")
        
        try:
            from project_organized.features.document_qa.api import register_routes as register_qa_routes
            register_qa_routes(app)
            logger.info("Registered document Q&A routes")
        except ImportError as e:
            logger.warning(f"Could not register document Q&A routes: {e}")
            
        try:
            from project_organized.features.document_export.api import register_routes as register_export_routes
            register_export_routes(app)
            logger.info("Registered document export routes")
        except ImportError as e:
            logger.warning(f"Could not register document export routes: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    try:
        app.run(host='0.0.0.0', port=port, debug=True)
    except OSError:
        # Try alternate ports if the specified one is taken
        for alt_port in [5002, 5003, 5004, 5005]:
            logger.info(f"Port {port} in use, trying {alt_port} instead")
            try:
                app.run(host='0.0.0.0', port=alt_port, debug=True)
                break
            except OSError:
                continue
