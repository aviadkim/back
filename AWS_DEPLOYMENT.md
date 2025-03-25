# AWS Deployment Guide for Financial Document Analysis System

This guide provides step-by-step instructions for deploying the Financial Document Analysis System to AWS using Lightsail Containers and other AWS services.

## Prerequisites

Before you begin, make sure you have:

1. An AWS account with appropriate permissions
2. AWS CLI installed and configured on your local machine
3. Docker installed and running on your local machine
4. Git and your application code cloned locally

## Step 1: Set Up AWS CLI

First, ensure your AWS CLI is properly installed and configured:

```bash
# Install AWS CLI (if not already installed)
# For macOS
brew install awscli

# For Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS CLI with your credentials
aws configure
```

When prompted, enter your AWS Access Key ID, Secret Access Key, default region (e.g., us-east-1), and preferred output format (json).

## Step 2: Create and Configure AWS Resources

### Set Up Secrets in AWS Secrets Manager

Use the provided script to set up your application secrets in AWS Secrets Manager:

```bash
# Make the script executable
chmod +x setup-aws-secrets.sh

# Run the script
./setup-aws-secrets.sh
```

The script will prompt you for the following information:
- MongoDB URI (for your database connection)
- HuggingFace API Key
- Secret Key for Flask
- JWT Secret for authentication

### Create a MongoDB Instance (Optional)

If you don't have a MongoDB instance already, you can create one using MongoDB Atlas or AWS DocumentDB. For a simple setup, MongoDB Atlas offers a free tier that's suitable for development and small production workloads.

1. Create an account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Set up a new cluster (free tier is sufficient to start)
3. Configure network access to allow connections from anywhere (for development) or from your AWS Lightsail container IP (for production)
4. Create a database user with appropriate permissions
5. Get your connection string from the Atlas dashboard

## Step 3: Create AWS Lightsail Container Service

You can create a Lightsail container service either through the AWS Console or using the AWS CLI:

### Using AWS Console:

1. Log in to the AWS Management Console
2. Navigate to Lightsail
3. Click on "Containers" in the left navigation
4. Click "Create container service"
5. Choose your preferred AWS Region
6. Select the power level (start with "Micro" for development, which costs about $7/month)
7. Name your service (e.g., "financial-docs")
8. Click "Create container service"

### Using AWS CLI:

```bash
aws lightsail create-container-service \
  --service-name financial-docs \
  --power micro \
  --scale 1 \
  --region us-east-1
```

## Step 4: Deploy Your Application

Use the provided deployment script to build and deploy your application:

```bash
# Make the script executable
chmod +x deploy-to-lightsail.sh

# Run the deployment script
./deploy-to-lightsail.sh
```

The script will:
1. Build your Docker image locally
2. Push the image to AWS Lightsail Container Service
3. Create a deployment on Lightsail with your environment variables
4. Configure the public endpoint

## Step 5: Verify Deployment

After the deployment completes (which might take a few minutes), verify your application is running:

1. Get your service URL:
   ```bash
   aws lightsail get-container-services --service-name financial-docs
   ```

2. Open the URL in a web browser and check the health endpoint:
   ```
   https://your-container-service-url.com/health
   ```

3. You should see a response like:
   ```json
   {
     "status": "ok",
     "message": "System is operational",
     "architecture": "Vertical Slice",
     "environment": "AWS"
   }
   ```

## Step 6: Set Up Custom Domain (Optional)

If you want to use a custom domain for your application:

1. Register a domain through AWS Route 53 or another registrar
2. Create a DNS record pointing to your Lightsail container service URL
3. Enable HTTPS by creating and attaching a Lightsail SSL/TLS certificate:
   ```bash
   aws lightsail create-container-service-certificate \
     --certificate-domain-name yourdomain.com \
     --certificate-alternative-names www.yourdomain.com \
     --service-name financial-docs
   ```

4. Attach the certificate to your container service:
   ```bash
   aws lightsail update-container-service \
     --service-name financial-docs \
     --public-endpoint "{\"containerName\":\"app\",\"containerPort\":10000,\"healthCheck\":{\"path\":\"/health\"},\"certificateName\":\"yourdomain.com\"}"
   ```

## Step 7: Set Up Monitoring and Alerts

To monitor your application's performance and receive alerts for any issues:

1. In the AWS Lightsail console, go to your container service
2. Click on the "Metrics" tab to view performance metrics
3. Set up alarms for CPU utilization, memory usage, and other metrics

## Troubleshooting

### Checking Container Logs

To view your container logs:

```bash
aws lightsail get-container-log --service-name financial-docs --container-name app
```

### Common Deployment Issues

1. **Container failing to start**: Check your application logs for errors, and ensure your environment variables are correctly set in AWS Secrets Manager.

2. **Database connection issues**: Verify that your MongoDB connection string is correct and that your database is accessible from AWS Lightsail.

3. **Permission issues**: Make sure your application has the necessary permissions to access AWS services and that your deployment IAM user has the required permissions.

4. **Memory or CPU issues**: If your application is running out of resources, consider upgrading your Lightsail container service power level.

## Scaling Your Application

As your application grows, you might need to scale it to handle more load:

### Vertical Scaling

Increase the power of your Lightsail container service:

```bash
aws lightsail update-container-service \
  --service-name financial-docs \
  --power small \
  --region us-east-1
```

Available power options are: nano, micro, small, medium, large, and xlarge.

### Horizontal Scaling

Increase the number of container nodes:

```bash
aws lightsail update-container-service \
  --service-name financial-docs \
  --scale 2 \
  --region us-east-1
```

## Backup Strategy

To ensure your data is safely backed up:

1. Schedule regular MongoDB backups using MongoDB Atlas or a custom backup script
2. Store application files and configurations in a version-controlled repository
3. Consider setting up AWS Backup for additional protection

## Upgrading and Updating

To deploy updates to your application:

1. Make your changes and commit them to your repository
2. Run the deployment script again:
   ```bash
   ./deploy-to-lightsail.sh
   ```

This will build a new image with your changes and deploy it to AWS Lightsail.

## Estimated Costs

For a basic setup with minimal usage, expect to pay approximately:

- AWS Lightsail Container Service (Micro power): $7/month
- MongoDB Atlas (Free tier): $0/month
- AWS Secrets Manager: ~$0.50/month per secret
- Data transfer: Varies based on usage (first 1 GB/month is free)

Total estimated cost for a small-scale deployment: **$10-20/month**

## Security Considerations

1. Always use encrypted connections (HTTPS) for production deployments
2. Keep your secrets in AWS Secrets Manager and avoid hardcoding them
3. Update dependencies regularly to patch security vulnerabilities
4. Implement proper authentication and authorization in your application
5. Consider enabling AWS CloudTrail for audit logging
6. Regularly review and update IAM permissions following the principle of least privilege

## Further Resources

- [AWS Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
