FROM python:3.9-slim

WORKDIR /app

# Install system dependencies, including Tesseract OCR and poppler-utils
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads data/embeddings data/templates logs templates && chmod -R 755 uploads data logs templates

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=10000

# Start the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app
