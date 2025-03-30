# FinDoc Analyzer - Setup Guide

This document provides detailed setup instructions for getting the FinDoc Analyzer system up and running.

## Prerequisites

- Python 3.9+ installed
- MongoDB installed (or Docker for containerized setup)
- Tesseract OCR installed (for PDF text extraction)
- Node.js and npm (if you need to rebuild the frontend)

### Installing Tesseract OCR

**Windows:**
1. Download the installer from https://github.com/UB-Mannheim/tesseract/wiki
2. Install with default options
3. Add the installation path (e.g., `C:\Program Files\Tesseract-OCR`) to your PATH environment variable
4. Make sure Hebrew language data is installed

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-heb  # Hebrew language data
```

**Mac:**
```bash
brew install tesseract
brew install tesseract-lang  # Installs additional language data
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/aviadkim/back.git
cd back
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate     # On Windows
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Open the `.env` file and update the following values:
- Generate random values for `SECRET_KEY` and `JWT_SECRET`
- Set your MongoDB connection in `MONGO_URI`
- Configure your preferred LLM (AI model) provider:
  - Set `LLM_PROVIDER` to one of: `openrouter`, `huggingface`, `mistral`, or `openai`
  - Add the corresponding API key
  - For OpenRouter, set model preferences in the `OPENROUTER_*_MODEL` variables

### 5. Create Required Directories

```bash
mkdir -p uploads data/embeddings logs templates
```

### 6. Start MongoDB

**Using Docker:**
```bash
docker-compose up -d
```

**Local MongoDB:**
If you have MongoDB installed locally, make sure it's running:
```bash
# Check if MongoDB is running
mongod --version
```

### 7. Start the Application

```bash
python app.py
```

The application should now be running at http://localhost:5000

## Troubleshooting

### PDF Processing Issues

If you encounter issues with PDF processing:

1. Check Tesseract OCR installation:
```bash
tesseract --version
tesseract --list-langs  # Should include 'heb' for Hebrew
```

2. Verify file permissions in the uploads directory:
```bash
chmod -R 755 uploads
```

3. Check the logs for specific errors:
```bash
cat logs/app.log
```

### AI Model Connectivity Issues

If the AI chat functionality isn't working:

1. Verify your API keys in the `.env` file
2. Check that your selected LLM provider is available and has sufficient credits
3. For OpenRouter, ensure the models you've selected are available
4. Examine the logs for connection errors:
```bash
grep "Error" logs/app.log
```

### MongoDB Connection Issues

If the application can't connect to MongoDB:

1. Check if MongoDB is running:
```bash
# For local MongoDB
ps aux | grep mongod

# For Docker
docker ps | grep mongo
```

2. Verify the connection string in your `.env` file
3. Check MongoDB logs:
```bash
# For Docker
docker logs $(docker ps -q --filter name=mongo)
```

## Using the Application

1. **Upload Documents**: Use the upload form to add financial documents (PDF, Excel, CSV)
2. **Select Documents**: Click on a document to activate it for chat context
3. **Ask Questions**: Use the chat interface to ask specific questions about the document

## Advanced Configuration

### Customizing OCR Settings

If you need to adjust OCR settings for better Hebrew text recognition, edit `utils/pdf_processor.py`:

```python
# Adjust OCR configuration parameters
custom_config = r'--oem 1 --psm 3'
page_text = pytesseract.image_to_string(image, lang=ocr_language, config=custom_config)
```

### Using Different AI Models

To change the AI models used:

1. Update your `.env` file with the appropriate model names
2. For OpenRouter, visit https://openrouter.ai/docs to see available models
3. For Hugging Face, update the model repository ID

## Deploying to Production

For production environments:

1. Set `FLASK_ENV=production` in your `.env` file
2. Use a proper WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Consider using NGINX as a reverse proxy
4. Set up monitoring and alerts

## Additional Resources

- [MongoDB Documentation](https://docs.mongodb.com/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Tesseract OCR Documentation](https://tesseract-ocr.github.io/tessdoc/)
- [Flask Documentation](https://flask.palletsprojects.com/)
