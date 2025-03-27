import os
import logging
from datetime import datetime # Added for timestamping
from typing import Dict, Any, Optional
from typing import Dict, Any, Optional, List # Added List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Setup logger
logger = logging.getLogger(__name__)

# SQLAlchemy Base class for models
Base = declarative_base()

# MongoDB connection
def get_mongo_client() -> Optional[MongoClient]:
    """
    Create a connection to MongoDB.
    
    Returns:
        MongoClient: MongoDB client, or None if there was an error.
    """
    # Corrected environment variable name to MONGODB_URI
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/financial_documents')
    
    try:
        client = MongoClient(mongo_uri)
        # Check the connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful")
        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

def get_mongo_db(db_name: Optional[str] = None):
    """
    Get the DB object from MongoDB.
    
    Args:
        db_name (Optional[str]): The name of the database (optional).
        
    Returns:
        Database: MongoDB database object or None.
    """
    client = get_mongo_client()
    if not client:
        return None
    
    # If no database name is provided, use the default from the URI or a fallback
    if not db_name:
        # Extract the database name from the URI
        # Corrected environment variable name to MONGODB_URI
        mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/financial_documents')
        db_name = mongo_uri.split('/')[-1]
        # Handle cases where the name might have query parameters or be empty
        if not db_name or '?' in db_name:
            db_name = 'financial_documents' # Default database name
    
    return client[db_name]

# SQLAlchemy engine and session
def init_sqlalchemy_db(app=None):
    """
    Initialize SQLAlchemy, optionally with a Flask app.
    
    Args:
        app: Flask application instance (optional).
        
    Returns:
        tuple: (engine, Session) - SQLAlchemy engine and scoped session factory.
    """
    # Determine the database URI
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///financial_documents.db')
    
    # Create SQLAlchemy engine
    engine = create_engine(db_uri, echo=False)
    
    # Create a scoped session factory
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    
    # If a Flask app is provided, configure session removal on teardown
    if app:
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            Session.remove()
    
    # Create all tables defined by Base's subclasses
    Base.metadata.create_all(engine)
    
    return engine, Session

