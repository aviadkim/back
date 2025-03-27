FROM python:3.9-slim

WORKDIR /app

# Install system dependencies excluding MongoDB
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create required directories with proper permissions
RUN mkdir -p /app/uploads /app/data/embeddings /app/data/templates /app/logs /app/templates && \
    chmod -R 755 /app/uploads /app/data /app/logs /app/templates

# Copy application files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=10000
ENV MONGO_URI=mongodb://mongo:27017/financial_documents
ENV DEFAULT_LANGUAGE=he
ENV LLM_PROVIDER=huggingface

# Run application
CMD gunicorn --bind 0.0.0.0:$PORT app:app
