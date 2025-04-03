"""Configuration for AI services"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Model names
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'openrouter')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', 'google/flan-t5-small')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')

# Application settings
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
PORT = int(os.getenv('PORT', '5001'))
MAX_UPLOAD_SIZE = os.getenv('MAX_UPLOAD_SIZE', '100MB')
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'heb+eng')
OCR_DPI = int(os.getenv('OCR_DPI', '300'))
