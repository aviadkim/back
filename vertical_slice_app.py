import os
import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# הגדרת לוגר
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# יצירת אפליקציית Flask
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)  # אפשר CORS לכל הדומיינים

# טעינת הגדרות מקובץ .env
from dotenv import load_dotenv
load_dotenv()

# הגדרת תיקיית העלאות
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# רישום ה-blueprints של הפיצ'רים השונים
from features.pdf_scanning import pdf_scanning_bp
from features.document_chat import document_chat_bp
from features.table_extraction import table_extraction_bp

app.register_blueprint(pdf_scanning_bp)
app.register_blueprint(document_chat_bp)
app.register_blueprint(table_extraction_bp)

# נתיבי API גלובליים

@app.route('/health')
def health():
    """בדיקת בריאות המערכת"""
    logger.info("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "System is operational",
        "version": "4.1"
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """העלאת קובץ"""
    logger.info("File upload requested")
    
    if 'file' not in request.files:
        logger.warning("No file part in the request")
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        logger.warning("No selected file")
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        logger.info(f"File uploaded: {filename}")
        
        # בדיקה אם זה PDF ואם כן, שליחה לסריקה אוטומטית
        if filename.lower().endswith('.pdf'):
            from features.pdf_scanning.service import process_pdf
            result = process_pdf(file_path)
            return jsonify({
                "status": "success",
                "message": "File uploaded and processed successfully",
                "document_id": result["document_id"],
                "filename": filename,
                "details": result
            })
        
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "document_id": filename.replace('.', '_'),
            "filename": filename
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """קבלת רשימת מסמכים"""
    logger.info("Documents list requested")
    
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
                    "page_count": 1 if doc_type != "PDF" else 10,
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
    
    logger.info(f"Returning {len(documents)} documents")
    return jsonify(documents)

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """קבלת פרטי מסמך לפי מזהה"""
    logger.info(f"Document details requested: {document_id}")
    
    # המרת מזהה בחזרה לשם קובץ אם צריך
    if '_' in document_id:
        filename = document_id.replace('_', '.', 1)
    else:
        filename = document_id
    
    # ייצור נתוני דוגמה עבור המסמך
    document = {
        "metadata": {
            "id": document_id,
            "filename": filename,
            "upload_date": "2025-03-30T00:00:00",
            "status": "completed",
            "page_count": 10,
            "language": "he",
            "type": "PDF",
            "size_bytes": 1024000
        },
        "processed_data": {
            "isin_data": [
                {"isin": "US0378331005", "company": "Apple Inc.", "market": "NASDAQ", "type": "מניה"},
                {"isin": "US88160R1014", "company": "Tesla Inc.", "market": "NASDAQ", "type": "מניה"},
                {"isin": "DE000BAY0017", "company": "Bayer AG", "market": "XETRA", "type": "מניה"}
            ],
            "financial_data": {
                "is_financial": True,
                "document_type": "דו\"ח שנתי",
                "metrics": {
                    "assets": [
                        {"name": "סך נכסים", "value": 1200000, "unit": "₪"},
                        {"name": "נכסים נזילים", "value": 550000, "unit": "₪"}
                    ],
                    "returns": [
                        {"name": "תשואה שנתית", "value": 8.7, "unit": "%"},
                        {"name": "תשואה ממוצעת 5 שנים", "value": 7.2, "unit": "%"}
                    ],
                    "ratios": [
                        {"name": "יחס שארפ", "value": 1.3},
                        {"name": "יחס P/E ממוצע", "value": 22.4}
                    ]
                }
            },
            "tables": {
                "1": [
                    {
                        "id": f"{document_id}_table_1",
                        "name": "חלוקת נכסים",
                        "page": 1,
                        "header": ["סוג נכס", "אחוז מהתיק", "שווי (₪)"],
                        "rows": [
                            ["מניות", "45%", "450,000"],
                            ["אג\"ח ממשלתי", "30%", "300,000"],
                            ["אג\"ח קונצרני", "15%", "150,000"],
                            ["מזומן", "10%", "100,000"]
                        ]
                    }
                ],
                "2": [
                    {
                        "id": f"{document_id}_table_2",
                        "name": "התפלגות מטבעית",
                        "page": 2,
                        "header": ["מטבע", "אחוז מהתיק", "שווי (₪)"],
                        "rows": [
                            ["שקל (₪)", "60%", "600,000"],
                            ["דולר ($)", "25%", "250,000"],
                            ["אירו (€)", "10%", "100,000"],
                            ["אחר", "5%", "50,000"]
                        ]
                    }
                ]
            }
        }
    }
    
    logger.info(f"Returning document details for: {document_id}")
    return jsonify(document)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """משרת את אפליקציית הפרונטאנד"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# יצירת תיקיות מוקאפים לסוכנים חכמים
@app.route('/api/agent', methods=['POST'])
def agent_endpoint():
    """נקודת קצה למודל הסוכנים החכמים"""
    data = request.json
    
    # סימולציה של מודלים שונים
    model_name = data.get('model', 'gemini').lower()
    prompt = data.get('prompt', '')
    
    response = {
        "model": model_name,
        "status": "success",
        "generated_text": ""
    }
    
    if model_name == 'llama':
        response["generated_text"] = f"תשובה ממודל LLAMA: {prompt[:50]}..."
    elif model_name == 'gemini':
        response["generated_text"] = f"תשובה ממודל Gemini: {prompt[:50]}..."
    elif model_name == 'mistral':
        response["generated_text"] = f"תשובה ממודל Mistral: {prompt[:50]}..."
    else:
        response["generated_text"] = f"תשובה ממודל ברירת מחדל: {prompt[:50]}..."
    
    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting application on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
