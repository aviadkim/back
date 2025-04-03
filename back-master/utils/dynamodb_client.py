"""
DynamoDB utility for interacting with AWS DynamoDB tables.
This is a simpler alternative to MongoDB for our document storage and retrieval needs.
"""
import os
import json
import uuid
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class DynamoDBClient:
    """A client for interacting with AWS DynamoDB tables."""
    
    def __init__(self):
        """Initialize the DynamoDB client."""
        self.use_dynamodb = os.environ.get('USE_DYNAMODB', 'False').lower() == 'true'
        self.region = os.environ.get('DYNAMODB_REGION', 'eu-central-1')
        
        # Table names
        self.documents_table = 'financial_documents'
        self.analysis_table = 'document_analysis'
        self.chat_table = 'chat_history'
        
        if self.use_dynamodb:
            self._init_dynamodb_client()
            logger.info("Using AWS DynamoDB for document storage")
        else:
            logger.info("DynamoDB disabled. Using local storage instead.")
    
    def _init_dynamodb_client(self):
        """Initialize the boto3 DynamoDB client."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Create the DynamoDB client
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region)
            self.documents = self.dynamodb.Table(self.documents_table)
            self.analysis = self.dynamodb.Table(self.analysis_table)
            self.chat_history = self.dynamodb.Table(self.chat_table)
            
            # Test connection
            try:
                self.documents.table_status
                logger.info(f"Successfully connected to DynamoDB table: {self.documents_table}")
            except ClientError as e:
                logger.error(f"Failed to connect to DynamoDB: {e}")
                self.use_dynamodb = False
                
        except ImportError:
            logger.warning("boto3 not installed. DynamoDB functionality disabled.")
            self.use_dynamodb = False
        except Exception as e:
            logger.error(f"Error initializing DynamoDB client: {e}")
            self.use_dynamodb = False
    
    def store_document_metadata(self, document_data):
        """
        Store document metadata in DynamoDB.
        
        Args:
            document_data: Dictionary containing document metadata
            
        Returns:
            Dictionary with operation result
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            # Make sure we have a document_id
            if 'document_id' not in document_data:
                document_data['document_id'] = str(uuid.uuid4())
            
            # Add timestamp if not present
            if 'created_at' not in document_data:
                document_data['created_at'] = datetime.now().isoformat()
            
            # Store in DynamoDB
            response = self.documents.put_item(Item=document_data)
            
            return {
                'success': True,
                'document_id': document_data['document_id'],
                'message': 'Document metadata stored successfully'
            }
        
        except Exception as e:
            logger.error(f"Error storing document metadata: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_document_metadata(self, document_id):
        """
        Retrieve document metadata from DynamoDB.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Dictionary with document metadata or error
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            response = self.documents.get_item(Key={'document_id': document_id})
            
            if 'Item' in response:
                return {'success': True, 'document': response['Item']}
            else:
                return {'success': False, 'error': 'Document not found'}
        
        except Exception as e:
            logger.error(f"Error retrieving document metadata: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_documents(self, limit=100):
        """
        List all documents in the documents table.
        
        Args:
            limit: Maximum number of documents to return
            
        Returns:
            List of document metadata dictionaries
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            response = self.documents.scan(Limit=limit)
            
            if 'Items' in response:
                return {'success': True, 'documents': response['Items']}
            else:
                return {'success': True, 'documents': []}
        
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_document(self, document_id):
        """
        Delete a document from the documents table.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            Dictionary with operation result
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            response = self.documents.delete_item(Key={'document_id': document_id})
            
            return {
                'success': True,
                'message': 'Document deleted successfully'
            }
        
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return {'success': False, 'error': str(e)}
    
    def store_analysis_result(self, document_id, analysis_data):
        """
        Store document analysis results in DynamoDB.
        
        Args:
            document_id: ID of the document
            analysis_data: Dictionary containing analysis results
            
        Returns:
            Dictionary with operation result
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            # Add document_id if not present
            if 'document_id' not in analysis_data:
                analysis_data['document_id'] = document_id
            
            # Add timestamp if not present
            if 'created_at' not in analysis_data:
                analysis_data['created_at'] = datetime.now().isoformat()
            
            # Store in DynamoDB
            response = self.analysis.put_item(Item=analysis_data)
            
            return {
                'success': True,
                'document_id': document_id,
                'message': 'Analysis results stored successfully'
            }
        
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_analysis_result(self, document_id):
        """
        Retrieve analysis results for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Dictionary with analysis results or error
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            response = self.analysis.get_item(Key={'document_id': document_id})
            
            if 'Item' in response:
                return {'success': True, 'analysis': response['Item']}
            else:
                return {'success': False, 'error': 'Analysis not found'}
        
        except Exception as e:
            logger.error(f"Error retrieving analysis results: {e}")
            return {'success': False, 'error': str(e)}
    
    def store_chat_message(self, chat_id, message_data):
        """
        Store a chat message in the chat history table.
        
        Args:
            chat_id: ID of the chat session
            message_data: Dictionary containing the message data
            
        Returns:
            Dictionary with operation result
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            # Generate a unique message ID
            message_id = str(uuid.uuid4())
            
            # Create the item to store
            item = {
                'chat_id': chat_id,
                'message_id': message_id,
                'timestamp': datetime.now().isoformat(),
                **message_data
            }
            
            # Store in DynamoDB
            response = self.chat_history.put_item(Item=item)
            
            return {
                'success': True,
                'chat_id': chat_id,
                'message_id': message_id,
                'message': 'Chat message stored successfully'
            }
        
        except Exception as e:
            logger.error(f"Error storing chat message: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_chat_history(self, chat_id):
        """
        Retrieve chat history for a chat session.
        
        Args:
            chat_id: ID of the chat session
            
        Returns:
            Dictionary with chat history or error
        """
        if not self.use_dynamodb:
            logger.warning("DynamoDB disabled. Using local storage.")
            return {'success': False, 'error': 'DynamoDB disabled'}
        
        try:
            # We need to use a query because we're looking for specific chat_id
            # This assumes we've set up a global secondary index on chat_id
            # For simplicity, we'll scan the table instead
            response = self.chat_history.scan(
                FilterExpression='chat_id = :chat_id',
                ExpressionAttributeValues={':chat_id': chat_id}
            )
            
            if 'Items' in response:
                # Sort by timestamp
                messages = sorted(response['Items'], key=lambda x: x.get('timestamp', ''))
                return {'success': True, 'messages': messages}
            else:
                return {'success': True, 'messages': []}
        
        except Exception as e:
            logger.error(f"Error retrieving chat history: {e}")
            return {'success': False, 'error': str(e)}
    
    # Local storage fallback methods
    def _local_save(self, data, filename):
        """Save data to a local JSON file."""
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Error saving to local file {filepath}: {e}")
            return False
    
    def _local_load(self, filename):
        """Load data from a local JSON file."""
        filepath = os.path.join('data', filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading from local file {filepath}: {e}")
            return None

# Create a singleton instance
db = DynamoDBClient()
