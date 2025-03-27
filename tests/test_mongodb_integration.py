import pytest
from pymongo import MongoClient
from datetime import datetime
import os

@pytest.fixture
def mongo_client():
    """Setup test MongoDB client with proper connection string."""
    connection_string = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(connection_string, serverSelectionTimeoutMS=2000)
    try:
        # Test connection
        client.admin.command('ping')
        db = client['test_db']
        yield db
    except Exception as e:
        pytest.skip(f"MongoDB not available: {str(e)}")
    finally:
        # Cleanup
        if 'client' in locals():
            client.drop_database('test_db')
            client.close()

def test_mongodb_connection(mongo_client):
    """Test MongoDB connection and basic operations."""
    collection = mongo_client['documents']
    
    # Insert test document
    doc_id = collection.insert_one({
        'filename': 'test.pdf',
        'upload_date': datetime.utcnow()
    }).inserted_id
    
    # Verify insertion
    doc = collection.find_one({'_id': doc_id})
    assert doc is not None
    assert doc['filename'] == 'test.pdf'
