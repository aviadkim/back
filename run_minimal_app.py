import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'System is running in minimal mode'}

@app.route('/')
def index():
    return {'status': 'ok', 'message': 'Financial Document Processor is running (minimal mode)'}

@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'File must be PDF'}), 400
            
        # Create uploads directory if it doesn't exist
        os.makedirs('uploads', exist_ok=True)
        
        # ...existing upload code...
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
