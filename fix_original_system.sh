#!/bin/bash

echo "===== תיקון המערכת המקורית עם כל היכולות ====="

# התקנת החבילות החסרות (אם צריך)
echo "מתקין חבילות חסרות..."
pip install langchain_mistralai PyPDF2 pdf2image

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

# בדיקה והוספה של פקודות מסד נתונים
if ! docker ps | grep -q mongo; then
  echo "מפעיל את MongoDB..."
  docker-compose up -d
fi

# יצירת .env עם ערכי AWS זמניים אם לא קיים
if [ ! -f .env ]; then
  echo "יוצר קובץ .env..."
  cat > .env << 'EOF'
# הגדרות כלליות
FLASK_ENV=development
PORT=5000

# הגדרות API חיצוניים
HUGGINGFACE_API_KEY=dummy_key
MISTRAL_API_KEY=dummy_key
OPENAI_API_KEY=dummy_key

# הגדרות מסד נתונים
MONGO_URI=mongodb://localhost:27017/financial_documents

# עקיפת שגיאות AWS במצב פיתוח
AWS_ACCESS_KEY_ID=dummy_key_for_local_dev
AWS_SECRET_ACCESS_KEY=dummy_key_for_local_dev
AWS_REGION=us-east-1

# הגדרות אבטחה
SECRET_KEY=dev_secret_key
JWT_SECRET=dev_jwt_secret

# הגדרות שפה
DEFAULT_LANGUAGE=he
EOF
fi

# יצירת תיקיות נדרשות
mkdir -p uploads data/embeddings data/templates logs

# יצירת תיקיית frontend/build אם אינה קיימת
mkdir -p frontend/build

# בניית הפרונטאנד (אם יש node.js)
if command -v node &> /dev/null && [ -f frontend/package.json ]; then
  echo "בונה את הפרונטאנד..."
  cd frontend
  npm install
  npm run build
  cd ..
else
  echo "לא ניתן לבנות את הפרונטאנד - node.js חסר או package.json לא קיים"
  echo "מעתיק במקום זאת את דף ה-HTML העשיר..."
  
  # העתקת ה-HTML העשיר במקום הבנייה המלאה
  mkdir -p frontend/build
  cat > frontend/build/index.html << 'EOF'
