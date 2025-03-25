from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import os
import jinja2
from dotenv import load_dotenv
import logging

# טעינת משתני סביבה מקובץ .env
load_dotenv()

# הגדרת לוגר
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/app.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# יצירת תיקיות נדרשות אם אינן קיימות
required_dirs = ['uploads', 'data', 'data/embeddings', 'logs', 'templates']
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)

# יצירת אפליקציית Flask
app = Flask(__name__, 
            static_folder='frontend/build/static')

# Set custom template folders with fallback
app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader('templates'),
    jinja2.FileSystemLoader('frontend/build')
])

# הגדרת CORS כדי לאפשר גישה מהפרונטאנד (כל מקור)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Import feature blueprints (Vertical Slice Architecture)
from features.pdf_scanning import pdf_scanning_bp

# רישום נתיבים
app.register_blueprint(pdf_scanning_bp)

# We'll continue to support legacy route structures during migration
try:
    from routes.document_routes import document_routes
    from routes.langchain_routes import langchain_routes
    app.register_blueprint(document_routes)
    app.register_blueprint(langchain_routes)
    logger.info("Legacy routes registered")
except ImportError:
    logger.info("Legacy routes not found")

# Import diagnostic module if available
try:
    from diagnostic import diagnostic_bp
    has_diagnostic = True
except ImportError:
    has_diagnostic = False
    logger.warning("Diagnostic module not found. Diagnostic routes will not be available.")

# Register diagnostic routes if available
if has_diagnostic:
    app.register_blueprint(diagnostic_bp, url_prefix='/diagnostic')
    
    @app.route('/system-diagnostic', methods=['GET'])
    def diagnostic_page():
        return render_template('diagnostic.html')

# נתיב ברירת מחדל להצגת הפרונטאנד
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        if path and os.path.exists(os.path.join('frontend/build', path)):
            return send_from_directory('frontend/build', path)
        else:
            return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving path {path}: {e}")
        return render_template('index.html')

# נתיב בדיקת תקינות
@app.route('/health')
def health_check():
    return jsonify({
        "status": "ok", 
        "message": "System is operational",
        "architecture": "Vertical Slice"
    })

# נתיב להגשת קבצים סטטיים מתיקיית build
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# נתיב למניפסט ופייקון
@app.route('/manifest.json')
def serve_manifest():
    try:
        return send_from_directory('frontend/build', 'manifest.json')
    except:
        # If manifest.json doesn't exist, create a basic one
        manifest = {
            "short_name": "Doc Analysis",
            "name": "Financial Document Analysis System",
            "icons": [],
            "start_url": ".",
            "display": "standalone",
            "theme_color": "#000000",
            "background_color": "#ffffff"
        }
        return jsonify(manifest)

@app.route('/favicon.ico')
def serve_favicon():
    try:
        return send_from_directory('frontend/build', 'favicon.ico')
    except:
        # Return a 204 No Content if favicon is missing
        return '', 204

# Simple test page for debugging
@app.route('/test')
def test_page():
    diagnostic_link = ""
    if has_diagnostic:
        diagnostic_link = """
        <div style="margin: 20px 0;">
            <a href="/system-diagnostic" style="display: inline-block; padding: 10px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px;">אבחון מערכת PDF</a>
            <p>לחץ על הכפתור לביצוע אבחון של בעיות בעיבוד קבצי PDF</p>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Page</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; }}
            .chatbox {{ height: 300px; border: 2px solid blue; padding: 10px; overflow-y: auto; }}
            .controls {{ margin-top: 10px; }}
            .diagnostic-btn {{ display: inline-block; margin: 20px 0; padding: 10px 15px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; }}
            .diagnostic-btn:hover {{ background-color: #45a049; }}
        </style>
    </head>
    <body>
        <h1>דף בדיקה פשוט</h1>
        
        {diagnostic_link}
        
        <div class="container">
            <h2>העלאת קובץ</h2>
            <form id="upload-form">
                <input type="file" id="file-input">
                <select id="language-select">
                    <option value="he" selected>עברית</option>
                    <option value="en">אנגלית</option>
                </select>
                <button type="submit">העלאה</button>
            </form>
            <div id="upload-status"></div>
        </div>
        
        <div class="container">
            <h2>צ'אט פשוט</h2>
            <div class="chatbox" id="chat-messages"></div>
            <div class="controls">
                <input type="text" id="message-input" placeholder="הקלד הודעה...">
                <button id="send-button">שלח</button>
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                console.log('Test page loaded');
                
                // Upload form
                const uploadForm = document.getElementById('upload-form');
                const fileInput = document.getElementById('file-input');
                const languageSelect = document.getElementById('language-select');
                const uploadStatus = document.getElementById('upload-status');
                
                uploadForm.addEventListener('submit', function(e) {{
                    e.preventDefault();
                    if (!fileInput.files.length) {{
                        uploadStatus.textContent = 'נא לבחור קובץ';
                        return;
                    }}
                    
                    const formData = new FormData();
                    formData.append('file', fileInput.files[0]);
                    formData.append('language', languageSelect.value);
                    
                    uploadStatus.textContent = 'שולח קובץ...';
                    
                    // Use the new PDF scanning endpoint for PDFs
                    const endpoint = fileInput.files[0].name.toLowerCase().endsWith('.pdf')
                        ? '/api/pdf/upload'
                        : '/api/upload';
                    
                    fetch(endpoint, {{
                        method: 'POST',
                        body: formData
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        uploadStatus.textContent = 'הקובץ הועלה בהצלחה!';
                        console.log('Upload response:', data);
                    }})
                    .catch(error => {{
                        uploadStatus.textContent = 'שגיאה בהעלאה: ' + error.message;
                        console.error('Upload error:', error);
                    }});
                }});
                
                // Chat
                const chatMessages = document.getElementById('chat-messages');
                const messageInput = document.getElementById('message-input');
                const sendButton = document.getElementById('send-button');
                
                sendButton.addEventListener('click', function() {{
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Add message to chat
                    const userMsg = document.createElement('div');
                    userMsg.textContent = 'שאלה: ' + message;
                    userMsg.style.textAlign = 'right';
                    userMsg.style.margin = '5px';
                    userMsg.style.backgroundColor = '#e3f2fd';
                    userMsg.style.padding = '5px';
                    userMsg.style.borderRadius = '5px';
                    chatMessages.appendChild(userMsg);
                    
                    messageInput.value = '';
                    
                    // Send to API
                    fetch('/api/chat', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify({{
                            question: message,
                            language: languageSelect.value
                        }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        console.log('Chat response:', data);
                        
                        const botMsg = document.createElement('div');
                        botMsg.textContent = 'תשובה: ' + (data.answer || data.error || 'אין תשובה');
                        botMsg.style.textAlign = 'left';
                        botMsg.style.margin = '5px';
                        botMsg.style.backgroundColor = '#f1f1f1';
                        botMsg.style.padding = '5px';
                        botMsg.style.borderRadius = '5px';
                        chatMessages.appendChild(botMsg);
                    }})
                    .catch(error => {{
                        console.error('Chat error:', error);
                        
                        const errorMsg = document.createElement('div');
                        errorMsg.textContent = 'שגיאה: ' + error.message;
                        errorMsg.style.color = 'red';
                        errorMsg.style.margin = '5px';
                        chatMessages.appendChild(errorMsg);
                    }});
                }});
                
                // Test initial API health
                fetch('/health')
                    .then(response => response.json())
                    .then(data => {{
                        console.log('API health:', data);
                    }})
                    .catch(error => {{
                        console.error('API health check error:', error);
                    }});
            }});
        </script>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    # קביעת פורט לשרת
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting server on port {port}, debug mode: {debug}")
    logger.info(f"Using Vertical Slice Architecture")
    app.run(host='0.0.0.0', port=port, debug=debug)
