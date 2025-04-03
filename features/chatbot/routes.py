from flask import request, jsonify
import logging
from . import chatbot_bp
from .service import process_query, get_chat_history, create_session

logger = logging.getLogger(__name__)

@chatbot_bp.route('', methods=['POST'])
def chat():
    """
    Process a chat query against document(s)
    ---
    post:
      summary: Process a chat query
      description: Asks a question about document(s) and gets an AI-generated answer
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                question:
                  type: string
                  description: Question to ask about the documents
                document_ids:
                  type: array
                  items:
                    type: string
                  description: Optional list of document IDs to query (if not provided, queries all documents)
                session_id:
                  type: string
                  description: Optional session ID for conversation continuity
                language:
                  type: string
                  enum: [he, en]
                  default: he
                  description: Language for the response
      responses:
        200:
          description: Answer to the query
        400:
          description: Bad request
        500:
          description: Server error
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        question = data.get('question')
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        document_ids = data.get('document_ids', [])
        session_id = data.get('session_id')
        language = data.get('language', 'he')
        
        # Create a new session if none provided
        if not session_id:
            session_id = create_session()
        
        # Process the query
        answer, metadata = process_query(question, document_ids, session_id, language)
        
        return jsonify({
            'session_id': session_id,
            'answer': answer,
            'metadata': metadata
        })
        
    except Exception as e:
        logger.error(f"Error processing chat query: {str(e)}")
        return jsonify({'error': f'Error processing query: {str(e)}'}), 500

@chatbot_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session_history(session_id):
    """
    Get chat history for a specific session
    ---
    get:
      summary: Get chat history
      description: Returns the chat history for a specific session
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Chat history
        404:
          description: Session not found
        500:
          description: Server error
    """
    try:
        history = get_chat_history(session_id)
        
        if history is None:
            return jsonify({'error': 'Session not found'}), 404
            
        return jsonify({'history': history})
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({'error': f'Error retrieving chat history: {str(e)}'}), 500

@chatbot_bp.route('/suggest', methods=['POST'])
def suggest_questions():
    """
    Suggest questions based on document(s)
    ---
    post:
      summary: Suggest questions
      description: Suggests questions that can be asked about the document(s)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                document_ids:
                  type: array
                  items:
                    type: string
                  description: List of document IDs to generate suggestions for
                count:
                  type: integer
                  default: 5
                  description: Number of suggestions to generate
                language:
                  type: string
                  enum: [he, en]
                  default: he
                  description: Language for the suggestions
      responses:
        200:
          description: Suggested questions
        400:
          description: Bad request
        500:
          description: Server error
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        document_ids = data.get('document_ids', [])
        count = data.get('count', 5)
        language = data.get('language', 'he')
        
        # This would call a service function to generate suggestions
        # For now we'll return placeholders
        # In a real implementation, you would use the agent_framework
        suggestions = [
            "מה סך כל ההכנסות לשנת 2024?",
            "מה שיעור הרווח התפעולי?",
            "מהן ההתחייבויות העיקריות?",
            "מהי תחזית התזרים לשנה הבאה?",
            "מה היחס הפיננסי הנוכחי?"
        ]
        
        if language == 'en':
            suggestions = [
                "What is the total revenue for 2024?",
                "What is the operating profit margin?",
                "What are the main liabilities?",
                "What is the cash flow forecast for next year?",
                "What is the current financial ratio?"
            ]
        
        return jsonify({
            'suggestions': suggestions[:count]
        })
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return jsonify({'error': f'Error generating suggestions: {str(e)}'}), 500
