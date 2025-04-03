# file: tasks.py
import os
import json
import logging
from celery_worker import celery_app
from config import Config
from database import update_document_status # Add DB import

# Import our processing modules (ensure these are importable in the Celery worker context)
from ocr_text_extractor import extract_text_with_ocr
from financial_data_extractor import (
    extract_isin_numbers,
    find_associated_data,
    extract_tables_from_text
)

# Configure logging for the task worker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tasks")

@celery_app.task(bind=True, name='tasks.process_document')
def process_document_task(self, file_path, document_id, original_filename, language):
    """
    Celery task to process an uploaded document asynchronously.
    Performs OCR, extracts financial data and tables.
    """
    logger.info(f"Starting background processing for document: {document_id} ({original_filename})")
    upload_folder = Config.UPLOAD_FOLDER # Use config for consistency

    try:
        # 1. Perform OCR
        logger.info(f"Starting OCR processing: {document_id}")
        document = extract_text_with_ocr(file_path, language=language)

        if not document:
            logger.error(f"OCR processing failed or returned no data for {document_id}")
            # Optionally, update status in DB here
            return {"status": "failed", "error": "OCR processing failed"}

        # Save extracted text
        extraction_path = os.path.join(upload_folder, f"{document_id}_ocr.json")
        with open(extraction_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, indent=2, ensure_ascii=False)
        logger.info(f"OCR processing completed: {document_id}")

        # 2. Extract financial data
        all_text = ""
        for page_num, page_data in document.items():
            all_text += page_data.get("text", "") + "\n\n"

        # Extract ISIN numbers
        isin_numbers = extract_isin_numbers(all_text)

        # Extract associated data for each ISIN
        financial_data = []
        for isin in isin_numbers:
            data = find_associated_data(all_text, isin, document)
            if data:
                financial_data.append(data)

        # Save financial data
        financial_path = os.path.join(upload_folder, f"{document_id}_financial.json")
        with open(financial_path, 'w', encoding='utf-8') as f:
            json.dump(financial_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Financial data extraction completed: {document_id}")

        # 3. Extract tables
        tables = extract_tables_from_text(all_text)

        # Save tables (if any found)
        tables_path = None
        if tables:
            tables_path = os.path.join(upload_folder, f"{document_id}_tables.json")
            with open(tables_path, 'w', encoding='utf-8') as f:
                json.dump(tables, f, indent=2, ensure_ascii=False)
            logger.info(f"Table extraction completed: {document_id} ({len(tables)} tables)")
        else:
             logger.info(f"No tables found during extraction for: {document_id}")


        # --- DB UPDATE ON SUCCESS START ---
        logger.info(f"Updating database record for successful processing of {document_id}")
        update_success = update_document_status(
            document_id=document_id,
            status="completed",
            ocr_path=extraction_path, # Store path to OCR results
            financial_path=financial_path, # Store path to financial results
            tables_path=tables_path # Store path to tables results (will be None if no tables)
        )
        if not update_success:
            logger.error(f"Failed to update database status to 'completed' for {document_id}")
            # Decide how to handle this - task technically succeeded but DB update failed.
            # Maybe raise an exception to trigger Celery retry?
        else:
            logger.info(f"Successfully updated database status to 'completed' for {document_id}")
        # --- DB UPDATE ON SUCCESS END ---

        logger.info(f"Successfully processed document: {document_id}")
        # Return value is still useful for direct task result inspection if needed
        return {
            "status": "completed",
            "document_id": document_id,
            "page_count": len(document),
            "isin_count": len(isin_numbers),
            "table_count": len(tables),
            "extraction_path": extraction_path,
            "financial_path": financial_path,
            "tables_path": tables_path
        }

    except Exception as e:
        error_message = f"Error processing document in background task: {str(e)}"
        logger.exception(error_message) # Use logger.exception to include traceback

        # --- DB UPDATE ON FAILURE START ---
        logger.info(f"Updating database record for failed processing of {document_id}")
        update_success = update_document_status(
            document_id=document_id,
            status="failed",
            error_message=error_message # Record the error message
        )
        if not update_success:
             logger.error(f"Failed to update database status to 'failed' for {document_id} after task error.")
        # --- DB UPDATE ON FAILURE END ---

        # Clean up potentially partially created files? (Consider carefully)
        # Example:
        # if 'extraction_path' in locals() and os.path.exists(extraction_path): os.remove(extraction_path)
        # if 'financial_path' in locals() and os.path.exists(financial_path): os.remove(financial_path)
        # if 'tables_path' in locals() and tables_path and os.path.exists(tables_path): os.remove(tables_path)
        # Return value indicates failure
        return {"status": "failed", "error": error_message}