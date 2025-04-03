#!/bin/bash

echo "===== Performing Safe API Key Cleanup ====="

# Make the API key removal script executable
chmod +x /workspaces/back/remove_api_keys.sh

# Run the script to clean API keys from all files
./remove_api_keys.sh

# Update fix_openrouter.sh (not in the list but likely contains keys)
if [ -f "/workspaces/back/fix_openrouter.sh" ]; then
  echo "Cleaning fix_openrouter.sh..."
  sed -i 's/OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEYYOUR_OPENROUTER_API_KEY
fi

# Additional clean up of common API key locations
echo "Performing additional cleanup..."
find /workspaces/back -type f -name "*.py" -o -name "*.sh" | xargs sed -i 's/YOUR_OPENROUTER_API_KEY'

# Reset the push_to_github.sh file because we modified it in this session
echo "Updating push_to_github.sh to ensure it's clean..."
cat > /workspaces/back/push_to_github.sh << 'EOL'
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

# 3. Create a .gitignore file if it doesn't exist
if [ ! -f "/workspaces/back/.gitignore" ]; then
    echo "Creating .gitignore file..."
    cat > /workspaces/back/.gitignore << 'EOL2'
# Environment variables
.env
.env.*
!.env.example

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
logs/
api_debug.log

# Test files
qa_test_results/
extractions/
uploads/

# IDE files
.idea/
.vscode/
*.swp
*.swo
EOL2
    echo "✅ Created .gitignore file"
fi

# 4. Check if git is initialized
if [ ! -d "/workspaces/back/.git" ]; then
    echo "Initializing git repository..."
    git init
    git config --global user.email "your-email@example.com"
    git config --global user.name "Your Name"
fi

# 5. Stage all files
echo "Staging files for commit..."
git add .

# 6. Check for API keys in staged files as final safety check
echo "Performing safety check for API keys in staged files..."
if git diff --cached | grep -E "sk-[a-zA-Z0-9]+" > /dev/null; then
    echo "⚠️  WARNING: Possible API keys found in staged files!"
    echo "Please check your files and remove any API keys before committing."
    exit 1
fi

# 7. Prompt for commit message
echo ""
echo "Enter commit message:"
read commit_message

# 8. Commit changes
echo "Committing changes..."
git commit -m "${commit_message:-'Update project files'}"

# 9. Push to GitHub (if remote is set up)
git_remote=$(git remote)
if [ -n "$git_remote" ]; then
    echo "Pushing to GitHub..."
    git push
else
    echo ""
    echo "No git remote is set up. To push to GitHub, run:"
    echo "git remote add origin https://github.com/username/repo.git"
    echo "git push -u origin master"
fi

echo ""
echo "===== Process Complete ====="
echo "The code is now ready on GitHub! 🚀"
EOL

echo -e "\n===== Cleanup Complete ====="
echo "API keys have been removed from code files."
echo "Now run the push_to_github.sh script again:"
echo "  ./push_to_github.sh"
