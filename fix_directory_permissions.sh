#!/bin/bash

echo "===== Fixing Directory Permissions ====="

# Create essential directories with proper permissions
mkdir -p /workspaces/back/extractions
mkdir -p /workspaces/back/uploads
mkdir -p /workspaces/back/exports
mkdir -p /workspaces/back/financial_data

# Set proper permissions
chmod -R 755 /workspaces/back/extractions
chmod -R 755 /workspaces/back/uploads
chmod -R 755 /workspaces/back/exports
chmod -R 755 /workspaces/back/financial_data

echo "✅ Directory permissions fixed successfully"
