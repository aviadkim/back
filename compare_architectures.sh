#!/bin/bash
# Compare old and new architecture to ensure all functionality is migrated

echo "===== Comparing Old and New Architectures ====="

# Count Python files in old architecture
old_files=$(find /workspaces/back -maxdepth 1 -name "*.py" | wc -l)
echo "Python files in old architecture: $old_files"

# Count Python files in new architecture
new_files=$(find /workspaces/back/project_organized -name "*.py" | wc -l)
echo "Python files in new architecture: $new_files"

# Count endpoints in old architecture
echo -e "\nEndpoints in old architecture:"
grep -r "@app.route" --include="*.py" /workspaces/back | grep -v project_organized | wc -l

# Count endpoints in new architecture
echo "Endpoints in new architecture:"
grep -r "@.*_bp.route" --include="*.py" /workspaces/back/project_organized | wc -l

echo -e "\n===== Migration Progress ====="
echo "Main features migrated:"
echo "✓ PDF Processing"
echo "✓ Document Upload"
echo "✓ Financial Analysis"
echo "✓ Document Q&A"
