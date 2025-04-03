from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
import sys
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from agent_framework.aws_integration import AWSAgentIntegration
from config.aws_config import USE_AWS_STORAGE

# יצירת Blueprint
aws_api = Blueprint('aws_api', __name__)

# יצירת לוגר
logger = logging.getLogger(__name__)

# יצירת מופע של אינטגרציית AWS
aws_integration = AWSAgentIntegration()

@aws_api.route('/upload', methods=['POST'])
def upload_document():
    """העלאת מסמך לעיבוד"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    language = request.form.get('language', 'auto')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)

        # יצירת תיקיית temp אם לא קיימת
        os.makedirs('temp', exist_ok=True)

        # שמירת הקובץ בתיקייה זמנית
        temp_path = os.path.join('temp', filename)
        file.save(temp_path)

        try:
            # עיבוד המסמך באמצעות AWS
            result = aws_integration.process_document(temp_path, language=language)

            # מחיקת הקובץ הזמני
            os.remove(temp_path)

            return jsonify({
                'document_id': result['document_id'],
                'status': 'processing',
                'message': 'Document received and processing'
            }), 202

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")

            # מחיקת הקובץ הזמני אם קיים
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format'}), 400

@aws_api.route('/documents', methods=['GET'])
def get_documents():
    """קבלת רשימת מסמכים"""
    try:
        documents = aws_integration.dynamodb_service.get_documents()
        return jsonify(documents), 200
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        return jsonify({'error': str(e)}), 500

@aws_api.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """קבלת פרטי מסמך"""
    try:
        document_data = aws_integration.get_document_data(document_id)
        return jsonify(document_data), 200
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        return jsonify({'error': str(e)}), 500

@aws_api.route('/documents/<document_id>/ask', methods=['POST'])
def ask_question(document_id):
    """שאילת שאלה על מסמך"""
    try:
        data = request.json
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400

        question = data['question']
        result = aws_integration.ask_question(document_id, question)

        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error asking question: {str(e)}")
        return jsonify({'error': str(e)}), 500

@aws_api.route('/documents/<document_id>/tables', methods=['GET'])
def get_tables(document_id):
    """קבלת טבלאות ממסמך"""
    try:
        tables = aws_integration.extract_tables(document_id)
        return jsonify(tables), 200
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        return jsonify({'error': str(e)}), 500