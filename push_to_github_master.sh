#!/bin/bash

echo "===== Pushing Project to GitHub Master Branch ====="

# 1. Make sure API keys are removed before pushing
echo "Removing API keys from code..."
if [ -f "/workspaces/back/remove_api_keys.sh" ]; then
    chmod +x /workspaces/back/remove_api_keys.sh
    ./remove_api_keys.sh
else
    echo "API key removal script not found. Creating a clean .env..."
    cat > "/workspaces/back/.env" << 'EOL'
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

# 2. Make all scripts executable for convenience
echo "Making all scripts executable..."
find /workspaces/back -name "*.sh" -exec chmod +x {} \;
find /workspaces/back -name "*.py" -exec grep -l "^#!/usr/bin/env python" {} \; | xargs -r chmod +x

# 3. Check current branch
echo "Checking current git branch..."
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# 4. Switch to master branch if not already on it
if [ "$current_branch" != "master" ]; then
    echo "Switching to master branch..."
    git checkout master || git checkout -b master
fi

# 5. Stage all files
echo "Staging files for commit..."
git add .

# 6. Create a meaningful commit message
echo -e "\nEnter commit message (press Enter to use default):"
read -r commit_message
if [ -z "$commit_message" ]; then
    commit_message="feat: Complete vertical slice architecture implementation with AI document processing"
fi

# 7. Commit changes
echo "Committing changes with message: $commit_message"
git commit -m "$commit_message"

# 8. Push to GitHub
echo "Pushing to GitHub master branch..."
git push origin master

# 9. Check push result and provide next steps
if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub master branch!"
    echo -e "\nNext steps:"
    echo "1. Your code is now available on GitHub"
    echo "2. To deploy the application: ./start_production.sh"
    echo "3. To monitor documents: python document_dashboard.py"
else
    echo "❌ Push failed. You may need to:"
    echo "1. Set up git credentials: git config --global user.email 'you@example.com'"
    echo "2. Configure remote: git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo "3. Try force push if needed: git push -f origin master"
fi

echo -e "\n===== Process Complete ====="
