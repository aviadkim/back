import os
import uuid
import logging
from datetime import datetime
from pymongo import MongoClient
from agent_framework.coordinator import AgentCoordinator

# Setup logging
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
client = MongoClient(MONGO_URI)
db = client.get_database()
sessions_collection = db.chat_sessions
messages_collection = db.chat_messages

# Initialize agent coordinator
try:
    agent_coordinator = AgentCoordinator()
except Exception as e:
    logger.error(f"Failed to initialize AgentCoordinator: {e}")
    agent_coordinator = None

def create_session():
    """
    Create a new chat session
    
    Returns:
        str: Session ID
    """
    session_id = str(uuid.uuid4())
    
    # Create session record
    session = {
        '_id': session_id,
        'created_at': datetime.now(),
        'last_active': datetime.now(),
        'message_count': 0
    }
    
    # Store session in MongoDB
    sessions_collection.insert_one(session)
    
    logger.info(f"Created new chat session: {session_id}")
    return session_id

def process_query(question, document_ids=None, session_id=None, language='he'):
    """
    Process a chat query using the agent framework
    
    Args:
        question (str): The question asked
        document_ids (list): Optional list of document IDs to query
        session_id (str): Optional session ID for conversation continuity
        language (str): Language code for the response
        
    Returns:
        tuple: (answer, metadata) - The answer and metadata about the processing
    """
    try:
        # Create session if needed
        if not session_id:
            session_id = create_session()
        
        # Update session last active time
        sessions_collection.update_one(
            {'_id': session_id},
            {'$set': {'last_active': datetime.now()},
             '$inc': {'message_count': 1}}
        )
        
        # Store the question
        message_id = str(uuid.uuid4())
        message = {
            '_id': message_id,
            'session_id': session_id,
            'timestamp': datetime.now(),
            'role': 'user',
            'content': question,
            'document_ids': document_ids or []
        }
        messages_collection.insert_one(message)
        
        # Use agent framework to process the query
        answer = "This is a placeholder response from the chatbot."
        metadata = {}
        
        if agent_coordinator:
            try:
                # Process query using agent framework
                result = agent_coordinator.process_query(question, document_ids, session_id, language)
                answer = result.get('answer', "No answer generated")
                metadata = result.get('metadata', {})
            except Exception as e:
                logger.error(f"Error in agent coordinator: {str(e)}")
                answer = f"Error processing query: {str(e)}"
        else:
            # Fallback responses when agent framework is not available
            if language == 'he':
                answer = "מערכת הסוכנים לא זמינה כרגע. אנא נסה שוב מאוחר יותר."
            else:
                answer = "The agent system is currently unavailable. Please try again later."
        
        # Store the answer
        response_id = str(uuid.uuid4())
        response = {
            '_id': response_id,
            'session_id': session_id,
            'timestamp': datetime.now(),
            'role': 'assistant',
            'content': answer,
            'metadata': metadata,
            'in_response_to': message_id
        }
        messages_collection.insert_one(response)
        
        return answer, metadata
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise

def get_chat_history(session_id):
    """
    Get chat history for a specific session
    
    Args:
        session_id (str): Session ID
        
    Returns:
        list: List of messages in the session
    """
    try:
        # Check if session exists
        session = sessions_collection.find_one({'_id': session_id})
        
        if not session:
            return None
        
        # Get messages for the session
        messages = list(messages_collection.find(
            {'session_id': session_id},
            {'_id': 1, 'timestamp': 1, 'role': 1, 'content': 1, 'metadata': 1}
        ).sort('timestamp', 1))
        
        # Convert MongoDB ObjectId and datetime to string for JSON serialization
        for msg in messages:
            if '_id' in msg and not isinstance(msg['_id'], str):
                msg['_id'] = str(msg['_id'])
            
            if 'timestamp' in msg and isinstance(msg['timestamp'], datetime):
                msg['timestamp'] = msg['timestamp'].isoformat()
        
        return messages
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise
