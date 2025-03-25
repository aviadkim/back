# AWS Deployment Setup for Financial Document Analysis System

## Overview

This document provides information about the AWS deployment setup that has been created for your Financial Document Analysis System. The setup uses AWS Lightsail Containers as the primary hosting service, with MongoDB Atlas for the database and various AWS services for storage, security, and integration.

## Files and Resources Created

The following files and resources have been created to facilitate AWS deployment:

### Deployment Scripts

1. **`deploy-to-lightsail.sh`** - Main deployment script that builds your Docker image and deploys it to AWS Lightsail.

2. **`setup-aws-secrets.sh`** - Script to set up your application secrets (API keys, database credentials, etc.) in AWS Secrets Manager and SSM Parameter Store.

3. **`setup-storage-bucket.sh`** - Script to create a Lightsail Object Storage bucket for storing uploaded documents.

4. **`setup-github-integration.sh`** - Script to create an IAM user for GitHub Actions integration, enabling automatic deployments.

### Configuration Files

1. **`lightsail-compose.yml`** - Docker Compose configuration optimized for AWS Lightsail Containers.

2. **`.github/workflows/deploy-to-lightsail.yml`** - GitHub Actions workflow for automatic deployment.

### Supporting Code

1. **`utils/aws_helpers.py`** - Utility module for accessing AWS Secrets Manager and other AWS services.

2. **`utils/storage_client.py`** - Storage client for handling document uploads to either local filesystem or AWS Lightsail Object Storage.

### Documentation

1. **`AWS_DEPLOYMENT.md`** - Comprehensive guide to AWS deployment of your application.

2. **`DEPLOYMENT_STEPS.md`** - Step-by-step instructions for deploying to AWS.

## Deployment Architecture

The deployment architecture consists of the following components:

1. **AWS Lightsail Container Service** - Hosts your Docker container, providing an HTTP endpoint for your application.

2. **MongoDB Atlas** - Cloud-hosted MongoDB database for storing document metadata and other application data.

3. **AWS Lightsail Object Storage** - Storage for uploaded documents, providing durability and scalability.

4. **AWS Secrets Manager** - Securely stores sensitive information like API keys and database credentials.

5. **AWS SSM Parameter Store** - Stores configuration parameters for your application.

6. **GitHub Actions** (optional) - Provides automated deployment whenever changes are pushed to your repository.

## How to Deploy

For complete step-by-step deployment instructions, see [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md).

### Quick Start

1. Configure AWS CLI:
   ```bash
   aws configure
   ```

2. Set up AWS Secrets:
   ```bash
   ./setup-aws-secrets.sh
   ```

3. Set up document storage:
   ```bash
   ./setup-storage-bucket.sh
   ```

4. Deploy the application:
   ```bash
   ./deploy-to-lightsail.sh
   ```

For automated deployment via GitHub, also set up GitHub integration:
```bash
./setup-github-integration.sh
```

## Cost Information

Here's a breakdown of the expected monthly costs for this deployment:

| Service | Configuration | Estimated Cost |
|---------|---------------|----------------|
| AWS Lightsail Container Service | Micro (512MB RAM, 0.25 vCPU) | $7/month |
| AWS Lightsail Object Storage | 5 GB Storage | $1-5/month |
| MongoDB Atlas | Free Tier (512MB Storage) | $0/month |
| AWS Secrets Manager | 4 Secrets | ~$2/month |
| **Total** | | **$10-15/month** |

These costs can scale as your application grows, but this setup provides a cost-effective starting point.

## Security Considerations

The deployment has been configured with security in mind:

1. **Secrets Management** - All sensitive information is stored in AWS Secrets Manager, not in the code or environment variables.

2. **IAM Permissions** - IAM users and policies are created with least privilege principles.

3. **HTTPS** - The application is served over HTTPS to ensure secure communication.

4. **Environment Separation** - AWS SSM Parameter Store is used to separate environment-specific configuration from the application code.

5. **Database Security** - MongoDB Atlas provides secure authentication and network isolation for your database.

6. **Document Storage Security** - Object storage bucket is configured with appropriate access controls to protect document data.

## Monitoring and Maintenance

Your deployment includes several monitoring and maintenance features:

1. **Container Logs** - Application logs are available in the AWS Lightsail console.

2. **Health Checks** - The deployment includes a `/health` endpoint that is monitored by AWS Lightsail.

3. **Automatic Deployment** - If you set up GitHub integration, your application will be automatically deployed when you push changes to the master branch.

