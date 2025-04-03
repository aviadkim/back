#!/bin/bash

echo "===== Verifying No API Keys in Staged Files ====="

# Check if files are staged
STAGED_FILES=$(git diff --cached --name-only)
if [ -z "$STAGED_FILES" ]; then
    echo "No files are staged for commit. Run 'git add' first."
    exit 1
fi

# Check staged files for API key patterns
API_KEY_FILES=$(git diff --cached | grep -E "sk-or-[a-zA-Z0-9]{10,}|AIza[A-Za-z0-9_\-]{35}|hf_[A-Za-z0-9]{10,}" | wc -l)

if [ "$API_KEY_FILES" -gt 0 ]; then
    echo "❌ WARNING: Possible API keys found in staged files!"
    echo "Run the following command to clean them:"
    echo "  ./remove_api_keys.sh"
    exit 1
else
    echo "✅ No API keys found in staged files."
    echo "You can safely commit your changes."
    echo ""
    echo "To commit and push:"
    echo "  git commit -m 'Your commit message'"
    echo "  git push"
    exit 0
fi
