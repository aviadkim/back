import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"
TEMP_DIR = BASE_DIR / "temp"

# Create directories if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Application settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", 5000))
FLASK_ENV = os.getenv("FLASK_ENV", "development")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-this")
JWT_SECRET = os.getenv("JWT_SECRET", "default-jwt-secret-change-this")

# Database settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/financial_documents")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

# Storage settings
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50))  # in MB

# AWS settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")

# OCR settings
OCR_ENGINE = os.getenv("OCR_ENGINE", "local")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "eng")
ADDITIONAL_LANGUAGES = os.getenv("ADDITIONAL_LANGUAGES", "heb").split(",")

# Cloud OCR settings
CLOUD_OCR_SERVICE = os.getenv("CLOUD_OCR_SERVICE", "")
AWS_TEXTRACT_KEY = os.getenv("AWS_TEXTRACT_KEY", "")
GOOGLE_VISION_KEY = os.getenv("GOOGLE_VISION_KEY", "")

# AI/ML settings
ENABLE_AI_FEATURES = os.getenv("ENABLE_AI_FEATURES", "true").lower() == "true"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/application.log")
LOG_ROTATION = os.getenv("LOG_ROTATION", "true").lower() == "true"
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10))  # in MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# Frontend settings
REACT_APP_API_URL = os.getenv("REACT_APP_API_URL", "http://localhost:5000/api")
REACT_APP_DEBUG = os.getenv("REACT_APP_DEBUG", "true").lower() == "true"
REACT_APP_DEFAULT_LANGUAGE = os.getenv("REACT_APP_DEFAULT_LANGUAGE", "en")

# Performance settings
WORKERS = int(os.getenv("WORKERS", 4))
MAX_CONCURRENT_PROCESSING = int(os.getenv("MAX_CONCURRENT_PROCESSING", 2))
PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", 300))  # in seconds
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
CACHE_EXPIRATION = int(os.getenv("CACHE_EXPIRATION", 3600))  # in seconds

# Security settings
ENABLE_CORS = os.getenv("ENABLE_CORS", "true").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 60))
JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))  # in seconds

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Export configuration as dictionary
config = {
    "debug": DEBUG,
    "port": PORT,
    "flask_env": FLASK_ENV,
    "secret_key": SECRET_KEY,
    "jwt_secret": JWT_SECRET,
    "mongo_uri": MONGO_URI,
    "storage_type": STORAGE_TYPE,
    "local_storage_path": LOCAL_STORAGE_PATH,
    "max_file_size": MAX_FILE_SIZE,
    "ocr_engine": OCR_ENGINE,
    "default_language": DEFAULT_LANGUAGE,
    "additional_languages": ADDITIONAL_LANGUAGES,
    "enable_ai_features": ENABLE_AI_FEATURES,
    "react_app_api_url": REACT_APP_API_URL,
    "workers": WORKERS,
    "processing_timeout": PROCESSING_TIMEOUT,
    "enable_cors": ENABLE_CORS,
    "cors_origins": CORS_ORIGINS,
    "enable_rate_limit": ENABLE_RATE_LIMIT,
    "rate_limit": RATE_LIMIT,
    "jwt_expiration": JWT_EXPIRATION,
}

# Document processor configuration
document_processor_config = {
    "ocr_engine": OCR_ENGINE,
    "default_language": DEFAULT_LANGUAGE,
    "additional_languages": ADDITIONAL_LANGUAGES,
    "enable_ai_features": ENABLE_AI_FEATURES,
    "processing_timeout": PROCESSING_TIMEOUT,
}