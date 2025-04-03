#!/bin/bash

echo "===== Restoring Financial Document Processor Workspace ====="

# 1. Set up environment variables
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    # Create .env file if it doesn't exist
    if [ -f .env.example ]; then
        cp .env.example .env
    else
        # Create minimal .env if example doesn't exist
        cat > .env << 'EOL'
# API Keys for External Services
# Replace with your actual API keys
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
# HUGGINGFACE_API_KEY=your_huggingface_api_key_here
# GEMINI_API_KEY=your_gemini_api_key_here

# Model Configuration 
DEFAULT_MODEL=openrouter
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
# HUGGINGFACE_MODEL=google/flan-t5-small
# GEMINI_MODEL=gemini-pro

# Application Configuration
DEBUG=true
PORT=5001
MAX_UPLOAD_SIZE=100MB
DEFAULT_LANGUAGE=heb+eng
OCR_DPI=300
EOL
    fi
    echo "Created .env file. Please edit it to add your actual OpenRouter API key."
    echo "⚠️ IMPORTANT: Get an OpenRouter API key from https://openrouter.ai/keys"
fi

# 2. Install project in development mode
echo "Installing project in development mode..."
if [ -f setup.py ]; then
    pip install -e .
else
    # Create minimal setup.py if it doesn't exist
    cat > setup.py << 'EOL'
from setuptools import setup, find_packages

setup(
    name="project_organized",
    version="0.1",
    packages=find_packages(),
)
EOL
    pip install -e .
fi

# 3. Install dependencies
echo "Installing dependencies..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    # Install minimal required packages
    pip install Flask PyPDF2 pdf2image pytesseract pandas python-dotenv openai tabula-py
fi

# 4. Set up project directories
echo "Creating necessary directories..."
mkdir -p uploads extractions exports qa_results financial_data

# 5. Make scripts executable
echo "Making scripts executable..."
find . -name "*.sh" -exec chmod +x {} \; 2>/dev/null || echo "No .sh files found"
find . -name "*.py" -type f -exec grep -l "^#!/usr/bin/env python" {} \; | xargs -r chmod +x 2>/dev/null || echo "No Python scripts found"

echo -e "\n===== Workspace Setup Complete ====="
echo "You can now:"
echo "1. Start the application:       ./start_production.sh"
echo "2. Monitor document processing: python document_dashboard.py"
echo "3. Run tests:                   ./test_full_implementation.sh"
echo "4. View cheat sheet:            ./github_cheatsheet.sh"

# Check if OpenRouter API key is set
if grep -q "OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY" .env; then
    echo -e "\n⚠️  WARNING: API key not set. For best results, edit .env and add your OpenRouter API key."
fi
