#!/usr/bin/env python3
"""
Comprehensive Test Suite for Financial Document Processing System
================================================================

This script performs comprehensive testing of the entire system:
- Environment setup and configuration
- PDF processing capabilities
- OCR performance
- Table extraction
- Financial data analysis
- API endpoints
- Frontend interaction
- Database operations

Usage:
    python3 comprehensive_test.py [--verbose] [--api-only] [--pdf-only] [--ui-only]

Requirements:
    - All system dependencies installed
    - API keys configured in .env
    - Test documents in test_documents/ directory
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tests/system_test.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SystemTest")

# Load environment variables
load_dotenv()

# Constants
API_BASE_URL = "http://localhost:5000"
TEST_DOCS_PATH = Path("test_documents")
RESULTS_PATH = Path("test_results")
API_ENDPOINTS = [
    "/api/health",
    "/api/version",
    "/api/upload",
    "/api/documents",
    "/api/analyze",
    "/api/tables",
    "/api/entities"
]
PDF_PROCESSOR_MODULES = [
    "text_extractor",
    "table_extractor",
    "financial_analyzer"
]

# Ensure results directory exists
RESULTS_PATH.mkdir(exist_ok=True)

class SystemTester:
    """Main test orchestrator."""

    def __init__(self, args):
        self.verbose = args.verbose
        self.api_only = args.api_only
        self.pdf_only = args.pdf_only
        self.ui_only = args.ui_only
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "environment": {},
            "dependencies": {},
            "api_tests": {},
            "pdf_processing": {},
            "database": {},
            "frontend": {},
            "performance": {}
        }

    def run_all_tests(self):
        """Run all system tests."""
        logger.info("Starting comprehensive system test")

        # Run only selected tests based on arguments
        if not self.api_only and not self.pdf_only and not self.ui_only:
            self.test_environment()
            self.test_dependencies()
            self.test_api_endpoints()
            self.test_pdf_processing()
            self.test_database()
            self.test_frontend()
            self.test_performance()
        else:
            if self.api_only:
                self.test_api_endpoints()
            if self.pdf_only:
                self.test_pdf_processing()
            if self.ui_only:
                self.test_frontend()

        # Save results
        self.save_results()

        # Report summary
        self.report_summary()

    def test_environment(self):
        """Test the environment setup."""
        logger.info("Testing environment setup...")

        # Check Python version
        python_version = sys.version
        self.results["environment"]["python_version"] = python_version
        logger.info(f"Python version: {python_version}")

        # Check environment variables
        required_env_vars = [
            "HUGGINGFACE_API_KEY",
            "FLASK_ENV",
            "MONGO_URI"
        ]
        env_status = {}
        for var in required_env_vars:
            value = os.environ.get(var)
            status = bool(value)
            if self.verbose:
                if var.endswith("API_KEY") and value:
                    # Don't log the actual API key
                    display_value = f"{value[:5]}...{value[-5:]}" if len(value) > 10 else "***"
                else:
                    display_value = value
                logger.info(f"Environment variable {var}: {display_value}")
            env_status[var] = status

        self.results["environment"]["env_vars"] = env_status

        # Check directories
        required_dirs = ["pdf_processor", "uploads", "models", "frontend"]
        dir_status = {}
        for directory in required_dirs:
            exists = os.path.isdir(directory)
            dir_status[directory] = exists
            logger.info(f"Directory {directory}: {'exists' if exists else 'missing'}")

        self.results["environment"]["directories"] = dir_status

    def test_dependencies(self):
        """Test if all required dependencies are installed."""
        logger.info("Testing dependencies...")

        # Check Python packages
        try:
            with open("requirements.txt", "r") as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

            package_status = {}
            for req in requirements:
                package_name = req.split("==")[0] if "==" in req else req
                try:
                    # Special handling for packages with different import names
                    import_name = package_name.replace("-", "_")
                    if import_name == 'python_dotenv':
                        import_name = 'dotenv'
                    elif import_name == 'beautifulsoup4':
                        import_name = 'bs4'
                    elif import_name == 'pillow':
                        import_name = 'PIL'
                    elif import_name == 'scikit_learn':
                        import_name = 'sklearn'

                    module = __import__(import_name)
                    package_status[package_name] = True
                    if self.verbose:
                        logger.info(f"Package {package_name}: installed")
                except ImportError:
                    package_status[package_name] = False
                    logger.warning(f"Package {package_name}: missing")

            self.results["dependencies"]["python_packages"] = package_status
        except Exception as e:
            logger.error(f"Error checking dependencies: {str(e)}")
            self.results["dependencies"]["error"] = str(e)

        # Check external tools
        external_tools = ["tesseract", "poppler-utils"] # poppler-utils might not be directly checkable via 'which'
        tools_status = {}

        for tool in external_tools:
            try:
                if tool == "poppler-utils":
                    # Check for pdftotext or pdfinfo instead
                    check_cmd = ["which", "pdftotext"]
                else:
                    check_cmd = ["which", tool]

                result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                status = result.returncode == 0
                tools_status[tool] = status
                logger.info(f"External tool {tool}: {'installed' if status else 'missing'}")
            except Exception as e:
                tools_status[tool] = False
                logger.error(f"Error checking {tool}: {str(e)}")

        self.results["dependencies"]["external_tools"] = tools_status

    def test_api_endpoints(self):
        """Test API endpoints."""
        logger.info("Testing API endpoints...")

        # Start the Flask app if not already running
        try:
            server_status = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
            server_running = True
        except requests.exceptions.ConnectionError:
            logger.info("Server not running, starting Flask app...")
            server_running = False
            # Start server in the background
            # Note: This might not be reliable in all environments.
            # It's better to ensure the server is running independently.
            try:
                subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # Wait for server to start
                time.sleep(10) # Increased wait time
            except Exception as e:
                logger.error(f"Failed to start Flask app: {e}")
                self.results["api_tests"]["error"] = "Failed to start Flask app"
                return

        # Test each endpoint
        endpoint_results = {}
        for endpoint in API_ENDPOINTS:
            if endpoint == "/api/upload":
                # Special case for upload endpoint - needs a file
                test_file = next(TEST_DOCS_PATH.glob("*.pdf"), None)
                if test_file:
                    try:
                        with open(test_file, "rb") as f:
                            response = requests.post(
                                f"{API_BASE_URL}{endpoint}",
                                files={"file": f},
                                data={"language": "auto"}
                            )
                        status = response.status_code
                        endpoint_results[endpoint] = {
                            "status": status,
                            "success": 200 <= status < 300,
                            "response": response.json() if 200 <= status < 300 and 'application/json' in response.headers.get('Content-Type', '') else response.text
                        }
                    except Exception as e:
                        endpoint_results[endpoint] = {
                            "status": None,
                            "success": False,
                            "error": str(e)
                        }
                else:
                    endpoint_results[endpoint] = {
                        "status": None,
                        "success": False,
                        "error": "No test PDF file found"
                    }
            else:
                # Normal GET endpoint
                try:
                    response = requests.get(f"{API_BASE_URL}{endpoint}")
                    status = response.status_code
                    endpoint_results[endpoint] = {
                        "status": status,
                        "success": 200 <= status < 300,
                        "response": response.json() if 200 <= status < 300 and 'application/json' in response.headers.get('Content-Type', '') else response.text
                    }
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "status": None,
                        "success": False,
                        "error": str(e)
                    }

            logger.info(f"API endpoint {endpoint}: {'success' if endpoint_results[endpoint]['success'] else 'failed'}")
            if not endpoint_results[endpoint]['success'] and self.verbose:
                logger.error(f"  Status: {endpoint_results[endpoint].get('status')}, Error: {endpoint_results[endpoint].get('error', 'Unknown error')}, Response: {endpoint_results[endpoint].get('response')}")

        self.results["api_tests"]["endpoints"] = endpoint_results

    def test_pdf_processing(self):
        """Test PDF processing capabilities."""
        logger.info("Testing PDF processing...")

        # Test each module in pdf_processor
        module_results = {}

        # Import modules directly
        try:
            # Adjust imports based on actual project structure
            # Assuming modules are directly under pdf_processor
            from pdf_processor.extraction.text_extractor import PDFTextExtractor
            from pdf_processor.tables.table_extractor import TableExtractor
            from pdf_processor.analysis.financial_analyzer import FinancialAnalyzer

            # Text extraction test
            text_extractor = PDFTextExtractor()
            table_extractor = TableExtractor()
            financial_analyzer = FinancialAnalyzer()

            # Process test documents
            doc_results = {}
            test_files = list(TEST_DOCS_PATH.glob("*.pdf"))
            if not test_files:
                logger.warning("No test PDF files found in test_documents/")
                self.results["pdf_processing"]["error"] = "No test PDF files found"
                return

            for pdf_file in test_files:
                logger.info(f"Processing test document: {pdf_file.name}")

                try:
                    # Extract text
                    start_time = time.time()
                    # Assuming extract_document returns a dict {page_num: {"text": ..., "metadata": ...}}
                    document = text_extractor.extract_document(str(pdf_file))
                    text_time = time.time() - start_time

                    # Check if any text was extracted
                    text_success = bool(document) and any(page.get("text") for page in document.values())

                    # Extract tables
                    start_time = time.time()
                    # Assuming extract_tables returns a dict {page_num: [table_data, ...]}
                    tables = table_extractor.extract_tables(str(pdf_file), None) # Pass None for pages if extracting all
                    table_time = time.time() - start_time

                    # Check if any tables were extracted
                    table_success = bool(tables) and any(tables.values())

                    # Analyze financial content
                    financial_content = False
                    if text_success:
                        for page_num, page_data in document.items():
                            if text_extractor.is_potentially_financial(page_data.get("text", "")):
                                financial_content = True
                                break

                    # Create dataframes from tables for analysis
                    financial_tables = []
                    if table_success:
                        for page_num, page_tables in tables.items():
                            for table in page_tables:
                                # Assuming convert_to_dataframe exists
                                df = table_extractor.convert_to_dataframe(table)
                                if not df.empty:
                                    # Assuming classify_table exists
                                    table_type = financial_analyzer.classify_table(df)
                                    if table_type != "unknown":
                                        financial_tables.append({
                                            "dataframe": df.to_dict(), # Store as dict for JSON serialization
                                            "type": table_type
                                        })

                    # Document result
                    doc_results[pdf_file.name] = {
                        "text_extraction": {
                            "success": text_success,
                            "processing_time": text_time,
                            "page_count": len(document) if document else 0,
                            "text_length": sum(len(page.get("text", "")) for page in document.values()) if document else 0
                        },
                        "table_extraction": {
                            "success": table_success,
                            "processing_time": table_time,
                            "table_count": sum(len(tables[page]) for page in tables) if tables else 0
                        },
                        "financial_analysis": {
                            "contains_financial_content": financial_content,
                            "financial_tables_count": len(financial_tables),
                            "table_types": [table["type"] for table in financial_tables]
                        }
                    }

                    logger.info(f"Document {pdf_file.name} processed successfully")
                    if self.verbose:
                        logger.info(f"  Text extraction: {'success' if text_success else 'failed'}")
                        logger.info(f"  Table extraction: {'success' if table_success else 'failed'}")
                        logger.info(f"  Financial content: {'detected' if financial_content else 'not detected'}")
                        logger.info(f"  Financial tables: {len(financial_tables)}")

                except Exception as e:
                    logger.error(f"Error processing document {pdf_file.name}: {str(e)}")
                    doc_results[pdf_file.name] = {
                        "error": str(e),
                        "success": False
                    }

            module_results["document_processing"] = doc_results

        except ImportError as e:
            logger.error(f"Error importing PDF processing modules: {str(e)}")
            module_results["import_error"] = str(e)
        except Exception as e:
            logger.error(f"Error in PDF processing test: {str(e)}")
            module_results["error"] = str(e)

        self.results["pdf_processing"] = module_results

    def test_database(self):
        """Test database connectivity and operations."""
        logger.info("Testing database connectivity...")

        db_results = {}

        try:
            # Test MongoDB connection
            from pymongo import MongoClient
            from pymongo.errors import ConnectionFailure

            mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/financial_documents")
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

            # Check connection
            try:
                server_info = client.server_info()
                db_results["connection"] = {
                    "success": True,
                    "server_version": server_info.get("version", "unknown")
                }
                logger.info(f"MongoDB connection successful, version: {server_info.get('version', 'unknown')}")
            except ConnectionFailure as e:
                 logger.error(f"MongoDB connection failed: {str(e)}")
                 db_results["connection"] = {"success": False, "error": str(e)}
                 self.results["database"] = db_results
                 return # Cannot proceed without DB connection

            # Check database and collections
            db = client.get_database() # Get default DB from URI or specify name
            collections = db.list_collection_names()
            db_results["collections"] = collections
            logger.info(f"Available collections: {', '.join(collections)}")

            # Test basic operations
            test_collection_name = "system_test_collection"
            test_collection = db.get_collection(test_collection_name)

            # Clean up previous test data if any
            test_collection.delete_many({"test_id": "system_test"})

            # Insert
            insert_result = test_collection.insert_one({
                "test_id": "system_test",
                "timestamp": datetime.now(),
                "status": "testing"
            })

            # Query
            query_result = test_collection.find_one({"test_id": "system_test"})

            # Update
            update_result = test_collection.update_one(
                {"test_id": "system_test"},
                {"$set": {"status": "completed"}}
            )

            # Verify update
            verify_result = test_collection.find_one({"test_id": "system_test"})

            # Delete
            delete_result = test_collection.delete_one({"test_id": "system_test"})

            # Record results
            db_results["operations"] = {
                "insert": bool(insert_result.inserted_id),
                "query": bool(query_result),
                "update": bool(update_result.modified_count),
                "verify": verify_result.get("status") == "completed" if verify_result else False,
                "delete": bool(delete_result.deleted_count)
            }

            logger.info("Database operations test completed")
            if self.verbose:
                for op, success in db_results["operations"].items():
                    logger.info(f"  {op}: {'success' if success else 'failed'}")

            # Clean up test collection
            # db.drop_collection(test_collection_name)

        except Exception as e:
            logger.error(f"Database test error: {str(e)}")
            db_results["error"] = str(e)
            db_results["success"] = False

        self.results["database"] = db_results

    def test_frontend(self):
        """Test frontend functionality."""
        logger.info("Testing frontend...")

        frontend_results = {}

        # Check if frontend directory exists and contains expected files
        try:
            frontend_dir = Path("frontend")
            if not frontend_dir.exists():
                logger.warning("Frontend directory not found")
                frontend_results["directory_exists"] = False
                self.results["frontend"] = frontend_results
                return

            frontend_results["directory_exists"] = True

            # Check for essential files
            essential_files = [
                "package.json",
                "src/App.jsx", # Assuming React with JSX
                "public/index.html"
            ]

            file_status = {}
            for file_path in essential_files:
                path = frontend_dir / file_path
                exists = path.exists()
                file_status[file_path] = exists
                logger.info(f"Frontend file {file_path}: {'exists' if exists else 'missing'}")

            frontend_results["essential_files"] = file_status

            # Check if node_modules exists (indicating npm install was run)
            node_modules = frontend_dir / "node_modules"
            frontend_results["node_modules_exists"] = node_modules.exists()

            # Check if build directory exists (indicating npm build was run)
            build_dir = frontend_dir / "build"
            frontend_results["build_exists"] = build_dir.exists()

            logger.info(f"Frontend dependencies: {'installed' if node_modules.exists() else 'not installed'}")
            logger.info(f"Frontend build: {'exists' if build_dir.exists() else 'not built'}")

            # Try running npm commands if needed and requested
            if self.verbose and not node_modules.exists():
                logger.info("Attempting to install frontend dependencies...")
                try:
                    # Use shell=True on Windows if needed, otherwise False
                    is_windows = sys.platform == "win32"
                    result = subprocess.run(
                        ["npm", "install"],
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=True, # Raise exception on non-zero exit code
                        shell=is_windows
                    )
                    logger.info("npm install completed successfully")
                    frontend_results["npm_install_attempt"] = True
                except subprocess.CalledProcessError as e:
                     logger.error(f"Error running npm install: {e.stderr}")
                     frontend_results["npm_install_attempt"] = False
                     frontend_results["npm_install_error"] = e.stderr
                except Exception as e:
                    logger.error(f"Error running npm install: {str(e)}")
                    frontend_results["npm_install_attempt"] = False
                    frontend_results["npm_install_error"] = str(e)

        except Exception as e:
            logger.error(f"Frontend test error: {str(e)}")
            frontend_results["error"] = str(e)

        self.results["frontend"] = frontend_results

    def test_performance(self):
        """Test system performance."""
        logger.info("Testing performance...")

        performance_results = {}

        # Test PDF processing performance on a sample document
        try:
            # Get the largest PDF for testing
            test_files = list(TEST_DOCS_PATH.glob("*.pdf"))
            if not test_files:
                logger.warning("No test PDF files found for performance testing")
                performance_results["no_test_files"] = True
                self.results["performance"] = performance_results
                return

            # Choose the largest file for performance testing
            test_file = max(test_files, key=lambda f: f.stat().st_size)
            file_size_mb = test_file.stat().st_size / (1024 * 1024)

            logger.info(f"Running performance test on {test_file.name} ({file_size_mb:.2f} MB)")

            # Import modules
            from pdf_processor.extraction.text_extractor import PDFTextExtractor
            from pdf_processor.tables.table_extractor import TableExtractor

            # Initialize extractors
            text_extractor = PDFTextExtractor()
            table_extractor = TableExtractor()

            # Measure text extraction performance
            start_time = time.time()
            document = text_extractor.extract_document(str(test_file))
            text_extraction_time = time.time() - start_time

            # Measure table extraction performance
            start_time = time.time()
            tables = table_extractor.extract_tables(str(test_file), None)
            table_extraction_time = time.time() - start_time

            # Calculate metrics
            page_count = len(document) if document else 0
            text_per_page = sum(len(page.get("text", "")) for page in document.values()) / max(page_count, 1) if document else 0
            table_count = sum(len(tables[page]) for page in tables) if tables else 0

            performance_results["file_info"] = {
                "name": test_file.name,
                "size_mb": file_size_mb,
                "page_count": page_count
            }

            performance_results["metrics"] = {
                "text_extraction_time": text_extraction_time,
                "table_extraction_time": table_extraction_time,
                "text_extraction_time_per_page": text_extraction_time / max(page_count, 1) if page_count > 0 else 0,
                "text_chars_per_page": text_per_page,
                "table_count": table_count
            }

            logger.info(f"Performance test completed in {text_extraction_time + table_extraction_time:.2f} seconds")
            logger.info(f"  Text extraction: {text_extraction_time:.2f} seconds ({performance_results['metrics']['text_extraction_time_per_page']:.2f} sec/page)")
            logger.info(f"  Table extraction: {table_extraction_time:.2f} seconds")
            logger.info(f"  Pages: {page_count}, Tables: {table_count}")

        except Exception as e:
            logger.error(f"Performance test error: {str(e)}")
            performance_results["error"] = str(e)

        self.results["performance"] = performance_results

    def save_results(self):
        """Save test results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = RESULTS_PATH / f"system_test_{timestamp}.json"

        try:
            with open(result_file, "w") as f:
                # Use a custom JSON encoder if necessary for complex objects like DataFrames
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"Test results saved to {result_file}")
        except Exception as e:
            logger.error(f"Error saving test results: {str(e)}")

    def report_summary(self):
        """Report a summary of test results."""
        logger.info("\n" + "="*80)
        logger.info("SYSTEM TEST SUMMARY")
        logger.info("="*80)

        overall_ok = True

        # Environment summary
        env_data = self.results.get("environment", {})
        env_vars = env_data.get("env_vars", {})
        env_status = "OK" if all(env_vars.values()) else "ISSUES FOUND"
        if env_status != "OK": overall_ok = False
        logger.info(f"Environment: {env_status}")
        if not all(env_vars.values()):
            missing_vars = [var for var, status in env_vars.items() if not status]
            logger.info(f"  Missing environment variables: {', '.join(missing_vars)}")

        # Dependencies summary
        deps_data = self.results.get("dependencies", {})
        python_pkgs = deps_data.get("python_packages", {})
        tools = deps_data.get("external_tools", {})
        deps_status = "OK" if all(python_pkgs.values()) and all(tools.values()) else "ISSUES FOUND"
        if deps_status != "OK": overall_ok = False
        logger.info(f"Dependencies: {deps_status}")
        if not all(python_pkgs.values()):
            missing_pkgs = [pkg for pkg, status in python_pkgs.items() if not status]
            logger.info(f"  Missing Python packages: {', '.join(missing_pkgs)}")
        if not all(tools.values()):
            missing_tools = [tool for tool, status in tools.items() if not status]
            logger.info(f"  Missing external tools: {', '.join(missing_tools)}")

        # API endpoints summary
        api_data = self.results.get("api_tests", {})
        endpoints = api_data.get("endpoints", {})
        endpoints_status = "OK" if endpoints and all(ep.get("success", False) for ep in endpoints.values()) else "ISSUES FOUND"
        if endpoints_status != "OK": overall_ok = False
        logger.info(f"API endpoints: {endpoints_status}")
        if not all(ep.get("success", False) for ep in endpoints.values()):
            failed_endpoints = [ep for ep, data in endpoints.items() if not data.get("success", False)]
            logger.info(f"  Failed endpoints: {', '.join(failed_endpoints)}")
        if "error" in api_data:
             logger.info(f"  API Test Error: {api_data['error']}")

        # PDF processing summary
        pdf_data = self.results.get("pdf_processing", {})
        pdf_results = pdf_data.get("document_processing", {})
        pdf_status = "OK" if pdf_results and all("error" not in doc for doc in pdf_results.values()) else "ISSUES FOUND"
        if pdf_status != "OK": overall_ok = False
        logger.info(f"PDF processing: {pdf_status}")
        if not all("error" not in doc for doc in pdf_results.values()):
            failed_docs = [doc for doc, data in pdf_results.items() if "error" in data]
            logger.info(f"  Failed documents: {', '.join(failed_docs)}")
        if "error" in pdf_data:
             logger.info(f"  PDF Processing Error: {pdf_data['error']}")
        if "import_error" in pdf_data:
             logger.info(f"  PDF Import Error: {pdf_data['import_error']}")

        # Database summary
        db_data = self.results.get("database", {})
        db_error = "error" in db_data or not db_data.get("connection", {}).get("success", False)
        db_status = "OK" if not db_error else "ISSUES FOUND"
        if db_status != "OK": overall_ok = False
        logger.info(f"Database: {db_status}")
        if db_error:
            logger.info(f"  Database error: {db_data.get('error', 'Connection failed')}")
        elif db_data.get("operations") and not all(db_data["operations"].values()):
            failed_ops = [op for op, success in db_data["operations"].items() if not success]
            logger.info(f"  Failed DB operations: {', '.join(failed_ops)}")

        # Frontend summary
        frontend = self.results.get("frontend", {})
        frontend_status = "OK" if frontend.get("directory_exists", False) and all(frontend.get("essential_files", {}).values()) else "ISSUES FOUND"
        if frontend_status != "OK": overall_ok = False
        logger.info(f"Frontend: {frontend_status}")
        if not frontend.get("directory_exists", False):
            logger.info("  Frontend directory not found")
        elif not all(frontend.get("essential_files", {}).values()):
            missing_files = [f for f, exists in frontend.get("essential_files", {}).items() if not exists]
            logger.info(f"  Missing frontend files: {', '.join(missing_files)}")
        if "error" in frontend:
             logger.info(f"  Frontend Test Error: {frontend['error']}")

        # Performance summary
        perf = self.results.get("performance", {})
        perf_error = "error" in perf
        perf_status = "OK" if not perf_error else "ISSUES FOUND"
        if perf_status != "OK": overall_ok = False
        logger.info(f"Performance: {perf_status}")
        if not perf_error and "metrics" in perf:
            metrics = perf["metrics"]
            logger.info(f"  Text extraction: {metrics.get('text_extraction_time', 0):.2f} seconds")
            logger.info(f"  Table extraction: {metrics.get('table_extraction_time', 0):.2f} seconds")
        elif perf_error:
            logger.info(f"  Performance Error: {perf['error']}")

        logger.info("="*80)
        logger.info(f"Overall system status: {'OK' if overall_ok else 'ISSUES FOUND'}")
        logger.info("="*80)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run comprehensive system tests for financial document processing")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--api-only", action="store_true", help="Test only API endpoints")
    parser.add_argument("--pdf-only", action="store_true", help="Test only PDF processing")
    parser.add_argument("--ui-only", action="store_true", help="Test only UI components (basic checks, not Selenium)")

    args = parser.parse_args()

    # Create and run tester
    tester = SystemTester(args)
    tester.run_all_tests()


if __name__ == "__main__":
    main()