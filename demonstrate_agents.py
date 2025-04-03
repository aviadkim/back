"""
Demonstration of agent capabilities

This script demonstrates the capabilities of all agents in the financial document
analysis system, showing how they work together to process queries about financial
documents.
"""

import os
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def demonstrate_agent_capabilities():
    """
    Demonstrate the capabilities of all agents in the system
    """
    # Load environment variables
    load_dotenv()
    
    # Ensure Hugging Face API key is available
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    if not api_key:
        logger.error("HUGGINGFACE_API_KEY not found in environment variables")
        return False
    
    logger.info(f"Using Hugging Face API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Import our agent components
    try:
        from agent_framework.coordinator import AgentCoordinator
        from agent_framework.memory_agent import MemoryAgent
        from agent_framework.nlp_agent import NaturalLanguageQueryAgent
        from agent_framework.table_generator import CustomTableGenerator
        from features.chatbot.services import ChatbotService
        
        logger.info("Successfully imported agent framework components")
    except ImportError as e:
        logger.error(f"Error importing agent components: {str(e)}")
        logger.error("Make sure you're running this script from the project root directory")
        return False
    
    # Initialize key components
    logger.info("\n=== Initializing Agent Framework Components ===")
    coordinator = AgentCoordinator()
    nlp_agent = NaturalLanguageQueryAgent()
    table_generator = CustomTableGenerator()
    chatbot_service = ChatbotService()
    
    # Create unique identifiers for this demonstration
    demo_id = uuid.uuid4().hex[:8]
    user_id = f"demo-user-{demo_id}"
    
    # 1. Demonstrate ChatbotService capabilities
    logger.info("\n=== 1. CHATBOT SERVICE CAPABILITIES ===")
    
    # Create a chat session
    logger.info("Creating a new chat session...")
    try:
        session_id = chatbot_service.create_session(
            user_id=user_id,
            document_ids=["demo-financial-statement-001"],
            language="en"
        )
        logger.info(f"Created session with ID: {session_id}")
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        session_id = f"fallback-session-{demo_id}"
        logger.info(f"Using fallback session ID: {session_id}")
    
    # Generate suggested questions for a document
    logger.info("\nGenerating suggested questions for a financial document...")
    try:
        suggestions = chatbot_service.generate_document_suggestions(
            document_id="demo-financial-statement-001",
            language="en"
        )
        logger.info("Document-specific suggested questions:")
        for i, question in enumerate(suggestions, 1):
            logger.info(f"  {i}. {question}")
    except Exception as e:
        logger.error(f"Error generating document suggestions: {str(e)}")
    
    # 2. Demonstrate Memory Agent capabilities
    logger.info("\n=== 2. MEMORY AGENT CAPABILITIES ===")
    
    # Get the memory agent for our session
    try:
        memory_agent = coordinator.get_memory_agent(session_id)
        logger.info(f"Retrieved memory agent for session {session_id}")
        
        # Add document references
        logger.info("Adding document references...")
        memory_agent.add_document_reference("demo-financial-statement-001", relevance_score=0.95)
        memory_agent.add_document_reference("demo-investment-portfolio-002", relevance_score=0.85)
        
        # Add conversation history
        logger.info("\nSimulating a conversation...")
        conversation = [
            ("user", "What is my current asset allocation?"),
            ("assistant", "Based on your financial statements, your current asset allocation is 60% stocks, 30% bonds, and 10% cash equivalents."),
            ("user", "What's my exposure to USD?"),
            ("assistant", "Your portfolio has a 45% exposure to USD, primarily through US equities and dollar-denominated bonds.")
        ]
        
        for role, content in conversation:
            memory_agent.add_message(role=role, content=content)
            logger.info(f"Added {role} message: \"{content}\"")
        
        # Retrieve conversation history
        logger.info("\nRetrieving conversation history...")
        history = memory_agent.get_message_history()
        logger.info(f"Retrieved {len(history)} messages")
        
        # Retrieve document references
        logger.info("\nRetrieving document references...")
        doc_refs = memory_agent.get_document_references()
        logger.info(f"Retrieved {len(doc_refs)} document references:")
        for i, ref in enumerate(doc_refs, 1):
            logger.info(f"  {i}. {ref['document_id']} (relevance: {ref['relevance_score']})")
        
        # Store and retrieve context
        logger.info("\nStoring context information...")
        memory_agent.store_context("risk_profile", "moderate")
        memory_agent.store_context("investment_horizon", "long-term")
        
        logger.info("Retrieving context information...")
        risk_profile = memory_agent.get_context("risk_profile")
        investment_horizon = memory_agent.get_context("investment_horizon")
        logger.info(f"Risk profile: {risk_profile}, Investment horizon: {investment_horizon}")
    except Exception as e:
        logger.error(f"Error demonstrating memory agent capabilities: {str(e)}")
    
    # 3. Demonstrate NLP Agent capabilities
    logger.info("\n=== 3. NLP AGENT CAPABILITIES ===")
    
    # Process a natural language query
    logger.info("Processing natural language query...")
    query = "Show me all bonds with yield greater than 5% in USD"
    
    # Use the NLP agent to process the query
    try:
        structured_query = nlp_agent.process_query(query)
        
        logger.info(f"Structured query results:")
        logger.info(f"  Columns: {structured_query.get('columns', [])}")
        logger.info(f"  Filters: {structured_query.get('filters', [])}")
        logger.info(f"  Sort by: {structured_query.get('sort_by', {})}")
        logger.info(f"  Group by: {structured_query.get('group_by')}")
    except Exception as e:
        logger.error(f"Error processing query with NLP agent: {str(e)}")
    
    # 4. Demonstrate Table Generator capabilities
    logger.info("\n=== 4. TABLE GENERATOR CAPABILITIES ===")
    
    # Sample financial data
    logger.info("Generating a custom table from financial data...")
    financial_data = [
        {"security_type": "bond", "name": "US Treasury 10Y", "yield_percent": 4.2, "maturity_date": "2033-05-15", "currency": "USD", "credit_rating": "AAA"},
        {"security_type": "bond", "name": "Corporate Bond A", "yield_percent": 5.3, "maturity_date": "2028-10-20", "currency": "USD", "credit_rating": "BBB+"},
        {"security_type": "bond", "name": "Corporate Bond B", "yield_percent": 6.1, "maturity_date": "2029-03-15", "currency": "USD", "credit_rating": "BB"},
        {"security_type": "bond", "name": "Government Bond C", "yield_percent": 3.8, "maturity_date": "2030-11-30", "currency": "EUR", "credit_rating": "AA-"},
        {"security_type": "stock", "name": "Tech Company X", "dividend_yield": 1.2, "sector": "Technology", "currency": "USD"},
        {"security_type": "stock", "name": "Bank Y", "dividend_yield": 3.5, "sector": "Financials", "currency": "EUR"},
        {"security_type": "etf", "name": "S&P 500 ETF", "expense_ratio": 0.04, "category": "Equity", "currency": "USD"}
    ]
    
    # Create a specification for the table
    table_spec = {
        "columns": ["name", "yield_percent", "maturity_date", "currency", "credit_rating"],
        "filters": [
            {"field": "security_type", "operator": "=", "value": "bond"},
            {"field": "yield_percent", "operator": ">", "value": 5.0},
            {"field": "currency", "operator": "=", "value": "USD"}
        ],
        "sort_by": {"field": "yield_percent", "direction": "desc"}
    }
    
    try:
        # Generate the table
        table = table_generator.generate_custom_table(financial_data, table_spec)
        
        logger.info(f"Generated table with {table.get('count', 0)} rows:")
        logger.info(f"  Headers: {table.get('headers', [])}")
        if table.get('rows'):
            for row in table.get('rows', []):
                logger.info(f"  Row: {row}")
    except Exception as e:
        logger.error(f"Error generating custom table: {str(e)}")
    
    # 5. Demonstrate Agent Coordinator capabilities
    logger.info("\n=== 5. AGENT COORDINATOR CAPABILITIES ===")
    
    # Process a query using the coordinator
    logger.info("Processing a query through the agent coordinator...")
    query = "What is the average yield of my bond investments?"
    
    try:
        result = coordinator.process_query(
            session_id=session_id,
            query=query,
            document_ids=["demo-financial-statement-001", "demo-investment-portfolio-002"]
        )
        
        logger.info(f"Query: \"{query}\"")
        logger.info(f"Answer: \"{result.get('answer', 'No answer generated')}\"")
        doc_refs = result.get('document_references', [])
        logger.info(f"Document references: {len(doc_refs)}")
    except Exception as e:
        logger.error(f"Error processing query through coordinator: {str(e)}")
    
    # Get active sessions
    logger.info("\nGetting active sessions...")
    try:
        sessions = coordinator.get_active_sessions()
        logger.info(f"Found {len(sessions)} active sessions")
    except Exception as e:
        logger.error(f"Error getting active sessions: {str(e)}")
    
    # 6. Clean up
    logger.info("\n=== 6. CLEANING UP ===")
    
    try:
        # Clear the session
        coordinator.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")
        
        # Remove from chatbot service mapping
        chatbot_service.remove_session(session_id)
        logger.info(f"Removed session from chatbot service mapping")
    except Exception as e:
        logger.error(f"Error cleaning up: {str(e)}")
    
    logger.info("\n=== AGENT CAPABILITIES DEMONSTRATION COMPLETE ===")
    return True

if __name__ == "__main__":
    demonstrate_agent_capabilities()
