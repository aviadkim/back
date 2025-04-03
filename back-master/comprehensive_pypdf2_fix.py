import os
import re

def fix_all_pypdf2_issues():
    """Fix all PyPDF2 compatibility issues in enhanced_pdf_processor.py"""
    file_path = 'enhanced_pdf_processor.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix import statement
    content = re.sub(
        r'from PyPDF2 import PdfFileReader',
        'from PyPDF2 import PdfReader',
        content
    )
    
    # In case there's just an import PyPDF2 without the specific import
    if 'from PyPDF2 import PdfReader' not in content:
        content = re.sub(
            r'import PyPDF2',
            'import PyPDF2\nfrom PyPDF2 import PdfReader',
            content
        )
    
    # Replace PdfFileReader with PdfReader throughout the file
    content = content.replace('PdfFileReader', 'PdfReader')
    
    # Replace getNumPages() with len(reader.pages)
    content = re.sub(
        r'([a-zA-Z_][a-zA-Z0-9_]*?)\.getNumPages\(\)',
        r'len(\1.pages)',
        content
    )
    
    # Replace page extraction method
    extract_text_method = '''def _extract_text_pypdf2(self, file_path):
        """Extract text using PyPDF2"""
        logger.info(f"Extracting text with PyPDF2: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                pages_text = {}
                for i in range(page_count):
                    page = pdf_reader.pages[i]
                    pages_text[i] = page.extract_text()
                
                return pages_text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return {}'''
    
    # Find and replace the _extract_text_pypdf2 method
    method_pattern = r'def _extract_text_pypdf2\(self, file_path\):.*?return \{\}'
    if re.search(method_pattern, content, re.DOTALL):
        content = re.sub(method_pattern, extract_text_method, content, flags=re.DOTALL)
    else:
        print("Warning: Could not find _extract_text_pypdf2 method to replace")
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Updated all PyPDF2 compatibility issues in enhanced_pdf_processor.py")
    return True

if __name__ == "__main__":
    fix_all_pypdf2_issues()
