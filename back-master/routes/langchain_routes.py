from flask import Blueprint, request, jsonify, current_app
import os
import uuid
import json
from datetime import datetime

# Import db instance from shared module
from shared.database import db as mongo_db # Renamed to avoid conflict if needed later
# Removed unused SQLAlchemy Document model import
# from models.document_models import Document
from agent_framework.coordinator import AgentCoordinator
from agent_framework.memory_agent import MemoryAgent

# Create blueprint
langchain_bp = Blueprint('langchain', __name__, url_prefix='/api')

# Create agent instances
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

# Removed in-memory chat_sessions dictionary

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
        
        # Create session metadata document
        session_data = {
            '_id': session_id, # Use session_id as MongoDB _id
            'created_at': datetime.utcnow(), # Use UTC time
            'language': language,
            'document_ids': document_ids.copy() if document_ids else [],
            # Messages are stored separately in 'chat_history' collection
        }
        
        # Store session metadata in MongoDB
        session_collection = "chat_sessions"
        stored_id = mongo_db.store_document(session_collection, session_data)
        
        if not stored_id:
            current_app.logger.error(f"Failed to store session metadata for session {session_id}")
            return jsonify({'error': 'Failed to create session in database'}), 500
            
        # Load documents into memory agent if provided
        if document_ids:
            doc_collection = "document_analysis_store" # Collection where MemoryAgent stores docs
            for doc_id in document_ids:
                # Fetch document metadata from MongoDB
                document_data = mongo_db.find_document(doc_collection, {'_id': doc_id})
                if document_data and 'analysis_path' in document_data and os.path.exists(document_data['analysis_path']):
                    # Load document into memory agent using the path from MongoDB
                    memory_agent.add_document(doc_id, document_data['analysis_path'])
                else:
                    current_app.logger.warning(f"Document metadata or analysis file not found for doc_id {doc_id} during session creation.")
        
        return jsonify({
            'success': True,
            'sessionId': session_id,
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating chat session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/session/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get chat session metadata and message history"""
    try:
        # Fetch session metadata from MongoDB
        session_collection = "chat_sessions"
        session_data = mongo_db.find_document(session_collection, {'_id': session_id})
        
        if not session_data:
            return jsonify({'error': 'Chat session not found'}), 404
            
        # Fetch chat messages from MongoDB
        # Convert ObjectId and datetime objects for JSON serialization if necessary
        messages = mongo_db.get_chat_history(session_id)
        serializable_messages = []
        for msg in messages:
            msg['_id'] = str(msg['_id']) # Convert ObjectId to string
            msg['timestamp'] = msg['timestamp'].isoformat() # Convert datetime to ISO string
            serializable_messages.append(msg)

        # Prepare response data
        response_session = {
            'id': session_data['_id'],
            'created_at': session_data['created_at'].isoformat(), # Convert datetime
            'language': session_data['language'],
            'document_ids': session_data['document_ids'],
        }
        
        return jsonify({
            'success': True,
            'session': response_session,
            'messages': serializable_messages, # Use fetched messages
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting chat session {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@langchain_bp.route('/chat/session/<session_id>/documents', methods=['POST'])
def update_session_documents(session_id):
    """Update documents associated with a chat session"""
    try:
        # Fetch session metadata from MongoDB
        session_collection = "chat_sessions"
        session_data = mongo_db.find_document(session_collection, {'_id': session_id})
        
        if not session_data:
            return jsonify({'error': 'Chat session not found'}), 404
            
        # Get request data
        data = request.json or {}
        new_document_ids_list = data.get('documentIds', []) # Renamed for clarity
        
        if not isinstance(new_document_ids_list, list):
            return jsonify({'error': 'documentIds must be an array'}), 400
            
        # --- Code below needs to be inside the try block ---
        # Get current document IDs from the fetched session data
        current_document_ids = session_data.get('document_ids', [])
        
        # Determine which documents to add and remove
        docs_to_add = [doc_id for doc_id in new_document_ids_list if doc_id not in current_document_ids]
        docs_to_remove = [doc_id for doc_id in current_document_ids if doc_id not in new_document_ids_list]

        # --- Update memory agent (logic remains similar) ---
        # Add new documents to memory agent
        doc_collection = "document_analysis_store" # Collection where MemoryAgent stores docs
        for doc_id in docs_to_add:
            # Fetch document metadata from MongoDB
            document_data = mongo_db.find_document(doc_collection, {'_id': doc_id})
            if document_data and 'analysis_path' in document_data and os.path.exists(document_data['analysis_path']):
                # Load document into memory agent using the path from MongoDB
                memory_agent.add_document(doc_id, document_data['analysis_path'])
            else:
                current_app.logger.warning(f"Document metadata or analysis file not found for doc_id {doc_id} during session update.")
        
        # Remove documents from memory agent
        for doc_id in docs_to_remove:
            memory_agent.forget_document(doc_id)
        
        # Update the document_ids list in the MongoDB session document
        update_success = mongo_db.update_document(
            session_collection,
            {'_id': session_id},
            {'document_ids': new_document_ids_list}
        )
        
        if not update_success:
             # Log an error, but maybe don't fail the whole request if memory agent was updated
             current_app.logger.warning(f"Failed to update document_ids in session {session_id} metadata, but memory agent changes applied.")

        return jsonify({
            'success': True,
            'documentIds': new_document_ids_list, # Return the new list
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
            
        # Fetch session metadata from MongoDB
        session_collection = "chat_sessions"
        session_data = mongo_db.find_document(session_collection, {'_id': session_id})
        
        if not session_data:
            return jsonify({'error': 'Chat session not found'}), 404
            
        language = session_data.get('language', 'he')
        session_document_ids = session_data.get('document_ids', [])
        
        # Save user message to DB
        user_message_id = mongo_db.save_chat_message(session_id, 'user', message)
        if not user_message_id:
             # Log error but potentially continue if history isn't critical for this query
             current_app.logger.error(f"Failed to save user message for session {session_id}")

        # Fetch recent chat history from DB for context
        # Note: The agent_coordinator might need adjustments to handle the DB message format
        chat_history_from_db = mongo_db.get_chat_history(session_id, limit=20) # Limit history length

        # Process query with agent coordinator
        # Use document_ids from request if provided, otherwise from session
        active_document_ids = document_ids if document_ids else session_document_ids
        result = agent_coordinator.process_query(
            query=message,
            document_ids=active_document_ids,
            language=language,
            chat_history=chat_history_from_db # Pass history from DB
        )
        
        # Save assistant response to DB
        assistant_response_content = result.get('answer', 'Sorry, I could not process that.')
        assistant_message_id = mongo_db.save_chat_message(session_id, 'assistant', assistant_response_content)
        if not assistant_message_id:
             current_app.logger.error(f"Failed to save assistant message for session {session_id}")
        
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
        # Fetch document metadata from MongoDB
        doc_collection = "document_analysis_store"
        document_data = mongo_db.find_document(doc_collection, {'_id': document_id})
        
        if not document_data:
            return jsonify({'error': 'Document not found in store'}), 404
            
        # Get document type from the metadata stored by MemoryAgent
        # Assuming MemoryAgent stores it in 'metadata.detected_document_type'
        document_type = document_data.get('metadata', {}).get('detected_document_type', 'other')
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
