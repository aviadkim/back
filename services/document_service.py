import os
import json
import logging
from datetime import datetime, timezone # Ensure timezone is imported
# Document model is no longer needed for queries, but might be for type hints if adapted
# from models.document_models import Document
from shared.database import db # Import DynamoDB connector
from utils.pdf_processor import PDFProcessor
from agent_framework.memory_agent import MemoryAgent
from agent_framework.coordinator import AgentCoordinator
# from config import Config # Config might not be needed directly here anymore

# Set up logging
logger = logging.getLogger(__name__)

# Create agent instances (assuming they don't need db passed in)
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

# Define the DynamoDB table name (consider making this configurable)
DOCUMENTS_TABLE_NAME = "financial_documents"

def process_document(document_id, file_path, language='he', processing_mode='standard'):
    """
    Process a document file, extract content, and update DynamoDB record.
    Meant to be run as a background task.
    """
    logger.info(f"Starting processing for document ID: {document_id}")
    document = None # Initialize document variable
    try:
        # Get document from DynamoDB
        document = db.find_document(DOCUMENTS_TABLE_NAME, {'id': document_id})

        if not document:
            logger.error(f"Document {document_id} not found in database for processing.")
            return False

        # Update status to processing
        update_payload = {
            'status': 'processing',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        if not db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, update_payload):
             logger.warning(f"Failed to update status to 'processing' for document {document_id}. Proceeding anyway.")
             # Decide if processing should stop if status update fails

        # Process file based on type
        file_type = document.get('file_type', '').lower()
        logger.info(f"Processing file type: {file_type} for document {document_id}")

        analysis_data = {}
        analysis_path = None
        processing_successful = False

        if file_type == 'pdf':
            pdf_processor = PDFProcessor()
            extracted_text, metadata, page_count = pdf_processor.process_pdf(file_path, language)
            logger.info(f"PDF processing complete for {document_id}. Pages: {page_count}, Text length: {len(extracted_text)}")

            # Prepare analysis data structure
            analysis_data = {
                'document_id': document_id,
                'file_name': document.get('file_name'),
                'language': language,
                'processing_mode': processing_mode,
                'processing_date': datetime.now(timezone.utc).isoformat(),
                'metadata': metadata or {}, # Ensure metadata is at least an empty dict
                'text_content': extracted_text or "", # Ensure text is at least empty string
                'tables': [],
                'entities': [],
                'financial_data': {},
                'page_count': page_count,
            }
            processing_successful = True # Mark as successful for now

        elif file_type in ['docx', 'xlsx', 'csv']:
            logger.warning(f"Processing for file type {file_type} not fully implemented yet for document {document_id}")
            # Placeholder processing for other types
            analysis_data = {
                'document_id': document_id,
                'file_name': document.get('file_name'),
                'language': language,
                'processing_mode': processing_mode,
                'processing_date': datetime.now(timezone.utc).isoformat(),
                'metadata': {},
                'text_content': f"[Content extraction for {file_type} files not implemented yet]",
                'tables': [], 'entities': [], 'financial_data': {},
                'page_count': 1, # Default assumption
            }
            processing_successful = True # Mark as successful for now

        else:
            logger.error(f"Unsupported file type: {file_type} for document {document_id}")
            processing_successful = False

        # --- Post-processing steps (common for supported types) ---
        if processing_successful:
            # Create data directory if it doesn't exist (consider central config for path)
            data_dir = os.path.join('data', 'documents')
            os.makedirs(data_dir, exist_ok=True)

            # Save analysis data to a JSON file (consider S3 or other storage for production)
            analysis_path = os.path.join(data_dir, f"{document_id}_analysis.json")
            try:
                with open(analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, ensure_ascii=False, indent=2)
                logger.info(f"Analysis data saved to {analysis_path} for document {document_id}")
            except IOError as e:
                 logger.error(f"Failed to save analysis file {analysis_path}: {e}")
                 analysis_path = None # Don't store path if saving failed
                 processing_successful = False # Mark as failed if analysis can't be saved

        # --- Final DB Update ---
        final_status = 'completed' if processing_successful else 'failed'
        final_update_payload = {
            'status': final_status,
            'updated_at': datetime.now(timezone.utc).isoformat(),
            # Only include analysis_path and page_count if processing was successful
            'analysis_path': analysis_path if processing_successful and analysis_path else document.get('analysis_path'), # Keep old path if new one failed? Or set null?
            'page_count': analysis_data.get('page_count') if processing_successful else document.get('page_count')
        }

        if not db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, final_update_payload):
             logger.error(f"Failed to update final status to '{final_status}' for document {document_id}")
             # This is problematic, status might be stuck in 'processing'

        # --- Post-DB Update Actions ---
        if processing_successful and analysis_path:
            # Add document context to memory agent
            if memory_agent:
                memory_agent.add_document(document_id, analysis_path)
                logger.info(f"Document {document_id} added/updated in memory agent.")

            # Trigger further AI analysis (if applicable)
            # Consider if this should be a separate task or part of this one
            analyze_document(document_id) # Call the next step

        logger.info(f"Processing finished for document {document_id} with status: {final_status}")
        return processing_successful

    except Exception as e:
        logger.exception(f"Unhandled error processing document {document_id}: {str(e)}")
        # Attempt to update status to failed in DynamoDB
        try:
            if document_id: # Ensure we have an ID
                 db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
        except Exception as db_error:
            logger.error(f"Failed to update document status to 'failed' after exception for {document_id}: {db_error}")
        return False


