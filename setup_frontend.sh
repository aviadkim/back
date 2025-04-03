#!/bin/bash

echo "===== Setting up the beautiful Hebrew React frontend ====="

# Create frontend directory if it doesn't exist
mkdir -p frontend/src/components
mkdir -p frontend/src/pages
mkdir -p frontend/src/assets
mkdir -p frontend/src/components/home
mkdir -p frontend/src/components/documents
mkdir -p frontend/src/components/tables

# Create package.json for the React app
cat > frontend/package.json << 'EOF'
{
  "name": "findoc-analyzer-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "react-dropzone": "^14.2.3",
    "axios": "^1.6.2",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:5000"
}
EOF

# Create App files and other components...
# [קוד שכבר נוסף קודם]

# Create a simple DocumentsPage
cat > frontend/src/pages/DocumentsPage.jsx << 'EOF'
import React from 'react';
import './DocumentsPage.css';

function DocumentsPage() {
  return (
    <div className="documents-page">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">המסמכים שלי</h1>
          <p className="page-description">צפייה, ניהול וניתוח המסמכים הפיננסיים שלך</p>
        </div>
        
        <div className="upload-section">
          <h2 className="section-title">העלאת מסמך חדש</h2>
          <div className="upload-widget">
            <div className="dropzone">
              <div className="dropzone-content">
                <i className="icon-upload-cloud"></i>
                <p>גרור ושחרר קובץ כאן או לחץ לבחירת קובץ</p>
                <span className="dropzone-hint">(PDF, Excel, CSV) בגודל עד 50MB</span>
              </div>
            </div>
            <div className="upload-options">
              <div className="language-selector">
                <label htmlFor="language-select">שפת המסמך:</label>
                <select id="language-select">
                  <option value="auto">זיהוי אוטומטי</option>
                  <option value="he">עברית</option>
                  <option value="en">אנגלית</option>
                  <option value="mixed">מעורב</option>
                </select>
              </div>
              <button className="btn-primary upload-button">
                <i className="icon-upload"></i> העלאה
              </button>
            </div>
          </div>
        </div>
        
        <div className="documents-section">
          <h2 className="section-title">המסמכים שלי</h2>
          <div className="empty-state">
            <i className="icon-documents"></i>
            <h3>אין מסמכים עדיין</h3>
            <p>העלה את המסמך הפיננסי הראשון שלך כדי להתחיל</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DocumentsPage;
EOF

cat > frontend/src/pages/DocumentsPage.css << 'EOF'
.documents-page {
  padding: 2rem 0;
}

.upload-section, .documents-section {
  margin-bottom: 3rem;
}

.upload-widget {
  background-color: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.dropzone {
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  margin-bottom: 1.5rem;
  background-color: rgba(0, 0, 0, 0.01);
  cursor: pointer;
  transition: border-color 0.3s ease, background-color 0.3s ease;
}

.dropzone:hover {
  border-color: var(--primary-color);
  background-color: rgba(74, 144, 226, 0.03);
}

.dropzone-content i {
  font-size: 3rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.dropzone-content p {
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.dropzone-hint {
  color: var(--light-text);
  font-size: 0.9rem;
}

.upload-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.language-selector {
  display: flex;
  align-items: center;
}

.language-selector label {
  margin-left: 0.5rem;
}

.language-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background-color: white;
}

.upload-button {
  display: flex;
  align-items: center;
}

.upload-button i {
  margin-left: 0.5rem;
}

.documents-section .empty-state {
  margin-top: 2rem;
}
EOF

# Create script to build the frontend
cat > frontend/build.sh << 'EOF'
#!/bin/bash
echo "Building React frontend..."
npm install
npm run build
echo "Frontend build completed!"
EOF
chmod +x frontend/build.sh

# Create a script to update the Flask app to serve the frontend
cat > update_flask_app.py << 'EOF'
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
EOF

# Create a master script to set up everything
cat > setup_and_run.sh << 'EOF'
#!/bin/bash

echo "===== Setting up the beautiful Hebrew React frontend ====="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
  echo "Node.js is required but not installed. Installing..."
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi

# Run the setup script
bash setup_frontend.sh

# Build the React frontend
cd frontend
bash build.sh
cd ..

# Update the Flask app to serve the frontend
python update_flask_app.py

# Kill any existing Flask processes
pkill -f "python.*app.py" || true

# Start Flask application
echo "Starting Flask application..."
python app.py
EOF
chmod +x setup_and_run.sh

echo "===== Setup script created ====="
echo "To run: bash setup_and_run.sh"
