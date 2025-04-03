#!/bin/bash

echo "===== Synchronizing Git Branches ====="

# 1. First verify current status
current_branch=$(git branch --show-current)
echo "Current branch: $current_branch"
git status

# 2. Make sure all current changes are committed
if [ -n "$(git status --porcelain)" ]; then
    echo -e "\nYou have uncommitted changes. Commit them first? [y/N]"
    read -r commit_response
    
    if [[ $commit_response =~ ^[Yy]$ ]]; then
        git add .
        echo "Enter commit message:"
        read -r commit_message
        git commit -m "$commit_message"
    else
        echo "Uncommitted changes exist. Please commit or stash them before continuing."
        exit 1
    fi
fi

# 3. Synchronize master and main branches
echo -e "\n===== Synchronizing master and main branches ====="

# First make sure we have the latest from remote
echo "Fetching latest from remote..."
git fetch origin

# Sync master branch
echo -e "\nSynchronizing master branch..."
git checkout master
git pull origin master

# Sync main branch
echo -e "\nSynchronizing main branch..."
git checkout main || git checkout -b main
git pull origin main || echo "No remote main branch or failed to pull"

# 4. Merge changes between branches
echo -e "\n===== Merging branches ====="

# First check if main is ahead of master
git checkout master
ahead_count=$(git rev-list --count master..main)

if [ "$ahead_count" -gt 0 ]; then
    echo "main branch is $ahead_count commits ahead of master."
    echo "Merging main into master..."
    git merge main -m "Merge main branch into master"
else
    echo "main branch is not ahead of master. No need to merge from main."
fi

# Now check if master is ahead of main
git checkout main
ahead_count=$(git rev-list --count main..master)

if [ "$ahead_count" -gt 0 ]; then
    echo "master branch is $ahead_count commits ahead of main."
    echo "Merging master into main..."
    git merge master -m "Merge master branch into main"
else
    echo "master branch is not ahead of main. No need to merge from master."
fi

# 5. Push changes to remote
echo -e "\n===== Pushing changes to remote ====="
git checkout master
echo "Pushing master branch..."
git push origin master

git checkout main
echo "Pushing main branch..."
git push origin main

# 6. Return to original branch
echo -e "\n===== Returning to original branch ====="
git checkout "$current_branch"

echo -e "\n===== Branch Synchronization Complete ====="
echo "Both master and main branches should now be in sync."

# 7. Show final status
echo -e "\nFinal status:"
git log --graph --oneline --decorate --all -n 10
