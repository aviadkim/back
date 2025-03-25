#!/usr/bin/env python3
"""
סקריפט להגדרת סביבת הפיתוח, יצירת תיקיות, ובדיקת תלויות
"""

import os
import sys
import shutil
import subprocess
import platform
import logging

# הגדרת לוגר
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """בדיקת גרסת פייתון"""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        logger.error(f"Python {required_version[0]}.{required_version[1]} or higher is required. You have {current_version[0]}.{current_version[1]}")
        return False
    
    logger.info(f"Python version {current_version[0]}.{current_version[1]} - OK")
    return True

def create_directories():
    """יצירת תיקיות נדרשות"""
    required_dirs = [
        'uploads',
        'data',
        'data/embeddings',
        'data/memory',
        'data/templates',
        'logs',
        'tests',
        'frontend/build'
    ]
    
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Directory '{directory}' - Created/Verified")
    
    return True

def check_tesseract():
    """בדיקת התקנת Tesseract OCR"""
    try:
        command = 'tesseract --version'
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if process.returncode == 0:
            version = process.stdout.split('\n')[0].strip()
            logger.info(f"Tesseract OCR - {version}")
            return True
        else:
            logger.warning("Tesseract OCR not found")
            return False
    
    except Exception as e:
        logger.warning(f"Error checking Tesseract: {e}")
        return False

def check_mongodb():
    """בדיקת תקינות חיבור MongoDB"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()  # will throw an exception if cannot connect
        logger.info("MongoDB - Connection successful")
        return True
    except ImportError:
        logger.warning("pymongo not installed - cannot check MongoDB")
        return False
    except Exception as e:
        logger.warning(f"MongoDB connection error: {e}")
        return False

def install_requirements():
    """התקנת תלויות Python"""
    if not os.path.exists("requirements.txt"):
        logger.error("requirements.txt not found")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        logger.info("Requirements - Installation successful")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error installing requirements: {e}")
        return False

def check_env_file():
    """בדיקת קובץ .env"""
    if not os.path.exists(".env"):
        logger.warning(".env file not found - creating from template")
        
        if os.path.exists(".env.template") or os.path.exists(".env Template.txt"):
            template_file = ".env.template" if os.path.exists(".env.template") else ".env Template.txt"
            shutil.copy(template_file, ".env")
            logger.info(".env - Created from template")
        else:
            logger.warning("No .env template found - creating basic .env file")
            with open(".env", "w") as f:
                f.write("""# הגדרות כלליות
FLASK_ENV=development
PORT=5000

# הגדרות API חיצוניים
HUGGINGFACE_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# הגדרות מסד נתונים
MONGO_URI=mongodb://localhost:27017/financial_documents

# הגדרות אבטחה
SECRET_KEY=development_key
JWT_SECRET=development_jwt_key

# הגדרות שפה
DEFAULT_LANGUAGE=he
""")
            logger.info(".env - Created basic file")
    else:
        logger.info(".env - File exists")
    
    return True

def print_system_info():
    """הדפסת מידע מערכת"""
    logger.info("=== מידע מערכת ===")
    logger.info(f"OS: {platform.system()} {platform.release()}")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Working directory: {os.getcwd()}")

def main():
    """פונקציה ראשית"""
    print_system_info()
    
    logger.info("=== בדיקת סביבת עבודה ===")
    
    # בדיקת גרסת פייתון
    if not check_python_version():
        sys.exit(1)
    
    # יצירת תיקיות
    create_directories()
    
    # התקנת תלויות
    install_requirements()
    
    # בדיקת קובץ .env
    check_env_file()
    
    # בדיקת Tesseract
    check_tesseract()
    
    # בדיקת MongoDB
    check_mongodb()
    
    logger.info("=== סיום בדיקת סביבה ===")
    logger.info("Setup completed successfully. You can now run the application with 'python app.py'")

if __name__ == "__main__":
    main()
