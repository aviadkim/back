from flask import Blueprint, request, jsonify
import os
import json
import logging
from agent_framework.coordinator import AgentCoordinator

# הגדרת לוגר
logger = logging.getLogger(__name__)

# יצירת Blueprint
langchain_routes = Blueprint('langchain_routes', __name__)

# יצירת מתאם הסוכנים עם מפתח API
try:
    coordinator = AgentCoordinator(api_key=os.getenv('HUGGINGFACE_API_KEY', None))
    logger.info("AgentCoordinator initialized successfully")
except Exception as e:
    logger.error(f"Error initializing AgentCoordinator: {str(e)}")
    # יצירת מתאם דמה שמחזיר תשובות סטטיות
    class DummyCoordinator:
        def answer_question(self, **kwargs):
            return {
                "answer": "זוהי תשובת דמה. המערכת אינה מחוברת למודל AI בזמן זה.",
                "sources": [],
                "conversation_id": kwargs.get("conversation_id", "dummy_conversation"),
                "language": kwargs.get("language", "he")
            }
        
        def process_document(self, **kwargs):
            return True
        
        def get_document_summary(self, document_id, **kwargs):
            return {"summary": "סיכום דמה", "document_id": document_id}
        
        def clear_conversation(self, conversation_id):
            return True
        
        def set_language(self, language):
            return True
    
    coordinator = DummyCoordinator()
    logger.warning("Using DummyCoordinator due to initialization error")

@langchain_routes.route('/api/chat', methods=['POST'])
def chat():
    """
    נקודת קצה לצ'אט עם המסמכים
    
    Request Body:
    - question: שאלת המשתמש
    - document_ids: רשימת מזהי מסמכים (אופציונלי)
    - conversation_id: מזהה שיחה (אופציונלי)
    - language: שפה מבוקשת (he/en, ברירת מחדל: he)
    
    Returns:
    - תשובה מבוססת מסמכים
    """
    try:
        data = request.json
        logger.info(f"Received chat request: {data}")
        
        question = data.get('question')
        document_ids = data.get('document_ids', [])
        conversation_id = data.get('conversation_id')
        language = data.get('language', 'he')  # ברירת מחדל היא עברית
        
        if not question:
            error_message = "חסרה שאלה" if language == "he" else "Missing question"
            return jsonify({"error": error_message}), 400
        
        try:
            response = coordinator.answer_question(
                question=question, 
                document_ids=document_ids, 
                conversation_id=conversation_id,
                language=language
            )
            return jsonify(response)
        except Exception as e:
            logger.error(f"Error in answer_question: {str(e)}")
            error_message = f"שגיאה: {str(e)}" if language == "he" else f"Error: {str(e)}"
            return jsonify({"error": error_message}), 500
    except Exception as e:
        logger.error(f"General error in chat endpoint: {str(e)}")
        return jsonify({"error": f"General error: {str(e)}"}), 500

@langchain_routes.route('/api/process_document', methods=['POST'])
def upload_document():
    """
    נקודת קצה להעלאת מסמך לעיבוד
    
    Request Body:
    - file: קובץ להעלאה
    - metadata: מטה-דאטה נוסף על המסמך (אופציונלי)
    - language: שפת המסמך (he/en, ברירת מחדל: he)
    
    Returns:
    - סטטוס העלאה ומזהה מסמך
    """
    language = request.form.get('language', 'he')  # ברירת מחדל היא עברית
    
    if 'file' not in request.files:
        error_message = "לא נשלח קובץ" if language == "he" else "No file sent"
        return jsonify({"error": error_message}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        error_message = "לא נבחר קובץ" if language == "he" else "No file selected"
        return jsonify({"error": error_message}), 400
    
    try:
        # קבלת מטה-דאטה נוסף אם יש
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except:
                metadata = {}
        
        # שמירת הקובץ למיקום זמני
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)
        
        # קריאת תוכן הקובץ
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # עיבוד המסמך
        document_id = os.path.basename(file_path)
        success = coordinator.process_document(
            document_id=document_id, 
            content=content,
            metadata=metadata,
            language=language
        )
        
        if success:
            success_message = "מסמך הועלה בהצלחה" if language == "he" else "Document uploaded successfully"
            return jsonify({
                "message": success_message,
                "document_id": document_id
            })
        else:
            error_message = "שגיאה בעיבוד המסמך" if language == "he" else "Error processing document"
            return jsonify({"error": error_message}), 500
            
    except Exception as e:
        error_message = f"שגיאה: {str(e)}" if language == "he" else f"Error: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/document/<document_id>', methods=['GET'])
