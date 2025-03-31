# Set up comprehensive logging in utils/logging_setup.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app_name, log_level=logging.INFO):
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Ensure log directory exists
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/application.log', 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    # Stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger