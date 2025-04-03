# Deploying with GitHub Actions

This guide explains how to use GitHub Actions to automatically build and deploy your Financial Document Analysis System to AWS Lightsail whenever you push changes to the master branch.

## Overview

We've set up a GitHub Actions workflow that will:

1. Set up all necessary AWS resources (DynamoDB tables, secrets, and Lightsail container service)
2. Build your Docker image
3. Push it to AWS Lightsail
4. Deploy your application

This approach eliminates the need for local deployment and avoids the disk space limitations in GitHub Codespaces.

## Prerequisites

Before you can use the GitHub Actions workflow, you need to add some secrets to your GitHub repository:

1. **AWS_ACCESS_KEY_ID**: Your AWS access key ID
2. **AWS_SECRET_ACCESS_KEY**: Your AWS secret access key
3. **AWS_REGION**: The AWS region to deploy to (e.g., `eu-central-1`)
4. **SERVICE_NAME**: The name for your Lightsail container service (e.g., `financial-docs`)
5. **HUGGINGFACE_API_KEY**: Your HuggingFace API key (optional but needed for AI features)

## Adding Secrets to GitHub

1. Go to your GitHub repository: https://github.com/aviadkim/back
2. Click on "Settings" (near the top of the page)
3. In the left sidebar, click on "Secrets and variables" > "Actions"
4. Click the "New repository secret" button to add each secret:

   - Name: `AWS_ACCESS_KEY_ID`
     Value: Your AWS access key ID

   - Name: `AWS_SECRET_ACCESS_KEY`
     Value: Your AWS secret access key

   - Name: `AWS_REGION`
     Value: `eu-central-1` (or your preferred region)

   - Name: `SERVICE_NAME`
     Value: `financial-docs` (or your preferred service name)

   - Name: `HUGGINGFACE_API_KEY`
     Value: Your HuggingFace API key (if available)

## Triggering the Deployment

Once your secrets are set up, the workflow will automatically run whenever you push changes to the master branch. You can also manually trigger the workflow:

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select the "Deploy to AWS Lightsail with DynamoDB" workflow
4. Click the "Run workflow" button
5. Select the branch (usually master) and click "Run workflow"

## Monitoring Deployment

You can monitor the deployment progress in several ways:

1. **GitHub Actions**: Go to the "Actions" tab in your repository to see the workflow runs and their status.

2. **AWS Lightsail Console**: Visit the [AWS Lightsail Container Services console](https://lightsail.aws.amazon.com/ls/webapp/home/containers) to see your deployment status and logs.

## Accessing Your Deployed Application

After the deployment completes (which may take several minutes), your application will be available at the URL provided by AWS Lightsail. You can find this URL:

1. In the GitHub Actions workflow output
2. In the AWS Lightsail Container Services console
3. By running this command if you have AWS CLI installed:
   ```bash
   aws lightsail get-container-services --service-name financial-docs --query 'containerServices[0].url' --output text
   ```

## Troubleshooting

If your deployment fails, check the following:

1. **GitHub Actions Logs**: Check the logs in the GitHub Actions tab to see what went wrong.

2. **IAM Permissions**: Ensure your AWS user has the necessary permissions. The user needs full access to Lightsail, SSM Parameter Store, and DynamoDB.

3. **Region Configuration**: Make sure all your resources are in the same AWS region.

4. **Container Health Checks**: Check if your application is passing the health checks. The workflow is configured to check the `/health` endpoint.

## Additional Resources

- [AWS Lightsail Documentation](https://docs.aws.amazon.com/lightsail/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)

## Next Steps

After your application is successfully deployed, consider:

1. **Setting up a custom domain**: Configure a domain name for your application
2. **Implementing monitoring**: Set up alerts for performance issues
3. **Setting up environment staging**: Create separate environments for development, staging, and production

Feel free to modify the GitHub Actions workflow file (`.github/workflows/deploy-to-lightsail-dynamo.yml`) to customize your deployment process.
