import logging
import json
from flask import jsonify
import os
import google.generativeai as genai
from config import Config # Import Config to access API keys
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
        """Initialize the router service and Gemini client."""
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

        # Configure Gemini
        self.gemini_model = None
        if Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Or another suitable model
                logger.info("Gemini client configured successfully.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini client: {e}")
        else:
            logger.warning("GEMINI_API_KEY not found in environment. General chat LLM capabilities disabled.")
    
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
                error_msg = "אירעה שגיאה בעיבוד השאלה" if language == 'he' else f"An error occurred processing your query: {str(e)}"
                return jsonify({'error': str(e), 'response': error_msg})
        
        # If no documents or no agent coordinator, route to general chat assistant
        try:
            return self._route_to_general_chat(message, language)
        except Exception as e:
            logger.error(f"Error routing to general chat: {e}")
            error_msg = "אירעה שגיאה בעיבוד השאלה. אנא נסה שנית." if language == 'he' else "An error occurred processing your request. Please try again."
            return jsonify({'error': str(e), 'response': error_msg})
    
    def _route_to_general_chat(self, message, language):
        """
        Route to general chat using LLM when no documents are provided.

        Args:
            message (str): User message
            language (str): Language code ('he' or 'en')

        Returns:
            flask.Response: JSON response
        """
        logger.info(f"Routing to general chat LLM for message: {message[:50]}...")

        # Default fallback responses
        default_response_he = "אני עוזר מסמכים חכם. אנא העלה מסמך פיננסי כדי שאוכל לעזור לך לנתח אותו ולענות על שאלות ספציפיות."
        default_suggested_he = ["איך להעלות מסמך?", "אילו סוגי מסמכים אתה יכול לנתח?", "מה אתה יכול לעשות עם מסמכים פיננסיים?"]
        default_response_en = "I'm a smart document assistant. Please upload a financial document so I can help you analyze it and answer specific questions."
        default_suggested_en = ["How do I upload a document?", "What types of documents can you analyze?", "What can you do with financial documents?"]

        response_text = default_response_he if language == 'he' else default_response_en
        suggested_questions = default_suggested_he if language == 'he' else default_suggested_en

        if not self.gemini_model:
            logger.warning("Gemini model not available. Returning default response.")
            return jsonify({
                'response': response_text,
                'suggested_questions': suggested_questions
            })

        try:
            # Construct the prompt for Gemini
            prompt = f"""System Prompt: You are a helpful assistant for 'FinDoc Analyzer', a financial document analysis application. The user is interacting with you before uploading any specific documents. Your goal is to provide a welcoming and informative response, guiding them on how to use the application. Respond in {'Hebrew' if language == 'he' else 'English'}.

User Message: {message}

Task: Generate a concise and helpful response to the user's message. Also, provide 3 relevant follow-up questions a user might ask in this context. Structure your output STRICTLY as a JSON object with keys "response" (string) and "suggested_questions" (a list of 3 strings). Example JSON: {{"response": "...", "suggested_questions": ["...", "...", "..."]}}
"""
            # Call Gemini API
            gemini_response = self.gemini_model.generate_content(prompt)

            # Attempt to parse the JSON response from Gemini
            try:
                # Clean potential markdown code block fences
                cleaned_text = gemini_response.text.strip().removeprefix('```json').removesuffix('```').strip()
                llm_output = json.loads(cleaned_text)
                response_text = llm_output.get('response', response_text) # Use LLM response or fallback
                suggested_questions = llm_output.get('suggested_questions', suggested_questions) # Use LLM suggestions or fallback
                # Ensure suggested_questions is a list of strings
                if not isinstance(suggested_questions, list) or not all(isinstance(q, str) for q in suggested_questions):
                    suggested_questions = default_suggested_he if language == 'he' else default_suggested_en
                logger.info("Successfully parsed response from Gemini.")

            except (json.JSONDecodeError, AttributeError, TypeError) as parse_error:
                logger.error(f"Failed to parse JSON response from Gemini: {parse_error}. Raw response: {gemini_response.text}")
                # Fallback to default if parsing fails

        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            # Fallback to default response on API error

        return jsonify({
            'response': response_text,
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
