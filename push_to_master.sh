#!/bin/bash
echo "===== Pushing updated code to GitHub master branch ====="

# Make sure we're on the master branch
echo "Checking current branch..."
current_branch=$(git branch --show-current)
if [ "$current_branch" != "master" ]; then
  echo "Switching to master branch..."
  git checkout master
fi

# Add all changes
echo "Adding all changes to git..."
git add .

# Create a meaningful commit message
echo "Creating commit..."
git commit -m "feat: Fix PDF extraction and file naming
- Fix parenthesis syntax error in enhanced_pdf_processor.py
- Improve document ID extraction and file naming logic
- Add comprehensive test suite for extraction validation
- Fix frontend advanced analysis and custom tables features"

# Push to GitHub master branch
echo "Pushing to GitHub master branch..."
git push origin master

# Check if push was successful
if [ $? -eq 0 ]; then
  echo "✅ Successfully pushed changes to GitHub master branch!"
else
  echo "❌ Failed to push changes. Please check error messages above."
fi
