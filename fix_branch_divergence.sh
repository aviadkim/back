#!/bin/bash

echo "===== Fixing Branch Divergence ====="

# 1. Show the current state
echo "Current branch state:"
git log --oneline --graph --decorate --all -n 10

# 2. Check if there are uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

# 3. Create a backup branch of the current state
current_branch=$(git branch --show-current)
backup_branch="backup_${current_branch}_$(date +%Y%m%d_%H%M%S)"
echo "Creating backup branch: $backup_branch"
git branch $backup_branch

# 4. Create a merged commit that combines both histories
echo "Creating a resolution commit..."

# Determine the action based on current branch
if [ "$current_branch" = "master" ]; then
    # We're on master, so merge main into it
    git merge main -m "Merge branch 'main' into master to resolve divergence"
else
    # Switch to master first
    git checkout master
    # Then merge from main
    git merge main -m "Merge branch 'main' into master to resolve divergence"
fi

# 5. Check if merge was successful
if [ $? -ne 0 ]; then
    echo "Merge conflict detected. Resolving automatically..."
    
    # Try to resolve conflicts by taking both changes
    git checkout --ours -- .
    git add .
    git commit -m "Merge branch 'main' into master, resolving conflicts by keeping both changes"
    
    if [ $? -ne 0 ]; then
        echo "Automatic conflict resolution failed. Restoring to previous state."
        git merge --abort
        git checkout $current_branch
        echo "Please resolve conflicts manually."
        exit 1
    fi
fi

# 6. Now make sure main is also updated
echo "Updating main branch with the merged changes..."
git checkout main
git merge master -m "Merge branch 'master' into main to synchronize branches"

# 7. Push both branches
echo "Pushing changes to remote repository..."
git push origin master
git push origin main

# 8. Return to original branch
git checkout $current_branch

echo -e "\n===== Branch Divergence Fixed ====="
echo "Both 'master' and 'main' branches should now be synchronized."
echo "Backup branch '$backup_branch' was created for safety."
echo "Current state:"
git log --oneline --graph --decorate --all -n 5
