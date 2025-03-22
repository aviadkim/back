from flask import Blueprint, request, jsonify
from flask import current_app, send_from_directory  # Separated imports
import os
import logging
from agent_framework import AgentCoordinator
from werkzeug.utils import secure_filename
from services.document_analyzer import analyze_pdf

document_routes = Blueprint('document_routes', __name__)
logger = logging.getLogger(__name__)

# יצירת מתאם סוכנים
agent_coordinator = AgentCoordinator()

@document_routes.route('/api/documents/process', methods=['POST'])
def process_document():
    """עיבוד מסמך באמצעות מסגרת הסוכנים."""
    if 'file' not in request.files:
        return jsonify({'error': 'לא סופק קובץ'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'לא נבחר קובץ'}), 400
        
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'רק קבצי PDF נתמכים'}), 400
    
    try:
        # שמירת הקובץ שהועלה באופן זמני
        temp_file_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(temp_file_path)
        
        # עיבוד המסמך עם מתאם הסוכנים
        results = agent_coordinator.process_document(temp_file_path)
        
        # ניקוי קובץ זמני
        os.remove(temp_file_path)
        
        return jsonify({
            'status': 'success',
            'document_id': 'doc_' + str(id(results)),  # במערכת אמיתית, השתמש במזהה מסמך מתאים
            'page_count': len(results.get('document_content', {})),
            'table_count': sum(len(tables) for tables in results.get('tables', {}).values()),
            'message': 'המסמך עובד בהצלחה'
        }), 200
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד המסמך: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_routes.route('/api/documents/<document_id>/available-fields', methods=['GET'])
def get_available_fields(document_id):
    """קבלת שדות זמינים להתאמת טבלה."""
    try:
        # במערכת אמיתית, קבל שדות ספציפיים למסמך
        # בינתיים, החזר סט סטנדרטי של שדות
        fields = [
            'security_type',
            'isin_number',
            'security_name',
            'current_price',
            'total_value',
            'portfolio_weight',
            'yield_percent',
            'maturity_date',
            'total_return',
            'performance',
            'currency',
            'credit_rating',
            'sector'
        ]
        
        return jsonify({
            'document_id': document_id,
            'fields': fields
        }), 200
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת שדות זמינים: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_routes.route('/api/documents/<document_id>/generate-table', methods=['POST'])
def generate_custom_table(document_id):
    """יצירת טבלה מותאמת אישית על סמך מפרט המשתמש."""
    try:
        query_spec = request.json
        if not query_spec:
            return jsonify({'error': 'לא סופק מפרט שאילתה'}), 400
            
        # יצירת הטבלה באמצעות מתאם הסוכנים
        result = agent_coordinator.generate_custom_table(document_id, query_spec)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"שגיאה ביצירת טבלה מותאמת אישית: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_routes.route('/api/documents/<document_id>/natural-language-query', methods=['POST'])
def process_natural_language_query(document_id):
    """עיבוד שאילתה בשפה טבעית ליצירת טבלה מותאמת אישית."""
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'לא סופקה שאילתה'}), 400
            
        query_text = data['query']
        
        # עיבוד השאילתה באמצעות מתאם הסוכנים
        result = agent_coordinator.process_natural_language_query(document_id, query_text)
        
        if 'error' in result:
            return jsonify(result), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"שגיאה בעיבוד שאילתה בשפה טבעית: {str(e)}")
        return jsonify({'error': str(e)}), 500

@document_routes.route('/api/documents/analyze', methods=['POST'])
def analyze_document():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check if file is empty
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload a PDF file'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the PDF
        analysis_result = analyze_pdf(filepath)
        
        return jsonify({
            'message': 'File analyzed successfully',
            'filename': filename,
            'analysis': analysis_result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@document_routes.route('/api/documents/<filename>')
def get_document(filename):
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404