# Database access class
class Database:
    """
    Class for accessing the database (MongoDB or SQLAlchemy).
    Provides a unified interface for database operations.
    """
    def __init__(self, use_mongo: bool = True):
        """
        Initialize database access.
        
        Args:
            use_mongo (bool): Whether to use MongoDB (True) or SQLAlchemy (False). Defaults to True.
        """
        self.use_mongo = use_mongo
        
        if use_mongo:
            self.client = get_mongo_client()
            if self.client:
                self.db = get_mongo_db() # Get the database object
            else:
                self.db = None # MongoDB connection failed
                logger.error("Database __init__: MongoDB client could not be initialized.")
        else:
            # Initialize SQLAlchemy if not using Mongo
            self.engine, self.Session = init_sqlalchemy_db()
            logger.info("Database __init__: SQLAlchemy initialized.")
    
    def get_collection(self, collection_name: str):
        """
        Get a MongoDB collection object.
        
        Args:
            collection_name (str): The name of the collection.
            
        Returns:
            Collection or None: The MongoDB collection object, or None if not using MongoDB or connection failed.
        """
        if not self.use_mongo or not self.db:
            logger.warning(f"Attempted to get MongoDB collection '{collection_name}' but not using Mongo or DB connection failed.")
            return None
        
        return self.db[collection_name]
    
    def get_session(self):
        """
        Get a SQLAlchemy session.
        
        Returns:
            Session or None: A new SQLAlchemy session, or None if using MongoDB.
        """
        if self.use_mongo:
            logger.warning("Attempted to get SQLAlchemy session while configured for MongoDB.")
            return None
        
        # Return a new session from the scoped session factory
        return self.Session()
    
    def store_document(self, collection_name: str, document: Dict[str, Any]) -> Optional[str]:
        """
        Store a document in the specified MongoDB collection.
        
        Args:
            collection_name (str): The name of the collection.
            document (Dict[str, Any]): The document to store.
            
        Returns:
            Optional[str]: The string representation of the inserted document's ID, or None if failed.
        """
        coll = self.get_collection(collection_name)
        if coll is not None:
            try:
                result = coll.insert_one(document)
                logger.info(f"Document inserted into '{collection_name}' with ID: {result.inserted_id}")
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"Error storing document in '{collection_name}': {e}")
                return None
        else:
            logger.error(f"Cannot store document, collection '{collection_name}' not accessible.")
            return None
    
    def find_document(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in the specified MongoDB collection.
        
        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query criteria.
            
        Returns:
            Optional[Dict[str, Any]]: The found document, or None if not found or error occurred.
        """
        coll = self.get_collection(collection_name)
        if coll is not None:
            try:
                document = coll.find_one(query)
                if document:
                    logger.debug(f"Document found in '{collection_name}' matching query: {query}")
                else:
                    logger.debug(f"No document found in '{collection_name}' matching query: {query}")
                return document
            except Exception as e:
                logger.error(f"Error finding document in '{collection_name}': {e}")
                return None
        else:
            logger.error(f"Cannot find document, collection '{collection_name}' not accessible.")
            return None
    
    def update_document(self, collection_name: str, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        Update a single document in the specified MongoDB collection.
        Uses $set operator for the update.
        
        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query criteria to find the document.
            update_data (Dict[str, Any]): The fields and values to update.
            
        Returns:
            bool: True if a document was modified, False otherwise.
        """
        coll = self.get_collection(collection_name)
        if coll is not None:
            try:
                result = coll.update_one(query, {"$set": update_data})
                if result.modified_count > 0:
                    logger.info(f"Document updated in '{collection_name}' matching query: {query}")
                    return True
                else:
                    # Log if no document matched or if the data was already the same
                    logger.info(f"No document updated in '{collection_name}' matching query: {query} (may not exist or already up-to-date)")
                    return False # Return False if no document was modified
            except Exception as e:
                logger.error(f"Error updating document in '{collection_name}': {e}")
                return False
        else:
            logger.error(f"Cannot update document, collection '{collection_name}' not accessible.")
            return False
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from the specified MongoDB collection.
        
        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query criteria to find the document to delete.
            
        Returns:
            bool: True if a document was deleted, False otherwise.
        """
        coll = self.get_collection(collection_name)
        if coll is not None:
            try:
                result = coll.delete_one(query)
                if result.deleted_count > 0:
                    logger.info(f"Document deleted from '{collection_name}' matching query: {query}")
                    return True
                else:
                    logger.info(f"No document deleted from '{collection_name}' matching query: {query} (document not found)")
                    return False # Return False if no document was deleted
            except Exception as e:
                logger.error(f"Error deleting document from '{collection_name}': {e}")
                return False
        else:
            logger.error(f"Cannot delete document, collection '{collection_name}' not accessible.")
            return False


    # --- Chat History Methods ---

    def save_chat_message(self, session_id: str, role: str, content: str) -> Optional[str]:
        """
        Save a chat message to the chat history collection.

        Args:
            session_id (str): The unique identifier for the chat session.
            role (str): The role of the message sender ('user' or 'assistant').
            content (str): The text content of the message.

        Returns:
            Optional[str]: The ID of the saved message, or None if saving failed.
        """
        chat_collection_name = "chat_history"
        coll = self.get_collection(chat_collection_name)
        if coll is not None:
            try:
                message = {
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "timestamp": datetime.utcnow() # Store timestamp
                }
                result = coll.insert_one(message)
                logger.info(f"Chat message saved for session {session_id} with ID: {result.inserted_id}")
                return str(result.inserted_id)
            except Exception as e:
                logger.error(f"Error saving chat message for session {session_id}: {e}")
                return None
        else:
            logger.error(f"Cannot save chat message, collection '{chat_collection_name}' not accessible.")
            return None

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve chat history for a specific session, ordered by timestamp.

        Args:
            session_id (str): The unique identifier for the chat session.
            limit (int): The maximum number of messages to retrieve (most recent). Defaults to 50.

        Returns:
            List[Dict[str, Any]]: A list of chat messages, ordered by timestamp ascending.
        """
        chat_collection_name = "chat_history"
        coll = self.get_collection(chat_collection_name)
        messages = []
        if coll is not None:
            try:
                # Find messages for the session, sort by timestamp descending, limit results
                cursor = coll.find({"session_id": session_id}).sort("timestamp", -1).limit(limit)
                # Convert cursor to list and reverse to get ascending order (oldest first)
                messages = list(cursor)[::-1]
                logger.info(f"Retrieved {len(messages)} chat messages for session {session_id}.")
            except Exception as e:
                logger.error(f"Error retrieving chat history for session {session_id}: {e}")
        else:
            logger.error(f"Cannot retrieve chat history, collection '{chat_collection_name}' not accessible.")
        return messages

# Create a default database instance (singleton pattern)
# This instance will be used throughout the application by importing 'db' from this module.
# It defaults to using MongoDB based on the Database class default.
db = Database()
