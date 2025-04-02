import os
import re

def modify_app_py():
    """Modify app.py to properly handle frontend files"""
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("Error: app.py not found")
        return False
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check if there's frontend serving code
    frontend_regex = r'(app\.route\([\'"]\/.*?[\'"].*?def\s+serve_frontend.*?\n\s*return\s+.*?)\n'
    
    if re.search(frontend_regex, content, re.DOTALL):
        # Replace existing frontend serving code
        modified_content = re.sub(
            frontend_regex,
            r'\1\n    # Check if build directory exists\n    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build")\n    if not os.path.exists(frontend_path):\n        return jsonify({"error": "Frontend not built. Please run npm run build in the frontend directory."}), 404\n',
            content,
            flags=re.DOTALL
        )
        
        # Add a fallback route for all frontend routes
        if '@app.route(\'/\', defaults' not in content and '@app.route(\'/<path:path>\'' not in content:
            # Find where to add the fallback route
            if 'if __name__ == "__main__":' in modified_content:
                # Add before the main block
                index = modified_content.find('if __name__ == "__main__":')
                serving_code = '''
# Serve React App - Catch all routes and redirect to index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build")
    if not os.path.exists(frontend_path):
        return jsonify({"error": "Frontend not built"}), 404
        
    if path != "" and os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, path)
    else:
        return send_from_directory(frontend_path, 'index.html')

'''
                modified_content = modified_content[:index] + serving_code + modified_content[index:]
    else:
        # Add frontend serving code
        if 'if __name__ == "__main__":' in content:
            # Add before the main block
            index = content.find('if __name__ == "__main__":')
            serving_code = '''
# Serve React App - Catch all routes and redirect to index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build")
    if not os.path.exists(frontend_path):
        return jsonify({"error": "Frontend not built"}), 404
        
    if path != "" and os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, path)
    else:
        return send_from_directory(frontend_path, 'index.html')

'''
            modified_content = content[:index] + serving_code + content[index:]
        else:
            # Add at the end
            serving_code = '''
# Serve React App - Catch all routes and redirect to index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend/build")
    if not os.path.exists(frontend_path):
        return jsonify({"error": "Frontend not built"}), 404
        
    if path != "" and os.path.exists(os.path.join(frontend_path, path)):
        return send_from_directory(frontend_path, path)
    else:
        return send_from_directory(frontend_path, 'index.html')
'''
            modified_content = content + serving_code
    
    # Make sure necessary imports are present
    if 'from flask import send_from_directory' not in modified_content:
        # Add import after flask import
        modified_content = re.sub(
            r'from flask import (.*?)\n',
            r'from flask import \1, send_from_directory\n',
            modified_content
        )
    
    if 'import os' not in modified_content:
        # Add import at the top
        modified_content = 'import os\n' + modified_content
    
    # Save modified file
    with open('app.py', 'w') as f:
        f.write(modified_content)
    
    print("✅ app.py modified to properly serve frontend files")
    return True

if __name__ == "__main__":
    modify_app_py()
