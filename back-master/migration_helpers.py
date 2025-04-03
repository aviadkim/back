#!/usr/bin/env python3
"""
Helper utilities for architecture migration.
These tools help gradually migrate the codebase to the new architecture
without breaking existing functionality.
"""
import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MigrationHelpers")

def ensure_directories():
    """Create the basic directory structure for the new architecture"""
    directories = [
        'project_organized/features',
        'project_organized/shared',
        'project_organized/shared/database',
        'project_organized/shared/pdf',
        'project_organized/shared/file_storage',
        'project_organized/shared/ai',
        'project_organized/config',
        'project_organized/tests',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def create_adapter_file(original_path, new_path, module_name=None):
    """
    Create an adapter file that imports from the new location.
    This allows gradual migration without breaking imports.
    
    Args:
        original_path: Path to the original file
        new_path: Path to the new file location
        module_name: Optional module name for the import
    """
    if not os.path.exists(new_path):
        logger.error(f"New file {new_path} doesn't exist. Create it first.")
        return False
        
    # Calculate relative import path
    rel_path = os.path.relpath(
        os.path.dirname(new_path),
        os.path.dirname(original_path)
    )
    
    if module_name is None:
        module_name = os.path.splitext(os.path.basename(new_path))[0]
    
    import_path = os.path.join(rel_path, module_name).replace('/', '.')
    
    # Create adapter content
    content = f"""# This file is now an adapter to the new architecture
# Please use {new_path} instead
# This adapter will be removed in a future version

# Original file: {original_path}
# New location: {new_path}

from {import_path} import *

# Keep backwards compatibility by importing the new functionality
"""
    
    # Only write if file doesn't exist or is already an adapter
    if not os.path.exists(original_path) or "This file is now an adapter" in open(original_path).read():
        with open(original_path, 'w') as f:
            f.write(content)
        logger.info(f"Created adapter file: {original_path}")
        return True
    else:
        logger.warning(f"File {original_path} exists and is not an adapter. Not overwriting.")
        return False

def generate_gitignore():
    """Generate a comprehensive .gitignore file for the project"""
    gitignore = """# Generated directories
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
node_modules/
.pytest_cache/

# Build and distribution
build/
dist/
*.egg-info/

# Data and uploads
uploads/*
!uploads/.gitkeep
extractions/*
!extractions/.gitkeep
enhanced_extractions/*
!enhanced_extractions/.gitkeep
excel_exports/*
!excel_exports/.gitkeep

# Logs
logs/*
!logs/.gitkeep
*.log

# Local development
.env
.vscode/
.idea/
*.swp
*.swo

# Test coverage
.coverage
coverage/
htmlcov/

# Documentation
docs/_build/
"""
    
    with open('/workspaces/back/.gitignore', 'w') as f:
        f.write(gitignore)
    logger.info("Generated .gitignore file")

if __name__ == "__main__":
    logger.info("Running migration helpers")
    
    ensure_directories()
    generate_gitignore()
    
    logger.info("✅ Setup completed! You can now start migrating components.")
    print("\nExample usage:")
    print("python migration_helpers.py")
    print("python -c 'from migration_helpers import create_adapter_file; create_adapter_file(\"routes/document.py\", \"features/document_upload/api.py\")'")
