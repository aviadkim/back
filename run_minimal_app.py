import os
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'ok', 'message': 'System is running in minimal mode'}

@app.route('/')
def index():
    return {'status': 'ok', 'message': 'Financial Document Processor is running (minimal mode)'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
