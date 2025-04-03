import os

def fix_document_routes():
    """Fix document routes to properly handle file uploads"""
    
    document_route_path = 'routes/document.py'
    
    if not os.path.exists(document_route_path):
        print(f"❌ Error: {document_route_path} not found")
        return False
    
    # Create a backup
    os.system(f"cp {document_route_path} {document_route_path}.backup")
    
    # Read the current content
    with open(document_route_path, 'r') as f:
        content = f.read()
    
    # Check if the route already exists
    if '@document_api.route("/upload", methods=["POST"])' in content:
        print("Upload route exists but might not be functioning correctly")
    else:
        print("Adding upload route handler")
        
        # Find a good place to add our route
        insertion_point = content.find('document_api = Blueprint')
        if insertion_point == -1:
            insertion_point = content.find('from flask import Blueprint')
        
        if insertion_point == -1:
            print("❌ Could not find a good insertion point")
            return False
        
        # Find the end of the imports
        import_section_end = content.find('\n\n', insertion_point)
        if import_section_end == -1:
            import_section_end = content.find('\n', insertion_point)
        
        # Add missing imports if needed
        new_imports = ""
        if 'from werkzeug.utils import secure_filename' not in content:
            new_imports += "from werkzeug.utils import secure_filename\n"
        if 'import os' not in content:
            new_imports += "import os\n"
        if 'from flask import jsonify, request' not in content and 'jsonify' not in content:
            new_imports += "from flask import jsonify, request\n"
        
        # Add missing imports
        if new_imports:
            content = content[:import_section_end] + new_imports + content[import_section_end:]
        
        # Find where to add the upload route
        route_insertion_point = content.rfind('\n\n', 0, len(content))
        if route_insertion_point == -1:
            route_insertion_point = len(content)
        
        # Add the upload route
        upload_route = '''

@document_api.route("/upload", methods=["POST"])
def upload_document():
    """
    Upload a document for processing.
    ---
    tags:
      - Documents
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The document file to upload
      - name: language
        in: formData
        type: string
        required: false
        default: eng
        description: Language of the document (e.g., eng, heb, heb+eng)
    responses:
      200:
        description: Document uploaded successfully
      400:
        description: Bad request (e.g., no file provided)
      500:
        description: Server error
    """
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file:
            # Get language parameter with default
            language = request.form.get('language', 'eng')
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            file.save(file_path)
            
            # Create a document ID (you would typically generate a unique ID)
            document_id = f"doc_{os.path.splitext(filename)[0]}"
            
            # Return success response
            return jsonify({
                "message": "Document uploaded successfully",
                "document_id": document_id,
                "filename": filename,
                "language": language,
                "status": "pending"
            }), 200
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

'''
        content = content[:route_insertion_point] + upload_route + content[route_insertion_point:]
    
    # Create a get document status route if it doesn't exist
    if '@document_api.route("/<document_id>", methods=["GET"])' not in content:
        print("Adding document status route")
        
        # Find where to add the status route
        route_insertion_point = content.rfind('\n\n', 0, len(content))
        if route_insertion_point == -1:
            route_insertion_point = len(content)
        
        # Add the status route
        status_route = '''

@document_api.route("/<document_id>", methods=["GET"])
def get_document(document_id):
    """
    Get document details and status.
    ---
    tags:
      - Documents
    parameters:
      - name: document_id
        in: path
        type: string
        required: true
        description: The document ID
    responses:
      200:
        description: Document details
      404:
        description: Document not found
      500:
        description: Server error
    """
    try:
        # In a real application, you would fetch this from a database
        # For demo purposes, we'll just return a mock response
        return jsonify({
            "document_id": document_id,
            "status": "completed",  # or "pending", "processing", "failed"
            "filename": f"{document_id}.pdf",
            "upload_date": "2025-04-01T12:00:00Z",
            "pages": 5,
            "language": "heb+eng"
        }), 200
    except Exception as e:
        print(f"Error getting document: {str(e)}")
        return jsonify({"error": str(e)}), 500

'''
        content = content[:route_insertion_point] + status_route + content[route_insertion_point:]
    
    # Write the updated content
    with open(document_route_path, 'w') as f:
        f.write(content)
    
    print("✅ Document routes fixed successfully")
    return True

if __name__ == "__main__":
    fix_document_routes()
