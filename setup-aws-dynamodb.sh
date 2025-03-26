#!/bin/bash
# Script to set up AWS DynamoDB and secrets for the Financial Document Analysis System

# Exit on any error
set -e

# Configuration variables
REGION=$(aws configure get region)
if [ -z "$REGION" ]; then
  REGION="eu-central-1"  # Default to EU Central (Frankfurt) if not configured
fi

# Generate random secrets
FLASK_SECRET_KEY=$(openssl rand -hex 24)
JWT_SECRET=$(openssl rand -hex 24)

echo "Setting up AWS DynamoDB and Secrets for Financial Document Analysis System"
echo "----------------------------------------------------------------------"

# Check for HuggingFace API key
read -p "Enter your HuggingFace API key: " HUGGINGFACE_API_KEY
if [ -z "$HUGGINGFACE_API_KEY" ]; then
  echo "Error: HuggingFace API key is required."
  echo "You can get one at https://huggingface.co/settings/tokens"
  exit 1
fi

echo "Creating DynamoDB tables..."

# Create Documents table
aws dynamodb create-table \
  --table-name financial_documents \
  --attribute-definitions \
    AttributeName=document_id,AttributeType=S \
  --key-schema \
    AttributeName=document_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION || echo "Table financial_documents already exists or couldn't be created."

# Create Analysis Results table
aws dynamodb create-table \
  --table-name document_analysis \
  --attribute-definitions \
    AttributeName=document_id,AttributeType=S \
  --key-schema \
    AttributeName=document_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION || echo "Table document_analysis already exists or couldn't be created."

# Create Chat History table
aws dynamodb create-table \
  --table-name chat_history \
  --attribute-definitions \
    AttributeName=chat_id,AttributeType=S \
  --key-schema \
    AttributeName=chat_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region $REGION || echo "Table chat_history already exists or couldn't be created."

echo "Setting up AWS Secrets Manager for API keys and security tokens..."

# Function to create a secret if it doesn't exist
create_secret() {
  local SECRET_NAME="$1"
  local SECRET_VALUE="$2"
  local DESCRIPTION="$3"
  
  # Check if secret exists
  if aws secretsmanager describe-secret --secret-id "${SECRET_NAME}" --region "$REGION" 2>/dev/null; then
    echo "Updating existing secret: $SECRET_NAME"
    aws secretsmanager update-secret --secret-id "${SECRET_NAME}" --secret-string "${SECRET_VALUE}" --region "$REGION"
  else
    echo "Creating new secret: $SECRET_NAME"
    aws secretsmanager create-secret --name "${SECRET_NAME}" --description "${DESCRIPTION}" --secret-string "${SECRET_VALUE}" --region "$REGION"
  fi
}

# Create secrets
PREFIX="financial-docs"
create_secret "${PREFIX}/HUGGINGFACE_API_KEY" "$HUGGINGFACE_API_KEY" "HuggingFace API Key for Financial Document Analyzer"
create_secret "${PREFIX}/SECRET_KEY" "$FLASK_SECRET_KEY" "Secret key for Flask application"
create_secret "${PREFIX}/JWT_SECRET" "$JWT_SECRET" "JWT Secret for authentication"

# Create SSM parameters for Lightsail
echo "Creating SSM Parameters for Lightsail..."
aws ssm put-parameter --name "HUGGINGFACE_API_KEY" --value "$HUGGINGFACE_API_KEY" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "SECRET_KEY" --value "$FLASK_SECRET_KEY" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "JWT_SECRET" --value "$JWT_SECRET" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "USE_DYNAMODB" --value "True" --type String --overwrite --region "$REGION"
aws ssm put-parameter --name "DYNAMODB_REGION" --value "$REGION" --type String --overwrite --region "$REGION"

echo "----------------------------------------------------------------------"
echo "AWS DynamoDB tables and secrets have been set up successfully!"
echo "The following DynamoDB tables were created or confirmed:"
echo "  - financial_documents: For storing document metadata"
echo "  - document_analysis: For storing analysis results"
echo "  - chat_history: For storing chat interactions"
echo ""
echo "The following secrets were created in AWS Secrets Manager:"
echo "  - $PREFIX/HUGGINGFACE_API_KEY: Your HuggingFace API key"
echo "  - $PREFIX/SECRET_KEY: Auto-generated key for Flask"
echo "  - $PREFIX/JWT_SECRET: Auto-generated key for JWT authentication"
echo ""
echo "Next, run the storage bucket setup script:"
echo "  ./setup-storage-bucket.sh"
echo ""
echo "And finally, run the deployment script:"
echo "  ./deploy-to-lightsail.sh"
