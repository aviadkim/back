from flask import Flask, jsonify, send_from_directory
import os
from routes.simple_document import document_api

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')

# Register blueprints
app.register_blueprint(document_api)

@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok",
        "message": "System is operational"
    })

# Serve React frontend for any other routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    static_folder = app.static_folder or 'frontend/build'
    if not os.path.exists(static_folder):
        return jsonify({"error": "Frontend not built"}), 404
    
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
