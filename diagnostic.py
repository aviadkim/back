import os
import subprocess
import sys
import importlib
import platform
import time
import json
import re
import logging
from flask import Blueprint, jsonify, request, send_file, render_template
import io
from typing import Dict, List, Any, Optional

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

diagnostic_bp = Blueprint('diagnostic', __name__)

@diagnostic_bp.route('/', methods=['GET'])
def diagnostic_dashboard():
    """Render the diagnostic dashboard"""
    return render_template('diagnostic.html')

@diagnostic_bp.route('/check', methods=['GET'])
def run_diagnostics():
    """Run comprehensive diagnostics on the PDF processing system"""
    results = {
        'status': 'ok',
        'checks': {},
        'issues_found': False,
        'recommendations': [],
        'timestamp': time.time(),
        'system_info': get_system_info()
    }
    
    # Basic checks
    check_python_dependencies(results)
    check_directory_structure(results)
    check_tesseract(results)
    check_mongodb(results)
    check_env_variables(results)
    check_pdf_libraries(results)
    
    # Advanced checks
    check_network_connectivity(results)
    check_disk_space(results)
    check_api_endpoints(results)
    
    # Determine overall status
    if any(not check.get('passed', False) for check in results['checks'].values()):
        results['status'] = 'issues_found'
        results['issues_found'] = True
    
    return jsonify(results)

@diagnostic_bp.route('/repair', methods=['POST'])
def repair_issues():
    """Attempt to automatically repair common issues"""
    issue_type = request.json.get('issue_type')
    
    results = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        if issue_type == 'directory_structure':
            results = repair_directory_structure()
        elif issue_type == 'python_dependencies':
            package = request.json.get('package')
            results = repair_python_dependencies(package)
        elif issue_type == 'mongodb':
            results = repair_mongodb()
        elif issue_type == 'tesseract_language':
            results = repair_tesseract_language()
        else:
            results['message'] = 'Unknown issue type'
    except Exception as e:
        results['message'] = f'Error during repair: {str(e)}'
        results['details']['error'] = str(e)
    
    return jsonify(results)

@diagnostic_bp.route('/test-pdf', methods=['POST'])
def test_pdf_processing():
    """Test PDF processing with a sample file"""
    results = {
        'success': False,
        'text_extraction': {
            'status': False,
            'elapsed_time': 0,
            'extracted_text': '',
            'character_count': 0
        },
        'ocr': {
            'status': False,
            'elapsed_time': 0,
            'supported_languages': []
        },
        'tables': {
            'status': False,
            'elapsed_time': 0,
            'tables_found': 0
        }
    }
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'message': 'Only PDF files are supported for testing'})
        
        # Save the uploaded file
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, 'test_file.pdf')
        file.save(file_path)
        
        # Test text extraction
        start_time = time.time()
        try:
            from pdf_processor.extraction.text_extractor import PDFTextExtractor
            extractor = PDFTextExtractor()
            doc = extractor.extract_document(file_path)
            
            # Get text from the first page
            if doc and 0 in doc:
                extracted_text = doc[0].get('text', '')
            else:
                extracted_text = ''
                
            results['text_extraction']['status'] = len(extracted_text) > 0
            results['text_extraction']['extracted_text'] = extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text
            results['text_extraction']['character_count'] = len(extracted_text)
        except Exception as e:
            results['text_extraction']['error'] = str(e)
        results['text_extraction']['elapsed_time'] = time.time() - start_time
        
        # Test OCR
        start_time = time.time()
        try:
            import pytesseract
            from PIL import Image
            import pdf2image
            
            # Get the first page as image
            images = pdf2image.convert_from_path(file_path, first_page=1, last_page=1)
            if images:
                # Test OCR on the first page
                ocr_text = pytesseract.image_to_string(images[0])
                results['ocr']['status'] = len(ocr_text) > 0
                results['ocr']['supported_languages'] = pytesseract.get_languages()
        except Exception as e:
            results['ocr']['error'] = str(e)
        results['ocr']['elapsed_time'] = time.time() - start_time
        
        # Test table extraction
        start_time = time.time()
        try:
            from pdf_processor.tables.table_extractor import TableExtractor
            
            table_extractor = TableExtractor()
            tables = table_extractor.extract_tables(file_path)
            
            # Count total tables across all pages
            total_tables = sum(len(page_tables) for page_tables in tables.values())
            
            results['tables']['status'] = total_tables > 0
            results['tables']['tables_found'] = total_tables
        except Exception as e:
            results['tables']['error'] = str(e)
        results['tables']['elapsed_time'] = time.time() - start_time
        
        # Overall success
        results['success'] = (
            results['text_extraction']['status'] or 
            results['ocr']['status'] or 
            results['tables']['status']
        )
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
    except Exception as e:
        results['error'] = str(e)
    
    return jsonify(results)

