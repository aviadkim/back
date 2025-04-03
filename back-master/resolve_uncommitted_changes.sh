#!/bin/bash

echo "===== Resolving Uncommitted Changes ====="

# 1. Show current status
echo "Current git status:"
git status

# 2. Ask what to do with uncommitted changes
echo -e "\nWhat would you like to do with uncommitted changes?"
echo "1) Commit them (recommended)"
echo "2) Stash them (retrieve later with git stash pop)"
echo "3) Discard them (cannot be recovered!)"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "Committing changes..."
        echo "Enter a commit message (or press Enter for default message):"
        read commit_message
        
        if [ -z "$commit_message" ]; then
            commit_message="WIP: Save changes before branch synchronization"
        fi
        
        # Add all changes and commit
        git add .
        git commit -m "$commit_message"
        echo "✅ Changes committed successfully"
        ;;
    2)
        echo "Stashing changes..."
        git stash save "Changes stashed before branch synchronization"
        echo "✅ Changes stashed successfully"
        echo "You can retrieve them later with: git stash pop"
        ;;
    3)
        echo "⚠️  WARNING: This will PERMANENTLY DISCARD all changes!"
        read -p "Are you sure? Type 'yes' to confirm: " confirm
        
        if [ "$confirm" = "yes" ]; then
            git reset --hard
            echo "✅ Changes discarded"
        else
            echo "Operation cancelled"
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Now run the fix_branch_divergence script
echo -e "\n===== Now running branch divergence fix ====="
./fix_branch_divergence.sh

echo -e "\n===== Process Complete ====="
echo "You can now proceed with your work."
