from flask import Blueprint, request, jsonify, send_file
import os
import json
import logging
import io
from werkzeug.utils import secure_filename
from typing import Dict, Any, List, Optional

from .services import pdf_scanning_service

# הגדרת לוגר
logger = logging.getLogger(__name__)

# הגדרת Blueprint
pdf_scanning_bp = Blueprint('pdf_scanning', __name__, url_prefix='/api/pdf')

@pdf_scanning_bp.route('/upload', methods=['POST'])
def upload_pdf():
    """
    העלאת וסריקת קובץ PDF
    """
    try:
        # בדיקה אם קיים קובץ בבקשה
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # בדיקה אם נבחר קובץ
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # קבלת שפה מבוקשת (ברירת מחדל: עברית)
        language = request.form.get('language', 'he')
        
        # בדיקת סוג הקובץ - חייב להיות PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400
        
        # עיבוד הקובץ
        result = pdf_scanning_service.scan_pdf(file, language)
        
        if not result:
            return jsonify({"error": "Error processing PDF"}), 500
        
        return jsonify({
            "message": "PDF processed successfully",
            "document_id": result.get("document_id", ""),
            "table_count": result.get("table_count", 0),
            "text_length": result.get("text_length", 0),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error uploading PDF: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error uploading PDF: {str(e)}"}), 500

@pdf_scanning_bp.route('/<document_id>', methods=['GET'])
def get_pdf_document(document_id):
    """
    קבלת פרטי מסמך PDF ספציפי
    """
    try:
        # קבלת שפה מבוקשת (ברירת מחדל: עברית)
        language = request.args.get('language', 'he')
        full_text = request.args.get('full_text', 'false').lower() == 'true'
        
        # קבלת המסמך
        document = pdf_scanning_service.get_document(document_id)
        
        if not document:
            error_message = "מסמך לא נמצא" if language == "he" else "Document not found"
            return jsonify({"error": error_message}), 404
        
        # אם לא ביקשו את הטקסט המלא, הסר אותו מהתשובה
        if not full_text and 'text_content' in document:
            # שלח רק תקציר של הטקסט
            if document['text_content']:
                document['text_preview'] = document['text_content'][:500] + '...'
            del document['text_content']
        
        message = "מסמך נטען בהצלחה" if language == "he" else "Document loaded successfully"
        
        return jsonify({
            "message": message,
            "document": document,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת מסמך: {str(e)}" if language == "he" else f"Error loading document: {str(e)}"
        return jsonify({"error": error_message}), 500

@pdf_scanning_bp.route('/', methods=['GET'])
def get_all_pdf_documents():
    """
    קבלת רשימת מסמכי PDF מעובדים
    """
    try:
        # קבלת שפה מבוקשת (ברירת מחדל: עברית)
        language = request.args.get('language', 'he')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # קבלת כל המסמכים
        documents = pdf_scanning_service.get_all_documents(limit, offset)
        
        # הסרת תוכן הטקסט המלא מהתשובה
        for doc in documents:
            if 'text_content' in doc:
                # שלח רק תקציר של הטקסט
                if doc['text_content']:
                    doc['text_preview'] = doc['text_content'][:200] + '...'
                del doc['text_content']
        
        message = "מסמכים נטענו בהצלחה" if language == "he" else "Documents loaded successfully"
        
        return jsonify({
            "message": message,
            "documents": documents,
            "count": len(documents),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת מסמכים: {str(e)}" if language == "he" else f"Error loading documents: {str(e)}"
        return jsonify({"error": error_message}), 500

@pdf_scanning_bp.route('/<document_id>/text', methods=['GET'])
def get_pdf_text(document_id):
    """
    קבלת הטקסט המלא של מסמך
    """
    try:
        # קבלת שפה מבוקשת (ברירת מחדל: עברית)
        language = request.args.get('language', 'he')
        format_type = request.args.get('format', 'json')
        
        # קבלת המסמך
        document = pdf_scanning_service.get_document(document_id)
        
        if not document:
            error_message = "מסמך לא נמצא" if language == "he" else "Document not found"
            return jsonify({"error": error_message}), 404
        
        text_content = document.get('text_content', '')
        
        # אם ביקשו טקסט פשוט
        if format_type.lower() == 'text':
            return text_content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
        # ברירת מחדל - החזרה כ-JSON
        message = "טקסט המסמך נטען בהצלחה" if language == "he" else "Document text loaded successfully"
        
        return jsonify({
            "message": message,
            "document_id": document_id,
            "text": text_content,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting document text {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת טקסט המסמך: {str(e)}" if language == "he" else f"Error loading document text: {str(e)}"
        return jsonify({"error": error_message}), 500

@pdf_scanning_bp.route('/<document_id>/tables', methods=['GET'])
def get_pdf_tables(document_id):
    """
    קבלת הטבלאות של מסמך
    """
    try:
        # קבלת שפה מבוקשת (ברירת מחדל: עברית)
        language = request.args.get('language', 'he')
        
        # קבלת המסמך
        document = pdf_scanning_service.get_document(document_id)
        
        if not document:
            error_message = "מסמך לא נמצא" if language == "he" else "Document not found"
            return jsonify({"error": error_message}), 404
        
        tables = document.get('tables', [])
        
        message = "טבלאות המסמך נטענו בהצלחה" if language == "he" else "Document tables loaded successfully"
        
        return jsonify({
            "message": message,
            "document_id": document_id,
            "tables": tables,
            "table_count": len(tables),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting document tables {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת טבלאות המסמך: {str(e)}" if language == "he" else f"Error loading document tables: {str(e)}"
        return jsonify({"error": error_message}), 500

@pdf_scanning_bp.route('/<document_id>/tables/<int:table_index>/export', methods=['GET'])
def export_table(document_id, table_index):
    """
    ייצוא טבלה ספציפית לקובץ אקסל
    """
    try:
        # קבלת המסמך
        document = pdf_scanning_service.get_document(document_id)
        
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # בדיקה אם יש טבלאות במסמך
        tables = document.get("tables", [])
        if table_index >= len(tables):
            return jsonify({"error": "Table not found"}), 404
        
        # קבלת נתוני הטבלה
        table_data = tables[table_index]
        
        # המרת נתוני הטבלה ל-DataFrame
        import pandas as pd
        import io
        
        # יצירת DataFrame מנתוני הטבלה
        if "rows" in table_data:
            # אם יש שורות מוגדרות, השתמש בהן
            df = pd.DataFrame([row.split() for row in table_data["rows"]])
            # הגדרת השורה הראשונה כשמות עמודות אם יש יותר משורה אחת
            if len(df) > 1:
                df.columns = df.iloc[0]
                df = df[1:]
        else:
            # אם אין מבנה שורות מוגדר, השתמש בתוכן הגולמי
            content_lines = table_data.get("content", "").split('\n')
            df = pd.DataFrame([line.split() for line in content_lines if line.strip()])
            # הגדרת השורה הראשונה כשמות עמודות אם יש יותר משורה אחת
            if len(df) > 1:
                df.columns = df.iloc[0]
                df = df[1:]
        
        # יצירת קובץ אקסל בזיכרון
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Table', index=False)
        
        output.seek(0)
        
        # שליחת הקובץ למשתמש
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{document_id}_table_{table_index}.xlsx"
        )
        
    except Exception as e:
        logger.error(f"Error exporting table {table_index} from document {document_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error exporting table: {str(e)}"}), 500
