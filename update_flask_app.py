import os
import re

# Read the current app.py
try:
    with open('app.py', 'r') as f:
        app_content = f.read()
except FileNotFoundError:
    app_content = """
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "message": "System is operational"})

if __name__ == '__main__':
    app.run(debug=True)
"""

# Check if the static folder is already configured
if "static_folder='frontend/build'" not in app_content:
    # Update the Flask app initialization to serve the React frontend
    app_content = re.sub(
        r"app\s*=\s*Flask\s*\(\s*__name__\s*[^)]*\)", 
        "app = Flask(__name__, static_folder='frontend/build', static_url_path='')", 
        app_content
    )

# Check if the root route is already defined
if "@app.route('/')" not in app_content and "@app.route('/', defaults={'path': ''})" not in app_content:
    # Add route to serve the React app
    serve_route = """

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    from flask import send_from_directory
    import os
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
"""
    
    # Find the if __name__ == '__main__': line and insert before it
    if "if __name__ == '__main__':" in app_content:
        app_content = app_content.replace("if __name__ == '__main__':", serve_route + "\nif __name__ == '__main__':")
    else:
        app_content += serve_route

# Write the updated app.py
with open('app.py', 'w') as f:
    f.write(app_content)

print("Updated app.py to serve the React frontend")
