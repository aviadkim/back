#!/bin/bash

echo "===== Fixing Git Upstream Configuration ====="

# Check current branch
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"

# Check remote configuration
echo "Current remote configuration:"
git remote -v

# Check upstream branches for current branch
echo "Current upstream configuration:"
git branch -vv | grep "*"

# Fix the branch upstream configuration
echo "Removing all upstream configurations for current branch..."
git config --unset-all branch.$current_branch.remote
git config --unset-all branch.$current_branch.merge

# Set the correct upstream
echo "Setting correct upstream to origin/$current_branch..."
git branch --set-upstream-to=origin/$current_branch $current_branch

echo "Fixed configuration:"
git branch -vv | grep "*"

# Try pushing now
echo "Attempting to push changes..."
git push origin $current_branch

echo "✅ Process complete!"
echo "If you still have issues, consider using force push:"
echo "  git push -f origin $current_branch"
