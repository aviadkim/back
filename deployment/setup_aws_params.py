#!/usr/bin/env python3
"""
Setup script for storing sensitive parameters in AWS Parameter Store
"""

import os
import sys
import boto3
import uuid
import getpass
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def create_parameter(ssm_client, name, value, description, overwrite=True):
    """Create a parameter in AWS Parameter Store"""
    try:
        ssm_client.put_parameter(
            Name=name,
            Value=value,
            Description=description,
            Type='SecureString',
            Overwrite=overwrite
        )
        print(f"✅ Successfully stored {name}")
    except Exception as e:
        print(f"❌ Error storing {name}: {e}")
        sys.exit(1)

def main():
    # Initialize boto3 client
    session = boto3.Session(profile_name=os.environ.get('AWS_PROFILE', None))
    ssm_client = session.client('ssm')
    
    # MongoDB URI
    mongo_uri = os.environ.get('MONGO_URI')
    if not mongo_uri:
        mongo_uri = input("Enter MongoDB URI (mongodb+srv://...) or a placeholder: ")
    
    # Hugging Face API Key
    huggingface_api_key = os.environ.get('HUGGINGFACE_API_KEY')
    if not huggingface_api_key:
        huggingface_api_key = getpass.getpass("Enter Hugging Face API key: ")
    
    # Generate secrets if they don't exist
    secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))
    jwt_secret = os.environ.get('JWT_SECRET', str(uuid.uuid4()))
    
    # Docker image URI (placeholder - will be updated by build script)
    docker_image_uri = os.environ.get('DOCKER_IMAGE_URI', 'placeholder')
    
    # Store parameters
    create_parameter(
        ssm_client, 
        '/financial-docs/mongodb-uri', 
        mongo_uri, 
        'MongoDB connection string for Financial Document Analysis System'
    )
    
    create_parameter(
        ssm_client, 
        '/financial-docs/huggingface-api-key', 
        huggingface_api_key, 
        'Hugging Face API key for Financial Document Analysis System'
    )
    
    create_parameter(
        ssm_client, 
        '/financial-docs/secret-key', 
        secret_key, 
        'Secret key for Flask application'
    )
    
    create_parameter(
        ssm_client, 
        '/financial-docs/jwt-secret', 
        jwt_secret, 
        'JWT secret for authentication'
    )
    
    create_parameter(
        ssm_client, 
        '/financial-docs/docker-image-uri', 
        docker_image_uri, 
        'URI of the Docker image for Financial Document Analysis System'
    )
    
    print("\n✅ All parameters successfully stored in AWS Parameter Store!")
    print("You can now run the deployment script.")

if __name__ == "__main__":
    main()