4. **Database Monitoring** - MongoDB Atlas provides monitoring and alerting capabilities for your database.

5. **AWS CloudWatch Integration** - AWS Lightsail integrates with CloudWatch to provide metrics and alerts.

## Scaling Considerations

As your application grows, consider the following scaling options:

1. **Vertical Scaling** - Increase the power of your Lightsail container service (from Micro to Small, Medium, Large, etc.).

2. **Horizontal Scaling** - Increase the number of container nodes in your Lightsail service.

3. **Database Scaling** - Upgrade from MongoDB Atlas free tier to a paid tier with more storage and performance.

4. **Storage Scaling** - AWS Lightsail Object Storage automatically scales as your storage needs grow.

5. **Advanced Scaling** - For more advanced scaling needs, consider migrating to Amazon ECS, EKS, or other more sophisticated container orchestration services.

## Customizing the Deployment

You can customize this deployment in several ways:

1. **Custom Domain** - Register a domain and configure it to point to your Lightsail container service.

2. **Additional Services** - Add other AWS services like SQS for queuing, SES for email, etc.

3. **Container Configuration** - Modify the `lightsail-compose.yml` file to change container settings.

4. **CI/CD Pipeline** - Enhance the GitHub Actions workflow to include testing, staging environments, etc.

5. **Multi-Region Deployment** - Deploy to multiple AWS regions for improved availability and latency.

## Troubleshooting

If you encounter issues with your deployment, consider these troubleshooting steps:

1. **Check Logs** - View the container logs in the AWS Lightsail console.

2. **Verify Secrets** - Ensure that your secrets are correctly set in AWS Secrets Manager and SSM Parameter Store.

3. **Check Database Connection** - Verify that your MongoDB Atlas connection string is correct and that your database is accessible.

4. **Storage Issues** - Check that your Lightsail Object Storage bucket is configured correctly and accessible.

5. **Deployment Errors** - If automated deployment fails, check the GitHub Actions logs for error messages.

A more detailed troubleshooting guide is available in [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md).

## AWS Management Console Access

You can access and manage your AWS resources through the following URLs:

1. **AWS Lightsail Console**: [https://lightsail.aws.amazon.com/ls/webapp/home/containers](https://lightsail.aws.amazon.com/ls/webapp/home/containers)

2. **AWS Secrets Manager Console**: [https://console.aws.amazon.com/secretsmanager/home](https://console.aws.amazon.com/secretsmanager/home)

3. **AWS SSM Parameter Store Console**: [https://console.aws.amazon.com/systems-manager/parameters](https://console.aws.amazon.com/systems-manager/parameters)

4. **AWS CloudWatch Console**: [https://console.aws.amazon.com/cloudwatch/home](https://console.aws.amazon.com/cloudwatch/home)

5. **AWS Cost Explorer**: [https://console.aws.amazon.com/cost-management/home](https://console.aws.amazon.com/cost-management/home)

## MongoDB Atlas Access

You can access and manage your MongoDB Atlas database through the following URL:

[https://cloud.mongodb.com/](https://cloud.mongodb.com/)

## GitHub Repository Integration

If you've set up GitHub integration, you can view and manage your deployment workflows through the "Actions" tab in your GitHub repository:

[https://github.com/aviadkim/back/actions](https://github.com/aviadkim/back/actions)

## Next Steps

Once your application is deployed, consider these next steps:

1. **Set up monitoring alerts** to be notified of any issues.

2. **Configure a custom domain** for your application.

3. **Implement a backup strategy** for your database and documents.

4. **Set up a staging environment** for testing changes before they go to production.

5. **Document your deployment process** for your team.

6. **Set up cost management alerts** to avoid unexpected bills.

## Support and Resources

If you need help with your AWS deployment, consider these resources:

1. **AWS Documentation**: [https://docs.aws.amazon.com/](https://docs.aws.amazon.com/)

2. **AWS Support**: [https://aws.amazon.com/support/](https://aws.amazon.com/support/)

3. **MongoDB Atlas Documentation**: [https://docs.atlas.mongodb.com/](https://docs.atlas.mongodb.com/)

4. **GitHub Actions Documentation**: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)

## Conclusion

This deployment setup provides a robust, scalable, and cost-effective solution for your Financial Document Analysis System. By leveraging AWS Lightsail Containers, MongoDB Atlas, and GitHub Actions, you can focus on developing and enhancing your application while minimizing infrastructure management overhead.

The provided scripts and utilities make it easy to deploy, update, and maintain your application, and the automatic deployment via GitHub ensures that your latest code is always running in production.
