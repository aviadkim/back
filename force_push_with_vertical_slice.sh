#!/bin/bash

echo "===== Force Pushing Vertical Slice Architecture to GitHub ====="

# 1. Make sure we have a clean environment for sensitive data
echo "Creating clean .env file..."
cp .env .env.backup 2>/dev/null || true
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

# 2. Add only important files we want to push
echo "Adding key vertical slice architecture files and document QA features..."

# The already committed files
echo "Previously committed vertical slice implementation files are already tracked"

# Project organized directory with the vertical slice implementation
echo "Adding project_organized directory..."
git add project_organized/

# Document Q&A files
echo "Adding document Q&A files..."
git add quick_qa_test.py
git add run_with_real_pdf.sh
git add comprehensive_qa_test.py 2>/dev/null || true
git add test_qa_feature.py 2>/dev/null || true
git add debug_api_keys.py 2>/dev/null || true
git add analyze_qa_results.py 2>/dev/null || true

# Add README with proper documentation
echo "Adding documentation..."
git add README.md

# Commit additional changes
echo "Committing additional vertical slice and document QA files..."
git commit -m "feat: Add document QA feature and project organization"

# Force push only if explicitly confirmed
echo ""
echo "⚠️  WARNING: You are about to force push these changes to GitHub."
echo "This will overwrite the remote branch with your local changes."
echo ""
echo "Type 'push' to confirm force push to GitHub: "
read confirmation

if [ "$confirmation" = "push" ]; then
    echo "Force pushing to GitHub..."
    git push -f origin main
    echo "✅ Force push complete!"
else
    echo "Force push aborted."
    echo "You can push manually when ready with: git push -f origin main"
fi

echo ""
echo "===== Process Complete ====="
echo "Your clean vertical slice architecture implementation should now be on GitHub!"
