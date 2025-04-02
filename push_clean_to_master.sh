#!/bin/bash

echo "===== Clean and Push to Master Branch ====="

# 1. First, make sure we're working with clean code (no API keys)
echo "Cleaning API keys from code..."
chmod +x /workspaces/back/remove_api_keys.sh
./remove_api_keys.sh

# 2. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 3. If we're on master, continue. Otherwise, switch to master
if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Switching to master branch..."
    git checkout master 2>/dev/null || git checkout -b master
fi

# 4. Stage all files
echo "Staging files for commit..."
git add .

# 5. Check if API keys are clean
echo "Checking for API keys in staged files..."
if git diff --cached | grep -E "sk-or-v1-[a-zA-Z0-9]{10,}" > /dev/null; then
    echo "⚠️ API keys still found. Running additional cleaning..."
    # Extra cleaning of staged files
    git diff --cached --name-only | while read file; do
        if [ -f "$file" ]; then
            sed -i 's/sk-or-[a-zA-Z0-9]\{20,\}/YOUR_OPENROUTER_API_KEY/g' "$file"
            sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
        fi
    done
    git add .
fi

# 6. Get commit message
echo ""
echo "Enter commit message (or press Enter for default):"
read commit_message
if [ -z "$commit_message" ]; then
    commit_message="feat: Implement vertical slice architecture and document QA"
fi

# 7. Commit changes
echo "Committing changes to master..."
git commit -m "$commit_message"

# 8. Push to master
echo "Pushing to master branch..."
git push -u origin master

echo ""
echo "===== Process Complete ====="
echo "Check GitHub to verify your changes are on the master branch."
