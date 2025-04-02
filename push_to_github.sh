#!/bin/bash

echo "===== Preparing and Pushing to GitHub ====="

# 1. Run the prepare script to handle environment variables
echo "Running preparation steps for GitHub..."
chmod +x /workspaces/back/prepare_for_github.sh
./prepare_for_github.sh

# 2. Make sure all scripts are executable
echo "Making all scripts executable..."
find /workspaces/back -name "*.sh" -exec chmod +x {} \;
find /workspaces/back -name "*.py" -type f -exec grep -l "^#!/usr/bin/env python" {} \; | xargs -r chmod +x

# 3. Final safety check for API keys
echo "Performing safety check for API keys..."
if grep -r "sk-or-[a-zA-Z0-9]" --include="*.py" --include="*.sh" --include="*.env" /workspaces/back; then
    echo "⚠️  WARNING: API keys found in files. Running nuclear clean..."
    chmod +x /workspaces/back/nuclear_clean.sh
    ./nuclear_clean.sh
fi

# 4. Stage all files
echo "Staging files for commit..."
git add .

# 5. Check for API keys in staged files
echo "Verifying no API keys in staged files..."
chmod +x /workspaces/back/verify_clean.sh
./verify_clean.sh
if [ $? -ne 0 ]; then
    echo "API keys found in staged files. Please fix them before continuing."
    exit 1
fi

# 6. Configure git if not already configured
if [ -z "$(git config --get user.email)" ]; then
    echo "Configuring git user..."
    git config --global user.email "you@example.com"
    git config --global user.name "Your Name"
    echo "Git configured with default values. You may want to update these."
fi

# 7. Prompt for commit message
echo ""
echo "Enter commit message (or press Enter for default message):"
read commit_message
if [ -z "$commit_message" ]; then
    commit_message="Update project with vertical slice architecture"
fi

# 8. Commit changes
echo "Committing changes..."
git commit -m "$commit_message"

# 9. Push to GitHub if remote is set up
git_remote=$(git remote)
if [ -n "$git_remote" ]; then
    echo "Pushing to GitHub..."
    git push
    echo "✅ Push complete!"
else
    echo ""
    echo "No git remote is set up. To push to GitHub:"
    echo "1. Create a new repository on GitHub"
    echo "2. Run these commands:"
    echo "   git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""
echo "===== Process Complete ====="
