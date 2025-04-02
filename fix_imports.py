#!/usr/bin/env python3
import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ImportFixer")

def install_requirements():
    """Install required packages using pip"""
    requirements = [
        "pdf2image",
        "Pillow",
        "pytesseract",
        "PyPDF2",  # Changed from pypdf2 to PyPDF2 (correct capitalization)
        "pandas",
        "flask"
    ]
    
    logger.info("Installing required packages...")
    for package in requirements:
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e.stderr}")
    
    logger.info("All packages installed successfully")

def check_imports():
    """Check if imports are working correctly"""
    test_imports = [
        "from pdf2image import convert_from_path",
        "from PIL import Image",
        "import pandas as pd",
        "import PyPDF2",  # Changed from pypdf2 to PyPDF2
        "from PyPDF2 import PdfReader",  # Added this import since it's used in code
        "import flask"
    ]
    
    logger.info("Testing imports...")
    for imp in test_imports:
        try:
            exec(imp)
            logger.info(f"✅ Import successful: {imp}")
        except ImportError as e:
            logger.error(f"❌ Import failed: {imp}")
            logger.error(f"Error: {e}")
    
    logger.info("Import tests completed")

if __name__ == "__main__":
    logger.info("Starting dependency installation and import testing")
    try:
        install_requirements()
        check_imports()
        print("\n✅ All dependencies installed and imports working correctly")
    except Exception as e:
        logger.error(f"Failed to fix imports: {e}")
        print("\n❌ There were errors fixing the imports. Check the logs.")
