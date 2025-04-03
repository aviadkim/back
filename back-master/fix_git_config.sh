#!/bin/bash

echo "===== Fixing Git Configuration ====="

# Reset the git remote configuration to prevent multiple values warning
echo "Removing existing remote configuration..."
git remote remove origin

# Add the correct remote (replace with your actual repository URL)
echo "Adding correct remote..."
git remote add origin https://github.com/aviadkim/back.git

# Set the default branch name to 'main'
echo "Setting default branch name to 'main'..."
git branch -m main

# Set up tracking for the main branch
echo "Setting up tracking for main branch..."
git branch --set-upstream-to=origin/main main

echo -e "\n✅ Git configuration fixed!"
echo "You should now be able to use normal git commands without warnings:"
echo "  - git pull"
echo "  - git push"
echo "  - git fetch"

echo -e "\nCurrent remote:"
git remote -v

echo -e "\nCurrent branch status:"
git status
