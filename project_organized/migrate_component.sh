#!/bin/bash
# Usage: ./migrate_component.sh <source_file> <feature_name> [<target_filename>]

SOURCE=$1
FEATURE=$2
TARGET_FILENAME=${3:-$(basename $SOURCE)}

# Create feature directory
mkdir -p project_organized/features/$FEATURE

# Copy source file
cp $SOURCE project_organized/features/$FEATURE/$TARGET_FILENAME

# Create __init__.py if it doesn't exist
if [ ! -f "project_organized/features/$FEATURE/__init__.py" ]; then
  echo "\"\"\"$FEATURE Feature\"\"\"" > project_organized/features/$FEATURE/__init__.py
fi

echo "Migrated $SOURCE to project_organized/features/$FEATURE/$TARGET_FILENAME"
