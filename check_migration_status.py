#!/usr/bin/env python3
"""Check the status of the vertical slice architecture migration"""
import os
import sys
import json
from collections import defaultdict
import re

def green(text):
    """Format text in green"""
    return f"\033[92m{text}\033[0m"

def yellow(text):
    """Format text in yellow"""
    return f"\033[93m{text}\033[0m"

def red(text):
    """Format text in red"""
    return f"\033[91m{text}\033[0m"

def blue(text):
    """Format text in blue"""
    return f"\033[94m{text}\033[0m"

def count_routes():
    """Count API routes in old and new architecture"""
    old_routes = 0
    new_routes = 0
    
    # Count old routes
    old_pattern = re.compile(r'@app\.route')
    for root, _, files in os.walk('/workspaces/back'):
        if 'project_organized' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        old_routes += len(old_pattern.findall(content))
                except:
                    pass
    
    # Count new routes
    new_pattern = re.compile(r'@\w+_bp\.route')
    for root, _, files in os.walk('/workspaces/back/project_organized'):
        for file in files:
            if file.endswith('.py'):
                try:
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        new_routes += len(new_pattern.findall(content))
                except:
                    pass
    
    return old_routes, new_routes

def count_features():
    """Count features in old and new architecture"""
    old_features = len(os.listdir('/workspaces/back/features')) if os.path.exists('/workspaces/back/features') else 0
    new_features = len(os.listdir('/workspaces/back/project_organized/features')) if os.path.exists('/workspaces/back/project_organized/features') else 0
    return old_features, new_features

def count_files():
    """Count Python files in old and new architecture"""
    old_files = 0
    new_files = 0
    
    # Count old files
    for root, _, files in os.walk('/workspaces/back'):
        if 'project_organized' in root or '.git' in root or 'node_modules' in root:
            continue
        old_files += sum(1 for f in files if f.endswith('.py'))
    
    # Count new files
    for root, _, files in os.walk('/workspaces/back/project_organized'):
        new_files += sum(1 for f in files if f.endswith('.py'))
    
    return old_files, new_files

def check_services():
    """Check services in old and new architecture"""
    old_services = []
    new_services = []
    
    # Check old services
    if os.path.exists('/workspaces/back/services'):
        for root, _, files in os.walk('/workspaces/back/services'):
            old_services.extend([f for f in files if f.endswith('.py')])
    
    # Check new services
    for feature_dir in os.listdir('/workspaces/back/project_organized/features'):
        feature_path = os.path.join('/workspaces/back/project_organized/features', feature_dir)
        if os.path.isdir(feature_path) and os.path.exists(os.path.join(feature_path, 'service.py')):
            new_services.append(f"{feature_dir}/service.py")
    
    return old_services, new_services

def main():
    """Main function"""
    print(blue("===== Vertical Slice Architecture Migration Status ====="))
    
    # Count API routes
    old_routes, new_routes = count_routes()
    print(f"\nAPI Routes:")
    print(f"  Old architecture: {yellow(old_routes)}")
    print(f"  New architecture: {green(new_routes)}")
    
    # Fix the formatting issue - don't apply formatting inside f-string formatter
    progress_percentage = new_routes / old_routes * 100 if old_routes else 0
    print(f"  Migration progress: {green(str(round(progress_percentage, 1)))}%")
    
    # Count features
    old_features, new_features = count_features()
    print(f"\nFeatures:")
    print(f"  Old architecture: {yellow(old_features)}")
    print(f"  New architecture: {green(new_features)}")
    
    # Count files
    old_files, new_files = count_files()
    print(f"\nPython Files:")
    print(f"  Old architecture: {yellow(old_files)}")
    print(f"  New architecture: {green(new_files)}")
    print(f"  Migration progress: {green(new_files / old_files * 100 if old_files else 0):.1f}%")
    
    print(blue("\n===== Recommended Next Steps ====="))
    if new_routes < old_routes:
        print(f"1. {yellow('Migrate more API routes')} - {old_routes - new_routes} routes still need migration")
    if new_features < old_features:
        print(f"2. {yellow('Migrate remaining features')} - {old_features - new_features} features still need migration")
    print(f"3. {green('Run tests')} - Use test_new_architecture.sh to verify the migration")
    print(f"4. {green('Update adapters')} - Create more adapter files for backward compatibility")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
