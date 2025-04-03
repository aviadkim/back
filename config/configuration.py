import os
from pathlib import Path
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

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

# OCR settings
OCR_ENGINE = os.getenv("OCR_ENGINE", "tesseract")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "eng")
ADDITIONAL_LANGUAGES = os.getenv("ADDITIONAL_LANGUAGES", "heb").split(",")

# Setup logging
def setup_logging(app_name="financial_documents", log_level=None):
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO")
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logger = logging.getLogger(app_name)
    logger.setLevel(numeric_level)
    
    # Check if handlers already exist to avoid duplicates
    if not logger.handlers:
        # File handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(LOGS_DIR, f"{app_name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# Document processor configuration
document_processor_config = {
    "ocr_engine": OCR_ENGINE,
    "default_language": DEFAULT_LANGUAGE,
    "additional_languages": ADDITIONAL_LANGUAGES,
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB file size limit