def get_document_summary(document_id):
    """
    נקודת קצה לקבלת סיכום מסמך
    
    URL Params:
    - document_id: מזהה המסמך
    
    Query Params:
    - language: שפה מבוקשת (he/en, ברירת מחדל: he)
    
    Returns:
    - סיכום המסמך ומידע נוסף
    """
    language = request.args.get('language', 'he')  # ברירת מחדל היא עברית
    
    try:
        summary = coordinator.get_document_summary(document_id, language=language)
        return jsonify(summary)
    except Exception as e:
        error_message = f"שגיאה: {str(e)}" if language == "he" else f"Error: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/conversation/<conversation_id>', methods=['DELETE'])
def clear_conversation(conversation_id):
    """
    נקודת קצה למחיקת היסטוריית שיחה
    
    URL Params:
    - conversation_id: מזהה השיחה למחיקה
    
    Query Params:
    - language: שפה מבוקשת (he/en, ברירת מחדל: he)
    
    Returns:
    - סטטוס מחיקה
    """
    language = request.args.get('language', 'he')  # ברירת מחדל היא עברית
    
    try:
        success = coordinator.clear_conversation(conversation_id)
        
        if success:
            success_message = "השיחה נמחקה בהצלחה" if language == "he" else "Conversation cleared successfully"
            return jsonify({"message": success_message})
        else:
            error_message = "השיחה לא נמצאה" if language == "he" else "Conversation not found"
            return jsonify({"error": error_message}), 404
            
    except Exception as e:
        error_message = f"שגיאה: {str(e)}" if language == "he" else f"Error: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/language', methods=['POST'])
def set_language():
    """
    נקודת קצה לשינוי שפת ברירת המחדל של המערכת
    
    Request Body:
    - language: שפה לשינוי (he/en)
    
    Returns:
    - סטטוס שינוי השפה
    """
    data = request.json
    language = data.get('language')
    
    if not language:
        return jsonify({"error": "Missing language parameter"}), 400
    
    try:
        success = coordinator.set_language(language)
        
        if success:
            if language == "he":
                return jsonify({"message": "שפת המערכת שונתה לעברית"})
            else:
                return jsonify({"message": "System language changed to English"})
        else:
            return jsonify({"error": "Invalid language. Supported languages: he, en"}), 400
            
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@langchain_routes.route('/api/health', methods=['GET'])
def health_check():
    """
    נקודת קצה לבדיקת תקינות המערכת
    
    Query Params:
    - language: שפה מבוקשת (he/en, ברירת מחדל: he)
    
    Returns:
    - סטטוס המערכת
    """
    language = request.args.get('language', 'he')  # ברירת מחדל היא עברית
    
    # Check if we're using the dummy coordinator
    using_dummy = isinstance(coordinator, DummyCoordinator)
    
    if using_dummy:
        status = "warning"
        status_message = "שירותי AI מוגבלים - משתמש במודל דמה" if language == "he" else "AI services limited - using dummy model"
    else:
        status = "ok"
        status_message = "שירותי AI פעילים" if language == "he" else "AI services operational"
    
    status_language = "עברית" if language == "he" else "English"
    
    return jsonify({
        "status": status,
        "message": status_message,
        "language": status_language
    })
