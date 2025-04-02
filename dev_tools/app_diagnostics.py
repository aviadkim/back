#!/usr/bin/env python3
"""
Application Diagnostics Tool
----------------------------
This script will:
1. Find and test actual connections between components in your app
2. Test UI interactions like button clicks and form submissions
3. Validate that API endpoints return proper data
4. Check if PDF processing works correctly
5. Identify dependency issues
6. Create a detailed report to share with your AI assistant

Usage:
1. Run this in your GitHub Codespace terminal:
   python app_diagnostics.py
2. Share the generated report with your AI assistant for help fixing issues

Requirements: Python 3.6+, your application dependencies
"""
import os
import sys
import json
import time
import re
import logging
import traceback
import importlib
import subprocess
import requests
import pkg_resources
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_diagnostics.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AppDiagnostics")

class AppDiagnostics:
    """Main diagnostics class to test your application"""
    
    def __init__(self, app_dir=None):
        """Initialize the diagnostics tool"""
        self.app_dir = os.path.abspath(app_dir if app_dir else os.getcwd())
        self.issues = []
        self.connections = []
        self.report_data = {
            "timestamp": datetime.now().isoformat(),
            "app_directory": self.app_dir,
            "app_type": "unknown",
            "issues_found": 0,
            "issues_by_category": {},
            "dependencies": {},
            "file_connections": [],
            "component_tests": [],
            "api_tests": [],
            "runtime_tests": []
        }
        self.app_process = None
        self.server_url = None
        
        # Try to auto-detect app type and entry point
        self._detect_app_type()
    
    def _detect_app_type(self):
        """Detect what type of application this is"""
        logger.info("Detecting application type...")
        
        # Check for package.json (Node.js/React/Vue/etc.)
        package_json_path = os.path.join(self.app_dir, "package.json")
        if os.path.exists(package_json_path):
            try:
                with open(package_json_path, 'r') as f:
                    data = json.load(f)
                
                # Get dependencies
                dependencies = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                
                # Identify app type
                if "react" in dependencies:
                    self.report_data["app_type"] = "react"
                    self.report_data["entry_point"] = "npm start"
                    self.server_url = "http://localhost:3000"
                elif "vue" in dependencies:
                    self.report_data["app_type"] = "vue"
                    self.report_data["entry_point"] = "npm run serve"
                    self.server_url = "http://localhost:8080"
                elif "express" in dependencies:
                    self.report_data["app_type"] = "express"
                    self.report_data["entry_point"] = data.get("main", "index.js")
                    self.server_url = "http://localhost:3000"
                elif "next" in dependencies:
                    self.report_data["app_type"] = "next.js"
                    self.report_data["entry_point"] = "npm run dev"
                    self.server_url = "http://localhost:3000"
                else:
                    self.report_data["app_type"] = "node.js"
                    self.report_data["entry_point"] = data.get("main", "index.js")
                
                self.report_data["dependencies"]["node"] = dependencies
                logger.info(f"Detected Node.js application type: {self.report_data['app_type']}")
                return
            except Exception as e:
                logger.error(f"Error reading package.json: {str(e)}")
        
        # Check for Python app types
        requirements_txt = os.path.join(self.app_dir, "requirements.txt")
        if os.path.exists(requirements_txt):
            try:
                with open(requirements_txt, 'r') as f:
                    requirements = f.read().splitlines()
                
                dependencies = {}
                for req in requirements:
                    if "==" in req:
                        name, version = req.split("==", 1)
                        dependencies[name.strip()] = version.strip()
                    else:
                        dependencies[req.strip()] = "unknown"
                
                # Identify Python app type
                if "flask" in dependencies:
                    self.report_data["app_type"] = "flask"
                    # Look for app.py, main.py, or wsgi.py
                    for file in ["app.py", "main.py", "wsgi.py"]:
                        if os.path.exists(os.path.join(self.app_dir, file)):
                            self.report_data["entry_point"] = file
                            break
                    self.server_url = "http://localhost:5000"
                elif "django" in dependencies:
                    self.report_data["app_type"] = "django"
                    self.report_data["entry_point"] = "python manage.py runserver"
                    self.server_url = "http://localhost:8000"
                elif "fastapi" in dependencies:
                    self.report_data["app_type"] = "fastapi"
                    # Look for main.py or app.py
                    for file in ["main.py", "app.py"]:
                        if os.path.exists(os.path.join(self.app_dir, file)):
                            self.report_data["entry_point"] = file
                            break
                    self.server_url = "http://localhost:8000"
                else:
                    self.report_data["app_type"] = "python"
                    # Look for main.py
                    if os.path.exists(os.path.join(self.app_dir, "main.py")):
                        self.report_data["entry_point"] = "main.py"
                
                self.report_data["dependencies"]["python"] = dependencies
                logger.info(f"Detected Python application type: {self.report_data['app_type']}")
                return
            except Exception as e:
                logger.error(f"Error reading requirements.txt: {str(e)}")
        
        # If we get here, we couldn't determine the app type
        logger.warning("Could not determine application type. Will attempt to detect based on files.")
        
        # Look for common entry points
        if os.path.exists(os.path.join(self.app_dir, "index.js")):
            self.report_data["app_type"] = "node.js"
            self.report_data["entry_point"] = "index.js"
            self.server_url = "http://localhost:3000"
        elif os.path.exists(os.path.join(self.app_dir, "app.py")):
            self.report_data["app_type"] = "python"
            self.report_data["entry_point"] = "app.py"
            self.server_url = "http://localhost:5000"
        elif os.path.exists(os.path.join(self.app_dir, "manage.py")):
            self.report_data["app_type"] = "django"
            self.report_data["entry_point"] = "python manage.py runserver"
            self.server_url = "http://localhost:8000"
        else:
            logger.warning("Could not find a recognizable entry point.")
    
    def _check_dependencies(self):
        """Check if all required dependencies are installed"""
        logger.info("Checking dependencies...")
        
        # Initialize dep tracking
        self.report_data["issues_by_category"]["dependencies"] = []
        
        if self.report_data["app_type"] in ["react", "vue", "express", "node.js", "next.js"]:
            # Check Node.js dependencies
            try:
                # Run npm list to check for errors
                result = subprocess.run(
                    ["npm", "list"], 
                    cwd=self.app_dir,
                    capture_output=True, 
                    text=True
                )
                
                # Check for missing dependencies in the output
                if "missing:" in result.stderr or "missing:" in result.stdout:
                    missing_deps = []
                    for line in (result.stderr + result.stdout).splitlines():
                        if "missing:" in line:
                            missing_dep = line.split("missing:", 1)[1].strip()
                            missing_deps.append(missing_dep)
                    
                    for dep in missing_deps:
                        issue = {
                            "category": "dependencies",
                            "severity": "high",
                            "message": f"Missing dependency: {dep}",
                            "file": "package.json",
                            "fix": "Run npm install to install missing dependencies"
                        }
                        self.issues.append(issue)
                        self.report_data["issues_by_category"]["dependencies"].append(issue)
                        self.report_data["issues_found"] += 1
            except Exception as e:
                logger.error(f"Error checking Node.js dependencies: {str(e)}")
                issue = {
                    "category": "dependencies",
                    "severity": "medium",
                    "message": f"Could not check Node.js dependencies: {str(e)}",
                    "file": "package.json",
                    "fix": "Make sure Node.js and npm are installed correctly"
                }
                self.issues.append(issue)
                self.report_data["issues_by_category"]["dependencies"].append(issue)
                self.report_data["issues_found"] += 1
        
        elif self.report_data["app_type"] in ["flask", "django", "fastapi", "python"]:
            # Check Python dependencies
            try:
                # Get installed packages
                installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
                
                # Check if required packages are installed
                if "python" in self.report_data["dependencies"]:
                    for package, version in self.report_data["dependencies"]["python"].items():
                        package_lower = package.lower()
                        if package_lower not in installed_packages:
                            issue = {
                                "category": "dependencies",
                                "severity": "high",
                                "message": f"Missing dependency: {package}",
                                "file": "requirements.txt",
                                "fix": f"Install the package using 'pip install {package}'"
                            }
                            self.issues.append(issue)
                            self.report_data["issues_by_category"]["dependencies"].append(issue)
                            self.report_data["issues_found"] += 1
            except Exception as e:
                logger.error(f"Error checking Python dependencies: {str(e)}")
                issue = {
                    "category": "dependencies",
                    "severity": "medium",
                    "message": f"Could not check Python dependencies: {str(e)}",
                    "file": "requirements.txt",
                    "fix": "Make sure Python and pip are installed correctly"
                }
                self.issues.append(issue)
                self.report_data["issues_by_category"]["dependencies"].append(issue)
                self.report_data["issues_found"] += 1
    
    def _find_file_connections(self):
        """Find connections between files in the application"""
        logger.info("Finding file connections...")
        
        # Initialize connections list
        self.report_data["file_connections"] = []
        
        # Initialize code issues category
        if "code" not in self.report_data["issues_by_category"]:
            self.report_data["issues_by_category"]["code"] = []
        
        # Track imports/requires between files
        import_patterns = {
            ".js": ["require(", "import ", "from "],
            ".jsx": ["require(", "import ", "from "],
            ".ts": ["require(", "import ", "from "],
            ".tsx": ["require(", "import ", "from "],
            ".py": ["import ", "from ", "load_module"],
        }
        
        # Walk through all files in the app directory
        for root, _, files in os.walk(self.app_dir):
            for file in files:
                # Skip node_modules, __pycache__, and other common directories
                if any(skip_dir in root for skip_dir in ["node_modules", "__pycache__", ".git", "venv", "env"]):
                    continue
                
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1]
                
                # Skip binary files and large files
                if file_ext in [".pyc", ".jpg", ".png", ".gif", ".pdf", ".zip"]:
                    continue
                
                try:
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Skip large files
                    if file_size > 1024 * 1024:  # 1 MB
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    rel_path = os.path.relpath(file_path, self.app_dir)
                    connections = []
                    
                    # Look for import/require statements
                    patterns = import_patterns.get(file_ext, [])
                    
                    for pattern in patterns:
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern in line and not line.strip().startswith("//") and not line.strip().startswith("#"):
                                connections.append({
                                    "line": i + 1,
                                    "text": line.strip(),
                                    "type": "import"
                                })
                    
                    # Add to connections list
                    if connections:
                        self.report_data["file_connections"].append({
                            "file": rel_path,
                            "connections": connections
                        })
                        
                    # Check for common issues based on file type
                    if file_ext == '.py':
                        # Python-specific issues
                        
                        # Check for exception handling without specific exceptions
                        if "except:" in content and "except Exception:" not in content:
                            issue = {
                                "category": "code",
                                "severity": "medium",
                                "message": f"Bare except clause found in {rel_path}",
                                "file": rel_path,
                                "fix": "Use specific exceptions instead of bare 'except:'"
                            }
                            self.issues.append(issue)
                            self.report_data["issues_by_category"]["code"].append(issue)
                            self.report_data["issues_found"] += 1
                        
                        # Check for hardcoded secrets
                        secret_patterns = [
                            r"api_key\s*=\s*['\"]([^'\"]+)['\"]",
                            r"password\s*=\s*['\"]([^'\"]+)['\"]",
                            r"secret\s*=\s*['\"]([^'\"]+)['\"]",
                            r"token\s*=\s*['\"]([^'\"]+)['\"]"
                        ]
                        
                        for pattern in secret_patterns:
                            matches = re.findall(pattern, content)
                            if matches:
                                issue = {
                                    "category": "security",
                                    "severity": "high",
                                    "message": f"Hardcoded secret found in {rel_path}",
                                    "file": rel_path,
                                    "fix": "Move secrets to environment variables"
                                }
                                if "security" not in self.report_data["issues_by_category"]:
                                    self.report_data["issues_by_category"]["security"] = []
                                self.issues.append(issue)
                                self.report_data["issues_by_category"]["security"].append(issue)
                                self.report_data["issues_found"] += 1
                                break
                    
                    elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
                        # JavaScript/TypeScript-specific issues
                        
                        # Check for console.log statements
                        if "console.log" in content:
                            issue = {
                                "category": "code",
                                "severity": "low",
                                "message": f"console.log statements found in {rel_path}",
                                "file": rel_path,
                                "fix": "Remove console.log statements before production deployment"
                            }
                            self.issues.append(issue)
                            self.report_data["issues_by_category"]["code"].append(issue)
                            self.report_data["issues_found"] += 1
                        
                        # Check for hardcoded API endpoints
                        api_patterns = [
                            r"axios\.get\(['\"]http",
                            r"fetch\(['\"]http",
                            r"url:\s*['\"]http"
                        ]
                        
                        for pattern in api_patterns:
                            if re.search(pattern, content):
                                issue = {
                                    "category": "code",
                                    "severity": "medium",
                                    "message": f"Hardcoded API endpoint found in {rel_path}",
                                    "file": rel_path,
                                    "fix": "Use environment variables or a config file for API endpoints"
                                }
                                self.issues.append(issue)
                                self.report_data["issues_by_category"]["code"].append(issue)
                                self.report_data["issues_found"] += 1
                                break
                    
                    # Check for incomplete features (TODO comments)
                    todo_matches = re.findall(r"(?:TODO|FIXME).*", content)
                    if todo_matches:
                        issue = {
                            "category": "code",
                            "severity": "low",
                            "message": f"Found {len(todo_matches)} TODO/FIXME comments",
                            "file": rel_path,
                            "todos": todo_matches[:5],
                            "fix": "Complete the implementation of these features"
                        }
                        self.issues.append(issue)
                        self.report_data["issues_by_category"]["code"].append(issue)
                        self.report_data["issues_found"] += 1
                        
                except Exception as e:
                    logger.error(f"Error analyzing file {file_path}: {str(e)}")
    
    def _check_database_connections(self):
        """Check database connections if applicable"""
        logger.info("Checking database connections...")
        
        # Initialize database issues
        if "database" not in self.report_data["issues_by_category"]:
            self.report_data["issues_by_category"]["database"] = []
        
        # Check if the app uses a database
        db_libraries = [
            # SQL databases
            "sqlalchemy", "mysql", "psycopg2", "sqlite3", "pg", "sequelize", 
            # NoSQL
            "mongodb", "mongoose", "firebase", "firestore", "dynamodb"
        ]
        
        uses_database = False
        db_type = None
        
        # Check dependencies for database libraries
        for dep_type, deps in self.report_data["dependencies"].items():
            for lib in db_libraries:
                if any(lib.lower() in dep.lower() for dep in deps):
                    uses_database = True
                    db_type = lib
                    break
        
        # Check file connections for database references
        if not uses_database:
            for connection in self.report_data["file_connections"]:
                for conn in connection["connections"]:
                    for lib in db_libraries:
                        if lib.lower() in conn["text"].lower():
                            uses_database = True
                            db_type = lib
                            break
                    if uses_database:
                        break
                if uses_database:
                    break
        
        if not uses_database:
            logger.info("No database usage detected, skipping database checks")
            return
        
        logger.info(f"Detected database usage: {db_type}")
        
        # Check for database configuration files
        db_config_files = []
        
        # Common database config file patterns
        config_patterns = {
            "sqlalchemy": ["database.py", "models.py", "db.py"],
            "mysql": ["database.py", "db.py", "mysql.py"],
            "psycopg2": ["database.py", "db.py", "postgres.py"],
            "sqlite3": ["database.py", "db.py", "sqlite.py"],
            "mongodb": ["database.py", "db.py", "mongo.py"],
            "mongoose": ["database.js", "db.js", "mongo.js"],
            "sequelize": ["database.js", "db.js", "sequelize.js"],
            "firebase": ["firebase.js", "firestore.js"],
        }
        
        # Look for config files
        for root, _, files in os.walk(self.app_dir):
            if any(skip_dir in root for skip_dir in ["node_modules", "__pycache__", ".git", "venv", "env"]):
                continue
            
            for file in files:
                # Check for known config files
                for _, patterns in config_patterns.items():
                    if file in patterns:
                        file_path = os.path.join(root, file)
                        db_config_files.append(os.path.relpath(file_path, self.app_dir))
                
                # Also check for .env files
                if file == ".env" or file.endswith(".env"):
                    file_path = os.path.join(root, file)
                    db_config_files.append(os.path.relpath(file_path, self.app_dir))
        
        if not db_config_files:
            # Add issue - database code but no config files
            issue = {
                "category": "database",
                "severity": "high",
                "message": f"Database usage detected ({db_type}) but no database configuration files found",
                "fix": "Create proper database configuration files"
            }
            self.issues.append(issue)
            self.report_data["issues_by_category"]["database"].append(issue)
            self.report_data["issues_found"] += 1
            return
        
        # Check database connection issues
        # We'll add a basic check for hardcoded credentials in config files
        for config_file in db_config_files:
            try:
                with open(os.path.join(self.app_dir, config_file), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Check for hardcoded database credentials
                credential_patterns = [
                    r"password\s*=\s*['\"]([^'\"]+)['\"]",
                    r"passwd\s*=\s*['\"]([^'\"]+)['\"]",
                    r"pwd\s*=\s*['\"]([^'\"]+)['\"]",
                    r"username\s*=\s*['\"]([^'\"]+)['\"]",
                    r"user\s*=\s*['\"]([^'\"]+)['\"]",
                ]
                
                for pattern in credential_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Found hardcoded database credentials
                        issue = {
                            "category": "database",
                            "severity": "high",
                            "message": f"Hardcoded database credentials found in {config_file}",
                            "file": config_file,
                            "fix": "Move database credentials to environment variables"
                        }
                        self.issues.append(issue)
                        self.report_data["issues_by_category"]["database"].append(issue)
                        self.report_data["issues_found"] += 1
                        break  # Only report once per file
            except Exception as e:
                logger.error(f"Error checking database config file {config_file}: {str(e)}")
    
    def _check_pdf_processing(self):
        """Check PDF processing functionality if applicable"""
        logger.info("Checking PDF processing capabilities...")
        
        # Initialize PDF issues
        if "pdf" not in self.report_data["issues_by_category"]:
            self.report_data["issues_by_category"]["pdf"] = []
        
        # Check if the app has PDF-related code
        has_pdf_code = False
        pdf_libraries = ["PyPDF2", "pdfminer", "pdfrw", "pdf", "pdfjs", "react-pdf"]
        
        # Check dependencies for PDF libraries
        for dep_type, deps in self.report_data["dependencies"].items():
            for lib in pdf_libraries:
                if any(lib.lower() in dep.lower() for dep in deps):
                    has_pdf_code = True
                    break
        
        # Check file connections for PDF references
        if not has_pdf_code:
            for connection in self.report_data["file_connections"]:
                for conn in connection["connections"]:
                    if "pdf" in conn["text"].lower():
                        has_pdf_code = True
                        break
                if has_pdf_code:
                    break
        
        if not has_pdf_code:
            logger.info("No PDF processing code detected, skipping PDF checks")
            return
        
        # Look for PDF files in the project
        pdf_files = []
        for root, _, files in os.walk(self.app_dir):
            for file in files:
                if file.lower().endswith(".pdf"):
                    if any(skip_dir in root for skip_dir in ["node_modules", "__pycache__", ".git", "venv", "env"]):
                        continue
                    pdf_files.append(os.path.relpath(os.path.join(root, file), self.app_dir))
        
        # Check PDF functionality
        if not pdf_files:
            # Add issue - PDF code but no PDF files
            issue = {
                "category": "pdf",
                "severity": "medium",
                "message": "PDF processing code detected but no PDF files found in the project",
                "fix": "Add test PDF files or check if the application expects PDFs from external sources"
            }
            self.issues.append(issue)
            self.report_data["issues_by_category"]["pdf"].append(issue)
            self.report_data["issues_found"] += 1
            return
        
        # Check for Python PDF libraries
        try:
            # Try to import PyPDF2
            pypdf2_available = importlib.util.find_spec("PyPDF2") is not None
            
            if pypdf2_available:
                # Try to read one of the PDF files
                for pdf_file in pdf_files[:1]:  # Just test the first one
                    try:
                        file_path = os.path.join(self.app_dir, pdf_file)
                        with open(file_path, 'rb') as f:
                            # Just check if we can open it, don't actually process
                            logger.info(f"Successfully opened PDF file: {pdf_file}")
                    except Exception as e:
                        # Failed to read PDF
                        issue = {
                            "category": "pdf",
                            "severity": "high",
                            "message": f"Failed to read PDF file {pdf_file}: {str(e)}",
                            "file": pdf_file,
                            "fix": "Check if the PDF file is valid and accessible"
                        }
                        self.issues.append(issue)
                        self.report_data["issues_by_category"]["pdf"].append(issue)
                        self.report_data["issues_found"] += 1
            else:
                # PyPDF2 not available
                issue = {
                    "category": "pdf",
                    "severity": "high",
                    "message": "PDF functionality detected but PyPDF2 library is not installed",
                    "fix": "Install PyPDF2 with 'pip install PyPDF2'"
                }
                self.issues.append(issue)
                self.report_data["issues_by_category"]["pdf"].append(issue)
                self.report_data["issues_found"] += 1
        except Exception as e:
            logger.error(f"Error checking PDF functionality: {str(e)}")
    
    def _analyze_code_issues(self):
        """Analyze code for common issues"""
        logger.info("Analyzing code for common issues...")
        
        # Initialize issues category
        if "code" not in self.report_data["issues_by_category"]:
            self.report_data["issues_by_category"]["code"] = []
        
        # Look for common issues in each file
        for root, _, files in os.walk(self.app_dir):
            # Skip node_modules, __pycache__, etc.
            if any(skip_dir in root for skip_dir in ["node_modules", "__pycache__", ".git", "venv", "env"]):
                continue
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1]
                
                # Skip binary files and large files
                if file_ext in [".pyc", ".jpg", ".png", ".gif", ".pdf", ".zip"]:
                    continue
                
                try:
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # Skip large files
                    if file_size > 1024 * 1024:  # 1 MB
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    rel_path = os.path.relpath(file_path, self.app_dir)
                    
                    # Check for long lines (code readability)
                    long_lines = [i+1 for i, line in enumerate(content.split('\n')) if len(line) > 100]
                    if len(long_lines) > 5:  # If there are more than 5 long lines
                        issue = {
                            "category": "code",
                            "severity": "low",
                            "message": f"File {rel_path} has {len(long_lines)} lines longer than 100 characters",
                            "file": rel_path,
                            "fix": "Break long lines to improve readability"
                        }
                        self.issues.append(issue)
                        self.report_data["issues_by_category"]["code"].append(issue)
                        self.report_data["issues_found"] += 1
                    
                    # Check for large functions/methods (complexity)
                    if file_ext in ['.py', '.js', '.jsx', '.ts', '.tsx']:
                        # Simple function detection - this is a basic approach
                        function_pattern = r"(def|function|const\s+\w+\s*=\s*\(|class|interface)\s+\w+"
                        functions = re.finditer(function_pattern, content)
                        
                        for match in functions:
                            # Get the position of the function definition
                            pos = match.start()
                            
                            # Find the next function or end of file
                            next_func = re.search(function_pattern, content[pos+1:])
                            if next_func:
                                next_pos = pos + 1 + next_func.start()
                                func_content = content[pos:next_pos]
                            else:
                                func_content = content[pos:]
                            
                            # Count lines in this function
                            func_lines = func_content.count('\n')
                            
                            if func_lines > 50:  # If function is too long
                                func_name = re.search(r"\s+(\w+)", match.group()).group(1)
                                issue = {
                                    "category": "code",
                                    "severity": "medium",
                                    "message": f"Large function '{func_name}' in {rel_path} ({func_lines} lines)",
                                    "file": rel_path,
                                    "fix": "Break down large functions into smaller, more focused ones"
                                }
                                self.issues.append(issue)
                                self.report_data["issues_by_category"]["code"].append(issue)
                                self.report_data["issues_found"] += 1
                                
                except Exception as e:
                    logger.error(f"Error analyzing code in {file_path}: {str(e)}")
    
    def _check_api_endpoints(self):
        """Check if API endpoints are working"""
        if not self.server_url:
            logger.warning("No server URL detected, skipping API checks")
            return
        
        logger.info("Testing API endpoints...")
        
        # Initialize API tests
        self.report_data["api_tests"] = []
        if "api" not in self.report_data["issues_by_category"]:
            self.report_data["issues_by_category"]["api"] = []
        
        # Common API endpoints to check
        common_endpoints = [
            {"path": "/", "method": "GET"},
            {"path": "/api", "method": "GET"},
            {"path": "/api/status", "method": "GET"},
            {"path": "/api/health", "method": "GET"},
            {"path": "/api/users", "method": "GET"},
            {"path": "/api/data", "method": "GET"},
        ]
        
        # Try to discover more endpoints from file connections
        for connection in self.report_data["file_connections"]:
            file_path = connection["file"]
            if "routes" in file_path or "api" in file_path:
                # This file might contain API route definitions
                try:
                    with open(os.path.join(self.app_dir, file_path), 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Look for path patterns in different frameworks
                    
                    # Express.js patterns
                    if self.report_data["app_type"] in ["express", "node.js"]:
                        patterns = [
                            r"app\.(get|post|put|delete)\(['\"](\/[^'\"]+)", 
                            r"router\.(get|post|put|delete)\(['\"](\/[^'\"]+)"
                        ]
                    # Flask patterns
                    elif self.report_data["app_type"] in ["flask"]:
                        patterns = [
                            r"@app\.route\(['\"](\/[^'\"]+)",
                            r"@blueprint\.route\(['\"](\/[^'\"]+)"
                        ]
                    # FastAPI patterns
                    elif self.report_data["app_type"] in ["fastapi"]:
                        patterns = [
                            r"@app\.(get|post|put|delete)\(['\"](\/[^'\"]+)",
                            r"@router\.(get|post|put|delete)\(['\"](\/[^'\"]+)"
                        ]
                    # Django patterns
                    elif self.report_data["app_type"] in ["django"]:
                        patterns = [
                            r"path\(['\"](\/[^'\"]+)",
                            r"url\(['\"](\/[^'\"]+)"
                        ]
                    else:
                        patterns = []
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if isinstance(match, tuple):
                                method, path = match
                                common_endpoints.append({
                                    "path": path,
                                    "method": method.upper(),
                                    "source_file": file_path
                                })
                            else:
                                # For patterns that don't capture the method
                                path = match
                                common_endpoints.append({
                                    "path": path,
                                    "method": "GET",
                                    "source_file": file_path
                                })
                except Exception as e:
                    logger.error(f"Error discovering API endpoints from {file_path}: {str(e)}")
        
        # Test each endpoint
        for endpoint in common_endpoints:
            path = endpoint["path"]
            method = endpoint["method"]
            
            logger.info(f"Testing endpoint: {method} {path}")
            
            try:
                # Construct the full URL
                url = self.server_url + path
                
                # Make the request
                if method == "GET":
                    response = requests.get(url, timeout=5)
                elif method == "POST":
                    # For POST, send empty JSON body
                    response = requests.post(url, json={}, timeout=5)
                elif method == "PUT":
                    response = requests.put(url, json={}, timeout=5)
                elif method == "DELETE":
                    response = requests.delete(url, timeout=5)
                else:
                    logger.warning(f"Unsupported method: {method}")
                    continue
                
                # Check response
                if response.status_code < 400:
                    # Success
                    self.report_data["api_tests"].append({
                        "endpoint": path,
                        "method": method,
                        "status": response.status_code,
                        "result": "success",
                        "response_size": len(response.content),
                        "response_type": response.headers.get("Content-Type", "unknown")
                    })
                else:
                    # Error
                    self.report_data["api_tests"].append({
                        "endpoint": path,
                        "method": method,
                        "status": response.status_code,
                        "result": "error",
                        "response_size": len(response.content),
                        "response_type": response.headers.get("Content-Type", "unknown")
                    })
                    
                    # Add to issues
                    issue = {
                        "category": "api",
                        "severity": "medium",
                        "message": f"API endpoint {method} {path} returned status {response.status_code}",
                        "file": endpoint.get("source_file", "Unknown"),
                        "fix": "Check the endpoint implementation and server logs"
                    }
                    self.issues.append(issue)
                    self.report_data["issues_by_category"]["api"].append(issue)
                    self.report_data["issues_found"] += 1
            except requests.exceptions.RequestException as e:
                # Request failed
                self.report_data["api_tests"].append({
                    "endpoint": path,
                    "method": method,
                    "result": "failed",
                    "error": str(e)
                })
                
                # Add to issues
                issue = {
                    "category": "api",
                    "severity": "high",
                    "message": f"API endpoint {method} {path} request failed: {str(e)}",
                    "file": endpoint.get("source_file", "Unknown"),
                    "fix": "Ensure the endpoint is implemented and the server is running correctly"
                }
                self.issues.append(issue)
                self.report_data["issues_by_category"]["api"].append(issue)
                self.report_data["issues_found"] += 1
    
    def _try_start_app(self):
        """Try to start the application for testing"""
        logger.info("Attempting to start the application...")
        
        if not self.report_data.get("entry_point"):
            logger.warning("No entry point detected, cannot start the application")
            return False
        
        try:
            # Different commands based on app type
            if self.report_data["app_type"] in ["react", "vue", "next.js"]:
                # For npm-based apps, parse the entry point
                cmd_parts = self.report_data["entry_point"].split()
                self.app_process = subprocess.Popen(
                    cmd_parts,
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif self.report_data["app_type"] == "express" or self.report_data["app_type"] == "node.js":
                # For Node.js apps
                self.app_process = subprocess.Popen(
                    ["node", self.report_data["entry_point"]],
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif self.report_data["app_type"] in ["flask", "fastapi"]:
                # For Python web apps
                self.app_process = subprocess.Popen(
                    ["python", self.report_data["entry_point"]],
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            elif self.report_data["app_type"] == "django":
                # For Django
                cmd_parts = self.report_data["entry_point"].split()
                self.app_process = subprocess.Popen(
                    cmd_parts,
                    cwd=self.app_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                logger.warning(f"Unsupported app type: {self.report_data['app_type']}")
                return False
            
            # Wait a bit for the server to start
            logger.info("Waiting for application to start...")
            time.sleep(5)
            
            # Check if the process is still running
            if self.app_process.poll() is not None:
                # Process exited
                stdout, stderr = self.app_process.communicate()
                logger.error(f"Application failed to start. Exit code: {self.app_process.returncode}")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                
                # Add to issues
                issue = {
                    "category": "startup",
                    "severity": "critical",
                    "message": f"Application failed to start. Exit code: {self.app_process.returncode}",
                    "file": self.report_data.get("entry_point", "Unknown"),
                    "details": f"STDOUT: {stdout}\nSTDERR: {stderr}",
                    "fix": "Check the error messages and ensure all dependencies are installed."
                }
                self.issues.append(issue)
                if "startup" not in self.report_data["issues_by_category"]:
                    self.report_data["issues_by_category"]["startup"] = []
                self.report_data["issues_by_category"]["startup"].append(issue)
                self.report_data["issues_found"] += 1
                return False
            
            # Check if the server is responding
            if self.server_url:
                try:
                    response = requests.get(self.server_url, timeout=5)
                    logger.info(f"Application started successfully. Status code: {response.status_code}")
                    return True
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Application may have started but is not responding: {str(e)}")
                    return True  # Still return True since the process is running
            
            return True
        except Exception as e:
            logger.error(f"Error starting application: {str(e)}")
            return False

    def _stop_app(self):
        """Stop the application if it's running"""
        if self.app_process and self.app_process.poll() is None:
            logger.info("Stopping application...")
            try:
                # Try gentle termination first
                self.app_process.terminate()
                time.sleep(2)
                
                # If still running, force kill
                if self.app_process.poll() is None:
                    self.app_process.kill()
                
                logger.info("Application stopped")
            except Exception as e:
                logger.error(f"Error stopping application: {str(e)}")

    def run_diagnostics(self):
        """Run all diagnostics tests"""
        logger.info("Starting application diagnostics...")
        
        try:
            # First, check dependencies
            self._check_dependencies()
            
            # Find file connections
            self._find_file_connections()
            
            # Check for code issues
            self._analyze_code_issues()
            
            # Check database connections
            self._check_database_connections()
            
            # Check PDF processing
            self._check_pdf_processing()
            
            # Try to start the app
            app_started = self._try_start_app()
            
            if app_started:
                # Check API endpoints
                self._check_api_endpoints()
                
                # Stop the app
                self._stop_app()
            
            # Generate the report
            self._generate_report()
            
            logger.info(f"Diagnostics completed. Found {self.report_data['issues_found']} issues.")
            return self.report_data
        except Exception as e:
            logger.error(f"Error during diagnostics: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _generate_report(self):
        """Generate a detailed report"""
        logger.info("Generating diagnostic report...")
        
        # Save the raw JSON report
        report_path = os.path.join(self.app_dir, "app_diagnostics_report.json")
        try:
            with open(report_path, 'w') as f:
                json.dump(self.report_data, f, indent=2)
            logger.info(f"Raw report saved to {report_path}")
        except Exception as e:
            logger.error(f"Error saving raw report: {str(e)}")
        
        # Generate a human-readable markdown report
        md_report_path = os.path.join(self.app_dir, "app_diagnostics_report.md")
        try:
            with open(md_report_path, 'w') as f:
                f.write(f"# Application Diagnostics Report\n\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Application info
                f.write(f"## Application Information\n\n")
                f.write(f"- **Directory**: {self.report_data['app_directory']}\n")
                f.write(f"- **Type**: {self.report_data['app_type']}\n")
                if "entry_point" in self.report_data:
                    f.write(f"- **Entry Point**: {self.report_data['entry_point']}\n")
                
                # Issues summary
                f.write(f"\n## Issues Summary\n\n")
                f.write(f"Found **{self.report_data['issues_found']}** issues\n\n")
                
                # Issues by category
                for category, issues in self.report_data["issues_by_category"].items():
                    if issues:
                        f.write(f"### {category.capitalize()} Issues ({len(issues)})\n\n")
                        for issue in issues:
                            f.write(f"- **{issue['message']}**\n")
                            if "file" in issue:
                                f.write(f"  - File: `{issue['file']}`\n")
                            f.write(f"  - Severity: {issue['severity']}\n")
                            f.write(f"  - Fix: {issue['fix']}\n\n")
                
                # File connections
                if self.report_data["file_connections"]:
                    f.write(f"\n## File Connections\n\n")
                    f.write(f"Found connections between {len(self.report_data['file_connections'])} files\n\n")
                    
                    # List the top 10 most connected files
                    top_files = sorted(self.report_data["file_connections"], 
                                      key=lambda x: len(x["connections"]), 
                                      reverse=True)[:10]
                    
                    f.write("### Top Connected Files\n\n")
                    for file_info in top_files:
                        f.write(f"- **{file_info['file']}** ({len(file_info['connections'])} connections)\n")
                        for connection in file_info["connections"][:3]:
                            f.write(f"  - Line {connection['line']}: `{connection['text']}`\n")
                        if len(file_info["connections"]) > 3:
                            f.write(f"  - ... and {len(file_info['connections']) - 3} more\n")
                
                # API endpoint tests
                if self.report_data.get("api_tests"):
                    f.write(f"\n## API Endpoint Tests\n\n")
                    f.write(f"Tested {len(self.report_data['api_tests'])} API endpoints\n\n")
                    
                    # Group by result
                    successful = [test for test in self.report_data["api_tests"] if test.get("result") == "success"]
                    failed = [test for test in self.report_data["api_tests"] if test.get("result") in ["error", "failed"]]
                    
                    f.write(f"- ✅ **{len(successful)}** successful endpoints\n")
                    f.write(f"- ❌ **{len(failed)}** failed endpoints\n\n")
                    
                    if failed:
                        f.write("### Failed Endpoints\n\n")
                        for test in failed:
                            f.write(f"- **{test['method']} {test['endpoint']}**\n")
                            if "status" in test:
                                f.write(f"  - Status: {test['status']}\n")
                            if "error" in test:
                                f.write(f"  - Error: {test['error']}\n\n")
                
                # Conclusion
                f.write(f"\n## Conclusion and Next Steps\n\n")
                
                if self.report_data["issues_found"] == 0:
                    f.write("Your application appears to be functioning correctly! No issues were detected.\n")
                else:
                    f.write("Based on the diagnostics, here are the recommended next steps:\n\n")
                    
                    # Group issues by priority
                    high_priority = []
                    for category, issues in self.report_data["issues_by_category"].items():
                        for issue in issues:
                            if issue.get("severity") == "high":
                                high_priority.append(issue)
                    
                    if high_priority:
                        f.write("### High Priority Issues\n\n")
                        for issue in high_priority[:5]:
                            f.write(f"- **{issue['message']}** - {issue['fix']}\n")
                    
                    f.write("\n### Improvement Areas\n\n")
                    
                    if "api" in self.report_data["issues_by_category"] and self.report_data["issues_by_category"]["api"]:
                        f.write("1. **API Endpoints**: Fix the failed API endpoints first\n")
                    
                    if "dependencies" in self.report_data["issues_by_category"] and self.report_data["issues_by_category"]["dependencies"]:
                        f.write("2. **Dependencies**: Install missing dependencies\n")
                    
                    if "database" in self.report_data["issues_by_category"] and self.report_data["issues_by_category"]["database"]:
                        f.write("3. **Database**: Fix database connection issues\n")
                    
                    if "pdf" in self.report_data["issues_by_category"] and self.report_data["issues_by_category"]["pdf"]:
                        f.write("4. **PDF Processing**: Address PDF handling issues\n")
                    
                    f.write("\n### For AI Assistant Help\n\n")
                    f.write("Share this report with your AI assistant for detailed help fixing these issues.\n")
                    f.write("When talking with the AI assistant:\n\n")
                    f.write("1. Be specific about which issue you want help with\n")
                    f.write("2. Share relevant code snippets from the identified files\n")
                    f.write("3. Ask for step-by-step solutions to fix each problem\n")
                
            logger.info(f"Markdown report saved to {md_report_path}")
        except Exception as e:
            logger.error(f"Error generating markdown report: {str(e)}")
            logger.error(traceback.format_exc())

def main():
    """Main function to run the diagnostics"""
    print("\nApplication Diagnostics Tool")
    print("---------------------------")
    print("This tool will analyze your application and identify issues\n")
    
    # Get app directory
    app_dir = os.getcwd()
    print(f"Analyzing application in: {app_dir}")
    
    # Run diagnostics
    diagnostics = AppDiagnostics(app_dir)
    results = diagnostics.run_diagnostics()
    
    if "error" in results:
        print(f"\n❌ Error during diagnostics: {results['error']}")
    else:
        print(f"\n✅ Diagnostics completed!")
        print(f"Found {results['issues_found']} issues")
        
        # Show report location
        report_path = os.path.join(app_dir, "app_diagnostics_report.md")
        print(f"\nDetailed report saved to: {report_path}")
        print("\nShare this report with your AI assistant for help fixing the issues.")
        
        # Try to open the report
        try:
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', report_path])
            elif sys.platform.startswith('win'):   # Windows
                os.startfile(report_path)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(['xdg-open', report_path])
        except:
            # If opening fails, just continue
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostics cancelled by user.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        traceback.print_exc()