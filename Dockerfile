# Use the official Python 3.12 image.
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/root/.cargo/bin:${PATH}"

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies required for the application and building packages
# Includes build tools, python dev headers, Pillow dependencies, Tesseract, Poppler, and curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       python3-dev \
       poppler-utils \
       tesseract-ocr \
       tesseract-ocr-heb \
       libjpeg-dev \
       zlib1g-dev \
       curl \
    # Clean up APT cache to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Rust using rustup
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 10000

# Define the command to run the application using Gunicorn
# Use the PORT environment variable provided by Elastic Beanstalk (defaulting to 10000 if not set)
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-10000}", "--workers", "2", "--threads", "4", "app:app"]
