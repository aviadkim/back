#!/bin/bash

echo "===== Setting Up AI Integration for Document Processing ====="

# 1. Set up the OpenRouter API key
echo "Setting up API keys..."
if [ ! -f ".env" ] || ! grep -q "OPENROUTER_API_KEY" .env; then
    # Create .env if it doesn't exist
    touch .env
    
    # Add OpenRouter API key
    echo "Please enter your OpenRouter API key (starts with 'sk-or-'):"
    read -r api_key
    
    # Validate key format
    if [[ ! $api_key =~ ^sk-or- ]]; then
        echo "⚠️ Warning: Key doesn't start with 'sk-or-'. This may not be a valid OpenRouter API key."
    fi
    
    # Add to .env file
    echo "OPENROUTER_API_KEY=$api_key" >> .env
    echo "DEFAULT_MODEL=openrouter" >> .env
    echo "OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free" >> .env
    echo "Added OpenRouter API key to .env file"
fi

# 2. Install required Python packages
echo "Installing AI and document processing dependencies..."
pip install --upgrade openai langchain huggingface-hub tabula-py pypdf2 pdf2image pytesseract pandas openai-chat plotly matplotlib

# 3. Create the necessary directories
mkdir -p uploads extractions financial_data qa_results

# 4. Set up shared AI service components
echo "Setting up shared AI components..."

# Make sure the AI service is properly configured
cat > project_organized/shared/ai/config.py << 'EOL'
"""Configuration for AI services"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Model names
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'openrouter')
OPENROUTER_MODEL = os.getenv('OPENROUTER_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
HUGGINGFACE_MODEL = os.getenv('HUGGINGFACE_MODEL', 'google/flan-t5-small')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')

# Application settings
DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
PORT = int(os.getenv('PORT', '5001'))
MAX_UPLOAD_SIZE = os.getenv('MAX_UPLOAD_SIZE', '100MB')
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'heb+eng')
OCR_DPI = int(os.getenv('OCR_DPI', '300'))
EOL

# 5. Create .env.example without real API keys
cat > .env.example << 'EOL'
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

echo "✅ AI Integration setup complete!"
echo "You can now run the application with ./project_organized/start_full_app.sh"
