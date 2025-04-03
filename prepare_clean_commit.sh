#!/bin/bash

echo "===== Preparing Clean Commit for GitHub ====="

# 1. Make sure .env is not accidentally committed
cp .env .env.backup 2>/dev/null || true
cp .env.example .env 2>/dev/null || true

# 2. Add only the essential files and directories
echo "Adding essential files and directories..."

# Add all the Python files in project_organized directory
git add project_organized/

# Add specific script files we've been working with
git add quick_qa_test.py run_with_real_pdf.sh
git add README.md
git add MIGRATION_PLAN.md
git add architecture_migration_plan.md

# Add scripts that we've created
git add prepare_for_github.sh
git add push_to_github.sh
git add fix_git_upstream.sh
git add force_push_to_github.sh

# Add the vertical slice architecture implementation
git add *_vertical_slice*
git add migrate_*.sh
git add setup_vertical_slice.sh
git add implement_vertical_slice.sh
git add validate_vertical_slice.sh

# 3. Double check for API keys and sensitive data
echo "Checking for API keys in staged files..."
if git diff --cached | grep -E "sk-[a-zA-Z0-9]{10,}|AIza[A-Za-z0-9_\-]{10,}|hf_[A-Za-z0-9]{10,}" > /dev/null; then
    echo "⚠️ WARNING: Found potential API keys in staged files. Aborting..."
    exit 1
fi

# 4. Show what's being committed
echo -e "\n===== Files Staged for Commit ====="
git diff --cached --name-status

echo -e "\n✅ Ready to commit!"
echo "Run this command to commit the changes:"
echo "  git commit -m \"feat: Implement vertical slice architecture and document Q&A\""
