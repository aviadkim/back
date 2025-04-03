import os

# List of all required directories
required_dirs = [
    'uploads',
    'data',
    'data/embeddings',
    'data/templates',
    'logs',
    'frontend/build/static',
    'frontend/build/static/css',
    'frontend/build/static/js',
    'frontend/build/static/media',
    'frontend/build/images'
]

# Create all required directories
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}")

print("\nAll required directories have been created!")
