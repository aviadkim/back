import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import ClientError
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config.aws_config import (
    DYNAMODB_DOCUMENTS_TABLE,
    DYNAMODB_PROCESSED_DATA_TABLE,
    DYNAMODB_CUSTOM_TABLES_TABLE,
    DYNAMODB_REGION
)

class DynamoDBService:
    """שירות לאחסון נתונים מובנים ב-DynamoDB"""

    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=DYNAMODB_REGION
        )

        self.documents_table = self.dynamodb.Table(DYNAMODB_DOCUMENTS_TABLE)
        self.processed_data_table = self.dynamodb.Table(DYNAMODB_PROCESSED_DATA_TABLE)
        self.custom_tables_table = self.dynamodb.Table(DYNAMODB_CUSTOM_TABLES_TABLE)
        self.logger = logging.getLogger(__name__)

    def save_document_metadata(self, metadata):
        """שמירת מטא-נתונים של מסמך"""
        try:
            if 'upload_date' not in metadata:
                metadata['upload_date'] = datetime.now().isoformat()

            self.documents_table.put_item(Item=metadata)
            return True
        except Exception as e:
            self.logger.error(f"Error saving to DynamoDB: {str(e)}")
            raise

    def get_document(self, document_id):
        """קבלת פרטי מסמך"""
        try:
            response = self.documents_table.get_item(Key={'id': document_id})
            return response.get('Item')
        except Exception as e:
            self.logger.error(f"Error getting document: {str(e)}")
            raise

    def get_documents(self):
        """קבלת רשימת מסמכים"""
        try:
            response = self.documents_table.scan()
            return response.get('Items', [])
        except Exception as e:
            self.logger.error(f"Error getting documents: {str(e)}")
            raise

    def save_processed_data(self, document_id, data):
        """שמירת נתונים מעובדים"""
        try:
            item = {
                'document_id': document_id,
                'processed_at': datetime.now().isoformat(),
                'data': data
            }
            self.processed_data_table.put_item(Item=item)
            return True
        except Exception as e:
            self.logger.error(f"Error saving processed data: {str(e)}")
            raise

    def get_processed_data(self, document_id):
        """קבלת נתונים מעובדים"""
        try:
            response = self.processed_data_table.get_item(Key={'document_id': document_id})
            return response.get('Item', {}).get('data', {})
        except Exception as e:
            self.logger.error(f"Error getting processed data: {str(e)}")
            raise

    def update_document_status(self, document_id, status, error_message=None):
        """עדכון סטטוס מסמך"""
        try:
            update_expression = "set #status = :status, updated_at = :updated_at"
            expression_values = {
                ':status': status,
                ':updated_at': datetime.now().isoformat()
            }

            if error_message and status == 'error':
                update_expression += ", error_message = :error_message"
                expression_values[':error_message'] = error_message

            self.documents_table.update_item(
                Key={'id': document_id},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ExpressionAttributeNames={'#status': 'status'}
            )
            return True
        except Exception as e:
            self.logger.error(f"Error updating status: {str(e)}")
            raise