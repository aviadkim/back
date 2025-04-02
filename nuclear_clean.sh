#!/bin/bash

echo "===== FINAL API KEY CLEANUP - NUCLEAR OPTION ====="

# This is the nuclear option that will find and replace any API key patterns
# regardless of context, to ensure no keys are accidentally committed

# API key patterns
PATTERNS=(
  "sk-or-[a-zA-Z0-9]\{20,\}"
  "sk-[a-zA-Z0-9]\{20,\}"
  "AIza[A-Z0-9_\-]\{30,\}"
  "hf_[a-zA-Z0-9]\{20,\}"
)

# Clean all staged files
STAGED_FILES=$(git diff --cached --name-only)

if [ -z "$STAGED_FILES" ]; then
    echo "No files are staged. Please run 'git add' first."
    exit 1
fi

echo "Cleaning staged files..."
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        echo "Cleaning $file..."
        
        # Check file type to avoid binary files
        if file "$file" | grep -q "text"; then
            for pattern in "${PATTERNS[@]}"; do
                # Replace API keys with placeholder
                sed -i "s/$pattern/YOUR_API_KEY_PLACEHOLDER/g" "$file"
            done
        fi
    fi
done

# Check for specific strings in debug_api_keys.py and service.py
for file in "/workspaces/back/debug_api_keys.py" "/workspaces/back/project_organized/shared/ai/service.py"; do
    if [ -f "$file" ]; then
        echo "Special handling for $file..."
        # Replace any line containing API key assignment
        sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY
        sed -i 's/api_key = "YOUR_OPENROUTER_API_KEY"
    fi
done

# Also fix any unstaged files
echo "Also checking unstaged files for remaining keys..."
git ls-files -o --exclude-standard | while read file; do
    if [ -f "$file" ] && file "$file" | grep -q "text"; then
        for pattern in "${PATTERNS[@]}"; do
            sed -i "s/$pattern/YOUR_API_KEY_PLACEHOLDER/g" "$file"
        done
    fi
done

# Update .env file with safe values
if [ -f "/workspaces/back/.env" ]; then
    echo "Cleaning .env file..."
    cp "/workspaces/back/.env" "/workspaces/back/.env.real"
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
    echo "Original API keys saved in .env.real, safe version in .env"
fi

echo -e "\n✅ Nuclear cleaning complete!"
echo "Verify with: ./verify_clean.sh"
echo "If any API keys remain, they will be detected when you try to commit."
