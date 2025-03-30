"""
Routes for Document Chat Feature
"""

from flask import request, jsonify
from . import document_chat_bp
from .service import create_chat_session, get_session_history, process_query, get_suggested_questions

@document_chat_bp.route('/api/chat/sessions', methods=['POST'])
def create_session():
    """Create a new chat session"""
    try:
        data = request.json
        user_id = data.get('userId', 'anonymous')
        documents = data.get('documents', [])
        
        session_id = create_chat_session(user_id, documents)
        
        return jsonify({
            'status': 'success',
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@document_chat_bp.route('/api/chat/sessions/<session_id>/history', methods=['GET'])
def get_history(session_id):
    """Get chat history for a session"""
    try:
        history = get_session_history(session_id)
        
        if not history:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@document_chat_bp.route('/api/chat/sessions/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message in a chat session"""
    try:
        data = request.json
        query = data.get('message')
        context = data.get('context', {})
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Message is required'
            }), 400
        
        response = process_query(session_id, query, context)
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'response': response
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@document_chat_bp.route('/api/chat/documents/<document_id>/suggestions', methods=['GET'])
def suggestions(document_id):
    """Get suggested questions for a document"""
    try:
        suggestions = get_suggested_questions(document_id)
        
        return jsonify({
            'status': 'success',
            'document_id': document_id,
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
