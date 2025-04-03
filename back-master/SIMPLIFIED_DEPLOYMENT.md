# Simplified AWS Deployment Guide with DynamoDB

This guide provides step-by-step instructions for deploying your Financial Document Analysis System to AWS using a simplified approach that leverages AWS's native database service (DynamoDB) instead of requiring an external MongoDB database.

## Overview

This deployment approach uses:

- **AWS Lightsail Containers** for hosting your application
- **AWS DynamoDB** for database functionality (instead of MongoDB)
- **AWS Lightsail Object Storage** for storing document files
- **AWS Secrets Manager** for storing sensitive information
- **HuggingFace API** for AI text analysis capabilities

The primary benefit of this approach is simplicity - everything is kept within the AWS ecosystem, eliminating the need to set up and manage external services.

## Prerequisites

Before you begin, you'll need:

1. **AWS Account**: If you don't have one, sign up at [https://aws.amazon.com/](https://aws.amazon.com/)
2. **HuggingFace Account**: Sign up at [https://huggingface.co/](https://huggingface.co/) and create an API token
3. **Local Development Environment**: With Docker installed
4. **AWS CLI**: Installed and configured on your local machine

## Step 1: Install AWS CLI

If you haven't already installed the AWS CLI, run:

```bash
chmod +x install-awscli.sh
./install-awscli.sh
```

After installation, configure AWS CLI with your AWS credentials:

```bash
aws configure
```

Enter the following information when prompted:
- AWS Access Key ID: *Your access key*
- AWS Secret Access Key: *Your secret key*
- Default region name: eu-central-1 (for Europe/Middle East)
- Default output format: json

## Step 2: Set Up AWS DynamoDB and Secrets

With our simplified approach, we'll use AWS DynamoDB instead of MongoDB:

```bash
chmod +x setup-aws-dynamodb.sh
./setup-aws-dynamodb.sh
```

When prompted, enter your HuggingFace API key. This script will:

- Create three DynamoDB tables for your application
- Set up AWS Secrets Manager with your HuggingFace API key
- Generate and store secure keys for your application
- Configure SSM Parameters for Lightsail integration

## Step 3: Set Up Document Storage

Next, set up a storage bucket for document files:

```bash
chmod +x setup-storage-bucket.sh
./setup-storage-bucket.sh
```

This script creates a Lightsail Object Storage bucket for storing your uploaded PDF documents.

## Step 4: Create the Lightsail Container Service

Before deploying, you need to create a Lightsail Container Service:

1. Go to the AWS Lightsail Console: [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)

2. Click "Create container service"

3. Configure your service:
   - Region: eu-central-1 (or your preferred region)
   - Service name: financial-docs
   - Power: Micro (the smallest/cheapest option)
   - Scale: 1
   
4. Click "Create container service"

## Step 5: Deploy Your Application

Now deploy your application to AWS Lightsail:

```bash
chmod +x deploy-to-lightsail-dynamo.sh
./deploy-to-lightsail-dynamo.sh
```

This script will:

1. Build your Docker container image
2. Push the image to AWS Lightsail
3. Configure the container with the appropriate environment variables
4. Deploy the application to Lightsail

## Step 6: Access Your Application

After the deployment completes (which may take 5-10 minutes):

1. Go to the AWS Lightsail Console: [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)

2. Click on your container service (financial-docs)

3. On the Public domain tab, you'll find your application URL (something like `https://financial-docs.xxxxxxxxxxxx.eu-central-1.cs.amazonlightsail.com`)

4. Open this URL in your browser to access your application

## Understanding the Simplifications

This deployment guide has been simplified in several key ways:

1. **Native AWS Database**: Using DynamoDB eliminates the need to set up and manage an external MongoDB database. The tables are automatically created and ready to use.

2. **Automated Secret Management**: The scripts automatically generate secure random keys for your application and store them in AWS Secrets Manager.

3. **Simplified Environment Variables**: The deployment script sets all necessary environment variables for your application, including database connection settings.

4. **Pre-configured Storage**: The Lightsail Object Storage bucket is set up and configured for your application to use for document storage.

## Cost Information

This deployment uses the most cost-effective AWS services:

- **Lightsail Container Service (Micro)**: $7/month
- **DynamoDB**: Free tier includes 25GB storage and sufficient read/write capacity for development
- **Lightsail Object Storage**: ~$1-5/month depending on usage
- **AWS Secrets Manager**: ~$0.40/month per secret

Total estimated cost for initial development: **$10-15/month**

Most importantly, with this approach you don't pay anything significant until your application starts getting real usage. AWS's free tier is very generous for the services we're using.

## Troubleshooting

If you encounter issues during deployment:

1. **Check Logs**: View container logs in the AWS Lightsail Console
2. **Verify AWS Permissions**: Ensure your AWS user has sufficient permissions
3. **Check Network Settings**: Make sure the container service allows inbound traffic
4. **Validate Health Check**: Check if the health check endpoint is responding correctly

If your deployment fails, you can retry by running the deployment script again.

## Next Steps

Once your application is deployed, consider:

1. **Setting Up GitHub Integration**: For automated deployments
2. **Configuring a Custom Domain**: To use your own domain name
3. **Implementing User Authentication**: To secure your application
4. **Setting Up Monitoring**: To track application performance and usage
5. **Creating Regular Backups**: To prevent data loss

## Need Help?

Refer to:

- The AWS documentation for [Lightsail Containers](https://aws.amazon.com/lightsail/containers/)
- The AWS documentation for [DynamoDB](https://aws.amazon.com/dynamodb/)
- The HuggingFace documentation for [API Usage](https://huggingface.co/docs/api-inference/quicktour)
