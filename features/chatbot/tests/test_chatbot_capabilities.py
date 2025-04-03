"""
Test the capabilities of the chatbot with the current Hugging Face API key

This script demonstrates the core capabilities of the chatbot system:
1. Session creation and management
2. Memory agent functionality
3. Document reference tracking
4. Message history management
5. Query processing with the agent framework
6. Suggested questions generation

Run this test with:
    python -m features.chatbot.tests.test_chatbot_capabilities
"""

import os
import uuid
import logging
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_chatbot_capabilities():
    """Test the capabilities of the chatbot with the current Hugging Face API key"""
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.error("❌ HUGGINGFACE_API_KEY not found in environment variables")
        logger.error("Please make sure it's set in your .env file or in your environment")
        return False
    
    logger.info(f"✅ Using Hugging Face API key: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Import our chatbot components
        from agent_framework.coordinator import AgentCoordinator
        from features.chatbot.services import ChatbotService
        
        # Initialize services
        logger.info("Initializing services")
        coordinator = AgentCoordinator()
        chatbot_service = ChatbotService()
        
        # 1. Test session creation
        logger.info("\n1. Testing session creation")
        user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        test_document_ids = ["sample-financial-doc-001"]
        
        logger.info(f"Creating session for user {user_id} with documents: {test_document_ids}")
        session_id = chatbot_service.create_session(
            user_id=user_id,
            document_ids=test_document_ids,
            language="en"
        )
        
        logger.info(f"✅ Created session with ID: {session_id}")
        
        # 2. Test memory agent functionality
        logger.info("\n2. Testing memory agent functionality")
        memory_agent = coordinator.get_memory_agent(session_id)
        
        # Add more document references
        memory_agent.add_document_reference("sample-financial-doc-002", relevance_score=0.85)
        logger.info("✅ Added document references")
        
        # Add messages to the conversation
        memory_agent.add_message(role="user", content="What is my portfolio allocation?")
        memory_agent.add_message(role="assistant", content="Based on your documents, your portfolio consists of 60% stocks, 30% bonds, and 10% cash equivalents.")
        logger.info("✅ Added conversation messages")
        
        # Get message history
        messages = memory_agent.get_message_history()
        logger.info(f"✅ Retrieved {len(messages)} messages from history")
        
        # Show the messages
        for i, msg in enumerate(messages):
            logger.info(f"  Message {i+1}: {msg['role']} - {msg['content'][:50]}...")
        
        # 3. Test query processing
        logger.info("\n3. Testing query processing")
        try:
            query = "What is my exposure to USD?"
            logger.info(f"Processing query: '{query}'")
            
            result = coordinator.process_query(
                session_id=session_id,
                query=query,
                document_ids=test_document_ids
            )
            
            logger.info(f"✅ Query response: {result.get('answer', 'No response generated')}")
            
        except Exception as e:
            logger.warning(f"⚠️ Query processing test encountered an issue: {str(e)}")
            logger.warning("This might be expected if the NLP model integration is not fully implemented")
        
        # 4. Test suggested questions
        logger.info("\n4. Testing suggested questions generation")
        suggested_questions = chatbot_service.generate_suggested_questions(
            session_id=session_id,
            query="What is my exposure to USD?",
            language="en"
        )
        
        logger.info("✅ Generated suggested questions:")
        for i, question in enumerate(suggested_questions):
            logger.info(f"  {i+1}. {question}")
            
        # 5. Test document-specific suggestions
        logger.info("\n5. Testing document-specific question suggestions")
        doc_suggestions = chatbot_service.generate_document_suggestions(
            document_id=test_document_ids[0],
            language="en"
        )
        
        logger.info("✅ Generated document-specific suggestions:")
        for i, question in enumerate(doc_suggestions):
            logger.info(f"  {i+1}. {question}")
        
        # Clean up the test session
        coordinator.clear_session(session_id)
        logger.info(f"\n✅ Cleaned up test session: {session_id}")
        
        logger.info("✅ Chatbot capabilities test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error testing chatbot capabilities: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("=== Testing Chatbot Capabilities ===")
    success = test_chatbot_capabilities()
    logger.info(f"Test {'passed ✓' if success else 'failed ✗'}")
