import os
import re

def fix_pypdf2_imports():
    """Fix PyPDF2 imports in enhanced_pdf_processor.py"""
    file_path = 'enhanced_pdf_processor.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace PdfFileReader with PdfReader
    updated_content = content.replace('PdfFileReader', 'PdfReader')
    
    # Check if we need to update the import statement
    if 'from PyPDF2 import PdfReader' not in updated_content:
        updated_content = re.sub(
            r'from PyPDF2 import PdfFileReader',
            'from PyPDF2 import PdfReader',
            updated_content
        )
        # If there's no import statement to replace, add it
        if 'from PyPDF2 import PdfReader' not in updated_content:
            updated_content = re.sub(
                r'import PyPDF2',
                'import PyPDF2\nfrom PyPDF2 import PdfReader',
                updated_content
            )
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(updated_content)
    
    print(f"Updated {file_path} to use PdfReader instead of PdfFileReader")
    return True

if __name__ == "__main__":
    fix_pypdf2_imports()
