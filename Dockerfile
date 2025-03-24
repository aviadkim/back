FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads data/embeddings data/templates logs

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=10000

# Expose port
EXPOSE 10000

# Run the application with gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
