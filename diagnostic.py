import os
import subprocess
import sys
import importlib
import platform
from flask import Blueprint, jsonify

diagnostic_bp = Blueprint('diagnostic', __name__)

@diagnostic_bp.route('/check', methods=['GET'])
def run_diagnostics():
    """Run diagnostics on the PDF processing system"""
    results = {
        'status': 'ok',
        'checks': {},
        'issues_found': False,
        'recommendations': []
    }
    
    # Check 1: Python Dependencies
    check_python_dependencies(results)
    
    # Check 2: Directory Structure
    check_directory_structure(results)
    
    # Check 3: Tesseract OCR Installation
    check_tesseract(results)
    
    # Check 4: Check MongoDB Connection
    check_mongodb(results)
    
    # Check 5: Check Environment Variables
    check_env_variables(results)
    
    # Check 6: Check PDF dependencies
    check_pdf_libraries(results)
    
    # Determine overall status
    if any(not check.get('passed', False) for check in results['checks'].values()):
        results['status'] = 'issues_found'
        results['issues_found'] = True
    
    return jsonify(results)

def check_python_dependencies(results):
    """Check if all required Python packages are installed"""
    required_packages = [
        'flask', 'pymongo', 'PyPDF2', 'pdf2image', 'pytesseract', 
        'pillow', 'langchain', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing_packages.append(package)
    
    results['checks']['python_dependencies'] = {
        'passed': len(missing_packages) == 0,
        'message': 'All required Python packages are installed' if len(missing_packages) == 0 else f'Missing packages: {", ".join(missing_packages)}',
        'missing_packages': missing_packages
    }
    
    if missing_packages:
        results['recommendations'].append(f'Install missing packages with: pip install {" ".join(missing_packages)}')

def check_directory_structure(results):
    """Check if all required directories exist and are writable"""
    required_dirs = ['uploads', 'data', 'data/embeddings', 'data/templates', 'logs']
    missing_dirs = []
    unwritable_dirs = []
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        elif not os.access(directory, os.W_OK):
            unwritable_dirs.append(directory)
    
    issues = []
    if missing_dirs:
        issues.append(f'Missing directories: {", ".join(missing_dirs)}')
    if unwritable_dirs:
        issues.append(f'No write permission for directories: {", ".join(unwritable_dirs)}')
    
    results['checks']['directory_structure'] = {
        'passed': len(issues) == 0,
        'message': 'All required directories exist and are writable' if len(issues) == 0 else '; '.join(issues),
        'missing_dirs': missing_dirs,
        'unwritable_dirs': unwritable_dirs
    }
    
    if missing_dirs:
        results['recommendations'].append(f'Create missing directories with: mkdir -p {" ".join(missing_dirs)}')
    if unwritable_dirs:
        results['recommendations'].append(f'Fix permissions with: chmod -R 755 {" ".join(unwritable_dirs)}')

def check_tesseract(results):
    """Check if Tesseract OCR is installed and available"""
    try:
        output = subprocess.check_output(['tesseract', '--version'], stderr=subprocess.STDOUT).decode('utf-8')
        version = output.split('\n')[0] if output else "Unknown"
        
        # Check if Hebrew language is installed
        lang_output = subprocess.check_output(['tesseract', '--list-langs'], stderr=subprocess.STDOUT).decode('utf-8')
        has_hebrew = 'heb' in lang_output.lower()
        
        results['checks']['tesseract'] = {
            'passed': True,
            'message': f'Tesseract installed: {version}',
            'version': version,
            'has_hebrew': has_hebrew
        }
        
        if not has_hebrew:
            results['checks']['tesseract']['passed'] = False
            results['checks']['tesseract']['message'] += ' - Hebrew language pack not found'
            results['recommendations'].append('Install Tesseract Hebrew language pack')
            
            # Add OS-specific instructions
            if platform.system() == 'Linux':
                results['recommendations'].append('For Linux: sudo apt-get install tesseract-ocr-heb')
            elif platform.system() == 'Darwin':  # macOS
                results['recommendations'].append('For macOS: brew install tesseract-lang')
            elif platform.system() == 'Windows':
                results['recommendations'].append('For Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki and select Hebrew during installation')
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        results['checks']['tesseract'] = {
            'passed': False,
            'message': 'Tesseract OCR is not installed or not in PATH',
            'version': None,
            'has_hebrew': False
        }
        
        # Add OS-specific instructions
        if platform.system() == 'Linux':
            results['recommendations'].append('Install Tesseract OCR with: sudo apt-get install tesseract-ocr tesseract-ocr-heb')
        elif platform.system() == 'Darwin':  # macOS
            results['recommendations'].append('Install Tesseract OCR with: brew install tesseract tesseract-lang')
        elif platform.system() == 'Windows':
            results['recommendations'].append('Download Tesseract installer from https://github.com/UB-Mannheim/tesseract/wiki')
        
        results['recommendations'].append('After installation, ensure Tesseract is in your system PATH')

def check_mongodb(results):
    """Check MongoDB connection"""
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/financial_documents')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        results['checks']['mongodb'] = {
            'passed': True,
            'message': 'Successfully connected to MongoDB',
            'uri': mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri  # Hide credentials
        }
    except (ImportError, ConnectionFailure, Exception) as e:
        results['checks']['mongodb'] = {
            'passed': False,
            'message': f'Failed to connect to MongoDB: {str(e)}',
            'uri': os.environ.get('MONGO_URI', 'Not set').split('@')[-1] if '@' in os.environ.get('MONGO_URI', '') else os.environ.get('MONGO_URI', 'Not set')
        }
        results['recommendations'].append('Ensure MongoDB is running: docker-compose up -d')
        results['recommendations'].append('Check MongoDB connection string in .env file')

