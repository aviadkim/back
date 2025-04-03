#!/bin/bash

echo "===== Setting up OpenRouter Integration ====="

# Update the .env file with OpenRouter configuration
if [ ! -f "/workspaces/back/.env" ]; then
    echo "Creating new .env file with OpenRouter configuration"
    cat > /workspaces/back/.env << 'EOL'
# API Keys for External Services
# OpenRouter API Key - Get one at https://openrouter.ai/
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

# Model Configuration
DEFAULT_MODEL=openrouter
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free

# Application Configuration
DEBUG=true
PORT=5001
MAX_UPLOAD_SIZE=100MB
DEFAULT_LANGUAGE=heb+eng
OCR_DPI=300
EOL
else
    echo "Updating existing .env file with OpenRouter configuration"
    # Check if OpenRouter key already exists
    if grep -q "OPENROUTER_API_KEY" /workspaces/back/.env; then
        echo "OpenRouter API key already exists in .env file"
    else
        # Add OpenRouter config
        cat >> /workspaces/back/.env << 'EOL'

# OpenRouter API Key - Get one at https://openrouter.ai/
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
EOL
    fi
    
    # Update default model to use OpenRouter
    sed -i 's/DEFAULT_MODEL=.*/DEFAULT_MODEL=openrouter/' /workspaces/back/.env
fi

# Install required packages
echo "Installing required packages..."
pip install python-dotenv requests

# Setup AI module structure
echo "Setting up AI module with OpenRouter integration..."
mkdir -p /workspaces/back/project_organized/shared/ai

# Make test script executable
chmod +x /workspaces/back/test_openrouter.py

echo "✅ OpenRouter integration setup complete!"
echo "Run the test script with: python test_openrouter.py"
