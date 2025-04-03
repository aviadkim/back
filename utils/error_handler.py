import logging
import traceback
import json
from flask import jsonify
from pathlib import Path # Added import

logger = logging.getLogger(__name__)

class ErrorResponse:
    """Standardized error response format."""
    
    @staticmethod
    def create(message, error=None, status_code=400, details=None):
        """Create a standardized error response.
        
        Args:
            message: User-friendly error message
            error: Original error object or message
            status_code: HTTP status code
            details: Additional error details
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        response = {
            "status": "error",
            "message": message,
        }
        
        if details:
            response["details"] = details
            
        if error and isinstance(error, Exception):
            logger.error(f"{message}: {str(error)}\n{traceback.format_exc()}")
        elif error:
            logger.error(f"{message}: {error}")
        else:
            logger.error(message)
            
        return jsonify(response), status_code

class ErrorHandler:
    """Centralized error handling for the application."""
    
    @staticmethod
    def handle_pdf_extraction_error(e, file_path, user_message=None):
        """Handle errors in PDF text extraction.
        
        Args:
            e: Exception object
            file_path: Path to the PDF file
            user_message: Optional user-friendly message
            
        Returns:
            Dict with error information
        """
        message = user_message or "Failed to extract text from document"
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        
        return {
            "error": str(e),
            "message": message,
            "metadata": {
                "filename": Path(file_path).name if hasattr(Path, 'name') else file_path,
                "processing_status": "failed"
            }
        }
    
    @staticmethod
    def handle_database_error(e, operation, user_message=None):
        """Handle database operation errors.
        
        Args:
            e: Exception object
            operation: Description of the database operation
            user_message: Optional user-friendly message
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        message = user_message or f"Database error during {operation}"
        logger.error(f"Database error during {operation}: {str(e)}\n{traceback.format_exc()}")
        
        return ErrorResponse.create(
            message=message,
            error=e,
            status_code=500,
            details={"operation": operation}
        )
    
    @staticmethod
    def handle_invalid_request(message, details=None):
        """Handle invalid API requests.
        
        Args:
            message: Error message
            details: Additional error details
            
        Returns:
            Tuple of (response_dict, status_code)
        """
        return ErrorResponse.create(
            message=message,
            status_code=400,
            details=details
        )