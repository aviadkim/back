#!/usr/bin/env python3
"""
Sample migration script for a specific component.
This shows how to migrate the PDF processor component to the new architecture.
"""
import os
import shutil
import logging
from migration_helpers import create_adapter_file, ensure_directories

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SampleMigration")

def migrate_pdf_processor():
    """Migrate PDF processor component to features/pdf_processing"""
    # Ensure feature directory exists
    os.makedirs('project_organized/features/pdf_processing', exist_ok=True)
    
    # Copy enhanced_pdf_processor.py to new location
    source_file = 'enhanced_pdf_processor.py'
    target_dir = 'project_organized/features/pdf_processing'
    target_file = os.path.join(target_dir, 'processor.py')
    
    # Only copy if source exists and target doesn't
    if os.path.exists(source_file) and not os.path.exists(target_file):
        shutil.copy2(source_file, target_file)
        logger.info(f"Copied {source_file} to {target_file}")
        
        # Create __init__.py to make it a proper package
        init_file = os.path.join(target_dir, '__init__.py')
        with open(init_file, 'w') as f:
            f.write("""\"\"\"PDF Processing Feature\"\"\"
from .processor import EnhancedPDFProcessor

__all__ = ['EnhancedPDFProcessor']
""")
        logger.info(f"Created {init_file}")
        
        # Create adapter in original location
        create_adapter_file(source_file, target_file)
        
    elif os.path.exists(target_file):
        logger.info(f"{target_file} already exists, not overwriting")
    else:
        logger.error(f"{source_file} not found")
        
def migrate_tests():
    """Migrate tests to new structure"""
    source_file = 'test_enhanced_endpoints.py'
    target_dir = 'project_organized/features/pdf_processing/tests'
    target_file = os.path.join(target_dir, 'test_endpoints.py')
    
    os.makedirs(target_dir, exist_ok=True)
    
    if os.path.exists(source_file) and not os.path.exists(target_file):
        shutil.copy2(source_file, target_file)
        logger.info(f"Copied {source_file} to {target_file}")
        
        # Update imports in the new file
        with open(target_file, 'r') as f:
            content = f.read()
        
        # Replace imports
        content = content.replace(
            'from enhanced_pdf_processor import EnhancedPDFProcessor',
            'from features.pdf_processing import EnhancedPDFProcessor'
        )
        
        with open(target_file, 'w') as f:
            f.write(content)
        logger.info(f"Updated imports in {target_file}")
    
if __name__ == "__main__":
    logger.info("Starting sample migration")
    
    ensure_directories()
    migrate_pdf_processor()
    migrate_tests()
    
    logger.info("✅ Sample migration completed!")
    print("\nNext steps:")
    print("1. Review the migrated files")
    print("2. Run tests to ensure everything works")
    print("3. Continue migrating other components")
