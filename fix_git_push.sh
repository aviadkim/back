#!/bin/bash

echo "===== Fixing Git Push Issues and Pushing to GitHub ====="

# 1. Check current status and branch
echo "Current branch and status:"
git branch
current_branch=$(git branch --show-current)
echo "Current status:"
git status

# 2. Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "\nUncommitted changes found. Adding all changes..."
    git add .
    
    echo "Enter commit message (or press Enter for default message):"
    read -r commit_message
    if [ -z "$commit_message" ]; then
        commit_message="Complete vertical slice architecture implementation"
    fi
    
    git commit -m "$commit_message"
    echo "Changes committed."
else
    echo -e "\nNo uncommitted changes found."
fi

# 3. Check remote configuration
echo -e "\nChecking remote configuration:"
git remote -v

if [ -z "$(git remote)" ]; then
    echo "No remote repository configured."
    echo "Please enter your GitHub username:"
    read -r github_user
    
    echo "Please enter your repository name (default: financial-document-processor):"
    read -r repo_name
    if [ -z "$repo_name" ]; then
        repo_name="financial-document-processor"
    fi
    
    echo "Adding remote repository..."
    git remote add origin "https://github.com/$github_user/$repo_name.git"
    echo "Remote repository added."
fi

# 4. Check which branches exist on remote
echo -e "\nFetching remote branch information..."
git fetch

# 5. Push to appropriate branch
echo -e "\nPushing to remote repository..."

# First try normal push to current branch
echo "Attempting to push to current branch ($current_branch)..."
push_result=$(git push origin $current_branch 2>&1)
push_status=$?

if [ $push_status -eq 0 ]; then
    echo "✅ Successfully pushed to $current_branch!"
else
    echo "Push to $current_branch failed. Error:"
    echo "$push_result"
    
    # Check if we're on main but need to push to master or vice versa
    if [ "$current_branch" = "main" ]; then
        echo -e "\nYou're on 'main' branch. Trying to push to 'master' branch..."
        git branch -f master main
        git push origin master
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed to master branch!"
        else
            echo "❌ Push to master also failed."
        fi
    elif [ "$current_branch" = "master" ]; then
        echo -e "\nYou're on 'master' branch. Trying to push to 'main' branch..."
        git branch -f main master
        git push origin main
        if [ $? -eq 0 ]; then
            echo "✅ Successfully pushed to main branch!"
        else
            echo "❌ Push to main also failed."
        fi
    fi
    
    # If all else fails, offer force push option
    echo -e "\nWould you like to try force push? (THIS WILL OVERWRITE REMOTE CHANGES) [y/N]"
    read -r force_push
    if [[ $force_push =~ ^[Yy]$ ]]; then
        echo "Force pushing to $current_branch..."
        git push -f origin $current_branch
        if [ $? -eq 0 ]; then
            echo "✅ Force push successful!"
        else
            echo "❌ Force push failed."
        fi
    fi
fi

echo -e "\n===== Git Push Operation Complete ====="
echo "If you're still having issues, please check GitHub access permissions"
echo "or set up SSH authentication for more reliable pushing."
