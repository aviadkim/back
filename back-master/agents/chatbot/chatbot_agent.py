import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..base.base_agent import BaseAgent
# Import other agents to delegate tasks
from ..query.query_agent import QueryAgent
from ..report.report_agent import ReportAgent

class ChatbotAgent(BaseAgent):
    """Agent specialized in handling user chat interactions."""

    def __init__(self, name: str = "chatbot", memory_path: Optional[str] = None):
        """Initialize the chatbot agent."""
        super().__init__(name, memory_path)
        # Instantiate other agents it needs to interact with
        # TODO: Consider how agent instances are managed/passed (dependency injection?)
        self.query_agent = QueryAgent() 
        self.report_agent = ReportAgent()
        # Potential future enhancement: Initialize an LLM for intent recognition/NLU
        # self.nlu_llm = ... 

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a user message/request.

        Args:
            task: Task dictionary containing user input.
                  Expected keys:
                  - type: "user_message"
                  - tenant_id: ID of the user/tenant interacting.
                  - user_input: The raw text message from the user.
                  - conversation_history: (Optional) Previous turns for context.

        Returns:
            Dictionary containing the chatbot's response or an error.
        """
        task_type = task.get("type", "unknown")
        tenant_id = task.get("tenant_id")
        user_input = task.get("user_input")

        if task_type != "user_message":
             return {"status": "error", "message": f"Chatbot only handles 'user_message' type, got {task_type}"}
        if not tenant_id:
            return {"status": "error", "message": "Missing tenant_id in chatbot task."}
        if not user_input:
            return {"status": "error", "message": "Missing user_input in chatbot task."}

        self.logger.info(f"Processing user input for tenant {tenant_id}: '{user_input}'")

        # --- Intent Recognition (Simplified) ---
        # TODO: Replace this with a more robust NLU/intent recognition mechanism (e.g., using an LLM)
        
        response = {"status": "success", "response_text": "I'm sorry, I didn't understand that."} # Default response

        try:
            if "show summary for document" in user_input.lower():
                # Example: "show summary for document doc123"
                parts = user_input.split()
                doc_id_index = parts.index("document") + 1
                if doc_id_index < len(parts):
                    document_id = parts[doc_id_index]
                    query_task = {
                        "type": "get_summary",
                        "tenant_id": tenant_id,
                        "document_id": document_id
                    }
                    summary_result = await self.query_agent.process(query_task)
                    if summary_result.get("status") == "success":
                        # Format the summary for the user
                        summary_data = summary_result.get("results", {})
                        # Remove internal fields before showing user
                        if '_id' in summary_data: del summary_data['_id'] 
                        if 'tenant_id' in summary_data: del summary_data['tenant_id']
                        response["response_text"] = f"Summary for {document_id}:\n```json\n{json.dumps(summary_data, indent=2, default=str)}\n```" # Added default=str
                    else:
                        response["response_text"] = f"Could not retrieve summary for {document_id}. Reason: {summary_result.get('message')}"
                else:
                     response["response_text"] = "Please specify the document ID after 'document'."

            elif "list instruments" in user_input.lower():
                 # Example: "list instruments for document doc123 type bond"
                 parts = user_input.lower().split()
                 doc_id = None
                 criteria = {}
                 if "document" in parts:
                     doc_id_index = parts.index("document") + 1
                     if doc_id_index < len(parts):
                         doc_id = parts[doc_id_index] # Assuming original case ID is needed later
                         criteria["document_id"] = doc_id 
                 # Simple criteria parsing (needs improvement)
                 if "type" in parts:
                     type_index = parts.index("type") + 1
                     if type_index < len(parts):
                         criteria["type"] = parts[type_index]
                 
                 query_task = {
                     "type": "query_instruments",
                     "tenant_id": tenant_id,
                     "query_criteria": criteria,
                     "limit": 20 # Limit results for chat
                 }
                 query_result = await self.query_agent.process(query_task)
                 if query_result.get("status") == "success":
                     instruments = query_result.get("results", [])
                     if instruments:
                         # Format instruments list
                         formatted_list = []
                         for inst in instruments:
                              # Remove internal fields
                              if '_id' in inst: del inst['_id']
                              if 'tenant_id' in inst: del inst['tenant_id']
                              formatted_list.append(f"- {inst.get('name', 'N/A')} ({inst.get('isin', 'N/A')}), Type: {inst.get('type', 'N/A')}, Value: {inst.get('value', 'N/A')} {inst.get('currency', '')}")
                         response["response_text"] = f"Found {len(instruments)} instruments:\n" + "\n".join(formatted_list)
                         if len(instruments) >= query_task["limit"]:
                              response["response_text"] += "\n(Result limited, refine your query for more specific results)"
                     else:
                         response["response_text"] = "No instruments found matching your criteria."
                 else:
                     response["response_text"] = f"Could not query instruments. Reason: {query_result.get('message')}"

            elif "generate report" in user_input.lower():
                 # Example: "generate report instrument table for document doc123"
                 parts = user_input.lower().split()
                 doc_id = None
                 report_type = "instrument_table" # Default or parse
                 # Basic parsing - needs improvement
                 if "document" in parts:
                     doc_id_index = parts.index("document") + 1
                     if doc_id_index < len(parts):
                         doc_id = parts[doc_id_index]
                 
                 if doc_id:
                     report_task = {
                         "type": f"generate_{report_type}", # e.g., generate_instrument_table
                         "tenant_id": tenant_id,
                         "document_id": doc_id,
                         "report_config": {"title": f"Requested Table for {doc_id}"} # Example config
                     }
                     report_result = await self.report_agent.process(report_task)
                     if report_result.get("status") == "success":
                          # Provide link or summary of the report
                          report_data = report_result.get("report", {})
                          response["response_text"] = f"Generated report '{report_data.get('title', 'Report')}' ({report_type}).\nData:\n```json\n{json.dumps(report_data.get('data', 'No data'), indent=2)}\n```" # Simple display for now
                     else:
                          response["response_text"] = f"Could not generate report. Reason: {report_result.get('message')}"
                 else:
                      response["response_text"] = "Please specify the document ID for the report."

            # Add more intent handling rules here...

        except Exception as e:
            self.logger.error(f"Error processing user input '{user_input}': {e}", exc_info=True)
            response = {"status": "error", "response_text": "An internal error occurred while processing your request."}

        # Store conversation turn? (Optional)
        # self.store_result(f"conversation_{tenant_id}_{datetime.now().isoformat()}", 
        #                   {"user": user_input, "bot": response.get("response_text")})

        return response

# Helper function for JSON serialization if needed (e.g., for complex objects in responses)
import json
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Add other type handlers if necessary
        return json.JSONEncoder.default(self, obj)