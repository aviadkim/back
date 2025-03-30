"""
Services for Document Chat Feature
"""

import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory data store (in a real app, this would be in a database)
_sessions = {}

def create_chat_session(user_id, documents=None):
    """
    Create a new chat session
    
    Args:
        user_id: ID of the user creating the session
        documents: List of document IDs to associate with the session
        
    Returns:
        str: Session ID
    """
    session_id = str(uuid.uuid4())
    
    _sessions[session_id] = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'documents': documents or [],
        'history': [
            {
                'role': 'assistant',
                'content': f'שלום! אני יכול לעזור לך לנתח את המסמכים שלך. מה תרצה לדעת?',
                'timestamp': datetime.now().isoformat()
            }
        ]
    }
    
    logger.info(f"Created chat session {session_id} for user {user_id} with documents {documents}")
    return session_id

def get_session_history(session_id):
    """
    Get the history of a chat session
    
    Args:
        session_id: ID of the session
        
    Returns:
        list: Chat history or None if session doesn't exist
    """
    session = _sessions.get(session_id)
    if not session:
        return None
    
    return session['history']

def process_query(session_id, query, context=None):
    """
    Process a user query
    
    Args:
        session_id: ID of the session
        query: User query text
        context: Additional context
        
    Returns:
        dict: Response with answer and metadata
    """
    # Create session if it doesn't exist
    if session_id not in _sessions:
        session_id = create_chat_session('anonymous')
    
    # Add user message to history
    _sessions[session_id]['history'].append({
        'role': 'user',
        'content': query,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate a response (in a real app, this would use an AI model)
    sample_responses = {
        'מה': 'אני יכול לנתח מסמכים פיננסיים, לחלץ נתונים מטבלאות, ולענות על שאלות לגבי התוכן.',
        'תן': 'הנה הנתונים שביקשת: [נתוני מסמך לדוגמה]',
        'איך': 'כדי לנתח מסמך, תעלה אותו דרך ממשק ההעלאה ואז תוכל לשאול שאלות ספציפיות.',
        'כמה': 'לפי הנתונים במסמך, הערך הוא כ-100,000 ש"ח.',
    }
    
    # Try to match the query to a predefined response
    answer = None
    for key, value in sample_responses.items():
        if key in query:
            answer = value
            break
    
    # Default response if no match found
    if not answer:
        answer = f"אני מבין שאתה שואל על '{query}'. אשמח לעזור, אבל אני צריך מידע נוסף או מסמך לנתח."
    
    # Add assistant response to history
    _sessions[session_id]['history'].append({
        'role': 'assistant',
        'content': answer,
        'timestamp': datetime.now().isoformat()
    })
    
    logger.info(f"Processed query for session {session_id}: {query[:50]}...")
    
    return {
        'answer': answer,
        'session_id': session_id,
        'model_used': 'demo_model',
        'sources': []  # In a real app, this would list document sources
    }

def get_suggested_questions(document_id):
    """
    Get suggested questions for a document
    
    Args:
        document_id: ID of the document
        
    Returns:
        list: Suggested questions
    """
    # In a real app, these would be generated based on document content
    suggested_questions = [
        {
            'id': f'sq_{document_id}_1',
            'text': 'מהם מספרי ה-ISIN במסמך?',
            'category': 'מזהים'
        },
        {
            'id': f'sq_{document_id}_2',
            'text': 'מהי התשואה השנתית המוצגת במסמך?',
            'category': 'ביצועים'
        },
        {
            'id': f'sq_{document_id}_3',
            'text': 'מהי חלוקת הנכסים בתיק?',
            'category': 'אלוקציה'
        },
        {
            'id': f'sq_{document_id}_4',
            'text': 'מהי החשיפה המטבעית של התיק?',
            'category': 'מטבעות'
        },
        {
            'id': f'sq_{document_id}_5',
            'text': 'מהן הנתונים הפיננסיים העיקריים במסמך?',
            'category': 'סיכום'
        }
    ]
    
    logger.info(f"Generated suggested questions for document {document_id}")
    return suggested_questions
