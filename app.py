from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS
import os
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
required_dirs = ['uploads', 'data', 'data/embeddings', 'logs']
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)

# יצירת אפליקציית Flask
app = Flask(__name__, 
            static_folder='frontend/build/static',
            template_folder='frontend/build')

# הגדרת CORS כדי לאפשר גישה מהפרונטאנד (כל מקור)
CORS(app, resources={r"/*": {"origins": "*"}})

# ייבוא נתיבים
from routes.document_routes import document_routes
from routes.langchain_routes import langchain_routes

# רישום נתיבים
app.register_blueprint(document_routes)
app.register_blueprint(langchain_routes)

# נתיב ברירת מחדל להצגת הפרונטאנד
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    try:
        if path and os.path.exists(os.path.join(app.template_folder, path)):
            return send_from_directory(app.template_folder, path)
        else:
            return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving path {path}: {e}")
        return render_template('index.html')

# נתיב בדיקת תקינות
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "message": "System is operational"})

# נתיב להגשת קבצים סטטיים מתיקיית build
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# נתיב למניפסט ופייקון
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(app.template_folder, 'manifest.json')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory(app.template_folder, 'favicon.ico')

if __name__ == '__main__':
    # קביעת פורט לשרת
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting server on port {port}, debug mode: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
