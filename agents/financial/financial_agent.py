import logging
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import json
import os
from datetime import datetime

from ..base.base_agent import BaseAgent
# Import the specific Gemini processor we validated
from gemini_financial_processor import GeminiFinancialProcessor, FinancialInstrument
# Keep other processors if needed for different analyses
from pdf_processor.extraction.text_extractor import PDFTextExtractor
from pdf_processor.tables.table_extractor import TableExtractor
from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer
# Import database functions
from database import add_financial_instruments, add_document_summary, get_db

class FinancialAgent(BaseAgent):
    """Agent specialized in financial document analysis."""
    
    def __init__(self, name: str = "financial", memory_path: Optional[str] = None):
        """Initialize the financial agent.
        
        Args:
            name: Name of the agent
            memory_path: Optional path to persist agent memory
        """
        super().__init__(name, memory_path)
        # Instantiate the Gemini processor (ensure API key is available via Config/dotenv)
        try:
            self.gemini_processor = GeminiFinancialProcessor()
        except ValueError as e:
            self.logger.error(f"Failed to initialize GeminiFinancialProcessor: {e}. Agent may not function correctly for instrument extraction.")
            self.gemini_processor = None # Handle initialization failure gracefully
        
        # Keep other tools if they serve different purposes (e.g., basic text/table extraction for other analyses)
        self.text_extractor = PDFTextExtractor()
        self.table_extractor = TableExtractor()
        self.financial_analyzer = FinancialAnalyzer() # May be used for non-instrument analysis
        
        # Initialize memory structures if they don't exist
        if "documents" not in self.memory:
            self.memory["documents"] = {}
        if "templates" not in self.memory:
            self.memory["templates"] = {}
        if "reports" not in self.memory:
            self.memory["reports"] = {}
    
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a financial task.
        
        Args:
            task: Task dictionary with instructions
            
        Returns:
            Dictionary containing results
        """
        task_type = task.get("type", "unknown")
        
        if task_type == "analyze_document":
            return await self._analyze_document(task)
        elif task_type == "generate_report":
            return await self._generate_report(task)
        elif task_type == "extract_tables":
            return await self._extract_tables(task)
        elif task_type == "analyze_tables":
            return await self._analyze_tables(task)
        elif task_type == "save_template":
            return await self._save_template(task)
        elif task_type == "apply_template":
            return await self._apply_template(task)
        elif task_type == "query_data":
            return await self._query_data(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    async def _analyze_document(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a financial document.
        
        Args:
            task: Task with document path
            
        Returns:
            Analysis results
        """
        pdf_path = task.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            return {
                "status": "error",
                "message": f"Invalid PDF path: {pdf_path}"
            }
        
        doc_id = task.get("doc_id", os.path.basename(pdf_path))
        tenant_id = task.get("tenant_id") # Expect tenant_id in the task
        force_refresh = task.get("force_refresh", False)
        
        if not tenant_id:
             return {
                 "status": "error",
                 "message": "Missing tenant_id in task for document analysis."
             }
        
        # Check if we've already analyzed this document (using agent's local memory - might remove later if DB is sole source)
        # if doc_id in self.memory.get("documents", {}) and not force_refresh:
        #     return {
        #         "status": "success",
        #         "message": "Using cached analysis",
        #         "doc_id": doc_id,
        #         "results": self.memory["documents"][doc_id]
        #     }
        # NOTE: Relying on DB might be better than agent memory for consistency. Keeping cache check commented for now.
        
        try:
            # --- Primary Instrument Extraction using Gemini ---
            instruments_to_save = []
            if self.gemini_processor:
                self.logger.info(f"Processing document for instrument extraction using Gemini: {pdf_path}")
                # process_document returns a list of FinancialInstrument Pydantic objects
                extracted_instruments = self.gemini_processor.process_document(pdf_path)
                if extracted_instruments:
                     # Convert Pydantic models to dictionaries for saving
                    instruments_to_save = [inst.model_dump() for inst in extracted_instruments]
                    self.logger.info(f"Gemini extracted {len(instruments_to_save)} instruments.")
                else:
                     self.logger.warning(f"Gemini processor returned no instruments for {pdf_path}.")
            else:
                self.logger.error("Gemini processor not initialized. Skipping instrument extraction.")
                # Potentially return an error status here if instrument extraction is critical
                # return {"status": "error", "message": "Gemini processor failed to initialize."}
        
            # --- Optional: Perform other analyses (e.g., using FinancialAnalyzer) ---
            # You might still want other analyses beyond just instrument listing.
            # Example: Get overall text summary or analyze specific tables differently.
            
            self.logger.info(f"Performing additional analysis (text/tables) on {pdf_path}")
            text_data = self.text_extractor.extract_document(pdf_path) # Still useful for context/other analysis
            tables_data = self.table_extractor.extract_tables(pdf_path) # Still useful
            
            # Use FinancialAnalyzer for other metrics if needed
            other_financial_metrics = {}
            # Example: Analyze text for sentiment, keywords, etc. (if analyzer supports it)
            # Example: Analyze tables for structure, specific non-instrument data
            # Populate other_financial_metrics based on FinancialAnalyzer results...
            # Placeholder:
            other_financial_metrics = {
                "text_page_count": len(text_data),
                "table_count": sum(len(t) for t in tables_data.values()),
                # Add actual metrics from financial_analyzer here if applicable
            }
            
            # Prepare summary data for database storage
            summary_to_save = {
                "instruments_extracted_count": len(instruments_to_save),
                "analysis_timestamp": datetime.now().isoformat(),
                **other_financial_metrics # Merge other metrics collected
            }
            
            # Store results in Database
            db_success = True
            if instruments_to_save:
                self.logger.info(f"Attempting to save {len(instruments_to_save)} instruments to DB for doc {doc_id}, tenant {tenant_id}")
                if not add_financial_instruments(document_id=doc_id, tenant_id=tenant_id, instruments_data=instruments_to_save):
                    self.logger.error(f"Failed to save financial instruments to DB for doc {doc_id}")
                    db_success = False # Mark as failed but continue to save summary if possible
            
            if summary_to_save:
                self.logger.info(f"Attempting to save document summary to DB for doc {doc_id}, tenant {tenant_id}")
                if not add_document_summary(document_id=doc_id, tenant_id=tenant_id, summary_data=summary_to_save):
                     self.logger.error(f"Failed to save document summary to DB for doc {doc_id}")
                     db_success = False # Mark as failed
            
            # Optionally, store raw/intermediate data in agent memory or separate DB collection if needed
            # self.memory["documents"][doc_id] = { ... } # If local caching is still desired
            # if self.memory_path:
            #     self._save_memory()
            
            if not db_success:
                # Decide on error handling - return error or just log?
                # Returning error for now if DB saving failed.
                return {
                    "status": "error",
                    "message": f"Document analyzed but failed to save results to database for doc_id: {doc_id}"
                }
            
            # Success case: Analysis and DB save completed
            return {
                "status": "success",
                "message": "Document analyzed and results saved successfully",
                "doc_id": doc_id,
                "results_summary": { # Provide a summary of what was done
                    "instruments_saved": len(instruments_to_save),
                    "summary_saved": bool(summary_to_save),
                    "other_metrics_keys": list(other_financial_metrics.keys())
                }
                }
            
            return {
                "status": "success",
                "message": "Document analyzed successfully",
                "doc_id": doc_id,
                "results": {
                    "text_pages": len(text_data),
                    "tables_found": sum(len(tables) for tables in tables_data.values()),
                    "financial_metrics": financial_data.get("text_analysis", {}),
                    "table_analyses": [
                        {
                            "page": ta["page"],
                            "table_id": ta["table_id"],
                            "table_type": ta["analysis"].get("table_type", "unknown")
                        }
                        for ta in table_analyses
                    ] if "table_analyses" in financial_data else []
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            return {
                "status": "error",
                "message": f"Error analyzing document: {str(e)}"
            }
    
    async def _extract_tables(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tables from a document.
        
        Args:
            task: Task with document path
            
        Returns:
            Extracted tables
        """
        pdf_path = task.get("pdf_path")
        if not pdf_path or not os.path.exists(pdf_path):
            return {
                "status": "error",
                "message": f"Invalid PDF path: {pdf_path}"
            }
        
        page_numbers = task.get("page_numbers")
        
        try:
            tables_data = self.table_extractor.extract_tables(pdf_path, page_numbers)
            
            # Convert tables to DataFrames
            tables_df = {}
            for page_num, page_tables in tables_data.items():
                tables_df[page_num] = []
                for table_idx, table in enumerate(page_tables):
                    df = self.table_extractor.convert_to_dataframe(table)
                    tables_df[page_num].append({
                        "id": table_idx,
                        "dataframe": df.to_dict(),  # Convert to dict for JSON serialization
                        "metadata": {
                            "bbox": table.get("bbox"),
                            "row_count": table.get("row_count"),
                            "col_count": table.get("col_count"),
                            "extraction_method": table.get("extraction_method")
                        }
                    })
            
            return {
                "status": "success",
                "message": "Tables extracted successfully",
                "tables": tables_df
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting tables: {str(e)}")
            return {
                "status": "error",
                "message": f"Error extracting tables: {str(e)}"
            }
    
    async def _analyze_tables(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze tables from a document.
        
        Args:
            task: Task with tables data
            
        Returns:
            Analysis of tables
        """
        tables = task.get("tables")
        if not tables:
            return {
                "status": "error",
                "message": "No tables provided for analysis"
            }
        
        try:
            analyses = []
            
            for table in tables:
                # Convert dict back to DataFrame
                df_dict = table.get("dataframe")
                if df_dict:
                    df = pd.DataFrame.from_dict(df_dict)
                    analysis = self.financial_analyzer.analyze_financial_table(df)
                    
                    analyses.append({
                        "table_id": table.get("id"),
                        "analysis": analysis
                    })
            
            return {
                "status": "success",
                "message": "Tables analyzed successfully",
                "analyses": analyses
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing tables: {str(e)}")
            return {
                "status": "error",
                "message": f"Error analyzing tables: {str(e)}"
            }
    
    async def _save_template(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Save a template for future use.
        
        Args:
            task: Task with template definition
            
        Returns:
            Template saving result
        """
        template_name = task.get("template_name")
        template_def = task.get("template_def")
        
        if not template_name or not template_def:
            return {
                "status": "error",
                "message": "Missing template name or definition"
            }
        
        try:
            self.memory["templates"][template_name] = {
                "created": datetime.now().isoformat(),
                "updated": datetime.now().isoformat(),
                "definition": template_def
            }
            
            if self.memory_path:
                self._save_memory()
            
            return {
                "status": "success",
                "message": f"Template '{template_name}' saved successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error saving template: {str(e)}")
            return {
                "status": "error",
                "message": f"Error saving template: {str(e)}"
            }
    
    async def _apply_template(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a saved template to document data.
        
        Args:
            task: Task with template name and document ID
            
        Returns:
            Result of template application
        """
        template_name = task.get("template_name")
        doc_id = task.get("doc_id")
        
        if not template_name or not doc_id:
            return {
                "status": "error",
                "message": "Missing template name or document ID"
            }
        
        # Check if template exists
        if template_name not in self.memory["templates"]:
            return {
                "status": "error",
                "message": f"Template '{template_name}' not found"
            }
        
        # Check if document exists
        if doc_id not in self.memory["documents"]:
            return {
                "status": "error",
                "message": f"Document '{doc_id}' not found"
            }
        
        try:
            template = self.memory["templates"][template_name]["definition"]
            document = self.memory["documents"][doc_id]
            
            # Apply template logic here - this would depend on your template format
            # For now, this is a simplified implementation
            result = self._process_template(template, document)
            
            return {
                "status": "success",
                "message": f"Template '{template_name}' applied successfully",
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error applying template: {str(e)}")
            return {
                "status": "error",
                "message": f"Error applying template: {str(e)}"
            }
    
    def _process_template(self, template: Dict[str, Any], document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a template with document data.
        
        Args:
            template: Template definition
            document: Document data
            
        Returns:
            Processed result
        """
        # This is a placeholder for template processing logic
        # The actual implementation would depend on your template format
        result = {
            "template_processed": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # Example of extracting specified metrics
        if "metrics" in template:
            result["metrics"] = {}
            financial_data = document.get("financial_data", {})
            
            for metric in template["metrics"]:
                # Check text analysis
                text_analysis = financial_data.get("text_analysis", {})
                for page_num, page_metrics in text_analysis.items():
                    if metric in page_metrics:
                        result["metrics"][metric] = page_metrics[metric]
                        break
                
                # Check table analyses
                if metric not in result["metrics"]:
                    table_analyses = financial_data.get("table_analyses", [])
                    for table_analysis in table_analyses:
                        analysis = table_analysis.get("analysis", {})
                        if metric in analysis:
                            result["metrics"][metric] = analysis[metric]
                            break
        
        return result
    
    async def _generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a financial report.
        
        Args:
            task: Task with report configuration
            
        Returns:
            Generated report
        """
        doc_id = task.get("doc_id")
        report_type = task.get("report_type", "summary")
        report_config = task.get("config", {})
        
        if not doc_id:
            return {
                "status": "error",
                "message": "Missing document ID"
            }
        
        # Check if document exists
        if doc_id not in self.memory["documents"]:
            return {
                "status": "error",
                "message": f"Document '{doc_id}' not found"
            }
        
        try:
            document = self.memory["documents"][doc_id]
            
            # Generate report based on type
            if report_type == "summary":
                report = self._generate_summary_report(document, report_config)
            elif report_type == "detailed":
                report = self._generate_detailed_report(document, report_config)
            elif report_type == "comparative":
                # Need multiple documents for comparison
                comparison_doc_ids = task.get("comparison_doc_ids", [])
                comparison_docs = {}
                
                for comp_id in comparison_doc_ids:
                    if comp_id in self.memory["documents"]:
                        comparison_docs[comp_id] = self.memory["documents"][comp_id]
                
                report = self._generate_comparative_report(document, comparison_docs, report_config)
            else:
                return {
                    "status": "error",
                    "message": f"Unknown report type: {report_type}"
                }
            
            # Store report
            report_id = f"{doc_id}_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.memory["reports"][report_id] = report
            
            if self.memory_path:
                self._save_memory()
            
            return {
                "status": "success",
                "message": f"Report generated successfully",
                "report_id": report_id,
                "report": report
            }
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating report: {str(e)}"
            }
    
    def _generate_summary_report(self, document: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary financial report.
        
        Args:
            document: Document data
            config: Report configuration
            
        Returns:
            Summary report
        """
        # Extract key financial information
        financial_data = document.get("financial_data", {})
        text_analysis = financial_data.get("text_analysis", {})
        table_analyses = financial_data.get("table_analyses", [])
        
        # Prepare report
        report = {
            "title": config.get("title", "Financial Summary Report"),
            "document": document.get("file_path", "Unknown"),
            "generated_at": datetime.now().isoformat(),
            "summary": {}
        }
        
        # Extract key metrics
        key_metrics = {}
        
        # Look for financial periods
        periods = set()
        for page_metrics in text_analysis.values():
            if "fiscal_periods" in page_metrics:
                periods.update(page_metrics["fiscal_periods"])
        if periods:
            key_metrics["periods"] = list(periods)
        
        # Look for currency values and dates
        for page_metrics in text_analysis.values():
            if "currency_values" in page_metrics and "currency_values" not in key_metrics:
                key_metrics["currency_values"] = page_metrics["currency_values"]
            if "dates" in page_metrics and "dates" not in key_metrics:
                key_metrics["dates"] = page_metrics["dates"]
        
        # Extract key financial metrics from tables
        income_statement_data = {}
        balance_sheet_data = {}
        cash_flow_data = {}
        
        for table_analysis in table_analyses:
            analysis = table_analysis.get("analysis", {})
            table_type = analysis.get("table_type", "unknown")
            
            if table_type == "income_statement":
                # Look for key income statement metrics
                if "income_analysis" in analysis:
                    income_analysis = analysis["income_analysis"]
                    for key, value in income_analysis.items():
                        income_statement_data[key] = value
            
            elif table_type == "balance_sheet":
                # Look for key balance sheet metrics
                if "balance_analysis" in analysis:
                    balance_analysis = analysis["balance_analysis"]
                    for key, value in balance_analysis.items():
                        balance_sheet_data[key] = value
            
            elif table_type == "cash_flow":
                # Look for key cash flow metrics
                if "cash_flow_analysis" in analysis:
                    cash_flow_analysis = analysis["cash_flow_analysis"]
                    for key, value in cash_flow_analysis.items():
                        cash_flow_data[key] = value
        
        # Add financial data to report
        report["summary"]["key_metrics"] = key_metrics
        
        if income_statement_data:
            report["summary"]["income_statement"] = income_statement_data
        if balance_sheet_data:
            report["summary"]["balance_sheet"] = balance_sheet_data
        if cash_flow_data:
            report["summary"]["cash_flow"] = cash_flow_data
        
        # Add growth rates if available
        growth_rates = {}
        for table_analysis in table_analyses:
            analysis = table_analysis.get("analysis", {})
            if "growth_rates" in analysis:
                growth_rates.update(analysis["growth_rates"])
        
        if growth_rates:
            report["summary"]["growth_rates"] = growth_rates
        
        return report
    
    def _generate_detailed_report(self, document: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed financial report.
        
        Args:
            document: Document data
            config: Report configuration
            
        Returns:
            Detailed report
        """
        # Start with a summary report
        report = self._generate_summary_report(document, config)
        report["title"] = config.get("title", "Detailed Financial Report")
        
        # Add detailed analysis
        financial_data = document.get("financial_data", {})
        text_analysis = financial_data.get("text_analysis", {})
        table_analyses = financial_data.get("table_analyses", [])
        
        # Add full table data
        tables_data = document.get("tables_data", {})
        
        detailed_tables = {}
        for page_num, page_tables in tables_data.items():
            for table_idx, table in enumerate(page_tables):
                table_id = f"page_{page_num}_table_{table_idx}"
                detailed_tables[table_id] = {
                    "page": page_num,
                    "id": table_idx,
                    "header": table.get("header", []),
                    "rows": table.get("rows", []),
                    "metadata": {
                        "bbox": table.get("bbox"),
                        "row_count": table.get("row_count"),
                        "col_count": table.get("col_count"),
                        "extraction_method": table.get("extraction_method")
                    }
                }
                
                # Find and add table analysis if available
                for table_analysis in table_analyses:
                    if table_analysis.get("page") == page_num and table_analysis.get("table_id") == table_idx:
                        detailed_tables[table_id]["analysis"] = table_analysis.get("analysis", {})
                        break
        
        report["details"] = {
            "tables": detailed_tables,
            "text_metrics": text_analysis
        }
        
        return report
    
    def _generate_comparative_report(self, document: Dict[str, Any], comparison_docs: Dict[str, Dict[str, Any]], 
                                   config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comparative financial report.
        
        Args:
            document: Primary document data
            comparison_docs: Dictionary of documents to compare with
            config: Report configuration
            
        Returns:
            Comparative report
        """
        # Start with a summary of the main document
        report = self._generate_summary_report(document, config)
        report["title"] = config.get("title", "Comparative Financial Report")
        
        # Add comparative analysis
        report["comparative"] = {
            "documents": [document.get("file_path", "Unknown")],
            "analysis": {}
        }
        
        # Add compared documents
        for doc_id, comp_doc in comparison_docs.items():
            report["comparative"]["documents"].append(comp_doc.get("file_path", doc_id))
        
        # Compare key financial metrics
        main_financial_data = document.get("financial_data", {})
        main_table_analyses = main_financial_data.get("table_analyses", [])
        
        # Collect metrics from the main document
        main_metrics = self._extract_metrics_for_comparison(main_table_analyses)
        
        # Build comparative analysis
        comparison_results = {}
        for doc_id, comp_doc in comparison_docs.items():
            comp_financial_data = comp_doc.get("financial_data", {})
            comp_table_analyses = comp_financial_data.get("table_analyses", [])
            
            # Extract comparable metrics
            comp_metrics = self._extract_metrics_for_comparison(comp_table_analyses)
            
            # Compare metrics
            doc_comparison = {}
            for metric_type, metrics in main_metrics.items():
                if metric_type in comp_metrics:
                    doc_comparison[metric_type] = self._compare_metrics(metrics, comp_metrics[metric_type])
            
            comparison_results[doc_id] = doc_comparison
        
        report["comparative"]["analysis"] = comparison_results
        
        return report
    
    def _extract_metrics_for_comparison(self, table_analyses: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract metrics that can be compared between documents.
        
        Args:
            table_analyses: List of table analyses
            
        Returns:
            Extracted metrics organized by type
        """
        metrics = {
            "income_statement": {},
            "balance_sheet": {},
            "cash_flow": {},
            "ratios": {}
        }
        
        for table_analysis in table_analyses:
            analysis = table_analysis.get("analysis", {})
            table_type = analysis.get("table_type", "unknown")
            
            if table_type == "income_statement" and "income_analysis" in analysis:
                metrics["income_statement"].update(analysis["income_analysis"])
            elif table_type == "balance_sheet" and "balance_analysis" in analysis:
                metrics["balance_sheet"].update(analysis["balance_analysis"])
            elif table_type == "cash_flow" and "cash_flow_analysis" in analysis:
                metrics["cash_flow"].update(analysis["cash_flow_analysis"])
            elif table_type == "ratios" and "ratio_analysis" in analysis:
                metrics["ratios"].update(analysis["ratio_analysis"])
        
        return metrics
    
    def _compare_metrics(self, metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two sets of metrics.
        
        Args:
            metrics1: First set of metrics
            metrics2: Second set of metrics
            
        Returns:
            Comparison results
        """
        comparison = {}
        
        for key, values1 in metrics1.items():
            if key in metrics2:
                values2 = metrics2[key]
                
                # Check if values are lists (time series data)
                if isinstance(values1, list) and isinstance(values2, list):
                    # Calculate differences
                    if len(values1) == len(values2):
                        diffs = []
                        percent_changes = []
                        
                        for i in range(len(values1)):
                            if values1[i] is not None and values2[i] is not None:
                                diff = values2[i] - values1[i]
                                diffs.append(diff)
                                
                                if values1[i] != 0:
                                    percent_change = (diff / abs(values1[i])) * 100
                                    percent_changes.append(round(percent_change, 2))
                                else:
                                    percent_changes.append(None)
                            else:
                                diffs.append(None)
                                percent_changes.append(None)
                        
                        comparison[key] = {
                            "values1": values1,
                            "values2": values2,
                            "absolute_diff": diffs,
                            "percent_change": percent_changes
                        }
                    else:
                        # Different lengths, can't directly compare
                        comparison[key] = {
                            "values1": values1,
                            "values2": values2,
                            "note": "Different time periods, direct comparison not possible"
                        }
                else:
                    # Not lists, compare single values
                    comparison[key] = {
                        "values1": values1,
                        "values2": values2
                    }
        
        return comparison
    
    async def _query_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Query financial data from analyzed documents.
        
        Args:
            task: Task with query parameters
            
        Returns:
            Query results
        """
        query_type = task.get("query_type", "metrics")
        doc_id = task.get("doc_id")
        
        if not doc_id:
            return {
                "status": "error",
                "message": "Missing document ID"
            }
        
        # Check if document exists
        if doc_id not in self.memory["documents"]:
            return {
                "status": "error",
                "message": f"Document '{doc_id}' not found"
            }
        
        try:
            document = self.memory["documents"][doc_id]
            
            if query_type == "metrics":
                metrics = task.get("metrics", [])
                results = self._query_metrics(document, metrics)
                
                return {
                    "status": "success",
                    "message": "Query executed successfully",
                    "results": results
                }
            elif query_type == "tables":
                filters = task.get("filters", {})
                results = self._query_tables(document, filters)
                
                return {
                    "status": "success",
                    "message": "Query executed successfully",
                    "results": results
                }
            else:
                return {
                    "status": "error",
                    "message": f"Unknown query type: {query_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            return {
                "status": "error",
                "message": f"Error executing query: {str(e)}"
            }
    
    def _query_metrics(self, document: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Query specific metrics from document.
        
        Args:
            document: Document data
            metrics: List of metrics to query
            
        Returns:
            Query results
        """
        results = {}
        financial_data = document.get("financial_data", {})
        text_analysis = financial_data.get("text_analysis", {})
        table_analyses = financial_data.get("table_analyses", [])
        
        for metric in metrics:
            # Check text analysis first
            for page_num, page_metrics in text_analysis.items():
                if metric in page_metrics:
                    results[metric] = {
                        "source": f"text_page_{page_num}",
                        "value": page_metrics[metric]
                    }
                    break
            
            # If not found in text, check table analyses
            if metric not in results:
                for table_analysis in table_analyses:
                    analysis = table_analysis.get("analysis", {})
                    
                    # Check each possible location within the analysis
                    table_type = analysis.get("table_type", "unknown")
                    if table_type == "income_statement" and "income_analysis" in analysis:
                        if metric in analysis["income_analysis"]:
                            results[metric] = {
                                "source": f"table_page_{table_analysis['page']}_id_{table_analysis['table_id']}",
                                "value": analysis["income_analysis"][metric]
                            }
                            break
                    elif table_type == "balance_sheet" and "balance_analysis" in analysis:
                        if metric in analysis["balance_analysis"]:
                            results[metric] = {
                                "source": f"table_page_{table_analysis['page']}_id_{table_analysis['table_id']}",
                                "value": analysis["balance_analysis"][metric]
                            }
                            break
                    elif table_type == "cash_flow" and "cash_flow_analysis" in analysis:
                        if metric in analysis["cash_flow_analysis"]:
                            results[metric] = {
                                "source": f"table_page_{table_analysis['page']}_id_{table_analysis['table_id']}",
                                "value": analysis["cash_flow_analysis"][metric]
                            }
                            break
                    elif table_type == "ratios" and "ratio_analysis" in analysis:
                        if metric in analysis["ratio_analysis"]:
                            results[metric] = {
                                "source": f"table_page_{table_analysis['page']}_id_{table_analysis['table_id']}",
                                "value": analysis["ratio_analysis"][metric]
                            }
                            break
        
        return results
    
    def _query_tables(self, document: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Query tables from document with filters.
        
        Args:
            document: Document data
            filters: Filters to apply to tables
            
        Returns:
            Filtered tables
        """
        results = {}
        tables_data = document.get("tables_data", {})
        
        # Filter by table type if specified
        table_type = filters.get("table_type")
        
        # Get table analyses for type identification
        financial_data = document.get("financial_data", {})
        table_analyses = financial_data.get("table_analyses", [])
        
        # Build a mapping of tables to their types
        table_types = {}
        for table_analysis in table_analyses:
            page = table_analysis.get("page")
            table_id = table_analysis.get("table_id")
            analysis = table_analysis.get("analysis", {})
            detected_type = analysis.get("table_type", "unknown")
            
            if page is not None and table_id is not None:
                table_types[(page, table_id)] = detected_type
        
        # Apply filters
        for page_num, page_tables in tables_data.items():
            filtered_tables = []
            
            for table_idx, table in enumerate(page_tables):
                # Check if table matches type filter
                if table_type:
                    detected_type = table_types.get((page_num, table_idx), "unknown")
                    if detected_type != table_type:
                        continue
                
                # You can add more filters here
                
                # Include table in results
                filtered_tables.append({
                    "id": table_idx,
                    "header": table.get("header", []),
                    "rows": table.get("rows", []),
                    "metadata": {
                        "bbox": table.get("bbox"),
                        "row_count": table.get("row_count"),
                        "col_count": table.get("col_count"),
                        "extraction_method": table.get("extraction_method")
                    },
                    "type": table_types.get((page_num, table_idx), "unknown")
                })
            
            if filtered_tables:
                results[str(page_num)] = filtered_tables
        
        return results
