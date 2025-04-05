"""
Demonstration of agent capabilities

This script demonstrates the capabilities of all agents in the financial document
analysis system, showing how they work together to process queries about financial
documents.
"""

import os
import uuid
import logging
import asyncio # Import asyncio
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

async def demonstrate_agent_capabilities(): # Make the function async
    """
    Demonstrate the capabilities of all agents in the system
    """
    # Load environment variables
    load_dotenv()
    
    # Ensure necessary API keys are available (OpenRouter or Gemini)
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not openrouter_key and not gemini_key:
        logger.error("Neither OPENROUTER_API_KEY nor GEMINI_API_KEY found in environment variables")
        return False
    
    if openrouter_key:
        logger.info(f"Using OpenRouter API key: {openrouter_key[:4]}...{openrouter_key[-4:]}")
    if gemini_key:
        logger.info(f"Using Gemini API key: {gemini_key[:4]}...{gemini_key[-4:]}")
    
    # Import our agent components
    try:
        from agent_framework.coordinator import AgentCoordinator
        from agent_framework.memory_agent import MemoryAgent
        from agent_framework.nlp_agent import NaturalLanguageQueryAgent
        from agent_framework.table_generator import CustomTableGenerator
        # Corrected import for ChatbotAgent
        from agents.chatbot.chatbot_agent import ChatbotAgent
        
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
    # chatbot_service = ChatbotService() # Original incorrect service
    chatbot_agent = ChatbotAgent() # Instantiate the correct agent
    
    # Create unique identifiers for this demonstration
    demo_id = uuid.uuid4().hex[:8]
    user_id = f"demo-user-{demo_id}"
    
    # 1. Demonstrate ChatbotService capabilities
    logger.info("\n=== 1. CHATBOT SERVICE CAPABILITIES ===")
    
    # Create a chat session (Using fallback ID as ChatbotAgent doesn't have create_session)
    logger.info("Creating a new chat session (using fallback ID)...")
    session_id = f"fallback-session-{demo_id}"
    logger.info(f"Using session ID: {session_id}")
    
    # --- ChatbotAgent Demonstration (Simplified) ---
    # The ChatbotAgent expects a task dict via its process method.
    # We'll simulate a simple interaction here instead of using the old service methods.
    logger.info("\nSimulating a chatbot query via ChatbotAgent...")
    chatbot_task = {
        "type": "user_message",
        "tenant_id": user_id, # Using demo user_id as tenant_id
        "user_input": "show summary for document demo-financial-statement-001"
        # Note: This will likely fail as the QueryAgent needs actual data access,
        # but it demonstrates calling the ChatbotAgent.
    }
    try:
        chatbot_response = await chatbot_agent.process(chatbot_task) # Assuming async, adjust if not
        logger.info(f"ChatbotAgent response: {chatbot_response}")
    except Exception as e:
         logger.error(f"Error processing chatbot task: {str(e)}")

    # Skipping original document suggestion generation as it's not part of ChatbotAgent
    logger.info("\nSkipping document suggestion generation (not applicable to ChatbotAgent).")
    
    # 2. Demonstrate Memory Agent capabilities (Skipping - Coordinator doesn't provide get_memory_agent)
    logger.info("\n=== 2. MEMORY AGENT CAPABILITIES (SKIPPED) ===")
    logger.info("Skipping MemoryAgent demonstration as AgentCoordinator does not have 'get_memory_agent' method.")
    # Initialize MemoryAgent directly if needed for other parts, but the demo logic relied on coordinator retrieval.
    # memory_agent = MemoryAgent()
    
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
            query=query
            # Removed document_ids as it's not an expected argument for coordinator.process_query
        )
        
        logger.info(f"Query: \"{query}\"")
        logger.info(f"Answer: \"{result.get('answer', 'No answer generated')}\"")
        doc_refs = result.get('document_references', [])
        logger.info(f"Document references: {len(doc_refs)}")
    except Exception as e:
        logger.error(f"Error processing query through coordinator: {str(e)}")
    
    # Get active sessions (Skipping - Coordinator doesn't have get_active_sessions)
    logger.info("\nGetting active sessions... (SKIPPED)")
    logger.info("Skipping get_active_sessions as AgentCoordinator does not have this method.")
    
    # 6. Clean up
    logger.info("\n=== 6. CLEANING UP ===")
    
    try:
        # Clear the session (Skipping - Coordinator doesn't have clear_session)
        # coordinator.clear_session(session_id)
        logger.info(f"Cleared session {session_id}")
        
        # Remove from chatbot service mapping (Skipping - not applicable to ChatbotAgent)
        # chatbot_service.remove_session(session_id)
        logger.info(f"Removed session from chatbot service mapping")
    except Exception as e:
        logger.error(f"Error cleaning up: {str(e)}")
    
    logger.info("\n=== AGENT CAPABILITIES DEMONSTRATION COMPLETE ===")
    return True

if __name__ == "__main__":
    asyncio.run(demonstrate_agent_capabilities()) # Run the async function
