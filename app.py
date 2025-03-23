from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Import routes
from routes.document_routes import document_routes
app.register_blueprint(document_routes)

# Import LangChain routes (if available)
try:
    from routes.langchain_routes import langchain_routes
    app.register_blueprint(langchain_routes)
    print("LangChain routes registered successfully")
except ImportError as e:
    print(f"Warning: Could not import LangChain routes: {e}")
    print("LangChain functionality will not be available")

# Basic error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health')
def health_check():
    # Check if Mistral API key is set
    mistral_available = bool(os.environ.get('MISTRAL_API_KEY'))
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'langchain_ready': mistral_available
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
