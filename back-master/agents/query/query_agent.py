import logging
from typing import Dict, List, Any, Optional
from ..base.base_agent import BaseAgent
from database import query_instruments, get_document_summary # Import necessary DB functions

class QueryAgent(BaseAgent):
    """Agent specialized in querying stored financial data."""

    def __init__(self, name: str = "query", memory_path: Optional[str] = None):
        """Initialize the query agent."""
        super().__init__(name, memory_path)
        # Potential future enhancement: Initialize an LLM client for NL-to-query translation
        # self.llm_client = ... 

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query task.

        Args:
            task: Task dictionary containing query details.
                  Expected keys:
                  - type: "query_instruments", "get_summary", etc.
                  - tenant_id: ID of the tenant whose data to query.
                  - query_criteria: Dictionary for instrument filtering (for type="query_instruments").
                  - document_id: Specific document ID (for type="get_summary" or specific instrument queries).
                  - natural_language_query: (Future) User's query in text.

        Returns:
            Dictionary containing query results or error status.
        """
        task_type = task.get("type", "unknown")
        tenant_id = task.get("tenant_id")

        if not tenant_id:
            return {"status": "error", "message": "Missing tenant_id in query task."}

        if task_type == "query_instruments":
            criteria = task.get("query_criteria", {})
            limit = task.get("limit", 100)
            # Basic security: ensure tenant_id is always used, even if criteria is empty
            if not isinstance(criteria, dict):
                 return {"status": "error", "message": "query_criteria must be a dictionary."}
            
            self.logger.info(f"Querying instruments for tenant {tenant_id} with criteria: {criteria}")
            results = query_instruments(tenant_id=tenant_id, query_criteria=criteria, limit=limit)
            return {"status": "success", "results": results}

        elif task_type == "get_summary":
            document_id = task.get("document_id")
            if not document_id:
                 return {"status": "error", "message": "Missing document_id for get_summary task."}
            
            self.logger.info(f"Getting summary for document {document_id}, tenant {tenant_id}")
            summary = get_document_summary(document_id=document_id, tenant_id=tenant_id)
            if summary:
                return {"status": "success", "results": summary}
            else:
                # Could be not found or DB error, get_document_summary logs details
                return {"status": "error", "message": f"Summary not found or error retrieving summary for document {document_id}."}
        
        # TODO: Add handling for natural_language_query using an LLM to translate to criteria
        # elif task_type == "natural_language_query":
        #     nl_query = task.get("natural_language_query")
        #     if not nl_query:
        #         return {"status": "error", "message": "Missing natural_language_query."}
        #     # 1. Translate nl_query to MongoDB criteria using LLM
        #     # criteria = self.translate_nl_to_mongo(nl_query) 
        #     # 2. Call query_instruments
        #     # results = query_instruments(tenant_id=tenant_id, query_criteria=criteria)
        #     # return {"status": "success", "results": results}
            
        else:
            return {
                "status": "error",
                "message": f"Unknown query task type: {task_type}"
            }

    # Placeholder for future NL-to-Query translation
    # def translate_nl_to_mongo(self, nl_query: str) -> Dict[str, Any]:
    #     # Use LLM to convert natural language like "show me all bonds worth more than 1 million"
    #     # into MongoDB query syntax like {"type": "bond", "value": {"$gt": 1000000}}
    #     self.logger.info(f"Translating NL query: {nl_query}")
    #     # ... LLM call and parsing logic ...
    #     return {} # Return translated criteria