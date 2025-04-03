# Use a specific Python version slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - build-essential: For compiling packages if needed
# - Tesseract OCR with English and Hebrew language packs
# - Poppler utils for PDF processing (used by pdf2image)
# - libgl1 for OpenCV headless dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1 \
    # libglib2.0-0 # May not be needed for headless opencv
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to reduce layer size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create necessary directories if they don't exist
# Ensure correct permissions if running as non-root user later
RUN mkdir -p uploads logs temp

# Set environment variables
ENV PYTHONUNBUFFERED=1
# Default port the application listens on inside the container
ENV PORT=5000

# Expose the port the application runs on
EXPOSE 5000

# Command to run the application
# Use app:create_app() to run the Flask app using the factory pattern
# Use gunicorn for a more production-ready server (can be used in dev too)
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
# Or run directly with python for simpler development setup (as used in docker-compose)
CMD ["python", "app.py"]
