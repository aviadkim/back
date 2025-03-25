import os
import json
import logging
from datetime import datetime
from models.document_models import Document, db
from utils.pdf_processor import PDFProcessor
from agent_framework.memory_agent import MemoryAgent
from agent_framework.coordinator import AgentCoordinator

# Set up logging
logger = logging.getLogger(__name__)

# Create agent instances
memory_agent = MemoryAgent()
agent_coordinator = AgentCoordinator()

def process_document(document_id, file_path, language='he', processing_mode='standard'):
    """
    Process a document file and extract content
    
    This function is meant to be run as a background task
    
    Args:
        document_id (str): The document ID
        file_path (str): Path to the document file
        language (str): Document language (default: 'he')
        processing_mode (str): Processing mode (basic, standard, detailed)
    
    Returns:
        bool: Success status
    """
    try:
        # Get document from database
        document = Document.query.get(document_id)
        
        if not document:
            logger.error(f"Document {document_id} not found in database")
            return False
        
        # Set document status to processing
        document.status = 'processing'
        db.session.commit()
        
        # Process file based on type
        file_type = document.file_type.lower()
        
        if file_type == 'pdf':
            # Process PDF
            pdf_processor = PDFProcessor()
            extracted_text, metadata, page_count = pdf_processor.process_pdf(file_path, language)
            
            # Update document with metadata
            document.page_count = page_count
            db.session.commit()
            
            # Create analysis data
            analysis_data = {
                'document_id': document_id,
                'file_name': document.file_name,
                'language': language,
                'processing_mode': processing_mode,
                'processing_date': datetime.now().isoformat(),
                'metadata': metadata,
                'text_content': extracted_text,
                'tables': [],  # Will be populated during analysis
                'entities': [],  # Will be populated during analysis
                'financial_data': {},  # Will be populated during analysis
                'page_count': page_count,
            }
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join('data', 'documents')
            os.makedirs(data_dir, exist_ok=True)
            
            # Save analysis data to file
            analysis_path = os.path.join(data_dir, f"{document_id}_analysis.json")
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # Update document with analysis path
            document.analysis_path = analysis_path
            document.status = 'completed'
            db.session.commit()
            
            # Add document to memory agent
            memory_agent.add_document(document_id, analysis_path)
            
            # Analyze document
            analyze_document(document_id)
            
            return True
        
        elif file_type in ['docx', 'xlsx', 'csv']:
            # Process other file types
            # This can be implemented based on file type
            logger.warning(f"Processing for file type {file_type} not fully implemented yet")
            
            # Create basic analysis data
            analysis_data = {
                'document_id': document_id,
                'file_name': document.file_name,
                'language': language,
                'processing_mode': processing_mode,
                'processing_date': datetime.now().isoformat(),
                'metadata': {},
                'text_content': f"[Content extraction for {file_type} files not implemented yet]",
                'tables': [],
                'entities': [],
                'financial_data': {},
                'page_count': 1,  # Default for non-PDF files
            }
            
            # Create data directory if it doesn't exist
            data_dir = os.path.join('data', 'documents')
            os.makedirs(data_dir, exist_ok=True)
            
            # Save analysis data to file
            analysis_path = os.path.join(data_dir, f"{document_id}_analysis.json")
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            # Update document with analysis path
            document.analysis_path = analysis_path
            document.status = 'completed'
            db.session.commit()
            
            return True
        
        else:
            # Unsupported file type
            logger.error(f"Unsupported file type: {file_type}")
            document.status = 'failed'
            db.session.commit()
            return False
            
    except Exception as e:
        logger.exception(f"Error processing document {document_id}: {str(e)}")
        
        # Update document status to failed
        try:
            document = Document.query.get(document_id)
            if document:
                document.status = 'failed'
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Error updating document status: {str(db_error)}")
            
        return False

def analyze_document(document_id, force=False):
    """
    Analyze document content with AI
    
    This function is meant to be run as a background task
    
    Args:
        document_id (str): The document ID
        force (bool): Force re-analysis even if already analyzed
        
    Returns:
        bool: Success status
    """
    try:
        # Get document from database
        document = Document.query.get(document_id)
        
        if not document:
            logger.error(f"Document {document_id} not found in database")
            return False
            
        # Check if document has analysis path
        if not document.analysis_path or not os.path.exists(document.analysis_path):
            logger.error(f"Document {document_id} has no analysis data")
            return False
            
        # Load analysis data
        with open(document.analysis_path, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
            
        # Check if document is already analyzed and not forcing re-analysis
        if (
            analysis_data.get('tables') 
            and analysis_data.get('entities') 
            and analysis_data.get('financial_data') 
            and not force
        ):
            logger.info(f"Document {document_id} already analyzed")
            return True
            
        # Set document status to processing
        document.status = 'processing'
        db.session.commit()
        
        # Extract text content
        text_content = analysis_data.get('text_content', '')
        
        if not text_content:
            logger.error(f"Document {document_id} has no text content")
            document.status = 'failed'
            db.session.commit()
            return False
            
        # Analyze document with agent coordinator
        result = agent_coordinator.analyze_document(
            document_id=document_id,
            text_content=text_content,
            document_type=document.document_type,
            language=analysis_data.get('language', 'he')
        )
        
        # Update analysis data with results
        if result.get('tables'):
            analysis_data['tables'] = result['tables']
            
        if result.get('entities'):
            analysis_data['entities'] = result['entities']
            
        if result.get('financial_data'):
            analysis_data['financial_data'] = result['financial_data']
            
        # Save updated analysis data
        with open(document.analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
        # Update document status
        document.status = 'completed'
        db.session.commit()
        
        # Re-add document to memory agent with updated analysis
        memory_agent.add_document(document_id, document.analysis_path)
        
        return True
        
    except Exception as e:
        logger.exception(f"Error analyzing document {document_id}: {str(e)}")
        
        # Update document status to failed
        try:
            document = Document.query.get(document_id)
            if document:
                document.status = 'failed'
                db.session.commit()
        except Exception as db_error:
            logger.error(f"Error updating document status: {str(db_error)}")
            
        return False
