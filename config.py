import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    MONGODB_URI = os.environ.get('MONGODB_URI')
    
    # API Keys
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
    
    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Analysis settings
    ANALYSIS_CACHE_TIME = 3600  # 1 hour
    MAX_PAGES_PER_DOC = 50
