import os
import sys
import importlib
import subprocess
import time
import threading
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def check_python_environment():
    print_header("CHECKING PYTHON ENVIRONMENT")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check virtual environment
    in_venv = sys.prefix != sys.base_prefix
    if in_venv:
        print_success(f"Virtual environment active: {sys.prefix}")
    else:
        print_error("Not running in a virtual environment")
    
    return {
        "in_venv": in_venv
    }

def check_dependencies():
    print_header("CHECKING DEPENDENCIES")
    
    critical_packages = [
        "flask", "pymongo", "python-dotenv", "sqlalchemy",
        "numpy", "pandas", "requests"
    ]
    
    ai_packages = [
        "openai", "langchain", "langchain_openai", 
        "sentence_transformers", "transformers", "huggingface_hub"
    ]
    
    pdf_packages = [
        "pypdf", "pdf2image", "pytesseract"
    ]
    
    results = {
        "critical": {},
        "ai": {},
        "pdf": {}
    }
    
    # Check critical packages
    print("Checking critical packages...")
    for package in critical_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print_success(f"{package} ({version})")
            results["critical"][package] = True
        except ImportError:
            print_error(f"{package} not found")
            results["critical"][package] = False
    
    # Check AI packages
    print("\nChecking AI packages...")
    for package in ai_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print_success(f"{package} ({version})")
            results["ai"][package] = True
        except ImportError:
            print_warning(f"{package} not found")
            results["ai"][package] = False
    
    # Check PDF processing packages
    print("\nChecking PDF processing packages...")
    for package in pdf_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "unknown")
            print_success(f"{package} ({version})")
            results["pdf"][package] = True
        except ImportError:
            print_warning(f"{package} not found")
            results["pdf"][package] = False
    
    return results

def check_mongodb():
    print_header("CHECKING MONGODB CONNECTION")
    
    try:
        from pymongo import MongoClient
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Get MongoDB URI from environment variables
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/financial_documents")
        
        # Try to connect with a short timeout
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.server_info()
        
        print_success(f"MongoDB connection successful: {mongo_uri}")
        db_name = mongo_uri.split("/")[-1].split("?")[0]
        print(f"Database name: {db_name}")
        
        # List collections
        db = client[db_name]
        collections = db.list_collection_names()
        if collections:
            print(f"Collections: {', '.join(collections)}")
        else:
            print_warning("No collections found in database")
        
        return True
    except Exception as e:
        print_error(f"MongoDB connection failed: {str(e)}")
        print_warning("Consider using a cloud MongoDB instance or updating your connection string")
        return False

def check_app_structure():
    print_header("CHECKING APPLICATION STRUCTURE")
    
    # Check key directories
    directories = [
        "agent_framework", "features", "models", "routes", 
        "services", "utils", "frontend/build", "uploads"
    ]
    
    # Check key feature slices
    feature_slices = [
        "features/chatbot", "features/pdf_scanning", 
        "features/document_intake", "features/financial_insights",
        "features/data_extraction", "features/compliance",
        "features/summarization", "features/copilot"
    ]
    
    # Check key files
    key_files = [
        "app.py", ".env", "requirements.txt"
    ]
    
    for directory in directories:
        if os.path.isdir(directory):
            print_success(f"Directory exists: {directory}")
        else:
            print_error(f"Directory missing: {directory}")
    
    print("\nChecking feature slices...")
    for feature in feature_slices:
        if os.path.isdir(feature):
            print_success(f"Feature slice exists: {feature}")
            # Check for key components in each feature
            for component in ["api", "services"]:
                component_path = os.path.join(feature, component)
                if os.path.exists(component_path):
                    print(f"  - Has {component} component")
        else:
            print_warning(f"Feature slice not found: {feature}")
    
    print("\nChecking key files...")
    for file in key_files:
        if os.path.isfile(file):
            print_success(f"File exists: {file}")
        else:
            print_error(f"File missing: {file}")
    
    # Check .env file
    if os.path.isfile(".env"):
        required_env_vars = ["MONGO_URI", "SECRET_KEY", "JWT_SECRET"]
        with open(".env", "r") as f:
            env_content = f.read()
            print("\nChecking .env variables...")
            for var in required_env_vars:
                if var in env_content:
                    print_success(f"Environment variable found: {var}")
                else:
                    print_warning(f"Environment variable missing: {var}")
    
    return True

def check_flask_app():
    print_header("TESTING FLASK APPLICATION")
    
    try:
        import app
        print_success("Flask application imported successfully")
        
        # Check for routes
        if hasattr(app, "app") and hasattr(app.app, "url_map"):
            print("\nRegistered routes:")
            for rule in app.app.url_map.iter_rules():
                methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                print(f"  {rule} [{methods}]")
        else:
            print_error("Could not inspect Flask routes")
        
        return True
    except Exception as e:
        print_error(f"Failed to import Flask application: {str(e)}")
        
        # Try to provide more specific advice based on the error
        error_str = str(e)
        if "No module named" in error_str:
            missing_module = error_str.split("'")[-2]
            print_warning(f"Missing module: {missing_module}")
            print(f"Try installing it with: pip install {missing_module}")
        
        return False

