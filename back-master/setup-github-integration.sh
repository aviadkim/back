#!/bin/bash
# Script to set up IAM user for GitHub Actions integration with AWS Lightsail

# Exit on any error
set -e

# Configuration variables - customize these
REGION="us-east-1"  # Change to your preferred region
SERVICE_NAME="financial-docs"  # Name of your Lightsail container service
IAM_USER_NAME="github-actions-${SERVICE_NAME}"  # Name for the IAM user
POLICY_NAME="GitHubActions-${SERVICE_NAME}-Policy"  # Name for the IAM policy

# Check for AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first."
    exit 1
fi

echo "Setting up IAM user for GitHub Actions integration with AWS Lightsail"
echo "---------------------------------------------------------------------"

# Create policy file
cat > github-actions-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:GetContainerServices",
                "lightsail:CreateContainerServiceDeployment",
                "lightsail:GetContainerImages",
                "lightsail:PushContainerImage",
                "lightsail:RegisterContainerImage",
                "ssm:GetParameter"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create the policy
echo "Creating IAM policy: ${POLICY_NAME}"
POLICY_ARN=$(aws iam create-policy --policy-name "${POLICY_NAME}" --policy-document file://github-actions-policy.json --query 'Policy.Arn' --output text)
echo "Policy created: ${POLICY_ARN}"

# Create the user
echo "Creating IAM user: ${IAM_USER_NAME}"
aws iam create-user --user-name "${IAM_USER_NAME}"

# Attach the policy to the user
echo "Attaching policy to user"
aws iam attach-user-policy --user-name "${IAM_USER_NAME}" --policy-arn "${POLICY_ARN}"

# Create access key for the user
echo "Creating access key for user"
ACCESS_KEY=$(aws iam create-access-key --user-name "${IAM_USER_NAME}")

ACCESS_KEY_ID=$(echo "${ACCESS_KEY}" | jq -r '.AccessKey.AccessKeyId')
SECRET_ACCESS_KEY=$(echo "${ACCESS_KEY}" | jq -r '.AccessKey.SecretAccessKey')

echo "---------------------------------------------------------------------"
echo "GitHub Actions integration setup complete."
echo ""
echo "IMPORTANT: Add the following secrets to your GitHub repository:"
echo ""
echo "  AWS_ACCESS_KEY_ID: ${ACCESS_KEY_ID}"
echo "  AWS_SECRET_ACCESS_KEY: ${SECRET_ACCESS_KEY}"
echo "  AWS_REGION: ${REGION}"
echo "  SERVICE_NAME: ${SERVICE_NAME}"
echo ""
echo "To add these secrets:"
echo "1. Go to your repository on GitHub"
echo "2. Click 'Settings' > 'Secrets and variables' > 'Actions'"
echo "3. Click 'New repository secret' and add each of the above"
echo ""
echo "Make sure to save these values securely. This is the only time"
echo "the Secret Access Key will be displayed."
echo "---------------------------------------------------------------------"

# Write credentials to a file for reference
cat > github-actions-credentials.txt << EOF
AWS_ACCESS_KEY_ID=${ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${SECRET_ACCESS_KEY}
AWS_REGION=${REGION}
SERVICE_NAME=${SERVICE_NAME}
EOF

echo "Credentials have been saved to github-actions-credentials.txt"
echo "IMPORTANT: Keep this file secure and do not commit it to your repository!"

# Clean up policy file
rm github-actions-policy.json
