from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import json
from datetime import datetime

from models.document_models import Document, db
from agent_framework.coordinator import AgentCoordinator
from agent_framework.memory_agent import MemoryAgent

# Create blueprint
langchain_bp = Blueprint('langchain', __name__, url_prefix='/api')

# Create agent instances
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

# Chat sessions storage
# In a production environment, this should be stored in a database
chat_sessions = {}

@langchain_bp.route('/chat/session', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        # Get request data
        data = request.json or {}
        language = data.get('language', 'he')
        document_ids = data.get('documentIds', [])
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session
        chat_sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'language': language,
            'document_ids': document_ids.copy() if document_ids else [],
            'messages': [],
        }
        
        # Load documents into memory agent if provided
        if document_ids:
            for doc_id in document_ids:
                # Load document if it exists
                document = Document.query.get(doc_id)
                if document and document.analysis_path and os.path.exists(document.analysis_path):
                    # Load document into memory agent
                    memory_agent.add_document(doc_id, document.analysis_path)
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating chat session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/session/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get chat session history"""
    try:
        # Check if session exists
        if session_id not in chat_sessions:
            return jsonify({'error': 'Chat session not found'}), 404
            
        session = chat_sessions[session_id]
        
        return jsonify({
            'success': True,
            'session': {
                'id': session['id'],
                'created_at': session['created_at'],
                'language': session['language'],
                'document_ids': session['document_ids'],
            },
            'messages': session['messages'],
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/session/<session_id>/documents', methods=['POST'])
def update_session_documents(session_id):
    """Update documents for a chat session"""
    try:
        # Check if session exists
        if session_id not in chat_sessions:
            return jsonify({'error': 'Chat session not found'}), 404
            
        # Get request data
        data = request.json or {}
        document_ids = data.get('documentIds', [])
        
        if not isinstance(document_ids, list):
            return jsonify({'error': 'documentIds must be an array'}), 400
            
        # Get current document IDs
        current_document_ids = chat_sessions[session_id]['document_ids']
        
        # Get new document IDs to add
        new_document_ids = [doc_id for doc_id in document_ids if doc_id not in current_document_ids]
        
        # Get document IDs to remove
        remove_document_ids = [doc_id for doc_id in current_document_ids if doc_id not in document_ids]
        
        # Update memory agent
        for doc_id in new_document_ids:
            # Load document if it exists
            document = Document.query.get(doc_id)
            if document and document.analysis_path and os.path.exists(document.analysis_path):
                # Load document into memory agent
                memory_agent.add_document(doc_id, document.analysis_path)
        
        # Remove documents from memory agent
        for doc_id in remove_document_ids:
            memory_agent.forget_document(doc_id)
        
        # Update session
        chat_sessions[session_id]['document_ids'] = document_ids
        
        return jsonify({
            'success': True,
            'documentIds': document_ids,
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error updating chat session documents {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/query', methods=['POST'])
def chat_query():
    """Process a chat query"""
    try:
        # Get request data
        data = request.json or {}
        session_id = data.get('sessionId')
        message = data.get('message')
        document_ids = data.get('documentIds', [])
        
        # Validate data
        if not session_id:
            return jsonify({'error': 'sessionId is required'}), 400
            
        if not message:
            return jsonify({'error': 'message is required'}), 400
            
        # Check if session exists
        if session_id not in chat_sessions:
            return jsonify({'error': 'Chat session not found'}), 404
            
        session = chat_sessions[session_id]
        language = session.get('language', 'he')
        
        # Add user message to session
        user_message = {
            'role': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat(),
        }
        
        chat_sessions[session_id]['messages'].append(user_message)
        
        # Process query with agent coordinator
        result = agent_coordinator.process_query(
            query=message,
            document_ids=document_ids if document_ids else session['document_ids'],
            language=language,
            chat_history=session['messages']
        )
        
        # Add assistant response to session
        assistant_message = {
            'role': 'assistant',
            'content': result['answer'],
            'timestamp': datetime.now().isoformat(),
            'document_references': result.get('document_references', []),
        }
        
        chat_sessions[session_id]['messages'].append(assistant_message)
        
        return jsonify({
            'success': True,
            'response': result['answer'],
            'document_references': result.get('document_references', []),
            'suggested_questions': result.get('suggested_questions', []),
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error processing chat query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/document-suggestions/<document_id>', methods=['GET'])
def document_suggestions(document_id):
    """Get suggested questions for a document"""
    try:
        # Get document
        document = Document.query.get(document_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
            
        # Get document type
        document_type = document.document_type
        language = request.args.get('language', 'he')
        
        # Generate suggestions based on document type
        suggestions = []
        
        if document_type == 'bankStatement':
            if language == 'he':
                suggestions = [
                    'מה היתרה בחשבון?',
                    'מהן ההוצאות הגדולות ביותר בחודש האחרון?',
                    'כמה כסף הוצאתי על מצרכים?',
                    'הראה לי את כל העברות מעל 1000 ש"ח',
                ]
            else:
                suggestions = [
                    'What is my account balance?',
                    'What are my largest expenses last month?',
                    'How much money did I spend on groceries?',
                    'Show me all transactions over 1000 NIS',
                ]
        elif document_type == 'investmentReport':
            if language == 'he':
                suggestions = [
                    'מה שווי תיק ההשקעות שלי?',
                    'מהי הקצאת הנכסים שלי?',
                    'אילו השקעות הניבו את התשואה הטובה ביותר ברבעון האחרון?',
                    'מהן העמלות שאני משלם על ההשקעות שלי?',
                ]
            else:
                suggestions = [
                    'What is my portfolio value?',
                    'What is my asset allocation?',
                    'Which investments performed best last quarter?',
                    'What fees am I paying on my investments?',
                ]
        else:
            # Default questions for any document
            if language == 'he':
                suggestions = [
                    'על מה המסמך הזה?',
                    'מהם המספרים העיקריים במסמך זה?',
                    'תוכל לסכם עבורי את המסמך הזה?',
                    'האם יש תובנות פיננסיות מהמסמך הזה?',
                ]
            else:
                suggestions = [
                    'What is this document about?',
                    'What are the key numbers in this document?',
                    'Can you summarize this document for me?',
                    'Are there any financial insights from this document?',
                ]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting document suggestions for {document_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/tables/generate', methods=['POST'])
def generate_table():
    """Generate a table from document data"""
    try:
        # Get request data
        data = request.json or {}
        name = data.get('name')
        table_type = data.get('type', 'summary')
        document_ids = data.get('documentIds', [])
        columns = data.get('columns', [])
        filters = data.get('filters', [])
        language = data.get('language', 'he')
        
        # Validate data
        if not name:
            return jsonify({'error': 'name is required'}), 400
            
        if not document_ids:
            return jsonify({'error': 'documentIds is required'}), 400
            
        if not columns:
            return jsonify({'error': 'columns is required'}), 400
            
        # Generate table spec
        table_spec = {
            'name': name,
            'type': table_type,
            'columns': columns,
            'filters': filters,
            'language': language,
        }
        
        # Generate table with agent coordinator
        result = agent_coordinator.generate_table(
            document_ids=document_ids,
            table_spec=table_spec
        )
        
        return jsonify({
            'success': True,
            'tableData': result['table_data'],
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error generating table: {str(e)}")
        return jsonify({'error': str(e)}), 500