def check_env_variables(results):
    """Check if all required environment variables are set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'FLASK_ENV': 'development',
        'PORT': '5000',
        'MONGO_URI': 'mongodb://localhost:27017/financial_documents',
        'SECRET_KEY': None,
        'JWT_SECRET': None,
        'DEFAULT_LANGUAGE': 'he'
    }
    
    api_vars = {
        'HUGGINGFACE_API_KEY': 'Required for AI model access',
        'MISTRAL_API_KEY': 'Optional - for Mistral AI',
        'OPENAI_API_KEY': 'Optional - for OpenAI'
    }
    
    missing_vars = []
    for var, default in required_vars.items():
        if not os.environ.get(var) and default is None:
            missing_vars.append(var)
    
    # Check at least one AI API key is set
    has_api_key = any(os.environ.get(key) for key in api_vars)
    
    results['checks']['env_variables'] = {
        'passed': len(missing_vars) == 0 and has_api_key,
        'message': 'All required environment variables are set' if len(missing_vars) == 0 and has_api_key else 'Missing required environment variables',
        'missing_vars': missing_vars,
        'has_api_key': has_api_key
    }
    
    if missing_vars:
        results['recommendations'].append(f'Set missing environment variables in .env file: {", ".join(missing_vars)}')
    
    if not has_api_key:
        results['recommendations'].append('Set at least one AI API key (HUGGINGFACE_API_KEY, MISTRAL_API_KEY, or OPENAI_API_KEY) in .env file')

def check_pdf_libraries(results):
    """Check PDF processing capabilities"""
    from importlib.util import find_spec
    
    libraries = {
        'PyPDF2': None,
        'pdf2image': None,
        'poppler': None,
        'pytesseract': None,
        'PIL': None
    }
    
    # Check Python libraries
    for lib in ['PyPDF2', 'pdf2image', 'pytesseract']:
        libraries[lib] = find_spec(lib) is not None
    
    # Check for PIL/Pillow
    libraries['PIL'] = find_spec('PIL') is not None
    
    # Check for poppler-utils
    try:
        poppler_output = subprocess.check_output(['pdfinfo', '-v'], stderr=subprocess.STDOUT).decode('utf-8')
        libraries['poppler'] = 'pdfinfo' in poppler_output.lower() or 'poppler' in poppler_output.lower()
    except (subprocess.CalledProcessError, FileNotFoundError):
        libraries['poppler'] = False
    
    missing_libs = [lib for lib, installed in libraries.items() if not installed]
    
    results['checks']['pdf_libraries'] = {
        'passed': len(missing_libs) == 0,
        'message': 'All required PDF processing libraries are installed' if len(missing_libs) == 0 else f'Missing PDF libraries: {", ".join(missing_libs)}',
        'libraries': libraries,
        'missing_libs': missing_libs
    }
    
    if 'poppler' in missing_libs:
        if platform.system() == 'Linux':
            results['recommendations'].append('Install poppler-utils with: sudo apt-get install poppler-utils')
        elif platform.system() == 'Darwin':  # macOS
            results['recommendations'].append('Install poppler with: brew install poppler')
        elif platform.system() == 'Windows':
            results['recommendations'].append('Download poppler for Windows from https://github.com/oschwartz10612/poppler-windows/releases')
    
    missing_py_libs = [lib for lib in missing_libs if lib not in ['poppler']]
    if missing_py_libs:
        results['recommendations'].append(f'Install missing Python libraries with: pip install {" ".join(missing_py_libs)}')

# Add this route to your main Flask app
def register_diagnostic_routes(app):
    app.register_blueprint(diagnostic_bp, url_prefix='/diagnostic')
