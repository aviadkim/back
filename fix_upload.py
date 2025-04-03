import os
import re

def fix_upload_form():
    """Fix the upload form handling in index.html"""
    frontend_path = 'frontend/build/index.html'
    
    if not os.path.exists(frontend_path):
        print(f"Error: {frontend_path} not found")
        return False
    
    # Read file
    with open(frontend_path, 'r') as f:
        content = f.read()
    
    # Find the upload form submission handler
    upload_handler_pattern = r'document\.getElementById\(\'uploadForm\'\)\.addEventListener\(\'submit\',\s*async\s*function\(e\)\s*\{.*?\}\);'
    upload_handler_match = re.search(upload_handler_pattern, content, re.DOTALL)
    
    if not upload_handler_match:
        print("Could not find upload form handler in frontend HTML")
        return False
    
    old_handler = upload_handler_match.group(0)
    
    # Create improved upload handler with better error handling
    new_handler = """document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('fileInput');
            const language = document.getElementById('languageSelect').value;
            
            if (!fileInput.files.length) {
                alert('Please select a file');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('language', language);
            
            showLoader('uploadLoader');
            document.getElementById('uploadResult').classList.add('hidden');
            
            try {
                const response = await fetch('/api/documents/upload', {
                    method: 'POST',
                    body: formData
                });
                
                // First check if the response is OK
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Upload failed with status ${response.status}: ${errorText}`);
                }
                
                // Then try to parse as JSON
                const responseText = await response.text();
                console.log("Response text:", responseText);
                
                let result;
                try {
                    result = JSON.parse(responseText);
                } catch (parseError) {
                    console.error("JSON parse error:", parseError);
                    throw new Error(`Failed to parse response: ${responseText}`);
                }
                
                // Display the result
                document.getElementById('uploadResultJson').textContent = JSON.stringify(result, null, 2);
                document.getElementById('uploadResult').classList.remove('hidden');
                
                // Refresh the document list
                loadDocuments();
                
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('uploadResultJson').textContent = 'Error uploading the file: ' + error.message;
                document.getElementById('uploadResult').classList.remove('hidden');
            } finally {
                hideLoader('uploadLoader');
            }
        });"""
    
    # Replace the handler
    updated_content = content.replace(old_handler, new_handler)
    
    # Write back to file
    with open(frontend_path, 'w') as f:
        f.write(updated_content)
    
    print("Fixed upload form handler in frontend HTML")
    return True

if __name__ == "__main__":
    fix_upload_form()
