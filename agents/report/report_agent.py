import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from ..base.base_agent import BaseAgent
# Assuming QueryAgent might be used, or direct DB access
from database import query_instruments, get_document_summary, get_financial_instruments 

class ReportAgent(BaseAgent):
    """Agent specialized in generating financial reports."""

    def __init__(self, name: str = "report", memory_path: Optional[str] = None):
        """Initialize the report agent."""
        super().__init__(name, memory_path)
        # Could potentially hold report templates or formatting rules

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a report generation task.

        Args:
            task: Task dictionary containing report details.
                  Expected keys:
                  - type: "generate_summary_report", "generate_instrument_table", "generate_comparison_report"
                  - tenant_id: ID of the tenant.
                  - document_id: ID of the primary document.
                  - comparison_document_ids: List of document IDs for comparison reports.
                  - report_config: Dictionary with specific formatting or content options.

        Returns:
            Dictionary containing the generated report or error status.
        """
        task_type = task.get("type", "unknown")
        tenant_id = task.get("tenant_id")

        if not tenant_id:
            return {"status": "error", "message": "Missing tenant_id in report task."}

        if task_type == "generate_summary_report":
            document_id = task.get("document_id")
            if not document_id:
                 return {"status": "error", "message": "Missing document_id for summary report."}
            return self._generate_summary(tenant_id, document_id, task.get("report_config", {}))

        elif task_type == "generate_instrument_table":
            document_id = task.get("document_id")
            query_criteria = task.get("query_criteria", {}) # Allow filtering instruments for the table
            if not document_id:
                 # Could generate table across all docs for tenant if needed, but require explicit flag?
                 return {"status": "error", "message": "Missing document_id for instrument table report."}
            return self._generate_instrument_table(tenant_id, document_id, query_criteria, task.get("report_config", {}))
        
        elif task_type == "generate_comparison_report":
            document_id = task.get("document_id")
            comparison_doc_ids = task.get("comparison_document_ids", [])
            if not document_id or not comparison_doc_ids:
                 return {"status": "error", "message": "Missing document_id or comparison_document_ids for comparison report."}
            return self._generate_comparison(tenant_id, document_id, comparison_doc_ids, task.get("report_config", {}))

        # TODO: Add more report types (e.g., consolidated portfolio)

        else:
            return {
                "status": "error",
                "message": f"Unknown report task type: {task_type}"
            }

    def _generate_summary(self, tenant_id: str, document_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a summary report for a document."""
        self.logger.info(f"Generating summary report for doc {document_id}, tenant {tenant_id}")
        summary_data = get_document_summary(document_id=document_id, tenant_id=tenant_id)
        
        if not summary_data:
            return {"status": "error", "message": f"Could not retrieve summary data for document {document_id}."}
            
        # Basic formatting (can be expanded)
        report = {
            "report_type": "summary",
            "document_id": document_id,
            "tenant_id": tenant_id,
            "generated_at": datetime.now().isoformat(),
            "title": config.get("title", f"Summary for {document_id}"),
            "data": summary_data # Return the raw summary data for now
        }
        return {"status": "success", "report": report}

    def _generate_instrument_table(self, tenant_id: str, document_id: str, criteria: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a table of financial instruments."""
        self.logger.info(f"Generating instrument table for doc {document_id}, tenant {tenant_id}, criteria: {criteria}")
        
        # Add document_id to criteria if querying within a single document
        query_criteria = {"document_id": document_id, **criteria}
        instruments = query_instruments(tenant_id=tenant_id, query_criteria=query_criteria, limit=config.get("limit", 1000)) # High limit for tables
        
        if not instruments:
            # Don't treat empty results as error necessarily, could be valid filter
             self.logger.warning(f"No instruments found matching criteria for doc {document_id}, tenant {tenant_id}")
             # Fallback: maybe get all instruments for the doc if criteria yielded nothing? Optional.
             # instruments = get_financial_instruments(document_id=document_id, tenant_id=tenant_id)

        # Format as DataFrame then dict/list for output (e.g., JSON for UI, maybe CSV option later)
        if instruments:
            df = pd.DataFrame(instruments)
            # Clean up internal fields if desired
            if '_id' in df.columns: df = df.drop(columns=['_id'])
            if 'tenant_id' in df.columns: df = df.drop(columns=['tenant_id'])
            # Convert NaN to None for JSON compatibility
            df = df.where(pd.notnull(df), None)
            table_data = df.to_dict(orient='records')
        else:
            table_data = []

        report = {
            "report_type": "instrument_table",
            "document_id": document_id,
            "tenant_id": tenant_id,
            "generated_at": datetime.now().isoformat(),
            "title": config.get("title", f"Instrument Table for {document_id}"),
            "data": table_data,
            "columns": list(df.columns) if instruments else []
        }
        return {"status": "success", "report": report}

    def _generate_comparison(self, tenant_id: str, doc_id1: str, doc_ids2: List[str], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a comparison report between documents (placeholder)."""
        self.logger.info(f"Generating comparison report for docs {doc_id1} vs {doc_ids2}, tenant {tenant_id}")
        
        # 1. Fetch data for doc1
        instruments1 = get_financial_instruments(document_id=doc_id1, tenant_id=tenant_id)
        summary1 = get_document_summary(document_id=doc_id1, tenant_id=tenant_id)
        
        # 2. Fetch data for comparison docs
        comparison_data = {}
        for doc_id2 in doc_ids2:
            instruments2 = get_financial_instruments(document_id=doc_id2, tenant_id=tenant_id)
            summary2 = get_document_summary(document_id=doc_id2, tenant_id=tenant_id)
            comparison_data[doc_id2] = {"instruments": instruments2, "summary": summary2}
            
        # 3. Perform comparison logic (e.g., diff instruments by ISIN, compare summary metrics)
        # This logic can be complex and depends on the desired comparison type
        comparison_results = {
             "instruments_diff": "TODO: Implement instrument comparison",
             "summary_comparison": "TODO: Implement summary comparison"
        } # Placeholder

        report = {
            "report_type": "comparison",
            "base_document_id": doc_id1,
            "comparison_document_ids": doc_ids2,
            "tenant_id": tenant_id,
            "generated_at": datetime.now().isoformat(),
            "title": config.get("title", f"Comparison Report: {doc_id1} vs {', '.join(doc_ids2)}"),
            "data": comparison_results 
        }
        return {"status": "success", "report": report}