
import os
from pymongo import MongoClient, errors
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')

try:
    print(f"Attempting to connect to MongoDB at {mongo_uri}")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    client.server_info()  # Will throw exception if cannot connect
    print("MongoDB connection successful!")
except errors.ServerSelectionTimeoutError as e:
    print(f"MongoDB connection failed: {e}")
    print("MongoDB may not be running. You'll need to start it separately.")
except Exception as e:
    print(f"Unexpected error with MongoDB: {e}")
    