def run_app_in_thread():
    from app import app
    import threading
    
    def run_flask():
        app.run(host='127.0.0.1', port=5000, use_reloader=False)
    
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
    time.sleep(2)  # Give the app time to start
    return thread

def test_api_endpoints():
    print_header("TESTING API ENDPOINTS")
    
    try:
        import requests
        
        # Try to import the app
        try:
            from app import app
            
            # Start the app in a separate thread
            thread = run_app_in_thread()
            
            # Test health endpoint
            try:
                response = requests.get('http://127.0.0.1:5000/health')
                if response.status_code == 200:
                    print_success(f"Health endpoint working: {response.json()}")
                else:
                    print_error(f"Health endpoint returned status code: {response.status_code}")
            except Exception as e:
                print_error(f"Failed to connect to health endpoint: {e}")
            
            # Other endpoint tests...
            
            return True
        except Exception as e:
            print_error(f"Could not import Flask app: {e}")
            return False
            
    except ImportError:
        print_error("Could not import 'requests' module")
        return False

def check_frontend():
    print_header("CHECKING FRONTEND")
    
    # Check if build directory exists
    if os.path.isdir("frontend/build"):
        print_success("Frontend build directory exists")
        
        # Count files in build directory
        build_files = list(Path("frontend/build").rglob("*"))
        print(f"Build directory contains {len(build_files)} files")
        
        # Check for index.html
        if os.path.isfile("frontend/build/index.html"):
            print_success("index.html exists in build directory")
        else:
            print_error("index.html missing from build directory")
        
        # Check for React components
        jsx_files = list(Path("frontend/src").rglob("*.jsx"))
        print(f"Found {len(jsx_files)} React component files (.jsx)")
        
        # List key components
        print("\nKey React components:")
        for jsx_file in jsx_files[:10]:  # Show first 10
            print(f"  - {jsx_file}")
        
        return True
    else:
        print_error("Frontend build directory missing")
        return False

def run_all_checks():
    results = {}
    
    results["python_env"] = check_python_environment()
    results["dependencies"] = check_dependencies()
    results["mongodb"] = check_mongodb()
    results["app_structure"] = check_app_structure()
    results["flask_app"] = check_flask_app()
    results["frontend"] = check_frontend()
    
    # Conditionally run API tests only if Flask app could be imported
    if results["flask_app"]:
        results["api_endpoints"] = test_api_endpoints()
    
    return results

def print_summary(results):
    print_header("TEST SUMMARY")
    
    # Calculate overall health
    critical_components = ["python_env", "app_structure"]
    working_components = sum(1 for component in results if results[component])
    total_components = len(results)
    health_percentage = (working_components / total_components) * 100
    
    # Count installed critical packages
    critical_packages = results.get("dependencies", {}).get("critical", {})
    critical_packages_installed = sum(1 for package in critical_packages if critical_packages[package])
    total_critical_packages = len(critical_packages) if critical_packages else 0
    
    print(f"Application Health: {health_percentage:.1f}%")
    print(f"Working Components: {working_components}/{total_components}")
    print(f"Critical Packages: {critical_packages_installed}/{total_critical_packages}")
    
    # Print advice based on results
    print("\nRecommendations:")
    
    if not results.get("mongodb", False):
        print_warning("- Set up MongoDB using Docker or MongoDB Atlas")
        print("  docker run -d -p 27017:27017 --name mongodb mongo:latest")
        print("  OR update your .env file with a MongoDB Atlas connection string")
    
    missing_critical = [package for package in critical_packages if not critical_packages[package]]
    if missing_critical:
        print_warning(f"- Install missing critical packages: {', '.join(missing_critical)}")
        print(f"  pip install {' '.join(missing_critical)}")
    
    if not results.get("flask_app", False):
        print_warning("- Fix issues with Flask application")
        print("  Check app.py for errors and missing dependencies")
    
    if not results.get("frontend", False):
        print_warning("- Build the frontend")
        print("  cd frontend && npm install && npm run build")
    
    print("\nNext steps to make your app fully functional:")
    print("1. Resolve database connection issues")
    print("2. Install all missing dependencies")
    print("3. Create a minimal working route to test your setup")
    print("4. Run the app with 'python app.py' and access at http://localhost:5000")

if __name__ == "__main__":
    print_header("COMPREHENSIVE APPLICATION TEST")
    print("Testing your Financial Document Analysis System...")
    
    results = run_all_checks()
    print_summary(results)
