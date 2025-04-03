#!/bin/bash

echo "===== Restoring Financial Document Data ====="

# Check if there are any backup files with the financial data
if [ -f "/workspaces/back/.env.bak" ]; then
  echo "Found environment backup file, restoring..."
  cp /workspaces/back/.env.bak /workspaces/back/.env
  echo "✅ Restored .env file from backup"
fi

# Check for backups of extraction files
if [ -d "/workspaces/back/extractions" ]; then
  echo "Checking extraction files..."
  # Find any backup extraction files and restore them
  find /workspaces/back/extractions -name "*_backup.json" -exec bash -c 'cp "$0" "${0/_backup.json/.json}"' {} \;
fi

# Check if test documents were affected
if [ -d "/workspaces/back/test_files" ]; then
  echo "Checking test files..."
  find /workspaces/back/test_files -name "*.bak" -exec bash -c 'cp "$0" "${0/.bak/}"' {} \;
fi

echo "✅ Finished restoring data"
echo "If specific files are still missing content, please provide the filenames so I can help restore them properly."
