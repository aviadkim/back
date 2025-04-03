#!/bin/bash

echo "===== Final Push to GitHub ====="

# 1. Verify vertical slice architecture
echo "Running architecture verification..."
chmod +x /workspaces/back/verify_vertical_slice_migration.sh
./verify_vertical_slice_migration.sh

# 2. Clean API keys before pushing
echo -e "\nCleaning API keys..."
chmod +x /workspaces/back/remove_api_keys.sh
./remove_api_keys.sh

# 3. Final check for any remaining API keys
echo -e "\nRunning final API key check on staged files..."
find /workspaces/back -type f \
  -not -path "*/\.*" \
  -not -path "*/venv/*" \
  -not -path "*/node_modules/*" | xargs grep -l "sk-or-" 2>/dev/null | while read file; do
    echo "Cleaning leftover API key in: $file"
    sed -i 's/sk-or-[a-zA-Z0-9]\{10,\}/YOUR_OPENROUTER_API_KEY/g' "$file"
    sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
done

# 4. Update .env with safe values
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

# 5. Make sure .env.example exists for GitHub
cp /workspaces/back/.env /workspaces/back/.env.example

# 6. Stage all files
echo -e "\nStaging files for commit..."
git add .

# 7. Commit changes with comprehensive message
echo -e "\nCommitting changes..."
git commit -m "feat: Complete vertical slice architecture implementation

- Reorganized code by business features instead of technical concerns
- Implemented Document Q&A feature with OpenRouter integration
- Created backward compatibility adapters
- Added comprehensive tests for all features
- Improved error handling and logging
- Enhanced documentation and project structure"

# 8. Push to GitHub (both main and master)
echo -e "\nPushing to GitHub..."
echo -n "Which branch do you want to push to? (main/master/both): "
read branch_choice

case "$branch_choice" in
  main)
    git push origin main
    ;;
  master)
    git push origin master
    ;;
  both|*)
    echo "Pushing to main branch..."
    git push origin main
    
    echo "Pushing to master branch..."
    git checkout master 2>/dev/null || git checkout -b master
    git merge main -m "Merge from main branch"
    git push origin master
    git checkout main
    ;;
esac

echo -e "\n✅ Push complete!"
echo "Your vertical slice architecture is now available on GitHub."