def analyze_document(document_id, force=False):
    """
    Analyze document content with AI using AgentCoordinator.
    Meant to be run as a background task after initial processing.
    """
    logger.info(f"Starting AI analysis for document ID: {document_id}. Force re-analysis: {force}")
    document = None # Initialize
    try:
        # Get document from DynamoDB
        document = db.find_document(DOCUMENTS_TABLE_NAME, {'id': document_id})

        if not document:
            logger.error(f"Document {document_id} not found in database for AI analysis.")
            return False

        analysis_path = document.get('analysis_path')
        if not analysis_path or not os.path.exists(analysis_path):
            logger.error(f"Analysis file path missing or file not found for document {document_id}. Path: {analysis_path}. Cannot perform AI analysis.")
            # Optionally update status?
            # db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'analysis_failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
            return False

        # Load existing analysis data
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
             logger.error(f"Error reading or parsing analysis file {analysis_path}: {e}")
             # db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'analysis_failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
             return False

        # Check if already analyzed (based on presence of specific keys) and not forcing
        already_analyzed = (
            bool(analysis_data.get('tables')) or # Check if keys exist and are not empty if needed
            bool(analysis_data.get('entities')) or
            bool(analysis_data.get('financial_data'))
        )
        if already_analyzed and not force:
            logger.info(f"Document {document_id} already has AI analysis data. Skipping (force=False).")
            # Ensure status is 'completed' if skipped
            if document.get('status') != 'completed':
                 db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'completed', 'updated_at': datetime.now(timezone.utc).isoformat()})
            return True

        # Update status to indicate AI analysis is in progress
        update_payload = {
            'status': 'analyzing',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        if not db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, update_payload):
             logger.warning(f"Failed to update status to 'analyzing' for document {document_id}. Proceeding anyway.")

        # Extract text content for the agent
        text_content = analysis_data.get('text_content', '')
        if not text_content:
            logger.error(f"No text content found in analysis file for document {document_id}. Cannot perform AI analysis.")
            db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'analysis_failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
            return False

        # Call the Agent Coordinator to perform AI analysis
        logger.info(f"Calling AgentCoordinator for document {document_id}...")
        ai_result = agent_coordinator.analyze_document(
            document_id=document_id,
            text_content=text_content,
            document_type=document.get('document_type', 'other'),
            language=analysis_data.get('language', 'he') # Use language from initial processing
        )
        logger.info(f"AgentCoordinator analysis finished for document {document_id}.")

        # Update analysis data with AI results (overwrite or merge?)
        analysis_data['tables'] = ai_result.get('tables', [])
        analysis_data['entities'] = ai_result.get('entities', [])
        analysis_data['financial_data'] = ai_result.get('financial_data', {})
        analysis_data['ai_analysis_date'] = datetime.now(timezone.utc).isoformat() # Add timestamp for AI analysis

        # Save updated analysis data back to the file
        try:
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Updated analysis data saved to {analysis_path} for document {document_id}")
        except IOError as e:
             logger.error(f"Failed to save updated analysis file {analysis_path}: {e}")
             # Don't update status to completed if saving failed
             db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'analysis_failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
             return False

        # Update final document status in DynamoDB
        final_status = 'completed'
        final_update_payload = {
            'status': final_status,
            'updated_at': datetime.now(timezone.utc).isoformat()
            # Add page_count if it wasn't set during initial processing but is available now?
            # 'page_count': analysis_data.get('page_count')
        }
        if not db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, final_update_payload):
             logger.error(f"Failed to update final status to '{final_status}' after AI analysis for document {document_id}")
             # Even if status update fails, the analysis file was updated, so return True? Or False?
             return False # Let's say failure to update status is a failure overall

        # Re-add/update document in memory agent with potentially richer analysis data
        if memory_agent:
             memory_agent.add_document(document_id, analysis_path)
             logger.info(f"Document {document_id} re-added/updated in memory agent after AI analysis.")

        logger.info(f"AI analysis finished successfully for document {document_id}.")
        return True

    except Exception as e:
        logger.exception(f"Unhandled error during AI analysis for document {document_id}: {str(e)}")
        # Attempt to update status to failed in DynamoDB
        try:
            if document_id: # Ensure we have an ID
                 db.update_document(DOCUMENTS_TABLE_NAME, {'id': document_id}, {'status': 'analysis_failed', 'updated_at': datetime.now(timezone.utc).isoformat()})
        except Exception as db_error:
            logger.error(f"Failed to update document status to 'analysis_failed' after exception for {document_id}: {db_error}")
        return False
