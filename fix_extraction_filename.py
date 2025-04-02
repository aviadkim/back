import os
import re

def fix_extraction_filename():
    """Fix the document ID extraction and file naming in enhanced_pdf_processor.py"""
    file_path = 'enhanced_pdf_processor.py'
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the current document_id extraction code
    # Here we're looking for the line that extracts document_id from filename
    pattern = r'document_id = filename\.split\(\'_\'\)\[0\] if \'_\' in filename else os\.path\.splitext\(filename\)\[0\]'
    
    if pattern in content:
        # The issue is that it's extracting only the first part before the underscore
        # but we need the full document_id which might contain underscores
        
        # Replace with a better extraction that preserves the full document_id
        new_extraction_code = """
        # Get original filename without path
        filename = os.path.basename(file_path)
        
        # Use the actual filename as document_id but remove .pdf extension
        document_id = os.path.splitext(filename)[0]
        """
        
        # Replace the simple document_id extraction with our improved version
        content = content.replace(pattern, new_extraction_code.strip())
    else:
        print("Warning: Could not find document_id extraction code")
        
        # Try to find the process_document method to insert proper document_id extraction
        process_method_pattern = r'def process_document\(self, file_path, output_dir=\'extractions\'\):'
        if process_method_pattern in content:
            # Find where to insert the document_id extraction code
            insert_pos = content.find(process_method_pattern) + len(process_method_pattern)
            
            # Find the next line after the method definition
            next_line_pos = content.find('\n', insert_pos) + 1
            
            # Insert proper document_id extraction
            content = content[:next_line_pos] + new_extraction_code + content[next_line_pos:]
        else:
            print("Error: Could not find process_document method")
            return False
    
    # Make sure the output path uses the document_id correctly
    if 'output_path = os.path.join(output_dir, f"doc_extraction.json")' in content:
        content = content.replace(
            'output_path = os.path.join(output_dir, f"doc_extraction.json")',
            'output_path = os.path.join(output_dir, f"{document_id}_extraction.json")'
        )
    else:
        print("Warning: Could not find output path definition. Looking for alternate patterns...")
        
        # Try to find other variations of the output path definition
        alternate_patterns = [
            r'output_path\s*=\s*os\.path\.join\(output_dir,\s*[\'"].*?[\'"]\)',
            r'output_path\s*=\s*os\.path\.join\(output_dir,\s*f[\'"]{1}.*?[\'"]{1}\)'
        ]
        
        for pattern in alternate_patterns:
            match = re.search(pattern, content)
            if match:
                old_path_def = match.group(0)
                new_path_def = f'output_path = os.path.join(output_dir, f"{{document_id}}_extraction.json")'
                content = content.replace(old_path_def, new_path_def)
                print(f"Found and replaced output path definition")
                break
    
    # Write the updated content back to the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Fixed document_id extraction and output filename in enhanced_pdf_processor.py")
    return True

if __name__ == "__main__":
    fix_extraction_filename()
