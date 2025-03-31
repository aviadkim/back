#!/bin/bash

# ====================================================================================
# Run script for Financial Document Analysis System with Vertical Slice Architecture
# ====================================================================================

echo -e "\033[1;34m===== Running Financial Document Analysis System (v5.0) =====\033[0m"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "\033[1;31mPython is not installed. Please install Python 3.8 or higher.\033[0m"
    exit 1
fi

# Create necessary directories
echo -e "\033[1;33mCreating necessary directories...\033[0m"
mkdir -p uploads data/embeddings data/templates logs

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo -e "\033[1;33mCreating virtual environment...\033[0m"
    python -m venv venv
    source venv/bin/activate
    echo -e "\033[1;32mVirtual environment created and activated.\033[0m"
else
    source venv/bin/activate
    echo -e "\033[1;32mVirtual environment activated.\033[0m"
fi

# Install basic dependencies if they're not already installed
echo -e "\033[1;33mInstalling basic dependencies...\033[0m"
pip install flask flask-cors python-dotenv pytest

# Check if we need to install additional dependencies
if [ "$1" == "--full" ]; then
    echo -e "\033[1;33mInstalling all dependencies (this may take a while)...\033[0m"
    pip install -r requirements.txt
else
    echo -e "\033[1;33mInstalling minimal dependencies for testing...\033[0m"
    pip install pypdf requests
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\033[1;33mCreating .env file...\033[0m"
    cat > .env << 'EOF'
# General settings
FLASK_ENV=development
PORT=5001

# API keys (dummy values for development)
HUGGINGFACE_API_KEY=dummy_key
MISTRAL_API_KEY=dummy_key
OPENAI_API_KEY=dummy_key
GEMINI_API_KEY=dummy_key

# Database settings
MONGO_URI=mongodb://localhost:27017/financial_documents

# Security settings
SECRET_KEY=dev_secret_key_123
JWT_SECRET=dev_jwt_secret_123

# Language settings
DEFAULT_LANGUAGE=he
DEFAULT_MODEL=gemini
EOF
    echo -e "\033[1;32m.env file created with development settings.\033[0m"
fi

# Run the application
echo -e "\033[1;33mStarting the application...\033[0m"
python vertical_slice_app.py

# Handle exit
trap "echo -e '\033[1;31mApplication stopped\033[0m'; exit" INT TERM EXIT
