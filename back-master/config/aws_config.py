import os
from dotenv import load_dotenv

load_dotenv()

# S3 Settings
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'financial-documents-bucket')
S3_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# DynamoDB Settings
DYNAMODB_DOCUMENTS_TABLE = os.environ.get('DYNAMODB_DOCUMENTS_TABLE', 'financial-documents')
DYNAMODB_PROCESSED_DATA_TABLE = os.environ.get('DYNAMODB_PROCESSED_DATA_TABLE', 'financial-processed-data')
DYNAMODB_CUSTOM_TABLES_TABLE = os.environ.get('DYNAMODB_CUSTOM_TABLES_TABLE', 'financial-custom-tables')
DYNAMODB_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# Textract Settings
TEXTRACT_REGION = os.environ.get('AWS_REGION', 'us-east-1')

# AI API Settings
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Feature Flags
USE_AWS_STORAGE = os.environ.get('USE_AWS_STORAGE', 'false').lower() == 'true'
USE_AWS_OCR = os.environ.get('USE_AWS_OCR', 'false').lower() == 'true'
USE_CLOUD_AI = os.environ.get('USE_CLOUD_AI', 'false').lower() == 'true'