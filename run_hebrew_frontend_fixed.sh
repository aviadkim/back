#!/bin/bash

echo "===== הרצת הפרונטאנד העשיר בעברית ====="

# הרג כל התהליכים הקיימים
echo "עוצר תהליכים קודמים..."
pkill -f "python.*app.*py" || true

# משיכת שינויים חדשים מהגיט
echo "מושך שינויים חדשים מהרפוזיטורי..."
git pull

# יצירת תיקיות נדרשות
mkdir -p uploads data/embeddings data/templates logs
mkdir -p frontend/build
mkdir -p frontend/src/assets

# יצירת קובץ .env עם ערכי AWS זמניים
echo "יוצר קובץ .env..."
cat > .env << 'EOF'
# הגדרות כלליות
FLASK_ENV=development
PORT=5001

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

# יצירת קובץ לוגו בסיסי
echo "יוצר קובץ לוגו..."
cat > frontend/src/assets/logo.svg << 'EOF'
<svg width="200" height="50" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="50" fill="#4A90E2"/>
  <text x="20" y="35" font-family="Arial" font-size="24" fill="white">FinDoc Analyzer</text>
</svg>
EOF

# יצירת ממשק עשיר סטטי במקום הבנייה המלאה
echo "יוצר פרונטאנד עשיר סטטי..."
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
      
      /* Upload Form styles */
      #file-upload-form {
        display: flex;
        flex-direction: column;
      }
      
      #file-input {
        display: none;
      }
      
      .upload-options {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 1rem;
      }
      
      .language-selector {
        display: flex;
        align-items: center;
      }
      
      .language-selector label {
        margin-left: 0.5rem;
      }
      
      #language-select {
        padding: 0.5rem 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 4px;
      }
      
      #upload-status {
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 4px;
        display: none;
      }
      
      .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
      }
      
      .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
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
          <button class="btn-primary" onclick="document.getElementById('upload-section').scrollIntoView({behavior: 'smooth'})">העלה מסמך</button>
        </section>
        
        <div id="upload-section" class="upload-widget">
          <h2>העלאת מסמך חדש</h2>
          <form id="file-upload-form">
            <div class="dropzone" onclick="document.getElementById('file-input').click()">
              <div class="dropzone-content">
                <div class="feature-icon">📄</div>
                <p id="file-label">גרור ושחרר קובץ כאן או לחץ לבחירת קובץ</p>
                <span style="color: #666; font-size: 0.9rem;">(PDF, Excel, CSV) בגודל עד 50MB</span>
              </div>
            </div>
            <input type="file" id="file-input" accept=".pdf,.xls,.xlsx,.csv">
            <div class="upload-options">
              <div class="language-selector">
                <label for="language-select">שפת המסמך:</label>
                <select id="language-select">
                  <option value="auto">זיהוי אוטומטי</option>
                  <option value="he">עברית</option>
                  <option value="en">אנגלית</option>
                  <option value="mixed">מעורב</option>
                </select>
              </div>
              <button class="btn-primary" type="button" onclick="uploadFile()">העלאה</button>
            </div>
          </form>
          <div id="upload-status"></div>
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

    <script>
      // הגדרת משתנים
      const fileInput = document.getElementById('file-input');
      const fileLabel = document.getElementById('file-label');
      const uploadStatus = document.getElementById('upload-status');
      
      // טיפול בבחירת קובץ
      fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
          fileLabel.textContent = this.files[0].name;
        } else {
          fileLabel.textContent = 'גרור ושחרר קובץ כאן או לחץ לבחירת קובץ';
        }
      });
      
      // פונקציית העלאת קובץ
      function uploadFile() {
        const file = fileInput.files[0];
        if (!file) {
          showStatus('נא לבחור קובץ', 'error');
          return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', document.getElementById('language-select').value);
        
        // עדכון סטטוס העלאה
        showStatus('מעלה את הקובץ...', 'info');
        
        // שליחת הקובץ לשרת
        fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
        .then(response => response.json())
        .then(data => {
          if (data.status === 'success') {
            showStatus('הקובץ הועלה בהצלחה!', 'success');
            // אופציונלי: ניתוב לדף המסמך
            if (data.document_id) {
              setTimeout(() => {
                window.location.href = `/documents/${data.document_id}`;
              }, 2000);
            }
          } else {
            showStatus(`שגיאה: ${data.message || 'אירעה שגיאה בהעלאת הקובץ'}`, 'error');
          }
        })
        .catch(error => {
          showStatus('שגיאה בהעלאת הקובץ', 'error');
          console.error('Error:', error);
        });
      }
      
      // הצגת הודעת סטטוס
      function showStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.style.display = 'block';
        
        // הסרת כל הקלאסים הקודמים
        uploadStatus.classList.remove('status-success', 'status-error', 'status-info');
        
        // הוספת הקלאס המתאים
        if (type === 'success') {
          uploadStatus.classList.add('status-success');
        } else if (type === 'error') {
          uploadStatus.classList.add('status-error');
        } else {
          uploadStatus.style.backgroundColor = '#cce5ff';
          uploadStatus.style.color = '#004085';
          uploadStatus.style.border = '1px solid #b8daff';
        }
      }
    </script>
  </body>
