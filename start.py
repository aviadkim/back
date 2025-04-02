#!/usr/bin/env python
"""
Startup script for the Financial Document Analysis System
This script handles:
1. Directory creation
2. Environment validation
3. MongoDB check
4. Starting the application
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("startup")

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def create_directories():
    """Create all required directories"""
    print_header("Creating required directories")
    
    required_dirs = [
        'uploads',
        'data',
        'data/embeddings',
        'data/templates',
        'logs',
        'frontend/build/static',
        'frontend/build/static/css',
        'frontend/build/static/js',
        'frontend/build/static/media',
        'frontend/build/images'
    ]
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
        else:
            logger.info(f"Directory already exists: {directory}")
            
    return True

def validate_environment():
    """Validate environment variables"""
    print_header("Validating environment")
    
    # Load environment variables
    load_dotenv()
    
    # Required environment variables
    required_vars = [
        'FLASK_ENV',
        'PORT',
        'SECRET_KEY',
        'JWT_SECRET',
        'DEFAULT_LANGUAGE'
    ]
    
    # Check all required variables
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please update your .env file with these variables")
        return False
    
    # Check API keys
    api_key = os.environ.get('HUGGINGFACE_API_KEY')
    if not api_key or api_key == 'your_huggingface_api_key_here':
        logger.warning("No valid HUGGINGFACE_API_KEY found. The system will use a dummy AI model.")
        logger.warning("For full functionality, please add your Hugging Face API key to the .env file.")
    else:
        logger.info("HUGGINGFACE_API_KEY found.")
    
    logger.info("Environment validation complete.")
    return True

def check_mongodb():
    """Check if MongoDB is running"""
    print_header("Checking MongoDB")
    
    # Check if Docker is installed
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Docker not found. Cannot verify MongoDB status.")
        logger.warning("If MongoDB is not running, the application may not work correctly.")
        return True
    
    # Check if MongoDB container is running
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=mongodb", "--format", "{{.Names}}"],
            check=True, 
            capture_output=True,
            text=True
        )
        
        if "mongodb" in result.stdout:
            logger.info("MongoDB is running.")
            return True
        
        # Try to start MongoDB using docker-compose
        logger.warning("MongoDB is not running. Attempting to start...")
        
        if os.path.exists("docker-compose.yml"):
            try:
                subprocess.run(["docker-compose", "up", "-d"], check=True)
                logger.info("MongoDB started successfully.")
                return True
            except subprocess.CalledProcessError:
                logger.error("Failed to start MongoDB using docker-compose.")
                logger.error("Please start MongoDB manually before running the application.")
                return False
        else:
            logger.error("docker-compose.yml not found. Cannot start MongoDB.")
            logger.error("Please start MongoDB manually before running the application.")
            return False
    
    except subprocess.CalledProcessError:
        logger.error("Error checking MongoDB status.")
        logger.warning("If MongoDB is not running, the application may not work correctly.")
        return True

def run_tests():
    """Run tests to make sure everything is working"""
    print_header("Running tests")
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-v"],
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("All tests passed successfully!")
            return True
        else:
            logger.error("Some tests failed.")
            print(result.stdout)
            print(result.stderr)
            return False
    
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        return False

def start_application():
    """Start the Flask application"""
    print_header("Starting the application")
    
    try:
        port = os.environ.get('PORT', '5000')
        logger.info(f"Starting application on port {port}")
        logger.info("Press Ctrl+C to stop the application")
        
        # Run the Flask application
        subprocess.run(["python", "app.py"], check=True)
        return True
    
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        return True
    
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        return False

def main():
    """Main function to run all checks and start the application"""
    print_header("Financial Document Analysis System Startup")
    
    # Run all checks
    if not create_directories():
        sys.exit(1)
    
    if not validate_environment():
        sys.exit(1)
    
    if not check_mongodb():
        sys.exit(1)
    
    # Run tests
    run_tests()
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main()
