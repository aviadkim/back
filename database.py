from datetime import datetime
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

logger = logging.getLogger("database")

client = None
db = None

def connect_db():
    """Establishes a connection to the MongoDB database."""
    global client, db
    if client is None:
        mongodb_uri = Config.MONGODB_URI
        if not mongodb_uri:
            logger.error("MONGODB_URI not set in configuration. Cannot connect to database.")
            raise ValueError("MONGODB_URI is not configured.")

        try:
            logger.info(f"Attempting to connect to MongoDB at {mongodb_uri.split('@')[-1]}")
            client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            client.admin.command('ismaster')
            db = client.get_database()
            logger.info("Successfully connected to MongoDB.")
        except ConnectionFailure as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            client = None
            db = None
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during MongoDB connection: {e}")
            client = None
            db = None
            raise

def get_db():
    """Returns the database instance, connecting if necessary."""
    if db is None:
        connect_db()
    return db

def add_document_record(document_id, filename, user_id=None, language=None):
    """Adds a new document record to the database."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot add document record.")
        return None

    doc_collection = database.documents
    now = datetime.utcnow()
    record = {
        "_id": document_id,
        "filename": filename,
        "user_id": user_id,
        "language": language,
        "status": "queued",
        "upload_time": now,
        "last_update_time": now,
        "task_id": None,
        "file_path": None,
        "ocr_path": None,
        "financial_path": None,
        "tables_path": None,
        "error_message": None
    }
    try:
        result = doc_collection.insert_one(record)
        logger.info(f"Inserted document record for {document_id} with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Failed to insert document record for {document_id}: {e}")
        return None

def update_document_status(document_id, status, task_id=None, file_path=None, 
                         ocr_path=None, financial_path=None, tables_path=None, 
                         error_message=None):
    """Updates the status and associated data paths of a document record."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot update document status.")
        return False

    doc_collection = database.documents
    now = datetime.utcnow()
    update_fields = {
        "status": status,
        "last_update_time": now
    }
    if task_id: update_fields["task_id"] = task_id
    if file_path: update_fields["file_path"] = file_path
    if ocr_path: update_fields["ocr_path"] = ocr_path
    if financial_path: update_fields["financial_path"] = financial_path
    if tables_path: update_fields["tables_path"] = tables_path
    if error_message: update_fields["error_message"] = error_message
    elif status != 'failed': 
        update_fields["error_message"] = None

    try:
        result = doc_collection.update_one({"_id": document_id}, {"$set": update_fields})
        if result.matched_count == 0:
            logger.warning(f"Attempted to update status for non-existent document_id: {document_id}")
            return False
        logger.info(f"Updated status for document {document_id} to {status}. Modified count: {result.modified_count}")
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Failed to update status for document {document_id}: {e}")
        return False

def get_document_by_id(document_id):
    """Retrieves a document record by its ID."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot get document.")
        return None
    doc_collection = database.documents
    try:
        return doc_collection.find_one({"_id": document_id})
    except Exception as e:
        logger.error(f"Failed to retrieve document {document_id}: {e}")
        return None

def list_all_documents(user_id=None, limit=100):
    """Lists documents, optionally filtered by user_id."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot list documents.")
        return []
    
    doc_collection = database.documents
    query = {}
    if user_id:
        query["user_id"] = user_id

    try:
        return list(doc_collection.find(query).sort("upload_time", -1).limit(limit))
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        return []

# Financial Data Functions
# =======================

