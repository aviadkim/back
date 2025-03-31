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

# Upload settings
UPLOAD_FOLDER = str(UPLOADS_DIR)
MAX_CONTENT_LENGTH = int(os.getenv("MAX_FILE_SIZE", 50)) * 1024 * 1024  # in bytes

# Database settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/financial_documents")
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")

# Storage settings
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local")
LOCAL_STORAGE_PATH = os.getenv("LOCAL_STORAGE_PATH", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50))  # in MB

# OCR settings
OCR_ENGINE = os.getenv("OCR_ENGINE", "local")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "eng")
ADDITIONAL_LANGUAGES = os.getenv("ADDITIONAL_LANGUAGES", "heb").split(",")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/application.log")
LOG_ROTATION = os.getenv("LOG_ROTATION", "true").lower() == "true"
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 10))  # in MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# Document processor configuration
document_processor_config = {
    "ocr_engine": OCR_ENGINE,
    "default_language": DEFAULT_LANGUAGE,
    "additional_languages": ADDITIONAL_LANGUAGES,
}