#!/bin/bash
# Deployment script for AWS Lightsail Containers

# Exit on any error
set -e

# Configuration variables - customize these
SERVICE_NAME="financial-docs"
REGION="us-east-1"  # Change to your preferred region
MONGODB_SERVICE="mongodb-docs"  # MongoDB container service name

# IMPORTANT: Before running this script, make sure you have:
# 1. AWS CLI installed and configured with the right credentials
# 2. Docker installed and running
# 3. Created the necessary secrets in AWS Secrets Manager

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install it first."
    exit 1
fi

# Build the container image
echo "Building Docker image..."
docker build -t "${SERVICE_NAME}-app" .

# Push the container image to AWS Lightsail
echo "Pushing image to AWS Lightsail..."
aws lightsail push-container-image \
    --region "$REGION" \
    --service-name "$SERVICE_NAME" \
    --label app \
    --image "${SERVICE_NAME}-app"

# Get the latest image
IMAGE_TAG=$(aws lightsail get-container-images --service-name "$SERVICE_NAME" --query 'containerImages[0].image' --output text)

# Create a deployment
echo "Creating deployment..."
aws lightsail create-container-service-deployment \
    --service-name "$SERVICE_NAME" \
    --region "$REGION" \
    --containers "{\"app\":{\"image\":\"$IMAGE_TAG\",\"ports\":{\"10000\":\"HTTP\"},\"environment\":{\"FLASK_ENV\":\"production\",\"PORT\":\"10000\",\"MONGO_URI\":\"{{ssm:MONGO_URI}}\",\"HUGGINGFACE_API_KEY\":\"{{ssm:HUGGINGFACE_API_KEY}}\",\"SECRET_KEY\":\"{{ssm:SECRET_KEY}}\",\"JWT_SECRET\":\"{{ssm:JWT_SECRET}}\"}}}" \
    --public-endpoint "{\"containerName\":\"app\",\"containerPort\":10000,\"healthCheck\":{\"path\":\"/health\",\"intervalSeconds\":10,\"timeoutSeconds\":5,\"successCodes\":\"200\",\"unhealthyThreshold\":2,\"healthyThreshold\":2}}"

echo "Deployment initiated. Check AWS Lightsail Console for status."
echo "Once deployment is complete, your app will be available at:"
aws lightsail get-container-services --service-name "$SERVICE_NAME" --query 'containerServices[0].url' --output text

echo "Deployment script completed. Note that the initial deployment might take several minutes."
