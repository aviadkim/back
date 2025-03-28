from pymongo import MongoClient
import os
from dotenv import load_dotenv

def test_mongo_connection():
    try:
        load_dotenv()
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/financial_documents")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Will raise an exception if cannot connect
        print("✅ Successfully connected to MongoDB")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

if __name__ == "__main__":
    test_mongo_connection()
