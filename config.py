import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    MONGODB_URI = os.environ.get('MONGODB_URI')
    
    # API Keys / Secrets
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_dev_secret_key_local') # Added default for local dev
    # Payment processing
    PADDLE_VENDOR_ID = os.environ.get('PADDLE_VENDOR_ID')
    PADDLE_API_KEY = os.environ.get('PADDLE_API_KEY')
    PADDLE_PUBLIC_KEY = os.environ.get('PADDLE_PUBLIC_KEY')

    JWT_SECRET = os.environ.get('JWT_SECRET', 'default_dev_jwt_secret_local') # Added default for local dev
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY') # Added Hugging Face key
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY') # Added OpenRouter API key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') # Added Gemini API key

    # Upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Analysis settings
    ANALYSIS_CACHE_TIME = 3600  # 1 hour
    MAX_PAGES_PER_DOC = 50
    
    # Celery Configuration (using Redis)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
