from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from routes import document_routes, langchain_routes
from models.document_models import init_db
from utils.logger import setup_logger

# Create Flask app
app = Flask(__name__, static_folder='frontend/build')
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup logger
logger = setup_logger()

# Initialize database
init_db()

# Create upload directory if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Register routes
app.register_blueprint(document_routes.document_bp)
app.register_blueprint(langchain_routes.langchain_bp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify server is running."""
    return jsonify({"status": "ok"}), 200

# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Handle 404 errors
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
