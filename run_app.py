#!/usr/bin/env python
import os
import sys
import time
import webbrowser
import threading

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("data/embeddings", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Set default AWS environment variables to avoid errors
if 'AWS_ACCESS_KEY_ID' not in os.environ:
    os.environ['AWS_ACCESS_KEY_ID'] = 'codespace_dummy_key'
    
if 'AWS_SECRET_ACCESS_KEY' not in os.environ:
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'codespace_dummy_secret'
    
if 'AWS_REGION' not in os.environ:
    os.environ['AWS_REGION'] = 'us-east-1'

# Set development environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['USE_DYNAMODB'] = 'false'  # Disable DynamoDB in development

# Open browser function
def open_browser():
    time.sleep(2)  # Wait for app to start
    print("\nOpening browser...")
    webbrowser.open('http://localhost:5000')

# Start browser thread
threading.Thread(target=open_browser).start()

# Print startup message
print("Starting application in development mode...")
print("Environment variables configured for local development")
print("Browser will open automatically")

# Import and run application
try:
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)
except Exception as e:
    print(f"Error starting application: {e}")
    sys.exit(1)
