import os

def create_mongodb_setup():
    """Create MongoDB setup and integration files"""
    
    # Create mongodb directory
    os.makedirs('mongodb', exist_ok=True)
    
    # Create connection file
    with open('mongodb/connection.py', 'w') as f:
        f.write("""
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
def get_mongo_client():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
    return MongoClient(mongo_uri)

# Get database and collections
def get_db_collections():
    client = get_mongo_client()
    db = client.get_database()
    
    collections = {
        'documents': db.documents,
        'users': db.users,
        'financial_data': db.financial_data,
        'extractions': db.extractions,
        'analytics': db.analytics
    }
    
    return db, collections
""")
    
    # Create schemas file
    with open('mongodb/schemas.py', 'w') as f:
        f.write("""
from datetime import datetime

# Document schema
document_schema = {
    'document_id': str,        # Unique identifier
    'filename': str,           # Original filename
    'upload_date': datetime,   # When the document was uploaded
    'status': str,             # 'processing', 'completed', 'error'
    'language': str,           # Document language
    'user_id': str,            # Owner of the document
    'file_path': str,          # Path to the file
    'extraction_path': str,    # Path to extracted data
    'page_count': int,         # Number of pages
    'content': str,            # Extracted text content
    'metadata': dict           # Additional metadata
}

# User schema
user_schema = {
    'username': str,           # Username (unique)
    'email': str,              # Email address (unique)
    'password_hash': str,      # Hashed password
    'created_at': datetime,    # Account creation date
    'last_login': datetime,    # Last login date
    'role': str,               # 'admin', 'user', etc.
    'organization': str,       # Organization name
    'settings': dict,          # User settings
    'api_key': str,            # API key for accessing the API
    'subscription': {          # Subscription information
        'plan': str,           # 'free', 'basic', 'pro', 'enterprise'
        'status': str,         # 'active', 'inactive', 'trial'
        'start_date': datetime,# Subscription start date
        'end_date': datetime,  # Subscription end date
        'features': list       # Enabled features
    }
}

# Financial data schema
financial_data_schema = {
    'document_id': str,        # Associated document ID
    'isins': list,             # List of ISINs found
    'securities': list,        # Detailed security information
    'tables': list,            # Extracted tables
    'currencies': list,        # Currency information
    'percentages': list,       # Percentage values
    'extracted_at': datetime,  # When the data was extracted
    'analyzed_at': datetime    # When the data was analyzed
}

# Analytics schema
analytics_schema = {
    'document_id': str,        # Associated document ID
    'user_id': str,            # User who performed the analysis
    'type': str,               # Type of analysis
    'parameters': dict,        # Analysis parameters
    'results': dict,           # Analysis results
    'created_at': datetime,    # When the analysis was created
    'updated_at': datetime     # When the analysis was last updated
}
""")
    
    # Create migration file
    with open('mongodb/migration.py', 'w') as f:
        f.write("""
import os
import json
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import MongoDB connection
from mongodb.connection import get_db_collections

def migrate_file_data_to_mongodb():
    """Migrate data from files to MongoDB"""
    logger.info("Starting migration of file data to MongoDB")
    
    # Get MongoDB collections
    db, collections = get_db_collections()
    documents_collection = collections['documents']
    financial_data_collection = collections['financial_data']
    
    # Get upload folder
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    extraction_folder = os.getenv('EXTRACTION_FOLDER', 'extractions')
    enhanced_folder = os.getenv('ENHANCED_FOLDER', 'enhanced_extractions')
    
    # Ensure folders exist
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(extraction_folder, exist_ok=True)
    os.makedirs(enhanced_folder, exist_ok=True)
    
    # Get all PDF files in the upload folder
    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith('.pdf')]
    
    migrated_count = 0
    
    for pdf_file in pdf_files:
        # Extract document_id from filename
        if '_' in pdf_file:
            document_id = pdf_file.split('_')[0]
        else:
            document_id = os.path.splitext(pdf_file)[0]
        
        # Check if document already exists in MongoDB
        if documents_collection.find_one({'document_id': document_id}):
            logger.info(f"Document {document_id} already exists in MongoDB, skipping")
            continue
        
        # Create document record
        document = {
            'document_id': document_id,
            'filename': pdf_file,
            'upload_date': datetime.now(),
            'status': 'completed',
            'language': 'unknown',
            'user_id': 'system',  # Default user during migration
            'file_path': os.path.join(upload_folder, pdf_file),
            'extraction_path': '',
            'page_count': 0,
            'content': '',
            'metadata': {}
        }
        
        # Look for extraction file
        extraction_path = os.path.join(extraction_folder, f"{document_id}_extraction.json")
        if os.path.exists(extraction_path):
            document['extraction_path'] = extraction_path
            try:
                with open(extraction_path, 'r') as f:
                    extraction_data = json.load(f)
                    document['content'] = extraction_data.get('content', '')
                    document['page_count'] = len(extraction_data.get('pages', []))
            except Exception as e:
                logger.error(f"Error reading extraction data for {document_id}: {e}")
        
        # Insert document into MongoDB
        result = documents_collection.insert_one(document)
        logger.info(f"Inserted document {document_id} into MongoDB with ID {result.inserted_id}")
        
        # Look for financial data
        financial_data_path = os.path.join(enhanced_folder, f"{document_id}_enhanced.json")
        if not os.path.exists(financial_data_path):
            financial_data_path = os.path.join(extraction_folder, f"{document_id}_financial.json")
        
        if os.path.exists(financial_data_path):
            try:
                with open(financial_data_path, 'r') as f:
                    financial_data = json.load(f)
                    financial_data['document_id'] = document_id
                    financial_data['extracted_at'] = datetime.now()
                    financial_data['analyzed_at'] = datetime.now()
                    
                    result = financial_data_collection.insert_one(financial_data)
                    logger.info(f"Inserted financial data for {document_id} into MongoDB with ID {result.inserted_id}")
            except Exception as e:
                logger.error(f"Error reading financial data for {document_id}: {e}")
        
        migrated_count += 1
    
    logger.info(f"Migration completed. Migrated {migrated_count} documents to MongoDB")
    return migrated_count

if __name__ == "__main__":
    migrate_file_data_to_mongodb()
""")
    
    # Create DB initialization file
    with open('mongodb/init_db.py', 'w') as f:
        f.write("""
from mongodb.connection import get_db_collections
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_mongodb():
    """Initialize MongoDB with indexes and default data"""
    logger.info("Initializing MongoDB")
    
    # Get MongoDB collections
    db, collections = get_db_collections()
    
    # Create indexes for documents collection
    logger.info("Creating indexes for documents collection")
    collections['documents'].create_index('document_id', unique=True)
    collections['documents'].create_index('user_id')
    collections['documents'].create_index('upload_date')
    
    # Create indexes for users collection
    logger.info("Creating indexes for users collection")
    collections['users'].create_index('username', unique=True)
    collections['users'].create_index('email', unique=True)
    collections['users'].create_index('api_key', unique=True, sparse=True)
    
    # Create indexes for financial_data collection
    logger.info("Creating indexes for financial_data collection")
    collections['financial_data'].create_index('document_id', unique=True)
    
    # Create indexes for analytics collection
    logger.info("Creating indexes for analytics collection")
    collections['analytics'].create_index([('document_id', 1), ('type', 1)])
    collections['analytics'].create_index('user_id')
    
    # Create default admin user if not exists
    logger.info("Creating default admin user if not exists")
    if collections['users'].count_documents({'username': 'admin'}) == 0:
        from werkzeug.security import generate_password_hash
        from datetime import datetime
        
        admin_user = {
            'username': 'admin',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('admin'),
            'created_at': datetime.now(),
            'last_login': None,
            'role': 'admin',
            'organization': 'System',
            'settings': {},
            'api_key': None
        }
        
        collections['users'].insert_one(admin_user)
        logger.info("Created default admin user")
    
    logger.info("MongoDB initialization completed")

if __name__ == "__main__":
    init_mongodb()
""")
    
    # Create .env file with MongoDB configuration
    with open('.env', 'a') as f:
        f.write("""
# MongoDB configuration
MONGO_URI=mongodb://localhost:27017/financial_documents

# Upload directories
UPLOAD_FOLDER=uploads
EXTRACTION_FOLDER=extractions
ENHANCED_FOLDER=enhanced_extractions

# Authentication
SECRET_KEY=your_secret_key_here
JWT_EXPIRATION_HOURS=24
""")
    
    print("MongoDB setup created successfully!")
    print("1. Create a .env file with your MongoDB connection string")
    print("2. Initialize the database with python -m mongodb.init_db")
    print("3. Migrate existing data with python -m mongodb.migration")

if __name__ == "__main__":
    create_mongodb_setup()
