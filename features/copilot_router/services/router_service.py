import logging
import json
from flask import jsonify
import os

# Import other services for routing
try:
    from agent_framework.coordinator import AgentCoordinator
except ImportError:
    print("Warning: Failed to import AgentCoordinator")
    AgentCoordinator = None

logger = logging.getLogger(__name__)

class CopilotRouterService:
    """
    Service for routing user requests to the appropriate specialized assistant.
    Acts as a central hub for directing queries to various features based on intent.
    """
    
    def __init__(self):
        """Initialize the router service."""
        self.agent_coordinator = None
        if AgentCoordinator:
            try:
                self.agent_coordinator = AgentCoordinator()
                logger.info("AgentCoordinator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize AgentCoordinator: {e}")
        else:
            logger.warning("AgentCoordinator not available, document-based chat will be limited")
        
        # Cache for document content
        self.document_cache = {}
    
    def route_request(self, message, context=None):
        """
        Route a request to the appropriate specialized assistant.
        
        Args:
            message (str): The user message
            context (dict, optional): Additional context for the request
                - document_ids: List of document IDs to provide context
                - language: Language code (default: 'he')
        
        Returns:
            flask.Response: JSON response to the client
        """
        if context is None:
            context = {}
        
        # Get language from context or default to Hebrew
        language = context.get('language', os.environ.get('DEFAULT_LANGUAGE', 'he'))
        
        # Get document IDs
        document_ids = context.get('document_ids', [])
        
        # Log the request
        logger.info(f"Routing request: message={message[:50]}... language={language}, document_ids={document_ids}")
        
        # Check for document_ids in the main request body too (frontend may send them there)
        if not document_ids and hasattr(context, 'get'):
            document_ids = context.get('document_ids', [])
        
        # If we have document IDs, use the agent coordinator to process the query
        if document_ids and self.agent_coordinator:
            try:
                # Convert chat history format if provided
                chat_history = context.get('chat_history', [])
                formatted_history = []
                for msg in chat_history:
                    if isinstance(msg, dict) and 'content' in msg and 'role' in msg:
                        formatted_history.append(msg)
                    elif isinstance(msg, dict) and 'text' in msg and 'sender' in msg:
                        # Convert from frontend format if needed
                        role = 'user' if msg.get('sender') == 'user' else 'assistant'
                        formatted_history.append({'role': role, 'content': msg.get('text', '')})
                
                # Process query with AI agent
                result = self.agent_coordinator.process_query(
                    query=message,
                    document_ids=document_ids,
                    language=language,
                    chat_history=formatted_history
                )
                
                # Return the result
                return jsonify({
                    'response': result.get('answer', ''),
                    'document_references': result.get('document_references', []),
                    'suggested_questions': result.get('suggested_questions', [])
                })
            
            except Exception as e:
                logger.error(f"Error processing query with agent coordinator: {e}")
                error_msg = language == 'he' \
                    ? f"אירעה שגיאה בעיבוד השאלה: {str(e)}" \
                    : f"An error occurred processing your query: {str(e)}"
                return jsonify({'error': error_msg, 'response': error_msg})
        
        # If no documents or no agent coordinator, route to general chat assistant
        try:
            return self._route_to_general_chat(message, language)
        except Exception as e:
            logger.error(f"Error routing to general chat: {e}")
            error_msg = language == 'he' \
                ? "אירעה שגיאה בעיבוד השאלה. אנא נסה שנית." \
                : "An error occurred processing your request. Please try again."
            return jsonify({'error': str(e), 'response': error_msg})
    
    def _route_to_general_chat(self, message, language):
        """
        Route to general chat when no documents are provided.
        
        Args:
            message (str): User message
            language (str): Language code
        
        Returns:
            flask.Response: JSON response
        """
        # Default responses for demo
        if language == 'he':
            response = "אני עוזר מסמכים חכם. אנא העלה מסמך פיננסי כדי שאוכל לעזור לך לנתח אותו ולענות על שאלות ספציפיות."
            suggested_questions = [
                "איך להעלות מסמך?",
                "אילו סוגי מסמכים אתה יכול לנתח?",
                "מה אתה יכול לעשות עם מסמכים פיננסיים?"
            ]
        else:
            response = "I'm a smart document assistant. Please upload a financial document so I can help you analyze it and answer specific questions."
            suggested_questions = [
                "How do I upload a document?",
                "What types of documents can you analyze?",
                "What can you do with financial documents?"
            ]
        
        # Additional handling for common queries
        lower_message = message.lower()
        
        # Simple Q&A for basic questions
        if any(term in lower_message for term in ['hello', 'hi', 'שלום', 'היי']):
            if language == 'he':
                response = "שלום! אני עוזר המסמכים החכם שלך. אני יכול לעזור לך לנתח מסמכים פיננסיים ולענות על שאלות לגביהם."
            else:
                response = "Hello! I'm your smart document assistant. I can help you analyze financial documents and answer questions about them."
        
        elif any(term in lower_message for term in ['help', 'עזרה']):
            if language == 'he':
                response = "אני יכול לעזור לך לנתח מסמכים פיננסיים. פשוט העלה מסמך (PDF, Excel או CSV) ואשתמש בבינה מלאכותית כדי לחלץ מידע חשוב ולענות על שאלות לגביו."
            else:
                response = "I can help you analyze financial documents. Simply upload a document (PDF, Excel, or CSV) and I'll use AI to extract important information and answer questions about it."
        
        return jsonify({
            'response': response,
            'suggested_questions': suggested_questions
        })

# Global router service instance
_router_service = None

def get_router_service():
    """
    Get or create a router service instance.
    
    Returns:
        CopilotRouterService: The router service instance
    """
    global _router_service
    if _router_service is None:
        _router_service = CopilotRouterService()
    return _router_service
