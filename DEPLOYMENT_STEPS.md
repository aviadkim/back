# Step-by-Step AWS Lightsail Deployment Guide

This guide provides detailed, hands-on instructions for deploying your Financial Document Analysis System to AWS Lightsail. Follow these steps in order.

## Before You Begin

### What You'll Need

1. An AWS account with admin access
2. AWS CLI installed and configured on your local machine
3. Docker installed and running locally
4. Your HuggingFace API key

## Step 1: Install and Configure AWS CLI

1. Install AWS CLI according to your operating system:

   **For macOS:**
   ```bash
   brew install awscli
   ```

   **For Linux:**
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```

   **For Windows:**
   Download and run the installer from https://awscli.amazonaws.com/AWSCLIV2.msi

2. Configure AWS CLI with your credentials:
   ```bash
   aws configure
   ```
   
   When prompted, enter:
   - Your AWS Access Key ID
   - Your AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Default output format (e.g., `json`)

## Step 2: Set Up AWS Resources

### Create MongoDB Database

For this deployment, we'll use MongoDB Atlas (cloud-hosted MongoDB) because it offers a free tier and is easier to set up than hosting MongoDB on AWS:

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free account
2. Create a new cluster (use the free tier)
3. Under "Security" → "Database Access", create a new database user with password authentication
4. Under "Security" → "Network Access", click "Add IP Address" and choose "Allow Access from Anywhere" (or restrict to AWS IP ranges for production)
5. Under "Databases" → "Connect", get your MongoDB connection string
   - It should look like: `mongodb+srv://username:password@cluster0.mongodb.net/financial_documents`

### Set Up AWS Secrets

1. Make the secrets setup script executable:
   ```bash
   chmod +x setup-aws-secrets.sh
   ```

2. Run the script:
   ```bash
   ./setup-aws-secrets.sh
   ```

3. When prompted, enter:
   - The MongoDB connection string from Atlas
   - Your HuggingFace API key
   - A strong random string for SECRET_KEY (used by Flask)
   - A strong random string for JWT_SECRET (used for authentication)

## Step 3: Create AWS Lightsail Container Service

1. Sign in to the AWS Management Console at [https://aws.amazon.com/console/](https://aws.amazon.com/console/)

2. Go to Lightsail: [https://lightsail.aws.amazon.com](https://lightsail.aws.amazon.com)

3. Click on "Containers" in the left navigation menu

4. Click "Create container service"

5. Choose your configuration:
   - Select a Region (use the same as in your AWS CLI configuration)
   - Choose a capacity (start with "Micro" - 512MB RAM, 0.25 vCPU - $7/month)
   - Set scale to 1 (you can increase later if needed)
   - Enter "financial-docs" as your service name

6. Click "Create container service"

The service will take a few minutes to provision. While waiting, continue with the next steps.

## Step 4: Set Up Document Storage

1. Make the storage setup script executable:
   ```bash
   chmod +x setup-storage-bucket.sh
   ```

2. Run the script:
   ```bash
   ./setup-storage-bucket.sh
   ```

3. This will create:
   - A Lightsail Object Storage bucket for your documents
   - Access keys for the bucket
   - SSM Parameters for the bucket configuration

The script will save the credentials to `bucket_credentials.json`. Keep this file secure and don't commit it to your repository.

## Step 5: Deploy Your Application

1. Make the deployment script executable:
   ```bash
   chmod +x deploy-to-lightsail.sh
   ```

2. Run the deployment script:
   ```bash
   ./deploy-to-lightsail.sh
   ```

3. The script will:
   - Build your Docker image
   - Push it to AWS Lightsail
   - Create a deployment with your environment variables
   - Set up the public endpoint

4. Wait for the deployment to complete (this may take 5-10 minutes)

5. The script will output your service URL when the deployment is complete

## Step 6: Verify Deployment

1. Go to the AWS Lightsail Console: [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)

2. Click on your container service (financial-docs)

3. Check that the status is "Running"

4. Copy the public URL and open it in your browser

5. Add "/health" to the URL to check the health endpoint
   - For example: `https://container-service-1.abcdef123456.us-east-1.cs.amazonlightsail.com/health`

6. You should see a response like:
   ```json
   {
     "status": "ok",
     "message": "System is operational",
     "architecture": "Vertical Slice",
     "environment": "AWS"
   }
   ```

## Troubleshooting

### Viewing Logs

1. In the AWS Lightsail Console, go to your container service
2. Click the "Logs" tab
3. Select your container and view the logs

### Common Issues

#### Deployment Timeout
- Check your MongoDB connection string
- Verify that your environment variables are correctly set
- Check the container logs for errors

#### Application Errors
- Verify that your HuggingFace API key is correct
- Make sure your MongoDB instance is accessible from AWS Lightsail
- Check that your bucket credentials are correct

#### Performance Issues
- Consider upgrading your container power if the application is slow
- Check if you're hitting any rate limits with external APIs

## Next Steps

Once your application is successfully deployed, consider:

1. **Setting up a custom domain**:
   - Register a domain through Route 53 or another registrar
   - Create a DNS record pointing to your Lightsail container service URL
   - Enable HTTPS with a Lightsail SSL/TLS certificate

2. **Monitoring and alerts**:
   - Set up CloudWatch alarms for your container service
   - Monitor memory and CPU usage
   - Set up alerts for any issues

3. **Backups**:
   - Set up regular MongoDB backups through Atlas
   - Consider backing up your document bucket regularly

## Managing Your Application

### AWS Lightsail Management Console

All management of your deployed application will be done through the AWS Lightsail Console:

**Direct URL**: [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)

Key management tasks:

1. **Viewing logs** - For debugging and monitoring
2. **Updating deployment** - When you make changes to your application
3. **Scaling your service** - As your usage grows
4. **Creating snapshots** - For backup and restore
5. **Managing networking** - For custom domains and HTTPS

### MongoDB Atlas Management

For database management, use the MongoDB Atlas Dashboard:

**Direct URL**: [https://cloud.mongodb.com](https://cloud.mongodb.com)

### Updating Your Application

When you make changes to your code:

1. Commit and push your changes to GitHub
2. Pull the changes to your local environment
3. Run the deployment script again:
   ```bash
   ./deploy-to-lightsail.sh
   ```

## Need Help?

If you encounter any issues with your deployment:

1. Check the container logs in the AWS Lightsail Console
2. Review the AWS_DEPLOYMENT.md file for additional guidance
3. Check the AWS Lightsail documentation: [https://docs.aws.amazon.com/lightsail/](https://docs.aws.amazon.com/lightsail/)
