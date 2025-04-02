#!/bin/bash
# Script to set up AWS Lightsail Object Storage Bucket for document uploads

# Exit on any error
set -e

# Configuration variables - customize these
REGION="us-east-1"  # Change to your preferred region
BUCKET_NAME="financial-docs-uploads"  # Name for your bucket
ACCESS_KEY_NAME="financial-docs-bucket-key"  # Name for your access key

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

echo "Setting up Lightsail Object Storage for Document Uploads"
echo "-------------------------------------------------------"

# Create the bucket
echo "Creating Lightsail bucket: $BUCKET_NAME"
if aws lightsail create-bucket --bucket-name "$BUCKET_NAME" --region "$REGION" 2>/dev/null; then
    echo "Bucket created successfully"
else
    echo "Bucket already exists or there was an error. Checking status..."
    aws lightsail get-bucket --bucket-name "$BUCKET_NAME" --region "$REGION"
fi

# Enable bucket versioning for file history
echo "Enabling versioning on the bucket"
aws lightsail update-bucket --bucket-name "$BUCKET_NAME" --versioning enabled --region "$REGION"

# Create access key for the bucket
echo "Creating access key for the bucket"
aws lightsail create-bucket-access-key --bucket-name "$BUCKET_NAME" --region "$REGION" > bucket_credentials.json
echo "Access key created and saved to bucket_credentials.json"
echo "IMPORTANT: Store these credentials securely and don't commit them to version control!"

# Configure CORS to allow your application to access the bucket
echo "Configuring CORS policy"
aws lightsail put-bucket-cors --bucket-name "$BUCKET_NAME" --cors-rules '[{"allowedOrigins":["*"],"allowedMethods":["GET","PUT","POST","DELETE"],"allowedHeaders":["*"],"maxAgeSeconds":3600}]' --region "$REGION"

# Create SSM parameters for the bucket credentials
echo "Creating SSM Parameters for Lightsail Object Storage..."
BUCKET_ACCESS_KEY_ID=$(jq -r '.accessKey.accessKeyId' bucket_credentials.json)
BUCKET_SECRET_ACCESS_KEY=$(jq -r '.accessKey.secretAccessKey' bucket_credentials.json)

aws ssm put-parameter --name "BUCKET_NAME" --value "$BUCKET_NAME" --type String --overwrite --region "$REGION"
aws ssm put-parameter --name "BUCKET_REGION" --value "$REGION" --type String --overwrite --region "$REGION"
aws ssm put-parameter --name "BUCKET_ACCESS_KEY_ID" --value "$BUCKET_ACCESS_KEY_ID" --type SecureString --overwrite --region "$REGION"
aws ssm put-parameter --name "BUCKET_SECRET_ACCESS_KEY" --value "$BUCKET_SECRET_ACCESS_KEY" --type SecureString --overwrite --region "$REGION"

echo "-------------------------------------------------------"
echo "AWS Lightsail Object Storage bucket has been set up successfully."
echo "Your documents will be stored in this bucket."
echo "Bucket name: $BUCKET_NAME"
echo "Bucket region: $REGION"
echo "Access keys have been stored in bucket_credentials.json and as AWS SSM parameters."
echo ""
echo "NOTE: You need to update your application to use the S3 client from boto3 to store uploaded documents in this bucket instead of the local filesystem."
