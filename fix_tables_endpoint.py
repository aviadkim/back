import os
import json
import re

def fix_tables_endpoint():
    """Fix the tables endpoint in app.py"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Find the get_document_tables function
    if 'def get_document_tables' in content:
        # Find the function start and end
        start_idx = content.find('@app.route(\'/api/documents/<document_id>/tables\')')
        if start_idx == -1:
            print("Could not find tables endpoint decorator")
            return False
        
        # Find the next function after get_document_tables
        next_function = re.search(r'@app\.route\(.*?\)\s*def \w+\(', content[start_idx+50:])
        if next_function:
            end_idx = start_idx + 50 + next_function.start()
        else:
            # If no next function, find the next route decorator
            end_idx = content.find('@app.route', start_idx + 10)
        
        if end_idx == -1:
            print("Could not determine where the function ends")
            return False
        
        # Extract the entire function
        old_function = content[start_idx:end_idx]
        
        # Create new implementation
        new_function = """@app.route('/api/documents/<document_id>/tables')
def get_document_tables(document_id):
    \"\"\"Get tables extracted from a document\"\"\"
    # Get the extraction path
    extraction_path = get_extraction_path(document_id)
    
    # Check if the document exists
    document_path = get_document_path(document_id)
    if not os.path.exists(document_path):
        return jsonify({"error": "Document not found"}), 404
    
    # If extraction file exists, read tables from it
    tables = []
    
    if os.path.exists(extraction_path):
        try:
            with open(extraction_path, 'r') as f:
                extraction_data = json.load(f)
                tables = extraction_data.get('tables', [])
        except Exception as e:
            app.logger.error(f"Error reading extraction data: {e}")
    
    # Return tables (empty list if none found)
    return jsonify({
        "tables": tables,
        "document_id": document_id,
        "table_count": len(tables)
    })
"""
        
        # Replace the old function with the new one
        new_content = content.replace(old_function, new_function)
        
        # Write the updated content back to app.py
        with open('app.py', 'w') as f:
            f.write(new_content)
        
        print("Tables endpoint function replaced successfully!")
        return True
    else:
        print("Could not find get_document_tables function in app.py")
        return False

if __name__ == "__main__":
    fix_tables_endpoint()
