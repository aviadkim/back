#!/bin/bash

echo "===== Preparing Project for GitHub Push ====="

# 1. Make sure .env is in .gitignore
if ! grep -q "\.env" "/workspaces/back/.gitignore" 2>/dev/null; then
    echo "Adding .env to .gitignore..."
    echo -e "\n# Environment variables\n.env\n.env.*\n!.env.example" >> /workspaces/back/.gitignore
    echo "✅ Added .env to .gitignore"
else
    echo "✅ .env is already in .gitignore"
fi

# 2. Create a safe .env.example file without actual API keys
echo "Creating .env.example file..."
cat > /workspaces/back/.env.example << 'EOL'
# API Keys for External Services
# Replace with your actual API keys
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY
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

# 3. Backup the current .env file with API keys
if [ -f "/workspaces/back/.env" ]; then
    echo "Creating backup of your current .env file..."
    cp /workspaces/back/.env /workspaces/back/.env.local
    echo "✅ Backed up your .env to .env.local"
    echo "⚠️ Note: .env.local will not be pushed to GitHub"
fi

# 4. Check for other sensitive data in the codebase
echo "Checking for potentially exposed API keys in code..."
find /workspaces/back -type f -name "*.py" -o -name "*.js" -o -name "*.sh" | xargs grep -l "sk-or-" || echo "✅ No API keys found in code files"

echo -e "\n===== Preparation Complete ====="
echo "Your project is now ready for GitHub:"
echo "1. Your API keys are stored in .env.local (not tracked by Git)"
echo "2. .env.example is provided for other developers"
echo "3. .env is added to .gitignore"
echo ""
echo "Run these commands to push to GitHub:"
echo "  git add ."
echo "  git commit -m 'Your commit message'"
echo "  git push"
echo ""
echo "⚠️ WARNING: Always verify no sensitive data is being committed before pushing!"
