import asyncio
import logging
import os
from dotenv import load_dotenv
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_agent_flow")

# Load environment variables (.env file should contain MONGODB_URI and GEMINI_API_KEY)
load_dotenv()
logger.info("Loaded environment variables.")

# Import Agents (ensure paths are correct relative to project root)
try:
    from agents.financial.financial_agent import FinancialAgent
    from agents.query.query_agent import QueryAgent
    from agents.report.report_agent import ReportAgent
    from agents.chatbot.chatbot_agent import ChatbotAgent
    from database import connect_db, close_db_connection, get_db # To check connection and potentially clear data
    logger.info("Successfully imported agents and database functions.")
except ImportError as e:
    logger.error(f"Failed to import agents or database functions. Check PYTHONPATH and file structure: {e}")
    exit(1)
except Exception as e:
     logger.error(f"An unexpected error occurred during import: {e}")
     exit(1)

# --- Test Configuration ---
TEST_PDF_PATH = "uploads/2._Messos_28.02.2025.pdf" 
# Use a unique ID for testing to avoid conflicts if run multiple times
TEST_DOCUMENT_ID = f"test_doc_{uuid.uuid4()}" 
TEST_TENANT_ID = "test_tenant_001" 
# --- ---

async def run_test_flow():
    """Runs the simulated agent workflow."""
    logger.info("--- Starting Agent Test Flow ---")

    # Check prerequisites
    if not os.path.exists(TEST_PDF_PATH):
        logger.error(f"Test PDF not found at: {TEST_PDF_PATH}")
        return
    if not os.getenv("MONGODB_URI"):
        logger.error("MONGODB_URI not found in .env file.")
        return
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY not found in .env file.")
        # Financial agent might still run without Gemini, but instrument extraction will fail.
        # Allow continuing but log warning.
        logger.warning("GEMINI_API_KEY missing, instrument extraction will likely fail.")

    # Connect to DB (and potentially clear previous test data for this doc/tenant)
    try:
        connect_db()
        # Optional: Clear previous test data for idempotency
        # db = get_db()
        # db.financial_instruments.delete_many({"document_id": TEST_DOCUMENT_ID, "tenant_id": TEST_TENANT_ID})
        # db.document_summaries.delete_many({"document_id": TEST_DOCUMENT_ID, "tenant_id": TEST_TENANT_ID})
        # logger.info(f"Cleared previous test data for doc {TEST_DOCUMENT_ID}, tenant {TEST_TENANT_ID}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB or clear data: {e}")
        return

    # Instantiate Agents
    logger.info("Instantiating agents...")
    try:
        financial_agent = FinancialAgent()
        query_agent = QueryAgent()
        report_agent = ReportAgent()
        chatbot_agent = ChatbotAgent() # Note: Chatbot currently instantiates its own Query/Report agents
        logger.info("Agents instantiated.")
    except Exception as e:
        logger.error(f"Failed to instantiate agents: {e}")
        close_db_connection()
        return

    # --- Step 1: Financial Agent Processing ---
    logger.info(f"\n--- Testing Financial Agent: Analyzing Document {TEST_DOCUMENT_ID} ---")
    financial_task = {
        "type": "analyze_document",
        "pdf_path": TEST_PDF_PATH,
        "doc_id": TEST_DOCUMENT_ID,
        "tenant_id": TEST_TENANT_ID,
        "force_refresh": True # Ensure it runs even if cached locally (though cache is commented out now)
    }
    financial_result = await financial_agent.process(financial_task)
    logger.info(f"Financial Agent Result:\n{financial_result}\n")

    # Check if financial processing succeeded before proceeding
    if financial_result.get("status") != "success":
        logger.error("Financial agent processing failed. Aborting further tests.")
        close_db_connection()
        return
        
    # Allow some time for DB operations if needed (usually not necessary for MongoDB)
    # await asyncio.sleep(1) 

    # --- Step 2: Query Agent - Get Summary ---
    logger.info(f"\n--- Testing Query Agent: Get Summary for {TEST_DOCUMENT_ID} ---")
    query_summary_task = {
        "type": "get_summary",
        "tenant_id": TEST_TENANT_ID,
        "document_id": TEST_DOCUMENT_ID
    }
    summary_result = await query_agent.process(query_summary_task)
    logger.info(f"Query Agent (Get Summary) Result:\n{summary_result}\n")

    # --- Step 3: Query Agent - Query Instruments ---
    logger.info(f"\n--- Testing Query Agent: Querying Bonds for {TEST_DOCUMENT_ID} ---")
    query_instruments_task = {
        "type": "query_instruments",
        "tenant_id": TEST_TENANT_ID,
        "query_criteria": {
            "document_id": TEST_DOCUMENT_ID, # Filter by doc ID
            "type": "bond" # Filter by type 'bond'
        },
        "limit": 5
    }
    instruments_result = await query_agent.process(query_instruments_task)
    logger.info(f"Query Agent (Query Instruments) Result:\n{instruments_result}\n")

    # --- Step 4: Report Agent - Generate Instrument Table ---
    logger.info(f"\n--- Testing Report Agent: Generate Instrument Table for {TEST_DOCUMENT_ID} ---")
    report_task = {
        "type": "generate_instrument_table",
        "tenant_id": TEST_TENANT_ID,
        "document_id": TEST_DOCUMENT_ID,
        "query_criteria": {"type": "structured product"}, # Example: Table of structured products
        "report_config": {"title": "Structured Products Table (Test)"}
    }
    report_result = await report_agent.process(report_task)
    logger.info(f"Report Agent Result:\n{report_result}\n")

    # --- Step 5: Chatbot Agent - Simulate User Query ---
    logger.info(f"\n--- Testing Chatbot Agent: Simulating User Query ---")
    # Simulate asking for the summary via chat
    chatbot_task = {
        "type": "user_message",
        "tenant_id": TEST_TENANT_ID,
        "user_input": f"show summary for document {TEST_DOCUMENT_ID}" 
    }
    chatbot_result = await chatbot_agent.process(chatbot_task)
    logger.info(f"Chatbot Agent Result:\n{chatbot_result}\n")
    
    # Simulate asking to list instruments
    logger.info(f"\n--- Testing Chatbot Agent: Simulating List Instruments Query ---")
    chatbot_task_2 = {
        "type": "user_message",
        "tenant_id": TEST_TENANT_ID,
        "user_input": f"list instruments for document {TEST_DOCUMENT_ID} type stock" 
    }
    chatbot_result_2 = await chatbot_agent.process(chatbot_task_2)
    logger.info(f"Chatbot Agent Result 2:\n{chatbot_result_2}\n")


    # --- Cleanup ---
    logger.info("--- Test Flow Complete. Closing DB connection. ---")
    close_db_connection()

if __name__ == "__main__":
    # Ensure asyncio event loop runs
    try:
        asyncio.run(run_test_flow())
    except Exception as e:
         logger.error(f"Test flow failed with unhandled exception: {e}", exc_info=True)
         # Ensure DB connection is closed even on error
         close_db_connection()