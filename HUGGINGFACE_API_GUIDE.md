# Getting Your HuggingFace API Key

This guide walks you through the steps to create a HuggingFace account and generate an API key, which is required for the AI text analysis features of your Financial Document Analysis System.

## What is HuggingFace?

HuggingFace is a platform that provides access to thousands of state-of-the-art machine learning models. Your application uses HuggingFace's models for natural language processing tasks like text analysis, entity extraction, and question answering.

## Step 1: Create a HuggingFace Account

1. Go to [https://huggingface.co/join](https://huggingface.co/join)

2. You can sign up using:
   - Email and password
   - Google account
   - GitHub account

3. Complete the registration process by following the on-screen instructions

4. Verify your email address if you signed up with email

## Step 2: Generate an API Token

1. Log in to your HuggingFace account

2. Click on your profile picture in the top-right corner

3. Select "Settings" from the dropdown menu

4. In the left sidebar, click on "Access Tokens"

5. Click the "New token" button

6. Configure your token:
   - **Name**: Give your token a descriptive name (e.g., "Financial Document Analyzer")
   - **Role**: Select "Read" (minimum required permission)
   
7. Click "Generate a token"

8. Your new token will be displayed. This is the only time HuggingFace will show you the complete token, so make sure to copy it immediately and store it securely.

## Step 3: Use the API Token in Your Deployment

When running the `setup-aws-dynamodb.sh` script, you'll be prompted to enter your HuggingFace API key. Paste the token you generated in Step 2.

```bash
Enter your HuggingFace API key: hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

The script will securely store this key in AWS Secrets Manager for your application to use.

## Important Notes About Your API Key

- **Security**: Your API key provides access to HuggingFace services. Keep it confidential and never share it publicly or commit it to version control.

- **Usage Limits**: The free tier of HuggingFace's Inference API includes a fair usage limit. For most document analysis tasks during development and testing, this should be sufficient.

- **Token Expiration**: You can set your token to expire after a certain period for added security. If you do this, remember to update your application with a new token before the expiration date.

- **Multiple Tokens**: You can create multiple tokens with different permissions for different purposes, which is a good practice for security.

## Troubleshooting

If you encounter issues with your HuggingFace API key:

1. **Invalid Key Error**: Double-check that you've entered the complete API key correctly

2. **Permission Error**: Ensure your API key has at least "Read" permissions

3. **Rate Limiting**: If you're hitting usage limits, you might need to upgrade to a paid plan or optimize your application to make fewer API calls

4. **Token Expired**: If your token has expired, generate a new one and update it in AWS Secrets Manager

## Next Steps

Once you have your HuggingFace API key, you can continue with the deployment process as outlined in the [SIMPLIFIED_DEPLOYMENT.md](SIMPLIFIED_DEPLOYMENT.md) guide.
