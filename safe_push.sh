#!/bin/bash

echo "===== Safely Pushing to GitHub ====="

# 1. Run API key cleaning
echo "Cleaning API keys from files..."
chmod +x /workspaces/back/remove_api_keys.sh
./remove_api_keys.sh

# 2. Run the nuclear clean as a final precaution
chmod +x /workspaces/back/nuclear_clean.sh
./nuclear_clean.sh

# 3. Stage all files
echo "Staging files for commit..."
git add .

# 4. Verify no API keys in staged files
echo "Verifying no API keys in staged files..."
chmod +x /workspaces/back/verify_clean.sh
./verify_clean.sh
if [ $? -ne 0 ]; then
    echo "API keys found in staged files. Cannot continue."
    exit 1
fi

# 5. Get commit message
echo "Enter commit message:"
read commit_message
if [ -z "$commit_message" ]; then
    commit_message="Update project files"
fi

# 6. Commit and push
echo "Committing and pushing changes..."
git commit -m "$commit_message"
git push

echo -e "\n✅ Successfully pushed to GitHub!"
echo "Your changes are now available at: https://github.com/aviadkim/back"
