from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from config.configuration import MONGO_URI, MONGO_USERNAME, MONGO_PASSWORD

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations."""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern to ensure a single database connection."""
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        """Initialize the MongoDB connection."""
        try:
            # Connect to MongoDB
            if MONGO_USERNAME and MONGO_PASSWORD:
                # Authentication required
                self._client = MongoClient(
                    MONGO_URI,
                    username=MONGO_USERNAME,
                    password=MONGO_PASSWORD
                )
            else:
                # No authentication
                self._client = MongoClient(MONGO_URI)
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get database name from URI
            db_name = MONGO_URI.split('/')[-1].split('?')[0]
            if not db_name:
                db_name = 'financial_documents'
                
            self._db = self._client[db_name]
            logger.info(f"Connected to MongoDB: {db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self._client = None
            self._db = None
            
        except Exception as e:
            logger.error(f"Unexpected error while connecting to MongoDB: {str(e)}")
            self._client = None
            self._db = None
    
    @property
    def db(self):
        """Get the database connection."""
        if self._db is None:
            self._initialize_connection()
        return self._db
    
    @property
    def client(self):
        """Get the MongoDB client."""
        if self._client is None:
            self._initialize_connection()
        return self._client
    
    def get_collection(self, collection_name):
        """Get a MongoDB collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection object
        """
        if self.db:
            return self.db[collection_name]
        return None
    
    def close_connection(self):
        """Close the MongoDB connection."""
        if self._client:
            self._client.close()
            logger.info("MongoDB connection closed")
            self._client = None
            self._db = None

# Create a singleton instance
db_service = DatabaseService()

# Helper functions
def get_db():
    """Get the database instance."""
    return db_service.db

def get_collection(collection_name):
    """Get a specific collection."""
    return db_service.get_collection(collection_name)

def save_document_results(document_id, processing_result):
    """Save document processing results to the database.
    
    Args:
        document_id: Unique document ID
        processing_result: Document processing results
        
    Returns:
        Result of the database operation
    """
    collection = get_collection('documents')
    if not collection:
        logger.error("Cannot save document: Database connection not available")
        return None
        
    # Ensure document has _id field
    processing_result['_id'] = document_id
    
    try:
        # Insert or replace document
        result = collection.replace_one(
            {'_id': document_id}, 
            processing_result, 
            upsert=True
        )
        return result
    except Exception as e:
        logger.error(f"Error saving document {document_id}: {str(e)}")
        return None

def get_document_by_id(document_id):
    """Get a document by ID.
    
    Args:
        document_id: Document ID
        
    Returns:
        Document data or None if not found
    """
    collection = get_collection('documents')
    if not collection:
        logger.error("Cannot get document: Database connection not available")
        return None
        
    try:
        return collection.find_one({'_id': document_id})
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        return None