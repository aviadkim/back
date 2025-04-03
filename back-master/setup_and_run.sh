#!/bin/bash

echo "===== Financial Document Analysis System Setup and Run ====="

# Fix and build the frontend
echo "===== Setting up the frontend ====="
cd frontend || exit 1 # Exit if cd fails

# Fix Tailwind CSS issues
echo "Installing correct Tailwind CSS dependencies..."
npm install -D tailwindcss@^3.0.0 postcss@^8.0.0 autoprefixer@^10.0.0

# Update PostCSS config
echo "Updating PostCSS config..."
cat > postcss.config.js << 'POSTCSS_EOF'
module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
  ]
};
POSTCSS_EOF

# Create simple tailwind config if it doesn't exist
if [ ! -f tailwind.config.js ] || [ $(grep -c "content" tailwind.config.js) -eq 0 ]; then
  echo "Creating Tailwind config..."
  cat > tailwind.config.js << 'TAILWIND_EOF'
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {},
  },
  plugins: [],
};
TAILWIND_EOF
fi

# Add Tailwind directives to CSS
if ! grep -q "@tailwind" src/index.css 2>/dev/null; then
  echo "Adding Tailwind directives to CSS..."
  cat > src/index.css << 'CSS_EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Your custom CSS goes here */
CSS_EOF
fi

# Build the frontend
echo "Building the frontend..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
  echo "Frontend build failed. Exiting."
  exit 1
fi

cd .. || exit 1 # Exit if cd fails

# Run the application
echo "===== Starting the application ====="
echo "The application will be available at http://localhost:5001 (or configured port)"
# Assuming run_app.py exists and correctly starts the Flask app
python run_app.py
