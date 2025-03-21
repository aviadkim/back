import os
import sys
import logging
import asyncio
from typing import Dict, Any, List, Optional
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.init_app import init_app
from agents.financial.financial_agent import FinancialAgent

# Initialize app and agents
app_context = init_app()
financial_agent = app_context["financial_agent"]

# Create FastAPI app
app = FastAPI(title="Financial Document Analyzer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define models
class AnalyzeDocumentRequest(BaseModel):
    doc_id: Optional[str] = None
    force_refresh: bool = False

class ExtractTablesRequest(BaseModel):
    page_numbers: Optional[List[int]] = None

class AnalyzeTablesRequest(BaseModel):
    tables: List[Dict[str, Any]]

class SaveTemplateRequest(BaseModel):
    template_name: str
    template_def: Dict[str, Any]

class ApplyTemplateRequest(BaseModel):
    template_name: str
    doc_id: str

class GenerateReportRequest(BaseModel):
    doc_id: str
    report_type: str = "summary"
    config: Dict[str, Any] = {}
    comparison_doc_ids: Optional[List[str]] = None

class QueryDataRequest(BaseModel):
    doc_id: str
    query_type: str
    metrics: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None

# Routes
@app.post("/analyze_document")
async def analyze_document(
    file: UploadFile = File(...),
    request_data: str = Form(...),
):
    """Analyze a PDF document."""
    # Parse request data
    request = AnalyzeDocumentRequest.parse_raw(request_data)
    
    # Save uploaded file
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        # Write uploaded file to temp file
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Create task
        task = {
            "type": "analyze_document",
            "pdf_path": tmp_path,
            "doc_id": request.doc_id if request.doc_id else file.filename,
            "force_refresh": request.force_refresh
        }
        
        # Process task
        result = await financial_agent.process(task)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract_tables")
async def extract_tables(
    file: UploadFile = File(...),
    request_data: str = Form(...),
):
    """Extract tables from a PDF document."""
    # Parse request data
    request = ExtractTablesRequest.parse_raw(request_data)
    
    # Save uploaded file
    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        # Write uploaded file to temp file
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Create task
        task = {
            "type": "extract_tables",
            "pdf_path": tmp_path,
            "page_numbers": request.page_numbers
        }
        
        # Process task
        result = await financial_agent.process(task)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return result
    except Exception as e:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_tables")
async def analyze_tables(request: AnalyzeTablesRequest):
    """Analyze tables from a PDF document."""
    try:
        # Create task
        task = {
            "type": "analyze_tables",
            "tables": request.tables
        }
        
        # Process task
        result = await financial_agent.process(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save_template")
async def save_template(request: SaveTemplateRequest):
    """Save a template for future use."""
    try:
        # Create task
        task = {
            "type": "save_template",
            "template_name": request.template_name,
            "template_def": request.template_def
        }
        
        # Process task
        result = await financial_agent.process(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apply_template")
async def apply_template(request: ApplyTemplateRequest):
    """Apply a saved template to document data."""
    try:
        # Create task
        task = {
            "type": "apply_template",
            "template_name": request.template_name,
            "doc_id": request.doc_id
        }
        
        # Process task
        result = await financial_agent.process(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_report")
async def generate_report(request: GenerateReportRequest):
    """Generate a financial report."""
    try:
        # Create task
        task = {
            "type": "generate_report",
            "doc_id": request.doc_id,
            "report_type": request.report_type,
            "config": request.config
        }
        
        if request.comparison_doc_ids:
            task["comparison_doc_ids"] = request.comparison_doc_ids
        
        # Process task
        result = await financial_agent.process(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query_data")
async def query_data(request: QueryDataRequest):
    """Query financial data from analyzed documents."""
    try:
        # Create task
        task = {
            "type": "query_data",
            "doc_id": request.doc_id,
            "query_type": request.query_type
        }
        
        if request.metrics:
            task["metrics"] = request.metrics
        
        if request.filters:
            task["filters"] = request.filters
        
        # Process task
        result = await financial_agent.process(task)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_documents")
async def list_documents():
    """List all analyzed documents."""
    try:
        documents = financial_agent.memory.get("documents", {})
        
        # Create summary list
        document_list = []
        for doc_id, doc_data in documents.items():
            document_list.append({
                "id": doc_id,
                "file_path": doc_data.get("file_path", "Unknown"),
                "analysis_date": doc_data.get("analysis_date", "Unknown"),
                "page_count": len(doc_data.get("text_data", {})),
                "table_count": sum(len(tables) for tables in doc_data.get("tables_data", {}).values())
            })
        
        return {
            "status": "success",
            "documents": document_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_templates")
async def list_templates():
    """List all saved templates."""
    try:
        templates = financial_agent.memory.get("templates", {})
        
        # Create summary list
        template_list = []
        for template_name, template_data in templates.items():
            template_list.append({
                "name": template_name,
                "created": template_data.get("created", "Unknown"),
                "updated": template_data.get("updated", "Unknown")
            })
        
        return {
            "status": "success",
            "templates": template_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_reports")
async def list_reports():
    """List all generated reports."""
    try:
        reports = financial_agent.memory.get("reports", {})
        
        # Create summary list
        report_list = []
        for report_id, report_data in reports.items():
            report_list.append({
                "id": report_id,
                "title": report_data.get("title", "Unknown"),
                "generated_at": report_data.get("generated_at", "Unknown"),
                "document": report_data.get("document", "Unknown"),
                "type": "comparative" if "comparative" in report_data else (
                    "detailed" if "details" in report_data else "summary"
                )
            })
        
        return {
            "status": "success",
            "reports": report_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_report/{report_id}")
async def get_report(report_id: str):
    """Get a specific report."""
    try:
        reports = financial_agent.memory.get("reports", {})
        
        if report_id not in reports:
            raise HTTPException(status_code=404, detail=f"Report '{report_id}' not found")
        
        return {
            "status": "success",
            "report": reports[report_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
