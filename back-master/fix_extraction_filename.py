import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_extraction_filename():
    """Fix the document ID extraction and file naming in enhanced_pdf_processor.py"""
    file_path = 'enhanced_pdf_processor.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for syntax issues
        if "os.makedirs(self.extraction_dir, exist_ok=True" in content and not "os.makedirs(self.extraction_dir, exist_ok=True)" in content:
            logger.info("Found missing parenthesis in makedirs call")
            content = content.replace("os.makedirs(self.extraction_dir, exist_ok=True", "os.makedirs(self.extraction_dir, exist_ok=True)")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed missing parenthesis")
        else:
            logger.info("No syntax issues found")
        
        # Ensure extraction paths are correct
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "f\"{document_id}_extraction.json\"" in content:
            logger.info("Found incorrect extraction filename format")
            content = content.replace(
                "f\"{document_id}_extraction.json\"", 
                "f\"{document_id}_{filename.replace('.pdf', '_extraction.json')}\""
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("Fixed extraction filename format")
        else:
            logger.info("Extraction filename format is correct")
        
        return True
        
    except Exception as e:
        logger.error(f"Error fixing file: {e}")
        return False

if __name__ == "__main__":
    logger.info("Fixing extraction filename and output filename in enhanced_pdf_processor.py")
    result = fix_extraction_filename()
    if result:
        logger.info("Successfully fixed issues")
    else:
        logger.error("Failed to fix issues")
