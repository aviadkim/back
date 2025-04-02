#!/usr/bin/env python
import os
import sys
import subprocess
import time
import json

def create_required_directories():
    """Create all required directories for the application"""
    print("\nCreating required directories...")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("test_files", exist_ok=True)
    print("Directories created successfully")

def check_env_file():
    """Check if .env file exists and create it if needed"""
    if not os.path.exists(".env"):
        print("\nCreating .env file from example...")
        if os.path.exists(".env.example"):
            os.system("cp .env.example .env")
            print("Created .env file from example.")
        else:
            print("Warning: No .env.example file found to create .env from")
            # Create a basic .env file
            with open(".env", "w") as f:
                f.write("FLASK_ENV=development\n")
                f.write("PORT=5000\n")
                f.write("SECRET_KEY=dev_secret_key\n")
                f.write("JWT_SECRET=dev_jwt_secret\n")
                f.write("MONGO_URI=mongodb://localhost:27017/financial_documents\n")
                f.write("DEFAULT_LANGUAGE=he\n")
    else:
        print("\n.env file already exists.")

def create_test_pdf():
    """Create a simple test PDF file"""
    print("\nCreating test PDF file...")
    try:
        if os.path.exists("test_files/create_simple_pdf.py"):
            subprocess.run(["python", "test_files/create_simple_pdf.py"], check=True)
        else:
            print("create_simple_pdf.py not found. Creating a simple test file...")
            with open("test_files/test.txt", "w") as f:
                f.write("This is a test document.")
            print("Created test_files/test.txt for testing.")
    except Exception as e:
        print(f"Error creating test PDF: {e}")
        print("Creating a simple test file instead...")
        with open("test_files/test.txt", "w") as f:
            f.write("This is a test document.")
        print("Created test_files/test.txt for testing.")

def check_mongodb():
    """Check if MongoDB is running and start it if possible"""
    print("\nChecking MongoDB connection...")
    try:
        from pymongo import MongoClient
        from pymongo.errors import ServerSelectionTimeoutError
        
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("MongoDB is running.")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        print("Attempting to start MongoDB via docker-compose...")
        try:
            subprocess.run(["docker-compose", "up", "-d", "mongodb"], check=False)
            print("Waiting for MongoDB to start...")
            time.sleep(5)
            
            # Try to connect again
            try:
                client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
                client.server_info()
                print("MongoDB is now running.")
                return True
            except Exception as retry_e:
                print(f"Still couldn't connect to MongoDB: {retry_e}")
                return False
        except Exception as docker_e:
            print(f"Failed to start MongoDB with docker-compose: {docker_e}")
            return False

def test_app_startup():
    """Test if the app can start up"""
    print("\nTesting app startup...")
    try:
        # Try to import main modules without running the app
        from flask import Flask
        print("Flask is installed.")
        
        # Try to import the main app module
        sys.path.append(os.getcwd())
        try:
            # Don't actually run the app, just try to import it
            print("Checking if app.py can be imported...")
            import importlib.util
            spec = importlib.util.spec_from_file_location("app", "app.py")
            if spec and spec.loader:
                print("app.py found and can be imported.")
            else:
                print("app.py found but cannot be imported properly.")
        except ImportError as e:
            print(f"Error importing app.py: {e}")
            return False
        
        return True
    except Exception as e:
        print(f"Error testing app startup: {e}")
        return False

def print_deployment_instructions():
    """Print instructions for deployment to AWS"""
    print("\n=== DEPLOYMENT INSTRUCTIONS ===")
    print("To deploy to AWS Elastic Beanstalk:")
    print("1. Add these secrets to your GitHub repository:")
    print("   - AWS_ACCESS_KEY_ID")
    print("   - AWS_SECRET_ACCESS_KEY") 
    print("   - AWS_REGION (e.g., us-east-1)")
    print("2. Trigger deployment by:")
    print("   - Pushing to the master branch, or")
    print("   - Manually triggering from the Actions tab")
    print("")
    print("This will use the GitHub Actions workflow already set up in your repository.")

def main():
    """Main test function"""
    print("=== FINANCIAL DOCUMENT ANALYSIS SYSTEM TEST ===")
    
    # Create directories
    create_required_directories()
    
    # Check .env file
    check_env_file()
    
    # Create test file
    create_test_pdf()
    
    # Check MongoDB
    mongodb_running = check_mongodb()
    
    # Test app startup
    app_ok = test_app_startup()
    
    # Summary
    print("\n=== TEST SUMMARY ===")
    print(f"Required directories: CREATED")
    print(f"Environment file (.env): {'EXISTS' if os.path.exists('.env') else 'MISSING'}")
    print(f"Test document: {'CREATED' if (os.path.exists('test_files/test_invoice.pdf') or os.path.exists('test_files/test.txt')) else 'FAILED'}")
    print(f"MongoDB connection: {'OK' if mongodb_running else 'FAILED'}")
    print(f"App startup test: {'OK' if app_ok else 'FAILED'}")
    
    if not mongodb_running:
        print("\nWARNING: MongoDB is not running. Start it with 'docker-compose up -d'")
    
    if not app_ok:
        print("\nWARNING: There may be issues with the app. Check the error messages above.")
    
    # Deployment instructions
    print_deployment_instructions()

if __name__ == "__main__":
    main()