<!DOCTYPE html>
<html lang="he" dir="rtl">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#4A90E2" />
    <meta
      name="description"
      content="FinDoc Analyzer - מערכת לניתוח מסמכים פיננסיים"
    />
    <title>FinDoc Analyzer</title>
    <style>
      body {
        font-family: 'Rubik', Arial, sans-serif;
        margin: 0;
        padding: 0;
        direction: rtl;
        background-color: #f9f9f9;
        color: #333;
      }
      
      .app-header {
        background-color: #4A90E2;
        color: white;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      }
      
      .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        max-width: 1200px;
        margin: 0 auto;
      }
      
      .navbar-logo {
        font-size: 1.5rem;
        font-weight: bold;
      }
      
      .navbar-links {
        display: flex;
        gap: 2rem;
      }
      
      .navbar-link {
        color: white;
        text-decoration: none;
      }
      
      .navbar-actions .btn-primary {
        background-color: white;
        color: #4A90E2;
      }
      
      .app-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
      }
      
      .hero-section {
        background-color: #f5f9ff;
        padding: 4rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        border-radius: 8px;
      }
      
      .hero-title {
        font-size: 2.5rem;
        margin-bottom: 1rem;
      }
      
      .hero-description {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
      }
      
      .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 2rem;
      }
      
      .feature-card {
        background-color: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
      }
      
      .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
      }
      
      .feature-icon {
        background-color: rgba(74, 144, 226, 0.1);
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1.5rem;
        font-size: 2rem;
        color: #4A90E2;
      }
      
      .btn-primary {
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 1.1rem;
        cursor: pointer;
        display: inline-block;
        text-decoration: none;
      }
      
      .btn-secondary {
        background-color: white;
        color: #4A90E2;
        border: 1px solid #4A90E2;
        padding: 0.75rem 1.5rem;
        border-radius: 4px;
        font-size: 1.1rem;
        cursor: pointer;
        display: inline-block;
        text-decoration: none;
        margin-right: 1rem;
      }
      
      .upload-widget {
        background-color: white;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-top: 2rem;
      }
      
      .dropzone {
        border: 2px dashed #e0e0e0;
        border-radius: 8px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        cursor: pointer;
        transition: border-color 0.3s ease;
      }
      
      .dropzone:hover {
        border-color: #4A90E2;
      }
      
      .footer {
        background-color: #2C3E50;
        color: white;
        padding: 2rem;
        text-align: center;
        margin-top: 3rem;
      }
      
      .footer-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        text-align: right;
      }
      
      .footer-links {
        list-style: none;
        padding: 0;
      }
      
      .footer-links li {
        margin-bottom: 0.5rem;
      }
      
      .footer-links a {
        color: #CCC;
        text-decoration: none;
      }
      
      .footer-bottom {
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 1rem;
        margin-top: 2rem;
      }
    </style>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root">
      <header class="app-header">
        <nav class="navbar">
          <div class="navbar-logo">FinDoc Analyzer</div>
          <div class="navbar-links">
            <a href="/" class="navbar-link">בית</a>
            <a href="/documents" class="navbar-link">המסמכים שלי</a>
            <a href="/custom-tables" class="navbar-link">טבלאות מותאמות</a>
          </div>
          <div class="navbar-actions">
            <button class="btn-primary">כניסה / הרשמה</button>
          </div>
        </nav>
      </header>
      
      <main class="app-container">
        <section class="hero-section">
          <h1 class="hero-title">הפיכת מסמכים פיננסיים לתובנות פעילות</h1>
          <p class="hero-description">
            פלטפורמה מבוססת בינה מלאכותית המחלצת, מנתחת ומארגנת מידע ממסמכים פיננסיים בעברית ובאנגלית
          </p>
          <button class="btn-secondary">צפה בהדגמה</button>
          <button class="btn-primary">העלה מסמך</button>
        </section>
        
        <div class="upload-widget">
          <h2>העלאת מסמך חדש</h2>
          <div class="dropzone">
            <div class="dropzone-content">
              <div class="feature-icon">📄</div>
              <p>גרור ושחרר קובץ כאן או לחץ לבחירת קובץ</p>
              <span style="color: #666; font-size: 0.9rem;">(PDF, Excel, CSV) בגודל עד 50MB</span>
            </div>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <label style="margin-right: 0.5rem;">שפת המסמך:</label>
              <select style="padding: 0.5rem; border: 1px solid #e0e0e0; border-radius: 4px;">
                <option>זיהוי אוטומטי</option>
                <option>עברית</option>
                <option>אנגלית</option>
                <option>מעורב</option>
              </select>
            </div>
            <button class="btn-primary">העלאה</button>
          </div>
        </div>
        
        <section style="margin-top: 3rem;">
          <h2 style="text-align: center; margin-bottom: 2rem;">יכולות המערכת</h2>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">📄</div>
              <h3>עיבוד מסמכים רב-לשוני</h3>
              <p>זיהוי טקסט בדיוק גבוה בעברית ובאנגלית, כולל מסמכים מעורבים</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📊</div>
              <h3>חילוץ טבלאות אוטומטי</h3>
              <p>זיהוי וחילוץ אוטומטי של טבלאות באמצעות אלגוריתמי AI מתקדמים</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🔍</div>
              <h3>זיהוי מספרי ISIN</h3>
              <p>זיהוי אוטומטי של מספרי ISIN, שמות חברות ומדדים פיננסיים בדיוק גבוה</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📈</div>
              <h3>חקירת נתונים אינטראקטיבית</h3>
              <p>חקירת נתונים שחולצו באמצעות לוחות מחוונים אינטראקטיביים ומסננים מתקדמים</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <h3>עוזר מסמכים חכם</h3>
              <p>שאל שאלות על המסמכים שלך בשפה טבעית וקבל תשובות מדויקות באופן מיידי</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">💾</div>
              <h3>ייצוא וניתוח מתקדם</h3>
              <p>ייצוא נתונים לפורמטים מובנים וניתוח מתקדם למציאת תובנות חבויות במסמכים</p>
            </div>
          </div>
        </section>
      </main>
      
      <footer class="footer">
        <div class="footer-grid">
          <div>
            <h3>FinDoc Analyzer</h3>
            <p>פלטפורמה מתקדמת לעיבוד מסמכים פיננסיים באמצעות בינה מלאכותית.</p>
          </div>
          <div>
            <h3>תכונות</h3>
            <ul class="footer-links">
              <li><a href="#">עיבוד מסמכים</a></li>
              <li><a href="#">זיהוי טבלאות</a></li>
              <li><a href="#">זיהוי ISIN</a></li>
              <li><a href="#">עוזר חכם</a></li>
            </ul>
          </div>
          <div>
            <h3>משאבים</h3>
            <ul class="footer-links">
              <li><a href="#">תיעוד</a></li>
              <li><a href="#">API</a></li>
              <li><a href="#">שאלות נפוצות</a></li>
              <li><a href="#">בלוג</a></li>
            </ul>
          </div>
          <div>
            <h3>צור קשר</h3>
            <p>info@findoc-analyzer.com</p>
            <p>03-1234567</p>
          </div>
        </div>
        <div class="footer-bottom">
          <p>© 2025 FinDoc Analyzer. כל הזכויות שמורות.</p>
        </div>
      </footer>
    </div>
  </body>
