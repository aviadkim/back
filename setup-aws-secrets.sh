#!/bin/bash
# Script to set up AWS Secrets Manager for storing sensitive configuration

# Exit on any error
set -e

# Configuration variables - customize these
REGION="us-east-1"  # Change to your preferred region
SECRET_PREFIX="financial-docs"  # Prefix for your secrets

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

# Function to create or update a secret
create_or_update_secret() {
    local SECRET_NAME="$1"
    local SECRET_VALUE="$2"
    local DESCRIPTION="$3"
    
    # Check if secret exists
    if aws secretsmanager describe-secret --secret-id "$SECRET_NAME" --region "$REGION" 2>/dev/null; then
        echo "Updating existing secret: $SECRET_NAME"
        aws secretsmanager update-secret \
            --secret-id "$SECRET_NAME" \
            --secret-string "$SECRET_VALUE" \
            --region "$REGION"
    else
        echo "Creating new secret: $SECRET_NAME"
        aws secretsmanager create-secret \
            --name "$SECRET_NAME" \
            --description "$DESCRIPTION" \
            --secret-string "$SECRET_VALUE" \
            --region "$REGION"
    fi
}

echo "Setting up AWS Secrets for Financial Document Analysis System"
echo "------------------------------------------------------------"

# Gather required secrets
read -p "Enter MongoDB URI (e.g., mongodb://user:pass@host:port/dbname): " MONGO_URI
read -p "Enter HuggingFace API Key: " HUGGINGFACE_API_KEY
read -p "Enter Secret Key for Flask app: " SECRET_KEY
read -p "Enter JWT Secret: " JWT_SECRET

# Create or update secrets in AWS Secrets Manager
create_or_update_secret "${SECRET_PREFIX}/MONGO_URI" "$MONGO_URI" "MongoDB connection string for Financial Document Analyzer"
create_or_update_secret "${SECRET_PREFIX}/HUGGINGFACE_API_KEY" "$HUGGINGFACE_API_KEY" "HuggingFace API Key for AI models"
create_or_update_secret "${SECRET_PREFIX}/SECRET_KEY" "$SECRET_KEY" "Secret key for Flask app"
create_or_update_secret "${SECRET_PREFIX}/JWT_SECRET" "$JWT_SECRET" "JWT Secret for authentication"

# Create SSM parameters that can be used by Lightsail
echo "Creating SSM Parameters for Lightsail..."
aws ssm put-parameter --name "MONGO_URI" --value "$MONGO_URI" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "HUGGINGFACE_API_KEY" --value "$HUGGINGFACE_API_KEY" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "SECRET_KEY" --value "$SECRET_KEY" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "JWT_SECRET" --value "$JWT_SECRET" --type SecureString --overwrite --region "$REGION"

echo "------------------------------------------------------------"
echo "AWS Secrets and SSM Parameters have been set up successfully."
echo "These secrets will be used by your AWS Lightsail deployment."
