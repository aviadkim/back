#!/bin/bash

echo "===== Force Pushing to GitHub ====="
echo "⚠️  WARNING: This will overwrite the remote branch with your local changes!"
echo "Press Enter to continue or Ctrl+C to cancel..."
read -r

# Get current branch name
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# Make sure we have all changes committed
echo "Checking for uncommitted changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "There are uncommitted changes. Commit them first:"
    git status
    exit 1
fi

# Force push to origin
echo "Force pushing to origin/$current_branch..."
git push -f origin $current_branch

echo "✅ Force push complete!"
