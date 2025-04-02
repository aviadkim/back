#!/bin/bash
# Usage: ./migrate_component.sh <source_file> <feature_name> [<target_filename>]

SOURCE=$1
FEATURE=$2
TARGET_FILENAME=${3:-$(basename $SOURCE)}

# Check parameters
if [ -z "$SOURCE" ] || [ -z "$FEATURE" ]; then
  echo "Usage: $(basename $0) <source_file> <feature_name> [<target_filename>]"
  echo "Example: $(basename $0) enhanced_financial_extractor.py financial_analysis/extractors"
  exit 1
fi

# Check if source file exists
if [ ! -f "$SOURCE" ]; then
  echo "Error: Source file '$SOURCE' not found"
  exit 1
fi

# Create feature directory
mkdir -p "project_organized/features/$FEATURE"

# Copy source file
cp "$SOURCE" "project_organized/features/$FEATURE/$TARGET_FILENAME"

# Create __init__.py if it doesn't exist
if [ ! -f "project_organized/features/$FEATURE/__init__.py" ]; then
  echo "\"\"\"$FEATURE Feature\"\"\"" > "project_organized/features/$FEATURE/__init__.py"
fi

echo "✅ Migrated $SOURCE to project_organized/features/$FEATURE/$TARGET_FILENAME"
