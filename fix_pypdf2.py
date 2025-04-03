import os
import re

def fix_file(filepath):
    with open(filepath, 'r') as file:
        content = file.read()
    
    # Replace old PyPDF2 imports with new ones
    content = re.sub(r'import PyPDF2', 'from PyPDF2 import PdfReader, PdfWriter', content)
    content = re.sub(r'PyPDF2\.PdfReader', 'PdfReader', content)
    content = re.sub(r'PyPDF2\.PdfWriter', 'PdfWriter', content)
    
    # Fix reader references
    content = re.sub(r'reader = PdfReader\(', 'reader = PdfReader(', content)
    content = re.sub(r'len\(reader\.pages\)', 'len(reader.pages)', content)
    content = re.sub(r'reader\.pages\[', 'reader.pages[', content)
    
    with open(filepath, 'w') as file:
        file.write(content)
    
    print(f"Fixed {filepath}")

# Process all Python files in pdf_processor directory
for root, dirs, files in os.walk('pdf_processor'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            fix_file(filepath)

print("All files processed")
