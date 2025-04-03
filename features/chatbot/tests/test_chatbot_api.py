"""
Tests for the chatbot API endpoints

This script tests the HTTP API endpoints for the chatbot feature:
1. Session creation
2. Query processing
3. Session history retrieval
4. Session clearing

Run this test with:
    python -m pytest features/chatbot/tests/test_chatbot_api.py -v
"""

import json
import pytest
from flask import Flask
from features.chatbot.api import chatbot_bp

# Mock the chatbot service for testing
class MockChatbotService:
    def create_session(self, user_id, document_ids=None, language='he'):
        return "test-session-id"
    
    def process_query(self, session_id, query, document_ids=None, language='he'):
        return {
            "session_id": session_id,
            "answer": f"Mock answer to: {query}",
            "document_references": [],
            "suggested_questions": ["What is my portfolio allocation?", "How is my performance this year?"]
        }
    
    def get_session_user(self, session_id):
        return "test-user"
        
    def generate_suggested_questions(self, session_id, query, language='he', result=None):
        return ["What is my portfolio allocation?", "How is my performance this year?"]
    
    def remove_session(self, session_id):
        return True

# Mock the agent coordinator for testing
class MockAgentCoordinator:
    def process_query(self, session_id, query, document_ids=None, language='he'):
        return {
            "answer": f"Mock coordinator answer to: {query}",
            "document_references": []
        }
    
    def get_memory_agent(self, session_id):
        return MockMemoryAgent()
    
    def get_active_sessions(self):
        return [
            {"session_id": "test-session-1", "created_at": "2023-01-01T00:00:00"},
            {"session_id": "test-session-2", "created_at": "2023-01-02T00:00:00"}
        ]
    
    def clear_session(self, session_id):
        return True

# Mock the memory agent for testing
class MockMemoryAgent:
    def get_message_history(self, limit=None):
        return [
            {"role": "user", "content": "Test question?", "timestamp": "2023-01-01T00:00:00"},
            {"role": "assistant", "content": "Test answer.", "timestamp": "2023-01-01T00:00:01"}
        ]
    
    def get_document_references(self):
        return [
            {"document_id": "test-doc-1", "relevance_score": 0.9, "timestamp": "2023-01-01T00:00:00"}
        ]

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Register the blueprint
    app.register_blueprint(chatbot_bp)
    
    # Replace the actual services with our mocks
    import features.chatbot.api
    features.chatbot.api.chatbot_service = MockChatbotService()
    features.chatbot.api.agent_coordinator = MockAgentCoordinator()
    
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
    assert "created_at" in data

def test_process_query(client):
    """Test processing a query"""
    response = client.post(
        '/api/chat/query',
        json={
            "session_id": "test-session-id",
            "query": "What's in my portfolio?",
            "document_ids": ["doc1"]
        }
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "Mock" in data["answer"]
    assert len(data["suggested_questions"]) == 2

def test_process_query_missing_params(client):
    """Test processing a query with missing parameters"""
    # Missing session_id
    response = client.post(
        '/api/chat/query',
        json={
            "query": "What's in my portfolio?"
        }
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False
    
    # Missing query
    response = client.post(
        '/api/chat/query',
        json={
            "session_id": "test-session-id"
        }
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data["success"] is False

def test_get_sessions(client):
    """Test retrieving active sessions"""
    response = client.get('/api/chat/sessions?user_id=test-user')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["sessions"]) == 2

def test_get_session_history(client):
    """Test retrieving session history"""
    response = client.get('/api/chat/session/test-session-id')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert len(data["messages"]) == 2
    assert data["session_id"] == "test-session-id"

def test_clear_session(client):
    """Test clearing a session"""
    response = client.delete('/api/chat/session/test-session-id')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert "cleared" in data["message"].lower()
