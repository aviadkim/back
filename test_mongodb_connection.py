from mongodb.connection import get_db_collections
import sys

def test_connection():
    """Test MongoDB connection"""
    try:
        db, collections = get_db_collections()
        print("Successfully connected to MongoDB!")
        print(f"Available collections: {', '.join(collections.keys())}")
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