def add_financial_instruments(document_id: str, tenant_id: str, instruments_data: list):
    """Adds multiple financial instrument records for a specific document and tenant."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot add financial instruments.")
        return False
    
    inst_collection = database.financial_instruments
    now = datetime.utcnow()
    
    records_to_insert = []
    for instrument in instruments_data:
        # Ensure essential fields are present, adapt as needed based on actual extraction output
        record = {
            "document_id": document_id,
            "tenant_id": tenant_id, # Assuming user_id is the tenant_id
            "isin": instrument.get("isin"),
            "name": instrument.get("name"),
            "type": instrument.get("type"),
            "value": instrument.get("value"),
            "currency": instrument.get("currency"),
            "percentage_in_portfolio": instrument.get("percentage_in_portfolio"),
            "extracted_at": now,
            # Add other fields from instrument dict if necessary
            **{k: v for k, v in instrument.items() if k not in ['isin', 'name', 'type', 'value', 'currency', 'percentage_in_portfolio']}
        }
        records_to_insert.append(record)

    if not records_to_insert:
        logger.info(f"No valid instrument data provided for document {document_id}.")
        return True # Nothing to insert, but not an error

    try:
        result = inst_collection.insert_many(records_to_insert)
        logger.info(f"Inserted {len(result.inserted_ids)} financial instruments for document {document_id}, tenant {tenant_id}.")
        return True
    except Exception as e:
        logger.error(f"Failed to insert financial instruments for document {document_id}: {e}")
        return False

def get_financial_instruments(document_id: str, tenant_id: str):
    """Retrieves all financial instruments for a specific document and tenant."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot get financial instruments.")
        return []
    
    inst_collection = database.financial_instruments
    query = {"document_id": document_id, "tenant_id": tenant_id}
    
    try:
        return list(inst_collection.find(query))
    except Exception as e:
        logger.error(f"Failed to retrieve financial instruments for document {document_id}: {e}")
        return []

def add_document_summary(document_id: str, tenant_id: str, summary_data: dict):
    """Adds or updates the financial summary for a specific document and tenant."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot add document summary.")
        return False
        
    summary_collection = database.document_summaries
    now = datetime.utcnow()
    
    record = {
        "document_id": document_id,
        "tenant_id": tenant_id,
        "generated_at": now,
        **summary_data # Merge the provided summary data
    }
    
    try:
        # Use update_one with upsert=True to insert if not exists, or update if exists
        result = summary_collection.update_one(
            {"document_id": document_id, "tenant_id": tenant_id},
            {"$set": record, "$setOnInsert": {"created_at": now}}, # Set created_at only on insert
            upsert=True
        )
        if result.upserted_id:
            logger.info(f"Inserted document summary for {document_id}, tenant {tenant_id}.")
        elif result.modified_count > 0:
            logger.info(f"Updated document summary for {document_id}, tenant {tenant_id}.")
        else:
             logger.info(f"Document summary for {document_id}, tenant {tenant_id} already up-to-date.")
        return True
    except Exception as e:
        logger.error(f"Failed to add/update document summary for {document_id}: {e}")
        return False

def get_document_summary(document_id: str, tenant_id: str):
    """Retrieves the financial summary for a specific document and tenant."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot get document summary.")
        return None
        
    summary_collection = database.document_summaries
    query = {"document_id": document_id, "tenant_id": tenant_id}
    
    try:
        return summary_collection.find_one(query)
    except Exception as e:
        logger.error(f"Failed to retrieve document summary for {document_id}: {e}")
        return None

def query_instruments(tenant_id: str, query_criteria: dict, limit: int = 100):
    """Queries financial instruments for a tenant based on criteria."""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot query instruments.")
        return []
        
    inst_collection = database.financial_instruments
    # Ensure tenant_id is always part of the query for security/isolation
    full_query = {"tenant_id": tenant_id, **query_criteria}
    
    try:
        # Example: find all bonds for the tenant
        # query_instruments(tenant_id, {"type": "bond"})
        # Example: find instruments with value > 1000000
        # query_instruments(tenant_id, {"value": {"$gt": 1000000}})
        logger.info(f"Executing instrument query for tenant {tenant_id}: {full_query}")
        return list(inst_collection.find(full_query).limit(limit))
    except Exception as e:
        logger.error(f"Failed to query instruments for tenant {tenant_id}: {e}")
        return []

# =======================

def close_db_connection():
    """Closes the database connection."""
    global client
    if client:
        client.close()
        client = None
        db = None
        logger.info("MongoDB connection closed.")

# User Management Functions
def add_user(email: str, password_hash: str) -> str:
    """Add a new user to the database"""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot add user.")
        return None

    try:
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        result = database.users.insert_one(user_data)
        logger.info(f"Added user {email} with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error adding user: {str(e)}")
        return None

def get_user_by_email(email: str) -> dict:
    """Get user by email"""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot get user.")
        return None

    try:
        return database.users.find_one({"email": email})
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}")
        return None

def update_user_password(user_id: str, new_password_hash: str) -> bool:
    """Update user password"""
    database = get_db()
    if database is None:
        logger.error("Database connection not available. Cannot update password.")
        return False

    try:
        result = database.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "password_hash": new_password_hash,
                "updated_at": datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating user password: {str(e)}")
        return False