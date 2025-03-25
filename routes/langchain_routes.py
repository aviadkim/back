from flask import Blueprint, request, jsonify
import os
import json
import logging
from datetime import datetime
from agent_framework import AgentCoordinator

# הגדרת לוגר
logger = logging.getLogger(__name__)

# יצירת Blueprint
langchain_routes = Blueprint('langchain_routes', __name__)

# יצירת מתאם הסוכנים
agent_coordinator = AgentCoordinator()

@langchain_routes.route('/api/chat', methods=['POST'])
def chat():
    """
    נקודת קצה לצ'אט עם המערכת
    """
    try:
        # קבלת נתוני הבקשה
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # חילוץ המידע הנדרש מהבקשה
        question = data.get('question')
        session_id = data.get('session_id')
        language = data.get('language', 'he')
        document_ids = data.get('document_ids', [])
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # אם לא סופק מזהה שיחה, יצור חדש
        if not session_id:
            session_id = agent_coordinator.get_memory_agent().session_id
        
        # עיבוד השאלה
        result = agent_coordinator.process_query(
            session_id=session_id,
            query=question,
            document_ids=document_ids,
            language=language
        )
        
        return jsonify({
            "session_id": session_id,
            "question": question,
            "answer": result["answer"],
            "language": language,
            "document_references": result["document_references"]
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error processing chat: {str(e)}"}), 500

@langchain_routes.route('/api/sessions', methods=['GET'])
def get_sessions():
    """
    קבלת רשימת שיחות פעילות
    """
    try:
        language = request.args.get('language', 'he')
        
        # קבלת רשימת השיחות
        sessions = agent_coordinator.get_active_sessions()
        
        message = "שיחות נטענו בהצלחה" if language == "he" else "Sessions loaded successfully"
        
        return jsonify({
            "message": message,
            "sessions": sessions,
            "count": len(sessions),
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting sessions: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת שיחות: {str(e)}" if language == "he" else f"Error loading sessions: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    קבלת פרטי שיחה ספציפית
    """
    try:
        language = request.args.get('language', 'he')
        
        # קבלת סוכן הזיכרון לשיחה
        memory_agent = agent_coordinator.get_memory_agent(session_id)
        
        # קבלת היסטוריית ההודעות
        message_history = memory_agent.get_message_history()
        
        # קבלת הפניות למסמכים
        document_references = memory_agent.get_document_references()
        
        # קבלת סיכום הזיכרון
        summary = memory_agent.get_memory_summary()
        
        message = "שיחה נטענה בהצלחה" if language == "he" else "Session loaded successfully"
        
        return jsonify({
            "message": message,
            "session_id": session_id,
            "message_history": message_history,
            "document_references": document_references,
            "summary": summary,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בטעינת שיחה: {str(e)}" if language == "he" else f"Error loading session: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    מחיקת שיחה ספציפית
    """
    try:
        language = request.args.get('language', 'he')
        
        # מחיקת השיחה
        success = agent_coordinator.clear_session(session_id)
        
        if not success:
            error_message = "שגיאה במחיקת שיחה" if language == "he" else "Error deleting session"
            return jsonify({"error": error_message}), 500
        
        message = "שיחה נמחקה בהצלחה" if language == "he" else "Session deleted successfully"
        
        return jsonify({
            "message": message,
            "session_id": session_id,
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה במחיקת שיחה: {str(e)}" if language == "he" else f"Error deleting session: {str(e)}"
        return jsonify({"error": error_message}), 500

@langchain_routes.route('/api/analyze', methods=['POST'])
def analyze_document():
    """
    ניתוח מסמך ושאלה ספציפית
    """
    try:
        # קבלת נתוני הבקשה
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # חילוץ המידע הנדרש מהבקשה
        document_id = data.get('document_id')
        question = data.get('question')
        session_id = data.get('session_id')
        language = data.get('language', 'he')
        
        if not document_id:
            return jsonify({"error": "No document_id provided"}), 400
            
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        # אם לא סופק מזהה שיחה, יצור חדש
        if not session_id:
            session_id = agent_coordinator.get_memory_agent().session_id
        
        # עיבוד השאלה עם הפניה למסמך ספציפי
        result = agent_coordinator.process_query(
            session_id=session_id,
            query=question,
            document_ids=[document_id],
            language=language
        )
        
        return jsonify({
            "session_id": session_id,
            "document_id": document_id,
            "question": question,
            "answer": result["answer"],
            "language": language
        })
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": f"Error analyzing document: {str(e)}"}), 500

@langchain_routes.route('/api/health', methods=['GET'])
def ai_health():
    """
    בדיקת זמינות מערכת ה-AI
    """
    try:
        # בדיקת מפתחות API
        huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
        mistral_api_key = os.environ.get('MISTRAL_API_KEY')
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        # בדיקת תיקיות נדרשות
        required_dirs = [
            os.path.join('data', 'memory'),
            os.path.join('data', 'embeddings'),
            os.path.join('data', 'templates')
        ]
        
        dir_status = {}
        for dir_path in required_dirs:
            dir_status[dir_path] = os.path.exists(dir_path)
        
        # מידע על מפתחות API
        api_keys = {
            "huggingface": bool(huggingface_api_key),
            "mistral": bool(mistral_api_key),
            "openai": bool(openai_api_key)
        }
        
        return jsonify({
            "status": "ok",
            "message": "AI system is operational",
            "api_keys": api_keys,
            "directories": dir_status,
            "coordinator": {
                "active_sessions": len(agent_coordinator.active_memory_agents)
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in AI health check: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"AI system error: {str(e)}"}), 500
