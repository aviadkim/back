from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure static files path
app.static_folder = 'frontend/build/static'
app.static_url_path = '/static'

# Import routes
from routes.document_routes import document_routes
app.register_blueprint(document_routes)

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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path.startswith('static/'):
        return app.send_static_file(path.replace('static/', ''))
    
    build_path = os.path.join('frontend', 'build')
    if path and os.path.exists(os.path.join(build_path, path)):
        return send_from_directory(build_path, path)
    return send_from_directory(build_path, 'index.html')

# Port configuration for Codespaces compatibility
port = int(os.environ.get('PORT', 8080))

def allowed_file(filename):
    """Check if file type is allowed."""
    return filename.lower().endswith('.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
