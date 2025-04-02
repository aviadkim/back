"""Service layer for document Q&A feature."""
import os
import logging
import json
from .simple_qa import SimpleQA
from ...shared.ai.service import AIService

logger = logging.getLogger(__name__)

class DocumentQAService:
    """Service for answering questions about documents"""
    
    def __init__(self):
        self.simple_qa = SimpleQA()
        self.ai_service = AIService()
        # Create extractions directory if it doesn't exist
        self.extraction_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'extractions'))
        os.makedirs(self.extraction_dir, exist_ok=True)
        
        # Check if OpenRouter is available
        self.has_openrouter = hasattr(self.ai_service, 'has_valid_openrouter_key') and self.ai_service.has_valid_openrouter_key
        if self.has_openrouter:
            logger.info("OpenRouter is available for enhanced Q&A responses")
    
    def answer_question(self, document_id, question):
        """Answer a question about a document
        
        Args:
            document_id: Document ID
            question: Question string
            
        Returns:
            Answer string
        """
        logger.info(f"Question about document {document_id}: {question}")
        
        # Get document content
        document_content = self._get_document_content(document_id)
        if not document_content:
            return "Sorry, I couldn't access the document content."
        
        # Try to use AI service first with OpenRouter if available
        try:
            doc_data = json.loads(document_content)
            content = doc_data.get('content', document_content)
            
            # Check which AI service to use
            if self.has_openrouter:
                logger.info("Using OpenRouter to answer question")
                return self.ai_service.generate_response(question, content, model="openrouter")
            elif self.ai_service.has_valid_hf_key or self.ai_service.has_valid_gemini_key:
                logger.info("Using AI service to answer question")
                return self.ai_service.generate_response(question, content)
        except Exception as e:
            logger.error(f"Error using AI service: {e}")
        
        # Fall back to simple QA
        logger.info("Falling back to simple QA")
        return self.simple_qa.answer(question, document_content)
    
    def _get_document_content(self, document_id):
        """Get document content based on ID"""
        # This would normally query a database or file system
        try:
            # First make sure the directory exists
            if not os.path.exists(self.extraction_dir):
                logger.error(f"Extraction directory does not exist: {self.extraction_dir}")
                return None
            
            logger.info(f"Looking for documents in {self.extraction_dir}")
            
            # List files and check for the document
            for filename in os.listdir(self.extraction_dir):
                if filename.startswith(document_id) and (filename.endswith('_extraction.json') or filename.endswith('sample_extraction.json')):
                    path = os.path.join(self.extraction_dir, filename)
                    logger.info(f"Found document extraction at {path}")
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        logger.error(f"Error reading file: {e}")
                        return None
            
            # If we reach here, we didn't find the file
            logger.error(f"Could not find extraction for document {document_id}")
            logger.info(f"Available files in {self.extraction_dir}: {os.listdir(self.extraction_dir)}")
            return None
        except Exception as e:
            logger.error(f"Error getting document content: {e}")
            return None
    
    def _is_financial_question(self, question):
        """Check if a question is about financial information"""
        financial_keywords = [
            'isin', 'price', 'value', 'stock', 'security', 'securities', 
            'portfolio', 'holding', 'holdings', 'asset', 'investment', 
            'currency', 'euro', 'dollar', 'eur', 'usd', 'gbp', 'percent'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in financial_keywords)
