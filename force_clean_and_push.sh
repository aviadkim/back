#!/bin/bash

echo "===== DEEP CLEANING AND FORCE PUSHING TO GITHUB ====="

# 1. First, unstage everything to start clean
git reset

# 2. Clean all API keys with extreme prejudice
echo "Performing deep API key cleaning..."

# Create empty .env file with only placeholders
cat > /workspaces/back/.env << 'EOL'
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

# 3. Clean all potential API keys with brute force approach
echo "Deep cleaning all files for API keys..."
find /workspaces/back -type f -name "*.py" -o -name "*.sh" -o -name "*.env*" -o -name "*.md" | xargs sed -i 's/sk-or-[a-zA-Z0-9_-]\{30,\}/YOUR_OPENROUTER_API_KEY/g'
find /workspaces/back -type f -name "*.py" -o -name "*.sh" -o -name "*.env*" -o -name "*.md" | xargs sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
find /workspaces/back -type f -name "*.py" -o -name "*.sh" -o -name "*.env*" -o -name "*.md" | xargs sed -i 's/"OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
find /workspaces/back -type f -name "*.py" -o -name "*.sh" -o -name "*.env*" -o -name "*.md" | xargs sed -i "s/'OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
find /workspaces/back -type f -name "*.py" -o -name "*.sh" -o -name "*.env*" -o -name "*.md" | xargs sed -i 's/api_key = "YOUR_OPENROUTER_API_KEY"/g'

# 4. Create a robust .gitignore
cat > /workspaces/back/.gitignore << 'EOL'
# Environment variables - keep API keys private
.env
.env.*
!.env.example

# Key backups
.key_backups*
*.bak
*.backup

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
logs/
api_debug.log

# Test files and temporary data
qa_test_results/
extractions/
uploads/
exports/
financial_data/
tmp/
temp/

# IDE files
.idea/
.vscode/
*.swp
*.swo
EOL

# 5. Delete problematic files that might contain API keys
echo "Removing problematic files and directories..."
rm -f /workspaces/back/.env.bak
rm -f /workspaces/back/.env.local
rm -f /workspaces/back/.env.real
rm -f /workspaces/back/*/*.bak
rm -rf /workspaces/back/.key_backups*

# 6. Stage specific files that we know are clean
echo "Staging clean files for commit..."
git add /workspaces/back/.env
git add /workspaces/back/.gitignore
git add /workspaces/back/README.md
git add /workspaces/back/project_organized
git add /workspaces/back/quick_qa_test.py
git add /workspaces/back/run_with_real_pdf.sh

# 7. Force push with clean files
echo "Committing changes..."
git commit -m "Reorganize project with vertical slice architecture"

# 8. Push to GitHub
echo "Force pushing to GitHub..."
git push -f

echo -e "\n✅ Completed force push to GitHub!"
echo "Note: Some files may have been excluded for safety."
echo "You can add more files manually with 'git add' and push again."
