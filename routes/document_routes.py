from flask import Blueprint, request, jsonify, send_file
import os
import json
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import io

# שינינו את הייבוא כך שיתמוך גם ב-PDFProcessor וגם ב-extract_text_from_pdf
from utils.pdf_processor import PDFProcessor
from utils import extract_text_from_pdf

# הגדרת לוגר
logger = logging.getLogger(__name__)

# יצירת Blueprint
document_routes = Blueprint('document_routes', __name__)

# הגדרת תיקיית העלאות
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv', 'docx', 'doc', 'txt'}

# בדיקה אם סיומת הקובץ מותרת
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# נתיב להעלאת קובץ
@document_routes.route('/api/upload', methods=['POST'])
def upload_file():
    """
    העלאת קובץ ועיבודו
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
        
        # בדיקה אם סוג הקובץ מותר
        if file and allowed_file(file.filename):
            # יצירת שם קובץ בטוח
            filename = secure_filename(file.filename)
            
            # הוספת חותמת זמן וזיהוי ייחודי לשם הקובץ כדי למנוע התנגשויות
            unique_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # יצירת שם קובץ חדש עם חותמת זמן ו-UUID
            basename, extension = os.path.splitext(filename)
            new_filename = f"{basename}_{timestamp}_{unique_id}{extension}"
            
            # נתיב מלא לשמירת הקובץ
            file_path = os.path.join(UPLOAD_FOLDER, new_filename)
            
            # שמירת הקובץ
            file.save(file_path)
            logger.info(f"File saved: {file_path}")
            
            # עיבוד הקובץ בהתאם לסוג
            if extension.lower() == '.pdf':
                # עיבוד PDF
                return process_pdf(file_path, language)
            elif extension.lower() in ['.xlsx', '.xls']:
                # עיבוד קובץ אקסל
                return process_excel(file_path, language)
            elif extension.lower() == '.csv':
                # עיבוד קובץ CSV
                return process_csv(file_path, language)
            else:
                # סוגי קבצים אחרים
                return jsonify({
                    "message": "File uploaded successfully, but processing not implemented for this file type",
                    "document_id": os.path.basename(file_path),
                    "language": language
                })
                
        else:
            return jsonify({"error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
            
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500

def process_pdf(file_path, language):
    """
    עיבוד קובץ PDF
    """
    try:
        # יצירת מעבד PDF
        pdf_processor = PDFProcessor(ocr_enabled=True, lang="heb+eng" if language == "he" else "eng")
        
        # חילוץ טקסט
        text = pdf_processor.extract_text(file_path)
        
        # חילוץ טבלאות
        tables = pdf_processor.extract_tables(file_path)
        
        # חילוץ מידע פיננסי
        financial_data = pdf_processor.extract_financial_data(file_path)
        
        # יצירת מזהה מסמך
        document_id = os.path.basename(file_path)
        
        # שמירת הנתונים המעובדים
        processed_data = {
            "document_id": document_id,
            "text": text,
            "tables": tables,
            "financial_data": financial_data,
            "file_path": file_path,
            "language": language,
            "processing_date": datetime.now().isoformat()
        }
        
        # שמירת הנתונים המעובדים לקובץ JSON
        json_path = os.path.join('data', f"{document_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"PDF processed successfully: {document_id}")
        
        return jsonify({
            "message": "PDF processed successfully",
            "document_id": document_id,
            "table_count": len(tables),
            "text_length": len(text),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500

def process_excel(file_path, language):
    """
    עיבוד קובץ אקסל
    """
    try:
        # קריאת קובץ אקסל
        xls = pd.ExcelFile(file_path)
        
        # קריאת כל הגיליונות
        sheets = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            sheets[sheet_name] = df.to_dict(orient='records')
        
        # יצירת מזהה מסמך
        document_id = os.path.basename(file_path)
        
        # שמירת הנתונים המעובדים
        processed_data = {
            "document_id": document_id,
            "sheets": sheets,
            "file_path": file_path,
            "language": language,
            "processing_date": datetime.now().isoformat()
        }
        
        # שמירת הנתונים המעובדים לקובץ JSON
        json_path = os.path.join('data', f"{document_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Excel processed successfully: {document_id}")
        
        return jsonify({
            "message": "Excel processed successfully",
            "document_id": document_id,
            "sheet_count": len(sheets),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error processing Excel: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing Excel: {str(e)}"}), 500

def process_csv(file_path, language):
    """
    עיבוד קובץ CSV
    """
    try:
        # ניסיון לקרוא עם קידוד UTF-8
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # אם זה נכשל, ננסה עם קידוד ISO-8859-8 (עברית)
            df = pd.read_csv(file_path, encoding='ISO-8859-8')
        
        # יצירת מזהה מסמך
        document_id = os.path.basename(file_path)
        
        # המרת DataFrame למילון
        data = df.to_dict(orient='records')
        
        # שמירת הנתונים המעובדים
        processed_data = {
            "document_id": document_id,
            "data": data,
            "file_path": file_path,
            "language": language,
            "processing_date": datetime.now().isoformat()
        }
        
        # שמירת הנתונים המעובדים לקובץ JSON
        json_path = os.path.join('data', f"{document_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"CSV processed successfully: {document_id}")
        
        return jsonify({
            "message": "CSV processed successfully",
            "document_id": document_id,
            "row_count": len(data),
            "column_count": len(df.columns),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing CSV: {str(e)}"}), 500

# נתיב לקבלת רשימת מסמכים
@document_routes.route('/api/documents', methods=['GET'])
def get_documents():
    """
    קבלת רשימת המסמכים המעובדים
    """
    try:
        language = request.args.get('language', 'he')
        
        # קריאת קבצי JSON מתיקיית data
        documents = []
        data_dir = 'data'
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                            doc_data = json.load(f)
                            
                            # יצירת תקציר מסמך
                            doc_summary = {
                                "document_id": doc_data.get("document_id", filename),
                                "processing_date": doc_data.get("processing_date", ""),
                                "language": doc_data.get("language", "unknown"),
                                "file_path": doc_data.get("file_path", "")
                            }
                            
                            # הוספת מידע נוסף בהתאם לסוג הקובץ
                            if "tables" in doc_data:
                                doc_summary["type"] = "PDF"
                                doc_summary["table_count"] = len(doc_data.get("tables", []))
                                doc_summary["text_length"] = len(doc_data.get("text", ""))
                            elif "sheets" in doc_data:
                                doc_summary["type"] = "Excel"
                                doc_summary["sheet_count"] = len(doc_data.get("sheets", {}))
                            elif "data" in doc_data:
                                doc_summary["type"] = "CSV"
                                doc_summary["row_count"] = len(doc_data.get("data", []))
                            
                            documents.append(doc_summary)
                    except Exception as e:
                        logger.error(f"Error reading document JSON {filename}: {str(e)}")
        
        # מיון לפי תאריך עיבוד (החדש ביותר קודם)
        documents.sort(key=lambda x: x.get("processing_date", ""), reverse=True)
        
        message = "מסמכים נטענו בהצלחה" if language == "he" else "Documents loaded successfully"
        
        return jsonify({
            "message": message,
            "documents": documents,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת מסמכים: {str(e)}" if language == "he" else f"Error loading documents: {str(e)}"
        return jsonify({"error": error_message}), 500

# נתיב לקבלת פרטי מסמך
@document_routes.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """
    קבלת פרטי מסמך ספציפי
    """
    try:
        language = request.args.get('language', 'he')
        
        # בדיקה אם קובץ JSON קיים
        json_path = os.path.join('data', f"{document_id}.json")
        
        if not os.path.exists(json_path):
            error_message = "מסמך לא נמצא" if language == "he" else "Document not found"
            return jsonify({"error": error_message}), 404
        
        # קריאת קובץ JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            document_data = json.load(f)
        
        message = "מסמך נטען בהצלחה" if language == "he" else "Document loaded successfully"
        
        return jsonify({
            "message": message,
            "document": document_data,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting document {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת מסמך: {str(e)}" if language == "he" else f"Error loading document: {str(e)}"
        return jsonify({"error": error_message}), 500

# נתיב לייצוא טבלה לאקסל
@document_routes.route('/api/export/<document_id>/table/<int:table_index>', methods=['GET'])
def export_table(document_id, table_index):
    """
    ייצוא טבלה ספציפית לקובץ אקסל
    """
    try:
        # בדיקה אם קובץ JSON קיים
        json_path = os.path.join('data', f"{document_id}.json")
        
        if not os.path.exists(json_path):
            return jsonify({"error": "Document not found"}), 404
        
        # קריאת קובץ JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            document_data = json.load(f)
        
        # בדיקה אם יש טבלאות במסמך
        if "tables" not in document_data or table_index >= len(document_data["tables"]):
            return jsonify({"error": "Table not found"}), 404
        
        # קבלת נתוני הטבלה
        table_data = document_data["tables"][table_index]
        
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

# נתיב למחיקת מסמך
@document_routes.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    מחיקת מסמך ספציפי
    """
    try:
        language = request.args.get('language', 'he')
        
        # בדיקה אם קובץ JSON קיים
        json_path = os.path.join('data', f"{document_id}.json")
        
        if not os.path.exists(json_path):
            error_message = "מסמך לא נמצא" if language == "he" else "Document not found"
            return jsonify({"error": error_message}), 404
        
        # קריאת קובץ JSON לקבלת נתיב הקובץ המקורי
        with open(json_path, 'r', encoding='utf-8') as f:
            document_data = json.load(f)
        
        # נתיב הקובץ המקורי
        original_file_path = document_data.get("file_path", "")
        
        # מחיקת קובץ JSON
        os.remove(json_path)
        
        # מחיקת הקובץ המקורי אם הוא קיים
        if original_file_path and os.path.exists(original_file_path):
            os.remove(original_file_path)
        
        message = "מסמך נמחק בהצלחה" if language == "he" else "Document deleted successfully"
        
        return jsonify({
            "message": message,
            "document_id": document_id,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה במחיקת מסמך: {str(e)}" if language == "he" else f"Error deleting document: {str(e)}"
        return jsonify({"error": error_message}), 500