</html>
EOF

# יצירת אפליקציית Flask עדכנית עם ניתוב לפורט חדש
echo "יוצר אפליקציית Flask עדכנית..."
cat > simple_flask_app.py << 'EOF'
#!/usr/bin/env python3
"""
אפליקציית Flask פשוטה לשירות הפרונטאנד העשיר
"""
import os
import sys
import json
import logging
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

# הגדרת לוגר
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# יצירת אפליקציית Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='')

# תיקיית העלאות
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# הגדרת פורט
PORT = int(os.environ.get('PORT', 5001))

@app.route('/health')
def health():
    """בדיקת בריאות המערכת"""
    return jsonify({"status": "ok", "message": "System is operational"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """העלאת קובץ"""
    logger.info("Processing file upload request")
    
    if 'file' not in request.files:
        logger.warning("No file part in request")
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"File saved: {file_path}")
        
        # טיפול בקובץ PDF
        if filename.lower().endswith('.pdf'):
            try:
                import PyPDF2
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    page_count = len(pdf_reader.pages)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                logger.info(f"PDF processed: {filename}, {page_count} pages")
            except Exception as e:
                logger.error(f"Error processing PDF: {e}")
        
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "document_id": filename.replace('.', '_'),
            "filename": filename
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """קבלת רשימת מסמכים"""
    # רשימת מסמכים מוקאפ
    documents = []
    
    # אם יש קבצים בתיקיית ההעלאות, הוסף אותם לרשימה
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
                doc_type = "unknown"
                if filename.lower().endswith('.pdf'):
                    doc_type = "PDF"
                elif filename.lower().endswith(('.xls', '.xlsx')):
                    doc_type = "Excel"
                elif filename.lower().endswith('.csv'):
                    doc_type = "CSV"
                    
                documents.append({
                    "id": filename.replace('.', '_'),
                    "filename": filename,
                    "upload_date": "2025-03-30T00:00:00",
                    "status": "completed",
                    "page_count": 1,
                    "language": "he",
                    "type": doc_type
                })
    
    # אם אין מסמכים, הוסף מסמך לדוגמה
    if not documents:
        documents.append({
            "id": "demo_document_1",
            "filename": "financial_report_2025.pdf",
            "upload_date": "2025-03-15T10:30:00",
            "status": "completed",
            "page_count": 12,
            "language": "he",
            "type": "PDF"
        })
        
    return jsonify(documents)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """משרת את אפליקציית הפרונטאנד"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    logger.info(f"Starting server on port {PORT}")
    app.run(debug=True, host='0.0.0.0', port=PORT)
EOF

# הרשאות הרצה
chmod +x simple_flask_app.py

# הרץ את האפליקציה
echo "מריץ את האפליקציה בפורט 5001..."
echo "גש לכתובת: http://localhost:5001 כדי לראות את הפרונטאנד העשיר"
python simple_flask_app.py
