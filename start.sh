#!/bin/bash

# =========================================================
# Start script for Financial Documents Analysis System
# =========================================================

echo -e "\033[1;34m===== Starting Financial Documents Analysis System (v4.1) =====\033[0m"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo -e "\033[1;31mPython is not installed. Please install Python 3.8 or higher.\033[0m"
    exit 1
fi

# Check if Node.js is installed (for frontend development if needed)
if ! command -v node &> /dev/null; then
    echo -e "\033[1;33mWarning: Node.js is not installed. Frontend development may not work.\033[0m"
fi

# Create necessary directories
echo -e "\033[1;33mCreating necessary directories...\033[0m"
mkdir -p uploads data/embeddings data/templates logs
mkdir -p features/pdf_scanning features/document_chat features/table_extraction
mkdir -p frontend/build

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

# Install requirements if they're not already installed
echo -e "\033[1;33mInstalling/updating Python dependencies...\033[0m"
pip install -r requirements.txt

# Check if .env file exists, if not create it
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
SECRET_KEY=dev_secret_key_$(date +%s)
JWT_SECRET=dev_jwt_secret_$(date +%s)

# Language settings
DEFAULT_LANGUAGE=he
DEFAULT_MODEL=gemini
EOF
    echo -e "\033[1;32m.env file created with development settings.\033[0m"
fi

# Start MongoDB if it's installed and not running
if command -v docker &> /dev/null; then
    if ! docker ps | grep -q mongodb; then
        echo -e "\033[1;33mStarting MongoDB using Docker...\033[0m"
        docker-compose up -d mongodb
    else
        echo -e "\033[1;32mMongoDB is already running.\033[0m"
    fi
else
    echo -e "\033[1;33mWarning: Docker not found. Make sure MongoDB is running externally.\033[0m"
fi

# Start the application
echo -e "\033[1;33mStarting the application...\033[0m"
python vertical_slice_app.py

# Handle exit
trap "echo -e '\033[1;31mApplication stopped\033[0m'; exit" INT TERM EXIT
