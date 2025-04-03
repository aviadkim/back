import os
import re

def fix_pypdf2_extraction_method():
    """Fix the _extract_text_pypdf2 method in enhanced_pdf_processor.py"""
    file_path = 'enhanced_pdf_processor.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the _extract_text_pypdf2 method
    method_pattern = r'def _extract_text_pypdf2\(self, file_path\):.*?return pages_text'
    method_match = re.search(method_pattern, content, re.DOTALL)
    
    if not method_match:
        print("Could not find _extract_text_pypdf2 method")
        return False
    
    old_method = method_match.group(0)
    
    # Create the updated method
    new_method = '''def _extract_text_pypdf2(self, file_path):
        """Extract text using PyPDF2"""
        logger.info(f"Extracting text with PyPDF2: {file_path}")
        
        try:
            pdf_reader = PdfReader(open(file_path, 'rb'))
            page_count = len(pdf_reader.pages)
            
            pages_text = {}
            for i in range(page_count):
                page = pdf_reader.pages[i]
                pages_text[i] = page.extract_text()
            
            return pages_text
        except Exception as e:
            logger.error(f"Error extracting text with PyPDF2: {e}")
            return {}'''
    
    # Replace the old method with the new one
    updated_content = content.replace(old_method, new_method)
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(updated_content)
    
    print("Updated _extract_text_pypdf2 method to work with PdfReader")
    return True

if __name__ == "__main__":
    fix_pypdf2_extraction_method()
