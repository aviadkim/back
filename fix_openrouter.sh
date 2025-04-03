#!/bin/bash

echo "===== Fixing OpenRouter Integration ====="

# 1. Save the existing .env file as backup
if [ -f "/workspaces/back/.env" ]; then
    cp /workspaces/back/.env /workspaces/back/.env.bak
    echo "Created backup of .env file at .env.bak"
fi

# 2. Update the .env file with a working OpenRouter configuration
cat > /workspaces/back/.env << 'EOL'
# API Keys for External Services
# This is a working OpenRouter API key format
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY

# Model Configuration 
DEFAULT_MODEL=openrouter
OPENROUTER_MODEL=deepseek/deepseek-chat-v3-0324:free
HUGGINGFACE_MODEL=google/flan-t5-small
GEMINI_MODEL=gemini-pro

# Application Configuration
DEBUG=true
PORT=5001
MAX_UPLOAD_SIZE=100MB
DEFAULT_LANGUAGE=heb+eng
OCR_DPI=300
EOL

echo "Updated .env file with working OpenRouter configuration"

# 3. Make sure the debug script is executable
chmod +x /workspaces/back/debug_api_keys.py

# 4. Run the debug script to verify the fix
echo -e "\nRunning API debug script to verify the fix..."
python /workspaces/back/debug_api_keys.py

echo -e "\n===== Fix Complete ====="
echo "If issues persist, try signing up for a new OpenRouter API key at: https://openrouter.ai/"
echo "Then update your .env file with the new key."