</html>
EOF
fi

# עקיפת שגיאות AWS באפליקציה המקורית
cat > aws_bypass.py << 'EOF'
"""
מודול לעקיפת שגיאות AWS בסביבת פיתוח מקומית
"""

import os
import sys
import importlib

# בדיקה אם אנו במצב פיתוח
if os.environ.get('FLASK_ENV') == 'development':
    # מוודא שאנחנו בתיקייה הנכונה
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    
    # הוספת מפתחות AWS זמניים לסביבה אם לא הוגדרו
    if 'AWS_ACCESS_KEY_ID' not in os.environ:
        os.environ['AWS_ACCESS_KEY_ID'] = 'dummy_key_for_local_dev'
    if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'dummy_key_for_local_dev'
    
    print("AWS Bypass Loaded - Using dummy credentials for local development")

# פונקציה לטעינת מודולים עם טיפול בשגיאות
def safe_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        print(f"Warning: Could not import module '{module_name}'")
        return None
EOF

# יצירת גרסה חלופית של app.py אם המקורי לא ניתן להרצה
cat > app_with_bypass.py << 'EOF'
"""
גרסה עם עקיפות של app.py המקורי
"""
import os
import sys
import importlib

# טעינת מודול העקיפה של AWS
try:
    import aws_bypass
except:
    pass

# טעינת חבילות בסיסיות
import flask
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

# יצירת אפליקציית Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# תיקיית העלאות
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# נסיון לייבא ולרשום blueprints
try:
    from features.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)
except Exception as e:
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
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
EOF

# הפעלת האפליקציה
echo "האם להריץ את האפליקציה המקורית או את הגרסה עם העקיפות?"
echo "1) הרץ את app.py המקורי"
echo "2) הרץ את app_with_bypass.py עם העקיפות"
read -p "בחירתך (1/2): " choice

if [ "$choice" = "1" ]; then
  echo "מריץ את האפליקציה המקורית..."
  PYTHONPATH=$(pwd) python app.py
else
  echo "מריץ את האפליקציה עם העקיפות..."
  PYTHONPATH=$(pwd) python app_with_bypass.py
fi
