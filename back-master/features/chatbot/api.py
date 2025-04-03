from flask import Blueprint, request, jsonify
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .services import ChatbotService
from agent_framework.coordinator import AgentCoordinator

# הגדרת לוגר
logger = logging.getLogger(__name__)

# הגדרת Blueprint
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/api/chat')

# יצירת מופעים של השירותים
chatbot_service = ChatbotService()
agent_coordinator = AgentCoordinator()

@chatbot_bp.route('/session', methods=['POST'])
def create_session():
    """
    יצירת שיחה חדשה עם המערכת
    """
    try:
        # קבלת הפרמטרים מהבקשה
        data = request.json or {}
        user_id = data.get('user_id', 'anonymous')
        document_ids = data.get('document_ids', [])
        language = data.get('language', 'he')
        
        # יצירת שיחה חדשה
        session_id = chatbot_service.create_session(user_id, document_ids, language)
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "message": "שיחה חדשה נוצרה בהצלחה" if language == 'he' else "Chat session created successfully",
            "created_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@chatbot_bp.route('/query', methods=['POST'])
def process_query():
    """
    עיבוד שאילתה והחזרת תשובה
    """
    try:
        # קבלת הפרמטרים מהבקשה
        data = request.json or {}
        session_id = data.get('session_id')
        query = data.get('query')
        document_ids = data.get('document_ids', [])
        language = data.get('language', 'he')
        
        # בדיקת תקינות הפרמטרים
        if not session_id:
            error_message = "מזהה שיחה חסר" if language == 'he' else "Missing session ID"
            return jsonify({"success": False, "error": error_message}), 400
            
        if not query:
            error_message = "שאילתה חסרה" if language == 'he' else "Missing query"
            return jsonify({"success": False, "error": error_message}), 400
        
        # עיבוד השאילתה
        result = agent_coordinator.process_query(
            session_id=session_id,
            query=query,
            document_ids=document_ids,
            language=language
        )
        
        # קבלת שאלות המשך מומלצות
        suggested_questions = chatbot_service.generate_suggested_questions(
            session_id=session_id,
            query=query,
            language=language,
            result=result
        )
        
        # יצירת התשובה
        response = {
            "success": True,
            "session_id": session_id,
            "query": query,
            "answer": result.get("answer", ""),
            "document_references": result.get("document_references", []),
            "suggested_questions": suggested_questions,
            "timestamp": datetime.now().isoformat()
        }
        
        # אם יש טבלה שנוצרה, הוסף אותה לתשובה
        if "table" in result:
            response["table"] = result["table"]
            
        # אם יש תרשים שנוצר, הוסף אותו לתשובה
        if "chart" in result:
            response["chart"] = result["chart"]
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
        error_message = f"שגיאה בעיבוד השאילתה: {str(e)}" if language == 'he' else f"Error processing query: {str(e)}"
        return jsonify({"success": False, "error": error_message}), 500

@chatbot_bp.route('/sessions', methods=['GET'])
def get_sessions():
    """
    קבלת רשימת שיחות פעילות
    """
    try:
        user_id = request.args.get('user_id', 'anonymous')
        
        # קבלת רשימת שיחות
        sessions = agent_coordinator.get_active_sessions()
        
        # סינון לפי משתמש אם ניתן
        if user_id != 'anonymous':
            sessions = [s for s in sessions if chatbot_service.get_session_user(s["session_id"]) == user_id]
        
        return jsonify({
            "success": True,
            "sessions": sessions,
            "count": len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@chatbot_bp.route('/session/<session_id>', methods=['GET'])
def get_session_history(session_id):
    """
    קבלת היסטוריית שיחה
    """
    try:
        # קבלת פרמטרים
        limit = request.args.get('limit')
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                limit = None
        
        # קבלת סוכן הזיכרון לשיחה
        memory_agent = agent_coordinator.get_memory_agent(session_id)
        
        # קבלת היסטוריית השיחה
        message_history = memory_agent.get_message_history(limit)
        
        # הפוך את סדר ההודעות כך שהישנות יהיו למעלה והחדשות למטה
        message_history.reverse()
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "messages": message_history,
            "document_references": memory_agent.get_document_references()
        })
        
    except Exception as e:
        logger.error(f"Error getting session history for {session_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@chatbot_bp.route('/session/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """
    מחיקת שיחה
    """
    try:
        # מחיקת השיחה
        success = agent_coordinator.clear_session(session_id)
        
        if success:
            # מחיקת המיפוי בשירות הצ'אטבוט
            chatbot_service.remove_session(session_id)
            
            return jsonify({
                "success": True,
                "message": f"Session {session_id} cleared successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to clear session {session_id}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@chatbot_bp.route('/documents/<document_id>/query', methods=['POST'])
def query_document(document_id):
    """
    שאילת שאלה ספציפית על מסמך
    """
    try:
        # קבלת הפרמטרים מהבקשה
        data = request.json or {}
        query = data.get('query')
        language = data.get('language', 'he')
        
        # בדיקת תקינות הפרמטרים
        if not query:
            error_message = "שאילתה חסרה" if language == 'he' else "Missing query"
            return jsonify({"success": False, "error": error_message}), 400
        
        # יצירת שיחה זמנית
        session_id = chatbot_service.create_temporary_session([document_id], language)
        
        # עיבוד השאילתה
        result = agent_coordinator.process_query(
            session_id=session_id,
            query=query,
            document_ids=[document_id],
            language=language
        )
        
        # יצירת התשובה
        response = {
            "success": True,
            "document_id": document_id,
            "query": query,
            "answer": result.get("answer", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # ניקוי השיחה הזמנית
        agent_coordinator.clear_session(session_id)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error querying document {document_id}: {str(e)}", exc_info=True)
        error_message = f"שגיאה בשאילת המסמך: {str(e)}" if language == 'he' else f"Error querying document: {str(e)}"
        return jsonify({"success": False, "error": error_message}), 500

@chatbot_bp.route('/document-suggestions/<document_id>', methods=['GET'])
def get_document_suggestions(document_id):
    """
    קבלת שאלות מומלצות למסמך ספציפי
    """
    try:
        language = request.args.get('language', 'he')
        
        # קבלת שאלות מומלצות
        suggestions = chatbot_service.generate_document_suggestions(document_id, language)
        
        return jsonify({
            "success": True,
            "document_id": document_id,
            "suggestions": suggestions
        })
        
    except Exception as e:
        logger.error(f"Error getting document suggestions for {document_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
