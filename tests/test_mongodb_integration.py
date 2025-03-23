import pytest
from pymongo import MongoClient
from datetime import datetime

@pytest.fixture
def mongo_client():
    client = MongoClient('mongodb://mongodb:27017/')
    db = client['test_db']
    yield db
    # Cleanup after tests
    client.drop_database('test_db')

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
