#!/bin/bash

echo "===== תיקון בעיות בסביבה ====="

# התקנת החבילות החסרות
echo "מתקין תלויות חסרות..."
pip install langchain_mistralai

# יצירת תיקיית assets אם היא לא קיימת
mkdir -p frontend/src/assets

# יצירת קובץ לוגו בסיסי אם הוא לא קיים
if [ ! -f frontend/src/assets/logo.svg ]; then
  echo "יוצר קובץ לוגו..."
  cat > frontend/src/assets/logo.svg << 'EOF'
<svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="50" fill="#4A90E2"/>
  <text x="20" y="35" font-family="Arial" font-size="24" fill="white">FinDoc Analyzer</text>
</svg>
EOF
fi

# יצירת fake_aws.py - מודול עוקף AWS
cat > fake_aws.py << 'EOF'
"""
מודול עוקף למניעת שגיאות AWS בסביבת פיתוח מקומית
"""

import sys
import os
import importlib.util
import types

class FakeDynamoDBTable:
    def __init__(self, *args, **kwargs):
        self.data = {}
    
    def put_item(self, *args, **kwargs):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}
    
    def get_item(self, *args, **kwargs):
        return {"Item": {}}
    
    def query(self, *args, **kwargs):
        return {"Items": []}
    
    def scan(self, *args, **kwargs):
        return {"Items": []}
    
    def update_item(self, *args, **kwargs):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}
    
    def delete_item(self, *args, **kwargs):
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

class FakeDynamoDB:
    def __init__(self, *args, **kwargs):
        pass
    
    def Table(self, table_name):
        return FakeDynamoDBTable()

class FakeBoto3:
    def __init__(self):
        pass
    
    def resource(self, service_name, *args, **kwargs):
        if service_name == 'dynamodb':
            return FakeDynamoDB()
        return None
    
    def client(self, service_name, *args, **kwargs):
        return types.SimpleNamespace(
            list_tables=lambda: {"TableNames": []},
            get_item=lambda **kwargs: {"Item": {}},
            put_item=lambda **kwargs: {"ResponseMetadata": {"HTTPStatusCode": 200}},
            query=lambda **kwargs: {"Items": []}
        )

# Monkey patch boto3
sys.modules['boto3'] = FakeBoto3()

print("Loaded AWS mocking module to bypass AWS errors")
EOF

# יצירת מודול פשוט עבור AgentCoordinator
mkdir -p agent_framework
cat > agent_framework/__init__.py << 'EOF'
"""
מסגרת סוכנים בסיסית למערכת
"""
EOF

cat > agent_framework/coordinator.py << 'EOF'
"""
מתאם סוכנים פשוט שלא דורש AWS או מודלים חיצוניים
"""

class AgentCoordinator:
    """מתאם סוכנים פשוט למטרות פיתוח"""
    
    def __init__(self, *args, **kwargs):
        self.name = "Development Agent Coordinator"
    
    def process_query(self, session_id, query, context=None):
        """מחזיר תגובה פשוטה לשאלה"""
        return {
            "answer": f"זוהי תשובה לשאלה: {query}",
            "sources": [],
            "session_id": session_id
        }
    
    def create_session(self, user_id, documents=None):
        """יוצר מזהה סשן חדש"""
        import uuid
        return str(uuid.uuid4())
    
    def load_session(self, session_id):
        """טוען סשן קיים"""
        return {"session_id": session_id, "history": []}
EOF

# יצירת תיקיית features אם היא לא קיימת
mkdir -p features/chatbot

# יצירת מודולים בסיסיים ל-chatbot
cat > features/chatbot/__init__.py << 'EOF'
"""
מודול צ'אטבוט פשוט
"""
from flask import Blueprint

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chat')

from . import routes
EOF

cat > features/chatbot/routes.py << 'EOF'
"""
נתיבי API לצ'אטבוט
"""
from flask import jsonify, request
from . import chatbot_bp
from .service import process_query, get_chat_history, create_session

@chatbot_bp.route('/query', methods=['POST'])
def query():
    """מעבד שאלה ומחזיר תשובה"""
    data = request.json
    session_id = data.get('session_id')
    query_text = data.get('query')
    
    if not session_id or not query_text:
        return jsonify({"error": "חסרים פרמטרים"}), 400
    
    result = process_query(session_id, query_text)
    return jsonify(result)

@chatbot_bp.route('/session', methods=['POST'])
def create_chat_session():
    """יוצר סשן צ'אט חדש"""
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    documents = data.get('documents', [])
    
    session_id = create_session(user_id, documents)
    return jsonify({"session_id": session_id})

@chatbot_bp.route('/history/<session_id>', methods=['GET'])
def history(session_id):
    """מחזיר היסטוריית צ'אט"""
    chat_history = get_chat_history(session_id)
    return jsonify(chat_history)
EOF

cat > features/chatbot/service.py << 'EOF'
"""
שירות צ'אטבוט
"""
import uuid
from agent_framework.coordinator import AgentCoordinator

# יצירת מופע גלובלי של מתאם הסוכנים
coordinator = AgentCoordinator()

# שמירת היסטוריית צ'אט בזיכרון (לפיתוח בלבד)
chat_history = {}

def process_query(session_id, query_text):
    """
    מעבד שאלה ומחזיר תשובה
    """
    # אם הסשן לא קיים, יוצר אחד חדש
    if session_id not in chat_history:
        session_id = create_session('anonymous')
    
    # שולח את השאלה למתאם הסוכנים
    result = coordinator.process_query(session_id, query_text)
    
    # שומר את השאלה והתשובה בהיסטוריה
    if session_id not in chat_history:
        chat_history[session_id] = []
    
    chat_history[session_id].append({
        "role": "user",
        "content": query_text
    })
    
    chat_history[session_id].append({
        "role": "assistant",
        "content": result["answer"]
    })
    
    return result

def get_chat_history(session_id):
    """
    מחזיר את היסטוריית הצ'אט לסשן מסוים
    """
    return chat_history.get(session_id, [])

def create_session(user_id, documents=None):
    """
    יוצר סשן צ'אט חדש
    """
    session_id = str(uuid.uuid4())
    chat_history[session_id] = []
    return session_id
EOF

# יצירת קובץ Flask בסיסי עם נתיבים פשוטים
cat > simple_app.py << 'EOF'
import os
import importlib
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

# יבוא מודול מזויף ל-AWS
import fake_aws

# יצירת אפליקציית Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# תיקיית העלאות
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# יבוא blueprints
try:
    from features.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)
except ImportError as e:
    print(f"אזהרה: לא ניתן לייבא את מודול הצ'אטבוט: {e}")

# נתיבי API בסיסיים

@app.route('/health')
def health():
    """בדיקת בריאות המערכת"""
    return jsonify({"status": "ok", "message": "System is operational"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """העלאת קובץ"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # בדרך כלל כאן היינו מעבדים את הקובץ
        
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "document_id": filename.replace('.', '_'),
            "filename": filename
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """קבלת רשימת מסמכים"""
    # החזרת רשימה ריקה או דמה למטרות פיתוח
    return jsonify([
        {
            "id": "demo_document_1",
            "filename": "financial_report_2024.pdf",
            "upload_date": "2024-01-15T10:30:00",
            "status": "completed",
            "page_count": 12,
            "language": "he"
        }
    ])

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """משרת את אפליקציית הפרונטאנד"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
EOF

echo "===== תיקון בעיות הסתיים ====="
echo "כעת נסה להריץ את הפרונטאנד העשיר עם:"
echo "cd frontend && npm run build && cd .."
echo "python simple_app.py"
