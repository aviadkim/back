"""
Tests for the chatbot API
"""
import json
import pytest
from flask import Flask
from features.chatbot.api import chatbot_bp
from features.chatbot.services import ChatbotService

# Mock the chatbot service for testing
class MockChatbotService:
    def create_session(self, user_id, document_ids=None, language='he'):
        return "test-session-id"
    
    def process_query(self, session_id, query, document_ids=None, language='he'):
        return {
            "session_id": session_id,
            "answer": f"Mock answer to: {query}",
            "document_references": [],
            "suggested_questions": ["Follow-up question 1?", "Follow-up question 2?"]
        }
    
    def get_chat_history(self, session_id):
        return [
            {"role": "user", "content": "Test question?"},
            {"role": "assistant", "content": "Test answer."}
        ]

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Register the blueprint
    app.register_blueprint(chatbot_bp)
    
    # Replace the actual service with our mock
    import features.chatbot.api
    features.chatbot.api.chatbot_service = MockChatbotService()
    
    with app.test_client() as client:
        yield client

def test_create_session(client):
    """Test creating a new chat session"""
    response = client.post(
        '/api/chat/session',
        json={"user_id": "test-user", "document_ids": ["doc1", "doc2"]}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["session_id"] == "test-session-id"

def test_process_query(client):
    """Test processing a query"""
    response = client.post(
        '/api/chat/query',
        json={
            "session_id": "test-session-id",
            "query": "What's in my portfolio?"
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "Mock answer to:" in data["answer"]
    assert len(data["suggested_questions"]) == 2

def test_get_chat_history(client):
    """Test retrieving chat history"""
    response = client.get('/api/chat/history/test-session-id')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["history"]) == 2
    assert data["history"][0]["role"] == "user"
    assert data["history"][1]["role"] == "assistant"
