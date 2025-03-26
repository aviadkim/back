FROM python:3.9-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required directories
RUN mkdir -p uploads data data/embeddings data/templates logs

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8080

# Set the command to run the application
CMD gunicorn --bind 0.0.0.0:$PORT app:app
