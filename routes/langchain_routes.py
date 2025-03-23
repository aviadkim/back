from flask import Blueprint, request, jsonify, current_app
import os
import logging
import uuid
from werkzeug.utils import secure_filename
from financial_document_processor import FinancialDocumentProcessor

langchain_routes = Blueprint('langchain_routes', __name__)
logger = logging.getLogger(__name__)

# יצירת מעבד מסמכים פיננסיים
try:
    # ניסיון ליצור את המעבד עם מפתח ה-API של Mistral
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    if mistral_api_key:
        financial_processor = FinancialDocumentProcessor(mistral_api_key=mistral_api_key)
        logger.info("FinancialDocumentProcessor initialized successfully")
    else:
        logger.warning("MISTRAL_API_KEY not found in environment variables")
        financial_processor = None
except Exception as e:
    logger.error(f"Error initializing FinancialDocumentProcessor: {str(e)}")
    financial_processor = None

@langchain_routes.route('/api/langchain/analyze', methods=['POST'])
def analyze_with_langchain():
    """ניתוח מסמך פיננסי באמצעות LangChain ו-Mistral AI."""
    if financial_processor is None:
        return jsonify({'error': 'LangChain processor not initialized. Please set MISTRAL_API_KEY environment variable.'}), 500
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400
    
    try:
        # יצירת מזהה ייחודי לעבודה זו
        job_id = str(uuid.uuid4())
        
        # שמירת הקובץ שהועלה באופן זמני
        temp_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'temp'), 'langchain')
        os.makedirs(temp_dir, exist_ok=True)
        
        # שמירת הקובץ
        filename = secure_filename(file.filename)
        file_path = os.path.join(temp_dir, f"{job_id}_{filename}")
        file.save(file_path)
        
        # עיבוד המסמך עם מעבד המסמכים הפיננסיים
        instruments = financial_processor.process_document(file_path)
        
        # המרת התוצאות למבנה JSON
        results = [instrument.dict() for instrument in instruments]
        
        # ניקוי קובץ זמני
        os.remove(file_path)
        
        return jsonify({
            'job_id': job_id,
            'filename': filename,
            'instruments_count': len(results),
            'instruments': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing document with LangChain: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_routes.route('/api/langchain/status', methods=['GET'])
def langchain_status():
    """בדיקת סטטוס מעבד המסמכים הפיננסיים."""
    status = {
        'langchain_available': financial_processor is not None,
        'mistral_api_key_set': os.environ.get("MISTRAL_API_KEY") is not None
    }
    
    return jsonify(status), 200
