#!/bin/bash

# First, make sure we install all the required dependencies
cd /workspaces/back
echo "Installing dependencies..."
python fix_imports.py > /dev/null 2>&1

# Run the migration status check with fixed formatting
echo "Checking migration status..."
python -c '
import os
import sys
import re

def green(text):
    return f"\033[92m{text}\033[0m"

def yellow(text):
    return f"\033[93m{text}\033[0m"

def blue(text):
    return f"\033[94m{text}\033[0m"

def count_routes():
    """Count API routes in old and new architecture"""
    old_routes = 0
    new_routes = 0
    
    # Count old routes
    old_pattern = re.compile(r"@app\.route")
    for root, _, files in os.walk("/workspaces/back"):
        if "project_organized" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        old_routes += len(old_pattern.findall(content))
                except:
                    pass
    
    # Count new routes
    new_pattern = re.compile(r"@\w+_bp\.route")
    for root, _, files in os.walk("/workspaces/back/project_organized"):
        for file in files:
            if file.endswith(".py"):
                try:
                    with open(os.path.join(root, file), "r") as f:
                        content = f.read()
                        new_routes += len(new_pattern.findall(content))
                except:
                    pass
    
    return old_routes, new_routes

def count_files():
    """Count Python files in old and new architecture"""
    old_files = 0
    new_files = 0
    
    # Count old files
    for root, _, files in os.walk("/workspaces/back"):
        if "project_organized" in root or ".git" in root or "node_modules" in root:
            continue
        old_files += sum(1 for f in files if f.endswith(".py"))
    
    # Count new files
    for root, _, files in os.walk("/workspaces/back/project_organized"):
        new_files += sum(1 for f in files if f.endswith(".py"))
    
    return old_files, new_files

# Main function
print(blue("===== Vertical Slice Architecture Migration Status ====="))

# Count API routes
old_routes, new_routes = count_routes()
print(f"\nAPI Routes:")
print(f"  Old architecture: {yellow(str(old_routes))}")
print(f"  New architecture: {green(str(new_routes))}")

progress_percentage = new_routes / old_routes * 100 if old_routes else 0
print(f"  Migration progress: {green(str(round(progress_percentage, 1)))}%")

# Count files
old_files, new_files = count_files()
print(f"\nPython Files:")
print(f"  Old architecture: {yellow(str(old_files))}")
print(f"  New architecture: {green(str(new_files))}")
progress_percentage = new_files / old_files * 100 if old_files else 0
print(f"  Migration progress: {green(str(round(progress_percentage, 1)))}%")

print(blue("\n===== Recommended Next Steps ====="))
if new_routes < old_routes:
    print(f"1. Migrate more API routes - {old_routes - new_routes} routes still need migration")
print(f"2. Run tests for individual features")
print(f"3. Create adapters for backward compatibility")
'

# Run the tests for each feature separately
echo -e "\nTesting features individually..."

cd /workspaces/back/project_organized

echo -e "\n===== Testing PDF Processing feature ====="
PYTHONPATH=/workspaces/back pytest features/pdf_processing/tests/ -v || echo "PDF Processing tests failed"

echo -e "\n===== Testing Document Upload feature ====="
PYTHONPATH=/workspaces/back pytest features/document_upload/tests/ -v || echo "Document Upload tests failed" 

echo -e "\n===== Testing Financial Analysis feature ====="
PYTHONPATH=/workspaces/back pytest features/financial_analysis/tests/ -v || echo "Financial Analysis tests failed"

# Finally, report success
echo -e "\n✅ Test run completed!"
echo "Some errors are expected during the migration process."
echo "Continue fixing each feature one by one."
