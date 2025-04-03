import os
import logging
from datetime import datetime, timezone # Added timezone
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

# Setup logger
logger = logging.getLogger(__name__)

# --- DynamoDB Client Initialization ---

def get_dynamodb_resource():
    """
    Initializes and returns a boto3 DynamoDB resource.
    Reads AWS credentials and region from environment variables or AWS config.
    """
    try:
        # Boto3 will automatically look for credentials in environment variables,
        # shared credential file (~/.aws/credentials), or AWS config file (~/.aws/config).
        # Explicitly getting region from env var, falling back to a default if needed.
        region_name = os.environ.get('AWS_REGION', 'us-east-1') # Default to us-east-1 if not set
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        # Perform a simple operation to test credentials and connection
        dynamodb.meta.client.list_tables(Limit=1)
        logger.info(f"DynamoDB resource initialized successfully for region {region_name}.")
        return dynamodb
    except (NoCredentialsError, PartialCredentialsError):
        logger.error("AWS credentials not found. Configure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
        return None
    except ClientError as e:
        # More specific error handling for potential AWS issues
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == 'UnrecognizedClientException':
             logger.error(f"AWS Security Token Service Error: {e}. Check your AWS credentials and permissions.")
        elif error_code == 'InvalidSignatureException':
             logger.error(f"AWS Signature Error: {e}. Check your AWS Secret Access Key.")
        elif 'Region' in str(e):
             logger.error(f"AWS Region Error: {e}. Check the configured AWS_REGION ('{region_name}').")
        else:
             logger.error(f"Failed to initialize DynamoDB resource: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during DynamoDB initialization: {e}")
        return None

# --- Database Access Class ---

class Database:
    """
    Class for accessing AWS DynamoDB.
    Provides a unified interface for database operations.
    """
    def __init__(self):
        """
        Initialize DynamoDB access.
        """
        self.dynamodb = get_dynamodb_resource()
        if not self.dynamodb:
            logger.error("Database __init__: DynamoDB resource could not be initialized.")
            # Consider raising an exception or handling this state appropriately

    def _get_table(self, table_name: str):
        """Helper to get a DynamoDB table object."""
        if not self.dynamodb:
            logger.error(f"DynamoDB resource not available. Cannot access table '{table_name}'.")
            return None
        try:
            return self.dynamodb.Table(table_name)
        except Exception as e:
            logger.error(f"Error getting DynamoDB table '{table_name}': {e}")
            return None

    # --- Generic Document Methods (Adapt based on actual table structures) ---

    def store_document(self, table_name: str, document: Dict[str, Any], primary_key_name: str = 'id') -> Optional[str]:
        """
        Store an item (document) in the specified DynamoDB table.
        Assumes 'id' is the primary key if not specified.

        Args:
            table_name (str): The name of the DynamoDB table.
            document (Dict[str, Any]): The item to store. Must include the primary key.
            primary_key_name (str): The name of the primary key attribute. Defaults to 'id'.

        Returns:
            Optional[str]: The value of the primary key if successful, or None if failed.
        """
        table = self._get_table(table_name)
        if table is not None and primary_key_name in document:
            try:
                # Add a timestamp if not present
                if 'createdAt' not in document:
                    document['createdAt'] = datetime.now(timezone.utc).isoformat()
                document['updatedAt'] = datetime.now(timezone.utc).isoformat()

                response = table.put_item(Item=document)
                logger.info(f"Item inserted/updated in '{table_name}' with primary key: {document[primary_key_name]}. Response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                return document[primary_key_name]
            except ClientError as e:
                logger.error(f"Error storing item in '{table_name}': {e.response['Error']['Message']}")
                return None
            except Exception as e:
                 logger.error(f"Unexpected error storing item in '{table_name}': {e}")
                 return None
        else:
            if not table:
                 logger.error(f"Cannot store item, table '{table_name}' not accessible.")
            elif primary_key_name not in document:
                 logger.error(f"Cannot store item, primary key '{primary_key_name}' missing in document.")
            return None

    def find_document(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single item (document) in the specified DynamoDB table by its key.

        Args:
            table_name (str): The name of the DynamoDB table.
            key (Dict[str, Any]): The primary key of the item to find (e.g., {'id': 'some_value'}).

        Returns:
            Optional[Dict[str, Any]]: The found item, or None if not found or error occurred.
        """
        table = self._get_table(table_name)
        if table is not None:
            try:
                response = table.get_item(Key=key)
                item = response.get('Item')
                if item:
                    logger.debug(f"Item found in '{table_name}' with key: {key}")
                else:
                    logger.debug(f"No item found in '{table_name}' with key: {key}")
                return item
            except ClientError as e:
                logger.error(f"Error finding item in '{table_name}' with key {key}: {e.response['Error']['Message']}")
                return None
            except Exception as e:
                 logger.error(f"Unexpected error finding item in '{table_name}': {e}")
                 return None
        else:
            logger.error(f"Cannot find item, table '{table_name}' not accessible.")
            return None

    def update_document(self, table_name: str, key: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        Update an item in the specified DynamoDB table.

        Args:
            table_name (str): The name of the table.
            key (Dict[str, Any]): The primary key of the item to update.
            update_data (Dict[str, Any]): Dictionary of attributes to update.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        table = self._get_table(table_name)
        if table is not None:
            # Add updatedAt timestamp
            update_data['updatedAt'] = datetime.now(timezone.utc).isoformat()

            # Construct UpdateExpression, ExpressionAttributeNames, and ExpressionAttributeValues
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            for i, (attr_name, attr_value) in enumerate(update_data.items()):
                # Use placeholders for attribute names and values to avoid reserved words issues
                name_placeholder = f"#attr{i}"
                value_placeholder = f":val{i}"
                update_expression_parts.append(f"{name_placeholder} = {value_placeholder}")
                expression_attribute_names[name_placeholder] = attr_name
                expression_attribute_values[value_placeholder] = attr_value

            update_expression = "SET " + ", ".join(update_expression_parts)

            try:
                response = table.update_item(
                    Key=key,
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ReturnValues="UPDATED_NEW" # Or "NONE" if you don't need the result
                )
                logger.info(f"Item updated in '{table_name}' with key {key}. Response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                return True
            except ClientError as e:
                logger.error(f"Error updating item in '{table_name}' with key {key}: {e.response['Error']['Message']}")
                return False
            except Exception as e:
                 logger.error(f"Unexpected error updating item in '{table_name}': {e}")
                 return False
        else:
            logger.error(f"Cannot update item, table '{table_name}' not accessible.")
            return False

    def delete_document(self, table_name: str, key: Dict[str, Any]) -> bool:
        """
        Delete a single item from the specified DynamoDB table.

        Args:
            table_name (str): The name of the table.
            key (Dict[str, Any]): The primary key of the item to delete.

        Returns:
            bool: True if the item was deleted successfully, False otherwise.
        """
        table = self._get_table(table_name)
        if table is not None:
            try:
                response = table.delete_item(Key=key)
                logger.info(f"Item deleted from '{table_name}' with key {key}. Response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                # Note: delete_item succeeds even if the item doesn't exist.
                # Check response metadata or use ConditionExpression if needed.
                return True
            except ClientError as e:
                logger.error(f"Error deleting item from '{table_name}' with key {key}: {e.response['Error']['Message']}")
                return False
            except Exception as e:
                 logger.error(f"Unexpected error deleting item in '{table_name}': {e}")
                 return False
        else:
            logger.error(f"Cannot delete item, table '{table_name}' not accessible.")
            return False

    # --- Chat History Methods (Assuming a 'chat_history' table) ---
    # Assumes 'chat_history' table has:
    # - Primary Key: session_id (Partition Key), timestamp (Sort Key)
    # - Attributes: role, content

    def save_chat_message(self, session_id: str, role: str, content: str) -> Optional[str]:
        """
        Save a chat message to the chat history table.

        Args:
            session_id (str): The unique identifier for the chat session (Partition Key).
            role (str): The role of the message sender ('user' or 'assistant').
            content (str): The text content of the message.

        Returns:
            Optional[str]: The timestamp (Sort Key) of the saved message, or None if saving failed.
        """
        chat_table_name = "chat_history"
        table = self._get_table(chat_table_name)
        if table is not None:
            try:
                timestamp = datetime.now(timezone.utc).isoformat()
                message = {
                    "session_id": session_id,
                    "timestamp": timestamp, # Use timestamp as sort key
                    "role": role,
                    "content": content,
                }
                response = table.put_item(Item=message)
                logger.info(f"Chat message saved for session {session_id} at {timestamp}. Response: {response.get('ResponseMetadata', {}).get('HTTPStatusCode')}")
                return timestamp # Return sort key
            except ClientError as e:
                logger.error(f"Error saving chat message for session {session_id}: {e.response['Error']['Message']}")
                return None
            except Exception as e:
                 logger.error(f"Unexpected error saving chat message in '{chat_table_name}': {e}")
                 return None
        else:
            logger.error(f"Cannot save chat message, table '{chat_table_name}' not accessible.")
            return None

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a specific session, ordered by timestamp.

        Args:
            session_id (str): The unique identifier for the chat session (Partition Key).
            limit (int): The maximum number of messages to retrieve (most recent). Defaults to 50.

        Returns:
            List[Dict[str, Any]]: A list of chat messages, ordered by timestamp ascending.
        """
        chat_table_name = "chat_history"
        table = self._get_table(chat_table_name)
        messages = []
        if table is not None:
            try:
                # Query for messages for the session, sort by timestamp descending (ScanIndexForward=False)
                response = table.query(
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('session_id').eq(session_id),
                    ScanIndexForward=False, # Get most recent first
                    Limit=limit
                )
                # Items are returned newest first, reverse to get oldest first
                messages = response.get('Items', [])[::-1]
                logger.info(f"Retrieved {len(messages)} chat messages for session {session_id}.")
            except ClientError as e:
                logger.error(f"Error retrieving chat history for session {session_id}: {e.response['Error']['Message']}")
            except Exception as e:
                 logger.error(f"Unexpected error retrieving chat history from '{chat_table_name}': {e}")
        else:
            logger.error(f"Cannot retrieve chat history, table '{chat_table_name}' not accessible.")
        return messages

# Create a default database instance (singleton pattern)
# This instance will be used throughout the application by importing 'db' from this module.
db = Database()
