import re

def add_enhanced_endpoint():
    """Add an enhanced extraction endpoint to app.py"""
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if the enhanced endpoint already exists
    if 'def get_document_enhanced' in content:
        print("Enhanced endpoint already exists!")
        return
    
    # Find where to add the new import
    import_section_end = content.find('\n\n', content.find('import'))
    new_import = "from enhanced_financial_extractor import EnhancedFinancialExtractor\n"
    
    # Find where to add the new endpoint (after the last endpoint)
    last_endpoint = content.rfind('@app.route')
    last_function_end = content.find('\n\n', content.find('def', last_endpoint))
    
    if last_function_end == -1:
        last_function_end = len(content)
    
    # Create the new endpoint
    new_endpoint = """

@app.route('/api/documents/<document_id>/enhanced')
def get_document_enhanced(document_id):
    \"\"\"Get enhanced financial extraction for a document\"\"\"
    # Check if the document exists
    document_path = get_document_path(document_id)
    if not os.path.exists(document_path):
        return jsonify({"error": "Document not found"}), 404
    
    # Check if enhanced extraction already exists
    enhanced_path = f"enhanced_extractions/{document_id}_enhanced.json"
    if os.path.exists(enhanced_path):
        try:
            with open(enhanced_path, 'r') as f:
                enhanced_data = json.load(f)
            return jsonify({
                "document_id": document_id,
                "enhanced_data": enhanced_data
            })
        except Exception as e:
            app.logger.error(f"Error reading enhanced extraction: {e}")
    
    # Perform enhanced extraction
    try:
        extractor = EnhancedFinancialExtractor()
        result = extractor.process_document(document_id)
        if result:
            return jsonify({
                "document_id": document_id,
                "enhanced_data": result
            })
        else:
            return jsonify({"error": "Enhanced extraction failed"}), 500
    except Exception as e:
        app.logger.error(f"Error during enhanced extraction: {e}")
        return jsonify({"error": f"Enhanced extraction error: {str(e)}"}), 500
"""
    
    # Add the new import and endpoint
    new_content = content[:import_section_end] + new_import + content[import_section_end:last_function_end] + new_endpoint
    
    # Write the updated content back to app.py
    with open('app.py', 'w') as f:
        f.write(new_content)
    
    print("Enhanced extraction endpoint added successfully!")

if __name__ == "__main__":
    add_enhanced_endpoint()
