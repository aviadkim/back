"""Service layer for document upload feature."""
import os
import uuid
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class DocumentUploadService:
    """Service for handling document uploads and management"""
    
    def __init__(self, upload_dir='uploads', extraction_dir='extractions'):
        self.upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', upload_dir))
        self.extraction_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', extraction_dir))
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.extraction_dir, exist_ok=True)
    
    def handle_upload(self, file, language='heb+eng'):
        """Handle a file upload
        
        Args:
            file: The uploaded file object
            language: OCR language setting
            
        Returns:
            Dict with document info or None on failure
        """
        try:
            # Generate a document ID
            document_id = f"doc_{uuid.uuid4().hex[:8]}"
            
            # Secure the filename and save with document ID prefix
            original_filename = secure_filename(file.filename)
            filename = f"{document_id}_{original_filename}"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save the file
            file.save(file_path)
            
            logger.info(f"Saved document {document_id} to {file_path}")
            
            # Create document record
            document = {
                'document_id': document_id,
                'filename': original_filename,
                'path': file_path,
                'upload_date': datetime.now().isoformat(),
                'status': 'uploaded',
                'language': language
            }
            
            # In a real application, this would be saved to a database
            # For now, we'll save to a JSON file
            self._save_document_record(document)
            
            # Create a sample extraction for testing
            self._create_sample_extraction(document_id, original_filename)
            
            # Queue for processing (in this simple version, we return immediately)
            # In a production system, this would trigger an async job
            return document
            
        except Exception as e:
            logger.error(f"Error handling upload: {e}")
            return None
    
    def list_documents(self):
        """List all documents
        
        Returns:
            List of document records
        """
        # In a real application, this would query a database
        # For now, we'll read all document records from JSON files
        try:
            documents = []
            record_dir = os.path.join(self.upload_dir, 'records')
            
            if os.path.exists(record_dir):
                for filename in os.listdir(record_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(record_dir, filename), 'r') as f:
                                doc = json.load(f)
                                documents.append(doc)
                        except:
                            pass
            
            # If we found documents in records, return them
            if documents:
                return documents
                
            # Fallback: Look for PDF files in uploads directory
            if os.path.exists(self.upload_dir):
                for filename in [f for f in os.listdir(self.upload_dir) if f.endswith('.pdf')]:
                    if filename.startswith('doc_'):
                        doc_id = filename.split('_')[0] + '_' + filename.split('_')[1]
                        documents.append({
                            'document_id': doc_id,
                            'filename': filename.replace(doc_id + '_', ''),
                            'path': os.path.join(self.upload_dir, filename),
                            'upload_date': datetime.now().isoformat(),
                            'status': 'uploaded'
                        })
                    else:
                        documents.append({
                            'document_id': f"doc_{uuid.uuid4().hex[:8]}",
                            'filename': filename,
                            'path': os.path.join(self.upload_dir, filename),
                            'upload_date': datetime.now().isoformat(),
                            'status': 'uploaded'
                        })
            
            # Also check for any sample extractions
            if os.path.exists(self.extraction_dir):
                for filename in os.listdir(self.extraction_dir):
                    if filename.endswith('sample_extraction.json'):
                        try:
                            doc_id = filename.split('_')[0] + '_' + filename.split('_')[1]
                            if not any(d['document_id'] == doc_id for d in documents):
                                documents.append({
                                    'document_id': doc_id,
                                    'filename': 'sample_document.pdf',
                                    'path': os.path.join(self.extraction_dir, filename),
                                    'upload_date': datetime.now().isoformat(),
                                    'status': 'processed'
                                })
                        except:
                            pass
            
            return documents
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    def get_document(self, document_id):
        """Get a document by ID
        
        Args:
            document_id: The document ID
            
        Returns:
            Document record or None if not found
        """
        record = self._get_document_record(document_id)
        if record:
            return record
            
        # Fallback: Look for file directly
        for filename in [f for f in os.listdir(self.upload_dir) if os.path.isfile(os.path.join(self.upload_dir, f))]:
            if filename.startswith(document_id) and filename.endswith('.pdf'):
                return {
                    'document_id': document_id,
                    'filename': filename.replace(document_id + '_', ''),
                    'path': os.path.join(self.upload_dir, filename),
                    'upload_date': datetime.now().isoformat(),
                    'status': 'uploaded'
                }
                
        # Also check for sample extractions
        if os.path.exists(self.extraction_dir):
            for filename in os.listdir(self.extraction_dir):
                if filename.startswith(document_id) and filename.endswith('sample_extraction.json'):
                    return {
                        'document_id': document_id,
                        'filename': 'sample_document.pdf',
                        'path': os.path.join(self.extraction_dir, filename),
                        'upload_date': datetime.now().isoformat(),
                        'status': 'processed'
                    }
        
        return None
    
    def get_financial_data(self, document_id):
        """Get financial data for a document
        
        Args:
            document_id: The document ID
            
        Returns:
            List of financial data entries or None if not found
        """
        # This is a placeholder that would normally integrate with the financial analysis feature
        # For now, return some dummy data
        return [
            {
                'isin': 'US0378331005',
                'name': 'Apple Inc.',
                'quantity': 100,
                'price': 145.86,
                'currency': 'USD',
                'market_value': 14586.00
            },
            {
                'isin': 'US02079K1079',
                'name': 'Alphabet Inc.',
                'quantity': 50,
                'price': 2321.34,
                'currency': 'USD',
                'market_value': 116067.00
            },
            {
                'isin': 'US5949181045',
                'name': 'Microsoft Corp',
                'quantity': 25,
                'price': 380.55,
                'currency': 'USD',
                'market_value': 9513.75
            }
        ]
    
    def _save_document_record(self, document):
        """Save a document record"""
        # In a real application, this would save to a database
        # For now, we'll create a file for each document
        record_dir = os.path.join(self.upload_dir, 'records')
        os.makedirs(record_dir, exist_ok=True)
        
        file_path = os.path.join(record_dir, f"{document['document_id']}.json")
        
        with open(file_path, 'w') as f:
            json.dump(document, f, indent=2)
    
    def _get_document_record(self, document_id):
        """Get a document record by ID"""
        record_dir = os.path.join(self.upload_dir, 'records')
        file_path = os.path.join(record_dir, f"{document_id}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return None
        
    def _create_sample_extraction(self, document_id, filename):
        """Create a sample extraction for testing"""
        extraction_file = os.path.join(self.extraction_dir, f"{document_id}_extraction.json")
        
        extraction_content = {
            "document_id": document_id,
            "filename": filename,
            "page_count": 5,
            "content": f"This is sample document content for testing with ID {document_id}. It contains financial information about several securities including Apple Inc. with ISIN US0378331005, Microsoft with ISIN US5949181045, and Amazon with ISIN US0231351067. The portfolio value is $1,500,000 as of March 15, 2025."
        }
        
        with open(extraction_file, 'w') as f:
            json.dump(extraction_content, f, indent=2)
            
        logger.info(f"Created sample extraction at {extraction_file}")
