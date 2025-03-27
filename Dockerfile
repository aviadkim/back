FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including MongoDB
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-heb \
    tesseract-ocr-eng \
    poppler-utils \
    gnupg \
    curl \
    && curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
       gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
       --dearmor && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/7.0 main" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list && \
    apt-get update && \
    apt-get install -y mongodb-org \
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
ENV MONGO_URI=mongodb://localhost:27017/financial_documents
ENV DEFAULT_LANGUAGE=he

# Start MongoDB and the application
CMD mongod --fork --logpath=/var/log/mongodb/mongod.log && \
    gunicorn --bind 0.0.0.0:$PORT app:app
