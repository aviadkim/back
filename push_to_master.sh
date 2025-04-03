#!/bin/bash

echo "===== Pushing to Master Branch ====="

# 1. First, make sure we're working with clean code (no API keys)
echo "Cleaning API keys from code..."
chmod +x /workspaces/back/prepare_for_github.sh
./prepare_for_github.sh

# 2. Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 3. Switch to master branch if not already there
if [ "$CURRENT_BRANCH" != "master" ]; then
    echo "Switching to master branch..."
    git checkout master
    if [ $? -ne 0 ]; then
        echo "Failed to switch to master branch. Creating it..."
        git checkout -b master
    fi
fi

# 4. Stage all files
echo "Staging files for commit..."
git add .

# 5. Verify no API keys in staged files
chmod +x /workspaces/back/verify_clean.sh
./verify_clean.sh
if [ $? -ne 0 ]; then
    echo "API keys found in staged files. Please fix before continuing."
    exit 1
fi

# 6. Get commit message
echo ""
echo "Enter commit message (or press Enter for default):"
read commit_message
if [ -z "$commit_message" ]; then
    commit_message="feat: Update vertical slice architecture implementation"
fi

# 7. Commit changes
echo "Committing changes to master..."
git commit -m "$commit_message"

# 8. Push to master
echo "Pushing to master branch..."
git push origin master
PUSH_RESULT=$?

# 9. If push fails, offer force push option
if [ $PUSH_RESULT -ne 0 ]; then
    echo "Push failed. Do you want to force push? (y/n)"
    read force_push
    if [ "$force_push" = "y" ]; then
        echo "Force pushing to master..."
        git push -f origin master
    else
        echo "Push aborted. You can push manually later."
    fi
fi

echo ""
echo "===== Process Complete ====="
echo "Check GitHub to verify your changes are on the master branch."
