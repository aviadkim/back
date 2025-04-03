#!/usr/bin/env python3
"""
Run the application with the vertical slice architecture.
This is a transition script that will run the new app structure
while keeping compatibility with the old structure.
"""
import os
import sys

def main():
    """Run the application with the vertical slice architecture"""
    print("Starting application with vertical slice architecture...")
    
    # Check if project_organized exists
    if not os.path.exists('project_organized'):
        print("Error: project_organized directory not found.")
        print("Run setup_vertical_slice.sh first to create the structure.")
        return 1
    
    # Change to the project_organized directory
    os.chdir('project_organized')
    
    # Run the app
    try:
        import app
        return 0
    except ImportError as e:
        print(f"Error importing app: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
