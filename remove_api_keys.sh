#!/bin/bash

echo "===== Removing API Keys from Code Files ====="

# Create a backup directory for original files
BACKUP_DIR="/workspaces/back/.key_backups_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Function to clean API keys from a file
clean_file() {
    local file=$1
    
    # Skip if file is in .git directory or is a binary file
    if [[ "$file" == *".git/"* ]] || [[ "$(file -b --mime-type "$file" 2>/dev/null)" == "application/octet-stream" ]]; then
        return
    fi
    
    # Create backup
    cp "$file" "$BACKUP_DIR/$(basename "$file")"
    
    # Replace OpenRouter API keys (YOUR_OPENROUTER_API_KEY
    sed -i 's/sk-or-[a-zA-Z0-9][a-zA-Z0-9]*[^"'\''[:space:]]*/YOUR_OPENROUTER_API_KEY/g' "$file"
    
    # Replace another OpenRouter API key format
    sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY "$file"
    
    # Replace any other API key patterns
    sed -i 's/AIza[A-Za-z0-9_\-][A-Za-z0-9_\-]*/YOUR_GEMINI_API_KEY/g' "$file"
    sed -i 's/hf_[A-Za-z0-9][A-Za-z0-9]*/YOUR_HUGGINGFACE_API_KEY/g' "$file"
    
    # Fix broken strings in code that may have been introduced by previous sed commands
    sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY/g' "$file"
    sed -i 's/openrouter_api_key = "YOUR_OPENROUTER_API_KEY/openrouter_api_key = "YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY/g' "$file"
    sed -i 's/api_key = "YOUR_OPENROUTER_API_KEY/api_key = "YOUR_OPENROUTER_API_KEY/g' "$file"
}

# Process all files with issues in the repository
echo "Processing files with known issues..."
PROBLEMATIC_FILES=(
    "/workspaces/back/run_safe_cleanup.sh"
    "/workspaces/back/verify_clean.sh"
    "/workspaces/back/setup_env.sh"
    "/workspaces/back/debug_api_keys.py"
    "/workspaces/back/project_organized/shared/ai/service.py"
    "/workspaces/back/push_to_github.sh"
    "/workspaces/back/test_real_world_qa.py"
    "/workspaces/back/test_openrouter.py"
    "/workspaces/back/prepare_for_github.sh"
    "/workspaces/back/remove_api_keys.sh"
    "/workspaces/back/force_clean_and_push.sh"
    "/workspaces/back/nuclear_clean.sh"
)

for file in "${PROBLEMATIC_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Cleaning file: $file"
        clean_file "$file"
    fi
done

# Create a clean .env
echo "Creating clean .env file..."
cat > "/workspaces/back/.env" << 'EOL'
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

# Update .gitignore
if [ ! -f "/workspaces/back/.gitignore" ]; then
    echo "Creating .gitignore file..."
    cat > /workspaces/back/.gitignore << 'EOL'
# Environment variables
.env
.env.*
!.env.example

# Key backups
.key_backups*

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

# Test files
qa_test_results/
extractions/
uploads/

# IDE files
.idea/
.vscode/
*.swp
*.swo
EOL
    echo "✅ Created .gitignore file"
fi

echo -e "\n===== API Key Removal Complete ====="
echo "All API keys have been replaced with placeholders."
echo "Original files backed up to: $BACKUP_DIR"
echo "You can now safely commit your changes."