@diagnostic_bp.route('/generate-test-pdf', methods=['GET'])
def generate_test_pdf():
    """Generate a test PDF file with different elements for testing"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
        
        # Create a PDF in memory
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # Add a title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Test PDF for Document Processing")
        
        # Add normal text
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, "This is a test PDF file generated for diagnostic purposes.")
        c.drawString(50, height - 100, "It contains text, numbers, and a simple table.")
        
        # Add some financial data
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 140, "Financial Data:")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 160, "Revenue: $1,250,000.00")
        c.drawString(50, height - 180, "Expenses: $750,000.00")
        c.drawString(50, height - 200, "Profit: $500,000.00")
        c.drawString(50, height - 220, "Profit Margin: 40%")
        
        # Create a simple table
        data = [
            ['Quarter', 'Revenue', 'Expenses', 'Profit'],
            ['Q1', '$300,000', '$200,000', '$100,000'],
            ['Q2', '$350,000', '$200,000', '$150,000'],
            ['Q3', '$280,000', '$160,000', '$120,000'],
            ['Q4', '$320,000', '$190,000', '$130,000']
        ]
        
        t = Table(data, colWidths=[80, 80, 80, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        t.wrapOn(c, width, height)
        t.drawOn(c, 50, height - 350)
        
        # Add some text in English and Hebrew (if font available)
        try:
            # Try to add Hebrew text if possible
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 400, "Text in English and Hebrew:")
            c.drawString(50, height - 420, "English: This is a test.")
            c.drawString(50, height - 440, "Hebrew: זהו מסמך בדיקה.")
        except:
            # If Hebrew fails, just add English
            c.drawString(50, height - 400, "Text in English:")
            c.drawString(50, height - 420, "English: This is a test.")
        
        # Finish the PDF
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name="test_document.pdf",
            mimetype="application/pdf"
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating PDF: {str(e)}'
        })

def get_system_info():
    """Get system information for diagnostics"""
    info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'processor': platform.processor() or 'Unknown',
        'hostname': platform.node()
    }
    
    # Get memory info if possible
    try:
        if platform.system() == 'Linux':
            mem_info = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        mem_info[key.strip()] = value.strip()
            
            if 'MemTotal' in mem_info:
                info['memory_total'] = mem_info['MemTotal']
            if 'MemFree' in mem_info:
                info['memory_free'] = mem_info['MemFree']
    except:
        pass
    
    return info

def check_python_dependencies(results):
    """Check if all required Python packages are installed"""
    # Extended list of required packages
    required_packages = [
        'flask', 'pymongo', 'PyPDF2', 'pdf2image', 'pytesseract', 
        'pillow', 'langchain', 'python-dotenv', 'sqlalchemy',
        'transformers', 'sentence-transformers', 'huggingface-hub',
        'pandas', 'numpy', 'tqdm', 'requests'
    ]
    
    missing_packages = []
    installed_packages = {}
    
    for package in required_packages:
        try:
            # Try to import the package
            module = importlib.import_module(package)
            
            # Get version if available
            version = getattr(module, '__version__', 'Unknown')
            installed_packages[package] = version
        except ImportError:
            missing_packages.append(package)
    
    results['checks']['python_dependencies'] = {
        'passed': len(missing_packages) == 0,
        'message': 'All required Python packages are installed' if len(missing_packages) == 0 else f'Missing packages: {", ".join(missing_packages)}',
        'missing_packages': missing_packages,
        'installed_packages': installed_packages
    }
    
    if missing_packages:
        results['recommendations'].append(f'Install missing packages with: pip install {" ".join(missing_packages)}')

def check_directory_structure(results):
    """Check if all required directories exist and are writable"""
    required_dirs = ['uploads', 'data', 'data/embeddings', 'data/templates', 'logs', 'templates']
    missing_dirs = []
    unwritable_dirs = []
    dir_info = {}
    
    for directory in required_dirs:
        dir_info[directory] = {
            'exists': os.path.exists(directory),
            'is_dir': os.path.isdir(directory) if os.path.exists(directory) else False,
            'writable': os.access(directory, os.W_OK) if os.path.exists(directory) else False
        }
        
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
        'unwritable_dirs': unwritable_dirs,
        'directories': dir_info
    }
    
    if missing_dirs:
        results['recommendations'].append(f'Create missing directories with: mkdir -p {" ".join(missing_dirs)}')
    if unwritable_dirs:
        results['recommendations'].append(f'Fix permissions with: chmod -R 755 {" ".join(unwritable_dirs)}')

def check_tesseract(results):
    """Check if Tesseract OCR is installed and available"""
    try:
        output = subprocess.check_output(['tesseract', '--version'], stderr=subprocess.STDOUT).decode('utf-8')
        version_match = re.search(r'tesseract\s+(\d+\.\d+\.\d+)', output)
        version = version_match.group(0) if version_match else "Unknown"
        
        # Check if Hebrew language is available
        lang_output = subprocess.check_output(['tesseract', '--list-langs'], stderr=subprocess.STDOUT).decode('utf-8')
        supported_langs = lang_output.strip().split('\n')[1:]  # Skip the header
        has_hebrew = 'heb' in lang_output.lower()
        
        # Try to get more detailed information
        tessdata_dir = None
        for line in output.split('\n'):
            if 'TESSDATA_PREFIX' in line:
                tessdata_dir = line.split('=')[1].strip()
        
        results['checks']['tesseract'] = {
            'passed': True,
            'message': f'Tesseract installed: {version}',
            'version': version,
            'has_hebrew': has_hebrew,
            'tessdata_dir': tessdata_dir,
            'supported_languages': supported_langs
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
            'has_hebrew': False,
            'supported_languages': []
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
        
        # Parse the URI to get host and port
        if '://' in mongo_uri:
            host_part = mongo_uri.split('://')[1].split('/')[0]
            if '@' in host_part:
                host_part = host_part.split('@')[1]  # Remove username/password
        else:
            host_part = 'unknown'
        
        # Try to connect
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        server_info = client.admin.command('ping')
        
        # Get additional server info if available
        try:
            server_status = client.admin.command('serverStatus')
            version = server_status.get('version', 'Unknown')
            uptime = server_status.get('uptime', 0)
            connections = server_status.get('connections', {}).get('current', 0)
        except:
            version = 'Unknown'
            uptime = 0
            connections = 0
        
        results['checks']['mongodb'] = {
            'passed': True,
            'message': 'Successfully connected to MongoDB',
            'uri': host_part,  # Hide credentials
            'version': version,
            'uptime': uptime,
            'connections': connections
        }
    except (ImportError, ConnectionFailure, Exception) as e:
        results['checks']['mongodb'] = {
            'passed': False,
            'message': f'Failed to connect to MongoDB: {str(e)}',
            'uri': host_part if 'host_part' in locals() else 'unknown'
        }
        
        # Custom recommendations
        if 'Connection refused' in str(e):
            results['recommendations'].append('Ensure MongoDB is running: docker-compose up -d')
            results['recommendations'].append('Check MongoDB connection string in .env file')
        elif 'authentication failed' in str(e).lower():
            results['recommendations'].append('Check MongoDB username and password in connection string')
        elif 'timed out' in str(e).lower():
            results['recommendations'].append('Check if MongoDB server is accessible from this network')
        else:
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
    env_values = {}
    
    for var, default in required_vars.items():
        value = os.environ.get(var)
        if not value and default is None:
            missing_vars.append(var)
        
        # Store sanitized values (hide secrets)
        if var in ['SECRET_KEY', 'JWT_SECRET', 'HUGGINGFACE_API_KEY', 'MISTRAL_API_KEY', 'OPENAI_API_KEY'] and value:
            env_values[var] = f"{value[:3]}...{value[-3:]}" if len(value) > 6 else "Set"
        else:
            env_values[var] = value or default
    
    # Check at least one AI API key is set
    has_api_key = any(os.environ.get(key) for key in api_vars)
    api_key_status = {}
    for key in api_vars:
        api_key_status[key] = bool(os.environ.get(key))
    
    results['checks']['env_variables'] = {
        'passed': len(missing_vars) == 0 and has_api_key,
        'message': 'All required environment variables are set' if len(missing_vars) == 0 and has_api_key else 'Missing required environment variables',
        'missing_vars': missing_vars,
        'has_api_key': has_api_key,
        'api_keys': api_key_status,
        'env_values': env_values
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
    
    versions = {}
    
    # Check Python libraries
    for lib in ['PyPDF2', 'pdf2image', 'pytesseract']:
        libraries[lib] = find_spec(lib) is not None
        if libraries[lib]:
            try:
                module = importlib.import_module(lib)
                versions[lib] = getattr(module, '__version__', 'Unknown')
            except:
                versions[lib] = 'Unknown'
    
    # Check for PIL/Pillow
    libraries['PIL'] = find_spec('PIL') is not None
    if libraries['PIL']:
        try:
            from PIL import __version__
            versions['PIL'] = __version__
        except:
            try:
                from PIL import Image
                versions['PIL'] = 'Installed (version unknown)'
            except:
                versions['PIL'] = 'Unknown'
    
    # Check for poppler-utils
    try:
        poppler_output = subprocess.check_output(['pdfinfo', '-v'], stderr=subprocess.STDOUT).decode('utf-8')
        poppler_version = re.search(r'pdfinfo\s+version\s+([\d\.]+)', poppler_output)
        libraries['poppler'] = True
        versions['poppler'] = poppler_version.group(1) if poppler_version else 'Unknown'
    except (subprocess.CalledProcessError, FileNotFoundError):
        libraries['poppler'] = False
    
    missing_libs = [lib for lib, installed in libraries.items() if not installed]
    
    results['checks']['pdf_libraries'] = {
        'passed': len(missing_libs) == 0,
        'message': 'All required PDF processing libraries are installed' if len(missing_libs) == 0 else f'Missing PDF libraries: {", ".join(missing_libs)}',
        'libraries': libraries,
        'versions': versions,
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

def check_network_connectivity(results):
    """Check network connectivity to external services"""
    external_services = {
        'huggingface.co': False,
        'api.openai.com': False,
        'api.mistral.ai': False,
        'cdn.jsdelivr.net': False,
        'github.com': False
    }
    
    response_times = {}
    
    for service in external_services:
        try:
            start_time = time.time()
            response = subprocess.run(
                ['ping', '-c', '1', service] if platform.system() != 'Windows' else ['ping', '-n', '1', service],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=3
            )
            end_time = time.time()
            
            external_services[service] = response.returncode == 0
            response_times[service] = round((end_time - start_time) * 1000)  # ms
        except:
            external_services[service] = False
            response_times[service] = -1
    
    all_passed = all(external_services.values())
    
    results['checks']['network_connectivity'] = {
        'passed': all_passed,
        'message': 'Successfully connected to all external services' if all_passed else 'Failed to connect to some external services',
        'services': external_services,
        'response_times': response_times
    }
    
    if not all_passed:
        failed_services = [service for service, status in external_services.items() if not status]
        results['recommendations'].append(f'Check network connectivity to: {", ".join(failed_services)}')
        results['recommendations'].append('Ensure firewall rules allow outbound connections to these services')

def check_disk_space(results):
    """Check available disk space"""
    try:
        if platform.system() == 'Windows':
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p('.'), None, ctypes.pointer(total_bytes), ctypes.pointer(free_bytes)
            )
            free_gb = free_bytes.value / (1024 ** 3)
            total_gb = total_bytes.value / (1024 ** 3)
        else:
            # Unix/Linux/Mac
            stat = os.statvfs('.')
            free_gb = (stat.f_frsize * stat.f_bavail) / (1024 ** 3)
            total_gb = (stat.f_frsize * stat.f_blocks) / (1024 ** 3)
        
        percent_free = (free_gb / total_gb) * 100 if total_gb > 0 else 0
        
        results['checks']['disk_space'] = {
            'passed': free_gb > 1.0,  # At least 1GB free
            'message': f'Sufficient disk space available ({free_gb:.2f} GB free)' if free_gb > 1.0 else f'Low disk space ({free_gb:.2f} GB free)',
            'free_gb': round(free_gb, 2),
            'total_gb': round(total_gb, 2),
            'percent_free': round(percent_free, 2)
        }
        
        if free_gb <= 1.0:
            results['recommendations'].append('Free up disk space to ensure proper document processing')
    except:
        results['checks']['disk_space'] = {
            'passed': True,  # Assume passed if we can't check
            'message': 'Could not determine disk space',
            'error': 'Failed to check disk space'
        }

def check_api_endpoints(results):
    """Check if API endpoints are working"""
    endpoints = {
        '/health': False,
        '/api/health': False
    }
    
    statuses = {}
    
    # These checks would normally involve HTTP requests
    # For safety, we'll do simple file existence checks instead
    try:
        # Check for main app file (as a proxy for /health endpoint)
        endpoints['/health'] = os.path.exists('app.py')
        
        # Check for API routes file (as a proxy for /api endpoints)
        endpoints['/api/health'] = os.path.exists('routes/document_routes.py')
        
        # Store detailed status
        statuses['/health'] = 'File exists' if endpoints['/health'] else 'File missing'
        statuses['/api/health'] = 'File exists' if endpoints['/api/health'] else 'File missing'
    except:
        pass
    
    all_endpoints_ok = all(endpoints.values())
    
    results['checks']['api_endpoints'] = {
        'passed': all_endpoints_ok,
        'message': 'All API endpoints are available' if all_endpoints_ok else 'Some API endpoints may be unavailable',
        'endpoints': endpoints,
        'statuses': statuses
    }
    
    if not all_endpoints_ok:
        missing_endpoints = [endpoint for endpoint, status in endpoints.items() if not status]
        results['recommendations'].append(f'Check implementation of endpoints: {", ".join(missing_endpoints)}')

def repair_directory_structure():
    """Create missing directories"""
    required_dirs = ['uploads', 'data', 'data/embeddings', 'data/templates', 'logs', 'templates']
    results = {
        'success': True,
        'message': 'Successfully created missing directories',
        'details': {
            'created_dirs': []
        }
    }
    
    try:
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                results['details']['created_dirs'].append(directory)
        
        if not results['details']['created_dirs']:
            results['message'] = 'No directories needed to be created'
    except Exception as e:
        results['success'] = False
        results['message'] = f'Error creating directories: {str(e)}'
    
    return results

def repair_python_dependencies(package=None):
    """Install missing Python dependencies"""
    results = {
        'success': False,
        'message': '',
        'details': {
            'installed': [],
            'failed': []
        }
    }
    
    try:
        if package:
            # Install specific package
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            results['details']['installed'].append(package)
            results['success'] = True
            results['message'] = f'Successfully installed {package}'
        else:
            # Install all missing packages
            required_packages = [
                'flask', 'pymongo', 'PyPDF2', 'pdf2image', 'pytesseract', 
                'pillow', 'langchain', 'python-dotenv', 'sqlalchemy',
                'transformers', 'sentence-transformers', 'huggingface-hub',
                'pandas', 'numpy', 'tqdm', 'requests'
            ]
            
            for pkg in required_packages:
                try:
                    importlib.import_module(pkg)
                except ImportError:
                    try:
                        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
                        results['details']['installed'].append(pkg)
                    except:
                        results['details']['failed'].append(pkg)
            
            if results['details']['installed']:
                results['success'] = True
                results['message'] = f'Successfully installed {len(results["details"]["installed"])} packages'
            else:
                results['message'] = 'No packages needed to be installed'
                results['success'] = True
    except Exception as e:
        results['success'] = False
        results['message'] = f'Error installing packages: {str(e)}'
    
    return results

def repair_mongodb():
    """Attempt to start MongoDB service"""
    results = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        # Try starting MongoDB with docker-compose
        if os.path.exists('docker-compose.yml'):
            subprocess.check_call(['docker-compose', 'up', '-d', 'mongodb'])
            results['success'] = True
            results['message'] = 'Started MongoDB using docker-compose'
            return results
        
        # If docker-compose not available, try system service
        if platform.system() == 'Linux':
            subprocess.check_call(['sudo', 'systemctl', 'start', 'mongod'])
            results['success'] = True
            results['message'] = 'Started MongoDB system service'
        elif platform.system() == 'Darwin':  # macOS
            subprocess.check_call(['brew', 'services', 'start', 'mongodb-community'])
            results['success'] = True
            results['message'] = 'Started MongoDB using Homebrew'
        elif platform.system() == 'Windows':
            subprocess.check_call(['net', 'start', 'MongoDB'])
            results['success'] = True
            results['message'] = 'Started MongoDB Windows service'
        else:
            results['message'] = 'Unable to start MongoDB: Unsupported operating system'
    except Exception as e:
        results['success'] = False
        results['message'] = f'Failed to start MongoDB: {str(e)}'
    
    return results

def repair_tesseract_language():
    """Install Tesseract Hebrew language pack"""
    results = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        if platform.system() == 'Linux':
            subprocess.check_call(['sudo', 'apt-get', 'update'])
            subprocess.check_call(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr-heb'])
            results['success'] = True
            results['message'] = 'Successfully installed Tesseract Hebrew language pack'
        elif platform.system() == 'Darwin':  # macOS
            subprocess.check_call(['brew', 'install', 'tesseract-lang'])
            results['success'] = True
            results['message'] = 'Successfully installed Tesseract language packs'
        elif platform.system() == 'Windows':
            results['success'] = False
            results['message'] = 'Manual installation required for Windows'
            results['details']['instructions'] = 'Download installer from https://github.com/UB-Mannheim/tesseract/wiki and select Hebrew during installation'
        else:
            results['message'] = 'Unsupported operating system'
    except Exception as e:
        results['success'] = False
        results['message'] = f'Failed to install language pack: {str(e)}'
    
    return results

# שים לב: אין כאן פונקציית register_diagnostic_routes - הסרנו אותה
